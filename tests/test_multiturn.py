import pytest
from app.agent.router import AgentRouter
from app.persistence.repository import repo

def test_multiturn_order_context_retention():
    router = AgentRouter()
    session_id = "test_multiturn_ci_sess_1"

    # Turn 1: Explicit order inquiry
    turn1 = router.process_message("Where is my order #4534?", session_id=session_id)
    assert turn1.route_taken in ["kag", "hybrid"]
    assert "4534" in turn1.answer or "Lost in Transit" in turn1.answer

    # Verify history is saved
    history = repo.get_history(session_id)
    assert len(history) >= 2

    # Turn 2: Follow-up question without repeating order number
    turn2 = router.process_message("Berapa nominal refund yang disetujui dan siapa agennya?", session_id=session_id)
    assert turn2.route_taken in ["kag", "hybrid"]
    assert "4534" in turn2.context_used
    assert "Siti Rahma" in turn2.context_used
    assert "1.899.000" in turn2.context_used

    # Turn 3: Follow-up question about shipping carrier
    turn3 = router.process_message("Kurirnya menggunakan apa?", session_id=session_id)
    assert turn3.route_taken in ["kag", "hybrid"]
    assert "FedEx" in turn3.context_used

    # Turn 4: Courtesy closing
    turn4 = router.process_message("Terima kasih banyak", session_id=session_id)
    assert turn4.route_taken == "direct"
    assert "Sama-sama" in turn4.answer or "membantu" in turn4.answer
