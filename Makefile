# Perintah pintas untuk menjalankan seluruh pipeline proyek.
# Jalankan `make all` untuk membangun semuanya dari nol, atau target
# individual (mis. `make warehouse`) saat mengulang satu tahap saja.

PYTHON ?= python

.PHONY: all install data clean-data warehouse sql notebooks dashboard test lint streamlit help

help:
	@echo "Target yang tersedia:"
	@echo "  make install    - pasang dependensi dari requirements.txt"
	@echo "  make data       - unduh dataset UCI dan konversi ke CSV"
	@echo "  make clean-data - bersihkan data mentah -> parquet"
	@echo "  make warehouse  - bangun SQLite star schema"
	@echo "  make sql        - jalankan semua query sql/ -> reports/sql_output/"
	@echo "  make notebooks  - eksekusi ketiga notebook dan simpan output"
	@echo "  make dashboard  - bangun dashboard HTML statis + screenshot PNG"
	@echo "  make test       - ruff check + pytest"
	@echo "  make streamlit  - jalankan dashboard interaktif"
	@echo "  make all        - seluruh pipeline dari nol"

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

data:
	$(PYTHON) -m src.data.download

clean-data:
	$(PYTHON) -m src.data.clean

warehouse:
	$(PYTHON) -m src.data.build_warehouse

sql:
	$(PYTHON) -m src.run_sql

notebooks:
	$(PYTHON) -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=1800 notebooks/01_eda.ipynb
	$(PYTHON) -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=1800 notebooks/02_segmentasi_rfm.ipynb
	$(PYTHON) -m jupyter nbconvert --execute --to notebook --inplace --ExecutePreprocessor.timeout=1800 notebooks/03_uji_ab_promosi.ipynb

dashboard:
	$(PYTHON) -m app.build_static_dashboard

lint:
	ruff check .

test: lint
	$(PYTHON) -m pytest

streamlit:
	streamlit run app/dashboard.py

all: data clean-data warehouse sql notebooks dashboard test
