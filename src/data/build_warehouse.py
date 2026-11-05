"""Membangun data warehouse SQLite berskema bintang (star schema).

Tabel yang dihasilkan di ``data/processed/retail_dw.sqlite``:

* ``fact_sales``   : satu baris per baris invoice (grain = item per invoice),
                     termasuk retur dengan ``is_return = 1`` dan kuantitas negatif.
* ``dim_product``  : kode stok, deskripsi, dan kategori hasil pemetaan kata kunci.
* ``dim_customer`` : pelanggan terdaftar (satu baris per ID) dan pelanggan tamu
                     (satu baris per negara) beserta tanggal pembelian pertama.
* ``dim_date``     : kalender harian lengkap untuk rentang data.
* ``dim_store``    : kanal/pasar penjualan. Dataset asli berasal dari satu toko
                     online di Inggris, sehingga dimensi ini memodelkan wilayah
                     pasar (UK, Eropa, luar Eropa) agar skema siap diperluas ke
                     multi-toko tanpa mengubah tabel fakta.

Mengapa star schema? Tabel fakta yang ramping (hanya kunci dan ukuran) membuat
agregasi cepat, sementara dimensi menyimpan atribut deskriptif yang gampang
difilter oleh alat BI seperti Power BI atau Tableau.
"""

from __future__ import annotations

import sqlite3
import sys

import pandas as pd

from src.config import CLEAN_PARQUET, WAREHOUSE_DB
from src.data.categorize import categorize_series
from src.data.clean import RETURNS_PARQUET

EUROPE_COUNTRIES = {
    "EIRE",
    "Germany",
    "France",
    "Netherlands",
    "Spain",
    "Switzerland",
    "Belgium",
    "Portugal",
    "Channel Islands",
    "Italy",
    "Norway",
    "Sweden",
    "Cyprus",
    "Austria",
    "Denmark",
    "Finland",
    "Greece",
    "Poland",
    "Lithuania",
    "Malta",
    "Iceland",
    "Czech Republic",
    "European Community",
}

STORES = pd.DataFrame(
    [
        {"store_key": 1, "store_code": "ONL-UK", "store_name": "Online Store - UK", "channel": "Online", "region": "United Kingdom"},
        {"store_key": 2, "store_code": "ONL-EU", "store_name": "Online Store - Europe", "channel": "Online", "region": "Europe"},
        {"store_key": 3, "store_code": "ONL-ROW", "store_name": "Online Store - Rest of World", "channel": "Online", "region": "Rest of World"},
    ]
)


def country_to_region(country: str) -> str:
    """Memetakan negara ke wilayah pasar yang dipakai ``dim_store``."""
    if country == "United Kingdom":
        return "United Kingdom"
    if country in EUROPE_COUNTRIES:
        return "Europe"
    return "Rest of World"


