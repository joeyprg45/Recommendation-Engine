from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Member:
    member_id: str
    name: str
    github_handle: str
    role: str
    monthly_cost: int


@dataclass(frozen=True)
class IssueRecord:
    issue_id: str
    title: str
    body: str
    labels: tuple[str, ...] = ()
    assignee: str | None = None
    related_task: str | None = None
    status: str = "open"


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    message: str
    author_name: str
    author_handle: str
    task_id: str
    changed_files: tuple[str, ...] = ()
    evidence: str = ""


@dataclass(frozen=True)
class ProjectRepository:
    repository_name: str
    description: str
    overview: str
    members: tuple[Member, ...]
    issues: tuple[IssueRecord, ...]
    commits: tuple[CommitRecord, ...]


@dataclass
class SkillSignal:
    skill: str
    source: str
    weight: float
    detail: str


@dataclass
class MemberProfile:
    member: Member
    signals: list[SkillSignal] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    summary: str = ""
