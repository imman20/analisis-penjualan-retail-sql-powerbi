"""Fungsi statistik untuk uji A/B dua kelompok.

Dirancang agar hasil setiap uji dikembalikan sebagai ``dict`` yang rapi,
sehingga gampang ditampilkan di notebook maupun diuji dengan pytest.

Uji yang tersedia:

* ``welch_ttest``        : perbandingan rata-rata (mis. nilai keranjang) tanpa
                           asumsi varians sama; dilengkapi interval kepercayaan
                           selisih rata-rata dan ukuran efek Cohen's d.
* ``proportion_test``    : perbandingan proporsi (mis. tingkat retur, tingkat
                           konversi pembelian ulang) dengan uji chi-square dan
                           interval kepercayaan selisih proporsi.
* ``bootstrap_mean_diff``: alternatif nonparametrik untuk interval kepercayaan
                           saat distribusi sangat miring (umum pada nilai keranjang).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats


@dataclass
class MeanTestResult:
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    diff: float
    relative_lift: float
    t_stat: float
    df: float
    p_value: float
    ci_low: float
    ci_high: float
    cohens_d: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class ProportionTestResult:
    n_a: int
    n_b: int
    successes_a: int
    successes_b: int
    rate_a: float
    rate_b: float
    diff: float
    relative_lift: float
    chi2: float
    p_value: float
    ci_low: float
    ci_high: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Ukuran efek Cohen's d dengan simpangan baku gabungan (pooled).

    Interpretasi umum: |d| ~ 0,2 kecil, ~ 0,5 sedang, ~ 0,8 besar.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a, n_b = len(a), len(b)
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    pooled_sd = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    if pooled_sd == 0:
        return 0.0
    return float((b.mean() - a.mean()) / pooled_sd)


def welch_ttest(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> MeanTestResult:
    """Uji t Welch dua sisi: H0 rata-rata A = rata-rata B.

    Welch dipakai (bukan Student) karena varians kedua kelompok hampir pasti
    berbeda pada data transaksi. Interval kepercayaan selisih dihitung dengan
    derajat bebas Welch-Satterthwaite.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a, n_b = len(a), len(b)
    mean_a, mean_b = a.mean(), b.mean()
    se_a2, se_b2 = a.var(ddof=1) / n_a, b.var(ddof=1) / n_b
    se_diff = np.sqrt(se_a2 + se_b2)
    df = (se_a2 + se_b2) ** 2 / (se_a2**2 / (n_a - 1) + se_b2**2 / (n_b - 1))
    t_stat, p_value = stats.ttest_ind(b, a, equal_var=False)
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    diff = mean_b - mean_a
    return MeanTestResult(
        n_a=int(n_a),
        n_b=int(n_b),
        mean_a=float(mean_a),
        mean_b=float(mean_b),
        diff=float(diff),
        relative_lift=float(diff / mean_a) if mean_a != 0 else float("nan"),
        t_stat=float(t_stat),
        df=float(df),
        p_value=float(p_value),
        ci_low=float(diff - t_crit * se_diff),
        ci_high=float(diff + t_crit * se_diff),
        cohens_d=cohens_d(a, b),
    )


def proportion_test(successes_a: int, n_a: int, successes_b: int, n_b: int, alpha: float = 0.05) -> ProportionTestResult:
    """Uji chi-square 2x2 (tanpa koreksi Yates) untuk dua proporsi.

    Interval kepercayaan selisih proporsi memakai pendekatan normal (Wald),
    memadai untuk ukuran sampel ribuan seperti pada data ini.
    """
    table = np.array([[successes_a, n_a - successes_a], [successes_b, n_b - successes_b]], dtype=float)
    chi2, p_value, _, _ = stats.chi2_contingency(table, correction=False)
    rate_a, rate_b = successes_a / n_a, successes_b / n_b
    diff = rate_b - rate_a
    se = np.sqrt(rate_a * (1 - rate_a) / n_a + rate_b * (1 - rate_b) / n_b)
    z = stats.norm.ppf(1 - alpha / 2)
    return ProportionTestResult(
        n_a=int(n_a),
        n_b=int(n_b),
        successes_a=int(successes_a),
        successes_b=int(successes_b),
        rate_a=float(rate_a),
        rate_b=float(rate_b),
        diff=float(diff),
        relative_lift=float(diff / rate_a) if rate_a != 0 else float("nan"),
        chi2=float(chi2),
        p_value=float(p_value),
        ci_low=float(diff - z * se),
        ci_high=float(diff + z * se),
    )


def bootstrap_mean_diff(a: np.ndarray, b: np.ndarray, n_boot: int = 5000, alpha: float = 0.05, seed: int = 42) -> tuple[float, float]:
    """Interval kepercayaan persentil bootstrap untuk selisih rata-rata (B - A)."""
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean()
    low, high = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(low), float(high)


def interpret_p(p_value: float, alpha: float = 0.05) -> str:
    """Kalimat interpretasi singkat untuk ditampilkan di notebook/laporan."""
    if p_value < alpha:
        return f"signifikan secara statistik (p = {p_value:.4f} < {alpha})"
    return f"tidak signifikan secara statistik (p = {p_value:.4f} >= {alpha})"


def interpret_effect_size(d: float) -> str:
    """Kategori ukuran efek menurut ambang batas Cohen."""
    magnitude = abs(d)
    if magnitude < 0.2:
        return "dapat diabaikan"
    if magnitude < 0.5:
        return "kecil"
    if magnitude < 0.8:
        return "sedang"
    return "besar"
