# PRD SupportSense AI: Perbaikan dan Pengembangan v2
*Disusun 5 November 2026 · Berdasarkan audit kode repo SejatiDimedia/supportsense-ai · Status: Draft untuk dieksekusi*

---

## 1. Ringkasan
SupportSense AI v1 sudah memiliki RAG, retrieval relasional (PostgreSQL), circuit breaker, logging terstruktur dengan `trace_id`, metrics Prometheus, dan 57 fungsi test. Audit menemukan tiga kelompok masalah: 
1. Celah keamanan dan bug yang berisiko jika repo dilihat klien.
2. Klaim README yang tidak sejalan dengan perilaku kode.
3. Kapabilitas yang diminta pasar untuk peran AI Automation & Agent Engineer yang belum ada.

Dokumen ini mendefinisikan apa yang diperbaiki, urutan prioritasnya, dan kriteria selesai untuk tiap item.

### Tujuan
1. Menutup risiko keamanan dan bug kritis sebelum repo dipakai sebagai bukti di proposal.
2. Menyelaraskan dokumentasi dengan perilaku kode yang sebenarnya.
3. Menambah kapabilitas v2: aksi nyata dengan human approval, structured output, adapter Claude/OpenAI, Telegram + n8n sungguhan, MCP, serta eval dan tracing.
4. Menjadikan repo ini studi kasus utuh: v1 (RAG + resiliensi) menuju v2 (siap produksi).

### Bukan Tujuan (*Non-goals*)
- Mengganti arsitektur modular monolith menjadi microservices.
- Sistem multi-agent (hanya dipertimbangkan jika terbukti perlu lewat eval).
- Integrasi WhatsApp (berbayar; channel dibuat modular, Telegram dulu).
- Redesign UI besar-besaran.

---

## 2. Hasil Audit Singkat

| Area | Status | Catatan |
|---|:---:|---|
| **RAG (chunker, retriever, reranker)** | Kuat | Section-aware chunking, cross-encoder |
| **Resiliensi LLM** | Baik | Timeout, backoff, circuit breaker (ada bug minor) |
| **Observability** | Parsial | `trace_id` dan Prometheus ada; tidak ada tracing LLM dan biaya |
| **Keamanan** | Lemah | Tanpa auth, kebocoran kredensial, risiko IDOR |
| **Eskalasi dan n8n** | Stub | Notifikasi hanya console.log; retry tidak otomatis |
| **Agent behavior** | Workflow | Satu kali planning lalu logika deterministik; tool hanya baca |
| **Structured output** | Belum ada | Argumen tool call dipakai mentah |
| **Human approval** | Belum ada | Hanya handoff, tidak ada aksi yang perlu disetujui |
| **Provider LLM** | Ollama saja | Belum ada Claude/OpenAI |
| **CI/CD dan container** | Belum ada | Tidak ada GitHub Actions dan Dockerfile aplikasi |

---

## 3. P0: Keamanan dan Bug Kritis (Hari 1 sampai 3)

### P0-1. Kebocoran `postgres_url` di `/api/telemetry`
- **Lokasi**: `app/api/routes_telemetry.py`
- **Masalah**: Response mengembalikan `settings.postgres_url` lengkap dengan user dan password.
- **Perbaikan**: Hapus field tersebut; ganti dengan boolean `connected` dan nama engine saja.
- **Kriteria Selesai**: Tidak ada string koneksi atau kredensial di response mana pun; ada unit test yang memastikannya.

### P0-2. Tanpa Autentikasi dan CORS Terlalu Longgar
- **Lokasi**: `app/main.py`, semua router
- **Masalah**: Endpoint `/chat`, `/metrics`, dan `/api/telemetry` terbuka untuk publik. CORS memakai `allow_origins=["*"]` bersama `allow_credentials=True`.
- **Perbaikan**: 
  - Dependency API key (header `X-API-Key`) untuk endpoint internal.
  - Endpoint `/metrics` dan `/api/telemetry` hanya untuk admin/internal.
  - CORS memakai allowlist dari environment tanpa wildcard.
  - Tambahkan rate limit per session dan per IP.
- **Kriteria Selesai**: Request tanpa key menerima `401 Unauthorized`; origin tidak terdaftar ditolak; ada test untuk kedua kasus.

