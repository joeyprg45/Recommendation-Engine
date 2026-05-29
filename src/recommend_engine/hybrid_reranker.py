from __future__ import annotations

from .models import MemberProfile


class HybridReranker:
    def __init__(self, alpha_floor: float = 0.25, alpha_ceiling: float = 0.8) -> None:
        self.alpha_floor = alpha_floor
        self.alpha_ceiling = alpha_ceiling

    def adaptive_alpha(self, profile: MemberProfile, target_skill: str) -> float:
        total_score = sum(profile.scores.values())
        skill_score = profile.scores.get(target_skill, 0.0)
        signal_count = len(profile.signals)

        if total_score <= 0:
            return self.alpha_floor

        concentration = skill_score / total_score
        evidence_density = min(signal_count / 12.0, 1.0)
        alpha = self.alpha_floor + (self.alpha_ceiling - self.alpha_floor) * max(concentration, evidence_density * 0.5)
        return max(self.alpha_floor, min(self.alpha_ceiling, alpha))

    def score(self, profile: MemberProfile, target_skill: str) -> float:
        direct_score = profile.scores.get(target_skill, 0.0)
        supporting_scores = [score for skill, score in profile.scores.items() if skill != target_skill]
        breadth_score = sum(supporting_scores) / max(len(supporting_scores), 1)
        alpha = self.adaptive_alpha(profile, target_skill)
        return alpha * direct_score + (1.0 - alpha) * breadth_score

    def rank(self, profiles: list[MemberProfile], target_skill: str) -> list[MemberProfile]:
        return sorted(profiles, key=lambda profile: (self.score(profile, target_skill), profile.member.name), reverse=True)
