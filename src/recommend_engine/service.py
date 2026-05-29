from __future__ import annotations

from .ab_testing import ABTestReport, ExperimentGroup, ExperimentMetrics, run_ab_test
from .analysis import infer_member_profile_cached, rank_members_by_skill, summarize_repository
from .cache import ProfileCache
from .chat_context import build_member_chat_context, build_repository_chat_context
from .demo_data import build_demo_repository
from .hybrid_reranker import HybridReranker
from .models import ProjectRepository


class RecommendationService:
    def __init__(
        self,
        repository: ProjectRepository | None = None,
        reranker: HybridReranker | None = None,
        cache: ProfileCache | None = None,
    ) -> None:
        self.repository = repository or build_demo_repository()
        self.reranker = reranker or HybridReranker()
        self.cache = cache or ProfileCache()

    def repository_summary(self) -> dict[str, object]:
        return summarize_repository(self.repository)

    def member_profile(self, member_id: str):
        return infer_member_profile_cached(self.repository, member_id, cache=self.cache)

    def member_context(self, member_id: str, question: str | None = None) -> str:
        return build_member_chat_context(self.repository, member_id, question=question)

    def repository_context(self, question: str | None = None) -> str:
        return build_repository_chat_context(self.repository, question=question)

    def rank_members(self, skill: str):
        return rank_members_by_skill(self.repository, skill)

    def evaluate_hybrid_release(self) -> ABTestReport:
        baseline = ExperimentGroup(
            name="lightgbm_baseline",
            metrics=ExperimentMetrics(
                ctr=[0.112, 0.118, 0.109, 0.114, 0.111, 0.116, 0.113, 0.117],
                conversion=[0.032, 0.031, 0.030, 0.033, 0.031, 0.032, 0.031, 0.032],
                ndcg=[0.61, 0.60, 0.62, 0.60, 0.61, 0.59, 0.61, 0.60],
            ),
        )
        candidate = ExperimentGroup(
            name="hybrid_reranker",
            metrics=ExperimentMetrics(
                ctr=[0.125, 0.129, 0.127, 0.124, 0.128, 0.126, 0.130, 0.127],
                conversion=[0.036, 0.037, 0.035, 0.036, 0.037, 0.036, 0.038, 0.036],
                ndcg=[0.78, 0.79, 0.80, 0.78, 0.79, 0.77, 0.79, 0.80],
            ),
        )
        return run_ab_test(baseline=baseline, candidate=candidate, effect_size=0.1)
