-- =============================================================================
-- 06. Pelanggan bernilai tinggi (subquery)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Siapa pelanggan terdaftar yang total belanjanya di atas
--                     rata-rata, dan berapa banyak jumlahnya?
-- Logika            : Subquery dalam FROM menghitung total belanja per pelanggan;
--                     subquery skalar di WHERE menghitung rata-rata belanja semua
--                     pelanggan terdaftar. Pelanggan tamu dikecualikan karena
--                     tidak bisa diidentifikasi.
-- Insight hasil     : Rata-rata belanja per pelanggan terdaftar GBP 2.917. Hanya
--                     1.162 dari 5.852 pelanggan (19,9%) yang berada di atas
--                     rata-rata, namun mereka menyumbang GBP 13,15 jt (77% dari
--                     pendapatan pelanggan terdaftar). Pelanggan #1 (ID 18102, UK)
--                     berbelanja GBP 581 rb = 199x rata-rata.
-- =============================================================================
SELECT
    t.customer_id,
    t.country,
    t.invoices,
    t.total_spend,
    ROUND(t.total_spend / t.invoices, 2) AS avg_order_value,
    ROUND(t.total_spend / (SELECT AVG(s.total_spend)
                           FROM (SELECT customer_key, SUM(line_total) AS total_spend
                                 FROM fact_sales WHERE is_return = 0 GROUP BY customer_key) AS s
                           JOIN dim_customer AS cc ON cc.customer_key = s.customer_key
                           WHERE cc.is_guest = 0), 2) AS times_average
FROM (
    SELECT
        c.customer_id,
        c.country,
        COUNT(DISTINCT f.invoice_no)  AS invoices,
        ROUND(SUM(f.line_total), 2)   AS total_spend
    FROM fact_sales AS f
    JOIN dim_customer AS c ON c.customer_key = f.customer_key
    WHERE f.is_return = 0 AND c.is_guest = 0
    GROUP BY c.customer_id, c.country
) AS t
WHERE t.total_spend > (
    SELECT AVG(s.total_spend)
    FROM (SELECT customer_key, SUM(line_total) AS total_spend
          FROM fact_sales WHERE is_return = 0 GROUP BY customer_key) AS s
    JOIN dim_customer AS cc ON cc.customer_key = s.customer_key
    WHERE cc.is_guest = 0
)
ORDER BY t.total_spend DESC;
