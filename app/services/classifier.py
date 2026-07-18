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
    results = search_techniques(alert_text, n_results=5)
    if not results:
        return "Relevant ATT&Ck techniques:\nNone"
    
    context = "Relevant ATT&Ck techniques:\n"

    for tech in results:
        context += (
            f"{tech['technique_id']}: {tech['name']} - "
            f"{tech.get('document', '')}\n"
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
    model="llama3.1:latest",
    temperature=0.1,
)

chain = prompt | llm.with_structured_output(TechniqueResult)

def classify_alert(alert_text: str) -> TechniqueResult:
    candidate_text = build_context(alert_text)

    result = chain.invoke(
        {
            "alert_text": alert_text,
            "candidates": candidate_text,
        }
    )

    if result.confidence > 1:
        result.confidence /= 100.0

    result.confidence = max(0.0, min(1.0, result.confidence))

    return result
