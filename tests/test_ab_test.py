"""Pengujian fungsi metrik uji A/B."""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.analysis.ab_test import (
    bootstrap_mean_diff,
    cohens_d,
    interpret_effect_size,
    interpret_p,
    proportion_test,
    welch_ttest,
)


def test_welch_matches_scipy_and_ci_contains_true_diff():
    rng = np.random.default_rng(42)
    a = rng.normal(100, 20, 500)
    b = rng.normal(110, 30, 400)
    result = welch_ttest(a, b)
    t_scipy, p_scipy = stats.ttest_ind(b, a, equal_var=False)
    assert abs(result.t_stat - t_scipy) < 1e-9
    assert abs(result.p_value - p_scipy) < 1e-9
    assert result.ci_low < 10 < result.ci_high
    assert result.p_value < 0.01
    assert result.diff == result.mean_b - result.mean_a


def test_welch_on_identical_distributions_is_not_significant():
    rng = np.random.default_rng(7)
    a = rng.normal(50, 5, 1000)
    b = rng.normal(50, 5, 1000)
    result = welch_ttest(a, b)
    assert result.p_value > 0.05
    assert result.ci_low < 0 < result.ci_high
    assert abs(result.cohens_d) < 0.1


def test_cohens_d_known_value():
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    b = np.array([3.0, 4.0, 5.0, 6.0, 7.0])
    # Selisih rata-rata 2, simpangan baku gabungan sqrt(2.5) -> d = 1.2649
    assert abs(cohens_d(a, b) - 2 / np.sqrt(2.5)) < 1e-9
    assert cohens_d(a, a) == 0.0


def test_proportion_test_matches_scipy_chi2():
    result = proportion_test(successes_a=120, n_a=2000, successes_b=170, n_b=2100)
    chi2, p, _, _ = stats.chi2_contingency([[120, 1880], [170, 1930]], correction=False)
    assert abs(result.chi2 - chi2) < 1e-9
    assert abs(result.p_value - p) < 1e-9
    assert abs(result.rate_a - 0.06) < 1e-12
    assert result.ci_low < result.diff < result.ci_high


def test_proportion_test_equal_rates_not_significant():
    result = proportion_test(100, 1000, 100, 1000)
    assert result.diff == 0.0
    assert result.p_value > 0.99


def test_bootstrap_ci_brackets_difference():
    rng = np.random.default_rng(3)
    a = rng.exponential(10, 300)
    b = rng.exponential(13, 300)
    low, high = bootstrap_mean_diff(a, b, n_boot=500)
    assert low < b.mean() - a.mean() < high


def test_interpretation_helpers():
    assert "signifikan" in interpret_p(0.01) and "tidak" not in interpret_p(0.01)
    assert interpret_p(0.3).startswith("tidak signifikan")
    assert interpret_effect_size(0.1) == "dapat diabaikan"
    assert interpret_effect_size(-0.3) == "kecil"
    assert interpret_effect_size(0.6) == "sedang"
    assert interpret_effect_size(1.2) == "besar"
