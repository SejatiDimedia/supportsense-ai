# PRD — AI-Powered Customer Support Assistant

**Versi**: 1.0
**Status**: Draft untuk portofolio Upwork (AI Automation Engineer role)
**Tujuan dokumen**: Menjadi acuan build sekaligus artefak yang bisa dilampirkan/dibagikan ke calon client sebagai bukti kemampuan system design, bukan cuma coding.

---

## 1. Overview

### 1.1 Latar Belakang
Perusahaan menerima pertanyaan customer berulang seputar produk, kebijakan, dan status order. Sebagian besar pertanyaan bisa dijawab dari dokumentasi (FAQ, SOP, product docs), sebagian lain butuh data relasional real-time (status order, siapa PIC yang menangani, history komplain). Tim support sering kewalahan menjawab manual, dan tidak ada sistem yang bisa membedakan "pertanyaan umum" vs "pertanyaan spesifik akun" secara otomatis.

### 1.2 Solusi
AI Assistant yang menggabungkan:
- **RAG** (Retrieval-Augmented Generation) untuk menjawab dari dokumen tidak terstruktur (FAQ, kebijakan, manual produk)
- **KAG** (Knowledge-Augmented Generation) untuk menjawab dari data relasional (customer → order → produk → issue → PIC)
- **Agentic routing** untuk menentukan kapan harus pakai RAG, KAG, tool-call langsung, atau eskalasi ke manusia
- **n8n** sebagai orchestration layer untuk eksekusi aksi (buat tiket, notifikasi, update sheet/CRM)

### 1.3 Target Pengguna
- Demo internal (portofolio) — end user adalah "customer" fiktif via web chat
- Skenario nyata (kalau dipakai client) — tim customer support & customer end-user

---

## 2. Prinsip Arsitektur (Non-Negotiable)

Semua keputusan desain di PRD ini diuji terhadap 6 prinsip berikut. Tiap komponen di Section 4 akan merujuk balik ke prinsip mana yang dipenuhi.

| # | Prinsip | Definisi Operasional untuk Proyek Ini |
|---|---|---|
| 1 | **Fit for Purpose** | Mulai dari modular monolith, bukan microservices. Tidak ada Kubernetes, tidak ada message broker eksternal di awal (n8n sudah cukup sebagai orchestrator ringan). |
| 2 | **Maintainability** | Struktur folder per domain (`rag/`, `kag/`, `agent/`, `ingestion/`, `api/`), bukan per tipe file. Setiap domain punya interface jelas, tidak saling import internal. |
| 3 | **Evolvability** | Domain `retrieval` (RAG) dan `graph` (KAG) dibungkus sebagai *service module* dengan kontrak API internal — siap diekstrak jadi microservice terpisah tanpa refactor besar kalau load naik. |
| 4 | **Resilience** | LLM lokal (Ollama) sebagai dependency utama diberi timeout + fallback jawaban degradasi. n8n workflow pakai retry + error branch, bukan fail-silent. |
| 5 | **Observability** | Structured logging (JSON) di setiap layer, request tracing dengan `trace_id` end-to-end dari webhook → API → LLM → response. |
| 6 | **Cost Efficiency** | 100% open-source & self-hosted (Ollama, Chroma, NetworkX/SQLite, n8n self-host, Streamlit). Tidak ada biaya API LLM berbayar di fase demo. |

---

## 3. Goals & Non-Goals

### Goals (MVP untuk portofolio)
- Customer bisa tanya via web chat (Streamlit) dan dapat jawaban akurat dari FAQ (RAG)
- Customer bisa tanya status order spesifik dan sistem traverse relasi data (KAG)
- Sistem bisa menentukan sendiri apakah butuh RAG, KAG, atau keduanya (agentic routing)
- Kalau confidence rendah / pertanyaan di luar cakupan → otomatis eskalasi (buat "tiket" dummy via n8n + notifikasi)
- Semua transaksi tercatat dengan trace_id yang bisa ditelusuri dari log

### Non-Goals (sengaja tidak dikerjakan di fase ini)
- Autentikasi multi-user / role-based access — cukup single-session demo
- Payment/billing integration
- Multi-language support (fokus Bahasa Inggris dulu)
- Horizontal scaling / load balancing — belum relevan di skala demo
- Fine-tuning model — pakai model open-source apa adanya

---

## 4. Arsitektur Sistem

