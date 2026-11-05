# Project Summary (STAR Format)

This concise overview is tailored for CV resumes, LinkedIn profiles, and interview talking points.

### Situation
Customer support operations struggle with heavy volumes of repetitive inquiries split between general company policies and order-specific relational records. Conventional chatbots often suffer from informational hallucinations or fail to navigate multi-hop entity relations across transactional databases, while upstream inference outages frequently cause unhandled application crashes.

### Task
As the sole developer in an AI Automation Engineer role, my objective was to design and build an autonomous customer support assistant utilizing a modular monolith architecture capable of answering policy questions accurately, traversing relational order records deterministically, delivering instant conversational courtesy responses, and escalating complex issues to human staff with zero data loss.

### Action
I engineered a dual-retrieval pipeline combining RAG (ChromaDB and Cross-Encoder reranking) for unstructured documents with KAG (PostgreSQL and NetworkX graphs) for relational order data. At the orchestration layer, I developed an agent router featuring deterministic fast-path filters for greetings and security enforcement, wrapped local model inference in an SRE Circuit Breaker state machine, and integrated a durable local SQLite staging queue to guarantee offline retry delivery to automation webhooks.

### Result
The system achieved a 100% pass rate across all 8 operational benchmark scenarios and completed all 47 automated unit tests cleanly. Direct greeting latency dropped to 2 milliseconds with zero token consumption, security violation attempts were neutralized in 12 milliseconds, and all escalation tickets dispatched during simulated automation outages were retained safely in the local queue with zero data loss.
