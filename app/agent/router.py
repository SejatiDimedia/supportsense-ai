import time
import uuid
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

from app.agent.hermes_client import HermesAgentClient
from app.rag.retriever import RAGRetriever
from app.rag.reranker import CrossEncoderReranker
from app.kag.graph_query import GraphQueryEngine, extract_order_number

logger = logging.getLogger(__name__)

@dataclass
class ChatResult:
    trace_id: str
    answer: str
    route_taken: str  # 'rag' | 'kag' | 'hybrid' | 'escalated' | 'direct'
    confidence_score: float
    escalated: bool
    latency_ms: float
    context_used: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentRouter:
    """
    Central Orchestrator: Menghubungkan RAG, KAG, dan LLM
    tanpa melanggar aturan separation of concerns.
    """
    def __init__(
        self,
        llm_client: Optional[HermesAgentClient] = None,
        rag_retriever: Optional[RAGRetriever] = None,
        rag_reranker: Optional[CrossEncoderReranker] = None,
        kag_engine: Optional[GraphQueryEngine] = None,
    ):
        self.llm = llm_client or HermesAgentClient()
        self.retriever = rag_retriever or RAGRetriever()
        self.reranker = rag_reranker or CrossEncoderReranker()
        self.kag = kag_engine or GraphQueryEngine()

    def process_message(self, user_message: str, session_id: Optional[str] = None) -> ChatResult:
        start_time = time.time()
        trace_id = str(uuid.uuid4())[:8]

        logger.info(f"[{trace_id}] Received user message: '{user_message}' (session: {session_id})")

        # 1. Deteksi cepat sapaan (Greeting pre-filter untuk rute direct)
        lower_msg = user_message.lower()
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "halo"]
        clean_text = lower_msg.strip("!.,? ")
        is_greeting = clean_text in greetings or any(g in lower_msg for g in ["hello", "good morning", "good afternoon", "good evening", "hi there"])
        substantive_keywords = ["order", "refund", "warranty", "ship", "product", "policy", "damage", "broken", "delay", "ticket", "#"]
        has_substantive_question = any(k in lower_msg for k in substantive_keywords)

        if is_greeting and not has_substantive_question:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return ChatResult(
                trace_id=trace_id,
                answer="Hello! Welcome to SupportSense AI. How can I assist you with your orders, products, or company policies today?",
                route_taken="direct",
                confidence_score=1.0,
                escalated=False,
                latency_ms=latency_ms,
                context_used="Direct greeting handler."
            )

        # 2. Deteksi cepat keamanan (Security check sederhana untuk bypass / hack)
        if any(keyword in lower_msg for keyword in ["hack", "bypass", "reset password manually", "override database"]):
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return ChatResult(
                trace_id=trace_id,
                answer="For security and compliance reasons, automated credential resets or manual account overrides cannot be performed via chat. Your request has been escalated to our Security & Fraud Prevention team.",
                route_taken="escalated",
                confidence_score=0.20,
                escalated=True,
                latency_ms=latency_ms,
                context_used="Security trigger: unauthorized action requested."
            )

        # 2. Minta LLM merencanakan tools yang dibutuhkan
        tool_calls = self.llm.plan_routing(user_message)
        tool_names = [call.get("function", {}).get("name") for call in tool_calls]

        # Cadangan: jika LLM lupa panggil KAG tapi teks jelas menyebut order #1234
        extracted_order = extract_order_number(user_message)
        if extracted_order and "lookup_relational_data" not in tool_names:
            tool_names.append("lookup_relational_data")

        rag_context = ""
        kag_context = ""
        route_taken = "direct"
        escalated = False
        confidence = 0.85

        # 3. Eksekusi KAG jika diminta
        if "lookup_relational_data" in tool_names:
            order_to_query = extracted_order
            if not order_to_query:
                # Cari nomor order dari argumen tool call LLM
                for call in tool_calls:
                    if call.get("function", {}).get("name") == "lookup_relational_data":
                        order_to_query = call.get("function", {}).get("arguments", {}).get("order_number")
                        break

            if order_to_query:
                kag_result = self.kag.query_order_context(order_to_query)
                kag_context = kag_result["summary"]
                if not kag_result["found"]:
                    # Order tidak ada di database relasional kita
                    confidence = 0.40
                    escalated = True

        # 4. Eksekusi RAG jika diminta
        if "search_knowledge_base" in tool_names or not tool_names:
            # Query semantik
            search_query = user_message
            for call in tool_calls:
                if call.get("function", {}).get("name") == "search_knowledge_base":
                    search_query = call.get("function", {}).get("arguments", {}).get("query", user_message)
                    break

            retrieved = self.retriever.retrieve(search_query, top_k=5)
            reranked = self.reranker.rerank(search_query, retrieved, top_n=2)
            if reranked:
                rag_context = "\n\n".join([f"[{c.metadata.get('source')} - {c.metadata.get('section')}]:\n{c.text}" for c in reranked])

        # 5. Cek apakah ada eskalasi eksplisit
        if "escalate_to_human" in tool_names:
            escalated = True
            confidence = 0.30

        # 6. Tentukan Rute Final
        if escalated:
            route_taken = "escalated"
        elif rag_context and kag_context:
            route_taken = "hybrid"
            confidence = 0.95
        elif kag_context:
            route_taken = "kag"
            confidence = 0.92
        elif rag_context:
            route_taken = "rag"
            confidence = 0.89
        else:
            route_taken = "direct"
            confidence = 0.70

        # 7. Gabungkan Konteks & Sintesis Jawaban Akhir
        combined_context = ""
        if kag_context:
            combined_context += f"=== RELATIONAL DATA (KAG) ===\n{kag_context}\n\n"
        if rag_context:
            combined_context += f"=== POLICY & DOCUMENTATION (RAG) ===\n{rag_context}\n\n"

        if not combined_context.strip():
            combined_context = "No specific documentation or order details found for this inquiry."

        answer = self.llm.generate_answer(user_message, combined_context)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return ChatResult(
            trace_id=trace_id,
            answer=answer,
            route_taken=route_taken,
            confidence_score=confidence,
            escalated=escalated,
            latency_ms=latency_ms,
            context_used=combined_context
        )