from app.services.classifier import (TechniqueResult, classify_alert)

def test_classifier_returns_return():
    result = classify_alert(
        "PowerShell executed an encoded command."
    )

    assert isinstance(result, TechniqueResult)

    assert result.technique_id != ""
    assert result.technique_name != ""

    assert 0.0 <= result.confidence <= 1.0