### 4.1 Pilihan Arsitektur: Modular Monolith

**Kenapa bukan microservices dari awal:**
Traffic di fase ini rendah (demo/portofolio), tim adalah 1 orang (kamu), dan kompleksitas microservices (service discovery, distributed tracing lintas service, network overhead) akan memperlambat rilis tanpa manfaat nyata. Ini justru melanggar prinsip *Fit for Purpose*.

**Kenapa bukan "big ball of mud" monolith biasa:**
Modular monolith berarti satu deployable unit (satu FastAPI app), TAPI dengan batasan domain yang tegas secara kode — supaya kalau nanti butuh pisah (misal RAG service butuh GPU dedicated, atau KAG butuh graph DB terpisah), ekstraksinya tinggal "angkat folder jadi service", bukan bongkar total.

### 4.2 Diagram Arsitektur (High-Level)

```
┌─────────────────┐
│  Streamlit UI    │  (Presentation Layer)
│  (Web Chat)      │
└────────┬─────────┘
         │ HTTP
         ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Application (Monolith)           │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐                  │
│  │ API Layer    │──▶│ Agent Router │ (decide: RAG/    │
│  │ /chat        │   │ (Hermes fn-  │  KAG/tool/       │
│  │ /health      │   │  calling)    │  escalate)       │
│  └─────────────┘   └──────┬───────┘                  │
│                             │                          │
│         ┌───────────────────┼───────────────────┐      │
│         ▼                   ▼                   ▼      │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐│
│  │ RAG Module   │   │ KAG Module   │   │ Escalation   ││
│  │ - chunking   │   │ - graph query│   │ Module       ││
│  │ - embedding  │   │ - traversal  │   │ - confidence ││
│  │ - retrieval  │   │              │   │   check      ││
│  │ - reranking  │   │              │   │ - webhook out││
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘│
│         │                   │                   │       │
│         ▼                   ▼                   │       │
│  ┌─────────────┐   ┌──────────────┐             │       │
│  │ Chroma       │   │ NetworkX /   │             │       │
│  │ (Vector DB)  │   │ SQLite Graph │             │       │
│  └─────────────┘   └──────────────┘             │       │
│                                                    │       │
│  ┌──────────────────────────────────────────┐    │       │
│  │ Ollama Client (LLM + Embedding calls)      │◀───┘       │
│  │ - timeout & retry wrapper                  │            │
│  │ - circuit breaker                          │            │
│  └──────────────────────────────────────────┘            │
│                                                             │
│  ┌──────────────────────────────────────────┐             │
│  │ Observability Layer                        │             │
│  │ - structured logger (JSON + trace_id)       │             │
│  │ - metrics endpoint (/metrics, Prometheus fmt)│            │
│  └──────────────────────────────────────────┘             │
│                                                             │
│  ┌──────────────────────────────────────────┐             │
│  │ Persistence: SQLite (conversation history, │             │
│  │ escalation log, request log)                │             │
│  └──────────────────────────────────────────┘             │
└──────────────────────┬──────────────────────────────────┘
                        │ Webhook (async, fire-and-forget with retry)
                        ▼
              ┌───────────────────┐
              │  n8n (self-hosted) │
              │  - escalation flow │
              │  - notif ke email/ │
              │    Slack (dummy)   │
              │  - update sheet    │
              └───────────────────┘
```

### 4.3 Struktur Folder (Separation of Concerns)

```
ai-support-assistant/
├── app/
│   ├── api/                 # HTTP layer — hanya request/response handling
│   │   ├── routes_chat.py
│   │   └── routes_health.py
│   ├── agent/                # Orchestration & routing logic
│   │   ├── router.py         # decide RAG/KAG/escalate
│   │   └── hermes_client.py  # function-calling wrapper
│   ├── rag/                  # Domain: unstructured retrieval
│   │   ├── chunking.py
│   │   ├── embedder.py
│   │   ├── retriever.py
│   │   └── reranker.py
│   ├── kag/                  # Domain: relational/graph retrieval
│   │   ├── graph_builder.py
│   │   └── graph_query.py
│   ├── escalation/           # Domain: human handoff
│   │   ├── confidence.py
│   │   └── webhook_client.py
│   ├── llm/                  # Shared infra: Ollama client
│   │   ├── client.py         # timeout, retry, circuit breaker
│   │   └── models.py
│   ├── observability/        # Shared infra: logging, metrics, tracing
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   ├── persistence/          # Shared infra: DB access
│   │   ├── db.py
│   │   └── repository.py
│   └── main.py                # FastAPI app entrypoint
├── n8n/
│   └── workflows/             # exported n8n workflow JSON
├── data/
│   ├── docs/                  # dummy FAQ/policy docs
│   └── graph_seed.json        # dummy customer-order-product data
├── ui/
│   └── streamlit_app.py
├── tests/
├── docker-compose.yml
└── README.md
```

