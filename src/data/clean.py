"""Pembersihan data transaksi Online Retail II.

Masalah kualitas data yang ditemukan saat eksplorasi dan cara penanganannya:

* **Duplikat persis** (~12 ribu baris): dihapus karena hampir pasti akibat
  ekspor ganda dari sistem kasir, bukan transaksi berbeda.
* **Kode stok non-produk** (POST, DOT, M, D, BANK CHARGES, ADJUST, dsb.):
  bukan barang dagangan melainkan ongkos kirim, penyesuaian manual, atau
  komisi; dihapus agar metrik produk tidak tercemar.
* **Harga <= 0**: hampir semuanya baris internal tanpa pelanggan
  (keterangan "check", "damages", "?"); dihapus.
* **Kuantitas negatif tanpa nomor invoice berawalan "C"**: penyesuaian stok
  (barang rusak/hilang), bukan retur pelanggan; dihapus.
* **Invoice berawalan "C"**: pembatalan/retur pelanggan. Dipisahkan ke tabel
  retur dengan ``is_return = True`` agar analisis penjualan dan analisis retur
  bisa dilakukan secara terpisah maupun digabung (net revenue).
* **Customer ID kosong** (~23% baris): dipertahankan sebagai pelanggan tamu
  (``is_guest = True``) karena tetap merupakan penjualan nyata; analisis
  per pelanggan (RFM, cohort) cukup memfilter ``is_guest = False``.

Fungsi-fungsi di sini murni (menerima dan mengembalikan DataFrame) sehingga
mudah diuji dengan pytest.
"""

from __future__ import annotations

import sys

import pandas as pd

from src.config import CLEAN_PARQUET, PROCESSED_DIR, RAW_CSV

RETURNS_PARQUET = PROCESSED_DIR / "retail_returns.parquet"

# Kode stok produk sungguhan di dataset ini selalu diawali 5 digit angka,
# opsional diikuti huruf varian (mis. 85123A, 79323P). Kode lain adalah
# biaya administratif (POST, DOT, M, D, BANK CHARGES, AMAZONFEE, ...),
# voucher hadiah (gift_0001_10) atau kode uji (TEST001).
PRODUCT_CODE_PATTERN = r"^\d{5}[A-Za-z]{0,3}$"

REQUIRED_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
]


def load_raw(path=RAW_CSV) -> pd.DataFrame:
    """Membaca CSV mentah dengan tipe data yang aman.

    ``invoice_no`` dan ``stock_code`` dibaca sebagai string sejak awal supaya
    nilai seperti "C489535" atau "85123A" tidak dipaksa menjadi angka.
    """
    df = pd.read_csv(
        path,
        dtype={"invoice_no": "string", "stock_code": "string", "description": "string"},
        parse_dates=["invoice_date"],
    )
    return df


def standardize_types(df: pd.DataFrame) -> pd.DataFrame:
    """Menyeragamkan tipe data dan membersihkan spasi/kapitalisasi."""
    out = df.copy()
    out["invoice_no"] = out["invoice_no"].astype("string").str.strip()
    out["stock_code"] = out["stock_code"].astype("string").str.strip().str.upper()
    out["description"] = out["description"].astype("string").str.strip()
    out["invoice_date"] = pd.to_datetime(out["invoice_date"])
    out["quantity"] = out["quantity"].astype("int64")
    out["unit_price"] = out["unit_price"].astype("float64")
    # Int64 (nullable) agar ID pelanggan kosong tetap NA, bukan 0 atau NaN float.
    out["customer_id"] = out["customer_id"].astype("Int64")
    out["country"] = out["country"].astype("string").str.strip()
    return out


def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Menghapus baris yang identik di seluruh kolom transaksi."""
    return df.drop_duplicates(subset=REQUIRED_COLUMNS).reset_index(drop=True)


def keep_product_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Menyaring hanya baris produk nyata berdasarkan pola kode stok."""
    mask = df["stock_code"].str.match(PRODUCT_CODE_PATTERN).fillna(False)
    return df[mask].reset_index(drop=True)


def drop_invalid_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Menghapus baris dengan harga nol/negatif dan deskripsi kosong."""
    mask = (df["unit_price"] > 0) & df["description"].notna()
    return df[mask].reset_index(drop=True)


def split_sales_and_returns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Memisahkan penjualan (qty > 0) dari retur (invoice "C", qty < 0).

    Kuantitas negatif tanpa prefiks "C" adalah penyesuaian stok internal dan
    dibuang. Baris retur tetap menyimpan kuantitas negatif sehingga
    ``line_total`` otomatis mengurangi pendapatan bila digabung.
    """
    is_cancel = df["invoice_no"].str.startswith("C").fillna(False)
    sales = df[(df["quantity"] > 0) & ~is_cancel].copy()
    returns = df[(df["quantity"] < 0) & is_cancel].copy()
    sales["is_return"] = False
    returns["is_return"] = True
    return sales.reset_index(drop=True), returns.reset_index(drop=True)


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Menambahkan kolom turunan yang sering dipakai analisis."""
    out = df.copy()
    out["line_total"] = (out["quantity"] * out["unit_price"]).round(2)
    out["is_guest"] = out["customer_id"].isna()
    out["invoice_month"] = out["invoice_date"].dt.to_period("M").astype(str)
    return out


def clean_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Menjalankan seluruh tahapan pembersihan dan mengembalikan (sales, returns)."""
    df = standardize_types(raw)
    df = drop_exact_duplicates(df)
    df = keep_product_rows(df)
    df = drop_invalid_prices(df)
    sales, returns = split_sales_and_returns(df)
    return add_derived_columns(sales), add_derived_columns(returns)


def cleaning_report(raw: pd.DataFrame, sales: pd.DataFrame, returns: pd.DataFrame) -> dict[str, int]:
    """Ringkasan angka sebelum/sesudah pembersihan untuk dokumentasi."""
    return {
        "raw_rows": int(len(raw)),
        "sales_rows": int(len(sales)),
        "return_rows": int(len(returns)),
        "dropped_rows": int(len(raw) - len(sales) - len(returns)),
        "sales_invoices": int(sales["invoice_no"].nunique()),
        "return_invoices": int(returns["invoice_no"].nunique()),
        "customers_with_id": int(sales["customer_id"].dropna().nunique()),
        "products": int(sales["stock_code"].nunique()),
    }


def main() -> int:
    raw = load_raw()
    print(f"[clean] baris mentah: {len(raw):,}")
    sales, returns = clean_transactions(raw)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sales.to_parquet(CLEAN_PARQUET, index=False)
    returns.to_parquet(RETURNS_PARQUET, index=False)
    report = cleaning_report(raw, sales, returns)
    for key, value in report.items():
        print(f"[clean] {key}: {value:,}")
    print(f"[clean] tersimpan: {CLEAN_PARQUET} dan {RETURNS_PARQUET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
