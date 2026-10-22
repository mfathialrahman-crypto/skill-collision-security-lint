# Distribution Pack — skill-collision-security-lint

Copy-paste ready. Do not change the core claim.

## Short (X / LinkedIn)

Most skill repos re-build the entire creator loop.
The higher-leverage problems are narrower:

• Name + description collisions that cause under/over-triggering
• Insecure or non-compliant SKILL.md frontmatter

I shipped two independent tools only:

skill-lint  — frontmatter + dangerous-pattern checks
skill-collision — exact name + Jaccard description + trigger-phrase overlap

Baseline (n=6): lint TP 100% / FP 0%, planted collision recall 100%.

Repo: https://github.com/mfathialrahman-crypto/skill-collision-security-lint
Report: docs/benchmark-v0.1.md

Apache-2.0. Not a skill-creator fork.

## Hacker News style

Title: Independent Collision Detector + Security Lint for Agent Skills (not another skill-creator)

Body:
Agent Skills are proliferating. Two practical problems keep appearing:

1. Skills collide on names and trigger descriptions → unpredictable activation.
2. SKILL.md files ship with invalid frontmatter or dangerous body patterns.

This repo contains only those two tools. No full creation loop, no framework lock-in.

- skill-lint: name format, description length/forbidden tokens, eval/exec/rm-rf/curl|sh patterns
- skill-collision: exact-name + Jaccard ≥ 0.55 on description tokens + trigger-phrase overlap

Public baseline report (n=6 fixtures): https://github.com/mfathialrahman-crypto/skill-collision-security-lint/blob/main/docs/benchmark-v0.1.md

Next step is measuring false-positive rate on ≥50 real public skills.

## Reddit (r/LocalLLaMA / r/MachineLearning / agent communities)

Same content as HN body + link to the benchmark.

## Next actions for stars + professionalism

1. Post the short version on X and LinkedIn today.
2. Submit to HN when traffic is low (morning US).
3. Open a PR or discussion on agentskills.io / related lists if they accept tooling.
4. Keep weekly commits that improve the false-positive measurement set.
5. Never claim stars or rankings that do not exist.