**Aturan Separation of Concerns:**
- `rag/`, `kag/`, `escalation/` **tidak boleh saling import**. Kalau `kag` butuh hasil dari `rag`, komunikasi harus lewat `agent/router.py`, bukan cross-import.
- Ubah logic reranking di `rag/reranker.py` tidak akan pernah menyebabkan bug di `kag/` — karena tidak ada shared mutable state, hanya kontrak fungsi (input/output jelas, tidak ada side effect antar modul).
- `llm/client.py` adalah satu-satunya titik yang boleh memanggil Ollama — supaya kalau nanti ganti provider (misal ke API berbayar untuk production), cukup ubah satu file.

### 4.4 Jalur Evolusi (Evolvability)

| Trigger | Aksi Evolusi |
|---|---|
| RAG retrieval jadi bottleneck (butuh GPU dedicated) | Ekstrak `rag/` jadi service terpisah, expose via internal REST/gRPC, panggil dari monolith seperti biasa |
| Graph data membesar (>100k node) | Migrasi dari NetworkX in-memory ke Neo4j (masih gratis, Community Edition), ganti `kag/graph_query.py` saja |
| Traffic tinggi & butuh async processing | Tambahkan queue (Redis/RabbitMQ, self-host gratis) di antara API dan LLM call, tanpa ubah domain logic |
| Butuh multi-tenant / multi-tim | Baru pertimbangkan split jadi microservices dengan API gateway |

Prinsipnya: **jangan split sebelum ada bukti nyata butuh split**. Modular monolith memberi opsi ini tanpa memaksa biaya operasional di awal.

---

## 5. Resilience & Fault Tolerance

| Skenario Kegagalan | Strategi Mitigasi |
|---|---|
| Ollama down / timeout | `llm/client.py` pakai timeout (misal 15s) + retry (2x, exponential backoff). Kalau tetap gagal → jawaban fallback: *"Maaf, sistem sedang sibuk, tim kami akan follow up manual"* + otomatis trigger escalation |
| Vector DB (Chroma) corrupt/tidak bisa diakses | Circuit breaker: kalau gagal 3x berturut-turut, skip RAG, fallback ke jawaban generik dari LLM tanpa context (graceful degradation, bukan crash total) |
| n8n webhook gagal terkirim (network issue) | Webhook call bersifat **fire-and-forget dengan retry queue lokal** (simpan ke tabel `pending_webhooks` di SQLite, retry via background job) — jadi eskalasi tidak hilang meski n8n sedang down |
| Query KAG tidak menemukan path (data tidak lengkap) | Return empty context, bukan exception — LLM tetap jalan dengan context kosong dan menjawab "informasi tidak ditemukan" |
| Reranker model gagal load | Fallback ke retrieval tanpa reranking (skip step, bukan block seluruh request) |

**Prinsip inti**: kegagalan di satu dependency (LLM, vector DB, n8n) **tidak boleh membuat seluruh chat endpoint down**. Selalu ada jalur degradasi yang tetap memberi respons ke user.

---

## 6. Observability

### 6.1 Structured Logging
Setiap request dapat `trace_id` unik (UUID) yang mengikuti alur: `API → Agent Router → RAG/KAG → LLM → n8n webhook`. Format log JSON:
```json
{
  "trace_id": "a1b2c3d4",
  "timestamp": "2026-09-11T10:23:00Z",
  "layer": "rag.retriever",
  "event": "retrieval_completed",
  "latency_ms": 142,
  "chunks_retrieved": 5,
  "status": "success"
}
```

### 6.2 Metrics
Endpoint `/metrics` (format Prometheus) menyediakan:
- Latency per komponen (embedding, retrieval, rerank, LLM generation, total)
- Jumlah request per route (RAG-only, KAG-only, hybrid, escalated)
- Error rate per dependency (Ollama, Chroma, n8n webhook)
- Resource usage dasar (bisa pakai `psutil` untuk CPU/RAM proses)

