-- =============================================================================
-- 09. Pertumbuhan pendapatan bulan-ke-bulan dan tahun-ke-tahun (LAG)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Seberapa besar pendapatan naik/turun dibanding bulan
--                     sebelumnya (MoM) dan bulan yang sama tahun lalu (YoY)?
-- Logika            : CTE mengagregasi pendapatan bulanan; LAG(revenue, 1)
--                     mengambil bulan sebelumnya dan LAG(revenue, 12) bulan yang
--                     sama tahun lalu. Pertumbuhan = (sekarang - sebelumnya) /
--                     sebelumnya. Desember 2011 bersifat parsial (9 hari) sehingga
--                     nilainya ditandai agar tidak disalahtafsirkan.
-- Insight hasil     : Lonjakan MoM terbesar terjadi di September (+29,0% pada 2010,
--                     +42,0% pada 2011) dan November (+30,6% / +31,6%), lalu anjlok
--                     di Desember (-45,8% pada 2010). Secara YoY, 2011 tumbuh di
--                     8 dari 11 bulan penuh; terkuat Sep 2011 (+18,3%) dan Mei 2011
--                     (+15,0%); terlemah Apr 2011 (-20,3%; hanya 21 hari aktif vs 23 hari
--                     pada Apr 2010 karena rangkaian libur panjang di UK).
-- =============================================================================
WITH monthly AS (
    SELECT
        d.year_month,
        ROUND(SUM(f.line_total), 2)     AS revenue,
        COUNT(DISTINCT f.invoice_no)    AS invoices
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.date_key
    WHERE f.is_return = 0
    GROUP BY d.year_month
)
SELECT
    year_month,
    revenue,
    invoices,
    LAG(revenue, 1)  OVER (ORDER BY year_month) AS revenue_prev_month,
    ROUND(100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY year_month))
          / LAG(revenue, 1) OVER (ORDER BY year_month), 2)  AS mom_growth_pct,
    LAG(revenue, 12) OVER (ORDER BY year_month) AS revenue_same_month_last_year,
    ROUND(100.0 * (revenue - LAG(revenue, 12) OVER (ORDER BY year_month))
          / LAG(revenue, 12) OVER (ORDER BY year_month), 2) AS yoy_growth_pct,
    CASE WHEN year_month = '2011-12' THEN 1 ELSE 0 END AS partial_month
FROM monthly
ORDER BY year_month;
