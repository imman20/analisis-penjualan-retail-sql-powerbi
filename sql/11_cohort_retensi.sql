-- =============================================================================
-- 11. Analisis cohort retensi pelanggan
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Dari pelanggan yang pertama kali membeli di bulan tertentu,
--                     berapa persen yang kembali membeli 1, 2, 3, ... bulan
--                     kemudian?
-- Logika            : (1) CTE first_purchase menentukan bulan kohort tiap
--                     pelanggan terdaftar; (2) CTE activity mencatat bulan-bulan
--                     aktif; (3) selisih bulan dihitung dari komponen tahun dan
--                     bulan (SQLite tidak punya DATEDIFF); (4) retensi = pelanggan
--                     aktif pada bulan ke-n / ukuran kohort. Hanya kohort dengan
--                     setidaknya 12 bulan observasi yang ditampilkan untuk
--                     bulan 0-12 agar perbandingan antar kohort adil.
-- Insight hasil     : Rata-rata hanya 20,2% pelanggan baru kembali pada bulan
--                     berikutnya, lalu stabil di kisaran 15-22% hingga bulan ke-12
--                     (18,3%). Kohort Des 2009 jauh lebih loyal (33-50% aktif tiap
--                     bulan) karena berisi pelanggan lama yang "baru" dalam jendela
--                     data. Kohort yang masuk saat musim puncak (Okt-Des 2010)
--                     kembali lebih rendah (5-15%) - banyak pembeli musiman.
-- =============================================================================
WITH first_purchase AS (
    SELECT
        f.customer_key,
        MIN(d.year_month) AS cohort_month,
        MIN(d.year * 12 + d.month) AS cohort_index
    FROM fact_sales AS f
    JOIN dim_date     AS d ON d.date_key = f.date_key
    JOIN dim_customer AS c ON c.customer_key = f.customer_key
    WHERE f.is_return = 0 AND c.is_guest = 0
    GROUP BY f.customer_key
),
activity AS (
    SELECT DISTINCT
        f.customer_key,
        d.year * 12 + d.month AS activity_index
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.date_key
    WHERE f.is_return = 0
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers
    FROM first_purchase
    GROUP BY cohort_month
),
retention AS (
    SELECT
        fp.cohort_month,
        a.activity_index - fp.cohort_index AS month_number,
        COUNT(DISTINCT a.customer_key)     AS active_customers
    FROM first_purchase AS fp
    JOIN activity AS a ON a.customer_key = fp.customer_key
    GROUP BY fp.cohort_month, month_number
)
SELECT
    r.cohort_month,
    cs.customers                                            AS cohort_size,
    r.month_number,
    r.active_customers,
    ROUND(100.0 * r.active_customers / cs.customers, 1)     AS retention_pct
FROM retention AS r
JOIN cohort_size AS cs ON cs.cohort_month = r.cohort_month
WHERE r.month_number <= 12
  AND r.cohort_month <= '2010-12'
ORDER BY r.cohort_month, r.month_number;