### 6.3 Tracing End-to-End
Karena skala masih kecil, tidak perlu Jaeger/OpenTelemetry penuh — cukup **trace_id yang konsisten di semua log line**, ditambah tabel `request_log` di SQLite yang menyimpan timeline tiap layer. Ini cukup untuk debug "kenapa response lambat" tanpa overhead infra tracing terdistribusi. Kalau nanti scale naik, tinggal ganti logger ke OpenTelemetry SDK — kontrak `trace_id` sudah kompatibel.

---

## 7. Cost Efficiency

| Komponen | Biaya | Alasan |
|---|---|---|
| LLM & Embedding | Rp 0 | Ollama self-host, model open-source |
| Vector DB | Rp 0 | Chroma in-process, tidak butuh server terpisah |
| Graph | Rp 0 | NetworkX in-memory / SQLite untuk skala kecil |
| Orchestration | Rp 0 | n8n self-hosted via Docker |
| Compute | Biaya listrik laptop/PC pribadi | Tidak ada cloud compute di fase demo |
| Deployment demo | Rp 0 | Cloudflare Tunnel / ngrok free tier untuk akses sementara |

**Keputusan sadar**: tidak pakai Kubernetes, tidak pakai managed vector DB berbayar (Pinecone dll), tidak pakai LLM API berbayar (OpenAI/Anthropic) di fase ini — karena volume transaksi portofolio jauh di bawah threshold yang membenarkan biaya tersebut. Kalau nanti dipakai client dengan traffic nyata, baru evaluasi ulang trade-off biaya vs performa (misal: LLM API berbayar untuk akurasi lebih tinggi, managed vector DB untuk mengurangi ops burden).

---

## 8. Data Model

### 8.1 RAG — Document Store (Chroma)
```
Collection: support_docs
- id: string
- document: text (chunk ~300-500 token)
- embedding: vector (768 dim, nomic-embed-text)
- metadata: { source: "faq.md" | "policy.md" | "product_manual.md", section: string }
```

### 8.2 KAG — Graph Schema (dummy data)
**Entities (nodes):** `Customer`, `Order`, `Product`, `Issue`, `Agent`

**Relations (edges):**
```
Customer -[PLACED]-> Order
Order -[CONTAINS]-> Product
Order -[HAS_ISSUE]-> Issue
Issue -[ASSIGNED_TO]-> Agent
Product -[BELONGS_TO_CATEGORY]-> Category
```

### 8.3 Persistence (SQLite)
```sql
-- conversation history
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY,
  trace_id TEXT,
  session_id TEXT,
  role TEXT, -- 'user' | 'assistant'
  message TEXT,
  route_taken TEXT, -- 'rag' | 'kag' | 'hybrid' | 'escalated'
  confidence_score REAL,
  created_at TIMESTAMP
);

-- escalation log
CREATE TABLE escalations (
  id INTEGER PRIMARY KEY,
  trace_id TEXT,
  reason TEXT,
  webhook_status TEXT, -- 'sent' | 'pending' | 'failed'
  retry_count INTEGER DEFAULT 0,
  created_at TIMESTAMP
);
```

---

## 9. API Spec (Internal Contract)

### `POST /chat`
```json
// Request
{
  "session_id": "sess_123",
  "message": "Where is my order #4521?"
}

// Response
{
  "trace_id": "a1b2c3d4",
  "answer": "Your order #4521 is currently being handled by our support agent Budi due to a reported shipping delay.",
  "route_taken": "kag",
  "confidence_score": 0.91,
  "escalated": false,
  "latency_ms": 890
}
```

### `GET /health`
Cek status Ollama, Chroma, dan koneksi n8n webhook (lightweight ping) — dipakai untuk monitoring dasar.

### `GET /metrics`
Prometheus-format metrics.

---

## 10. n8n Workflow Design

**Workflow: `escalation-handler`**
```
[Webhook Trigger] 
      ↓
[Set Node: format ticket data]
      ↓
[IF: confidence_score < 0.6 OR route_taken == 'escalated']
      ↓ (true)                          ↓ (false)
[Create dummy ticket]              [No-op / log only]
      ↓
[Send notification — Email/Slack dummy]
      ↓
[Update Google Sheet log] (opsional, tetap gratis dengan Google Sheets free tier)
      ↓
[Respond to Webhook: success]
```

