#!/usr/bin/env bash
# Menjalankan seluruh pipeline dari nol: unduh data -> bersihkan -> warehouse
# -> query SQL -> notebook -> dashboard statis -> lint dan tes.
# Hentikan di langkah pertama yang gagal agar kesalahan tidak merambat.
set -euo pipefail

cd "$(dirname "$0")"

echo "== [1/7] Unduh dan konversi dataset =="
python -m src.data.download

echo "== [2/7] Pembersihan data =="
python -m src.data.clean

echo "== [3/7] Membangun star schema SQLite =="
python -m src.data.build_warehouse

echo "== [4/7] Menjalankan query SQL =="
python -m src.run_sql

echo "== [5/7] Mengeksekusi notebook =="
for nb in notebooks/01_eda.ipynb notebooks/02_segmentasi_rfm.ipynb notebooks/03_uji_ab_promosi.ipynb; do
    python -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=1800 "$nb"
done

echo "== [6/7] Membangun dashboard statis dan screenshot =="
python -m app.build_static_dashboard

echo "== [7/7] Lint dan unit test =="
ruff check .
python -m pytest

echo "Selesai. Jalankan 'streamlit run app/dashboard.py' untuk dashboard interaktif."
