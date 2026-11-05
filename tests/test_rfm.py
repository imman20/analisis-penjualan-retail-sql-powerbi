"""Pengujian fungsi RFM dan segmentasi."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.analysis.rfm import (
    cluster_profile,
    compute_rfm,
    fit_kmeans,
    prepare_cluster_features,
    score_rfm,
    segment_from_scores,
    select_k_by_silhouette,
)


def _sales_frame() -> pd.DataFrame:
    rows = [
        (1, "A1", "2011-01-01", 100.0),
        (1, "A2", "2011-03-01", 50.0),
        (1, "A2", "2011-03-01", 25.0),  # baris kedua di invoice yang sama
        (2, "B1", "2010-06-15", 10.0),
        (3, "C1", "2011-03-10", 500.0),
        (None, "G1", "2011-03-10", 999.0),  # tamu, harus diabaikan
    ]
    df = pd.DataFrame(rows, columns=["customer_id", "invoice_no", "invoice_date", "line_total"])
    df["customer_id"] = df["customer_id"].astype("Int64")
    return df


def test_compute_rfm_values():
    rfm = compute_rfm(_sales_frame(), snapshot_date="2011-03-11")
    rfm = rfm.set_index("customer_id")
    assert len(rfm) == 3  # tamu diabaikan
    assert rfm.loc[1, "frequency"] == 2  # dua invoice berbeda
    assert rfm.loc[1, "monetary"] == 175.0
    assert rfm.loc[1, "recency_days"] == 10
    assert rfm.loc[2, "recency_days"] == (pd.Timestamp("2011-03-11") - pd.Timestamp("2010-06-15")).days
    assert rfm.loc[3, "recency_days"] == 1


def test_default_snapshot_is_day_after_last_purchase():
    rfm = compute_rfm(_sales_frame()).set_index("customer_id")
    assert rfm.loc[3, "recency_days"] == 1


def test_score_rfm_produces_scores_in_range_and_segments():
    rng = np.random.default_rng(0)
    rfm = pd.DataFrame(
        {
            "customer_id": range(100),
            "recency_days": rng.integers(1, 400, 100),
            "frequency": rng.integers(1, 30, 100),
            "monetary": rng.gamma(2.0, 500.0, 100),
        }
    )
    scored = score_rfm(rfm)
    for col in ["r_score", "f_score", "m_score"]:
        assert scored[col].between(1, 5).all()
        # Kuantil: tiap skor mendapat ~20 pelanggan.
        assert scored[col].value_counts().min() >= 15
    assert scored["rfm_score"].str.len().eq(3).all()
    assert scored["segment"].notna().all()


def test_segment_rules():
    assert segment_from_scores(5, 5, 5) == "Champions"
    assert segment_from_scores(5, 1, 1) == "New Customers"
    assert segment_from_scores(1, 5, 5) == "At Risk"
    assert segment_from_scores(1, 1, 1) == "Lost"
    assert segment_from_scores(3, 4, 4) == "Loyal Customers"
    assert segment_from_scores(2, 1, 2) == "Hibernating"


def test_kmeans_pipeline_runs_and_profiles():
    rng = np.random.default_rng(1)
    rfm = pd.DataFrame(
        {
            "customer_id": range(200),
            "recency_days": np.concatenate([rng.integers(1, 30, 100), rng.integers(300, 600, 100)]),
            "frequency": np.concatenate([rng.integers(10, 40, 100), rng.integers(1, 3, 100)]),
            "monetary": np.concatenate([rng.normal(5000, 500, 100), rng.normal(100, 20, 100)]),
        }
    )
    X, _ = prepare_cluster_features(rfm)
    assert X.shape == (200, 3)
    scores = select_k_by_silhouette(X, [2, 3])
    assert scores["k"].tolist() == [2, 3]
    assert scores["silhouette"].between(-1, 1).all()
    # Dua kelompok yang sangat terpisah: k = 2 harus memberi silhouette tertinggi.
    assert scores.loc[scores["k"] == 2, "silhouette"].iloc[0] > scores.loc[scores["k"] == 3, "silhouette"].iloc[0]
    rfm["cluster"] = fit_kmeans(X, 2)
    profile = cluster_profile(rfm)
    assert len(profile) == 2
    assert abs(profile["share_customers"].sum() - 1.0) < 1e-6
