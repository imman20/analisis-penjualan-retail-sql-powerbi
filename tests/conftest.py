"""Fixture bersama: data mentah kecil yang meniru struktur Online Retail II.

Data dibuat secara manual agar tiap kasus pembersihan (duplikat, retur,
kode non-produk, harga nol, pelanggan tamu) terwakili dan hasilnya bisa
diverifikasi dengan tangan.
"""

from __future__ import annotations

import pandas as pd
import pytest


def make_raw_small() -> pd.DataFrame:
    """Fungsi biasa agar bisa dipanggil langsung di luar mekanisme fixture."""
    rows = [
        # invoice, stock, desc, qty, date, price, customer, country
        ("536365", "85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 6, "2010-12-01 08:26:00", 2.55, 17850, "United Kingdom"),
        ("536365", "85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 6, "2010-12-01 08:26:00", 2.55, 17850, "United Kingdom"),  # duplikat
        ("536365", "71053", "WHITE METAL LANTERN", 6, "2010-12-01 08:26:00", 3.39, 17850, "United Kingdom"),
        ("536366", "22633", "HAND WARMER UNION JACK", 6, "2010-12-01 08:28:00", 1.85, 17850, "United Kingdom"),
        ("536367", "84879", "ASSORTED COLOUR BIRD ORNAMENT", 32, "2010-12-01 08:34:00", 1.69, 13047, "United Kingdom"),
        ("536367", "POST", "POSTAGE", 1, "2010-12-01 08:34:00", 18.00, 13047, "United Kingdom"),  # non-produk
        ("536368", "22960", "JAM MAKING SET WITH JARS", 6, "2010-12-02 10:03:00", 4.25, 12583, "France"),
        ("536369", "21756", "BATH BUILDING BLOCK WORD", 3, "2010-12-03 10:03:00", 5.95, None, "United Kingdom"),  # tamu
        ("536370", "22728", "ALARM CLOCK BAKELIKE PINK", 24, "2011-01-05 09:00:00", 3.75, 12583, "France"),
        ("536371", "21756", "BATH BUILDING BLOCK WORD", 1, "2011-01-10 09:00:00", 0.0, None, "United Kingdom"),  # harga nol
        ("536372", "85123A", "check", -3, "2011-01-11 09:00:00", 2.55, None, "United Kingdom"),  # penyesuaian stok
        ("C536373", "85123A", "WHITE HANGING HEART T-LIGHT HOLDER", -2, "2011-01-12 09:00:00", 2.55, 17850, "United Kingdom"),  # retur
        ("536374", "22633", "HAND WARMER UNION JACK", 12, "2011-02-01 11:00:00", 1.85, 13047, "United Kingdom"),
        ("536375", "22960", "JAM MAKING SET WITH JARS", 2, "2011-02-15 11:00:00", 4.25, 12583, "France"),
    ]
    df = pd.DataFrame(rows, columns=["invoice_no", "stock_code", "description", "quantity", "invoice_date", "unit_price", "customer_id", "country"])
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    return df


@pytest.fixture
def raw_small() -> pd.DataFrame:
    return make_raw_small()
