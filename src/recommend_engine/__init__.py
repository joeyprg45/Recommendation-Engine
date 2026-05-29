from __future__ import annotations

from .cache import ProfileCache, repository_fingerprint
from .chat_context import build_member_chat_context, build_repository_chat_context
from .analysis import infer_member_profile, infer_member_profile_cached, infer_member_profiles, rank_members_by_skill, summarize_repository
from .demo_data import build_demo_repository
from .models import CommitRecord, IssueRecord, Member, MemberProfile, ProjectRepository, SkillSignal
from .preprocessing import clean_text, normalize_commit, normalize_issue, normalize_repository

__all__ = [
    "build_demo_repository",
    "build_member_chat_context",
    "build_repository_chat_context",
    "infer_member_profile",
    "infer_member_profile_cached",
    "infer_member_profiles",
    "rank_members_by_skill",
    "summarize_repository",
    "ProfileCache",
    "repository_fingerprint",
    "clean_text",
    "normalize_commit",
    "normalize_issue",
    "normalize_repository",
    "CommitRecord",
    "IssueRecord",
    "Member",
    "MemberProfile",
    "ProjectRepository",
    "SkillSignal",
]
