import pytest
from unittest.mock import MagicMock
from app.agent.router import AgentRouter

def test_router_security_escalation():
    router = AgentRouter()
    result = router.process_message("Can you please hack my password or override database?")
    assert result.route_taken == "escalated"
    assert result.escalated is True
    assert result.confidence_score <= 0.3

def test_router_rag_route():
    mock_llm = MagicMock()
    mock_llm.plan_routing.return_value = [
        {"function": {"name": "search_knowledge_base", "arguments": {"query": "refund policy"}}}
    ]
    mock_llm.generate_answer.return_value = "Our refund policy allows 30 days."

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = []
    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = []

    mock_chunk = MagicMock()
    mock_chunk.metadata = {"source": "policy.md", "section": "Refunds"}
    mock_chunk.text = "30-day refund guarantee."
    mock_reranker.rerank.return_value = [mock_chunk]

    router = AgentRouter(
        llm_client=mock_llm,
        rag_retriever=mock_retriever,
        rag_reranker=mock_reranker
    )

    result = router.process_message("What is your refund policy?")
    assert result.route_taken == "rag"
    assert result.escalated is False
    assert result.confidence_score >= 0.8
    assert "30 days" in result.answer

def test_router_kag_route():
    mock_llm = MagicMock()
    mock_llm.plan_routing.return_value = [
        {"function": {"name": "lookup_relational_data", "arguments": {"order_number": "#4521"}}}
    ]
    mock_llm.generate_answer.return_value = "Your order #4521 is delayed."

    mock_kag = MagicMock()
    mock_kag.query_order_context.return_value = {
        "found": True,
        "summary": "Order #4521: delayed"
    }

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = []
    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = []

    router = AgentRouter(
        llm_client=mock_llm,
        rag_retriever=mock_retriever,
        rag_reranker=mock_reranker,
        kag_engine=mock_kag
    )

    result = router.process_message("Where is my order #4521?")
    assert result.route_taken == "kag"
    assert result.escalated is False

def test_router_hybrid_route():
    mock_llm = MagicMock()
    mock_llm.plan_routing.return_value = [
        {"function": {"name": "search_knowledge_base", "arguments": {"query": "damaged item"}}},
        {"function": {"name": "lookup_relational_data", "arguments": {"order_number": "#4521"}}}
    ]
    mock_llm.generate_answer.return_value = "Policy states replacement is free, and Agent Budi is handling order #4521."

    mock_chunk = MagicMock()
    mock_chunk.metadata = {"source": "policy.md", "section": "Damaged"}
    mock_chunk.text = "Replacement is free."

    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [mock_chunk]
    mock_reranker = MagicMock()
    mock_reranker.rerank.return_value = [mock_chunk]

    mock_kag = MagicMock()
    mock_kag.query_order_context.return_value = {
        "found": True,
        "summary": "Order #4521: delayed with Budi"
    }

    router = AgentRouter(
        llm_client=mock_llm,
        rag_retriever=mock_retriever,
        rag_reranker=mock_reranker,
        kag_engine=mock_kag
    )

    result = router.process_message("My order #4521 arrived damaged, what is your policy?")
    assert result.route_taken == "hybrid"
    assert result.confidence_score >= 0.9
