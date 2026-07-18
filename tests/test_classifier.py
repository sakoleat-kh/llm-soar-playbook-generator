from app.services.classifier import (TechniqueResult, classify_alert)

ALERTS = [
    "PowerShell executed an encoded command.",
    "User opened an invoice attachment from an unknown sender.",
    "Administrator logged in from a foreign country.",
    "Remote Desktop connection established to a server.",
    "SSH connection detected between Linux hosts.",
]

def test_classifier():
    for alert in ALERTS:
        result = classify_alert(alert)

        assert isinstance(result, TechniqueResult)
        assert result.technique_id != ""
        assert result.technique_name != ""
        assert 0.0 <= result.confidence <= 1.0

def test_classifier_without_rag():
    for alert in ALERTS:
        result = classify_alert(alert)

        assert isinstance(result, TechniqueResult)
        assert result.technique_id != ""
        assert result.technique_name != ""
        assert 0.0 <= result.confidence <= 1.0
