import pytest
from unittest.mock import patch

from app.services.classifier import ( TechniqueResult, classify_alert, build_context)

FAKE_RESULTS = [
    {
        "technique_id": "T1059",
        "name": "Command and Scripting Interpreter",
        "document": "PowerShell execution detected.",
        "tactics": "Execution",
        "distance": 0.11,
    }
]

def test_build_context_empty():
    context = build_context([])
    assert "None" in context

def test_build_context():
    context = build_context(FAKE_RESULTS)

    assert "T1059" in context
    assert "PowerShell" in context

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_normal_alert(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.95,
    )

    result = classify_alert(
        "powershell.exe executed"
    )

    assert isinstance(result, TechniqueResult)
    assert result.path == "llm"
    assert result.technique_id == "T1059"
@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_empty_respones(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS
    mock_llm.return_value = None

    result = classify_alert("")

    assert result.path == "fallback"
    assert result.technique_id == "T1059"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_invalid_technique(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T9999",
        technique_name="Fake",
        confidence=0.99,
    )

    result = classify_alert("powershell")

    assert result.path == "fallback"
    assert result.technique_id == "T1059"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_low_confidence(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059", 
        technique_name="Command and Scripting Interpreter",
        confidence=0.20,
    )

    result = classify_alert("powershell")

    assert result.path == "fallback"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_threshold(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.50,
    )

    result = classify_alert("powershell")

    assert result.path == "llm"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_long_alert(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.93,
    )

    alert = "powershell.exe" * 700

    result = classify_alert(alert)

    assert isinstance(result, TechniqueResult)

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_khmer(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.88,
    )

    result = classify_alert(
        "មានការប្រើប្រាស់​ PowerShell លើម៉ាស៊ីនមេ"
    )
    assert result.technique_id == "T1059"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_chinese(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.89,
    )

    result = classify_alert(

       " 攻击者执行了PowerShell命令。"
    )

    assert result.technique_id == "T1059"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_error_result(mock_llm, mock_search):

    mock_search.return_value = FAKE_RESULTS

    mock_llm.return_value = TechniqueResult(
        technique_id="ERROR",
        technique_name="Ollama unavilable",
        confidence=0.0,
        path="error"
    )

    result = classify_alert("powershell")

    assert result.path == "error"

@patch("app.services.classifier.search_techniques")
@patch("app.services.classifier._invoke_with_retry")
def test_no_context(mock_llm, mock_search):

    mock_search.return_value = []
    mock_llm.return_value = None

    result = classify_alert("abc")

    assert result.technique_id == "UNKNOWN"
    assert result.path == "fallback"

def test_build_context_multiple():
    context = build_context(
        FAKE_RESULTS * 2
    )

    assert context.count("T1059") == 2