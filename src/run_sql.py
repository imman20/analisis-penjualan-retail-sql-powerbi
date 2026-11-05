"""Menjalankan seluruh query di folder ``sql/`` dan menyimpan hasilnya sebagai CSV.

Setiap file ``NN_nama.sql`` dieksekusi terhadap warehouse SQLite dan hasilnya
ditulis ke ``reports/sql_output/NN_nama.csv``. Selain itu dibuat berkas
``reports/sql_output/_indeks.md`` berisi jumlah baris dan pratinjau tiap hasil
agar mudah ditinjau di GitHub tanpa membuka CSV satu per satu.

Jalankan dengan ``python -m src.run_sql`` dari akar proyek.
"""

from __future__ import annotations

import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd

from src.config import SQL_DIR, SQL_OUTPUT_DIR, WAREHOUSE_DB


def list_sql_files(sql_dir: Path = SQL_DIR) -> list[Path]:
    """Mengembalikan file .sql terurut berdasarkan nomor di awal nama."""
    return sorted(sql_dir.glob("*.sql"))


def run_query_file(conn: sqlite3.Connection, sql_path: Path) -> pd.DataFrame:
    """Mengeksekusi satu file SQL dan mengembalikan hasilnya sebagai DataFrame."""
    query = sql_path.read_text(encoding="utf-8")
    return pd.read_sql_query(query, conn)


def run_all(db_path: Path = WAREHOUSE_DB, sql_dir: Path = SQL_DIR, output_dir: Path = SQL_OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    """Menjalankan semua query dan menyimpan CSV + indeks markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}
    index_lines = ["# Indeks hasil query SQL", "", "Dibuat otomatis oleh `python -m src.run_sql`.", ""]

    with sqlite3.connect(db_path) as conn:
        for sql_path in list_sql_files(sql_dir):
            started = time.perf_counter()
            df = run_query_file(conn, sql_path)
            elapsed = time.perf_counter() - started
            csv_path = output_dir / f"{sql_path.stem}.csv"
            df.to_csv(csv_path, index=False)
            results[sql_path.stem] = df
            print(f"[sql] {sql_path.name:45s} -> {len(df):6,} baris ({elapsed:.2f}s)")

            index_lines.append(f"## {sql_path.stem}")
            index_lines.append("")
            index_lines.append(f"- File query: `sql/{sql_path.name}`")
            index_lines.append(f"- Hasil: `reports/sql_output/{csv_path.name}` ({len(df):,} baris, {elapsed:.2f} detik)")
            index_lines.append("")
            index_lines.append(df.head(8).to_markdown(index=False))
            index_lines.append("")

    (output_dir / "_indeks.md").write_text("\n".join(index_lines), encoding="utf-8")
    return results


def main() -> int:
    if not WAREHOUSE_DB.exists():
        print(f"Warehouse tidak ditemukan: {WAREHOUSE_DB}. Jalankan python -m src.data.build_warehouse dahulu.")
        return 1
    run_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
