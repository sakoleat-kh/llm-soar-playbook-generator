from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.services.enrichment import get_technique_detail

class PlaybookStep(BaseModel):
    step_num : int
    step_name : str
    action : str
    command_or_tool : str
    expected_outcome : str

class PlaybookDraft(BaseModel):
    technique_id : str
    technique_name : str
    alert_summary : str
    steps: List[PlaybookStep] = Field(min_length=5, max_length=5)

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)

structured_llm = llm.with_structured_output(PlaybookDraft)

SYSTEM_PROMT = """

You are a senior SOC incident responder.

Generate a 5-step incident response playbook in JSOn.

ATT&CK  Technique:
{technique_id}: {technique_name}

Technique Description:
{technique_description}

Alert:
{alert_summary}

Rules:
- Return ONLY valid JSON.
- Produce exactly 5 steps.
- Each step must contain:
    - step_num
    - step_name
    - action
    - command_or_tool
    - expected_outcome
- Steps must be specific, practical, and actionable.
- Use realistic SOC tools where appropriate (Microsoft Defender, CrowdStrike,
splunk, Velociraptor, PowerShell, Windows Event Viewer, etc.).

"""

def generate_playbook(
    technique_id: str,
    alert: str,
) -> PlaybookDraft:
    """
    Generate an incident response playbook for the classified ATT&CK technique.
    """

    technique = get_technique_detail(technique_id)

    if technique is None:
        raise ValueError(f"Technique '{technique_id}' not found.")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMT),
        ]
    )
    chain = prompt | structured_llm

    return chain.invoke(
        {
            "technique_id": technique["technique_id"],
            "technique_name": technique["name"],
            "technique_description": technique["description"],
            "alert_summary": alert,
        }
    )