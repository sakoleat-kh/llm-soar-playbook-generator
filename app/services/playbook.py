
from __future__ import annotations

from app.services.sigma_service import get_sigma_rules


from pydantic import BaseModel
from typing import List


def generate_playbook(technique_id: str, technique_name: str, alert_summary: str) -> PlaybookDraft:
    sigma_rules = get_sigma_rules(technique_id)

    print("===== SIGMA RULES =====")
    print(sigma_rules)
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
    title: str
    raw_url: str

class PlaybookStep(BaseModel):
    step_num: int
    step_name: str
    action: str
    command_or_tool: str
    expected_outcome: str

class PlaybookDraft(BaseModel):
    technique_id: str
    technique_name: str
    alert_summary: str
    steps: List[PlaybookStep]
    sigma_rules: List[SigmaRule] = []



    