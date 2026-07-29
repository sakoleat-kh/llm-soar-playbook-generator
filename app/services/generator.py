from typing import List

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.services.enrichment import get_technique_detail

class PlaybookStep(BaseModel):
    step_num : int = Field(
        description="Step number in the plybook",
        examples=[1]
    )
    step_name : str = Field(
        description="Name of the response step",
        examples=["Contain the Threat"]
    )
    action : str = Field(
        description="Action to perform",
        examples=["Isolate the affected host from the network."]
    )
    command_or_tool : str = Field(
        description="Tool or command used to perform the action",
        examples=["Microsoft Defender"]
    )
    expected_outcome : str = Field(
        description="Expected result after completing the action",
        examples=["Host is isolated from the network."]
    )

class PlaybookDraft(BaseModel):
    technique_id : str = Field(
        description="MITRE ATT&CK technique ID",
        examples=["T1059"]
    )
    technique_name : str = Field(
        description="MITRE ATT&CK technique name",
        examples=["Command and Scripting Interpreter"]
    )
    alert_summary : str = Field(
        description="Summary of the security alert",
        examples=["PowerShell executed an encoded command from explorer.exe."]
    )
    steps: List[PlaybookStep] = Field(min_length=5, max_length=5, description="Generated incident response playbook with five response steps.")

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)

structured_llm = llm.with_structured_output(PlaybookDraft)

SYSTEM_PROMT = """

You are a senior SOC incident responder.

Generate an incident response playbook as VALID JSOn.

ATT&CK  Technique:
{technique_id}: {technique_name}

Technique Description:
{technique_description}

Alert:
{alert_summary}

Requiremnets:
- Return ONLY valid JSON.
- Produce EXACTLY 5 incident response steps.
- Every step MUST be different.
- Never repeat the same action.
- Never output placeholder text.
- Never output "Repeats the call parameter".

Each step must contain:
    - step_num
    - step_name
    - action
    - command_or_tool
    - expected_outcome

The five steps should roughly cover:
1. Containment
2. Evidence Collection
3. Investigation
4. Reediation
5. Recovery

USe realistic SOC tools whenever appropriate, for example:
- Microsoft Defender
- CrowdStrike
- Velociraptor
- Sysmon
- Windows Event Viewer
- PowerShell
- Splunk

Return JSON only.
"""

def generate_playbook(
    technique_id: str,
    alert: str,
) -> PlaybookDraft:
    """
    Generate an incident response playbook for a classified ATT&CK technique.
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

    print("\n========================")
    print("Generated Playbook")
    print("==========================")

    print(result)

    print("\nPlaybook Steps")

    for step in result.steps:
        print("-----------------------------")
        print(f"Step {step.step_nu}")
        print(f"Name : {step.action}")
        print(f"Action : {step.action}")
        print(f"Tool : {step.command_or_tool}")
        print(f"Outcome: {step.expected_outcome}")

    print("============================================\n")

    return result