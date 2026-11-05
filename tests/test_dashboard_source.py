"""Saya menguji batas antara demo sampel dan analisis penuh."""

import pytest

from src.config import SAMPLE_CSV
from src.dashboard_data import compute_kpis
from src.dashboard_source import load_dashboard_source
from src.data.build_warehouse import build_all, write_warehouse
from src.data.clean import clean_transactions, load_raw


def test_sample_fallback_does_not_create_full_warehouse(tmp_path):
    warehouse = tmp_path / "full.sqlite"
    data, is_sample = load_dashboard_source(warehouse, SAMPLE_CSV)
    assert is_sample
    assert not warehouse.exists()
    assert not data.empty
    sales, returns = clean_transactions(load_raw(SAMPLE_CSV))
    assert compute_kpis(data)["net_revenue"] == pytest.approx(sales.line_total.sum() + returns.line_total.sum(), abs=1e-7)


def test_existing_warehouse_takes_priority(tmp_path):
    warehouse = tmp_path / "full.sqlite"
    sales, returns = clean_transactions(load_raw(SAMPLE_CSV))
    write_warehouse(build_all(sales, returns), warehouse)
    data, is_sample = load_dashboard_source(warehouse, tmp_path / "missing.csv")
    assert not is_sample
    assert len(data) == len(sales) + len(returns)
