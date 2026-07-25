
from __future__ import annotations

from app.services.sigma_service import get_sigma_rules

from app.utils.logger import logger

from pydantic import BaseModel, Field
from typing import List


def generate_playbook(technique_id: str, technique_name: str, alert_summary: str) -> PlaybookDraft:
    sigma_rules = get_sigma_rules(technique_id)

    print("===== SIGMA RULES =====")
    print(sigma_rules)
    logger.info(
    "playbook_generated",
    extra={
        "technique_id": technique_id,
        "alert_id": alert_summary,
    }
    )
    return PlaybookDraft(
        technique_id=technique_id,
        technique_name=technique_name,
        alert_summary=alert_summary,
        steps=[
            PlaybookStep(
                step_num=1,
                step_name="Contain the Threat",
                action="Isolate the affected host from the network.",
                command_or_tool="EDR",
                expected_outcome="Host is isolated."
            ),
            PlaybookStep(
                step_num=2,
                step_name="Collect Evidence",
                action="Collect logs and forensic artifacts.",
                command_or_tool="SIEM",
                expected_outcome="Evidence collected"
            ),
            PlaybookStep(
                step_num=3,
                step_name="Investigate",
                action="Analyze the attack behavior.",
                command_or_tool="MITRE ATT&CK",
                expected_outcome="Root cause identified."
            ),
            PlaybookStep(
                step_num=4,
                step_name="Remediate",
                action="Remove malicious files and block indicators.",
                command_or_tool="EDR / Firewall",
                expected_outcome="Threat removed."
            ), 
            PlaybookStep(
                step_num=5,
                step_name="Recovery",
                action="Restore normal operations and monitor the system,",
                command_or_tool="Monitoring",
                expected_outcome="System is operational."
            ),
        ],
        sigma_rules=sigma_rules,
    )

class SigmaRule(BaseModel):
    title: str = Field(
        description="URL of the Sigma rule in the SigmaHQ repository",
        examples=[
            "https://raw.githubusercontent.com/SigmaHQ/sigma/main/rules/windows/proc_creation_win_cscript_vbs.yml"
        ]
    )
    raw_url: str

class PlaybookStep(BaseModel):
    step_num: int = Field(
        description="Step number in the response playbook",
        examples=[1]
    )
    step_name: str = Field(
        description="Name of the response step",
        examples=["Contain the Threat"]
    )
    action: str = Field(
        description="Action to be performed",
        examples=["Isolate the affected host from the network."]
    )
    command_or_tool: str = Field(
        description="Tool or command used to perform the action",
        examples=["EDR"]
    )
    expected_outcome: str = Field(
        description="Expected result after the step is completed",
        examples=["Hostis isolated"]
    )

class PlaybookDraft(BaseModel):
    technique_id: str = Field(
        description="MITRE ATT&CK technique ID",
        examples=["T1059"]
    )
    technique_name: str = Field(
        description="MITRE ATT&CK name",
        examples=["Command and Scripting Interpreter"]
    )
    alert_summary: str = Field(
        description="Summary of the classified security alert",
        examples=[
            "PowerShell executed an encoded command from explorer.exe."
        ]
    )
    steps: List[PlaybookStep] = Field(
        description="List of generated response steps"
    )
    sigma_rules: List[SigmaRule] = Field(
        default_factory=list,
        description="Related Sigma detection rules"
    )



    