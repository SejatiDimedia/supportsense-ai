# SupportSense AI: Asisten Layanan Pelanggan Otomatis untuk Operasional Bisnis

Asisten virtual cerdas yang menjawab pertanyaan kebijakan operasional sekaligus melacak status transaksi secara akurat untuk memangkas beban kerja tim layanan pelanggan.

## Latar Belakang

Banyak perusahaan menerima volume pertanyaan berulang yang tinggi setiap hari. Pertanyaan tersebut umumnya terbagi dalam dua kelompok, yaitu pertanyaan seputar kebijakan umum (seperti prosedur pengembalian dana, garansi, dan panduan produk) serta pertanyaan spesifik terkait transaksi pelanggan (seperti lokasi paket, kendala kurir, dan staf yang menangani keluhan).

Penanganan manual untuk kedua jenis pertanyaan ini membuat tim operasional kewalahan, memperlambat waktu tunggu pelanggan, dan meningkatkan biaya operasional. Di sisi lain, sistem asisten otomatis biasa kerap memberikan jawaban yang tidak tepat (halusinasi) atau tidak mampu menghubungkan data transaksi yang tersebar di berbagai catatan internal. Akibatnya, pelanggan mendapatkan informasi yang salah dan beban kerja tim layanan pelanggan tetap tinggi.

## Tujuan Proyek

Membangun asisten layanan pelanggan berbasis AI yang mampu:
- Menjawab pertanyaan kebijakan operasional secara akurat langsung dari panduan resmi.
- Memeriksa data transaksi dan riwayat penanganan kendala pelanggan secara tepat.
- Memberikan respons instan untuk percakapan umum seperti sapaan dan ucapan terima kasih.
- Mengalihkan pertanyaan rumit atau permintaan berisiko ke staf manusia secara otomatis tanpa risiko data hilang.

## Solusi

### 1. Penelusuran Dokumen Kebijakan yang Tepat
Sistem mencari informasi dari panduan dan dokumen resmi perusahaan, menyaring bagian yang paling relevan, dan menyusun jawaban yang sesuai dengan aturan operasional yang berlaku.

### 2. Pelacakan Riwayat Transaksi dan Penanganan Kendala
Sistem menelusuri data relasional pelanggan, nomor pesanan, rincian produk, catatan kendala pengiriman, hingga staf operasional yang ditugaskan, sehingga pelanggan memperoleh status yang jelas dan pasti.

### 3. Respons Cepat untuk Percakapan Rutin
Sapaan umum dan ungkapan terima kasih dijawab langsung dalam hitungan milidetik tanpa membebani sistem pemrosesan utama, menjaga interaksi tetap responsif dan hemat sumber daya.

### 4. Pengalihan Mandiri ke Staf Manusia dengan Jaminan Antrean Aman
Ketika sistem mendeteksi tingkat kepastian informasi yang rendah, data pesanan tidak ditemukan, atau terdapat permintaan keamanan yang mencurigakan, sistem otomatis membuat tiket tindak lanjut untuk staf operasional. Jika saluran pengiriman tiket sedang mengalami gangguan jaringan, data tiket tetap tersimpan di antrean cadangan lokal untuk dikirim ulang setelah koneksi pulih.

### 5. Panel Transparansi Dasar Jawaban
Operator dan staf pengawas dapat memeriksa langsung kutipan panduan atau catatan data transaksi yang menjadi dasar dari setiap jawaban yang dihasilkan asisten.

## Hasil

Pengujian pada skenario operasional menunjukkan:
- 8 dari 8 skenario pengujian bisnis lulus verifikasi fungsional dengan tingkat keberhasilan 100%.
- 47 pengujian unit otomatis dinyatakan lulus tanpa kesalahan.
- Respons sapaan langsung diberikan dalam waktu 2 milidetik.
- Deteksi permintaan manipulasi keamanan dan pengalihan ke staf diselesaikan dalam waktu 12 milidetik.
- Seluruh tiket eskalasi yang dibuat saat layanan otomasi eksternal tidak aktif berhasil tertahan di antrean lokal tanpa ada data yang hilang.

## Teknologi

FastAPI, Python, Ollama, ChromaDB, PostgreSQL, NetworkX, n8n, React, dan Streamlit.

## Konsultasi

Tertarik mengotomatisasi layanan pelanggan bisnis Anda dengan asisten yang aman dari kesalahan informasi? Mari diskusikan kebutuhan dan arsitektur alur kerja perusahaan Anda dalam sesi konsultasi.
