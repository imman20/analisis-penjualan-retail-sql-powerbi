"""Mengunduh dataset publik Online Retail II (UCI) dan mengonversinya ke CSV.

Alur:
1. Unduh arsip zip dari UCI Machine Learning Repository ke ``data/raw/``.
2. Ekstrak file ``online_retail_II.xlsx`` (dua sheet: 2009-2010 dan 2010-2011).
3. Gabungkan kedua sheet menjadi satu CSV mentah ``data/raw/online_retail_II.csv``.
4. Simpan sampel 5.000 baris pertama ke ``data/raw/sample/`` agar repositori tetap
   ringan (file penuh berukuran > 20 MB sehingga diabaikan oleh git).

Skrip ini idempoten: jika CSV mentah sudah ada, langkah unduh dan konversi
dilewati. Jalankan dengan ``python -m src.data.download`` dari akar proyek.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from src.config import RAW_CSV, RAW_DIR, SAMPLE_CSV, SAMPLE_ROWS

# Sumber resmi dataset (lisensi CC BY 4.0).
DATASET_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP_PATH = RAW_DIR / "online_retail_ii.zip"
XLSX_NAME = "online_retail_II.xlsx"

# Nama kolom asli -> nama snake_case yang dipakai di seluruh proyek.
COLUMN_MAP = {
    "Invoice": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def download_zip(url: str = DATASET_URL, dest: Path = ZIP_PATH, retries: int = 2) -> Path:
    """Mengunduh arsip zip dengan percobaan ulang sederhana.

    Percobaan ulang diperlukan karena koneksi ke server UCI kadang terputus
    di tengah transfer untuk file berukuran ~45 MB.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"[download] arsip sudah ada, lewati: {dest}")
        return dest

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            print(f"[download] percobaan {attempt}/{retries}: {url}")
            urllib.request.urlretrieve(url, dest)
            # Validasi sederhana: pastikan file benar-benar arsip zip.
            with zipfile.ZipFile(dest) as zf:
                zf.testzip()
            return dest
        except Exception as exc:  # noqa: BLE001 - kita ingin mencoba ulang apa pun errornya
            last_error = exc
            print(f"[download] gagal: {exc}")
            time.sleep(3)
    raise RuntimeError(f"Gagal mengunduh dataset setelah {retries} percobaan: {last_error}")


def extract_xlsx(zip_path: Path = ZIP_PATH, dest_dir: Path = RAW_DIR) -> Path:
    """Mengekstrak file xlsx dari arsip zip."""
    xlsx_path = dest_dir / XLSX_NAME
    if xlsx_path.exists():
        print(f"[extract] xlsx sudah ada, lewati: {xlsx_path}")
        return xlsx_path
    with zipfile.ZipFile(zip_path) as zf:
        zf.extract(XLSX_NAME, dest_dir)
    print(f"[extract] selesai: {xlsx_path}")
    return xlsx_path


def xlsx_to_csv(xlsx_path: Path, csv_path: Path = RAW_CSV) -> pd.DataFrame:
    """Menggabungkan semua sheet xlsx ke satu CSV mentah.

    Membaca xlsx 1 juta baris dengan openpyxl memakan waktu beberapa menit;
    karena itu hasilnya disimpan sebagai CSV supaya langkah berikutnya cepat.
    """
    print("[convert] membaca xlsx (butuh beberapa menit)...")
    sheets = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")
    frames = []
    for sheet_name, frame in sheets.items():
        frame = frame.rename(columns=COLUMN_MAP)
        frame["source_sheet"] = sheet_name
        frames.append(frame)
        print(f"[convert] sheet '{sheet_name}': {len(frame):,} baris")
    df = pd.concat(frames, ignore_index=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"[convert] CSV mentah disimpan: {csv_path} ({len(df):,} baris)")
    return df


def write_sample(df: pd.DataFrame, sample_path: Path = SAMPLE_CSV, n: int = SAMPLE_ROWS) -> None:
    """Menyimpan sampel kecil yang ikut dikomit agar struktur data bisa dilihat di GitHub."""
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df.head(n).to_csv(sample_path, index=False)
    print(f"[sample] {n:,} baris disimpan: {sample_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="unduh dan konversi ulang walau CSV sudah ada")
    args = parser.parse_args(argv)

    if RAW_CSV.exists() and not args.force:
        print(f"[download] CSV mentah sudah ada, lewati semua langkah: {RAW_CSV}")
        if not SAMPLE_CSV.exists():
            write_sample(pd.read_csv(RAW_CSV, nrows=SAMPLE_ROWS))
        return 0

    zip_path = download_zip()
    xlsx_path = extract_xlsx(zip_path)
    df = xlsx_to_csv(xlsx_path)
    write_sample(df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
