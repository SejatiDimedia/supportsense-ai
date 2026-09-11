import os
import sys
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import httpx
import streamlit as st

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.agent.router import AgentRouter
from app.rag.embedder import VectorStoreManager
from app.kag.graph_builder import SupportKnowledgeGraph
from app.persistence.repository import repo
from app.escalation.webhook_client import webhook_client

logger = logging.getLogger(__name__)

# --- Page Configuration ---
st.set_page_config(
    page_title="SupportSense AI — Hybrid RAG + KAG Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Impeccable Dark Theme Styling (Zero Emoji, Clean Typography, WCAG AA Compliant) ---
st.markdown(
    """
    <style>
    /* Base Typography & Font Stack */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top Header Styling */
    .brand-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.25rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .brand-title-wrap {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .brand-title {
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin: 0;
    }
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .brand-pill-dot {
        width: 6px;
        height: 6px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 6px #10B981;
    }
    .brand-subtitle {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-top: 0.4rem;
        margin-bottom: 1.2rem;
        line-height: 1.45;
    }
    
    /* Modern Translucent Badges (High Contrast, Sleek Dark Palette) */
    .badge-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.6rem;
        margin-bottom: 0.5rem;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.22rem 0.65rem;
        border-radius: 6px;
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-rag {
        background: rgba(16, 185, 129, 0.16);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.35);
    }
    .badge-kag {
        background: rgba(139, 92, 246, 0.16);
        color: #A78BFA;
        border: 1px solid rgba(167, 139, 250, 0.35);
    }
    .badge-hybrid {
        background: rgba(245, 158, 11, 0.16);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.35);
    }
    .badge-direct {
        background: rgba(59, 130, 246, 0.16);
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.35);
    }
    .badge-escalated {
        background: rgba(239, 68, 68, 0.18);
        color: #F87171;
        border: 1px solid rgba(248, 113, 113, 0.4);
    }
    .badge-metric {
        background: rgba(255, 255, 255, 0.05);
        color: #CBD5E1;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    
    /* Sidebar Cards */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 0.65rem;
    }
    .sidebar-card-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .sidebar-card-value {
        font-size: 0.92rem;
        font-weight: 600;
        color: #F8FAFC;
    }
    .sidebar-card-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.15rem;
    }
    
    /* Quick Action Prompt Chips */
    .scenario-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.45rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Router & Knowledge Graph Singletons
@st.cache_resource
def get_router(cache_buster: str = "v2_postgres_integrated") -> AgentRouter:
    return AgentRouter()

@st.cache_resource
def get_system_topology(cache_buster: str = "v2_postgres_integrated") -> Dict[str, Any]:
    try:
        vsm = VectorStoreManager()
        chroma_count = vsm.get_or_create_collection().count()
    except Exception:
        chroma_count = 0

    try:
        kg = SupportKnowledgeGraph()
        graph_nodes = kg.graph.number_of_nodes()
        graph_edges = kg.graph.number_of_edges()
    except Exception:
        graph_nodes, graph_edges = 0, 0

    return {
        "chroma_count": chroma_count,
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
    }

router_instance = get_router()
topology = get_system_topology()

# --- Query Dispatcher ---
def submit_query(prompt_text: str):
    if not prompt_text.strip():
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    # Try local FastAPI endpoint, fallback to direct AgentRouter
    api_url = f"http://localhost:{settings.app_port}/chat"
    chat_result = None

    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(
                api_url,
                json={"message": prompt_text, "session_id": st.session_state.session_id},
            )
            if resp.status_code == 200:
                chat_result = resp.json()
    except Exception:
        pass

    if not chat_result:
        res = router_instance.process_message(
            user_message=prompt_text,
            session_id=st.session_state.session_id,
        )
        chat_result = res.to_dict()

    st.session_state.messages.append({
        "role": "assistant",
        "content": chat_result["answer"],
        "trace_id": chat_result["trace_id"],
        "route_taken": chat_result["route_taken"],
        "confidence_score": chat_result["confidence_score"],
        "escalated": chat_result["escalated"],
        "latency_ms": chat_result["latency_ms"],
        "context_used": chat_result["context_used"],
    })

# --- Sidebar: System Control & Observability Cockpit ---
with st.sidebar:
    st.markdown("### SupportSense Cockpit")
    st.caption("AI Customer Support Assistant | Modular Monolith")

    # Session Manager Card
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">Active Session ID</div>
            <div class="sidebar-card-value" style="font-family: monospace;">{st.session_state.session_id}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_btn2:
        if st.button("New Session", use_container_width=True):
            st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"
            st.session_state.messages = []
            st.rerun()

    if st.button("Reload System & Cache", use_container_width=True, help="Purge cached singletons and reconnect to database"):
        st.cache_resource.clear()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("#### System Components")

    # 1. LLM Model Card
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">LLM Engine (Ollama)</div>
            <div class="sidebar-card-value">{settings.llm_model}</div>
            <div class="sidebar-card-sub">Embeddings: {settings.embedding_model}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Chroma Vector DB Card
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">Unstructured RAG (Chroma)</div>
            <div class="sidebar-card-value">{topology['chroma_count']} Document Chunks</div>
            <div class="sidebar-card-sub">Collection: support_docs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. KAG Knowledge Graph Card
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">Relational KAG (NetworkX)</div>
            <div class="sidebar-card-value">{topology['graph_nodes']} Nodes & {topology['graph_edges']} Edges</div>
            <div class="sidebar-card-sub">Entities: Customer, Order, Product, Issue, Agent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Escalation Queue Card
    pending_escalations = repo.get_pending_escalations(limit=50)
    pending_count = len(pending_escalations)

    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">Escalation Webhook Queue</div>
            <div class="sidebar-card-value">{pending_count} Pending Records</div>
            <div class="sidebar-card-sub">Zero-Loss Local SQLite Retention</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pending_count > 0:
        if st.button("Flush Pending Retries", use_container_width=True):
            recovered = webhook_client.process_pending_retries()
            st.success(f"Dispatched {recovered} items.")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown("#### Session Telemetry")
    assistant_msgs = [m for m in st.session_state.messages if m.get("role") == "assistant"]
    total_queries = len(assistant_msgs)

    if total_queries > 0:
        avg_latency = sum(m.get("latency_ms", 0) for m in assistant_msgs) / total_queries
        routes = [m.get("route_taken", "unknown") for m in assistant_msgs]
        route_dist = {r: routes.count(r) for r in set(routes)}

        st.write(f"**Total Queries:** `{total_queries}`")
        st.write(f"**Avg Latency:** `{avg_latency:.1f} ms`")
        st.write("**Route Breakdown:**")
        for r, cnt in route_dist.items():
            st.caption(f"- `{r.upper()}`: {cnt} queries")
    else:
        st.caption("No queries executed yet.")

# --- Main App Header ---
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title-wrap">
            <span class="brand-title">SupportSense AI</span>
        </div>
        <div class="brand-pill">
            <span class="brand-pill-dot"></span>
            Operational
        </div>
    </div>
    <div class="brand-subtitle">
        Enterprise Customer Support Assistant powered by <strong>Hybrid RAG + KAG</strong> agentic orchestration, 
        sub-millisecond fast-path greetings, and zero-loss human escalation.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- PRD Acceptance Benchmark Scenarios ---
st.markdown('<div class="scenario-title">Quick Test Scenarios (PRD Section 17):</div>', unsafe_allow_html=True)
cols = st.columns(5)

scenarios = [
    ("Refund Policy", "What is your refund policy?", "RAG: Document search & cross-encoder rerank"),
    ("Order #4521", "Where is my order #4521?", "KAG: Relational graph traversal"),
    ("Damaged + #4521", "My order #4521 arrived damaged, what is your policy and who can help me?", "Hybrid: RAG policy + KAG agent traversal"),
    ("Security Check", "Can you hack into my account to reset my password manually?", "Escalation: Guardrail bypass detection"),
    ("Order #9999999", "Where is my order #9999999?", "Escalation: Unknown entity fallback"),
]

for i, (label, prompt_val, help_text) in enumerate(scenarios):
    with cols[i]:
        if st.button(label, help=help_text, use_container_width=True, key=f"btn_scenario_{i}"):
            submit_query(prompt_val)
            st.rerun()

st.markdown("---")

# --- Chat Messages Stream ---
if not st.session_state.messages:
    st.info("Welcome to SupportSense AI. Select any quick test scenario above or enter an inquiry below to evaluate the agent router.")

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    with st.chat_message(role):
        st.markdown(content)

        # Assistant Telemetry & Grounding Inspector
        if role == "assistant" and "route_taken" in msg:
            route = msg.get("route_taken", "direct").lower()
            confidence = msg.get("confidence_score", 0.0)
            latency = msg.get("latency_ms", 0.0)
            trace_id = msg.get("trace_id", "none")
            escalated = msg.get("escalated", False)
            context = msg.get("context_used", "")

            badge_class = f"badge-{route}" if route in ["rag", "kag", "hybrid", "direct", "escalated"] else "badge-metric"

            # Render Badges
            st.markdown(
                f"""
                <div class="badge-bar">
                    <span class="badge {badge_class}">{route}</span>
                    <span class="badge badge-metric">Conf: {confidence * 100:.0f}%</span>
                    <span class="badge badge-metric">{latency:.1f} ms</span>
                    <span class="badge badge-metric">Trace: {trace_id}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Grounding & Context Inspector (Clean Dark-Theme Rendering with Syntax Highlighting)
            if context and context.strip() and context != "Direct greeting handler.":
                with st.expander(f"Grounding & Context Inspector (Trace: {trace_id})", expanded=False):
                    # Check if hybrid or combined
                    has_kag = "=== RELATIONAL DATA (KAG) ===" in context
                    has_rag = "=== POLICY & DOCUMENTATION (RAG) ===" in context

                    if has_kag and has_rag:
                        tab1, tab2 = st.tabs(["Relational Graph (KAG)", "Retrieved Documentation (RAG)"])
                        with tab1:
                            kag_content = context.split("=== POLICY & DOCUMENTATION (RAG) ===")[0].replace("=== RELATIONAL DATA (KAG) ===", "").strip()
                            st.code(kag_content, language="markdown")
                        with tab2:
                            rag_content = context.split("=== POLICY & DOCUMENTATION (RAG) ===")[1].strip()
                            st.code(rag_content, language="markdown")
                    elif has_kag:
                        kag_content = context.replace("=== RELATIONAL DATA (KAG) ===", "").strip()
                        st.markdown("**Relational Graph Traversal Result:**")
                        st.code(kag_content, language="markdown")
                    elif has_rag:
                        rag_content = context.replace("=== POLICY & DOCUMENTATION (RAG) ===", "").strip()
                        st.markdown("**Retrieved Documentation Chunks:**")
                        st.code(rag_content, language="markdown")
                    else:
                        st.code(context, language="markdown")

# --- User Input Box ---
user_input = st.chat_input("Ask about order status, warranty, returns, or company policies...")
if user_input:
    submit_query(user_input)
    st.rerun()
