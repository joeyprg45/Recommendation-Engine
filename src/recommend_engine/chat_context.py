from __future__ import annotations

from .analysis import extract_skills_from_text, infer_member_profile
from .models import MemberProfile, ProjectRepository, SkillSignal


def build_member_chat_context(repository: ProjectRepository, member_id: str, question: str | None = None) -> str:
    profile = infer_member_profile(repository, member_id)
    highlighted_skills = extract_skills_from_text(question or "") if question else []
    selected_signals = _select_signals(profile, highlighted_skills)

    lines = [
        f"対象メンバー: {profile.member.name} (@{profile.member.github_handle})",
        f"役割: {profile.member.role}",
        f"要約: {profile.summary}",
        "",
        "主要スキル:",
    ]

    for skill, score in list(profile.scores.items())[:5]:
        lines.append(f"- {skill}: {score:.1f}")

    if question:
        lines.extend(["", f"質問: {question}"])

    lines.extend(["", "関連根拠:"])
    for signal in selected_signals[:8]:
        lines.append(f"- [{signal.source}] {signal.skill} ({signal.weight:.1f}): {signal.detail}")

    return "\n".join(lines)


def build_repository_chat_context(repository: ProjectRepository, question: str | None = None) -> str:
    lines = [
        f"リポジトリ: {repository.repository_name}",
        f"説明: {repository.description}",
        f"概要: {repository.overview}",
        f"メンバー数: {len(repository.members)}",
        f"issue 数: {len(repository.issues)}",
        f"commit 数: {len(repository.commits)}",
    ]

    if question:
        lines.extend(["", f"質問: {question}"])

    return "\n".join(lines)


def _select_signals(profile: MemberProfile, highlighted_skills: list[str]) -> list[SkillSignal]:
    if not highlighted_skills:
        return sorted(profile.signals, key=lambda signal: (-signal.weight, signal.source, signal.skill))

    selected = [signal for signal in profile.signals if signal.skill in highlighted_skills]
    if selected:
        return sorted(selected, key=lambda signal: (-signal.weight, signal.source, signal.skill))

    return sorted(profile.signals, key=lambda signal: (-signal.weight, signal.source, signal.skill))
