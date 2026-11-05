# Panduan Kontribusi

Terima kasih sudah tertarik membantu proyek ini. Walaupun ini adalah proyek
portofolio pribadi, saran, laporan bug, dan pull request tetap sangat diterima.

## Alur kerja

1. Fork repositori lalu buat branch dari `main`, misalnya `feat/query-churn`.
2. Pasang dependensi: `pip install -r requirements.txt`.
3. Siapkan data: `make data clean-data warehouse` (butuh koneksi internet
   untuk mengunduh dataset UCI, sekitar 45 MB).
4. Lakukan perubahan. Pastikan:
   - `ruff check .` tidak menghasilkan keluhan;
   - `python -m pytest` lulus seluruhnya;
   - jika mengubah query SQL, jalankan `python -m src.run_sql` dan perbarui
     komentar "Insight hasil" di file terkait dengan angka terbaru.
5. Buat pull request dengan deskripsi singkat: apa yang diubah dan mengapa.

## Konvensi

- **Pesan commit** mengikuti [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
- **Bahasa**: dokumentasi dan komentar kode dalam Bahasa Indonesia; nama
  variabel, fungsi, kolom, dan istilah teknis dalam bahasa Inggris.
- **Komentar kode** menjelaskan *mengapa*, bukan *apa*.
- **File SQL** diberi nomor urut dan diawali blok komentar: pertanyaan bisnis,
  logika, dan insight hasil.
- **Angka di dokumentasi** harus berasal dari hasil eksekusi nyata, bukan
  perkiraan.

## Melaporkan masalah

Buka issue dengan menyertakan versi Python, perintah yang dijalankan, dan
pesan kesalahan lengkap.
