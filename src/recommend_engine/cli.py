from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass

from .service import RecommendationService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recommend-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("repository", help="show repository summary")

    profile_parser = subparsers.add_parser("profile", help="show a member profile")
    profile_parser.add_argument("--member", required=True)

    context_parser = subparsers.add_parser("context", help="show chat context for a member")
    context_parser.add_argument("--member", required=True)
    context_parser.add_argument("--question", default=None)

    rank_parser = subparsers.add_parser("rank", help="rank members by skill")
    rank_parser.add_argument("--skill", required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = RecommendationService()

    if args.command == "repository":
        print(_to_pretty_json(service.repository_summary()))
        return

    if args.command == "profile":
        print(_profile_to_text(service.member_profile(args.member)))
        return

    if args.command == "context":
        print(service.member_context(args.member, question=args.question))
        return

    if args.command == "rank":
        print(_ranking_to_text(service.rank_members(args.skill), args.skill))
        return

    raise SystemExit(f"unknown command: {args.command}")


def _profile_to_text(profile) -> str:
    scores = sorted(profile.scores.items(), key=lambda item: (-item[1], item[0]))
    lines = [
        f"名前: {profile.member.name}",
        f"GitHub: @{profile.member.github_handle}",
        f"役割: {profile.member.role}",
        f"要約: {profile.summary}",
        "",
        "スコア:",
    ]
    for skill, score in scores:
        lines.append(f"- {skill}: {score:.1f}")
    return "\n".join(lines)


def _ranking_to_text(profiles, skill: str) -> str:
    lines = [f"skill={skill}"]
    for index, profile in enumerate(profiles, start=1):
        lines.append(f"{index}. {profile.member.name} (@{profile.member.github_handle}) - {profile.scores.get(skill, 0.0):.1f}")
    return "\n".join(lines)


def _to_pretty_json(payload) -> str:
    if is_dataclass(payload):
        payload = asdict(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
