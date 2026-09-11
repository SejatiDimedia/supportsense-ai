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
    page_title="SupportSense AI — Hybrid RAG + KAG Customer Support",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Impeccable Styling (Operate Mode, Accessible Contrast, Crisp Density) ---
st.markdown(
    """
    <style>
    /* Global Typography & Spacing */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header styling */
    .brand-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    .brand-subtitle {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1.25rem;
        line-height: 1.4;
    }
    
    /* Route Badges (High Contrast, Accessible, WCAG AA Compliant) */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .badge-rag {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .badge-kag {
        background-color: #F5F3FF;
        color: #5B21B6;
        border: 1px solid #DDD6FE;
    }
    .badge-hybrid {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    .badge-direct {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }
    .badge-escalated {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .badge-metric {
        background-color: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    
    /* Inspection card */
    .inspect-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.8rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    
    /* Sidebar card container */
    .status-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.75rem;
    }
    .status-header {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .status-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
    }
    .status-online {
        color: #059669;
        font-weight: 600;
    }
    .status-offline {
        color: #DC2626;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- State Management ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Router singleton
@st.cache_resource
def get_router() -> AgentRouter:
    return AgentRouter()

@st.cache_resource
def get_system_topology() -> Dict[str, Any]:
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

# --- Helper: Send Query ---
def submit_query(prompt_text: str):
    if not prompt_text.strip():
        return

    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt_text})

    # Try dispatching to local FastAPI server if active, fallback to direct AgentRouter
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
        # Fallback to direct local AgentRouter instance
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
    st.markdown("### ⚡ SupportSense Cockpit")
    st.caption("AI Customer Support Assistant | Multi-Path Orchestrator")

    # Session Manager
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-header">Current Session</div>
            <div class="status-value" style="font-family: monospace;">{st.session_state.session_id}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_btn2:
        if st.button("➕ New Session", use_container_width=True):
            st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🛠️ System Components")

    # Component 1: Ollama Model
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-header">LLM Engine (Ollama)</div>
            <div class="status-value">{settings.llm_model}</div>
            <small style="color: #64748B;">Embedding: {settings.embedding_model}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Component 2: RAG Vector Store
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-header">Unstructured RAG (Chroma)</div>
            <div class="status-value">{topology['chroma_count']} Document Chunks</div>
            <small style="color: #64748B;">Collection: support_docs</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Component 3: KAG Knowledge Graph
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-header">Relational KAG (NetworkX)</div>
            <div class="status-value">{topology['graph_nodes']} Nodes & {topology['graph_edges']} Edges</div>
            <small style="color: #64748B;">Entities: Customer, Order, Product, Issue, Agent</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Component 4: Escalation Pipeline & Pending Webhooks
    pending_escalations = repo.get_pending_escalations(limit=50)
    pending_count = len(pending_escalations)

    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-header">Escalation Webhook Queue</div>
            <div class="status-value">{pending_count} Pending Items</div>
            <small style="color: #64748B;">Target: {settings.n8n_webhook_url}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pending_count > 0:
        if st.button("🚀 Flush Pending Retries", use_container_width=True):
            recovered = webhook_client.process_pending_retries()
            st.success(f"Retried queue: {recovered} successfully sent.")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📊 Session Telemetry")
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
        st.caption("No queries executed in this session yet.")


# --- Main Application Area ---
st.markdown('<div class="brand-title">SupportSense AI Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-subtitle">'
    'Enterprise customer support assistant demonstrating hybrid <strong>RAG + KAG</strong> architecture, '
    'agentic router decision trees, sub-millisecond greeting filters, and zero-loss escalation fallback.'
    '</div>',
    unsafe_allow_html=True,
)

# --- PRD Benchmark Quick Scenarios ---
st.markdown("##### ⚡ Quick Test Scenarios (PRD Section 17):")
cols = st.columns(5)

scenarios = [
    ("📄 Refund Policy", "What is your refund policy?", "RAG documentation retrieval"),
    ("📦 Order #4521", "Where is my order #4521?", "KAG relational graph traversal"),
    ("⚡ Damaged + #4521", "My order #4521 arrived damaged, what is your policy and who can help me?", "Hybrid RAG + KAG synthesis"),
    ("🔒 Security Bypass", "Can you hack into my account to reset my password manually?", "Security escalation trigger"),
    ("❓ Order #9999999", "Where is my order #9999999?", "Missing order escalation"),
]

for i, (label, prompt_val, help_text) in enumerate(scenarios):
    with cols[i]:
        if st.button(label, help=help_text, use_container_width=True, key=f"quick_btn_{i}"):
            submit_query(prompt_val)
            st.rerun()

st.markdown("---")

# --- Chat Stream Rendering ---
if not st.session_state.messages:
    st.info(
        "👋 Welcome! Click one of the quick test scenarios above or type any inquiry below to test the agent router.",
        icon="ℹ️",
    )

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    with st.chat_message(role):
        st.markdown(content)

        # Assistant Telemetry Bar & Context Inspector
        if role == "assistant" and "route_taken" in msg:
            route = msg.get("route_taken", "direct").lower()
            confidence = msg.get("confidence_score", 0.0)
            latency = msg.get("latency_ms", 0.0)
            trace_id = msg.get("trace_id", "none")
            escalated = msg.get("escalated", False)
            context = msg.get("context_used", "")

            # Badge Styling
            badge_class = f"badge-{route}" if route in ["rag", "kag", "hybrid", "direct", "escalated"] else "badge-metric"
            esc_status = "⚠️ ESCALATED" if escalated else "NORMAL"

            st.markdown(
                f"""
                <div style="margin-top: 0.6rem; margin-bottom: 0.4rem;">
                    <span class="badge {badge_class}">{route}</span>
                    <span class="badge badge-metric">Conf: {confidence * 100:.0f}%</span>
                    <span class="badge badge-metric">{latency:.1f} ms</span>
                    <span class="badge badge-metric">Trace: {trace_id}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Grounding & Context Drawer
            if context and context.strip():
                with st.expander(f"🔍 Grounding & Context Inspector (Trace {trace_id})", expanded=False):
                    st.markdown(
                        f"""
                        <div class="inspect-box">
                            <pre style="white-space: pre-wrap; font-size: 0.8rem; margin: 0; color: #334155;">{context}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# --- User Input Box ---
user_input = st.chat_input("Type your question or request (e.g. 'What is the warranty policy?' or 'Where is order #4521?')...")
if user_input:
    submit_query(user_input)
    st.rerun()
