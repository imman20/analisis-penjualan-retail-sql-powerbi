-- =============================================================================
-- 12. Analisis Pareto 80/20 produk (window SUM kumulatif)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Berapa persen produk yang menyumbang 80% pendapatan?
--                     Apakah katalog terlalu gemuk dengan produk yang hampir
--                     tidak laku?
-- Logika            : Produk diurutkan dari pendapatan tertinggi; SUM() OVER
--                     (ORDER BY revenue DESC) memberi pendapatan kumulatif; pangsa
--                     kumulatif dibandingkan ambang 80%. Query luar meringkas
--                     berapa produk masuk kelas A (<= 80%), B (80-95%), C (> 95%).
-- Insight hasil     : Prinsip Pareto berlaku: 1.029 produk (21,9% katalog)
--                     menghasilkan 80% pendapatan (GBP 15,71 jt). Sebaliknya,
--                     2.417 produk (51,4% katalog) hanya menyumbang 5% pendapatan
--                     (GBP 0,98 jt) - kandidat rasionalisasi stok.
-- =============================================================================
WITH product_revenue AS (
    SELECT
        p.product_key,
        p.stock_code,
        p.description,
        SUM(f.line_total) AS revenue
    FROM fact_sales AS f
    JOIN dim_product AS p ON p.product_key = f.product_key
    WHERE f.is_return = 0
    GROUP BY p.product_key, p.stock_code, p.description
),
cumulative AS (
    SELECT
        pr.*,
        ROW_NUMBER() OVER (ORDER BY pr.revenue DESC)                         AS product_rank,
        SUM(pr.revenue) OVER (ORDER BY pr.revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        SUM(pr.revenue) OVER ()                                              AS total_revenue,
        COUNT(*) OVER ()                                                     AS total_products
    FROM product_revenue AS pr
),
classified AS (
    SELECT
        c.*,
        1.0 * c.cumulative_revenue / c.total_revenue AS cumulative_share,
        CASE
            WHEN 1.0 * c.cumulative_revenue / c.total_revenue <= 0.80 THEN 'A (80% pendapatan)'
            WHEN 1.0 * c.cumulative_revenue / c.total_revenue <= 0.95 THEN 'B (80-95%)'
            ELSE 'C (5% terakhir)'
        END AS abc_class
    FROM cumulative AS c
)
SELECT
    abc_class,
    COUNT(*)                                                   AS products,
    ROUND(100.0 * COUNT(*) / MAX(total_products), 2)           AS products_share_pct,
    ROUND(SUM(revenue), 2)                                     AS revenue,
    ROUND(100.0 * SUM(revenue) / MAX(total_revenue), 2)        AS revenue_share_pct,
    MIN(product_rank)                                          AS first_rank,
    MAX(product_rank)                                          AS last_rank
FROM classified
GROUP BY abc_class
ORDER BY abc_class;
