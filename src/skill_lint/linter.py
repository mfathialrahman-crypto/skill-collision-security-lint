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
    (r"(?i)os\.popen\s*\(", "os.popen call"),
    (r"(?i)subprocess\.(call|run|Popen)", "subprocess invocation"),
    (r"(?i)rm\s+-rf", "destructive rm -rf"),
    (r"(?i)curl\s+.*\|\s*(ba)?sh", "curl | sh pattern"),
    (r"(?i)wget\s+[^\n|]*\|\s*(ba)?sh", "wget | sh pattern"),
    (r"(?i)pickle\.loads\s*\(", "pickle.loads (RCE risk)"),
    (r"(?i)base64\.b64decode\s*\(", "base64 decode (possible obfuscation)"),
    (r"(?i)__import__\s*\(", "dynamic __import__"),
    (r"(?i)chmod\s+777\b", "world-writable chmod"),
]

# Live credentials. Placeholders such as ghp_REDACTED are below the length floor.
SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "github personal access token"),
    (r"github_pat_[A-Za-z0-9_]{22,}", "github fine-grained token"),
    (r"sk-(?:proj-)?[A-Za-z0-9]{20,}", "secret key token"),
    (r"xai-[A-Za-z0-9]{20,}", "xai api key"),
    (r"AKIA[0-9A-Z]{16}", "aws access key id"),
    (r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", "private key block"),
    (
        r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]",
        "hardcoded credential assignment",
    ),
]

EXFIL_PATTERNS = [
    (r"(?i)ignore (?:all |any )?(?:previous|prior|above) instructions", "prompt-injection override"),
    (r"(?i)(?:webhook\.site|ngrok\.io|pastebin\.com|discord(?:app)?\.com/api/webhooks)", "known exfil host"),
    (r"(?i)requests\.(?:post|put|patch)\s*\(", "outbound http write"),
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


def _call_slice(body: str, open_paren: int) -> str:
    """Arguments of one call. Stops at the matching closer so a later safe call cannot hide an earlier unsafe one."""
    depth = 0
    end = min(len(body), open_paren + 500)
    for i in range(open_paren, end):
        ch = body[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return body[open_paren : i + 1]
        elif ch == "\n" and depth <= 1 and i > open_paren + 1:
            # Single-line calls should not swallow the rest of the file.
            rest = body[open_paren:i]
            if ")" not in rest:
                return rest
    return body[open_paren:end]


def _unsafe_yaml_load(body: str) -> bool:
    for match in re.finditer(r"(?i)yaml\.load\s*\(", body):
        window = _call_slice(body, match.end() - 1)
        if re.search(r"(?i)Loader\s*=\s*yaml\.(?:UnsafeLoader|Loader|FullLoader|CLoader)\b", window):
            return True
        if not re.search(r"(?i)SafeLoader|CSafeLoader", window):
            return True
    return False


def _explicit_unsafe_loader(body: str) -> bool:
    return bool(re.search(r"(?i)yaml\.load\s*\([^)]*Loader\s*=\s*yaml\.Loader\b", body))


def _append_pattern_checks(
    results: list[dict[str, Any]],
    text: str,
    patterns: list[tuple[str, str]],
) -> None:
    for pattern, label in patterns:
        hit = re.search(pattern, text) is not None
        results.append(
            {
                "check": f"security-{label}",
                "ok": not hit,
                "message": f"found {label}" if hit else "clean",
            }
        )


def lint_skill_md(path: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    meta, body = _load_skill_md(path)
    scanned = f"{meta.get('description') or ''}\n{body}"

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

    desc = meta.get("description")
    if not desc:
        results.append({"check": "description-present", "ok": False, "message": "missing description"})
    else:
        results.append({"check": "description-present", "ok": True, "message": "present"})
        if not isinstance(desc, str):
            results.append({"check": "description-type", "ok": False, "message": "description must be string"})
        else:
            if len(desc) > MAX_DESC_LEN:
                results.append({"check": "description-length", "ok": False, "message": f"len={len(desc)} > {MAX_DESC_LEN}"})
            else:
                results.append({"check": "description-length", "ok": True, "message": f"len={len(desc)}"})
            for bad in FORBIDDEN_IN_DESC:
                if bad in desc:
                    results.append({"check": f"description-forbidden-{bad!r}", "ok": False, "message": f"contains {bad!r}"})
                else:
                    results.append({"check": f"description-forbidden-{bad!r}", "ok": True, "message": "clean"})

    _append_pattern_checks(results, body, DANGEROUS_PATTERNS)

    explicit = _explicit_unsafe_loader(body)
    results.append(
        {
            "check": "security-unsafe yaml.load",
            "ok": not explicit,
            "message": "found unsafe yaml.load" if explicit else "clean",
        }
    )
    plain = _unsafe_yaml_load(body)
    results.append(
        {
            "check": "security-yaml.load without SafeLoader",
            "ok": not plain,
            "message": "found yaml.load without SafeLoader" if plain else "clean",
        }
    )

    # Secrets and exfil are scanned in description + body. A token in frontmatter is still a leak.
    _append_pattern_checks(results, scanned, SECRET_PATTERNS)
    _append_pattern_checks(results, scanned, EXFIL_PATTERNS)

    return results


def lint_path(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    if path.is_file() and path.name == "SKILL.md":
        return lint_skill_md(path)
    if path.is_dir():
        skill_md = path / "SKILL.md"
        if skill_md.exists():
            return lint_skill_md(skill_md)
        all_results = []
        for child in sorted(path.iterdir()):
            if child.is_dir() and (child / "SKILL.md").exists():
                all_results.extend(lint_skill_md(child / "SKILL.md"))
        return all_results or [{"check": "path", "ok": False, "message": "no SKILL.md found"}]
    return [{"check": "path", "ok": False, "message": f"not a SKILL.md or skill directory: {path}"}]
