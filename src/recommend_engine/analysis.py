from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
import re

from .demo_data import build_demo_repository
from .models import CommitRecord, IssueRecord, MemberProfile, ProjectRepository, SkillSignal
from .preprocessing import normalize_repository


SKILL_ALIASES: dict[str, str] = {
    "modeling": "ranking_modeling",
    "ranking": "ranking_modeling",
    "ml": "machine_learning",
    "cosmosdb": "cloud_data_architecture",
    "infra": "cloud_data_architecture",
    "feature-store": "feature_store",
    "api": "backend_api_design",
    "fastapi": "backend_api_design",
    "architecture": "system_architecture",
    "preprocessing": "data_quality",
    "data-quality": "data_quality",
    "embeddings": "embedding_systems",
    "redis": "caching_and_performance",
    "azure-openai": "azure_openai_integration",
    "hybrid": "hybrid_ranking",
    "experiment": "experimentation",
    "evaluation": "experimentation",
    "stats": "statistics",
    "performance": "performance_engineering",
    "refactor": "refactoring",
}

KEYWORD_ALIASES: tuple[tuple[str, str], ...] = (
    ("ndcg", "ranking_modeling"),
    ("lambdarank", "ranking_modeling"),
    ("lightgbm", "ranking_modeling"),
    ("collaborative filtering", "ranking_modeling"),
    ("feature store", "feature_store"),
    ("cosmosdb", "cloud_data_architecture"),
    ("fastapi", "backend_api_design"),
    ("plugin", "system_architecture"),
    ("pd.isna", "data_quality"),
    ("outlier", "data_quality"),
    ("embedding", "embedding_systems"),
    ("redis", "caching_and_performance"),
    ("azure openai", "azure_openai_integration"),
    ("hybridreranker", "hybrid_ranking"),
    ("alpha", "hybrid_ranking"),
    ("ctr", "experimentation"),
    ("mann-whitney", "statistics"),
    ("t-test", "statistics"),
    ("latency", "performance_engineering"),
)

SOURCE_WEIGHTS: dict[str, float] = {
    "issue_label": 2.0,
    "issue_text": 0.9,
    "commit_message": 2.5,
    "commit_evidence": 3.0,
    "changed_file": 1.2,
    "task_ownership": 0.5,
}


