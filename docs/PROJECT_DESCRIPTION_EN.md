# SupportSense AI — Enterprise-Grade Autonomous Customer Support Engine (Hybrid RAG + Relational KAG)

SupportSense AI is an enterprise-grade autonomous customer support platform engineered to modernize customer experience, e-commerce operations, and warehouse logistics. The platform fuses two distinct machine-reasoning paradigms into a cohesive architecture: **Knowledge-Augmented Generation (KAG)** powered by structured relational SQL databases (PostgreSQL 16) for transactional integrity, and **Retrieval-Augmented Generation (RAG)** driven by high-density vector embeddings (ChromaDB) paired with a neural Cross-Encoder Reranker for unstructured regulatory documents and company policies.

Operating as an integrated support command center, human support specialists can monitor customer inquiries in real time, inspect the autonomous semantic routing decisions taken by the routing engine, audit the deterministic data trail (*Grounding Audit Drawer*) behind every AI-synthesized answer, and verify cluster infrastructure health (48 PostgreSQL graph nodes, 47 data edges, and 14 regulatory vector chunks) via a live diagnostic telemetry modal. For end customers, the platform delivers a natural conversational experience characterized by sub-second latency, persistent multi-turn order context retention, progressive word-by-word streaming responses, and responsive accessibility across desktop and mobile devices.

The project centers on the complete elimination of AI hallucination (*zero hallucination*) through strict decoupling of transactional SQL data from regulatory policy texts, substantial inference cost optimization via high-speed lexical pre-filtering (*Direct Route <5ms*), banking-grade system fault tolerance (*Circuit Breaker Pattern* with Closed, Open, and Half-Open states), rigorous prompt injection and domain boundary containment, and seamless automated handovers to human agents (*Human-in-the-Loop*) via n8n automation webhooks.

---

## Project Summary

- **Category:** Enterprise AI, Autonomous Agent Systems, Hybrid RAG + KAG, Customer Support Automation, E-Commerce Logistics.
- **Role:** Principal AI Systems & Full-Stack Engineer (Solo Developer).
- **Core Focus:** 5-way semantic routing orchestration (*AgentRouter*), hallucination elimination via relational SQL vs vector text decoupling, persistent multi-turn conversational reasoning, inference circuit breaker resilience, transparent grounding audit drawer, client-side session persistence (*localStorage*), mobile slide-out drawer, and automated human escalation workflows via n8n.
- **Backend & Architecture:** Python 3.13, FastAPI, Modular Monolith Architecture (Strict separation of Agent, RAG, KAG, Persistence, Escalation, Observability, and API Gateway layers), Structured JSON Logging with Distributed UUID Trace IDs (`trace_id`).
- **Database & Relational Integrity:** PostgreSQL 16 Alpine (Docker Container), SQLite parity for local audit persistence, 3NF ACID-compliant relational schema (`customers`, `products`, `orders`, `order_items`, `shipments`, `issues`, `agents`, `conversation_history`), Knowledge Graph with 48 Nodes and 47 Structural Edges.
- **Retrieval & Vector Engine (RAG):** ChromaDB Vector Store, 384-dimensional dense vector embeddings (`nomic-embed-text` / `all-minilm`), hierarchical character chunking with adaptive overlap, Sentence-Transformers Cross-Encoder Neural Reranker (`ms-marco-MiniLM-L-6-v2`) for precision semantic relevance scoring.
- **AI Inference & Automation:** Ollama Self-Hosted Daemon (LLM Models: `hermes-2-pro:latest` / `llama3.2:latest`), Custom Resilience Circuit Breaker (3 consecutive failure threshold, 30-second cooldown timeout, *Half-Open* recovery probing, graceful structured fallback response), n8n Workflow Automation Engine (Port 5678).
- **Frontend & Web Console:** React 18, Vite 6, TypeScript (100% Strict Mode), Tailwind CSS, Lucide Icons, Global React Error Boundary for zero-crash UI resilience, `StreamingText` progressive typing engine with visual blinking cursor, isolated mobile slide-out drawer (`< 768px`), Dual-Tone Enterprise Design System (Obsidian Charcoal `#0E1116`, Floating White Canvas `#FFFFFF`, and Vibrant Lime Accent `#D4F638`).
- **Testing & Software Reliability:** Integrated Pytest Suite (58 Automated Unit, Integration, and End-to-End Tests with 100% PASS rate), Impeccable Design Quality & Accessibility Auditor (0 Warnings, 0 Errors, WCAG AA contrast compliance).

