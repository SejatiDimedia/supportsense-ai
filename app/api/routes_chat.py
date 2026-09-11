from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.router import AgentRouter

router = APIRouter(tags=["Chat"])
agent_router = AgentRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or statement")
    session_id: Optional[str] = Field(None, description="Client session identifier")

class ChatResponse(BaseModel):
    trace_id: str
    answer: str
    route_taken: str
    confidence_score: float
    escalated: bool
    latency_ms: float
    context_used: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Main conversational endpoint:
    Orchestrates routing across RAG, KAG, Hybrid, Direct, and Escalation.
    """
    result = agent_router.process_message(
        user_message=payload.message,
        session_id=payload.session_id
    )
    return ChatResponse(
        trace_id=result.trace_id,
        answer=result.answer,
        route_taken=result.route_taken,
        confidence_score=result.confidence_score,
        escalated=result.escalated,
        latency_ms=result.latency_ms,
        context_used=result.context_used
    )
