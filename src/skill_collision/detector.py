"""Detect collisions between skill names, descriptions, and trigger phrases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import re
import yaml


def _tokens(text: str) -> set[str]:
    """Tokenize for Jaccard. Strips punctuation and hyphens so 'json.' == 'json'."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower().replace("-", " "))
    return {t for t in cleaned.split() if len(t) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _extract_triggers(description: str) -> str:
    """Extract activation / trigger-oriented phrases from a description.

    Captures clauses that typically control when a skill fires
    (e.g. 'Use when the user...', 'Triggers on...', 'when the user needs...').
    """
    if not description or not isinstance(description, str):
        return ""
    patterns = [
        r"(?i)(?:use\s+(?:when|for|to)|when\s+the\s+user|triggers?\s+(?:on|when|for)|activation\s+(?:phrase|on|when))[^.]*\.?",
    ]
    found: list[str] = []
    for p in patterns:
        found.extend(re.findall(p, description))
    # Deduplicate while preserving order and join
    seen = set()
    unique = []
    for phrase in found:
        key = phrase.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(phrase.strip())
    return " ".join(unique)


def _load_meta(skill_dir: Path) -> dict[str, Any] | None:
    """Load frontmatter. Returns None on missing file; raises-like via special key on parse error."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {"_dir": skill_dir.name, "_error": "no frontmatter"}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"_dir": skill_dir.name, "_error": "malformed frontmatter"}
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        return {"_dir": skill_dir.name, "_error": f"yaml: {exc}"}
    meta["_dir"] = skill_dir.name
    return meta


def detect_collisions(
    root: Path,
    jaccard_threshold: float = 0.55,
    trigger_threshold: float = 0.40,
) -> dict[str, Any]:
    root = root.resolve()
    skills: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    for child in sorted(root.iterdir()):
        if child.is_dir():
            meta = _load_meta(child)
            if not meta:
                continue
            if meta.get("_error"):
                parse_errors.append({"dir": meta["_dir"], "error": meta["_error"]})
                continue
            if meta.get("name"):
                skills.append(meta)

    collisions: list[dict[str, Any]] = []
    names_seen: dict[str, str] = {}

    for s in skills:
        name = str(s["name"]).lower()
        if name in names_seen:
            collisions.append({
                "type": "exact-name",
                "a": names_seen[name],
                "b": s["_dir"],
                "detail": f"duplicate name '{name}'",
            })
        else:
            names_seen[name] = s["_dir"]

    for i, a in enumerate(skills):
        for b in skills[i + 1 :]:
            # Full description overlap
            da = _tokens(str(a.get("description", "")))
            db = _tokens(str(b.get("description", "")))
            score = _jaccard(da, db)
            if score >= jaccard_threshold:
                collisions.append({
                    "type": "description-overlap",
                    "a": a["_dir"],
                    "b": b["_dir"],
                    "detail": f"Jaccard={score:.2f}",
                })

            # Trigger-phrase overlap (activation language)
            ta = _tokens(_extract_triggers(str(a.get("description", ""))))
            tb = _tokens(_extract_triggers(str(b.get("description", ""))))
            tscore = _jaccard(ta, tb)
            if tscore >= trigger_threshold and ta and tb:
                collisions.append({
                    "type": "trigger-overlap",
                    "a": a["_dir"],
                    "b": b["_dir"],
                    "detail": f"Trigger Jaccard={tscore:.2f}",
                })

    return {"scanned": len(skills), "collisions": collisions, "parse_errors": parse_errors}
