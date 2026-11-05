-- =============================================================================
-- 10. Akumulasi pendapatan berjalan per tahun (running total)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Bagaimana laju akumulasi pendapatan 2011 dibanding 2010
--                     di bulan yang sama (year-to-date)?
-- Logika            : SUM() OVER (PARTITION BY year ORDER BY month ROWS BETWEEN
--                     UNBOUNDED PRECEDING AND CURRENT ROW) menghasilkan total
--                     kumulatif yang di-reset tiap tahun. Rata-rata bergerak 3
--                     bulan ditambahkan untuk menghaluskan fluktuasi.
-- Insight hasil     : Hingga akhir November, YTD 2011 (GBP 8,86 jt) unggul tipis
--                     3,0% atas YTD 2010 (GBP 8,60 jt). Tiga bulan Sep-Nov
--                     menyumbang 36,2% (2010) dan 37,8% (2011) pendapatan tahunan; rata-rata bergerak
--                     3 bulan naik dari ~GBP 0,65 jt (paruh pertama) ke ~GBP 1,19 jt
--                     (November 2011).
-- =============================================================================
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        d.year_month,
        ROUND(SUM(f.line_total), 2) AS revenue
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.date_key
    WHERE f.is_return = 0
    GROUP BY d.year, d.month, d.year_month
)
SELECT
    year,
    month,
    year_month,
    revenue,
    ROUND(SUM(revenue) OVER (PARTITION BY year ORDER BY month
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS ytd_revenue,
    ROUND(AVG(revenue) OVER (ORDER BY year_month
                             ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)         AS moving_avg_3m,
    ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY year), 2)              AS share_of_year_pct
FROM monthly
ORDER BY year, month;
