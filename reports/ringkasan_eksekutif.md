# Ringkasan Eksekutif: Analisis Penjualan Retail Online 2009-2011

**Sumber**: Online Retail II (UCI), 1 Des 2009 - 9 Des 2011, peritel online
berbasis Inggris dengan pelanggan mayoritas pembeli grosir. Semua angka berasal
dari pipeline di repositori ini (`make all`); mata uang GBP.

## Gambaran kinerja

| KPI | Nilai |
|---|---|
| Pendapatan kotor | 19,64 juta |
| Nilai retur | 0,72 juta (3,6% dari penjualan) |
| **Pendapatan bersih** | **18,93 juta** |
| Invoice penjualan | 39.516 |
| Pelanggan terdaftar | 5.875 (plus pelanggan tamu = 13,1% pendapatan) |
| Nilai pesanan rata-rata (AOV) | 497 (median 301) |
| Pertumbuhan YTD November 2011 vs 2010 | +3,0% (8,86 juta vs 8,60 juta) |

## Lima insight utama

1. **Bisnis ini hidup dari musim Natal.** November adalah puncak di kedua tahun
   (1,43 juta pada 2010; 1,45 juta pada 2011), hampir tiga kali bulan terendah
   (Feb 2011, 0,51 juta). Tiga bulan Sep-Nov menyumbang 36-38% pendapatan
   tahunan. Kesalahan perencanaan stok di kuartal ini berdampak jauh lebih
   besar daripada di bulan lain.

2. **Seperlima pelanggan menghasilkan dua pertiga pendapatan.** Segmen RFM
   "Champions" (1.304 pelanggan, 22,3%) menyumbang 68,6% pendapatan pelanggan
   terdaftar dengan rata-rata 16,8 pesanan per pelanggan. Sebaliknya, 31%
   pelanggan (Hibernating dan Lost) sudah tidak membeli selama 13-19 bulan dan
   hanya mewakili 4,7% pendapatan.

3. **Katalog terlalu gemuk.** 1.029 produk (21,9% katalog) menghasilkan 80%
   pendapatan, sementara 2.417 produk (51,4%) hanya menyumbang 5%. Tidak ada
   satu produk pun yang melebihi 1,7% pendapatan, sehingga risiko konsentrasi
   produk rendah tetapi biaya pengelolaan ekor panjang tinggi.

4. **Pelanggan ekspor memesan tiga kali lebih besar.** UK menyumbang 85,5%
   pendapatan, tetapi AOV luar Eropa 1.281 dan Eropa 821 vs UK 464 (pola tetap
   setelah pencilan dipangkas). Belanda (AOV 2.545) dan Australia (1.936) adalah
   pasar distributor besar yang belum tergarap luas (masing-masing hanya 22 dan
   14 pelanggan).

5. **Retur terkonsentrasi di satu kategori.** Tingkat retur keseluruhan 3,6%,
   tetapi Kitchen & Dining mencapai 4,6% nilai dan 7,1% unit dengan 3.401
   invoice retur - kemungkinan kerusakan barang pecah belah saat pengiriman.
   Pada perbandingan musim puncak, proporsi pelanggan yang melakukan retur
   turun signifikan dari 26,0% (2010) menjadi 22,2% (2011), p = 0,002.

## Hasil uji perbandingan musim puncak (kerangka A/B)

Q4 2010 (A) vs Q4 2011 (B), periode 1 Okt - 9 Des:

| Metrik | A | B | p-value | Kesimpulan |
|---|---|---|---|---|
| Rata-rata nilai keranjang | 506 | 569 | 0,112 (Welch) | Tidak signifikan; Cohen's d 0,03; median hampir sama (301 vs 303) |
| Tingkat pembelian ulang | 44,6% | 43,5% | 0,412 (chi-square) | Tidak berubah |
| Tingkat retur pelanggan | 26,0% | 22,2% | 0,002 (chi-square) | Turun signifikan |

Klaim "keranjang naik 12%" tidak didukung data; kenaikan rata-rata berasal dari
segelintir pesanan grosir ekstrem. Dataset tidak memuat eksperimen terkontrol,
sehingga ini adalah kuasi-eksperimen dengan keterbatasan yang dijelaskan di
`docs/metodologi.md`.

## Rekomendasi

1. **Rencanakan kuartal puncak dari Juli.** Gunakan tren MoM (lonjakan +29-42%
   di September) untuk menyiapkan stok kategori yang tumbuh: Christmas &
   Seasonal (+18%), Stationery & Gift Wrap (+15%), Bags & Accessories (+14%).
2. **Jalankan program retensi berjenjang.** Account manager untuk Champions;
   kontak langsung untuk 68 pelanggan At Risk (rata-rata belanja 3.939);
   email otomatis berbiaya rendah untuk Hibernating; hentikan pemasaran
   berbayar untuk segmen Lost.
3. **Rasionalisasi katalog.** Tinjau 2.417 produk kelas C untuk dihentikan
   atau digabung; alihkan ruang gudang dan modal kerja ke produk kelas A.
4. **Kembangkan pasar distributor di Belanda, Australia, dan Jerman** dengan
   insentif pesanan besar; AOV-nya sudah 2-5 kali UK.
5. **Audit kemasan dan kurir untuk Kitchen & Dining** dan ukur dampaknya dengan
   eksperimen terkontrol: acak pesanan ke kemasan lama vs baru, metrik utama
   tingkat retur, ukuran sampel ditentukan di awal (prosedur uji sudah tersedia
   di notebook 03).
6. **Perbaiki pencatatan pelanggan.** 2.922 invoice tamu (2,57 juta pendapatan)
   tidak bisa dianalisis per pelanggan; mewajibkan ID pelanggan di kasir akan
   meningkatkan kualitas segmentasi.
