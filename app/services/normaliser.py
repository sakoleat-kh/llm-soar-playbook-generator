import re
from datetime import datetime, UTC
from pydantic import BaseModel
from app.services.sigma import AlertInput

class NormalisedAlert(BaseModel):
    sender: str
    subject: str
    body_text: str
    source_system: str
    alert_type: str
    iocs: list[str]
    severity_level: str
    timestamp: datetime

IP_REGEX = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
DOMAIN_REGEX = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"

def determine_alert_type(subject: str) -> str:
    subject_lower = subject.lower()

    if "login" in subject_lower:
        return "login"
    elif "malware" in subject_lower:
        return "malware"
    elif "phishing" in subject_lower:
        return "phishing"
    return "unknown"

def determine_severity_level(severity: int) -> str:
    if severity >= 8:
        return "high"
    elif severity >= 4:
        return "medium"
    return "low"

def extract_iocs(text: str) -> list[str]:
    ips = re.findall(IP_REGEX, text)
    domains = re.findall(DOMAIN_REGEX, text)

    return list(set(ips + domains))

def normalise_alert(raw: AlertInput) -> NormalisedAlert:
    combined_text = f"{raw.subject} {raw.body_text}"

    return NormalisedAlert(
        sender=raw.sender,
        subject=raw.subject,
        body_text=raw.body_text,
        source_system=raw.source_system,
        alert_type=determine_alert_type(raw.subject),
        iocs=extract_iocs(combined_text),
        severity_level=determine_severity_level(raw.severity),
        timestamp=datetime.now(UTC)
    )

