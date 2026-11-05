# Changelog

Semua perubahan penting pada proyek ini dicatat di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/)
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/lang/id/).

## [Unreleased]

## [1.0.0] - 2025-11-05

### Added

- Pipeline data: unduh dataset Online Retail II (UCI), pembersihan
  (duplikat, kode non-produk, harga tidak valid, pemisahan retur), dan
  pembangunan star schema SQLite (`fact_sales`, `dim_product`,
  `dim_customer`, `dim_date`, `dim_store`).
- Pemetaan kategori produk berbasis kata kunci (9 kategori).
- 15 query SQL analitik bernomor: KPI, JOIN/GROUP BY/HAVING, subquery, CTE,
  window function (RANK, LAG, running total), cohort retensi, Pareto 80/20,
  RFM, tingkat retur, dan pola hari/jam; beserta `src/run_sql.py`.
- Notebook: EDA, segmentasi RFM + KMeans (pemilihan k via silhouette), dan
  uji A/B kuasi-eksperimental (uji t Welch, chi-square, interval kepercayaan,
  Cohen's d).
- Dashboard Streamlit interaktif dan dashboard HTML statis (Plotly) dengan
  screenshot otomatis via Playwright.
- Dokumentasi: kamus data, skema star (Mermaid), pertanyaan bisnis, metodologi,
  panduan Power BI/Tableau, ringkasan eksekutif.
- Unit test (pytest) untuk pembersihan, kategori, warehouse, RFM, uji A/B,
  dan validitas seluruh query SQL; workflow CI GitHub Actions.