**Error handling di n8n**: setiap node kritikal (create ticket, send notif) dibungkus dengan **Error Trigger workflow** terpisah — kalau gagal, n8n log error dan retry otomatis (built-in retry setting di n8n), bukan silent fail.

---

## 11. Tech Stack Final

| Layer | Tools |
|---|---|
| LLM & Agent | Ollama, Hermes-2-Pro (atau Llama 3.1 8B) |
| Embedding | nomic-embed-text |
| Reranking | sentence-transformers cross-encoder (ms-marco-MiniLM) |
| Vector DB | Chroma |
| Graph | NetworkX (MVP) → Neo4j Community (kalau evolve) |
| Backend | Python, FastAPI |
| Automation | n8n (self-hosted, Docker) |
| Database | SQLite |
| Frontend | Streamlit |
| Observability | Custom JSON logger + `/metrics` Prometheus-format |
| Deployment | Docker Compose (lokal), Cloudflare Tunnel (demo publik) |
| Version Control | GitHub |

---

## 12. Milestones

| Fase | Deliverable | Estimasi |
|---|---|---|
| 1. Setup dasar | Docker Compose (Ollama, n8n), struktur folder, FastAPI skeleton | 1-2 hari |
| 2. RAG module | Chunking, embedding, retrieval, reranking + dummy docs | 2-3 hari |
| 3. KAG module | Graph builder + query + dummy relational data | 2 hari |
| 4. Agent router | Hermes function-calling untuk decide route | 2 hari |
| 5. Resilience & Observability | Timeout, circuit breaker, structured logging, `/metrics` | 1-2 hari |
| 6. n8n integration | Escalation workflow + webhook retry | 1 hari |
| 7. Streamlit UI | Chat interface | 1 hari |
| 8. Testing & demo prep | End-to-end test, rekam video demo, tulis README | 1-2 hari |

**Total estimasi**: ~2 minggu kerja part-time.

---

## 13. Ringkasan Justifikasi Arsitektur

| Prinsip | Bagaimana PRD Ini Memenuhinya |
|---|---|
| Fit for Purpose | Modular monolith, tanpa Kubernetes/microservices prematur |
| Maintainability | Folder per domain, no cross-import antar domain, kontrak fungsi jelas |
| Evolvability | RAG/KAG dibungkus sebagai modul siap-ekstrak, jalur migrasi graph & queue sudah dipetakan |
| Resilience | Timeout, retry, circuit breaker, graceful degradation di setiap dependency eksternal |
| Observability | trace_id konsisten, structured logging, endpoint metrics |
| Cost Efficiency | 100% open-source & self-hosted, tidak ada biaya cloud di fase demo |

---

## 14. Metodologi Eksekusi — Guided Build dengan AI Antigravity

### 14.1 Prinsip Kerja
Proyek ini dikerjakan **oleh kamu sendiri sebagai eksekutor**, dengan AI Antigravity berperan sebagai pemandu teknis langkah-demi-langkah. Tujuannya bukan sekadar "menghasilkan aplikasi jadi", tapi memastikan kamu **paham setiap keputusan teknis yang diambil**, sehingga saat interview/screening client kamu bisa menjelaskan arsitektur dan kode dengan percaya diri — bukan cuma "AI yang buatkan".

**Aturan main:**
1. Setiap langkah dari Milestone (Section 12) dipecah lebih kecil menjadi **task-level steps** (Section 14.3)
2. AI Antigravity **tidak lanjut ke step berikutnya tanpa konfirmasi eksplisit** dari kamu
3. Sebelum eksekusi tiap step, AI Antigravity wajib menjelaskan: **apa yang akan dikerjakan, kenapa (rujukan ke prinsip arsitektur di Section 2), dan apa yang perlu kamu verifikasi setelahnya**
4. Kamu berhak bertanya "kenapa begini?", "apa alternatifnya?", atau minta penjelasan ulang sebelum approve — ini bagian dari proses belajar, bukan hambatan

### 14.2 Format Interaksi per Step
Setiap step mengikuti pola tetap ini supaya konsisten dan mudah ditelusuri:

```
STEP [nomor] — [Nama Task]
──────────────────────────
Tujuan       : Apa yang dicapai step ini
Rujukan PRD  : Section berapa di PRD ini yang jadi acuan
Yang dikerjakan AI : Kode/config/command apa yang dibuat
Yang perlu kamu cek : Checklist verifikasi manual sebelum lanjut
Pertanyaan terbuka : Ruang buat kamu tanya sebelum approve

>>> Ketik "lanjut" untuk ke step berikutnya, atau tanyakan dulu.
```

