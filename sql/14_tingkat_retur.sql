-- =============================================================================
-- 14. Tingkat retur per kategori produk (agregasi kondisional + JOIN)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Kategori mana yang paling banyak dikembalikan pelanggan,
--                     diukur sebagai persentase nilai penjualan?
-- Logika            : Penjualan dan retur berada di tabel fakta yang sama dengan
--                     flag is_return, sehingga cukup agregasi kondisional (CASE)
--                     tanpa JOIN tambahan. Return rate (nilai) = |nilai retur| /
--                     nilai penjualan; return rate (unit) = |unit retur| / unit
--                     terjual. HAVING memastikan kategori dengan basis kecil
--                     tidak masuk.
-- Insight hasil     : Tingkat retur keseluruhan 3,6% dari nilai penjualan.
--                     Stationery & Gift Wrap paling tinggi (11,8% nilai) tetapi
--                     sebagian besar berasal dari satu pesanan 80.995 unit "PAPER
--                     CRAFT, LITTLE BIRDIE" yang dibatalkan di hari yang sama;
--                     tanpa itu kategori ini ~1,8%. Kitchen & Dining (4,6% nilai,
--                     7,1% unit; 3.401 invoice retur) adalah masalah retur yang
--                     sesungguhnya - barang pecah belah rawan rusak saat kirim.
-- =============================================================================
SELECT
    p.category,
    COUNT(DISTINCT CASE WHEN f.is_return = 0 THEN f.invoice_no END)         AS sales_invoices,
    COUNT(DISTINCT CASE WHEN f.is_return = 1 THEN f.invoice_no END)         AS return_invoices,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2)   AS gross_revenue,
    ROUND(-SUM(CASE WHEN f.is_return = 1 THEN f.line_total ELSE 0 END), 2)  AS returned_value,
    ROUND(100.0 * -SUM(CASE WHEN f.is_return = 1 THEN f.line_total ELSE 0 END)
          / SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2) AS return_rate_value_pct,
    ROUND(100.0 * -SUM(CASE WHEN f.is_return = 1 THEN f.quantity ELSE 0 END)
          / SUM(CASE WHEN f.is_return = 0 THEN f.quantity ELSE 0 END), 2)   AS return_rate_units_pct
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_key = f.product_key
GROUP BY p.category
HAVING SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END) > 100000
ORDER BY return_rate_value_pct DESC;
