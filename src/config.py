"""Konfigurasi path terpusat agar setiap skrip merujuk lokasi file yang sama.

Semua path dihitung relatif terhadap akar repositori sehingga skrip bisa
dijalankan dari direktori mana pun (misalnya dari ``notebooks/`` atau CI).
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SQL_DIR = ROOT_DIR / "sql"
REPORTS_DIR = ROOT_DIR / "reports"
SQL_OUTPUT_DIR = REPORTS_DIR / "sql_output"
ASSETS_DIR = ROOT_DIR / "assets"

# File data pada setiap tahap pipeline.
RAW_CSV = RAW_DIR / "online_retail_II.csv"
SAMPLE_CSV = RAW_DIR / "sample" / "online_retail_II_sample.csv"
CLEAN_PARQUET = PROCESSED_DIR / "retail_clean.parquet"
WAREHOUSE_DB = PROCESSED_DIR / "retail_dw.sqlite"
DASHBOARD_HTML = REPORTS_DIR / "dashboard.html"

SAMPLE_ROWS = 5_000