### P0-3. Risiko IDOR dan Kebocoran Data Pribadi
- **Lokasi**: `app/kag/sql_query.py`, `app/kag/graph_query.py`, `app/agent/router.py`
- **Masalah**: Siapa pun yang mengetik nomor order mendapat nama, email pelanggan, email agen, dan resi. Seluruhnya ikut masuk ke konteks LLM.
- **Perbaikan**: 
  - Verifikasi identitas sebelum membuka data order (nomor order ditambah email atau nomor HP yang cocok).
  - Simpan daftar order terverifikasi per sesi.
  - Masking email dan data sensitif di konteks LLM.
  - Kirim ke LLM hanya field yang benar-benar dibutuhkan.
- **Kriteria Selesai**: Order milik orang lain tidak bisa dibuka tanpa verifikasi; ada test negatif untuk skenario ini.

### P0-4. Webhook Eskalasi Bergantung pada Keberhasilan Penulisan Database
- **Lokasi**: `app/agent/router.py` (blok `save_message` dan `send_escalation_webhook` dalam satu try block)
- **Masalah**: Jika penulisan SQLite gagal, webhook eskalasi tidak terkirim.
- **Perbaikan**: Menerapkan pola Outbox. Simpan eskalasi dengan status `pending` lebih dulu, lalu coba kirim; kegagalan salah satu langkah tidak menggagalkan yang lain.
- **Kriteria Selesai**: Test simulasi kegagalan DB tetap menghasilkan eskalasi terkirim atau masuk antrean pending.

### P0-5. Endpoint Async Memanggil Kode Sinkron yang Memblokir
- **Lokasi**: `app/api/routes_chat.py`, `app/llm/client.py`
- **Masalah**: `async def` memanggil `process_message` yang memakai `httpx.Client` dan `time.sleep`. Satu panggilan Ollama yang lambat dapat menahan seluruh event loop server.
- **Perbaikan**: Ubah ke `def` biasa (threadpool FastAPI) atau migrasi penuh ke `httpx.AsyncClient` dan `asyncio.sleep`.
- **Kriteria Selesai**: Tes beban 20 request paralel tidak saling memblokir; p95 latency tercatat di README.

### P0-6. Higiene Secret dan Konfigurasi
- **Masalah**: Kredensial default `postgres:postgres` tertanam di config dan compose; `.env.example` tidak memuat `POSTGRES_URL`.
- **Perbaikan**: Pindahkan ke environment variables; lengkapi `.env.example`; jalankan `gitleaks` pada seluruh riwayat git.
- **Kriteria Selesai**: `gitleaks` bersih dan `.env.example` memuat seluruh variabel yang dipakai.

---

## 4. P1: Keandalan dan Kejujuran Dokumentasi (Hari 3 sampai 7)

### P1-1. Worker Retry Eskalasi Otomatis
- **Masalah**: `process_pending_retries` hanya dipanggil dari tombol Streamlit dan test manual, sehingga klaim *zero-loss* otomatis tidak terpenuhi di dunia nyata.
- **Perbaikan**: 
  - Jalankan sebagai background task di lifespan FastAPI (atau APScheduler).
  - Tambahkan kolom `next_retry_at` dengan skema exponential backoff.
  - Status `dead_letter` setelah batas maksimal percobaan terlampaui.
  - Gauge Prometheus untuk menghitung jumlah tiket `pending`.
- **Kriteria Selesai**: Dengan n8n dimatikan lalu dinyalakan, eskalasi tertunda terkirim sendiri tanpa intervensi manual.

### P1-2. Confidence Score yang Dinamis dan Jujur
- **Masalah**: Skor saat ini adalah konstanta hardcoded per rute (`rag: 0.89`, `kag: 0.92`, `hybrid: 0.95`).
- **Perbaikan**: Ganti nama menjadi `route_score`, atau hitung secara riil dari skor reranker, kelengkapan konteks, dan pemeriksaan groundedness jawaban; sesuaikan aturan `should_escalate` dan dokumentasinya.
- **Kriteria Selesai**: Skor bervariasi dinamis mengikuti kualitas konteks dan ada test untuk konteks lemah yang memicu eskalasi.

