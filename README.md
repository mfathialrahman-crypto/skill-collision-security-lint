# skill-collision-security-lint

**Independent tools for Agent Skills ecosystems.**  
Not a skill-creator clone. Not a full meta-system.

Two focused capabilities:

1. **Collision Detector** — Detect name, description, and trigger overlap across skills (local + public indexes).
2. **Security Lint** — Static analysis of SKILL.md for frontmatter violations, dangerous patterns, progressive-disclosure risks, and license attribution.

## Why this exists

Most skill repositories re-implement the entire creation loop. The highest-leverage problems are narrower:
- Skills that collide on trigger phrases and under/over-fire.
- Skills that ship insecure or non-compliant frontmatter.

This repository ships only those two tools, with measurable before/after reports.

## Quick start

```bash
pip install -e .
skill-lint path/to/skill-or-directory
skill-collision --local path/to/skills
```

## Design rules

- Zero dependency on any single agent runtime beyond standard Python.
- Output is always machine-readable JSON + human summary.
- Every check ships with at least one reproducible test case (n≥5 where applicable).
- Attribution: any code derived from Anthropic skill-creator patterns carries explicit notice (see NOTICE).

## Status

- [x] Repository scaffold
- [x] Collision Detector v0.1 (exact name + Jaccard description)
- [x] Security Lint v0.1 (name/description rules + dangerous patterns)
- [ ] Benchmark suite (n≥5)
- [ ] Public before/after report

## License

Apache-2.0. See LICENSE.
