"""Palet warna dan gaya grafik yang dipakai notebook dan dashboard.

Satu sumber kebenaran untuk warna supaya grafik di notebook (matplotlib),
dashboard statis, dan dashboard Streamlit (Plotly) terlihat seragam. Urutan
warna kategorikal bersifat tetap (bukan diputar) dan sudah divalidasi aman
untuk buta warna pada pasangan yang berdampingan; kategori "Other" selalu
memakai abu-abu netral agar tidak bersaing dengan kategori bermakna.
"""

from __future__ import annotations

import matplotlib as mpl

# Warna kategorikal berurutan (slot 1..8). Jangan menambah slot ke-9: lipat ke "Other".
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
OTHER_GRAY = "#898781"

# Ramp sekuensial satu warna (biru, terang -> gelap) untuk magnitudo/heatmap.
SEQUENTIAL = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]

# Warna kromatik untuk teks/garis bantu.
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Urutan kategori produk yang konsisten di semua grafik (berdasarkan pendapatan).
CATEGORY_ORDER = [
    "Home Decor",
    "Kitchen & Dining",
    "Bags & Accessories",
    "Stationery & Gift Wrap",
    "Candles & Lighting",
    "Christmas & Seasonal",
    "Garden & Outdoor",
    "Toys & Kids",
    "Other",
]
CATEGORY_COLORS = {name: (OTHER_GRAY if name == "Other" else SERIES[i]) for i, name in enumerate(CATEGORY_ORDER)}

# Dua kelompok uji A/B selalu memakai dua slot pertama.
GROUP_COLORS = {"A": SERIES[0], "B": SERIES[1]}


def apply_matplotlib_style() -> None:
    """Gaya matplotlib: garis tipis, grid hairline, tanpa bingkai atas/kanan."""
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "axes.edgecolor": AXIS,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "grid.linestyle": "-",
            "axes.axisbelow": True,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlecolor": INK_PRIMARY,
            "axes.labelcolor": INK_SECONDARY,
            "axes.labelsize": 10,
            "xtick.color": INK_MUTED,
            "ytick.color": INK_MUTED,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "lines.linewidth": 2,
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Segoe UI", "Arial"],
            "figure.dpi": 110,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
        }
    )


def gbp(value: float, decimals: int = 0) -> str:
    """Format angka sebagai GBP ringkas: 1.234.567 -> 'GBP 1,23 jt'."""
    if abs(value) >= 1_000_000:
        return f"GBP {value / 1_000_000:,.2f} jt".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(value) >= 1_000:
        return f"GBP {value / 1_000:,.1f} rb".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"GBP {value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
