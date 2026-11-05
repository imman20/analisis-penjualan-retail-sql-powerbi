"""Saya memisahkan sumber demo sampel dari warehouse analisis penuh."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.config import SAMPLE_CSV, WAREHOUSE_DB
from src.dashboard_data import load_flat
from src.data.build_warehouse import build_all, write_warehouse
from src.data.clean import clean_transactions, load_raw


def load_dashboard_source(db_path: Path = WAREHOUSE_DB, sample_path: Path = SAMPLE_CSV) -> tuple[pd.DataFrame, bool]:
    """Saya memakai sampel hanya bila warehouse penuh belum tersedia."""
    if db_path.exists():
        return load_flat(db_path), False
    sales, returns = clean_transactions(load_raw(sample_path))
    with TemporaryDirectory(prefix="retail-demo-") as folder:
        sample_db = Path(folder) / "sample.sqlite"
        write_warehouse(build_all(sales, returns), sample_db)
        return load_flat(sample_db), True
