from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.services.chroma_service import search_techniques

class TechniqueResult(BaseModel):
    """Predicted MITRE ATT&CK technique."""

    technique_id: str = Field(..., description="MITRE ATT&CK Technique ID")
    technique_name: str = Field(..., description="MITRE ATT&CK Technique Name")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )

SYSTEM_PROMPT = """
You are a cybersecurity analyst.
Your task is to map a security alert to ONE MITRE ATT&CK technique.
You will be given:
1. The alert.
2. candidate ATT&CK technique retrieved from a vector database.

Choose ONLY ONE technique from the candidate list.
Return ONLY JSON.

Example:
{{
    "technique_id": " T1059.001",
    "technique_name": "PowerShell",
    "confidence": 0.92

}}

confidence MUST be a decimaml between 0.0 and 1.0

Do NOT return percentages.
Do NOT return markdown.

"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Alert:
{alert}
Candidate Techniques:
{candidates}

""",
        ),
    ]
)

llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0.1,
)

chain = prompt | llm.with_structured_output(TechniqueResult)

def classify_alert(alert_text: str) -> TechniqueResult:
    """
    Classify a security alert into the most likely MITRE ATT&CK technique.
    Uses ChromaDB retrieval before querying the LLM.

    """

    candidates = search_techniques(alert_text, n_results=5)
    candidate_text = "\n".join(
        [
            f"{c['technique_id']} - {c['name']}"
            for c in candidates
        ]
    )

    result = chain.invoke(
        {
            "alert": alert_text,
            "candidates": candidate_text,
        }
    )

    # Normalize confidence if model returns percentage
    if result.confidence > 1:
        result.confidence /= 100.0

    result.confidence = max(0.0, min(1.0, result.confidence))

    return result