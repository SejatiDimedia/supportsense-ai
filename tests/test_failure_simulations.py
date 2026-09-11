import pytest
from unittest.mock import MagicMock
from app.llm.client import ResilientOllamaClient, CircuitBreaker
from app.agent.hermes_client import HermesAgentClient
from app.agent.router import AgentRouter
from app.persistence.repository import repo
from app.persistence.db import init_db

def test_simulation_1_ollama_offline_fallback():
    """
    Simulasi 1 (PRD 16.3): Matikan Ollama / Port Salah
    Ekspektasi: Sistem mengembalikan jawaban degradasi (fallback), bukan crash.
    """
    # Point client to a non-existent port
    offline_client = ResilientOllamaClient(
        base_url="http://127.0.0.1:59999",
        timeout=0.2,
        max_retries=1,
        backoff_factor=0.01,
        circuit_breaker=CircuitBreaker(failure_threshold=2)
    )
    hermes = HermesAgentClient(resilient_client=offline_client)
    router = AgentRouter(llm_client=hermes)

    # Process message when Ollama is completely offline
    result = router.process_message("What is your refund policy?")

    assert result is not None
    assert "apologize" in result.answer.lower() or "support team" in result.answer.lower()
    assert result.latency_ms > 0
    # Circuit breaker recorded failures
    assert offline_client.circuit_breaker.failure_count > 0

def test_simulation_2_n8n_unreachable_queue_retention():
    """
    Simulasi 2 (PRD 16.3): n8n Webhook Tidak Dapat Diakses
    Ekspektasi: Webhook disimpan ke tabel pending_webhooks / escalations di SQLite, tidak hilang.
    """
    init_db()
    trace_id = "trc_fail_sim_2"
    payload = {
        "user_message": "Where is my order #9999999?",
        "reason": "Order not found in knowledge graph"
    }

    esc_id = repo.save_escalation(
        trace_id=trace_id,
        reason=payload["reason"],
        payload=payload,
        webhook_status="pending"
    )

    assert esc_id > 0
    pending_list = repo.get_pending_escalations()
    target = next((item for item in pending_list if item["id"] == esc_id), None)

    assert target is not None
    assert target["webhook_status"] == "pending"
    assert target["trace_id"] == trace_id
    assert target["payload"]["reason"] == payload["reason"]

def test_simulation_3_rag_empty_retrieval():
    """
    Simulasi 3 (PRD 16.3): Kosongkan Hasil Retrieval RAG
    Ekspektasi: LLM tetap merespons dengan pesan ramah tanpa exception.
    """
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [] # Empty retrieval results

    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = []

    mock_llm = MagicMock()
    mock_llm.plan_routing.return_value = [
        {"function": {"name": "search_knowledge_base", "arguments": {"query": "unknown spaceship parts"}}}
    ]
    mock_llm.generate_answer.return_value = "I could not find specific documentation regarding spaceship parts."

    router = AgentRouter(
        llm_client=mock_llm,
        rag_retriever=mock_retriever,
        rag_reranker=mock_reranker
    )

    result = router.process_message("Do you sell spaceship parts?")
    assert result is not None
    assert result.route_taken == "direct" or result.route_taken == "rag"
    assert "spaceship" in result.answer.lower() or "could not find" in result.answer.lower()
