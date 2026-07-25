import re
from datetime import datetime, UTC
from pydantic import BaseModel, Field
from app.services.sigma import AlertInput

class NormalisedAlert(BaseModel):
    sender: str = Field (
        description="Email address or sender of the seciruty alert",
        examples=["analyst@example.com"]
    )
    subject: str = Field(
        description="Subject or title of the security alert",
        examples=["Suspicious PowerShell Activity"]
    )
    body_text: str = Field(
        description="Normalized alert description",
        examples=["Encoded PowerShell command executed from explorer.exe."]
    )
    source_system: str = Field(
        description="System that generated the alert",
        examples=["Microsoft Sentinel"]
    )
    alert_type: str = Field(
        description="Type of security alert",
        examples=["Malware Detection"]
    )
    iocs: list[str] = Field(
        description="List of extracted Indicators of Compromise (IOCs)",
        examples=[["explorer.exe", "powershell.exe."]]
    )
    severity_level: str = Field(
        description="Normalized severity level",
        examples=["medium"]
    )
    timestamp: datetime = Field(
        description="Timestamp when the alert waas generated",
        examples=["2026-27-26T12:30:00Z"]
    )

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