### 14.3 Breakdown Step per Milestone

**Fase 1 — Setup Dasar**
- Step 1.1: Buat struktur folder sesuai Section 4.3
- Step 1.2: Setup `docker-compose.yml` untuk Ollama & n8n
- Step 1.3: Pull model LLM & embedding di Ollama, verifikasi jalan (`ollama list`, test prompt)
- Step 1.4: Buat FastAPI skeleton kosong + endpoint `/health`, verifikasi server jalan

**Fase 2 — Modul RAG**
- Step 2.1: Siapkan dummy dokumen (FAQ, policy, product manual)
- Step 2.2: Implementasi `chunking.py`, verifikasi hasil chunk masuk akal
- Step 2.3: Implementasi `embedder.py` + koneksi ke Chroma, verifikasi embedding tersimpan
- Step 2.4: Implementasi `retriever.py`, test query manual, cek relevansi hasil
- Step 2.5: Implementasi `reranker.py`, bandingkan hasil sebelum/sesudah rerank

**Fase 3 — Modul KAG**
- Step 3.1: Siapkan dummy data relasional (`graph_seed.json`)
- Step 3.2: Implementasi `graph_builder.py`, verifikasi graph terbentuk benar
- Step 3.3: Implementasi `graph_query.py`, test traversal manual dengan beberapa skenario pertanyaan

**Fase 4 — Agent Router**
- Step 4.1: Implementasi `hermes_client.py` untuk function-calling
- Step 4.2: Implementasi `router.py` — logic decide RAG/KAG/hybrid/escalate
- Step 4.3: Test end-to-end dengan beberapa pertanyaan contoh, verifikasi routing tepat

**Fase 5 — Resilience & Observability**
- Step 5.1: Tambahkan timeout + retry + circuit breaker di `llm/client.py`
- Step 5.2: Implementasi structured logger dengan `trace_id`
- Step 5.3: Implementasi endpoint `/metrics`
- Step 5.4: Simulasi kegagalan (matikan Ollama sementara) untuk verifikasi graceful degradation

**Fase 6 — Integrasi n8n**
- Step 6.1: Buat workflow `escalation-handler` di n8n
- Step 6.2: Implementasi `webhook_client.py` dengan retry queue lokal
- Step 6.3: Test skenario eskalasi end-to-end, verifikasi notifikasi terkirim

**Fase 7 — Streamlit UI**
- Step 7.1: Buat chat interface dasar
- Step 7.2: Hubungkan ke endpoint `/chat`, tampilkan trace_id & route_taken untuk keperluan demo

**Fase 8 — Testing & Demo Prep**
- Step 8.1: Skenario test menyeluruh (RAG-only, KAG-only, hybrid, escalation, failure case)
- Step 8.2: Rekam video demo
- Step 8.3: Tulis README final (arsitektur, cara run, hasil test)

### 14.4 Checkpoint Wajib Tanya
Di titik-titik berikut, AI Antigravity **wajib berhenti dan menunggu keputusanmu** sebelum lanjut, karena ada trade-off yang perlu kamu pahami dan setujui sendiri:
- Sebelum memilih model LLM spesifik (ukuran vs kecepatan vs akurasi)
- Sebelum menentukan strategi chunking (ukuran chunk, overlap)
- Sebelum finalisasi schema graph (entity & relation apa saja yang dimodelkan)
- Sebelum menentukan threshold confidence untuk eskalasi
- Sebelum deployment ke publik (Cloudflare Tunnel/ngrok) — karena menyangkut exposure data dummy ke internet

### 14.5 Output Belajar yang Diharapkan
Di akhir proyek, selain aplikasi jadi, kamu juga punya:
- Catatan keputusan teknis per step (bisa dikumpulkan jadi semacam *decision log* — nilai tambah lagi untuk portofolio, menunjukkan cara berpikir bukan cuma hasil akhir)
- Kemampuan menjelaskan setiap bagian arsitektur tanpa harus buka kode dulu
- Confidence untuk menjawab pertanyaan teknis client saat interview/screening

---

## 15. Security & Data Handling