### P1-3. Structured Output dan Validasi Tool Call
- **Lokasi**: `app/agent/hermes_client.py`, `app/agent/router.py`
- **Masalah**: Argumen tool call dipakai mentah tanpa validasi skema.
- **Perbaikan**: 
  - Model Pydantic untuk setiap tool.
  - Jika tidak valid, retry maksimal 2 kali dengan umpan balik error ke model.
  - Jika tetap gagal, fallback anggun ke eskalasi staf manusia.
- **Kriteria Selesai**: Test dengan output rusak (JSON salah, field hilang, tool tidak dikenal) tertangani tanpa crash.

### P1-4. Refactor `router.py`
- **Masalah**: Ukuran 419 baris, blok `save_message` diulang empat kali, logika bisnis bercampur aduk.
- **Perbaikan**: Pecah menjadi pipeline langkah (`prefilter`, `guardrail`, `planner`, `retrieval`, `synthesizer`, `persistence`); satu fungsi persist tunggal; target maksimal sekitar 150 baris per file.
- **Kriteria Selesai**: Seluruh test lama lulus tanpa perubahan perilaku fungsional.

### P1-5. Guardrail dan Pertahanan Prompt Injection
- **Masalah**: Deteksi berbasis keyword (`hack`, `bypass`) mudah dikelabui dan rawan salah tangkap; belum ada pertahanan terhadap prompt injection tidak langsung.
- **Perbaikan**: 
  - Gunakan word boundary dan klasifikasi intent oleh model kecil.
  - Perlakukan pesan pengguna dan dokumen hasil retrieval sebagai input tidak tepercaya (*untrusted input*).
  - Tambahkan pemisahan instruksi dan data pada prompt template.
- **Kriteria Selesai**: Suite uji injection (lihat P2-9) lulus pada ambang yang disepakati.

### P1-6. Test Suite yang Hermetik
- **Masalah**: `test_embedder` dan `test_multiturn` gagal jika dijalankan di mesin tanpa Ollama aktif dan Chroma terisi.
- **Perbaikan**: Mock Ollama dan Chroma pada unit test; tandai test yang butuh layanan nyata sebagai integration test dan jalankan terpisah.
- **Kriteria Selesai**: `pytest` lulus penuh 100% di mesin bersih dan di CI environment.

### P1-7. Perbaikan State Machine Circuit Breaker
- **Masalah**: Setiap retry internal dihitung sebagai kegagalan terpisah; status `HALF_OPEN` mengizinkan percobaan tak terbatas; tidak thread-safe.
- **Perbaikan**: Hitung kegagalan per panggilan utama, batasi satu percobaan di `HALF_OPEN`, tambahkan lock sinkronisasi.
- **Kriteria Selesai**: `test_circuit_breaker` mencakup ketiga verifikasi perilaku tersebut.

### P1-8. README dan Dokumentasi yang Jujur (*Honest Positioning*)
- **Perbaikan**: 
  - Samakan diagram dengan kenyataan (PostgreSQL sebagai sumber utama, NetworkX sebagai fallback).
  - Perbarui jumlah test yang valid.
  - Sebut 8 skenario sebagai *smoke test*, bukan klaim akurasi umum.
  - Tambahkan bagian *Known Limitations* dan *Roadmap v2*.
  - Pindahkan bagian Upwork Talking Points ke `docs/` atau rapikan dari README.
  - Tambahkan Architecture Decision Records (ADR) singkat (mengapa modular monolith, mengapa deterministic routing workflow bukan multi-agent otonom).
- **Kriteria Selesai**: Setiap klaim di README dapat diverifikasi langsung dari kode atau hasil test.

### P1-9. Fondasi DevOps Dasar
- **Perbaikan**: 
  - Dockerfile multi-stage untuk aplikasi utama.
  - Docker Compose untuk menjalankan seluruh stack lokal.
  - GitHub Actions CI (linting `ruff`, pengujian `pytest`, secret scan `gitleaks`).
  - Konfigurasi `pre-commit`.
  - Deskripsi dan topics pada repositori GitHub.
- **Kriteria Selesai**: `git clone` lalu `docker compose up` langsung menjalankan sistem, dan status badge CI hijau.

---

## 5. P2: Fitur v2 Sesuai Kebutuhan Pasar (Minggu 2 sampai 5)

