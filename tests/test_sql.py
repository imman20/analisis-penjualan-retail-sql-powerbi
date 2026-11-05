"""Memastikan setiap file di sql/ valid dan bisa dijalankan pada warehouse kecil.

Pengujian ini tidak memverifikasi angka bisnis (itu peran notebook dan
dokumentasi), melainkan menjaga agar perubahan skema tidak diam-diam
merusak salah satu query.
"""

from __future__ import annotations

import sqlite3

import pytest

from src.config import SQL_DIR
from src.data.build_warehouse import build_all, write_warehouse
from src.data.clean import clean_transactions
from src.run_sql import list_sql_files, run_all, run_query_file


@pytest.fixture(scope="module")
def small_db(tmp_path_factory):
    # Fixture raw_small bersifat function-scope, jadi data dibangun langsung di sini.
    from tests.conftest import make_raw_small

    sales, returns = clean_transactions(make_raw_small())
    db_path = tmp_path_factory.mktemp("dw") / "retail_dw.sqlite"
    write_warehouse(build_all(sales, returns), db_path)
    return db_path


def test_there_are_at_least_twelve_sql_files():
    assert len(list_sql_files(SQL_DIR)) >= 12


def test_every_sql_file_has_business_question_header():
    for path in list_sql_files(SQL_DIR):
        text = path.read_text(encoding="utf-8")
        assert "Pertanyaan bisnis" in text, path.name
        assert "Insight hasil" in text, path.name
        assert "(diisi setelah" not in text, f"insight belum diisi di {path.name}"


@pytest.mark.parametrize("sql_path", list_sql_files(SQL_DIR), ids=lambda p: p.name)
def test_each_query_executes(small_db, sql_path):
    with sqlite3.connect(small_db) as conn:
        df = run_query_file(conn, sql_path)
    assert df.shape[1] >= 1


def test_run_all_writes_csv_and_index(small_db, tmp_path):
    out_dir = tmp_path / "sql_output"
    results = run_all(db_path=small_db, output_dir=out_dir)
    assert len(results) == len(list_sql_files(SQL_DIR))
    assert (out_dir / "_indeks.md").exists()
    assert (out_dir / "01_ringkasan_kpi.csv").exists()
