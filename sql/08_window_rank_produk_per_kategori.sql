-- =============================================================================
-- 08. Tiga produk teratas di setiap kategori (window function RANK)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Produk apa yang menjadi andalan di masing-masing kategori?
-- Logika            : CTE menghitung pendapatan per produk, lalu RANK() OVER
--                     (PARTITION BY category ORDER BY revenue DESC) memberi
--                     peringkat di dalam kategori tanpa perlu self-join. Filter
--                     rank <= 3 dilakukan di query luar karena window function
--                     tidak boleh dipakai langsung di WHERE.
-- Insight hasil     : Ketergantungan pada produk juara berbeda tajam antar
--                     kategori: di Candles & Lighting satu produk (WHITE HANGING
--                     HEART T-LIGHT HOLDER) menyumbang 17,2% pendapatan kategori,
--                     di Garden & Outdoor 13,9% (ASSORTED COLOUR BIRD ORNAMENT),
--                     sedangkan di Home Decor produk #1 hanya 3,0% - portofolio
--                     Home Decor paling terdiversifikasi.
-- =============================================================================
WITH product_revenue AS (
    SELECT
        p.category,
        p.stock_code,
        p.description,
        SUM(f.quantity)             AS units,
        ROUND(SUM(f.line_total), 2) AS revenue
    FROM fact_sales AS f
    JOIN dim_product AS p ON p.product_key = f.product_key
    WHERE f.is_return = 0
    GROUP BY p.category, p.stock_code, p.description
),
ranked AS (
    SELECT
        pr.*,
        RANK() OVER (PARTITION BY pr.category ORDER BY pr.revenue DESC) AS rank_in_category,
        ROUND(100.0 * pr.revenue / SUM(pr.revenue) OVER (PARTITION BY pr.category), 2) AS share_in_category_pct
    FROM product_revenue AS pr
)
SELECT category, rank_in_category, stock_code, description, units, revenue, share_in_category_pct
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;
