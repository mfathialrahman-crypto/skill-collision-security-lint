# skill-collision-security-lint

**Independent tools for Agent Skills ecosystems.**  
Not a skill-creator clone. Not a full meta-system.

Two focused capabilities:

1. **Collision Detector** — Detect name, description, and trigger-phrase overlap across skills (local + public indexes).
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

The Project Engineering Constitution that governs continuous improvement lives in [`AGENTS.md`](./AGENTS.md).

## Design rules

- Zero dependency on any single agent runtime beyond standard Python.
- Output is always machine-readable JSON + human summary.
- Every check ships with at least one reproducible test case (n≥5 where applicable).
- Attribution: any code derived from Anthropic skill-creator patterns carries explicit notice (see NOTICE).

## Status

- [x] Repository scaffold
- [x] Collision Detector v0.1.1 (exact name + Jaccard description + trigger-phrase overlap)
- [x] Security Lint v0.1.2 (v0.1.1 patterns, plus secrets, exfil hosts, prompt-injection overrides, os.popen, wget|sh, chmod 777, and a per-call yaml.load check that a later SafeLoader cannot mask)
- [x] Regression tests + CI (3.10–3.12)
- [x] Benchmark suite (n=6 fixtures)
- [x] Public before/after report → [docs/benchmark-v0.1.md](docs/benchmark-v0.1.md)

**Baseline metrics (v0.1):** Lint true-positive 100%, false-positive 0%. Collision recall on planted pair 100%.

## What v0.1.2 catches

Static checks, not a semantic proof. A later `yaml.safe_load` no longer hides an earlier `yaml.load`. Live tokens (`ghp_`, `github_pat_`, `sk-`, `xai-`, `AKIA`, private-key blocks, hardcoded assignments of 12+ characters) fail the lint. So do prompt-injection overrides, `requests.post/put/patch`, and known exfil hosts. Placeholders shorter than the length floor, such as `ghp_REDACTED`, stay clean.

## Private review

The tools stay free. A commissioned review of a private skill pack — secrets, exfiltration, and collisions against your own set — is an issue on this repository titled `review:`. No subscription.

## License

Apache-2.0. See LICENSE.