def build_dim_date(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Membuat kalender harian; ``date_key`` berformat YYYYMMDD agar mudah di-JOIN."""
    dates = pd.date_range(start.normalize(), end.normalize(), freq="D")
    dim = pd.DataFrame({"full_date": dates})
    dim["date_key"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["full_date"].dt.year
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["full_date"].dt.strftime("%b")
    dim["year_month"] = dim["full_date"].dt.strftime("%Y-%m")
    dim["week_of_year"] = dim["full_date"].dt.isocalendar().week.astype(int)
    dim["day"] = dim["full_date"].dt.day
    dim["day_of_week"] = dim["full_date"].dt.dayofweek + 1  # 1 = Senin ... 7 = Minggu
    dim["day_name"] = dim["full_date"].dt.strftime("%a")
    dim["is_weekend"] = (dim["day_of_week"] >= 6).astype(int)
    dim["full_date"] = dim["full_date"].dt.strftime("%Y-%m-%d")
    cols = ["date_key", "full_date", "year", "quarter", "month", "month_name", "year_month", "week_of_year", "day", "day_of_week", "day_name", "is_weekend"]
    return dim[cols]


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per kode stok; deskripsi diambil dari varian yang paling sering muncul."""
    desc = (
        df.groupby(["stock_code", "description"], observed=True)
        .size()
        .reset_index(name="n")
        .sort_values(["stock_code", "n"], ascending=[True, False])
        .drop_duplicates("stock_code")
        .drop(columns="n")
        .reset_index(drop=True)
    )
    desc["category"] = categorize_series(desc["description"])
    desc.insert(0, "product_key", range(1, len(desc) + 1))
    return desc[["product_key", "stock_code", "description", "category"]]


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Pelanggan terdaftar (per ID) dan pelanggan tamu (per negara).

    Sejumlah kecil pelanggan tercatat di lebih dari satu negara; kita memakai
    negara yang paling sering muncul agar setiap pelanggan punya satu negara.
    """
    registered = df[~df["is_guest"]]
    country_mode = (
        registered.groupby(["customer_id", "country"], observed=True)
        .size()
        .reset_index(name="n")
        .sort_values(["customer_id", "n"], ascending=[True, False])
        .drop_duplicates("customer_id")
        .drop(columns="n")
    )
    first_purchase = registered[~registered["is_return"]].groupby("customer_id")["invoice_date"].min().dt.strftime("%Y-%m-%d")
    country_mode["first_purchase_date"] = country_mode["customer_id"].map(first_purchase)
    country_mode["is_guest"] = 0

    guest_countries = df.loc[df["is_guest"], "country"].dropna().unique()
    guests = pd.DataFrame({"customer_id": pd.array([pd.NA] * len(guest_countries), dtype="Int64"), "country": sorted(guest_countries)})
    guests["first_purchase_date"] = None
    guests["is_guest"] = 1

    dim = pd.concat([country_mode, guests], ignore_index=True)
    dim["region"] = dim["country"].map(country_to_region)
    dim.insert(0, "customer_key", range(1, len(dim) + 1))
    return dim[["customer_key", "customer_id", "country", "region", "is_guest", "first_purchase_date"]]


def build_fact_sales(df: pd.DataFrame, dim_product: pd.DataFrame, dim_customer: pd.DataFrame) -> pd.DataFrame:
    """Menukar atribut deskriptif dengan surrogate key dari tiap dimensi."""
    fact = df.copy()
    fact["date_key"] = fact["invoice_date"].dt.strftime("%Y%m%d").astype(int)
    fact = fact.merge(dim_product[["product_key", "stock_code"]], on="stock_code", how="left")

    # Pelanggan terdaftar dicocokkan lewat ID, tamu lewat negara.
    reg_map = dim_customer.loc[dim_customer["is_guest"] == 0, ["customer_key", "customer_id"]]
    guest_map = dim_customer.loc[dim_customer["is_guest"] == 1, ["customer_key", "country"]].rename(columns={"customer_key": "guest_key"})
    fact = fact.merge(reg_map, on="customer_id", how="left").merge(guest_map, on="country", how="left")
    fact["customer_key"] = fact["customer_key"].fillna(fact["guest_key"]).astype(int)

    fact["store_key"] = fact["country"].map(country_to_region).map(STORES.set_index("region")["store_key"]).astype(int)
    fact["is_return"] = fact["is_return"].astype(int)
    fact["invoice_datetime"] = fact["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    fact = fact.sort_values(["invoice_datetime", "invoice_no"]).reset_index(drop=True)
    fact.insert(0, "sales_key", range(1, len(fact) + 1))
    cols = ["sales_key", "invoice_no", "invoice_datetime", "date_key", "product_key", "customer_key", "store_key", "quantity", "unit_price", "line_total", "is_return"]
    return fact[cols]


SCHEMA_SQL = """
CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,
    full_date     TEXT NOT NULL,
    year          INTEGER NOT NULL,
    quarter       INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    month_name    TEXT NOT NULL,
    year_month    TEXT NOT NULL,
    week_of_year  INTEGER NOT NULL,
    day           INTEGER NOT NULL,
    day_of_week   INTEGER NOT NULL,
    day_name      TEXT NOT NULL,
    is_weekend    INTEGER NOT NULL
);
CREATE TABLE dim_product (
    product_key   INTEGER PRIMARY KEY,
    stock_code    TEXT NOT NULL UNIQUE,
    description   TEXT,
    category      TEXT NOT NULL
);
CREATE TABLE dim_customer (
    customer_key        INTEGER PRIMARY KEY,
    customer_id         INTEGER,
    country             TEXT NOT NULL,
    region              TEXT NOT NULL,
    is_guest            INTEGER NOT NULL,
    first_purchase_date TEXT
);
CREATE TABLE dim_store (
    store_key   INTEGER PRIMARY KEY,
    store_code  TEXT NOT NULL UNIQUE,
    store_name  TEXT NOT NULL,
    channel     TEXT NOT NULL,
    region      TEXT NOT NULL
);
CREATE TABLE fact_sales (
    sales_key         INTEGER PRIMARY KEY,
    invoice_no        TEXT NOT NULL,
    invoice_datetime  TEXT NOT NULL,
    date_key          INTEGER NOT NULL REFERENCES dim_date(date_key),
    product_key       INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_key      INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    store_key         INTEGER NOT NULL REFERENCES dim_store(store_key),
    quantity          INTEGER NOT NULL,
    unit_price        REAL NOT NULL,
    line_total        REAL NOT NULL,
    is_return         INTEGER NOT NULL
);
CREATE INDEX idx_fact_date ON fact_sales(date_key);
CREATE INDEX idx_fact_product ON fact_sales(product_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_store ON fact_sales(store_key);
CREATE INDEX idx_fact_invoice ON fact_sales(invoice_no);
"""


def write_warehouse(tables: dict[str, pd.DataFrame], db_path=WAREHOUSE_DB) -> None:
    """Menulis ulang file SQLite dari nol agar hasil selalu deterministik."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        for name, table in tables.items():
            table.to_sql(name, conn, if_exists="append", index=False)
        conn.execute("ANALYZE")


def build_all(sales: pd.DataFrame, returns: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Merakit semua tabel dimensi dan fakta dari data bersih."""
    df = pd.concat([sales, returns], ignore_index=True)
    dim_date = build_dim_date(df["invoice_date"].min(), df["invoice_date"].max() + pd.offsets.MonthEnd(0))
    dim_product = build_dim_product(df)
    dim_customer = build_dim_customer(df)
    fact = build_fact_sales(df, dim_product, dim_customer)
    return {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_customer": dim_customer,
        "dim_store": STORES,
        "fact_sales": fact,
    }


def main() -> int:
    sales = pd.read_parquet(CLEAN_PARQUET)
    returns = pd.read_parquet(RETURNS_PARQUET)
    tables = build_all(sales, returns)
    write_warehouse(tables)
    for name, table in tables.items():
        print(f"[warehouse] {name}: {len(table):,} baris")
    print(f"[warehouse] tersimpan: {WAREHOUSE_DB} ({WAREHOUSE_DB.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
