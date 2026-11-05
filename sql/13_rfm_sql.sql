-- =============================================================================
-- 13. Segmentasi RFM langsung di SQL (NTILE + CASE)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Bagaimana komposisi basis pelanggan menurut segmen RFM,
--                     dan segmen mana yang menyumbang pendapatan terbesar?
-- Logika            : (1) Agregasi per pelanggan: recency (hari sejak belanja
--                     terakhir hingga 1 hari setelah tanggal data terakhir),
--                     frequency (jumlah invoice), monetary (total belanja).
--                     (2) NTILE(5) memberi skor kuantil 1-5; recency diurutkan
--                     menurun supaya yang baru belanja mendapat skor 5.
--                     (3) CASE memetakan kombinasi skor ke segmen bernama,
--                     mengikuti aturan yang sama dengan src/analysis/rfm.py.
-- Insight hasil     : Champions (1.355 pelanggan, 23,2%) menyumbang 70,3% pendapatan
--                     pelanggan terdaftar (GBP 11,99 jt) dengan rata-rata 16,4
--                     invoice dan belanja GBP 8.849. Loyal Customers menambah 12,4%.
--                     Segmen bermasalah: Hibernating (1.176; 20,1%) dan Lost (600;
--                     10,3%) yang tidak belanja selama 400-567 hari; At Risk hanya
--                     86 pelanggan tetapi bernilai tinggi (rata-rata GBP 3.623).
-- =============================================================================
WITH snapshot AS (
    SELECT DATE(MAX(invoice_datetime), '+1 day') AS snapshot_date FROM fact_sales
),
customer_rfm AS (
    SELECT
        c.customer_id,
        c.country,
        CAST(JULIANDAY((SELECT snapshot_date FROM snapshot)) - JULIANDAY(DATE(MAX(f.invoice_datetime))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT f.invoice_no) AS frequency,
        ROUND(SUM(f.line_total), 2)  AS monetary
    FROM fact_sales AS f
    JOIN dim_customer AS c ON c.customer_key = f.customer_key
    WHERE f.is_return = 0 AND c.is_guest = 0
    GROUP BY c.customer_id, c.country
),
scored AS (
    SELECT
        cr.*,
        NTILE(5) OVER (ORDER BY cr.recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY cr.frequency ASC, cr.monetary ASC)  AS f_score,
        NTILE(5) OVER (ORDER BY cr.monetary ASC)   AS m_score
    FROM customer_rfm AS cr
),
segmented AS (
    SELECT
        s.*,
        (s.f_score + s.m_score) / 2.0 AS value_score,
        CASE
            WHEN s.r_score >= 4 AND (s.f_score + s.m_score) / 2.0 >= 4   THEN 'Champions'
            WHEN s.r_score >= 3 AND (s.f_score + s.m_score) / 2.0 >= 3.5 THEN 'Loyal Customers'
            WHEN s.r_score >= 4 AND (s.f_score + s.m_score) / 2.0 < 2    THEN 'New Customers'
            WHEN s.r_score >= 3 AND (s.f_score + s.m_score) / 2.0 < 3.5  THEN 'Potential Loyalists'
            WHEN s.r_score = 2  AND (s.f_score + s.m_score) / 2.0 >= 3   THEN 'Need Attention'
            WHEN s.r_score <= 2 AND (s.f_score + s.m_score) / 2.0 >= 4   THEN 'At Risk'
            WHEN s.r_score = 1  AND (s.f_score + s.m_score) / 2.0 < 2    THEN 'Lost'
            ELSE 'Hibernating'
        END AS segment
    FROM scored AS s
)
SELECT
    segment,
    COUNT(*)                                                     AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)           AS customers_share_pct,
    ROUND(AVG(recency_days), 0)                                  AS avg_recency_days,
    ROUND(AVG(frequency), 1)                                     AS avg_frequency,
    ROUND(AVG(monetary), 2)                                      AS avg_monetary,
    ROUND(SUM(monetary), 2)                                      AS total_monetary,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS revenue_share_pct
FROM segmented
GROUP BY segment
ORDER BY total_monetary DESC;
