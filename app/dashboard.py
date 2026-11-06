"""Dashboard interaktif penjualan retail (Streamlit).

Jalankan dari akar proyek: ``streamlit run app/dashboard.py``.

Dashboard membaca warehouse SQLite (``data/processed/retail_dw.sqlite``) sekali
lalu menyimpannya di cache; semua filter (periode, negara, kategori) diterapkan
di memori sehingga interaksi terasa instan. Logika agregasi dan figur dipakai
bersama dengan dashboard statis (``src/dashboard_data.py`` dan
``src/dashboard_figures.py``) supaya angka di keduanya selalu sama.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dashboard_data import (  # noqa: E402
    apply_filters,
    category_share,
    compute_kpis,
    country_revenue,
    day_hour_matrix,
    monthly_trend,
    rfm_segments,
    top_products,
)
from src.dashboard_figures import (  # noqa: E402
    fig_category_share,
    fig_country_bar,
    fig_country_map,
    fig_day_hour_heatmap,
    fig_monthly_trend,
    fig_rfm_segments,
    fig_top_products,
)
from src.dashboard_source import load_dashboard_source  # noqa: E402
from src.viz import CATEGORY_ORDER  # noqa: E402

st.set_page_config(page_title="Dashboard Penjualan Retail", page_icon=":bar_chart:", layout="wide")


@st.cache_data(show_spinner="Memuat warehouse...")
def get_data() -> tuple[pd.DataFrame, bool]:
    return load_dashboard_source()


def fmt_gbp(value: float) -> str:
    if abs(value) >= 1e6:
        return f"GBP {value / 1e6:,.2f} jt"
    if abs(value) >= 1e3:
        return f"GBP {value / 1e3:,.1f} rb"
    return f"GBP {value:,.0f}"


df, is_sample = get_data()

# ---- Baris filter: satu baris di atas semua grafik agar seluruh dashboard mengikuti irisan yang sama.
st.title("Dashboard Penjualan Retail")
if is_sample:
    st.warning("Mode sampel: saya menampilkan sampel 5.000 baris yang tersedia di repo. Angka dashboard ini tidak mewakili hasil analisis penuh di README.")
st.caption("Online Retail II (UCI) - 1 Des 2009 s.d. 9 Des 2011. Pendapatan dalam GBP; retur sudah diperhitungkan pada pendapatan bersih.")

min_date, max_date = df["full_date"].min().date(), df["full_date"].max().date()
f1, f2, f3 = st.columns([1.2, 1.4, 1.4])
with f1:
    date_range = st.date_input("Periode", value=(min_date, max_date), min_value=min_date, max_value=max_date)
with f2:
    all_countries = sorted(df["country"].unique())
    countries = st.multiselect("Negara (kosong = semua)", options=all_countries, default=[])
with f3:
    categories = st.multiselect("Kategori produk (kosong = semua)", options=CATEGORY_ORDER, default=[])

start, end = (date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date))
filtered = apply_filters(df, start=start, end=end, countries=countries, categories=categories)

if filtered.empty:
    st.warning("Tidak ada transaksi pada kombinasi filter ini.")
    st.stop()

# ---- Kartu KPI.
kpi = compute_kpis(filtered)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pendapatan bersih", fmt_gbp(kpi["net_revenue"]), help="Penjualan kotor dikurangi nilai retur")
c2.metric("Invoice", f"{kpi['invoices']:,}")
c3.metric("Pelanggan terdaftar", f"{kpi['customers']:,}")
c4.metric("AOV", f"GBP {kpi['aov']:,.0f}", help="Rata-rata nilai per invoice penjualan")
c5.metric("Tingkat retur", f"{kpi['return_rate']:.1%}", help="Nilai retur / penjualan kotor")

# ---- Tab analisis.
tab_tren, tab_produk, tab_negara, tab_rfm, tab_waktu = st.tabs(["Tren bulanan", "Produk & kategori", "Negara", "Segmen RFM", "Hari & jam"])

with tab_tren:
    monthly = monthly_trend(filtered)
    st.plotly_chart(fig_monthly_trend(monthly), width="stretch")
    with st.expander("Lihat tabel"):
        st.dataframe(monthly.style.format({"revenue": "{:,.0f}", "aov": "{:,.0f}"}), width="stretch", hide_index=True)

with tab_produk:
    left, right = st.columns([1.3, 1])
    top = top_products(filtered, n=10)
    cat = category_share(filtered)
    left.plotly_chart(fig_top_products(top), width="stretch")
    right.plotly_chart(fig_category_share(cat), width="stretch")
    with st.expander("Lihat tabel"):
        st.dataframe(top.style.format({"net_revenue": "{:,.0f}", "units": "{:,.0f}"}), width="stretch", hide_index=True)

with tab_negara:
    country = country_revenue(filtered)
    left, right = st.columns([1.3, 1])
    left.plotly_chart(fig_country_map(country), width="stretch")
    right.plotly_chart(fig_country_bar(country, n=10, exclude_uk=True), width="stretch")
    with st.expander("Lihat tabel"):
        st.dataframe(country.drop(columns="map_name").style.format({"revenue": "{:,.0f}", "aov": "{:,.0f}", "share_pct": "{:.2f}"}), width="stretch", hide_index=True)

with tab_rfm:
    st.caption("Segmen dihitung ulang pada data terfilter (pelanggan tamu dikecualikan). Tanggal acuan recency = sehari setelah transaksi terakhir pada irisan data.")
    seg = rfm_segments(filtered)
    if seg.empty:
        st.info("Tidak ada pelanggan terdaftar pada filter ini.")
    else:
        st.plotly_chart(fig_rfm_segments(seg), width="stretch")
        st.dataframe(seg.style.format({"revenue": "{:,.0f}", "avg_recency_days": "{:,.0f}", "avg_frequency": "{:,.1f}", "avg_monetary": "{:,.0f}", "customers_share_pct": "{:.1f}", "revenue_share_pct": "{:.1f}"}), width="stretch", hide_index=True)

with tab_waktu:
    st.plotly_chart(fig_day_hour_heatmap(day_hour_matrix(filtered)), width="stretch")

st.markdown("---")
st.caption("Sumber data: Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository. Kategori produk ditetapkan dari kata kunci deskripsi (lihat docs/metodologi.md).")
