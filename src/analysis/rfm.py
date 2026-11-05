"""Segmentasi pelanggan dengan RFM (Recency, Frequency, Monetary).

RFM dipilih karena mudah dijelaskan ke tim bisnis: setiap pelanggan dinilai
dari kapan terakhir belanja (R), seberapa sering (F), dan seberapa besar (M).
Modul ini menyediakan dua pendekatan yang saling melengkapi:

1. **Skor kuantil 1-5** per dimensi lalu pemetaan ke segmen bernama
   (Champions, Loyal, At Risk, dst.) - transparan dan langsung dapat dipakai
   tim pemasaran.
2. **KMeans** pada fitur RFM yang ditransformasi log dan distandardisasi,
   dengan jumlah klaster dipilih lewat skor silhouette - memberi segmen
   berbasis data sebagai pembanding.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def compute_rfm(sales: pd.DataFrame, snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Menghitung tabel RFM per pelanggan dari baris penjualan (tanpa retur).

    Parameter
    ---------
    sales : DataFrame dengan kolom ``customer_id``, ``invoice_no``,
            ``invoice_date``, ``line_total``. Baris tanpa ``customer_id`` diabaikan.
    snapshot_date : tanggal acuan recency; default = satu hari setelah transaksi
            terakhir agar pelanggan yang belanja di hari terakhir punya recency 1.
    """
    df = sales.dropna(subset=["customer_id"]).copy()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    if snapshot_date is None:
        snapshot_date = df["invoice_date"].max().normalize() + pd.Timedelta(days=1)
    snapshot_date = pd.Timestamp(snapshot_date)

    rfm = df.groupby("customer_id").agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice_no", "nunique"),
        monetary=("line_total", "sum"),
    )
    rfm["recency_days"] = (snapshot_date - rfm["last_purchase"].dt.normalize()).dt.days
    rfm = rfm.drop(columns="last_purchase").reset_index()
    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm[["customer_id", "recency_days", "frequency", "monetary"]]


def _quantile_score(series: pd.Series, ascending: bool, bins: int = 5) -> pd.Series:
    """Memberi skor 1..bins berdasarkan kuantil.

    ``rank(method="first")`` dipakai agar ``qcut`` tidak gagal saat banyak nilai
    kembar (mis. frequency = 1 untuk ribuan pelanggan).
    """
    ranked = series.rank(method="first", ascending=ascending)
    return pd.qcut(ranked, q=bins, labels=range(1, bins + 1)).astype(int)


def score_rfm(rfm: pd.DataFrame, bins: int = 5) -> pd.DataFrame:
    """Menambahkan skor R, F, M (1 = terburuk, 5 = terbaik) dan segmen bernama."""
    out = rfm.copy()
    # Recency: semakin kecil (baru belanja) semakin baik, maka urutan dibalik.
    out["r_score"] = _quantile_score(out["recency_days"], ascending=False, bins=bins)
    out["f_score"] = _quantile_score(out["frequency"], ascending=True, bins=bins)
    out["m_score"] = _quantile_score(out["monetary"], ascending=True, bins=bins)
    out["rfm_score"] = out["r_score"].astype(str) + out["f_score"].astype(str) + out["m_score"].astype(str)
    out["segment"] = [segment_from_scores(r, f, m) for r, f, m in zip(out["r_score"], out["f_score"], out["m_score"], strict=True)]
    return out


def segment_from_scores(r: int, f: int, m: int) -> str:
    """Aturan pemetaan skor ke segmen, diadaptasi dari praktik umum RFM.

    Rata-rata F dan M digabung sebagai "nilai" pelanggan, lalu disilangkan
    dengan recency. Aturan diurutkan dari segmen paling bernilai.
    """
    value = (f + m) / 2
    if r >= 4 and value >= 4:
        return "Champions"
    if r >= 3 and value >= 3.5:
        return "Loyal Customers"
    if r >= 4 and value < 2:
        return "New Customers"
    if r >= 3 and value < 3.5:
        return "Potential Loyalists"
    if r == 2 and value >= 3:
        return "Need Attention"
    if r <= 2 and value >= 4:
        return "At Risk"
    if r == 1 and value < 2:
        return "Lost"
    return "Hibernating"


def prepare_cluster_features(rfm: pd.DataFrame) -> tuple[np.ndarray, StandardScaler]:
    """Transformasi log1p + standardisasi agar skala R, F, M sebanding.

    Frequency dan monetary sangat miring ke kanan (sedikit pelanggan grosir
    besar); tanpa log, KMeans hanya akan memisahkan pencilan tersebut.
    """
    features = np.column_stack(
        [
            np.log1p(rfm["recency_days"].to_numpy(dtype=float)),
            np.log1p(rfm["frequency"].to_numpy(dtype=float)),
            np.log1p(rfm["monetary"].clip(lower=0).to_numpy(dtype=float)),
        ]
    )
    scaler = StandardScaler()
    return scaler.fit_transform(features), scaler


def select_k_by_silhouette(X: np.ndarray, k_values: range | list[int] = range(2, 9), random_state: int = 42) -> pd.DataFrame:
    """Menghitung skor silhouette untuk tiap k; k terbaik = skor tertinggi."""
    rows = []
    for k in k_values:
        model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        labels = model.fit_predict(X)
        rows.append({"k": k, "silhouette": float(silhouette_score(X, labels)), "inertia": float(model.inertia_)})
    return pd.DataFrame(rows)


def fit_kmeans(X: np.ndarray, k: int, random_state: int = 42) -> np.ndarray:
    """Melatih KMeans dan mengembalikan label klaster."""
    model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    return model.fit_predict(X)


def cluster_profile(rfm: pd.DataFrame, label_col: str = "cluster") -> pd.DataFrame:
    """Profil ringkas tiap klaster: ukuran, rata-rata R/F/M, dan total belanja."""
    profile = rfm.groupby(label_col).agg(
        customers=("customer_id", "size"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
    )
    profile["share_customers"] = profile["customers"] / profile["customers"].sum()
    profile["share_revenue"] = profile["total_monetary"] / profile["total_monetary"].sum()
    return profile.round(2).reset_index()
