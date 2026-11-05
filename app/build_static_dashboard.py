"""Membangun dashboard HTML statis (tanpa server) dan screenshot PNG.

Keluaran:
* ``reports/dashboard.html``      - satu halaman HTML berisi KPI dan grafik Plotly
                                    interaktif (hover) yang bisa dibuka langsung di
                                    browser; plotly.js dimuat dari CDN agar file tetap
                                    ringan untuk dikomit.
* ``assets/dashboard_overview.png`` - screenshot area atas (KPI + tren) sebagai gambar
                                    hero README.
* ``assets/dashboard_produk.png``   - screenshot panel produk dan kategori.
* ``assets/dashboard_rfm.png``      - screenshot panel negara dan segmen RFM.

Screenshot memakai Chromium lewat Playwright. Untuk screenshot, salinan HTML
dengan plotly.js tertanam (bukan CDN) dibuat di folder sementara supaya tidak
membutuhkan koneksi internet. Jalankan: ``python -m app.build_static_dashboard``.
"""

from __future__ import annotations

import html
import os
import sys
import tempfile
from pathlib import Path

import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ASSETS_DIR, DASHBOARD_HTML, WAREHOUSE_DB  # noqa: E402
from src.dashboard_data import (  # noqa: E402
    category_share,
    compute_kpis,
    country_revenue,
    day_hour_matrix,
    load_flat,
    monthly_trend,
    rfm_segments,
    top_products,
)
from src.dashboard_figures import fig_category_share, fig_country_bar, fig_day_hour_heatmap, fig_monthly_trend, fig_rfm_segments, fig_top_products  # noqa: E402

CHROMIUM_CANDIDATES = [os.environ.get("CHROMIUM_PATH", ""), "/opt/pw-browsers/chromium", "/usr/bin/chromium", "/usr/bin/chromium-browser"]

CSS = """
:root {
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --border: rgba(11,11,11,0.10); --accent: #2a78d6; --good: #006300;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink); font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.wrap { max-width: 1400px; margin: 0 auto; padding: 24px 16px 40px; }
header { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px; margin-bottom: 18px; }
h1 { font-size: 24px; margin: 0; font-weight: 650; letter-spacing: -0.01em; }
.sub { color: var(--ink-2); font-size: 13px; }
.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 16px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
.kpi .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
.kpi .value { font-size: 26px; font-weight: 600; margin-top: 4px; }
.kpi .hint { color: var(--ink-2); font-size: 12px; margin-top: 2px; }
.grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin-bottom: 12px; }
.grid.two { grid-template-columns: 1.25fr 1fr; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 8px 10px 4px; }
footer { color: var(--muted); font-size: 12px; margin-top: 18px; }
@media (max-width: 900px) { .kpis { grid-template-columns: repeat(2, 1fr); } .grid.two { grid-template-columns: 1fr; } }
"""


def fmt_gbp(value: float) -> str:
    if abs(value) >= 1e6:
        return f"GBP {value / 1e6:,.2f} jt"
    if abs(value) >= 1e3:
        return f"GBP {value / 1e3:,.1f} rb"
    return f"GBP {value:,.0f}"


