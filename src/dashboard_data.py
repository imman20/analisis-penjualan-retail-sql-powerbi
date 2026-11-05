"""Akses data dan agregasi yang dipakai bersama oleh dashboard Streamlit dan statis.

Semua fungsi menerima DataFrame "flat" (fakta yang sudah di-JOIN dengan dimensi)
sehingga logika filter dan agregasi hanya ditulis sekali dan hasil kedua
dashboard dijamin konsisten.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.analysis.rfm import compute_rfm, score_rfm
from src.config import WAREHOUSE_DB

FLAT_QUERY = """
SELECT
    f.invoice_no,
    f.invoice_datetime,
    d.full_date,
    d.year_month,
    d.year,
    d.day_of_week,
    d.day_name,
    c.customer_id,
    c.country,
    c.region,
    c.is_guest,
    p.stock_code,
    p.description,
    p.category,
    f.quantity,
    f.unit_price,
    f.line_total,
    f.is_return
FROM fact_sales AS f
JOIN dim_date     AS d ON d.date_key = f.date_key
JOIN dim_customer AS c ON c.customer_key = f.customer_key
JOIN dim_product  AS p ON p.product_key = f.product_key
"""

# Nama negara di dataset yang perlu diselaraskan dengan nama standar untuk peta.
COUNTRY_ALIASES = {
    "EIRE": "Ireland",
    "RSA": "South Africa",
    "USA": "United States",
    "Korea": "South Korea",
    "Czech Republic": "Czechia",
}


def load_flat(db_path: Path = WAREHOUSE_DB) -> pd.DataFrame:
    """Memuat seluruh tabel fakta beserta atribut dimensi yang dibutuhkan dashboard."""
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(FLAT_QUERY, conn, parse_dates=["invoice_datetime", "full_date"])
    df["is_return"] = df["is_return"].astype(bool)
    df["is_guest"] = df["is_guest"].astype(bool)
    df["customer_id"] = df["customer_id"].astype("Int64")
    return df


def apply_filters(df: pd.DataFrame, start=None, end=None, countries: list[str] | None = None, categories: list[str] | None = None) -> pd.DataFrame:
    """Menerapkan filter periode, negara, dan kategori; None berarti tanpa filter."""
    mask = pd.Series(True, index=df.index)
    if start is not None:
        mask &= df["full_date"] >= pd.Timestamp(start)
    if end is not None:
        mask &= df["full_date"] <= pd.Timestamp(end)
    if countries:
        mask &= df["country"].isin(countries)
    if categories:
        mask &= df["category"].isin(categories)
    return df[mask]


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    """KPI ringkas: pendapatan bersih, invoice, pelanggan, AOV, tingkat retur."""
    sales = df[~df["is_return"]]
    returns = df[df["is_return"]]
    gross = float(sales["line_total"].sum())
    returned = float(-returns["line_total"].sum())
    invoices = int(sales["invoice_no"].nunique())
    return {
        "gross_revenue": gross,
        "returned_value": returned,
        "net_revenue": gross - returned,
        "invoices": invoices,
        "customers": int(sales["customer_id"].nunique()),
        "units": int(sales["quantity"].sum()),
        "aov": gross / invoices if invoices else 0.0,
        "return_rate": returned / gross if gross else 0.0,
    }


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    sales = df[~df["is_return"]]
    out = sales.groupby("year_month").agg(revenue=("line_total", "sum"), invoices=("invoice_no", "nunique"), customers=("customer_id", "nunique")).reset_index()
    out["aov"] = out["revenue"] / out["invoices"]
    out["partial_month"] = out["year_month"] == "2011-12"
    return out


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Peringkat produk memakai pendapatan bersih (penjualan - retur)."""
    out = df.groupby(["stock_code", "description", "category"]).agg(net_revenue=("line_total", "sum")).reset_index()
    units = df[~df["is_return"]].groupby("stock_code")["quantity"].sum().rename("units")
    out = out.merge(units, on="stock_code", how="left").fillna({"units": 0})
    return out.sort_values("net_revenue", ascending=False).head(n).reset_index(drop=True)


def category_share(df: pd.DataFrame) -> pd.DataFrame:
    sales = df[~df["is_return"]]
    out = sales.groupby("category").agg(revenue=("line_total", "sum"), invoices=("invoice_no", "nunique")).reset_index()
    out["share_pct"] = 100 * out["revenue"] / out["revenue"].sum()
    return out.sort_values("revenue", ascending=False).reset_index(drop=True)


def country_revenue(df: pd.DataFrame) -> pd.DataFrame:
    sales = df[~df["is_return"]]
    out = sales.groupby(["country", "region"]).agg(revenue=("line_total", "sum"), invoices=("invoice_no", "nunique"), customers=("customer_id", "nunique")).reset_index()
    out["aov"] = out["revenue"] / out["invoices"]
    out["share_pct"] = 100 * out["revenue"] / out["revenue"].sum()
    out["map_name"] = out["country"].map(lambda c: COUNTRY_ALIASES.get(c, c))
    return out.sort_values("revenue", ascending=False).reset_index(drop=True)


def rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    """Segmen RFM dihitung ulang pada data terfilter sehingga mengikuti pilihan pengguna."""
    sales = df[~df["is_return"] & ~df["is_guest"]].rename(columns={"invoice_datetime": "invoice_date"})
    if sales.empty:
        return pd.DataFrame(columns=["segment", "customers", "revenue", "customers_share_pct", "revenue_share_pct", "avg_recency_days", "avg_frequency", "avg_monetary"])
    scored = score_rfm(compute_rfm(sales))
    out = scored.groupby("segment").agg(customers=("customer_id", "size"), revenue=("monetary", "sum"), avg_recency_days=("recency_days", "mean"), avg_frequency=("frequency", "mean"), avg_monetary=("monetary", "mean")).reset_index()
    out["customers_share_pct"] = 100 * out["customers"] / out["customers"].sum()
    out["revenue_share_pct"] = 100 * out["revenue"] / out["revenue"].sum()
    return out.sort_values("revenue", ascending=False).reset_index(drop=True)


def day_hour_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Matriks jumlah invoice per hari (baris) dan jam (kolom)."""
    sales = df[~df["is_return"]].drop_duplicates("invoice_no")
    hours = sales["invoice_datetime"].dt.hour
    matrix = pd.crosstab(sales["day_of_week"], hours).reindex(range(1, 8), fill_value=0)
    matrix.index = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    return matrix
