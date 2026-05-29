from __future__ import annotations

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
