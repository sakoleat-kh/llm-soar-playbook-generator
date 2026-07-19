import app.services.classifier as classifier

from app.services.classifier import TechniqueResult, classify_alert
from langchain_core.exceptions import OutputParserException

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

def test_retry_after_output_parser(monkeypatch):
    
    calls = {"count": 0}

    monkeypatch.setattr(
        classifier,
        "search_techniques",
        lambda *args, **kwargs: []
    )

    def fake(alert_text, candidates):

        calls["count"] += 1

        if calls["count"] < 2:
            raise OutputParserException("bad json")
        
        return TechniqueResult(
            technique_id="T1059",
            technique_name="Command and Scripting Interpreter",
            confidence=0.93,
            path="llm",
        )
    
    monkeypatch.setattr(classifier, "_invoke_chain",fake)

    result = classifier.classify_alert(
        "PowerShell executed an encoded command."
    )

    assert result.technique_id.startswith("T1059")    
    assert result.confidence == 0.93
    assert result.path == "llm"
def test_connection_error(monkeypatch):
    """Connection failure should return an error result."""

    monkeypatch.setattr(
        classifier,
        "search_techniques",
        lambda *args, **kwargs: []
    )

    def fake(alert_text, candidates):
        raise ConnectionError("Unable to connect to Ollama")
    
    monkeypatch.setattr(classifier, "_invoke_chain", fake)

    result = classifier.classify_alert(
        "PowerShell executed an encoded command."
    )

    assert result.path == "error"
    assert result.error == "ConnectionError"

def test_empty_response_uses_fallback(monkeypatch):
    """Empty LLM response should use Chroma fallback."""

    monkeypatch.setattr(
        classifier,
        "search_techniques",
        lambda *args, **kwargs: [
            {
                "technique_id": "T1566.001",
                "name": "Spearphshing Attchment",
            }
        ],
    )
    monkeypatch.setattr(
        classifier, 
        "_invoke_chain",
        lambda alert_text, candidates: None,
    )

    result = classifier.classify_alert(
        "User opened an invoice attachment."
    )

    assert result.path == "fallback"
    assert result.technique_id == "T1566.001"

def test_low_confidence_uses_fallback(monkeypatch):
    """Low-confidence prediction should use Chroma fallback"""

    monkeypatch.setattr(
        classifier,
        "search_techniques",
        lambda *args, **kwargs: [
            {
                "technique_id": "T1078",
                "name": "value Accounts",
            }
        ],
    )

    monkeypatch.setattr(
        classifier,
        "_invoke_chain",
        lambda alert_text, candidates: TechniqueResult(
            technique_id="T1059",
            technique_name="Command and Scripting Interpreter",
            confidence=0.25,
            path="llm",
        ),
    )

    result = classify_alert(
        "Administrator logged in from a foreign country."
    )

    assert result.path == "fallback"
    assert result.technique_id == "T1078"