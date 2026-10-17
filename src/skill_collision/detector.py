"""Detect collisions between skill names and descriptions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in text.replace("-", " ").split() if len(t) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _load_meta(skill_dir: Path) -> dict[str, Any] | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None
    meta["_dir"] = skill_dir.name
    return meta


def detect_collisions(root: Path, jaccard_threshold: float = 0.55) -> dict[str, Any]:
    root = root.resolve()
    skills: list[dict[str, Any]] = []
    for child in sorted(root.iterdir()):
        if child.is_dir():
            meta = _load_meta(child)
            if meta and meta.get("name"):
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

    return {"scanned": len(skills), "collisions": collisions}
