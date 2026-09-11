import time
import uuid
import logging
import re
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

from app.agent.hermes_client import HermesAgentClient
from app.rag.retriever import RAGRetriever
from app.rag.reranker import CrossEncoderReranker
from app.kag.graph_query import GraphQueryEngine, extract_order_number

from app.observability.logger import set_trace_id, log_event
from app.observability.metrics import metrics
from app.persistence.repository import repo
from app.escalation.confidence import should_escalate, calculate_confidence_score
from app.escalation.webhook_client import N8nWebhookClient

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
        webhook_client: Optional[N8nWebhookClient] = None,
    ):
        self.llm = llm_client or HermesAgentClient()
        self.retriever = rag_retriever or RAGRetriever()
        self.reranker = rag_reranker or CrossEncoderReranker()
        self.kag = kag_engine or GraphQueryEngine()
        self.webhook = webhook_client or N8nWebhookClient()

    def process_message(self, user_message: str, session_id: Optional[str] = None) -> ChatResult:
        start_time = time.time()
        trace_id = str(uuid.uuid4())[:8]
        set_trace_id(trace_id)
        effective_session = session_id or f"sess_{trace_id}"

        log_event(logger, "message_received", layer="agent.router", message=f"Received user message: '{user_message}' (session: {effective_session})")

        # 0. Ambil riwayat percakapan sesi (sliding window 12 pesan terbaru untuk LLM)
        chat_history = repo.get_recent_history(effective_session, limit=12)

        # Deteksi nomor order aktif: utamakan pesan saat ini, fallback ke riwayat panjang sesi (tanpa batas 4 pertanyaan)
        extracted_order = extract_order_number(user_message)
        active_session_order = None
        if not extracted_order:
            active_session_order = repo.get_session_active_order(effective_session, max_lookback=100)

        order_in_scope = extracted_order or active_session_order

        # 1. Deteksi cepat sapaan / closing (Greeting pre-filter untuk rute direct)
        lower_msg = user_message.lower()
        greetings = [
            "hi", "hello", "hey", "halo", "hai",
            "good morning", "good afternoon", "good evening", "good night",
            "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
            "terima kasih", "makasih", "thank you", "thanks"
        ]
        clean_text = lower_msg.strip("!.,? ")
        is_greeting = clean_text in greetings or any(
            g in lower_msg for g in [
                "hello", "good morning", "good afternoon", "good evening", "hi there",
                "halo", "hai", "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
                "terima kasih", "makasih"
            ]
        )
        substantive_keywords = [
            "order", "refund", "warranty", "ship", "product", "policy", "damage",
            "broken", "delay", "ticket", "agen", "kurir", "resi", "barang",
            "status", "pesanan", "retur", "garansi"
        ]
        has_substantive_question = ("#" in lower_msg) or any(
            re.search(rf"\b{re.escape(k)}\b", lower_msg) for k in substantive_keywords
        )

        if is_greeting and not has_substantive_question:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            if any(t in lower_msg for t in ["terima kasih", "makasih", "thank"]):
                answer = "Sama-sama! Senang bisa membantu Anda. Jika ada pertanyaan lain seputar pesanan atau layanan kami, jangan ragu untuk bertanya."
            elif any(t in lower_msg for t in ["halo", "hai", "selamat pagi", "selamat siang", "selamat sore", "selamat malam"]):
                answer = "Halo! Selamat datang di SupportSense AI. Ada yang bisa saya bantu terkait pesanan, produk, atau kebijakan kami hari ini?"
            else:
                answer = "Hello! Welcome to SupportSense AI. How can I assist you with your orders, products, or company policies today?"
            metrics.record_request("direct", latency_ms)
            try:
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="user",
                    message=user_message,
                    route_taken="direct",
                    confidence_score=1.0
                )
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="assistant",
                    message=answer,
                    route_taken="direct",
                    confidence_score=1.0
                )
            except Exception as e:
                logger.error(f"Error persisting greeting to SQLite: {e}", exc_info=True)

            return ChatResult(
                trace_id=trace_id,
                answer=answer,
                route_taken="direct",
                confidence_score=1.0,
                escalated=False,
                latency_ms=latency_ms,
                context_used="Direct greeting handler."
            )

        # 2. Deteksi cepat keamanan (Security check sederhana untuk bypass / hack)
        if any(keyword in lower_msg for keyword in ["hack", "bypass", "reset password manually", "override database"]):
            latency_ms = round((time.time() - start_time) * 1000, 2)
            answer = "For security and compliance reasons, automated credential resets or manual account overrides cannot be performed via chat. Your request has been escalated to our Security & Fraud Prevention team."
            confidence = calculate_confidence_score("escalated", has_rag_context=False, is_malicious=True)
            metrics.record_request("escalated", latency_ms)
            try:
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="user",
                    message=user_message,
                    route_taken="escalated",
                    confidence_score=confidence
                )
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="assistant",
                    message=answer,
                    route_taken="escalated",
                    confidence_score=confidence
                )
                self.webhook.send_escalation_webhook(
                    trace_id=trace_id,
                    reason="Security trigger: unauthorized action or injection attempt requested.",
                    user_message=user_message,
                    session_id=effective_session,
                    route_taken="escalated",
                    confidence_score=confidence
                )
            except Exception as e:
                logger.error(f"Error persisting security escalation to SQLite: {e}", exc_info=True)

            return ChatResult(
                trace_id=trace_id,
                answer=answer,
                route_taken="escalated",
                confidence_score=confidence,
                escalated=True,
                latency_ms=latency_ms,
                context_used="Security trigger: unauthorized action requested."
            )

        # 3. Deteksi cepat out-of-domain (pertanyaan umum di luar lingkup customer support)
        out_of_domain_topics = [
            "presiden", "perdana menteri", "menteri", "gubernur", "pemilu", "pilpres", "partai", "dpr",
            "ibukota", "sejarah", "perang dunia", "kemerdekaan", "lagu", "lirik", "chord",
            "resep masakan", "cuaca hari ini", "prakiraan cuaca", "puisi", "pantun", "cerpen",
            "film", "bioskop", "artis", "selebriti", "zodiak", "ramalan", "gempa", "tsunami"
        ]
        is_out_of_domain = any(topic in lower_msg for topic in out_of_domain_topics)
        if is_out_of_domain and not has_substantive_question and not order_in_scope:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            answer = (
                "Maaf, saya adalah asisten AI khusus customer support SupportSense AI. "
                "Layanan saya dibatasi untuk membantu informasi pesanan (#XXXX), produk, status pengiriman, "
                "garansi, komplain paket, serta kebijakan retur dan pengembalian dana kami. "
                "Pertanyaan di luar topik tersebut (seperti sejarah, politik, atau pengetahuan umum) tidak dapat saya jawab. "
                "Apakah ada yang bisa saya bantu terkait pesanan atau layanan kami?"
            )
            metrics.record_request("direct", latency_ms)
            try:
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="user",
                    message=user_message,
                    route_taken="direct",
                    confidence_score=1.0
                )
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="assistant",
                    message=answer,
                    route_taken="direct",
                    confidence_score=1.0
                )
            except Exception as e:
                logger.error(f"Error persisting out-of-domain refusal to SQLite: {e}", exc_info=True)

            return ChatResult(
                trace_id=trace_id,
                answer=answer,
                route_taken="direct",
                confidence_score=1.0,
                escalated=False,
                latency_ms=latency_ms,
                context_used="Deterministic out-of-domain guardrail."
            )

        # 4. Minta LLM merencanakan tools yang dibutuhkan (didukung chat_history)
        tool_calls = self.llm.plan_routing(user_message, chat_history=chat_history)
        tool_names = [call.get("function", {}).get("name") for call in tool_calls]

        # Cadangan 1: jika ada nomor order eksplisit di pesan saat ini
        if extracted_order and "lookup_relational_data" not in tool_names:
            tool_names.append("lookup_relational_data")

        # Cadangan 2: Multi-turn follow-up jika user menanyakan detail terkait pesanan aktif di sesi
        order_related_keywords = [
            "refund", "agent", "agen", "kurir", "courier", "track", "resi", "status",
            "barang", "product", "paket", "package", "kirim", "ship", "lost", "hilang",
            "rusak", "damage", "rma", "ganti", "pengganti", "dana", "money", "uang", "pic", "kapan", "estimasi"
        ]
        is_order_followup = bool(
            active_session_order and any(
                re.search(rf"\b{re.escape(k)}\b", lower_msg) for k in order_related_keywords
            )
        )
        if is_order_followup and "lookup_relational_data" not in tool_names:
            tool_names.append("lookup_relational_data")

        rag_context = ""
        kag_context = ""
        route_taken = "direct"
        escalated = False
        confidence = 0.85
        order_found = None

        # 4. Eksekusi KAG jika diminta
        if "lookup_relational_data" in tool_names:
            order_to_query = order_in_scope
            if not order_to_query:
                # Cari nomor order dari argumen tool call LLM
                for call in tool_calls:
                    if call.get("function", {}).get("name") == "lookup_relational_data":
                        raw_arg = call.get("function", {}).get("arguments", {}).get("order_number")
                        if raw_arg:
                            order_to_query = extract_order_number(raw_arg) or raw_arg
                            break

            if order_to_query:
                kag_result = self.kag.query_order_context(order_to_query)
                kag_context = kag_result["summary"]
                order_found = kag_result["found"]
                if not order_found:
                    # Order tidak ada di database relasional kita
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
            # Relevansi minimal: jika skor cross-encoder sangat negatif (< -7.0), abaikan dokumen yang tidak relevan
            valid_chunks = [
                c for c in reranked
                if not isinstance(getattr(c, "score", None), (int, float)) or getattr(c, "score", 0) >= -7.0
            ]
            if valid_chunks:
                rag_context = "\n\n".join([f"[{c.metadata.get('source')} - {c.metadata.get('section')}]:\n{c.text}" for c in valid_chunks])

        # 5. Cek apakah ada eskalasi eksplisit
        if "escalate_to_human" in tool_names:
            escalated = True

        # 6. Tentukan Rute Final & Confidence
        if escalated:
            route_taken = "escalated"
            confidence = calculate_confidence_score("escalated", has_rag_context=bool(rag_context), order_found=order_found)
        elif rag_context and kag_context:
            route_taken = "hybrid"
            confidence = calculate_confidence_score("hybrid", has_rag_context=True)
        elif kag_context:
            route_taken = "kag"
            confidence = calculate_confidence_score("kag", has_rag_context=False)
        elif rag_context:
            route_taken = "rag"
            confidence = calculate_confidence_score("rag", has_rag_context=True)
        else:
            route_taken = "direct"
            confidence = 0.70

        if should_escalate(confidence, route_taken):
            escalated = True
            route_taken = "escalated"

        # Strict Out-of-Context Guardrail:
        # Jika tidak ada tool yang dipanggil, tidak ada konteks RAG/KAG, dan tidak ada intensi customer support
        if not tool_names and not kag_context and not rag_context and not has_substantive_question and not order_in_scope:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            answer = (
                "Maaf, saya adalah asisten AI khusus customer support SupportSense AI. "
                "Layanan saya terbatas hanya untuk menjawab pertanyaan terkait layanan pelanggan kami: "
                "informasi pesanan (#XXXX), produk, status pengiriman, garansi, komplain paket, "
                "serta kebijakan retur dan pengembalian dana. "
                "Pertanyaan di luar konteks layanan pelanggan tidak dapat saya jawab. "
                "Apakah ada yang bisa saya bantu terkait pesanan atau produk kami?"
            )
            metrics.record_request("direct", latency_ms)
            try:
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="user",
                    message=user_message,
                    route_taken="direct",
                    confidence_score=1.0
                )
                repo.save_message(
                    trace_id=trace_id,
                    session_id=effective_session,
                    role="assistant",
                    message=answer,
                    route_taken="direct",
                    confidence_score=1.0
                )
            except Exception as e:
                logger.error(f"Error persisting out-of-context refusal to SQLite: {e}", exc_info=True)

            return ChatResult(
                trace_id=trace_id,
                answer=answer,
                route_taken="direct",
                confidence_score=1.0,
                escalated=False,
                latency_ms=latency_ms,
                context_used="Strict out-of-context guardrail: inquiry has no customer support context."
            )

        # 7. Gabungkan Konteks & Sintesis Jawaban Akhir
        combined_context = ""
        if kag_context:
            combined_context += f"=== RELATIONAL DATA (KAG) ===\n{kag_context}\n\n"
        if rag_context:
            combined_context += f"=== POLICY & DOCUMENTATION (RAG) ===\n{rag_context}\n\n"

        if not combined_context.strip():
            combined_context = "No specific documentation or order details found for this inquiry."

        answer = self.llm.generate_answer(user_message, combined_context, chat_history=chat_history)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Record observability metrics
        metrics.record_request(route_taken, latency_ms)

        # Auto-persist conversation & escalation to SQLite database
        try:
            repo.save_message(
                trace_id=trace_id,
                session_id=effective_session,
                role="user",
                message=user_message,
                route_taken=route_taken,
                confidence_score=confidence
            )
            repo.save_message(
                trace_id=trace_id,
                session_id=effective_session,
                role="assistant",
                message=answer,
                route_taken=route_taken,
                confidence_score=confidence
            )
            if escalated:
                self.webhook.send_escalation_webhook(
                    trace_id=trace_id,
                    reason=f"Route: {route_taken}, Confidence: {confidence:.2f}",
                    user_message=user_message,
                    session_id=effective_session,
                    route_taken=route_taken,
                    confidence_score=confidence
                )
        except Exception as e:
            logger.error(f"Error persisting to SQLite: {e}", exc_info=True)

        return ChatResult(
            trace_id=trace_id,
            answer=answer,
            route_taken=route_taken,
            confidence_score=confidence,
            escalated=escalated,
            latency_ms=latency_ms,
            context_used=combined_context
        )