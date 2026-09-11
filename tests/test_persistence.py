import pytest
from app.persistence.db import init_db
from app.persistence.repository import repo

def test_sqlite_persistence_flow():
    init_db()

    # 1. Test saving conversation messages
    sess_id = "test_sess_999"
    msg_id1 = repo.save_message(
        trace_id="trc_001",
        session_id=sess_id,
        role="user",
        message="Hello testing DB",
        route_taken="direct",
        confidence_score=1.0
    )
    assert msg_id1 > 0

    msg_id2 = repo.save_message(
        trace_id="trc_001",
        session_id=sess_id,
        role="assistant",
        message="Hello! How can I help?",
        route_taken="direct",
        confidence_score=1.0
    )
    assert msg_id2 > msg_id1

    # 2. Test reading history
    history = repo.get_history(sess_id)
    assert len(history) >= 2
    assert history[0]["role"] == "user"
    assert history[0]["message"] == "Hello testing DB"
    assert history[1]["role"] == "assistant"

    # 3. Test saving and retrieving escalation
    esc_id = repo.save_escalation(
        trace_id="trc_esc_002",
        reason="Order not found #9999999",
        payload={"order": "#9999999", "user": "test_user"},
        webhook_status="pending"
    )
    assert esc_id > 0

    pending = repo.get_pending_escalations()
    matching = [p for p in pending if p["id"] == esc_id]
    assert len(matching) == 1
    assert matching[0]["trace_id"] == "trc_esc_002"
    assert matching[0]["payload"]["order"] == "#9999999"

    # 4. Test updating escalation status
    repo.update_escalation_status(esc_id, status="sent")
    pending_after = repo.get_pending_escalations()
    assert not any(p["id"] == esc_id for p in pending_after)
