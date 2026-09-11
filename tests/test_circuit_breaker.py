import time
import pytest
from unittest.mock import MagicMock, patch
from app.llm.models import CircuitState, LLMResponse
from app.llm.client import CircuitBreaker, ResilientOllamaClient, FALLBACK_ANSWER

def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 1st failure
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1

    # 2nd failure
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 2

    # 3rd failure -> TRIPS to OPEN!
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 3
    assert cb.can_execute() is False

    # Wait for recovery timeout
    time.sleep(0.25)
    assert cb.can_execute() is True # Transitions to HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN

    # Success in HALF_OPEN -> Transitions to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

def test_resilient_client_open_circuit_immediate_fallback():
    mock_cb = MagicMock()
    mock_cb.can_execute.return_value = False # Circuit is OPEN

    client = ResilientOllamaClient(circuit_breaker=mock_cb)
    resp = client.chat(messages=[{"role": "user", "content": "hi"}])

    assert resp.is_fallback is True
    assert resp.content == FALLBACK_ANSWER
    assert "Circuit breaker is OPEN" in resp.error

@patch("httpx.Client.post")
def test_resilient_client_retry_logic(mock_post):
    # First call raises connection error, second call succeeds
    mock_fail = MagicMock()
    mock_fail.raise_for_status.side_effect = Exception("Connection refused")

    mock_ok = MagicMock()
    mock_ok.raise_for_status.return_value = None
    mock_ok.json.return_value = {
        "message": {"content": "Hello after retry!", "tool_calls": []}
    }

    mock_post.side_effect = [Exception("Connection refused"), mock_ok]

    client = ResilientOllamaClient(max_retries=1, backoff_factor=0.01)
    resp = client.chat(messages=[{"role": "user", "content": "hello"}])

    assert resp.is_fallback is False
    assert resp.content == "Hello after retry!"
    assert mock_post.call_count == 2
