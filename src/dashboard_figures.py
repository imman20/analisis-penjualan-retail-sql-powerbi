"""Figur Plotly yang dipakai bersama oleh dashboard Streamlit dan dashboard statis.

Setiap fungsi menerima hasil agregasi dari ``src.dashboard_data`` dan
mengembalikan ``plotly.graph_objects.Figure``. Gaya mengikuti ``src.viz``:
garis tipis, grid hairline, warna kategori tetap, dan satu sumbu y per grafik.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.viz import AXIS, CATEGORY_COLORS, GRID, INK_MUTED, INK_PRIMARY, INK_SECONDARY, OTHER_GRAY, SEQUENTIAL, SERIES

FONT = dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK_PRIMARY, size=12)
MONTH_ID = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mei", "06": "Jun", "07": "Jul", "08": "Agu", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des"}


def _base_layout(fig: go.Figure, title: str, height: int = 360) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=INK_PRIMARY), x=0, xanchor="left"),
        font=FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=48, b=10),
        height=height,
        hoverlabel=dict(bgcolor="white", font=dict(color=INK_PRIMARY)),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(color=INK_SECONDARY)),
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS, tickfont=dict(color=INK_MUTED), title_font=dict(color=INK_SECONDARY), zeroline=False)
    fig.update_yaxes(gridcolor=GRID, gridwidth=1, linecolor="rgba(0,0,0,0)", tickfont=dict(color=INK_MUTED), title_font=dict(color=INK_SECONDARY), zeroline=False)
    return fig


def fig_monthly_trend(monthly: pd.DataFrame) -> go.Figure:
    """Garis pendapatan bulanan; bulan parsial ditandai titik terbuka."""
    fig = go.Figure()
    labels = [f"{MONTH_ID[m[5:]]} {m[:4]}" for m in monthly["year_month"]]
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=monthly["revenue"],
            mode="lines+markers",
            name="Pendapatan",
            line=dict(color=SERIES[0], width=2),
            marker=dict(size=7, color=SERIES[0], line=dict(color="white", width=2)),
            customdata=monthly[["invoices", "aov"]].to_numpy(),
            hovertemplate="<b>%{x}</b><br>Pendapatan: GBP %{y:,.0f}<br>Invoice: %{customdata[0]:,}<br>AOV: GBP %{customdata[1]:,.0f}<extra></extra>",
        )
    )
    partial = monthly[monthly["partial_month"]]
    if not partial.empty:
        fig.add_trace(
            go.Scatter(
                x=[f"{MONTH_ID[m[5:]]} {m[:4]}" for m in partial["year_month"]],
                y=partial["revenue"],
                mode="markers",
                name="Bulan parsial (data tidak lengkap)",
                marker=dict(size=11, color="white", line=dict(color=SERIES[0], width=2)),
                hovertemplate="<b>%{x}</b> (hanya sebagian hari)<br>Pendapatan: GBP %{y:,.0f}<extra></extra>",
            )
        )
    if len(monthly) > 0:
        peak = monthly.loc[monthly["revenue"].idxmax()]
        fig.add_annotation(x=labels[int(monthly.index.get_loc(peak.name))], y=peak["revenue"], text=f"Puncak GBP {peak['revenue'] / 1e6:.2f} jt", showarrow=True, arrowhead=0, arrowcolor=INK_MUTED, ax=-60, ay=-25, font=dict(color=INK_SECONDARY, size=11))
    fig.update_yaxes(title="GBP", tickformat="~s", rangemode="tozero")
    return _base_layout(fig, "Tren pendapatan bulanan", height=380)


def fig_top_products(top: pd.DataFrame) -> go.Figure:
    """Bar horizontal produk teratas; warna mengikuti kategori."""
    top = top.iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=top["net_revenue"],
            y=top["description"].str.title(),
            orientation="h",
            marker=dict(color=[CATEGORY_COLORS.get(c, OTHER_GRAY) for c in top["category"]]),
            customdata=top[["category", "units"]].to_numpy(),
            hovertemplate="<b>%{y}</b><br>Kategori: %{customdata[0]}<br>Pendapatan bersih: GBP %{x:,.0f}<br>Unit: %{customdata[1]:,}<extra></extra>",
            text=[f"GBP {v / 1e3:,.0f} rb" for v in top["net_revenue"]],
            textposition="outside",
            textfont=dict(color=INK_SECONDARY, size=11),
            cliponaxis=False,
        )
    )
    # Ruang ekstra di kanan agar label nilai di ujung bar tidak terpotong.
    fig.update_xaxes(title="Pendapatan bersih (GBP)", tickformat="~s", showgrid=True, gridcolor=GRID, range=[0, float(top["net_revenue"].max()) * 1.22])
    fig.update_yaxes(showgrid=False, tickfont=dict(size=11))
    fig.update_layout(bargap=0.35)
    return _base_layout(fig, "10 produk teratas (pendapatan bersih, warna = kategori)", height=420)


def fig_category_share(cat: pd.DataFrame) -> go.Figure:
    cat = cat.iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=cat["share_pct"],
            y=cat["category"],
            orientation="h",
            marker=dict(color=[CATEGORY_COLORS.get(c, OTHER_GRAY) for c in cat["category"]]),
            customdata=cat[["revenue", "invoices"]].to_numpy(),
            hovertemplate="<b>%{y}</b><br>Pangsa: %{x:.1f}%<br>Pendapatan: GBP %{customdata[0]:,.0f}<br>Invoice: %{customdata[1]:,}<extra></extra>",
            text=[f"{v:.1f}%" for v in cat["share_pct"]],
            textposition="outside",
            textfont=dict(color=INK_SECONDARY, size=11),
            cliponaxis=False,
        )
    )
    fig.update_xaxes(title="Pangsa pendapatan (%)", showgrid=True, gridcolor=GRID, range=[0, float(cat["share_pct"].max()) * 1.22])
    fig.update_yaxes(showgrid=False)
    fig.update_layout(bargap=0.35)
    return _base_layout(fig, "Pangsa pendapatan per kategori", height=420)


def fig_country_bar(country: pd.DataFrame, n: int = 10, exclude_uk: bool = True) -> go.Figure:
    data = country[country["country"] != "United Kingdom"] if exclude_uk else country
    data = data.head(n).iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=data["revenue"],
            y=data["country"],
            orientation="h",
            marker=dict(color=SERIES[0]),
            customdata=data[["share_pct", "invoices", "aov"]].to_numpy(),
            hovertemplate="<b>%{y}</b><br>Pendapatan: GBP %{x:,.0f} (%{customdata[0]:.2f}%)<br>Invoice: %{customdata[1]:,}<br>AOV: GBP %{customdata[2]:,.0f}<extra></extra>",
        )
    )
    uk_share = country.loc[country["country"] == "United Kingdom", "share_pct"]
    note = f" (UK = {uk_share.iloc[0]:.1f}%, tidak ditampilkan)" if exclude_uk and not uk_share.empty else ""
    fig.update_xaxes(title="Pendapatan (GBP)", tickformat="~s", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(bargap=0.35)
    return _base_layout(fig, f"Pasar ekspor terbesar{note}", height=400)


def fig_country_map(country: pd.DataFrame) -> go.Figure:
    """Peta choropleth pendapatan per negara (skala log agar UK tidak menenggelamkan yang lain)."""
    import numpy as np

    data = country.copy()
    data["log_revenue"] = np.log10(data["revenue"].clip(lower=1))
    fig = go.Figure(
        go.Choropleth(
            locations=data["map_name"],
            locationmode="country names",
            z=data["log_revenue"],
            customdata=data[["country", "revenue", "invoices"]].to_numpy(),
            colorscale=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
            marker_line_color="white",
            marker_line_width=0.5,
            colorbar=dict(title="log10 GBP", thickness=10, len=0.6, tickfont=dict(color=INK_MUTED)),
            hovertemplate="<b>%{customdata[0]}</b><br>Pendapatan: GBP %{customdata[1]:,.0f}<br>Invoice: %{customdata[2]:,}<extra></extra>",
        )
    )
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth", bgcolor="rgba(0,0,0,0)", landcolor="#f0efec", showcountries=True, countrycolor="white")
    fig = _base_layout(fig, "Pendapatan per negara (skala log)", height=420)
    fig.update_layout(margin=dict(l=0, r=0, t=48, b=0))
    return fig


def fig_rfm_segments(seg: pd.DataFrame) -> go.Figure:
    """Dua ukuran per segmen (pangsa pelanggan vs pangsa pendapatan) dalam satu sumbu persen."""
    seg = seg.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=seg["segment"], x=seg["customers_share_pct"], orientation="h", name="Pangsa pelanggan", marker=dict(color=SERIES[0]), customdata=seg[["customers"]].to_numpy(), hovertemplate="<b>%{y}</b><br>%{x:.1f}% pelanggan (%{customdata[0]:,})<extra></extra>"))
    fig.add_trace(go.Bar(y=seg["segment"], x=seg["revenue_share_pct"], orientation="h", name="Pangsa pendapatan", marker=dict(color=SERIES[1]), customdata=seg[["revenue"]].to_numpy(), hovertemplate="<b>%{y}</b><br>%{x:.1f}% pendapatan (GBP %{customdata[0]:,.0f})<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08)
    fig.update_xaxes(title="Persen", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(showgrid=False)
    return _base_layout(fig, "Segmen RFM: pangsa pelanggan vs pangsa pendapatan", height=420)


def fig_day_hour_heatmap(matrix: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=[f"{h:02d}" for h in matrix.columns],
            y=list(matrix.index),
            colorscale=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
            xgap=2,
            ygap=2,
            colorbar=dict(title="Invoice", thickness=10, tickfont=dict(color=INK_MUTED)),
            hovertemplate="%{y} pukul %{x}:00<br>Invoice: %{z:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Jam", side="bottom")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _base_layout(fig, "Jumlah invoice per hari dan jam", height=330)
