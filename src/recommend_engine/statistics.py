from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt


@dataclass(frozen=True)
class TestResult:
    statistic: float
    p_value: float
    significant: bool
    test_name: str


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def two_sample_t_test(a: list[float], b: list[float], alpha: float = 0.05) -> TestResult:
    if len(a) < 2 or len(b) < 2:
        return TestResult(0.0, 1.0, False, "t_test")

    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    var_a = sum((x - mean_a) ** 2 for x in a) / (len(a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (len(b) - 1)
    denom = sqrt((var_a / len(a)) + (var_b / len(b)))
    if denom == 0:
        return TestResult(0.0, 1.0, False, "t_test")

    t_stat = (mean_a - mean_b) / denom
    p_value = min(1.0, max(0.0, 2.0 * (1.0 - _normal_cdf(abs(t_stat)))))
    return TestResult(t_stat, p_value, p_value < alpha, "t_test")


def mann_whitney_u_test(a: list[float], b: list[float], alpha: float = 0.05) -> TestResult:
    if not a or not b:
        return TestResult(0.0, 1.0, False, "mann_whitney_u")

    combined = [(value, 0) for value in a] + [(value, 1) for value in b]
    combined.sort(key=lambda item: item[0])

    rank_sum_a = 0.0
    rank = 1
    for _, group in combined:
        if group == 0:
            rank_sum_a += rank
        rank += 1

    n1 = len(a)
    n2 = len(b)
    u1 = rank_sum_a - (n1 * (n1 + 1) / 2)
    mean_u = (n1 * n2) / 2
    std_u = sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    if std_u == 0:
        return TestResult(0.0, 1.0, False, "mann_whitney_u")

    z = (u1 - mean_u) / std_u
    p_value = min(1.0, max(0.0, 2.0 * (1.0 - _normal_cdf(abs(z)))))
    return TestResult(u1, p_value, p_value < alpha, "mann_whitney_u")


def estimate_minimum_sample_size(effect_size: float, alpha: float = 0.05, power: float = 0.8) -> int:
    effect_size = max(effect_size, 1e-6)
    z_alpha = 1.96 if alpha <= 0.05 else 1.64
    z_beta = 0.84 if power >= 0.8 else 1.04
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return max(20, int(n + 0.999))
