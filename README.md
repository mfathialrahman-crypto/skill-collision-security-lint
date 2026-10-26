# skill-collision-security-lint

**Independent tools for Agent Skills ecosystems.**  
Not a skill-creator clone. Not a full meta-system.

Version **0.1.2**

Two focused, high-leverage capabilities:

1. **Collision Detector** — Detect name, description, and trigger-phrase overlap across skills (local + public indexes).
2. **Security Lint** — Static analysis of SKILL.md for frontmatter violations, dangerous patterns, progressive-disclosure risks, and license attribution.

## Why this exists

Most skill repositories re-implement the entire creation loop. The highest-leverage problems are narrower:

- Skills that collide on trigger phrases and under/over-fire.
- Skills that ship insecure or non-compliant frontmatter.

This repository ships only those two tools, with measurable before/after reports.

## Install

```bash
pip install -e git+https://github.com/mfathialrahman-crypto/skill-collision-security-lint.git#egg=skill-collision-security-lint
```

Or clone:

```bash
git clone https://github.com/mfathialrahman-crypto/skill-collision-security-lint.git
cd skill-collision-security-lint
pip install -e .
```

## Quick start

```bash
skill-lint path/to/skill-or-directory
skill-collision --local path/to/skills
```

The Project Engineering Constitution that governs continuous improvement lives in [`AGENTS.md`](./AGENTS.md).

## Design rules

- Zero dependency on any single agent runtime beyond standard Python.
- Output is always machine-readable JSON + human summary.
- Every check ships with at least one reproducible test case (n≥5 where applicable).
- Attribution: any code derived from Anthropic skill-creator patterns carries explicit notice (see NOTICE).

## Status

- [x] Repository scaffold
- [x] Collision Detector v0.1.2 (exact name + Jaccard description + trigger-phrase overlap)
- [x] Security Lint v0.1.2 (name/description rules + expanded dangerous patterns: eval/exec/subprocess/rm/curl|sh/pickle/unsafe-yaml/base64)
- [x] Regression tests + CI (3.10–3.12)
- [x] Benchmark suite (n=6 fixtures)
- [x] Public before/after report → [docs/benchmark-v0.1.md](docs/benchmark-v0.1.md)

**Baseline metrics (v0.1):** Lint true-positive 100%, false-positive 0%. Collision recall on planted pair 100%.

## License

Apache-2.0. See LICENSE.