def _normalize(text: str) -> str:
    normalized = text.lower()
    normalized = normalized.replace("/", " ")
    normalized = re.sub(r"[^\w\s\-\.]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _canonical_skill(name: str) -> str:
    return SKILL_ALIASES.get(name, name)


def _skill_from_text(text: str) -> list[str]:
    normalized = _normalize(text)
    skills: list[str] = []
    for keyword, skill in KEYWORD_ALIASES:
        if keyword in normalized:
            skills.append(skill)
    return skills


def extract_skills_from_text(text: str) -> list[str]:
    return list(dict.fromkeys(_skill_from_text(text)))


def _append_signal(signals: list[SkillSignal], skill: str, source: str, weight: float, detail: str) -> None:
    signals.append(SkillSignal(skill=skill, source=source, weight=weight, detail=detail))


def _member_lookup(repository: ProjectRepository) -> dict[str, str]:
    return {member.member_id: member.github_handle for member in repository.members}


def _issue_owner_map(repository: ProjectRepository) -> dict[str, str]:
    return {issue.related_task or issue.issue_id: issue.assignee or "" for issue in repository.issues}


def _signals_from_issue(issue: IssueRecord) -> list[SkillSignal]:
    signals: list[SkillSignal] = []
    for label in issue.labels:
        skill = _canonical_skill(label)
        _append_signal(signals, skill, "issue_label", SOURCE_WEIGHTS["issue_label"], f"{issue.issue_id}:{label}")

    for skill in _skill_from_text(f"{issue.title} {issue.body}"):
        _append_signal(signals, skill, "issue_text", SOURCE_WEIGHTS["issue_text"], f"{issue.issue_id}:{issue.title}")

    return signals


def _signals_from_commit(commit: CommitRecord) -> list[SkillSignal]:
    signals: list[SkillSignal] = []
    for skill in _skill_from_text(commit.message):
        _append_signal(signals, skill, "commit_message", SOURCE_WEIGHTS["commit_message"], commit.message)

    for skill in _skill_from_text(commit.evidence):
        _append_signal(signals, skill, "commit_evidence", SOURCE_WEIGHTS["commit_evidence"], commit.evidence)

    for file_name in commit.changed_files:
        for skill in _skill_from_text(file_name):
            _append_signal(signals, skill, "changed_file", SOURCE_WEIGHTS["changed_file"], file_name)

    return signals


def infer_member_profiles(repository: ProjectRepository | None = None) -> list[MemberProfile]:
    repository = normalize_repository(repository or build_demo_repository())
    issues_by_task = {issue.related_task or issue.issue_id: issue for issue in repository.issues}
    member_signals: dict[str, list[SkillSignal]] = defaultdict(list)

    for issue in repository.issues:
        if issue.assignee:
            member_signals[issue.assignee].extend(_signals_from_issue(issue))
            _append_signal(
                member_signals[issue.assignee],
                "task_ownership",
                "task_ownership",
                SOURCE_WEIGHTS["task_ownership"],
                f"assigned:{issue.issue_id}",
            )

    for commit in repository.commits:
        owner = repository.task_owners.get(commit.task_id)
        if not owner and commit.task_id in issues_by_task:
            owner = issues_by_task[commit.task_id].assignee
        if owner:
            member_signals[owner].extend(_signals_from_commit(commit))

    profiles: list[MemberProfile] = []
    for member in repository.members:
        signals = member_signals.get(member.member_id, [])
        scores: dict[str, float] = defaultdict(float)
        for signal in signals:
            scores[signal.skill] += signal.weight

        summary = _summarize_member(member.name, signals, scores)
        profiles.append(MemberProfile(member=member, signals=list(signals), scores=dict(sorted(scores.items(), key=lambda item: (-item[1], item[0]))), summary=summary))

    return profiles


def infer_member_profile(repository: ProjectRepository | None, member_id: str) -> MemberProfile:
    repository = repository or build_demo_repository()
    for profile in infer_member_profiles(repository):
        if profile.member.member_id == member_id or profile.member.github_handle == member_id:
            return profile
    raise KeyError(f"member not found: {member_id}")


def rank_members_by_skill(repository: ProjectRepository | None, skill: str) -> list[MemberProfile]:
    canonical = _canonical_skill(skill)
    profiles = infer_member_profiles(repository)
    return sorted(profiles, key=lambda profile: profile.scores.get(canonical, 0.0), reverse=True)


def summarize_repository(repository: ProjectRepository | None = None) -> dict[str, object]:
    repository = normalize_repository(repository or build_demo_repository())
    profiles = infer_member_profiles(repository)
    total_signals = sum(len(profile.signals) for profile in profiles)
    top_profiles = sorted(profiles, key=lambda profile: sum(profile.scores.values()), reverse=True)
    return {
        "repository_name": repository.repository_name,
        "overview": repository.overview,
        "member_count": len(repository.members),
        "issue_count": len(repository.issues),
        "commit_count": len(repository.commits),
        "signal_count": total_signals,
        "top_profiles": [
            {
                "member": profile.member.name,
                "handle": profile.member.github_handle,
                "top_skills": list(profile.scores.items())[:3],
            }
            for profile in top_profiles[:3]
        ],
    }


def _summarize_member(member_name: str, signals: list[SkillSignal], scores: dict[str, float]) -> str:
    if not signals:
        return "履歴からは明確なスキルシグナルが見つからない。"

    strongest = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:3]
    signal_sources = ", ".join(sorted({signal.source for signal in signals}))
    skill_text = ", ".join(f"{skill}({score:.1f})" for skill, score in strongest)
    return f"{member_name} は {skill_text} を中心に強い。主な根拠は {signal_sources}。"


def profile_to_dict(profile: MemberProfile) -> dict[str, object]:
    return asdict(profile)
