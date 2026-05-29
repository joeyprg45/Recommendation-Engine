import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "demo" / "github_mcp"
ISSUE_DIR = DEMO_ROOT / "raw" / "issues"
PUSH_DIR = DEMO_ROOT / "raw" / "pushes"
DERIVED_DIR = DEMO_ROOT / "derived"


SKILL_RULES = {
    "lightgbm": "ml_ranking",
    "lambdarank": "ml_ranking",
    "ndcg": "ml_evaluation",
    "cold-start": "cold_start_modeling",
    "cold_start": "cold_start_modeling",
    "cosmos": "data_platform",
    "redis": "serving_performance",
    "plugin": "software_architecture",
    "api": "backend_api",
    "ab": "experimentation",
    "test": "experimentation",
    "refactor": "maintainability",
    "fix": "data_quality",
    "preprocess": "data_quality",
    "embedding": "llm_embedding",
    "hybrid": "hybrid_recommendation",
}


def _load_json_files(path: Path):
    rows = []
    for fp in sorted(path.glob("*.json")):
        rows.append(json.loads(fp.read_text(encoding="utf-8")))
    return rows


def _scan_text_for_skills(text: str):
    text_l = text.lower()
    found = []
    for key, skill in SKILL_RULES.items():
        if key in text_l:
            found.append(skill)
    return found


def build_profiles():
    issues = _load_json_files(ISSUE_DIR)
    pushes = _load_json_files(PUSH_DIR)
    scores = {}

    for issue in issues:
        text = " ".join(
            [issue.get("title", ""), " ".join(issue.get("labels", [])), issue.get("acceptance_notes", "")]
        )
        issue_skills = _scan_text_for_skills(text)
        for actor in issue.get("assignees", []):
            scores.setdefault(actor, {})
            for sk in issue_skills:
                scores[actor][sk] = scores[actor].get(sk, 0) + 1

    for push in pushes:
        pusher = push.get("pusher")
        scores.setdefault(pusher, {})
        for c in push.get("commits", []):
            commit_skills = _scan_text_for_skills(c.get("message", ""))
            for sk in commit_skills:
                scores[pusher][sk] = scores[pusher].get(sk, 0) + 2

    profiles = []
    chat_context = []
    for member, member_scores in sorted(scores.items()):
        ranked = sorted(member_scores.items(), key=lambda x: x[1], reverse=True)
        top_skills = [name for name, _ in ranked[:5]]
        profiles.append(
            {
                "member": member,
                "top_skills": top_skills,
                "skill_scores": member_scores,
            }
        )
        chat_context.append(
            {
                "member": member,
                "summary": f"{member} shows strong evidence in: {', '.join(top_skills) if top_skills else 'unknown'}",
            }
        )

    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    (DERIVED_DIR / "member_skill_profiles.json").write_text(
        json.dumps(profiles, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    (DERIVED_DIR / "chat_context.json").write_text(
        json.dumps(chat_context, indent=2, ensure_ascii=True), encoding="utf-8"
    )


if __name__ == "__main__":
    build_profiles()
