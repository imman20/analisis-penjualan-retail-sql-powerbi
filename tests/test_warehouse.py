"""Pengujian skema star dan integritas referensial warehouse."""

from __future__ import annotations

import sqlite3

import pandas as pd
import pytest

from src.data.build_warehouse import STORES, build_all, build_dim_date, country_to_region, write_warehouse
from src.data.clean import clean_transactions


@pytest.fixture
def tables(raw_small):
    sales, returns = clean_transactions(raw_small)
    return build_all(sales, returns)


def test_all_five_tables_are_built(tables):
    assert set(tables) == {"fact_sales", "dim_product", "dim_customer", "dim_date", "dim_store"}


def test_fact_row_count_matches_sales_plus_returns(raw_small, tables):
    sales, returns = clean_transactions(raw_small)
    assert len(tables["fact_sales"]) == len(sales) + len(returns)
    assert tables["fact_sales"]["is_return"].sum() == len(returns)


def test_every_fact_key_exists_in_its_dimension(tables):
    fact = tables["fact_sales"]
    assert fact["product_key"].isin(tables["dim_product"]["product_key"]).all()
    assert fact["customer_key"].isin(tables["dim_customer"]["customer_key"]).all()
    assert fact["date_key"].isin(tables["dim_date"]["date_key"]).all()
    assert fact["store_key"].isin(tables["dim_store"]["store_key"]).all()


def test_dim_customer_has_one_row_per_registered_customer_and_guest_per_country(tables):
    dim = tables["dim_customer"]
    registered = dim[dim["is_guest"] == 0]
    guests = dim[dim["is_guest"] == 1]
    assert registered["customer_id"].is_unique
    assert set(registered["customer_id"]) == {17850, 13047, 12583}
    assert len(guests) == 1 and guests["country"].iloc[0] == "United Kingdom"


def test_dim_date_covers_full_range_with_valid_keys():
    dim = build_dim_date(pd.Timestamp("2010-12-30"), pd.Timestamp("2011-01-02"))
    assert len(dim) == 4
    assert dim["date_key"].tolist() == [20101230, 20101231, 20110101, 20110102]
    assert dim.loc[dim["full_date"] == "2011-01-01", "is_weekend"].iloc[0] == 1  # Sabtu


def test_country_region_mapping():
    assert country_to_region("United Kingdom") == "United Kingdom"
    assert country_to_region("France") == "Europe"
    assert country_to_region("Australia") == "Rest of World"
    assert set(STORES["region"]) == {"United Kingdom", "Europe", "Rest of World"}


def test_write_warehouse_creates_queryable_sqlite(tables, tmp_path):
    db_path = tmp_path / "dw.sqlite"
    write_warehouse(tables, db_path)
    with sqlite3.connect(db_path) as conn:
        total = conn.execute("SELECT ROUND(SUM(line_total), 2) FROM fact_sales WHERE is_return = 0").fetchone()[0]
        # Tabel internal sqlite_stat1 (hasil ANALYZE) tidak dihitung.
        n_tables = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
        orphan = conn.execute(
            "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product p ON p.product_key = f.product_key WHERE p.product_key IS NULL"
        ).fetchone()[0]
    assert n_tables == 5
    assert orphan == 0
    assert total == round(float(tables["fact_sales"].query("is_return == 0")["line_total"].sum()), 2)