def build_html(include_plotlyjs: str | bool) -> str:
    """Merakit halaman dashboard; ``include_plotlyjs`` 'cdn' untuk repo, True untuk screenshot."""
    df = load_flat(WAREHOUSE_DB)
    kpi = compute_kpis(df)
    figs = {
        "tren": fig_monthly_trend(monthly_trend(df)),
        "produk": fig_top_products(top_products(df, 10)),
        "kategori": fig_category_share(category_share(df)),
        "negara": fig_country_bar(country_revenue(df), 10, exclude_uk=True),
        "rfm": fig_rfm_segments(rfm_segments(df)),
        "heatmap": fig_day_hour_heatmap(day_hour_matrix(df)),
    }
    first = True
    parts = {}
    for key, fig in figs.items():
        parts[key] = pio.to_html(fig, full_html=False, include_plotlyjs=include_plotlyjs if first else False, config={"displayModeBar": False, "responsive": True})
        first = False

    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    start = f"{df['full_date'].min():%d} {bulan[df['full_date'].min().month - 1]} {df['full_date'].min():%Y}"
    end = f"{df['full_date'].max():%d} {bulan[df['full_date'].max().month - 1]} {df['full_date'].max():%Y}"
    kpi_cards = [
        ("Pendapatan bersih", fmt_gbp(kpi["net_revenue"]), f"kotor {fmt_gbp(kpi['gross_revenue'])}, retur {fmt_gbp(kpi['returned_value'])}"),
        ("Invoice penjualan", f"{kpi['invoices']:,}", f"{kpi['units'] / 1e6:,.2f} jt unit terjual"),
        ("Pelanggan terdaftar", f"{kpi['customers']:,}", "di luar pelanggan tamu"),
        ("AOV", f"GBP {kpi['aov']:,.0f}", "rata-rata nilai per invoice"),
        ("Tingkat retur", f"{kpi['return_rate']:.1%}", "nilai retur / penjualan kotor"),
    ]
    kpi_html = "".join(f'<div class="kpi"><div class="label">{html.escape(label)}</div><div class="value">{html.escape(value)}</div><div class="hint">{html.escape(hint)}</div></div>' for label, value, hint in kpi_cards)

    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Penjualan Retail</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div id="hero">
  <header>
    <div>
      <h1>Dashboard Penjualan Retail</h1>
      <div class="sub">Online Retail II (UCI) &middot; {start} &ndash; {end} &middot; nilai dalam GBP &middot; dibuat otomatis oleh <code>app/build_static_dashboard.py</code></div>
    </div>
    <div class="sub">Versi interaktif dengan filter: <code>streamlit run app/dashboard.py</code></div>
  </header>
  <section id="overview">
    <div class="kpis">{kpi_html}</div>
    <div class="grid"><div class="card">{parts["tren"]}</div></div>
  </section>
  </div>
  <section id="produk" class="grid two">
    <div class="card">{parts["produk"]}</div>
    <div class="card">{parts["kategori"]}</div>
  </section>
  <section id="pelanggan" class="grid two">
    <div class="card">{parts["negara"]}</div>
    <div class="card">{parts["rfm"]}</div>
  </section>
  <section id="waktu" class="grid">
    <div class="card">{parts["heatmap"]}</div>
  </section>
  <footer>Sumber data: Chen, D. (2019). Online Retail II [Dataset]. UCI Machine Learning Repository (CC BY 4.0). Kategori produk ditetapkan dari kata kunci deskripsi; peringkat produk memakai pendapatan bersih (penjualan dikurangi retur).</footer>
</div>
</body>
</html>"""


def find_chromium() -> str | None:
    for candidate in CHROMIUM_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def take_screenshots(html_path: Path) -> None:
    """Screenshot bagian-bagian dashboard dengan Chromium headless (deviceScaleFactor 2)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[screenshot] playwright tidak terpasang; lewati screenshot.")
        return

    executable = find_chromium()
    launch_kwargs = {"executable_path": executable} if executable else {}
    targets = [("#hero", "dashboard_overview.png"), ("#produk", "dashboard_produk.png"), ("#pelanggan", "dashboard_rfm.png")]
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(**launch_kwargs)
        except Exception as exc:  # noqa: BLE001
            print(f"[screenshot] gagal menjalankan Chromium ({exc}); lewati screenshot.")
            return
        page = browser.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
        page.goto(html_path.as_uri())
        page.wait_for_selector(".plotly", timeout=60_000)
        page.wait_for_timeout(1500)  # beri waktu animasi Plotly selesai
        for selector, filename in targets:
            page.locator(selector).screenshot(path=str(ASSETS_DIR / filename))
            print(f"[screenshot] {ASSETS_DIR / filename}")
        page.screenshot(path=str(ASSETS_DIR / "dashboard_full.png"), full_page=True)
        print(f"[screenshot] {ASSETS_DIR / 'dashboard_full.png'}")
        browser.close()


def main() -> int:
    if not WAREHOUSE_DB.exists():
        print(f"Warehouse tidak ditemukan: {WAREHOUSE_DB}")
        return 1
    DASHBOARD_HTML.parent.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    DASHBOARD_HTML.write_text(build_html("cdn"), encoding="utf-8")
    print(f"[dashboard] {DASHBOARD_HTML} ({DASHBOARD_HTML.stat().st_size / 1e3:.0f} KB)")

    with tempfile.TemporaryDirectory() as tmp:
        offline = Path(tmp) / "dashboard_offline.html"
        offline.write_text(build_html(True), encoding="utf-8")
        take_screenshots(offline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
