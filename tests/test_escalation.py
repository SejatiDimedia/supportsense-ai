import pytest
from unittest.mock import MagicMock, patch
from app.escalation.confidence import should_escalate, calculate_confidence_score
from app.escalation.webhook_client import N8nWebhookClient
from app.persistence.db import init_db
from app.persistence.repository import repo

def test_confidence_evaluation_rules():
    # Less than 0.60 threshold
    assert should_escalate(0.55, "rag") is True
    assert should_escalate(0.40, "kag") is True
    # Normal routes above threshold
    assert should_escalate(0.89, "rag") is False
    assert should_escalate(0.95, "hybrid") is False
    # Route is explicitly escalated
    assert should_escalate(0.90, "escalated") is True
    # Security trigger
    assert should_escalate(0.99, "direct", is_security_trigger=True) is True

    # Calculation logic
    assert calculate_confidence_score("hybrid", has_rag_context=True) == 0.95
    assert calculate_confidence_score("kag", has_rag_context=False) == 0.92
    assert calculate_confidence_score("rag", has_rag_context=True) == 0.89
    assert calculate_confidence_score("escalated", has_rag_context=False, order_found=False) == 0.40
    assert calculate_confidence_score("escalated", has_rag_context=False, is_malicious=True) == 0.20

def test_webhook_dispatch_offline_fallback():
    init_db()
    # Webhook pointing to closed port
    client = N8nWebhookClient(webhook_url="http://127.0.0.1:59998/webhook/test", timeout=0.1)

    result = client.send_escalation_webhook(
        trace_id="trc_offline_esc",
        reason="Test n8n offline",
        user_message="My account is locked",
        session_id="sess_offline_1",
        route_taken="escalated",
        confidence_score=0.25
    )

    assert result["status"] == "pending"
    assert result["queued_locally"] is True

    # Verify it exists in SQLite pending queue
    pending = repo.get_pending_escalations()
    found = [p for p in pending if p["id"] == result["escalation_id"]]
    assert len(found) == 1
    assert found[0]["trace_id"] == "trc_offline_esc"

@patch("httpx.Client.post")
def test_webhook_background_retry_recovery(mock_post):
    init_db()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "application/json"}
    mock_resp.json.return_value = {"status": "ticket_created", "ticket_id": "TICK-1234"}
    mock_post.return_value = mock_resp

    client = N8nWebhookClient(webhook_url="http://localhost:5678/webhook/escalation")

    # Queue an item
    esc_id = repo.save_escalation("trc_retry_test", "Order dispute", {"order": "#4521"}, "pending")

    # Process queue
    recovered_count = client.process_pending_retries(max_items=5)
    assert recovered_count >= 1

    # Verify it's no longer pending
    pending_after = repo.get_pending_escalations()
    assert not any(p["id"] == esc_id for p in pending_after)
