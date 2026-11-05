-- =============================================================================
-- 05. Bauran kategori per tahun (GROUP BY + CASE pivot)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Kategori produk mana yang tumbuh dan mana yang menyusut
--                     antara 2010 dan 2011?
-- Logika            : Agregasi per kategori, lalu CASE WHEN memutar (pivot)
--                     pendapatan per tahun menjadi kolom. 2009 hanya berisi bulan
--                     Desember dan 2011 berakhir 9 Desember, sehingga perbandingan
--                     paling adil adalah 2010 vs 2011 pada periode Jan-9 Des.
--                     Growth dihitung pada periode yang disamakan tersebut.
-- Insight hasil     : Home Decor (25,2%) dan Kitchen & Dining (24,1%) menyumbang
--                     hampir separuh pendapatan. Pada periode yang disamakan
--                     (1 Jan - 9 Des), kategori yang tumbuh: Christmas & Seasonal
--                     +18,4%, Stationery & Gift Wrap +15,0%, Bags & Accessories
--                     +14,0%; yang menyusut: Candles & Lighting -13,9% dan
--                     Garden & Outdoor -12,1%.
-- =============================================================================
SELECT
    p.category,
    COUNT(DISTINCT p.product_key)                                            AS products,
    ROUND(SUM(CASE WHEN d.year = 2010 THEN f.line_total ELSE 0 END), 2)      AS revenue_2010,
    ROUND(SUM(CASE WHEN d.year = 2011 THEN f.line_total ELSE 0 END), 2)      AS revenue_2011,
    ROUND(SUM(CASE WHEN d.year = 2010 AND d.full_date <= '2010-12-09' THEN f.line_total ELSE 0 END), 2) AS revenue_2010_to_dec9,
    ROUND(100.0 * (SUM(CASE WHEN d.year = 2011 THEN f.line_total ELSE 0 END)
                   - SUM(CASE WHEN d.year = 2010 AND d.full_date <= '2010-12-09' THEN f.line_total ELSE 0 END))
          / SUM(CASE WHEN d.year = 2010 AND d.full_date <= '2010-12-09' THEN f.line_total ELSE 0 END), 2) AS growth_like_for_like_pct,
    ROUND(100.0 * SUM(f.line_total) / (SELECT SUM(line_total) FROM fact_sales WHERE is_return = 0), 2) AS share_of_total_pct
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_key = f.product_key
JOIN dim_date    AS d ON d.date_key = f.date_key
WHERE f.is_return = 0
GROUP BY p.category
ORDER BY share_of_total_pct DESC;
