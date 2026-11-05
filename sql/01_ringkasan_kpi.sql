-- =============================================================================
-- 01. Ringkasan KPI utama (agregasi dasar)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Berapa total pendapatan bersih, jumlah transaksi, jumlah
--                     pelanggan, dan nilai rata-rata pesanan (AOV) sepanjang
--                     periode data?
-- Logika            : Pendapatan kotor dihitung dari baris penjualan (is_return = 0),
--                     nilai retur dari baris is_return = 1 (line_total negatif),
--                     sehingga net = kotor + retur. AOV = pendapatan kotor /
--                     jumlah invoice penjualan.
-- Insight hasil     : Periode 1 Des 2009 - 9 Des 2011: pendapatan kotor GBP 19,64 jt,
--                     retur GBP 0,72 jt (3,6%), pendapatan bersih GBP 18,93 jt dari
--                     39.516 invoice, 5.875 pelanggan terdaftar, 4.721 produk, dan
--                     11,19 jt unit. AOV GBP 497,08 - tinggi karena pelanggan
--                     mayoritas pembeli grosir (wholesaler).
-- =============================================================================
SELECT
    MIN(d.full_date)                                                         AS first_date,
    MAX(d.full_date)                                                         AS last_date,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total END), 2)           AS gross_revenue,
    ROUND(SUM(CASE WHEN f.is_return = 1 THEN f.line_total END), 2)           AS returned_value,
    ROUND(SUM(f.line_total), 2)                                              AS net_revenue,
    COUNT(DISTINCT CASE WHEN f.is_return = 0 THEN f.invoice_no END)          AS sales_invoices,
    COUNT(DISTINCT CASE WHEN f.is_return = 1 THEN f.invoice_no END)          AS return_invoices,
    COUNT(DISTINCT CASE WHEN c.is_guest = 0 THEN f.customer_key END)         AS registered_customers,
    COUNT(DISTINCT f.product_key)                                            AS products_sold,
    SUM(CASE WHEN f.is_return = 0 THEN f.quantity END)                       AS units_sold,
    ROUND(SUM(CASE WHEN f.is_return = 0 THEN f.line_total END)
          / COUNT(DISTINCT CASE WHEN f.is_return = 0 THEN f.invoice_no END), 2) AS avg_order_value
FROM fact_sales AS f
JOIN dim_date     AS d ON d.date_key = f.date_key
JOIN dim_customer AS c ON c.customer_key = f.customer_key;
