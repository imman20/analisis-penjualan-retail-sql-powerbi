-- =============================================================================
-- 07. Nilai pesanan rata-rata per wilayah pasar (CTE)
-- -----------------------------------------------------------------------------
-- Pertanyaan bisnis : Apakah pelanggan luar negeri berbelanja dalam nilai pesanan
--                     yang lebih besar daripada pelanggan domestik?
-- Logika            : CTE pertama menggulung baris invoice menjadi satu baris per
--                     invoice (grain pesanan), CTE kedua menggabungkannya dengan
--                     dim_store. Median tidak tersedia di SQLite, sehingga
--                     dipakai rata-rata dan rata-rata terpangkas via percentil
--                     sederhana (invoice di bawah persentil 99) agar tidak
--                     didominasi pesanan grosir ekstrem.
-- Insight hasil     : AOV naik seiring jarak: UK GBP 464 (36.184 invoice), Eropa
--                     GBP 821 (3.099 invoice), luar Eropa GBP 1.281 (233 invoice).
--                     Setelah dipangkas pada persentil 99 polanya tetap sama
--                     (GBP 390 / 688 / 1.031), jadi bukan efek pencilan: pelanggan
--                     jauh menggabungkan pesanan menjadi lebih besar untuk menekan
--                     ongkos kirim (rata-rata 588-810 unit per pesanan vs 254 di UK).
-- =============================================================================
WITH invoice_totals AS (
    SELECT
        f.invoice_no,
        f.store_key,
        SUM(f.line_total)   AS invoice_value,
        SUM(f.quantity)     AS invoice_units,
        COUNT(*)            AS invoice_lines
    FROM fact_sales AS f
    WHERE f.is_return = 0
    GROUP BY f.invoice_no, f.store_key
),
ranked AS (
    SELECT
        it.*,
        PERCENT_RANK() OVER (PARTITION BY it.store_key ORDER BY it.invoice_value) AS pct_rank
    FROM invoice_totals AS it
)
SELECT
    s.store_name,
    s.region,
    COUNT(*)                                                           AS invoices,
    ROUND(SUM(r.invoice_value), 2)                                     AS revenue,
    ROUND(AVG(r.invoice_value), 2)                                     AS avg_order_value,
    ROUND(AVG(CASE WHEN r.pct_rank <= 0.99 THEN r.invoice_value END), 2) AS trimmed_aov_p99,
    ROUND(AVG(r.invoice_units), 1)                                     AS avg_units_per_order,
    ROUND(AVG(r.invoice_lines), 1)                                     AS avg_lines_per_order
FROM ranked AS r
JOIN dim_store AS s ON s.store_key = r.store_key
GROUP BY s.store_name, s.region
ORDER BY avg_order_value DESC;
