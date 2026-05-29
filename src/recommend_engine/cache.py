from __future__ import annotations

import json
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from .models import Member, MemberProfile, ProjectRepository


class ProfileCache:
    def __init__(self, cache_dir: str | Path = ".cache/recommend_engine") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, repository: ProjectRepository, member_id: str) -> Path:
        digest = repository_fingerprint(repository)
        return self.cache_dir / f"{repository.repository_name.replace('/', '_')}__{member_id}__{digest}.json"

    def load(self, repository: ProjectRepository, member_id: str) -> MemberProfile | None:
        cache_path = self._cache_path(repository, member_id)
        if not cache_path.exists():
            return None

        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        member = Member(**payload["member"])
        return MemberProfile(
            member=member,
            signals=[],
            scores=dict(payload.get("scores", {})),
            summary=payload.get("summary", ""),
        )

    def save(self, repository: ProjectRepository, profile: MemberProfile) -> None:
        cache_path = self._cache_path(repository, profile.member.member_id)
        payload = {
            "member": asdict(profile.member),
            "scores": profile.scores,
            "summary": profile.summary,
        }
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def repository_fingerprint(repository: ProjectRepository) -> str:
    payload = {
        "repository_name": repository.repository_name,
        "issues": [issue.issue_id for issue in repository.issues],
        "commits": [commit.sha for commit in repository.commits],
        "task_owners": sorted(repository.task_owners.items()),
    }
    digest = sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:16]
