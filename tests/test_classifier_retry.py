import pytest
from unittest.mock import MagicMock, patch

from langchain_core.exceptions import OutputParserException
from app.services.classifier import (TechniqueResult, _invoke_with_retry)

def test_invoke_with_retry_success_first_attempt():
    """LLM succeeds immediately."""
    result = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and scripting Interpreter",
        confidence=0.95,
    )

    with patch(
        "app.services.classifier._invoke_chain",
        return_value=result,
    ) as mock_chain:
        response = _invoke_with_retry("powershell.exe", "context")

    assert response == result
    mock_chain.assert_called_once()

def test_invoke_with_retry_none_response():
    """LLM returns None."""
    with patch(
        "app.services.classifier._invoke_chain",
        return_value=None,
    ):
        response = _invoke_with_retry("alert", "context")

    assert response is None

@patch("app.services.classifier.time.sleep", return_value=None)
def test_retry_after_parser_error_then_success(mock_sleep):
    """Parser fails once, then succeeds."""
    result = TechniqueResult(
        technique_id="T1059",
        technique_name="Command and Scripting Interpreter",
        confidence=0.91,
    )

    with patch(
        "app.services.classifier._invoke_chain",
        side_effect=[
            OutputParserException("bad json"),
            result,
        ],
    ):
        response = _invoke_with_retry("alert", "context")
    
    assert response.technique_id == "T1059"
    mock_sleep.assert_called_once()

@patch("app.services.classifier.time.sleep", return_value=None)
def test_retry_three_parser_failures(mock_sleep):
    """Parser keeps failing untill retries exhausted."""
    with patch(
        "app.services.classifier._invoke_chain",
        side_effect=OutputParserException("bad json")
    ):
        with pytest.raises(OutputParserException):
            _invoke_with_retry("alert", "context")

    assert mock_sleep.call_count == 2

def test_connection_error_returns_error_result():
    """ConnectionError returns an error TechniqueResult."""
    with patch(
        "app.services.classifier._invoke_chain",
        side_effect = ConnectionError,
    ):
        response = _invoke_with_retry("alert", "context")

    assert response.path == "error"
    assert response.technique_id == "ERROR"
    assert response.confidence == 0.0