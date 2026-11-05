# Ringkasan Proyek (Format STAR)

Format ringkas ini ditujukan untuk resume CV, profil LinkedIn, dan bahan persiapan wawancara kerja.

### Situation
Banyak operasional bisnis kewalahan menangani volume pertanyaan pelanggan berulang yang terbagi antara kebijakan umum dan data relasional pesanan spesifik. Solusi chatbot konvensional sering mengalami kesalahan informasi (halusinasi) atau gagal menelusuri hubungan data transaksi lintas entitas, sementara ketidakstabilan pada layanan inferensi model kerap memicu kegagalan sistem secara menyeluruh.

### Task
Sebagai pengembang tunggal dalam peran AI Automation Engineer, tanggung jawab saya adalah merancang dan membangun asisten layanan pelanggan otonom berbasis arsitektur modular monolith yang mampu menjawab pertanyaan kebijakan secara akurat, menelusuri data transaksi secara deterministik, merespons percakapan umum secara instan, serta mengalihkan kendala kritis ke staf operasional tanpa risiko kehilangan data.

### Action
Saya mengimplementasikan sistem penelusuran ganda yang memadukan RAG (ChromaDB dan reranker Cross-Encoder) untuk dokumen panduan serta KAG (PostgreSQL dan graf NetworkX) untuk data relasional pesanan. Di layer orkestrasi, saya membangun agent router dengan jalur pintas deterministik untuk sapaan dan penyaringan keamanan, membungkus inferensi model bahasa lokal dengan pola keandalan SRE Circuit Breaker, serta mengintegrasikan antrean eskalasi persisten pada SQLite untuk menjamin pengiriman ulang tiket ke webhook otomasi n8n saat jaringan terputus.

### Result
Sistem meraih tingkat kelulusan 100% pada 8 skenario pengujian bisnis acuan serta menyelesaikan seluruh 47 pengujian unit otomatis tanpa kesalahan. Respons sapaan rutin berhasil ditekan hingga 2 milidetik tanpa konsumsi token model, deteksi pelanggaran keamanan diselesaikan dalam 12 milidetik, dan seluruh tiket keluhan saat layanan eksternal mengalami gangguan berhasil diamankan di antrean cadangan lokal tanpa kehilangan data.