Meski proyek ini bersifat demo/portofolio dengan data dummy, praktik keamanan tetap diterapkan sejak awal — ini justru poin plus yang bisa ditunjukkan ke client bahwa kamu terbiasa dengan best practice, bukan cuma "asal jalan".

### 15.1 Prinsip untuk Fase Demo
- **Tidak ada data customer/perusahaan asli** yang dipakai — semua dummy dan disebutkan eksplisit di README
- **Konfigurasi sensitif** (URL Ollama, webhook n8n, API key kalau ada) disimpan di `.env`, tidak pernah hardcode di kode atau ter-commit ke GitHub (`.gitignore` mencakup `.env`)
- **Akses demo publik** (via Cloudflare Tunnel/ngrok) diberi basic auth sederhana atau session token, tidak dibiarkan terbuka tanpa proteksi — mencegah orang asing mengakses instance Ollama/n8n kamu
- **Log tidak menyimpan informasi yang meniru data pribadi asli** meski itu dummy, sebagai kebiasaan yang benar sejak awal

### 15.2 Catatan untuk Skenario Produksi (Kalau Nanti Dipakai Client Sungguhan)
Bagian ini **tidak dikerjakan di fase demo**, tapi dicatat sebagai kesadaran arsitektur (relevan untuk diskusi teknis dengan client):
- Data customer asli perlu enkripsi at-rest (database) dan in-transit (HTTPS wajib, bukan opsional)
- Perlu access control berbasis role (support agent vs admin) sebelum multi-user
- Perlu audit log terpisah dari application log untuk kebutuhan compliance
- Vector DB & graph DB yang menyimpan data customer perlu kebijakan retensi & penghapusan data (relevan untuk GDPR-like requirements tergantung yurisdiksi client)

---

## 16. Testing Strategy

### 16.1 Unit Test
Fokus pada modul yang logic-nya deterministik dan tidak bergantung pada model LLM benar-benar jalan (supaya test cepat & stabil):
- `chunking.py` — verifikasi ukuran chunk & overlap sesuai spesifikasi
- `graph_query.py` — verifikasi traversal menghasilkan path yang benar untuk graph dummy
- `router.py` — verifikasi logic routing (kalau confidence < threshold → escalate, dst.) dengan **mock response** dari Hermes/Ollama, bukan panggil model asli
- `confidence.py` — verifikasi scoring logic

**Prinsip**: LLM & embedding call di-mock di unit test. Tujuannya supaya test suite bisa jalan cepat dan konsisten tanpa tergantung Ollama menyala, dan supaya jelas membedakan "bug logic" vs "model kebetulan jawab beda".

### 16.2 Integration Test
Test yang benar-benar memanggil Ollama, Chroma, dan n8n (jalan lokal), untuk memverifikasi seluruh chain terhubung dengan benar:
- Test `/chat` endpoint end-to-end dengan pertanyaan contoh dari Section 17 (Appendix)
- Test webhook eskalasi benar-benar sampai ke n8n dan trigger workflow

### 16.3 Failure Simulation Test
Sengaja mematikan/mengganggu satu dependency untuk verifikasi resilience (Section 5) benar-benar bekerja, bukan cuma teori di PRD:
- Matikan Ollama → verifikasi fallback jawaban degradasi muncul, bukan error 500
- Matikan n8n → verifikasi webhook masuk retry queue lokal, tidak hilang
- Kosongkan hasil retrieval RAG → verifikasi LLM tetap merespons dengan graceful "informasi tidak ditemukan"

### 16.4 Definition of Done per Fase
Supaya progres tidak ambigu, tiap fase di Section 12/14.3 dianggap selesai kalau:

| Fase | Definition of Done |
|---|---|
| 1. Setup Dasar | `docker-compose up` jalan tanpa error, `/health` return 200, Ollama bisa generate response test |
| 2. RAG | Query dummy menghasilkan chunk relevan yang secara manual dinilai benar (spot check minimal 5 query) |
| 3. KAG | Minimal 3 skenario traversal (lihat Section 17) menghasilkan path & jawaban yang benar |
| 4. Agent Router | Routing tepat untuk minimal 8 skenario campuran (RAG/KAG/hybrid/escalate) |
| 5. Resilience & Observability | Semua 3 failure simulation test (16.3) menghasilkan graceful degradation, bukan crash |
| 6. n8n Integration | Eskalasi end-to-end terverifikasi sampai notifikasi diterima |
| 7. UI | Chat interface bisa dipakai tanpa error untuk seluruh skenario demo |
| 8. Testing & Demo | Semua skenario Section 17 sudah dites & didokumentasikan hasilnya di README |

