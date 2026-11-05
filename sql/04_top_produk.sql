-- =============================================================================
-- 04. Sepuluh produk dengan pendapatan tertinggi (JOIN + ORDER BY + LIMIT)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Produk apa yang paling menghasilkan uang, dan apakah
--                     produk terlaris berdasarkan unit sama dengan yang terlaris
--                     berdasarkan pendapatan?
-- Logika            : Agregasi per produk, JOIN dim_product untuk deskripsi dan
--                     kategori. Peringkat memakai pendapatan BERSIH (penjualan
--                     dikurangi retur) karena ada pesanan raksasa yang dibatalkan
--                     di hari yang sama (mis. 80.995 unit "PAPER CRAFT, LITTLE
--                     BIRDIE") yang akan menyesatkan bila hanya memakai penjualan
--                     kotor. Kolom units dan invoices membantu membedakan produk
--                     murah-volume tinggi dari produk mahal-volume rendah.
-- Insight hasil     : Produk #1 "REGENCY CAKESTAND 3 TIER" (GBP 314 rb bersih,
--                     3.918 invoice, harga rata-rata GBP 14,19) menang lewat harga,
--                     sedangkan #2 "WHITE HANGING HEART T-LIGHT HOLDER" (GBP 252 rb)
--                     dan #3 "JUMBO BAG RED RETROSPOT" (GBP 181 rb) menang lewat
--                     volume (95-97 ribu unit, harga GBP 2-3). Tidak ada produk yang
--                     menyumbang lebih dari 1,7% pendapatan - risiko konsentrasi
--                     produk rendah.
-- =============================================================================
SELECT
    p.stock_code,
    p.description,
    p.category,
    SUM(CASE WHEN f.is_return = 0 THEN f.quantity ELSE 0 END)                   AS units_sold,
    COUNT(DISTINCT CASE WHEN f.is_return = 0 THEN f.invoice_no END)             AS invoices,
    ROUND(AVG(CASE WHEN f.is_return = 0 THEN f.unit_price END), 2)              AS avg_unit_price,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total ELSE 0 END), 2)       AS gross_revenue,
    ROUND(SUM(f.line_total), 2)                                                 AS net_revenue,
    ROUND(100.0 * SUM(f.line_total)
          / (SELECT SUM(line_total) FROM fact_sales), 2)                        AS net_revenue_share_pct
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_key = f.product_key
GROUP BY p.stock_code, p.description, p.category
ORDER BY net_revenue DESC
LIMIT 10;
