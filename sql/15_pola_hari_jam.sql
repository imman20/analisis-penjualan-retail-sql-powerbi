-- =============================================================================
-- 15. Pola transaksi menurut hari dan jam (fungsi tanggal + GROUP BY)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Kapan pelanggan paling banyak bertransaksi? Kapan waktu
--                     terbaik mengirim kampanye email atau menjadwalkan staf
--                     layanan pelanggan?
-- Logika            : Hari diambil dari dim_date, jam diambil dari komponen waktu
--                     invoice_datetime dengan strftime('%H'). Jumlah invoice
--                     dipakai sebagai ukuran utama karena menggambarkan kapan
--                     pesanan dibuat; pendapatan ditambahkan sebagai pelengkap.
-- Insight hasil     : Transaksi terkonsentrasi pada jam kerja: pukul 12.00 adalah
--                     jam tersibuk (6.369 invoice), diikuti 13.00 (5.638) dan 14.00
--                     (4.974); hampir tidak ada transaksi sebelum pukul 07.00 atau
--                     setelah 20.00. Kamis adalah hari tersibuk (8.168 invoice),
--                     Sabtu praktis kosong (30 invoice) - sistem pemesanan grosir
--                     tidak beroperasi di akhir pekan. Slot Rabu 12.00 adalah
--                     puncak absolut (1.212 invoice, 3,1% dari total).
-- =============================================================================
SELECT
    d.day_of_week,
    d.day_name,
    CAST(strftime('%H', f.invoice_datetime) AS INTEGER) AS hour_of_day,
    COUNT(DISTINCT f.invoice_no)                        AS invoices,
    ROUND(SUM(f.line_total), 2)                         AS revenue,
    ROUND(100.0 * COUNT(DISTINCT f.invoice_no)
          / (SELECT COUNT(DISTINCT invoice_no) FROM fact_sales WHERE is_return = 0), 2) AS invoice_share_pct
FROM fact_sales AS f
JOIN dim_date AS d ON d.date_key = f.date_key
WHERE f.is_return = 0
GROUP BY d.day_of_week, d.day_name, hour_of_day
ORDER BY d.day_of_week, hour_of_day;
