import logging
import time
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.exceptions import OutputParserException
from app.services.chroma_service import search_techniques

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF = [2, 4, 8]
CONFIDENCE_THRESHOLD = 0.5

class TechniqueResult(BaseModel):
    """Predicted MITRE ATT&CK technique."""

    technique_id: str = Field(..., description="MITRE ATT&CK Technique ID")
    technique_name: str = Field(..., description="MITRE ATT&CK Technique Name")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )
    path: Literal["llm", "fallback", "error"] = "llm"
    error: str | None = None

SYSTEM_PROMPT = """
You are an MITRE ATT&CK classifier.

You MUST classify the alert using ONLY ONE of the techniques provided under
'Relevant ATT&CK Techniques'.

Rules:
- Do NOT invent technique IDs.
- Do NOT return any technique that is not listed.
- Choose exactly one candidate.
- confidence must be between 0.0 and 1.0


Return ONLY JSON:

{{
    "technique_id": "...",
    "technique_name": "...",
    "confidence": 0.95
}}

Rules:
- confidence MUST be a decimal between 0.0 and 1.0.
- Never return percentages like 95 or 87.
- Return 0.95 instead of 95.
- Return ONLY the JSON object.
"""

SIMPLIFIED_PROMPT = """
Return ONLY valid JSON.

Fields:
- technique_id
- technique_name
- confidence

Rules:
- confidence must be a decimal between 0.0 and 1.0.
- Never return percentages.
- Example:
{{
    "technique_id": "T1059",
    "technique_name": "Command and Scripting Interpreter",
    "confidence": 0.93
}}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Alert:
{alert_text}

Revelant ATT&CK Techniques:
{candidates}

Choose ONLY ONE technique from the list above.

Do NOT invent another ATT&CK ID.

""",
        ),
    ]
)

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.1,
    num_predict=64,
)

chain = prompt | llm.with_structured_output(TechniqueResult)

def _invoke_chain(alert_text: str, candidates: str, system_prompt: str = SYSTEM_PROMPT):
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                """

Alert:
{{alert_text}}

Relevant ATT&CK Techniques:
{{candidates}}

""",
            ),
        ]
    )

    chain = prompt | llm.with_structured_output(TechniqueResult)

    return chain.invoke(
        {
            "alert_text": alert_text,
            "candidates": candidates,
        }
    )

def _invoke_with_retry(alert_text: str, candidates: str):
    simplified = False

    for attempt in range(MAX_RETRIES):
        try:
            
            if simplified:
                retry_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", SIMPLIFIED_PROMPT),
                        (
                            "human",
                            """
Alert:
{{alert_text}}

Relevant ATT&CK Techniques:
{{candidates}}

""",
                        ),
                    ]
                )

                retry_chain = (
                    retry_prompt
                    | llm.with_structured_output(TechniqueResult)
                )
                
                result = retry_chain.invoke(
                    {
                        "alert_text": alert_text,
                        "candidates": candidates,
                    }
                )

            else:
                result = _invoke_chain(alert_text, candidates)
            
            if result is None:
                return None
            
            return result
        
        except OutputParserException:

            logger.warning(
                "Parser failure on attempt %d/%d",
                attempt +1,
                MAX_RETRIES,
            )

            simplified = True

            if attempt < MAX_RETRIES -1:
                time.sleep(BACKOFF[attempt])
                continue

            raise

        except ConnectionError:

            logger.exception("Cannot connect to Ollama.")

            return TechniqueResult(
                technique_id="ERROR",
                technique_name="Ollama unavailable",
                confidence=0.0,
                path="error",
                error="ConnectionError",
            )

def build_context(results: list[dict]) -> str:
    """
    Build ATT&CK context using ChromaDB search.
    """

    if not results:
        return "Relevant ATT&CK techniques:\nNone"
        
    lines = []

    for tech in results:
        lines.append(
            f"{tech['technique_id']} - "
            f"{tech['name']}\n"
            f"{tech.get('document', '')}"
        )
    return "\n".join(lines)
                  
def classify_alert(alert_text: str) -> TechniqueResult:
    """Classify an alert using RAG with a ChromaDB fallback."""
    context_results = search_techniques(alert_text, n_results=5)
    context = build_context(context_results)

    result = _invoke_with_retry(
            alert_text,
            context,
    )

    valid_ids = {tech["technique_id"] for tech in context_results}

    if result is not None and result.technique_id not in valid_ids:
        logger.warning(
            "LLM return invalid technique %s. Using fallback.",
            result.technique_id,
        )

        if context_results:
            top = context_results[0]

            return TechniqueResult(
                technique_id=top["technique_id"],
                technique_name=top["name"],
                confidence=0.5,
                path="fallback",
            )

    if result is None:
        logger.warning("Empty LLM response. Using ChromaDB fallback.")

        if context_results:
            
            top = context_results[0]

            return TechniqueResult(
                technique_id=top["technique_id"],
                technique_name=top["name"],
                confidence=0.5,
                path="fallback"
            )
        return TechniqueResult(
                technique_id="UNKNOWN",
                technique_name="UNKNOWN",
                confidence=0.0,
                path="fallback"
        )
    if result.path == "error":
        return result
        

    if result.confidence >= CONFIDENCE_THRESHOLD:
        result.path = "llm"
        logger.info(
            "classification_path=llm confidence=%2.f technique=%s",
            result.confidence,
            result.technique_id,
        )
        return result
    
    if context_results:
        top = context_results[0]

        logger.info(
            "classification_path=fallback llm_confidence=%2.f fallback=%s",
            result.confidence,
            top["technique_id"],
        )

        return TechniqueResult(
            technique_id=top["technique_id"],
            technique_name=top["name"],
            confidence=max(result.confidence, 0.5),
            path="fallback"
        )
    
    result.path = "llm"
    return result