---

## Background & Motivation

In the modern enterprise landscape, businesses increasingly seek to deploy Generative AI to mitigate customer service operational overhead. However, the overwhelming majority of solutions deployed today are fragile wrappers around generic commercial APIs (*simple ChatGPT wrappers*) that introduce severe operational and financial liabilities.

Historically, traditional AI customer support chatbots and generic LLM implementations have suffered from critical real-world flaws:

1. **Severe Hallucinations on Transactional and Financial Data:** Generic LLMs routinely fabricate shipping statuses, tracking numbers, and refund amounts when queried about specific customer orders. Providing fabricated logistics information erodes customer trust and exposes businesses to legal disputes.
2. **Exorbitant API Token Cost Inefficiencies:** In conventional architectures, every incoming message—including simple greetings (*"Hello good morning"*), pleasantries, or irrelevant questions—is forwarded to an expensive commercial LLM. Consequently, 60% to 70% of API budgets are wasted on conversational trivialities.
3. **Black-Box Opacity and Lack of Accountability:** Support team leads and compliance officers have no visibility into how a response was synthesized. When an AI mistakenly promises an unauthorized discount or approves an unverified damage claim, there is no verifiable data audit trail to diagnose the error.
4. **Fragile Single Point of Failure:** If local inference servers or third-party cloud AI APIs encounter latency spikes, GPU queue saturations, or network timeouts, customer-facing applications typically freeze, throw unhandled exceptions, or collapse into a blank screen.
5. **Lack of Domain Boundaries (Prompt Injections & Topic Drift):** Unconstrained chatbots are easily manipulated by users into answering off-topic inquiries—spanning political debates, world history, and cooking recipes—turning expensive proprietary business assets into public entertainment forums.
6. **Multi-Turn Context Drift:** Most systems fail to maintain entity persistence across subsequent conversational turns when customers ask follow-up questions without re-stating their order numbers (e.g., *"What carrier was assigned to that?"* immediately following a tracking inquiry).

I designed and engineered the SupportSense AI platform to systematically eliminate these structural vulnerabilities through rigorous software engineering principles:

1. **Dual-Engine Anti-Hallucination Architecture (KAG + RAG):** Explicitly routing transactional inquiries to a normalized PostgreSQL relational database via structured SQL queries (KAG), while restricting ChromaDB vector retrieval to official policy documents (RAG). The LLM is strictly bound to verifiable context.
2. **Sub-5ms Semantic Pre-Filtering (Direct Path):** Routine greetings and out-of-domain inquiries are resolved instantaneously at the router level without querying databases or invoking LLMs, reducing overall compute expenditure by up to 70%.
3. **Auditable Grounding Drawer:** Every synthesized answer includes an interactive inspection trigger that slides open a visual drawer revealing the exact SQL JOIN rows or official document clauses referenced.
4. **Banking-Grade System Resilience (Circuit Breaker & Error Boundary):** The backend is protected by a 3-stage circuit breaker pattern that yields graceful fallback responses during model outages; the frontend is enclosed within a React Error Boundary to prevent unhandled JavaScript render crashes.
5. **Defensive Security Guardrails:** Automated real-time lexical classification detects prompt injections, unauthorized account override requests, and out-of-scope inquiries, rejecting them with polite precision within milliseconds.
6. **Deterministic Multi-Turn Context Memory:** The persistence repository automatically resolves and retains active order numbers across extensive conversational lookbacks, enabling seamless natural dialogue.

---

## Key Engineering Contributions

