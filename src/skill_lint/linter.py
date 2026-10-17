"""Static linter for SKILL.md files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# Frontmatter rules derived from agentskills / skill-creator constraints
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
FORBIDDEN_IN_DESC = (": ", "<", ">")

DANGEROUS_PATTERNS = [
    (r"(?i)eval\s*\(", "eval() call"),
    (r"(?i)exec\s*\(", "exec() call"),
    (r"(?i)os\.system\s*\(", "os.system call"),
    (r"(?i)subprocess\.(call|run|Popen)", "subprocess invocation"),
    (r"(?i)rm\s+-rf", "destructive rm -rf"),
    (r"(?i)curl\s+.*\|\s*(ba)?sh", "curl | sh pattern"),
]


def _load_skill_md(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    body = parts[2]
    return meta, body


def lint_skill_md(path: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    meta, body = _load_skill_md(path)

    # name
    name = meta.get("name")
    if not name:
        results.append({"check": "name-present", "ok": False, "message": "missing name in frontmatter"})
    else:
        results.append({"check": "name-present", "ok": True, "message": f"name={name}"})
        if not isinstance(name, str) or not NAME_RE.match(name):
            results.append({"check": "name-format", "ok": False, "message": "name must be kebab-case 2-64 chars"})
        else:
            results.append({"check": "name-format", "ok": True, "message": "valid kebab-case"})
        if len(str(name)) > MAX_NAME_LEN:
            results.append({"check": "name-length", "ok": False, "message": f"name > {MAX_NAME_LEN}"})
        else:
            results.append({"check": "name-length", "ok": True, "message": "ok"})

    # description
    desc = meta.get("description")
    if not desc:
        results.append({"check": "description-present", "ok": False, "message": "missing description"})
    else:
        results.append({"check": "description-present", "ok": True, "message": "present"})
        if not isinstance(desc, str):
            results.append({"check": "description-type", "ok": False, "message": "description must be string"})
        else:
            if len(desc) > MAX_DESC_LEN:
                results.append({"check": "description-length", "ok": False, "message": f">{len={len(desc)} > {MAX_DESC_LEN}"})
            else:
                results.append({"check": "description-length", "ok": True, "message": f"len={len(desc)}"})
            for bad in FORBIDDEN_IN_DESC:
                if bad in desc:
                    results.append({"check": f"description-forbidden-{bad!r}", "ok": False, "message": f"contains {bad!r}"})
                else:
                    results.append({"check": f"description-forbidden-{bad!r}", "ok": True, "message": "clean"})

    # dangerous body patterns
    for pattern, label in DANGEROUS_PATTERNS:
        if re.search(pattern, body):
            results.append({"check": f"security-{label}", "ok": False, "message": f"found {label}"})
        else:
            results.append({"check": f"security-{label}", "ok": True, "message": "clean"})

    return results


def lint_path(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    if path.is_file() and path.name == "SKILL.md":
        return lint_skill_md(path)
    if path.is_dir():
        skill_md = path / "SKILL.md"
        if skill_md.exists():
            return lint_skill_md(skill_md)
        # recurse one level
        all_results = []
        for child in sorted(path.iterdir()):
            if child.is_dir() and (child / "SKILL.md").exists():
                all_results.extend(lint_skill_md(child / "SKILL.md"))
        return all_results or [{"check": "path", "ok": False, "message": "no SKILL.md found"}]
    return [{"check": "path", "ok": False, "message": f"not a SKILL.md or skill directory: {path}"}]
