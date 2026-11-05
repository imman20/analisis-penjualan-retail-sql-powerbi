# Pertanyaan Bisnis dan Jawabannya

Setiap pertanyaan dijawab oleh satu file SQL di folder `sql/` (dijalankan oleh
`python -m src.run_sql`, hasil di `reports/sql_output/`) dan/atau notebook.
Semua angka di bawah berasal dari eksekusi nyata pada warehouse; periode data
1 Des 2009 - 9 Des 2011, mata uang GBP.

| # | Pertanyaan bisnis | File SQL / notebook | Teknik | Insight (angka hasil) |
|---|---|---|---|---|
| 1 | Berapa skala bisnis: pendapatan, transaksi, pelanggan, AOV? | `sql/01_ringkasan_kpi.sql` | Agregasi kondisional | Pendapatan kotor 19,64 jt; retur 0,72 jt (3,6%); bersih 18,93 jt; 39.516 invoice; 5.875 pelanggan terdaftar; 4.721 produk; AOV 497,08. |
| 2 | Negara mana yang paling besar dan seberapa dominan UK? | `sql/02_penjualan_per_negara.sql` | JOIN, GROUP BY, HAVING, subquery skalar | UK 85,5% pendapatan (16,80 jt). Ekspor terbesar: EIRE 3,2%, Belanda 2,8%, Jerman 2,0%. AOV Belanda 2.545 dan Australia 1.936 vs UK 464. |
| 3 | Bagaimana tren bulanan dan kapan puncaknya? | `sql/03_tren_bulanan.sql`, notebook 01 | GROUP BY pada dim_date | November puncak di kedua tahun (1,43 jt dan 1,45 jt), 2,7x bulan terendah (Feb 2011, 0,51 jt). Kenaikan dimulai September. |
| 4 | Produk apa yang paling menghasilkan? | `sql/04_top_produk.sql` | Agregasi, ORDER BY, LIMIT | Regency Cakestand 3 Tier 314 rb bersih; White Hanging Heart T-Light Holder 252 rb; Jumbo Bag Red Retrospot 181 rb. Tidak ada produk > 1,7% pendapatan. |
| 5 | Kategori mana yang tumbuh dan menyusut? | `sql/05_kategori_per_tahun.sql` | CASE pivot per tahun | Home Decor 25,2% dan Kitchen & Dining 24,1% pangsa. Like-for-like 2011 vs 2010: Christmas & Seasonal +18,4%, Stationery +15,0%, Bags +14,0%; Candles -13,9%, Garden -12,1%. |
| 6 | Siapa pelanggan bernilai di atas rata-rata? | `sql/06_pelanggan_di_atas_rata_rata.sql` | Subquery di FROM dan WHERE | Rata-rata belanja 2.917 per pelanggan. 1.162 pelanggan (19,9%) di atas rata-rata menyumbang 13,15 jt (77% pendapatan pelanggan terdaftar). Pelanggan #1 belanja 581 rb. |
| 7 | Apakah pelanggan luar negeri memesan lebih besar? | `sql/07_cte_aov_per_wilayah.sql` | CTE, PERCENT_RANK | AOV UK 464, Eropa 821, luar Eropa 1.281; setelah pemangkasan p99 tetap 390 / 688 / 1.031. Pelanggan jauh menggabungkan pesanan. |
| 8 | Produk andalan tiap kategori? | `sql/08_window_rank_produk_per_kategori.sql` | RANK() OVER PARTITION BY | Produk #1 Candles & Lighting menyumbang 17,2% kategorinya; di Home Decor hanya 3,0% - portofolio paling terdiversifikasi. |
| 9 | Berapa pertumbuhan MoM dan YoY? | `sql/09_window_growth_mom.sql` | LAG(1), LAG(12) | Lonjakan September (+29,0% / +42,0%) dan November (+30,6% / +31,6%). YoY 2011 positif di 8 dari 11 bulan penuh; terkuat Sep 2011 +18,3%. |
| 10 | Bagaimana akumulasi YTD 2011 vs 2010? | `sql/10_window_running_total.sql` | SUM() OVER running total, moving average | YTD November 2011 8,86 jt vs 2010 8,60 jt (+3,0%). Sep-Nov = 36,2% (2010) dan 37,8% (2011) pendapatan tahunan. |
| 11 | Berapa persen pelanggan baru yang kembali? | `sql/11_cohort_retensi.sql` | Cohort analysis dengan CTE bertingkat | Retensi bulan ke-1 rata-rata 20,2%, stabil 15-22% hingga bulan ke-12 (18,3%). Kohort musim puncak (Okt-Des 2010) kembali paling rendah (5-15%). |
| 12 | Berapa produk yang menghasilkan 80% pendapatan? | `sql/12_pareto_produk.sql` | SUM() OVER kumulatif, klasifikasi ABC | 1.029 produk (21,9%) = 80% pendapatan; 2.417 produk (51,4%) hanya 5%. |
| 13 | Bagaimana komposisi segmen RFM? | `sql/13_rfm_sql.sql`, notebook 02 | NTILE(5), CASE | SQL: Champions 1.355 (23,2%) = 70,3% pendapatan. Notebook (pandas): Champions 1.304 (22,3%) = 68,6%; KMeans k = 2 (silhouette 0,44) memisahkan 2.335 pelanggan inti (88% pendapatan). |
| 14 | Kategori mana yang paling banyak diretur? | `sql/14_tingkat_retur.sql` | Agregasi kondisional, HAVING | Stationery 11,8% tetapi 1,8% tanpa satu pesanan anomali 80.995 unit; Kitchen & Dining 4,6% nilai / 7,1% unit dengan 3.401 invoice retur adalah masalah nyata. |
| 15 | Kapan transaksi terjadi? | `sql/15_pola_hari_jam.sql`, notebook 01 | strftime, GROUP BY | Puncak pukul 12.00 (6.369 invoice); Kamis tersibuk (8.168); Sabtu 30 invoice. Slot Rabu 12.00 = 3,1% seluruh invoice. |
| 16 | Apakah musim puncak 2011 lebih baik dari 2010? | notebook 03 | Uji t Welch, chi-square, Cohen's d, bootstrap, power | AOV 506 vs 569 (+12,4%) tidak signifikan (p = 0,112; d = 0,03). Pembelian ulang 44,6% vs 43,5% (p = 0,412). Tingkat retur turun 26,0% -> 22,2% (p = 0,002, signifikan). |

## Catatan pembacaan

- Angka SQL dan notebook bisa berbeda tipis pada segmen RFM karena cara
  memecah nilai kembar (`NTILE` vs `rank(method="first")`); aturan segmennya
  sama. Lihat `docs/metodologi.md`.
- Desember 2011 hanya berisi 9 hari data; semua perbandingan tahunan memakai
  periode yang disamakan (1 Jan - 9 Des) atau menandai bulan tersebut sebagai
  parsial.
