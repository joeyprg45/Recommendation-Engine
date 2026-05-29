from __future__ import annotations

from dataclasses import dataclass

from .statistics import TestResult, estimate_minimum_sample_size, mann_whitney_u_test, two_sample_t_test


@dataclass(frozen=True)
class ExperimentMetrics:
    ctr: list[float]
    conversion: list[float]
    ndcg: list[float]


@dataclass(frozen=True)
class ExperimentGroup:
    name: str
    metrics: ExperimentMetrics


@dataclass(frozen=True)
class MetricComparison:
    metric: str
    baseline_mean: float
    candidate_mean: float
    delta: float
    t_test: TestResult
    mw_test: TestResult
    significant: bool


@dataclass(frozen=True)
class ABTestReport:
    baseline: str
    candidate: str
    min_sample_size: int
    comparisons: tuple[MetricComparison, ...]
    early_stop_recommended: bool


def run_ab_test(
    baseline: ExperimentGroup,
    candidate: ExperimentGroup,
    effect_size: float = 0.15,
    alpha: float = 0.05,
    power: float = 0.8,
) -> ABTestReport:
    min_sample = estimate_minimum_sample_size(effect_size=effect_size, alpha=alpha, power=power)

    comparisons = (
        _compare_metric("ctr", baseline.metrics.ctr, candidate.metrics.ctr, alpha=alpha),
        _compare_metric("conversion", baseline.metrics.conversion, candidate.metrics.conversion, alpha=alpha),
        _compare_metric("ndcg", baseline.metrics.ndcg, candidate.metrics.ndcg, alpha=alpha),
    )

    observed = min(
        len(baseline.metrics.ctr),
        len(candidate.metrics.ctr),
        len(baseline.metrics.conversion),
        len(candidate.metrics.conversion),
        len(baseline.metrics.ndcg),
        len(candidate.metrics.ndcg),
    )
    enough_samples = observed >= min_sample
    significant_wins = sum(1 for comparison in comparisons if comparison.significant and comparison.delta > 0)
    early_stop = enough_samples and significant_wins >= 2

    return ABTestReport(
        baseline=baseline.name,
        candidate=candidate.name,
        min_sample_size=min_sample,
        comparisons=comparisons,
        early_stop_recommended=early_stop,
    )


def _compare_metric(metric: str, baseline: list[float], candidate: list[float], alpha: float) -> MetricComparison:
    base_mean = _mean(baseline)
    cand_mean = _mean(candidate)
    t_result = two_sample_t_test(candidate, baseline, alpha=alpha)
    mw_result = mann_whitney_u_test(candidate, baseline, alpha=alpha)
    significant = t_result.significant and mw_result.significant
    return MetricComparison(
        metric=metric,
        baseline_mean=base_mean,
        candidate_mean=cand_mean,
        delta=cand_mean - base_mean,
        t_test=t_result,
        mw_test=mw_result,
        significant=significant,
    )


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)
