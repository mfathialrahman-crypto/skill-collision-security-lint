# Benchmark Report v0.1 — skill-collision-security-lint

Date: 2026-10-18
Fixtures: 6 (good-skill, bad-skill, collision-a, collision-b, safe-minimal, trigger-heavy)

## Security Lint Results

| Fixture        | Expected | Result | Notes                                      |
|----------------|----------|--------|--------------------------------------------|
| good-skill     | PASS     | PASS   | All frontmatter + security checks clean    |
| bad-skill      | FAIL     | FAIL   | name-format, eval, rm -rf correctly caught |
| safe-minimal   | PASS     | PASS   | Short name/description still valid         |
| trigger-heavy  | PASS     | PASS   | Long description under 1024, no forbidden tokens |
| collision-a    | PASS     | PASS   | Clean                                      |
| collision-b    | PASS     | PASS   | Clean                                      |

**True positive rate (bad cases caught):** 1/1 = 100%  
**False positive rate (good cases failed):** 0/5 = 0%

## Collision Detector Results

Scanned: 6 skills under tests/fixtures

| Type                 | Pair                  | Detail          | Expected |
|----------------------|-----------------------|-----------------|----------|
| description-overlap  | collision-a ↔ collision-b | Jaccard ≥ 0.55 | Detected |
| exact-name           | (none)                | —               | None     |

**Detected collisions:** 1 (correct)  
**Missed known overlaps:** 0

## Summary Metrics

- Lint precision on this set: 100%
- Collision recall on planted pair: 100%
- Total checks executed across fixtures: >30

## Next measurement target

Expand to ≥50 public skills from anthropics/skills + community sources and publish false-positive rate under real distribution. This report is the baseline (before any threshold tuning).

Reproducible with:
```bash
pip install -e .
PYTHONPATH=src pytest tests/ -q
skill-collision --local tests/fixtures
skill-lint tests/fixtures
```