---

## 17. Appendix — Skenario Demo & Test Case

Daftar ini punya fungsi ganda: sebagai **test case** selama development, dan sebagai **script video demo** di akhir proyek.

| # | Tipe | Pertanyaan Contoh | Ekspektasi Jawaban / Route |
|---|---|---|---|
| 1 | RAG | "What is your refund policy?" | Jawaban dari dokumen policy, `route_taken: rag` |
| 2 | RAG | "How long is the product warranty?" | Jawaban dari product manual, `route_taken: rag` |
| 3 | KAG | "Where is my order #4521?" | Traverse Order→Issue→Agent, `route_taken: kag` |
| 4 | KAG | "Who is handling my complaint about the delayed shipment?" | Traverse Customer→Order→Issue→Agent, `route_taken: kag` |
| 5 | Hybrid | "My order #4521 arrived damaged, what's your policy on that and who can help me?" | RAG (policy kerusakan) + KAG (PIC order tersebut), `route_taken: hybrid` |
| 6 | Escalation (low confidence) | "Can you hack into my account to reset my password manually?" | Confidence rendah / di luar cakupan → `escalated: true`, tiket dummy dibuat |
| 7 | Escalation (data tidak ditemukan) | "Where is order #9999999?" (order tidak ada di data) | KAG return kosong → jawaban "tidak ditemukan" + opsi eskalasi |
| 8 | Failure simulation | (Ollama dimatikan manual) "What is your refund policy?" | Fallback graceful message, bukan error 500, otomatis log ke escalation |

**Catatan**: hasil aktual dari 8 skenario ini didokumentasikan di README dengan screenshot/log sebagai bukti sistem bekerja sesuai desain — ini yang paling meyakinkan client dibanding klaim tanpa bukti.

---

## 18. Risks & Assumptions

### 18.1 Assumptions (Asumsi yang Diambil)
- Laptop/PC yang dipakai punya spesifikasi cukup untuk menjalankan model LLM kecil (min. 16GB RAM direkomendasikan; kalau 8GB, model diturunkan ke ukuran lebih kecil seperti `phi3` atau `llama3.2:1b`)
- Dummy data (dokumen & graph) dianggap cukup representatif untuk mendemonstrasikan kapabilitas RAG+KAG, meski skalanya jauh lebih kecil dari data produksi asli
- Model open-source (Llama/Qwen/Hermes ukuran kecil-menengah) dianggap cukup untuk demo, meski akurasinya tidak akan setara model besar berbayar (GPT-4 class)
- n8n self-hosted dan Ollama berjalan di mesin yang sama dengan aplikasi (tidak ada asumsi infrastruktur terdistribusi)

### 18.2 Risks (Risiko yang Disadari Sejak Awal)
| Risiko | Dampak | Mitigasi |
|---|---|---|
| Model kecil kurang akurat untuk reasoning kompleks | Jawaban hybrid/agentic routing bisa salah arah | Uji dengan beberapa model, pilih yang paling stabil untuk function-calling (Hermes dikenal kuat di area ini); dokumentasikan limitasi secara jujur di README |
| Laptop tidak kuat menjalankan model + Chroma + n8n bersamaan | Demo lemot atau crash saat presentasi live | Siapkan video demo hasil rekaman sebagai cadangan kalau live demo bermasalah |
| Dummy data terlalu sederhana sehingga tidak meyakinkan kompleksitas nyata | Client meragukan kemampuan sistem menangani data skala nyata | Perkaya skenario Section 17 dengan variasi cukup (ambigu, edge case, tidak ditemukan), bukan cuma "happy path" |
| Waktu pengerjaan meleset dari estimasi 2 minggu | Portofolio molor, kehilangan momentum apply job | Prioritaskan Fase 1-4 (core RAG+KAG+routing) selesai dulu sebagai MVP yang sudah bisa didemokan, Fase 5-8 sebagai penyempurnaan |
| Ketergantungan ke AI Antigravity untuk tiap step membuat proses lambat di awal | Momentum belajar/eksekusi terganggu | Checkpoint wajib (14.4) dibatasi hanya di keputusan penting, bukan tiap baris kode — supaya tetap efisien |