**5-Way Semantic Routing Engine (`AgentRouter`)**
- Architected an independent decision orchestration engine in [`app/agent/router.py`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/app/agent/router.py) that evaluates user intent and dispatches queries across 5 distinct operational pathways:
  - **Direct Route (<5ms):** High-speed lexical pattern matching that intercepts greetings, acknowledgments, and off-topic inquiries, returning structured responses with near-zero latency.
  - **KAG Relational Route:** Deterministically extracts order numbers (#XXXX) and executes multi-table relational traversals in PostgreSQL.
  - **RAG Vector Route:** Performs semantic vector search over warranty, return, and refund documentation in ChromaDB.
  - **Hybrid Route:** Jointly resolves physical order records and legal warranty clauses to evaluate complex RMA claims.
  - **Escalation Route:** Automates handovers to human teams when customer sentiment is volatile or confidence scores fall below threshold.

**Dual-Engine Architecture: Relational KAG & Dense Vector RAG**
- United two disparate data paradigms into a cohesive, hallucination-free retrieval pipeline:
  - **Relational KAG Engine:** Constructed an enterprise knowledge graph comprising 48 nodes and 47 relational edges from a normalized PostgreSQL 3NF schema. Generates parameterized multi-table SQL queries (`orders` JOIN `customers` JOIN `order_items` JOIN `shipments` JOIN `issues`) completely immune to SQL injection vulnerabilities.
  - **Vector RAG Engine:** Built an end-to-end document indexing pipeline featuring recursive hierarchical character chunking, 384-dimensional dense vector embeddings, and a Sentence-Transformers Cross-Encoder Neural Reranker to filter retrieved candidates down to the top 2 most relevant policy excerpts.

**Enterprise Circuit Breaker Pattern for Local Inference Resilience**
- Implemented a production-grade *Circuit Breaker Pattern* within the LLM client in [`app/llm/client.py`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/app/llm/client.py) to protect backend services against local Ollama service interruptions:
  - **CLOSED State:** Normal operational mode; all outbound inference requests proceed unhindered.
  - **OPEN State:** Upon recording 3 consecutive connection failures or timeouts, the circuit trips open for a 30-second cooldown duration, short-circuiting calls and instantly delivering pre-validated fallback messages to users.
  - **HALF-OPEN State:** Following cooldown expiration, a single probe request is permitted through to verify daemon recovery before restoring full traffic flow.

**High-Performance Multi-Turn Session History & Context Persistence**
- Developed a transactional conversation repository in [`app/persistence/repository.py`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/app/persistence/repository.py) that logs dialogue turns and distributed trace identifiers.
- Implemented an automated reverse-lookback resolution algorithm scanning up to 100 historical turns to automatically detect the active order number under discussion when users ask subsequent elliptical questions.

**Production-Grade React Console with LocalStorage Sync & Mobile Drawer**
- Engineered an enterprise-grade React 18 single-page application with a polished dual-tone visual hierarchy:
  - Wrapped the application root in a class-based *Global React Error Boundary* ([`ErrorBoundary.tsx`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/frontend/src/components/ErrorBoundary.tsx)) that traps unhandled rendering exceptions and provides an interactive recovery action.
  - Implemented bidirectional state synchronization with browser `localStorage` (`supportsense_sessions` and `supportsense_history_${sessionId}`), ensuring zero loss of chat histories across browser refreshes (`F5`) and tab switches.
  - Designed an off-canvas slide-out navigation drawer for mobile and tablet screens (`< 768px`) complete with a darkened backdrop overlay and header hamburger toggle.
  - Implemented a `StreamingText` sub-component in [`ChatStream.tsx`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/frontend/src/components/ChatStream.tsx) delivering a tactile, word-by-word progressive typing animation with a blinking visual cursor.

**Context Grounding Audit Drawer**
- Developed a collapsible right-side grounding drawer in [`GroundingDrawer.tsx`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/frontend/src/components/GroundingDrawer.tsx) accessible via a single click on any assistant response.
- Exposes transparent diagnostic metadata: distributed trace ID, selected routing pipeline, millisecond latency metrics, confidence ratings, raw relational SQL rows, and source vector policy text.

**Automated Human-in-the-Loop Escalation via n8n Webhook**
- Built an asynchronous webhook dispatcher in [`app/escalation/webhook_client.py`](file:///Users/timurdianradhasejati/Programming/Code/AI/supportsense/app/escalation/webhook_client.py) that forwards incident payloads to an n8n workflow on port `5678` whenever severe complaints, negative sentiment, or low confidence scores (< 0.65) are detected.

---

## Core Product Features

**1. Operator Command Center (Dual-Tone Workspace Console)**
- Unified interface pairing an Obsidian Charcoal (`#0E1116`) navigation sidebar with a high-radius floating white canvas (`rounded-[24px]`).
- Model selector dropdown (`SupportSense 1.0`), one-click session sharing, and verified operator profile credentials.
- Instant search filtering across previous conversation sessions with quick reset hotkeys (`⌘ N`).

**2. Autonomous Multi-Turn Order & Logistics Tracking**
- Real-time verification of e-commerce order identifiers (e.g., `#4521`, `#4523`, `#4534`).
- Comprehensive logistics breakdown displaying carrier names (FedEx, DHL, JNE, SiCepat), tracking numbers, current parcel states, purchased items, and carrier investigation logs for lost or damaged goods.
- Seamless conversational continuity across follow-up questions without re-entering tracking identifiers.

**3. Corporate Policy & Warranty Verification**
- Accurate interpretation of 30-day return windows, opened-box seal criteria, full refund eligibility, and 24-month manufacturer hardware warranty terms.
- Driven by dense ChromaDB vector search coupled with Cross-Encoder reranking for supreme legal accuracy.

**4. Context Grounding Audit Drawer**
- Interactive side-drawer granting operators instant auditability over raw machine context.
- Displays raw multi-table SQL query results, vector source excerpts, confidence percentage badges (e.g., `95%`), and unique trace identifiers (`trace_id`).

**5. Real-Time Cluster Telemetry Modal**
- Comprehensive diagnostic pop-up providing live infrastructure observability:
  - Active PostgreSQL knowledge graph nodes (48 Nodes, 47 Edges).
  - Total ChromaDB policy vector collections (14 Chunks).
  - Active neural inference models (`Hermes 2 Pro` and `nomic-embed-text`).
  - Health connectivity statuses for PostgreSQL (Port 5433) and Ollama (Port 11434).

**6. Domain Boundary & Security Guardrails**
- Sub-5ms polite rejections of out-of-domain inquiries (politics, world history, recipes, weather) unrelated to customer support.
- Instant mitigation and audit logging of prompt injection attempts, database override commands, and manual credential bypass requests.

**7. Automated Human Agent Handover Workflow**
- Autonomous detection of customer churn risk and escalating dissatisfaction.
- Instantaneous webhook dispatch to n8n automation pipelines for automated priority ticket creation in external CRM systems.

---

## Tech Stack & System Architecture

SupportSense AI leverages a robust, modern software stack optimized for data integrity, minimal latency, and enterprise production readiness:

- **Backend Core Framework:** Python 3.13, FastAPI (Uvicorn ASGI Server, REST Endpoints `/chat`, `/health`, `/telemetry`, `/metrics`)
- **Software Architecture:** Modular Monolith Architecture with strict domain separation
- **Frontend & UI Console:** React 18, Vite 6, TypeScript (Strict Mode), Tailwind CSS, Lucide Icons
- **Relational Database (KAG):** PostgreSQL 16 Alpine (Docker Container on Port 5433), SQLite Parity for local audit storage
- **Vector Database (RAG):** ChromaDB Vector Store (14 policy chunks in `./data/chroma`)
- **Embedding Engine:** Nomic Embed Text / All-MiniLM (384-dimensional dense vectors)
- **Reranker Model:** Sentence-Transformers Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
- **Neural Inference (LLM):** Ollama Local Daemon (Port 11434, Hermes 2 Pro / Llama 3.2)
- **Workflow Automation:** n8n Containerized Engine (Port 5678)
- **Observability & Tracing:** Structured JSON Logging with Distributed UUID Trace IDs, Prometheus-style Latency Metrics
- **Testing & Quality Assurance:** Pytest Suite (58 passing tests), Impeccable Design Quality & Accessibility Auditor

---

## Real-World Engineering Challenges & Applied Solutions

**1. Eliminating AI Hallucinations on Specific Transactional Orders**
- *Challenge:* When customers inquire about order statuses such as *"Where is my order #4534?"*, standard commercial LLMs routinely hallucinate fictional dispatch dates, fake carriers, and nonexistent tracking numbers.
- *Solution:* I established a strict data boundary using the KAG architecture. Order numbers are extracted deterministically, triggering a parameterized SQL query to PostgreSQL 16 to retrieve ground-truth records (`Lost in Transit`, FedEx carrier, assigned specialist notes). This verified dataset is passed to the LLM prompt accompanied by an inviolable grounding constraint: the model is strictly forbidden from stating any fact outside the provided SQL payload.

**2. Mitigating API Token Cost Overhead and Inference Latency Bottlenecks**
- *Challenge:* Invoking an 8-billion parameter neural network to process routine pleasantries like *"Good morning"* or random questions like *"Who was the first president?"* consumes 2 to 4 seconds of GPU compute and squanders API expenditure.
- *Solution:* I engineered a pre-filtering gate within `AgentRouter`. High-performance lexical analyzers evaluate incoming messages; if a greeting or out-of-domain topic is detected, the router returns a structured template response in under 5 milliseconds (`Direct Route <5ms>`), bypassing LLM inference and database lookups entirely. This optimization slashes compute overhead by over 70%.

**3. Preventing Cascade Failures During Local LLM Daemon Interruptions**
- *Challenge:* In self-hosted inference setups, local LLM daemons (such as Ollama) can experience GPU out-of-memory spikes or heavy queue backpressure. If the backend blindly dispatches requests, connection timeouts cascade, freezing the user interface.
- *Solution:* I implemented the *Circuit Breaker Pattern* on the LLM client. The circuit continuously monitors outbound network health. Upon registering 3 consecutive failures, it trips to the *OPEN* state for 30 seconds, immediately short-circuiting calls and serving structured graceful fallback messages. After 30 seconds, it enters *HALF-OPEN* mode, probing server stability with a single request before restoring regular traffic.

**4. Preserving Client-Side Chat State Without Database Query Overhead**
- *Challenge:* In single-page React applications, browser refreshes (`F5`) wipe volatile in-memory component states, resulting in lost conversation transcripts and a frustrating user experience.
- *Solution:* I built a synchronized caching layer between React state and browser `localStorage`. Each session is indexed under discrete keys (`supportsense_sessions` and `supportsense_history_${sessionId}`). When operators switch sessions or refresh the browser, full conversation streams are rehydrated instantaneously offline without placing recurring load on the backend database.

**5. Resolving Conversational Ambiguity in Follow-up Turns (Multi-Turn Context Drift)**
- *Challenge:* Customers frequently ask brief follow-up questions in subsequent turns (e.g., *"What products are in there?"*) without repeating their order number. Conventional stateless chatbots treat the inquiry in isolation and fail to resolve the target entity.
- *Solution:* I implemented a conversational context lookback mechanism in the persistence repository. The system traverses up to 100 preceding dialog turns to locate the active order entity in scope, automatically binding it to the subsequent SQL KAG query without requiring user re-entry.

---

## Business Value & Key Takeaways

- **Measurable Financial Efficiency:** Demonstrated that combining semantic routing with deterministic direct-path resolution cuts operational AI token expenditure by up to 70% in high-volume customer service operations.
- **Enterprise Trust Through Verifiable Auditing (*Auditable AI*):** Understood that enterprise adoption hinges on transparency. Providing an inspectable data trail via the *Grounding Audit Drawer* delivers total peace of mind to business stakeholders, compliance teams, and legal departments.
- **Superiority of Separation of Concerns:** Reinforced the architectural imperative of decoupling structured transactional records (SQL for financial amounts, logistics dates, and SKUs) from unstructured regulatory knowledge (Vectors for policy clauses). The resulting Hybrid RAG + KAG architecture dramatically outperforms naive document-only RAG systems.
- **Production-Grade Software Defense:** Solidified expertise in engineering resilient AI applications—from rigorous input domain guardrails and neural circuit breakers to client-side crash isolation via React Error Boundaries and automated test suites boasting 58 passing tests.
