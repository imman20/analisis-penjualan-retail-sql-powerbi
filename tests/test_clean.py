"""Pengujian tahap pembersihan data."""

from __future__ import annotations

import pandas as pd

from src.data.clean import (
    clean_transactions,
    cleaning_report,
    drop_exact_duplicates,
    drop_invalid_prices,
    keep_product_rows,
    split_sales_and_returns,
    standardize_types,
)


def test_standardize_types_sets_expected_dtypes(raw_small):
    df = standardize_types(raw_small)
    assert str(df["customer_id"].dtype) == "Int64"
    assert pd.api.types.is_datetime64_any_dtype(df["invoice_date"])
    # Tidak boleh ada huruf kecil pada kode stok setelah standardisasi.
    assert not df["stock_code"].str.contains(r"[a-z]").any()


def test_exact_duplicates_are_removed(raw_small):
    df = drop_exact_duplicates(standardize_types(raw_small))
    assert len(df) == len(raw_small) - 1
    assert not df.duplicated().any()


def test_non_product_codes_are_dropped(raw_small):
    df = keep_product_rows(standardize_types(raw_small))
    assert "POST" not in set(df["stock_code"])
    assert {"85123A", "71053", "22633"} <= set(df["stock_code"])


def test_zero_price_rows_are_dropped(raw_small):
    df = drop_invalid_prices(standardize_types(raw_small))
    assert (df["unit_price"] > 0).all()


def test_returns_are_split_and_stock_adjustments_dropped(raw_small):
    df = standardize_types(raw_small)
    sales, returns = split_sales_and_returns(df)
    assert (sales["quantity"] > 0).all()
    assert (returns["quantity"] < 0).all()
    assert returns["invoice_no"].str.startswith("C").all()
    # Baris "check" dengan qty -3 tanpa prefiks C harus hilang dari keduanya.
    assert "536372" not in set(sales["invoice_no"]) | set(returns["invoice_no"])


def test_clean_transactions_end_to_end(raw_small):
    sales, returns = clean_transactions(raw_small)
    # 14 baris mentah: -1 duplikat, -1 POST, -1 harga nol, -1 penyesuaian, -1 retur = 9 penjualan.
    assert len(sales) == 9
    assert len(returns) == 1
    assert {"line_total", "is_guest", "is_return", "invoice_month"} <= set(sales.columns)
    assert sales.loc[sales["invoice_no"] == "536367", "line_total"].iloc[0] == round(32 * 1.69, 2)
    assert sales["is_guest"].sum() == 1
    report = cleaning_report(raw_small, sales, returns)
    assert report["raw_rows"] == 14
    assert report["dropped_rows"] == 4