### P2-1. Abstraksi Provider LLM
- Interface `LLMProvider` dengan adapter modular: Ollama, Anthropic (Claude), dan OpenAI.
- Pemilihan provider dinamis melalui konfigurasi `.env`.
- Perutean model cerdas (model kecil/cepat untuk klasifikasi dan guardrail, model besar untuk penalaran sintesis kompleks).
- Prompt caching untuk system prompt dan konteks dokumen statis di Claude.
- **Kriteria Selesai**: Ketiga provider lulus suite test fungsional yang sama.

### P2-2. Channel Telegram via n8n
- Dua antarmuka bot Telegram: **Customer Bot** (untuk interaksi publik) dan **Admin Bot** (untuk approval dan notifikasi staf).
- Verifikasi `secret_token` webhook, allowlist `chat_id` admin, dan rate limiting per chat.
- Adapter channel yang modular sehingga integrasi WhatsApp atau Web Chat dapat dipasang tanpa mengubah service agent inti.

### P2-3. Workflow n8n Produksi
- Menggantikan node stub dengan integrasi Telegram dan database sungguhan.
- Menyimpan riwayat tiket eskalasi ke PostgreSQL.
- Autentikasi header pada webhook.
- Idempotency key berbasis `trace_id`.
- ID tiket terurut dari database sequence, bukan acak/random string.

### P2-4. Aksi Nyata dengan Human Approval (*Human-in-the-Loop*)
- Tool aksi bisnis baru: `create_refund_request` dan `update_ticket_status`.
- Alur kerja approval:
  1. Agent menyiapkan aksi dengan status `pending_approval`.
  2. Admin Bot mengirimkan pesan interaktif dengan tombol **Setujui** / **Tolak** ke Telegram staf.
  3. Callback interaktif idempotent menggunakan `approval_id` unik.
  4. Aksi mutasi dieksekusi hanya setelah disetujui, dan seluruh jejak masuk audit log.
- **Kriteria Selesai**: Tombol yang ditekan berulang hanya memproses aksi satu kali; penolakan membatalkan mutasi data secara bersih.

### P2-5. Persistensi Penuh di PostgreSQL
- Memindahkan tabel `conversations`, `escalations`, `approvals`, dan `audit_log` ke PostgreSQL menggunakan migrasi database Alembic.
- SQLite dipertahankan hanya untuk mode evaluasi lokal ringan/dev.

### P2-6. Observability Terpadu dan Kontrol Biaya
- Tracing per langkah (Langfuse atau setara) yang mencatat token, biaya komputasi, dan latensi per request.
- Batasan anggaran harian dan per sesi dengan circuit breaker otomatis jika batas biaya tercapai.
- Alert biaya dan lonjakan error langsung ke grup admin Telegram.

### P2-7. Eval Suite dan Regression Testing Otomatis
- Minimal 50 test case (kombinasi kasus sintetis dan kasus nyata yang dianonymize) dengan penilaian per langkah dan end-to-end.
- LLM-as-judge yang dikalibrasi terhadap anotasi manusia.
- Regression test otomatis di CI pipeline setiap ada perubahan model atau prompt template.
- Pelaporan hasil benchmark yang dapat diaudit di dalam repositori.

### P2-8. Model Context Protocol (MCP) Server
- Membungkus pencarian order dan knowledge base internal sebagai server MCP (Model Context Protocol) read-only dengan autentikasi dan hak akses minimum.
- Diverifikasi terkoneksi dan dapat dipanggil dari Claude Desktop / Claude Code.

### P2-9. Suite Uji Ketahanan Prompt Injection
- Minimal 20 skenario serangan injeksi, termasuk serangan *indirect prompt injection* melalui dokumen hasil retrieval dan pesan manipulatif pelanggan.
- Mencatat persentase keberhasilan serangan sebelum dan sesudah penerapan filter mitigasi.

---

