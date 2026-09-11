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
                        "description": "Nomor pesanan lengkap dengan tanda pagar jika ada (misal: '#4521' atau '4521')"
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
Analyze the user's inquiry and decide which tools to call:
1. Call 'search_knowledge_base' for general policies, warranties, returns, refunds, FAQs, or damaged package rules.
2. Call 'lookup_relational_data' if the user mentions a specific order number (#1234, etc.) or asks about shipping status, delivery issues, or assigned support agent.
3. If the question involves BOTH a general policy AND a specific order (e.g. 'My order #4521 arrived broken, what is your refund policy?'), call BOTH tools (Hybrid route).
4. Call 'escalate_to_human' if the inquiry asks for dangerous/impossible tasks (bypassing security, manual database overrides, abusive requests) or is completely unanswerable.
5. If it's a simple greeting like 'hi' or 'hello', you may answer directly without calling any tools."""


class HermesAgentClient:
    """
    Klien pemanggil Ollama Chat API yang menangani pemanggilan tool (function calling)
    dan pembentukan jawaban akhir (response synthesis), dilindungi oleh ResilientOllamaClient.
    """
    def __init__(self, resilient_client: Optional[ResilientOllamaClient] = None):
        self.client = resilient_client or ResilientOllamaClient()

    def plan_routing(self, user_message: str) -> List[Dict[str, Any]]:
        """
        Mengirim pesan user ke Ollama dengan daftar SUPPORT_TOOLS.
        Mengembalikan daftar tool calls yang diputuskan oleh LLM.
        """
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        resp = self.client.chat(messages=messages, tools=SUPPORT_TOOLS, temperature=0.0)
        return resp.tool_calls

    def generate_answer(self, user_message: str, context: str) -> str:
        """
        Menghasilkan jawaban final ke pengguna dengan menyuntikkan konteks yang
        sudah diambil dari RAG dan/atau KAG.
        """
        system_instruction = (
            "You are a professional, helpful, and empathetic AI Customer Support Assistant.\n"
            "Answer the customer's question clearly and concisely based ONLY on the provided context below.\n"
            "If the context states an order is delayed, explain the reason and mention the assigned agent if present.\n"
            "If the context does not contain enough information, politely explain that and suggest escalating to our team.\n\n"
            f"=== RETRIEVED CONTEXT ===\n{context}\n========================="
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ]
        resp = self.client.chat(messages=messages, temperature=0.2)
        return resp.content