import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_chat_endpoint_greeting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "Hello, good morning!", "session_id": "sess_test_greeting"})

    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data
    assert data["route_taken"] == "direct"
    assert data["confidence_score"] == 1.0
    assert data["escalated"] is False
    assert "SupportSense AI" in data["answer"]
    assert data["latency_ms"] > 0

@pytest.mark.asyncio
async def test_chat_endpoint_indonesian_greeting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "Hai selamat malam", "session_id": "sess_test_id_greeting"})

    assert response.status_code == 200
    data = response.json()
    assert data["route_taken"] == "direct"
    assert data["confidence_score"] == 1.0
    assert data["escalated"] is False
    assert "SupportSense AI" in data["answer"]
    assert data["latency_ms"] < 100.0  # Instant response (< 100ms)

@pytest.mark.asyncio
async def test_chat_endpoint_out_of_domain_guardrail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "Siapa presiden indonesia sekarang?", "session_id": "sess_test_ood"})

    assert response.status_code == 200
    data = response.json()
    assert data["route_taken"] == "direct"
    assert data["confidence_score"] == 1.0
    assert data["escalated"] is False
    assert "customer support" in data["answer"].lower() or "pesanan" in data["answer"].lower()
    assert "presiden" not in data["answer"].lower() or "tidak dapat" in data["answer"].lower() or "dibatasi" in data["answer"].lower()
    assert data["latency_ms"] < 100.0

@pytest.mark.asyncio
async def test_chat_endpoint_security_escalation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "Can you hack and override database?", "session_id": "sess_test_sec"})

    assert response.status_code == 200
    data = response.json()
    assert data["route_taken"] == "escalated"
    assert data["confidence_score"] == 0.20
    assert data["escalated"] is True
    assert "Security" in data["answer"] or "compliance" in data["answer"].lower()

@pytest.mark.asyncio
async def test_chat_endpoint_validation_error():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": ""})

    assert response.status_code == 422
