# Verifikasi penyempurnaan

Tanggal: 5 November 2026 (Asia/Jakarta).

Saya menjalankan lint dan 49 unit test (47 tes lama serta 2 tes batas sumber dashboard). Seluruh tes lulus. Streamlit AppTest dari root menampilkan 5 KPI tanpa exception serta peringatan mode sampel. Fallback memakai sampel asli 5.000 baris pada SQLite sementara, tanpa menulis warehouse penuh atau mengganti angka laporan. Saya memeriksa 28 tautan relatif README tanpa target berkas rusak.

KPI penuh tetap mengikuti reports/sql_output/01_ringkasan_kpi.csv: gross GBP19.642.692,15, retur GBP716.425,97, net GBP18.926.266,18, 39.516 invoice dan 5.875 pelanggan terdaftar. Angka ringkasan dibaca dengan pembulatan yang sama di README dan laporan. Pipeline penuh tidak saya jalankan ulang karena unduhan UCI ditolak jaringan (403). Angka penuh tidak dianggap hasil eksekusi ulang kali ini. Notebook dan output SQL final dipertahankan.

Saya memisahkan dependensi runtime dan pengembangan yang dipin. Screenshot otomatis opsional memerlukan pemasangan Playwright dan Chromium secara terpisah. Deployment Streamlit memerlukan login pemilik; URL demo belum tersedia.

Saya menambahkan English summary setelah badge. Tag `v1.0.0` menunjuk commit terakhir main sebelum penyempurnaan, dengan riwayat linear tanpa commit merge dua parent.
