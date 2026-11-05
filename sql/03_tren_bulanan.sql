-- =============================================================================
-- 03. Tren pendapatan bulanan (GROUP BY pada dimensi tanggal)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Bagaimana pola pendapatan dari bulan ke bulan, dan kapan
--                     puncak musiman terjadi?
-- Logika            : JOIN ke dim_date lalu agregasi per year_month. Bulan
--                     Desember 2011 hanya berisi 9 hari data sehingga perlu
--                     ditandai (partial_month) agar tidak disalahartikan sebagai
--                     penurunan.
-- Insight hasil     : Pola musiman sangat kuat dan berulang: November adalah puncak
--                     (2010: GBP 1,43 jt; 2011: GBP 1,45 jt), sekitar 2,7x bulan
--                     terendah (Feb 2011: GBP 0,51 jt). Kenaikan mulai terasa sejak
--                     September (pembelian stok Natal oleh pengecer). AOV tertinggi
--                     justru di Januari (GBP 584-620) saat jumlah invoice sedikit.
-- =============================================================================
SELECT
    d.year_month,
    d.year,
    d.month_name,
    COUNT(DISTINCT d.full_date)                    AS active_days,
    COUNT(DISTINCT f.invoice_no)                   AS invoices,
    COUNT(DISTINCT f.customer_key)                 AS customers,
    SUM(f.quantity)                                AS units,
    ROUND(SUM(f.line_total), 2)                    AS revenue,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.invoice_no), 2) AS avg_order_value,
    CASE WHEN d.year_month = '2011-12' THEN 1 ELSE 0 END AS partial_month
FROM fact_sales AS f
JOIN dim_date AS d ON d.date_key = f.date_key
WHERE f.is_return = 0
GROUP BY d.year_month, d.year, d.month_name
ORDER BY d.year_month;
