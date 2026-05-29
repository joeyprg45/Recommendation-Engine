from __future__ import annotations

from dataclasses import replace

from .models import CommitRecord, IssueRecord, ProjectRepository


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def normalize_labels(labels: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for label in labels:
        cleaned = clean_text(label).lower()
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
    return tuple(normalized)


def normalize_issue(issue: IssueRecord) -> IssueRecord:
    return replace(
        issue,
        title=clean_text(issue.title),
        body=clean_text(issue.body),
        labels=normalize_labels(issue.labels),
        assignee=clean_text(issue.assignee) or None,
        related_task=clean_text(issue.related_task) or None,
        status=clean_text(issue.status).lower() or "open",
    )


def normalize_commit(commit: CommitRecord) -> CommitRecord:
    return replace(
        commit,
        sha=clean_text(commit.sha),
        message=clean_text(commit.message),
        author_name=clean_text(commit.author_name),
        author_handle=clean_text(commit.author_handle),
        task_id=clean_text(commit.task_id),
        changed_files=tuple(clean_text(file_name) for file_name in commit.changed_files if clean_text(file_name)),
        evidence=clean_text(commit.evidence),
    )


def normalize_repository(repository: ProjectRepository) -> ProjectRepository:
    return replace(
        repository,
        repository_name=clean_text(repository.repository_name),
        description=clean_text(repository.description),
        overview=clean_text(repository.overview),
        issues=tuple(normalize_issue(issue) for issue in repository.issues),
        commits=tuple(normalize_commit(commit) for commit in repository.commits),
        task_owners={clean_text(task_id): clean_text(member_id) for task_id, member_id in repository.task_owners.items() if clean_text(task_id) and clean_text(member_id)},
    )
