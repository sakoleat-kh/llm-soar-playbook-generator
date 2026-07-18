from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

import time

from app.services.chroma_service import search_techniques

class TechniqueResult(BaseModel):
    """Predicted MITRE ATT&CK technique."""

    technique_id: str = Field(..., description="MITRE ATT&CK Technique ID")
    technique_name: str = Field(..., description="MITRE ATT&CK Technique Name")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence score"
    )

SYSTEM_PROMPT = """
You are a cybersecurity analyst.

You will receive:
1, relevant ATT&Ck technique retrivend from a vector database.
2. A security alert.

Choose the single best matching MITRE ATT&Ck technuqie.

Use the retrieved techniques as primary context.

Return JSOn only with:
- technique_id
- technique_name
- confidence

Do not explain anything

"""

def build_context(alert_text: str) -> str:
    """
    Build ATT&CK context using ChromaDB search.
    """
    results = search_techniques(alert_text, n_results=3)
    if not results:
        return "Relevant ATT&Ck techniques:\nNone"
    
    context = "Relevant ATT&Ck techniques:\n"

    for tech in results:
        context += (
            f"{tech['technique_id']} - "
            f"{tech['name']}\n"
        )
    return context
                  

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Alert:
{alert_text}
Candidate Techniques:
{candidates}

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

def classify_alert(alert_text: str) -> TechniqueResult:
    start = time.perf_counter()

    candidate_text = build_context(alert_text)
    print(f"Search took {time.perf_counter()-start:.2f}s")

    llm_start = time.perf_counter()

    result = chain.invoke(
        {
            "alert_text": alert_text,
            "candidates": candidate_text,
        }
    )

    print(f"LLM took {time.perf_counter()-llm_start:.2f}s")

    return result
