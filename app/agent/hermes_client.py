import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

from app.llm.client import ResilientOllamaClient

logger = logging.getLogger(__name__)

# 1. Definisi Tools sesuai standar Ollama / OpenAI function-calling
SUPPORT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Cari dokumen kebijakan perusahaan, garansi produk, prosedur pengembalian dana (refund), barang rusak, atau FAQ umum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kata kunci atau topik pencarian semantik (misal: 'refund policy', 'product warranty length')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_relational_data",
            "description": "Cari data relasional pesanan spesifik, status pengiriman kurir, komplain aktif, dan agen PIC yang menangani.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "Nomor pesanan spesifik yang ditanyakan (contoh format: #XXXX). Gunakan nomor pesanan dari konteks percakapan jika ini pertanyaan lanjutan."
                    }
                },
                "required": ["order_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Eskalasi ke agen manusia jika pertanyaan meminta aksi terlarang (reset password langsung, hack akun), komplain di luar SOP, atau pengguna sangat frustrasi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Alasan singkat mengapa percakapan harus dieskalasi ke manusia"
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

ROUTER_SYSTEM_PROMPT = """You are an expert AI Customer Support Routing Agent.
Analyze the user's inquiry and conversation history, then decide which tools to call:
1. Call 'search_knowledge_base' for general policies, warranties, returns, refunds, FAQs, or damaged package rules.
2. Call 'lookup_relational_data' if the user mentions an order number (#XXXX) or asks follow-up questions about an order previously discussed (status, refund amount, courier, tracking, agent, etc.).
3. If the question involves BOTH a general policy AND a specific order, call BOTH tools (Hybrid route).
4. Call 'escalate_to_human' if the inquiry asks for dangerous/impossible tasks (bypassing security, manual database overrides, abusive requests) or is completely unanswerable.
5. If it's a simple greeting or acknowledgment like 'hi', 'hello', or 'thanks', you may answer directly without calling any tools."""


class HermesAgentClient:
    """
    Klien pemanggil Ollama Chat API yang menangani pemanggilan tool (function calling)
    dan pembentukan jawaban akhir (response synthesis), dilindungi oleh ResilientOllamaClient.
    Mendukung riwayat percakapan (chat history) untuk kesinambungan multi-turn.
    """
    def __init__(self, resilient_client: Optional[ResilientOllamaClient] = None):
        self.client = resilient_client or ResilientOllamaClient()

    def plan_routing(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Mengirim pesan user dan riwayat percakapan ke Ollama dengan daftar SUPPORT_TOOLS.
        Mengembalikan daftar tool calls yang diputuskan oleh LLM.
        """
        messages = [{"role": "system", "content": ROUTER_SYSTEM_PROMPT}]

        if chat_history:
            for h in chat_history[-4:]:
                r = h.get("role", "user")
                c = h.get("message", "")
                if r in ("user", "assistant") and c:
                    messages.append({"role": r, "content": c})

        messages.append({"role": "user", "content": user_message})
        resp = self.client.chat(messages=messages, tools=SUPPORT_TOOLS, temperature=0.0)
        return resp.tool_calls

    def generate_answer(
        self,
        user_message: str,
        context: str,
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Menghasilkan jawaban final ke pengguna dengan menyuntikkan konteks yang
        sudah diambil dari RAG dan/atau KAG, serta riwayat percakapan untuk multi-turn coherence.
        """
        system_instruction = (
            "You are a professional, helpful, and empathetic AI Customer Support Assistant for SupportSense AI.\n"
            "Your sole domain of responsibility is customer support: orders, shipping, courier tracking, warranties, returns, refunds, damaged packages, and store policies.\n"
            "STRICT DOMAIN BOUNDARY & OUT-OF-SCOPE RULES:\n"
            "1. If the customer asks questions unrelated to customer support (such as general trivia, historical figures, politics, presidents, geography, math, coding, or chit-chat), "
            "politely decline to answer, state that you are an AI assistant specialized only in customer support, and invite them to ask about their orders or company policies.\n"
            "2. NEVER answer out-of-scope trivia, historical facts, or political questions, even if you know the answer from your general pretraining knowledge.\n"
            "3. Always maintain this boundary consistently across all inquiries.\n\n"
            "Answer the customer's question clearly and concisely based strictly on the provided RETRIEVED CONTEXT below.\n"
            "CRITICAL FACTUAL GROUNDING & ANTI-HALLUCINATION RULES:\n"
            "1. ONLY state facts present in the context. Never invent names, agents, emails, phone numbers, tracking numbers, or refund amounts.\n"
            "2. If the customer assumes or claims false information (e.g. claims a wrong product, wrong agent, wrong courier, wrong refund amount), "
            "politely correct them using the exact facts from the context.\n"
            "3. If the context states 'No active complaints or delivery issues recorded' and the customer claims an item is broken or delayed, "
            "clarify that the order is on record as delivered without active complaints, and offer to open a new ticket.\n"
            "4. Maintain conversational continuity across multi-turn exchanges without contradicting the context.\n"
            "5. If the context does not contain enough information, politely explain that and suggest escalating to our team.\n\n"
            f"=== RETRIEVED CONTEXT ===\n{context}\n========================="
        )

        messages = [{"role": "system", "content": system_instruction}]

        if chat_history:
            for h in chat_history[-6:]:
                r = h.get("role", "user")
                c = h.get("message", "")
                if r in ("user", "assistant") and c:
                    messages.append({"role": r, "content": c})

        messages.append({"role": "user", "content": user_message})
        resp = self.client.chat(messages=messages, temperature=0.2)
        return resp.content