-- =============================================================================
-- 02. Pendapatan per negara (JOIN + GROUP BY + HAVING)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Negara mana yang menyumbang pendapatan terbesar, dan
--                     seberapa dominan pasar domestik (UK)?
-- Logika            : JOIN fakta ke dim_customer untuk mendapatkan negara,
--                     agregasi per negara, lalu HAVING menyaring negara dengan
--                     minimal 20 invoice agar pasar yang terlalu kecil tidak
--                     mengganggu peringkat. Pangsa dihitung lewat subquery total.
-- Insight hasil     : UK mendominasi dengan 85,5% pendapatan (GBP 16,80 jt, 36.184
--                     invoice). Pasar ekspor terbesar: EIRE (3,2%), Belanda (2,8%),
--                     Jerman (2,0%), Prancis (1,6%). AOV luar negeri jauh lebih
--                     tinggi: Belanda GBP 2.545 dan Australia GBP 1.936 vs UK
--                     GBP 464 - pelanggan ekspor cenderung distributor besar.
-- =============================================================================
SELECT
    c.country,
    c.region,
    COUNT(DISTINCT f.invoice_no)                              AS invoices,
    COUNT(DISTINCT CASE WHEN c.is_guest = 0 THEN c.customer_key END) AS customers,
    ROUND(SUM(f.line_total), 2)                               AS revenue,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.invoice_no), 2) AS avg_order_value,
    ROUND(100.0 * SUM(f.line_total)
          / (SELECT SUM(line_total) FROM fact_sales WHERE is_return = 0), 2) AS revenue_share_pct
FROM fact_sales AS f
JOIN dim_customer AS c ON c.customer_key = f.customer_key
WHERE f.is_return = 0
GROUP BY c.country, c.region
HAVING COUNT(DISTINCT f.invoice_no) >= 20
ORDER BY revenue DESC;