## 6. P3: Poles Portfolio & Publikasi
- **Video Demo (Loom) 3–5 Menit**: Menampilkan alur interaksi pelanggan, alur approval staf via Telegram, penanganan otomatis saat server down, dan dashboard biaya/tracing.
- **Diagram Arsitektur Terbaru & ADR**: Diagram Mermaid v2 dan dokumen keputusan arsitektur (ADR).
- **Higiene Bahasa Inggris**: Seluruh komentar kode, docstring, dan commit message dirapikan dalam bahasa Inggris profesional untuk calon klien internasional.
- **Tag Rilis Terstruktur**: Tag `v1.1` (perbaikan keamanan & kestabilan) dan `v2.0` (fitur baru pasar), dilengkapi file `CHANGELOG.md`.
- **Repo Edukasi Terpisah**: Mini repo "agent loop from scratch without frameworks" sebagai materi pendukung kepemimpinan teknis.

---

## 7. Jadwal Usulan Pelaksanaan

| Periode | Cakupan Kerja | Hasil / Target Deliverable |
|---|---|---|
| **Hari 1–3** | P0-1 s/d P0-6 | Repo aman dari kebocoran data, tag `v1.1-security` |
| **Hari 3–7** | P1-1 s/d P1-9 | README jujur & akurat, CI GitHub Actions hijau, test hermetik |
| **Hari 7** | **Kirim Proposal** | **Repo siap dilampirkan: v1.1 stabil & v2 sedang berjalan** |
| **Minggu 2–3** | P2-1 s/d P2-4 | Provider Claude/OpenAI, Bot Telegram, Aksi Human Approval |
| **Minggu 4–5** | P2-5 s/d P2-9 | PostgreSQL Alembic, Eval suite 50 kasus, Tracing biaya, MCP Server |
| **Minggu 6** | P3 | Video Loom, poles portofolio, rilis tag `v2.0` |

---

## 8. Metrik Keberhasilan

| Metrik Evaluasi | Target Kuantitatif |
|---|:---:|
| Temuan keamanan P0 yang masih terbuka | **0** |
| Hasil scan gitleaks pada seluruh riwayat commit | **Bersih (0 leaks)** |
| Tingkat kelulusan test di CI (mesin bersih tanpa dependensi luar) | **100% PASS** |
| Cakupan skenario evaluasi (Eval Suite) | **≥ 50 kasus teruji** |
| Serangan prompt injection yang berhasil setelah mitigasi | **< 10% dari test suite** |
| Aksi sensitif yang dieksekusi tanpa human approval | **0 (Strictly Blocked)** |
| Tiket eskalasi yang hilang saat n8n mati lalu hidup kembali | **0 (Zero Loss via Auto Worker)** |
| Transparansi biaya per percakapan dan p95 latency | **Tercatat & Dipublikasikan** |

---

## 9. Manajemen Risiko dan Mitigasi

| Risiko Potensial | Strategi Mitigasi |
|---|---|
| Cakupan kerja v2 terlalu besar sehingga pengiriman proposal tertunda | Kirim proposal tepat di Hari ke-7 setelah P0 dan P1 tuntas; selesaikan P2 secara bertahap |
| Risiko klaim fitur yang belum selesai di depan klien | Tulis status secara jujur dan transparan di README dan cover letter proposal |
| Pembengkakan biaya API Claude/OpenAI saat fase pengembangan | Pasang anggaran kuota harian ketat, gunakan model kecil untuk klasifikasi, aktifkan prompt caching |
| Uji evaluasi terlalu kecil atau memiliki bias penilaian | Sertakan data uji yang tidak dipakai saat perancangan prompt, validasi judge dengan verifikasi manusia |
| Kebocoran data pelanggan riil | Gunakan 100% data dummy atau terapkan anonimisasi ketat sebelum dimasukkan ke repositori |

---

## 10. Checklist Kesiapan Sebelum Mengirim Proposal

- [ ] Semua item P0 (P0-1 s/d P0-6) selesai dan diverifikasi lulus test
- [ ] Scan `gitleaks` bersih pada seluruh riwayat git commit
- [ ] README sudah jujur, akurat, dan konsisten dengan perilaku kode nyata
- [ ] Pipeline CI GitHub Actions hijau dan build Dockerfile berhasil
- [ ] Background worker retry eskalasi berjalan otomatis di server
- [ ] Repositori dilengkapi deskripsi, topics relevan, dan tag rilis `v1.1`
- [ ] Draft video demo singkat (Loom) tersedia
- [ ] Dokumen proposal mendeskripsikan v2 sebagai roadmap pekerjaan aktif, bukan fitur yang sudah final
