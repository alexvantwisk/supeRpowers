---
name: skill-auditor
description: >
  Use when auditing, reviewing, or improving Claude Code skills against best
  practices. Scores any skill folder against a 38-check rubric covering
  description quality, content efficiency, gotchas, examples, scripts,
  multi-skill orchestration, and testability. Use when the user says 'audit
  this skill', 'review my skill', 'check skill quality', 'score this skill',
  'is this skill any good', 'improve this skill', 'what's wrong with my skill',
  'run skill audit', or 'generate eval criteria for this skill'. Also activate
  when the user asks to compare skills against best practices or benchmark a
  skill. Do NOT use for creating new skills from scratch (use skill-creator
  instead), generating R package skills from GitHub repos (use
  r-package-skill-generator instead), reviewing R code quality (use
  r-code-reviewer agent), or general code review.
disable-model-invocation: true
---

# Skill Auditor

Score any Claude Code skill against a 38-check rubric synthesized from Anthropic engineers, official documentation, and power user best practices.

## Three Modes

### `audit` — Read-only assessment (default)

Score one or all skills. No changes made.

```
/skill-auditor audit <skill-name>
/skill-auditor audit all
```

### `fix` — Propose and apply improvements

Audit first, then fix the highest-impact failures.

```
/skill-auditor fix <skill-name>
```

### `eval` — Generate eval criteria

Create binary yes/no eval questions and test prompts for a skill.

```
/skill-auditor eval <skill-name>
```

## Progress Tracking

Use TaskCreate/TaskUpdate to track progress throughout the audit. Create tasks at session start, update as each phase completes.

**For `audit` mode (single skill):** One task: "Score [skill-name] against 38-check rubric"

**For `audit all` mode:** Task per phase: "Phase 1: Score all N skills", "Phase 2: Compile gap report". Mark each in_progress when starting, completed when done.

**For `fix` mode:** Task per batch: "Batch 1: Descriptions", "Batch 2: Gotchas", etc. Add "Verify batch N" after each commit.

**For `eval` mode:** One task: "Generate eval criteria for [skill-name]"

Always mark tasks completed before moving to the next phase.

## Workflow

### Phase 1: Deterministic Checks (Script)

Run the scoring script on the target skill:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/score_skill.py" <skill-directory> --siblings-dir <skills-root> --max-lines 300
```

**With project conventions** (e.g., for R projects with rules files):

```bash
python "${CLAUDE_SKILL_DIR}/scripts/score_skill.py" <skill-directory> --conventions <rules-file> --max-lines 300 --siblings-dir <skills-root>
```

The script scores 17 deterministic checks: frontmatter format, description quality (D1-D7), content efficiency (C2-C5), gotchas heading (G1), example structure (E1, E5), scripts presence (V2), and sibling references (O4). Use `--format table` for human-readable output. Outputs structured JSON by default.

### Phase 2: Judgment Checks (Claude)

Read `references/audit-rubric.md` for the full 38-check rubric.

Using the script's JSON output plus your own reading of the SKILL.md content, score the remaining checks that require judgment:

**Content efficiency (C1, C3, C6, C7):**
- Read the skill. Is there content Claude already knows well? Flag it.
- Is terminology consistent throughout?
- Any time-sensitive information?

**Gotchas (G1-G6):**
- Does a dedicated Gotchas/Pitfalls section exist?
- Are the gotchas real failure points or hypothetical?
- Scan for ambiguous instructions (Drifter prevention).
- Check for scope constraints (Overachiever prevention).

**Examples (E1-E5):**
- Are there input/output pairs or just prompt-only examples?
- Happy path AND edge case covered?
- Do code examples follow project conventions?

**Scripts & Verification (V1-V5):**
- Is there a feedback loop for quality-critical operations?
- Are scripts provided for deterministic tasks?
- Clear execution vs reference distinction?

**Orchestration (O1-O4):**
- Run `python "${CLAUDE_SKILL_DIR}/scripts/extract_frontmatter.py" <skills-root>` to extract all sibling descriptions and detect territory overlaps.
- Map territory boundaries using the overlap warnings from the script.
- Check for cross-references to sibling skills (O4 is partially automated by score_skill.py).

**Testability (T1-T4):**
- Can you define 3-6 binary eval questions for this skill?
- Can you meaningfully A/B test it vs raw Claude?
- Are success criteria specific enough to operationalize?

### Phase 3: Report

Generate a report card per skill:

```
## Skill: <name>
Score: X/38

D: Description Quality     ███████ X/7
C: Content Efficiency      ███████ X/7
G: Gotchas                 ██████░ X/6
E: Examples                █████░░ X/5
V: Scripts & Verification  █████░░ X/5
O: Orchestration           ████░░░ X/4
T: Testability             ████░░░ X/4

### Failures
| Check | Finding | Impact |
|-------|---------|--------|
| D3    | No negative boundaries in description | HIGH |
| G1    | No Gotchas section | HIGH |
| ...   | ... | ... |

### Top 3 Fixes
1. [highest impact fix]
2. [second highest]
3. [third highest]
```

**Impact priority:** D > G > O > C > E > T > V

### Auditing All Skills

When `$ARGUMENTS` is "all" or "audit all":

1. Glob all `skills/*/SKILL.md` in the project
2. Run `extract_frontmatter.py` to get all descriptions and overlap warnings
3. Dispatch parallel subagents (3 skills per subagent). Each runs Phase 1 + Phase 2.
4. Collect all report cards. **Do NOT trust subagent arithmetic** — subagents systematically miscount P/F totals.
5. Use `python "${CLAUDE_SKILL_DIR}/scripts/aggregate_report.py" <scores-dir> --output audit-gap-report.md` to compile the gap report. The script recomputes all totals from individual P/F detail rows.
6. Save report to `docs/superpowers/specs/audit-gap-report.md`

## Fix Mode

When mode is `fix`:

1. Run the full audit first
2. Read `references/remediation-guide.md` for fix strategies
3. Read `references/failure-modes.md` to diagnose failure patterns
4. Address failures in priority order: D → G → O → C → E → T → V
5. For each fix, show the before/after diff and explain why
6. After each batch of fixes, run `python "${CLAUDE_SKILL_DIR}/scripts/verify_batch.py" <skills-root> --all --max-lines 300` to validate constraints
7. Re-run the deterministic script after changes to verify improvement

## Eval Mode

When mode is `eval`:

1. Read the skill thoroughly
2. Generate 3-6 binary yes/no eval questions (autoresearch method)
3. Generate 3+ representative test prompts (happy path, edge case, boundary)
4. Define specific success criteria per test prompt
5. Write to `skills/<name>/eval.md` (development-only, not loaded by plugin)

## Gotchas

**Description ≠ summary.** The most common audit failure is a description that summarizes the skill instead of specifying when to trigger. Descriptions are triggers, not documentation.

**Obvious content is invisible waste.** Skills that restate what Claude already knows consume tokens without adding value. The hardest audit judgment is deciding what Claude "already knows" — err on the side of cutting.

**Not every skill needs scripts.** V-section checks apply selectively. A pure-instruction skill (code review guidelines, writing conventions) may legitimately score 0/5 on scripts. Flag it but don't penalize.

**Orchestration needs ALL siblings.** You cannot audit O-section for a single skill in isolation. You must read all sibling skill descriptions to detect overlaps and missing boundaries.

**Meta-skills need adapted criteria.** Skills that generate or operate on other skills (e.g., skill-creator, r-package-skill-generator) may need different E-section expectations — their "examples" might be generated skill outputs, not user-facing code. Use skill-auditor for auditing these skills, but use r-package-skill-generator (not skill-auditor) when the goal is to generate a new skill from a GitHub package repo.

**Subagent arithmetic is unreliable.** All 5 subagents in the 15-skill audit miscounted P/F totals (e.g., 4 passes reported as "3/7"). Always recompute from individual P/F detail rows using `aggregate_report.py`, never trust subagent section totals.

**Line budget management.** After adding Gotchas + Examples sections, skills approach line limits. Track remaining budget with `verify_batch.py --all` before starting content additions.

## Examples

### Happy Path: Audit a single skill

```
> /skill-auditor audit r-stats

## Skill: r-stats
Score: 31/38

D: Description Quality     ███████ 7/7
C: Content Efficiency      █████░░ 5/7
G: Gotchas                 ██████░ 6/6
E: Examples                ████░░░ 4/5
V: Scripts & Verification  ████░░░ 4/5
O: Orchestration           ███░░░░ 3/4
T: Testability             ██░░░░░ 2/4

### Failures
| Check | Finding                          | Impact |
|-------|----------------------------------|--------|
| C3    | Terminology inconsistency: mixed "model" / "fit" | MEDIUM |
| T2    | No binary eval questions defined | LOW    |
| ...   | ...                              | ...    |
```

### Edge Case: Fix mode with before/after diff

```
> /skill-auditor fix r-visualization

Fixing D3 (negative boundaries missing from description)...

- description: >
-   Use when creating ggplot2 visualizations...
+ description: >
+   Use when creating ggplot2 visualizations...
+   Do NOT use for Shiny reactive plots (use r-shiny),
+   statistical model diagnostics (use r-stats), or
+   clinical forest plots (use r-clinical).

Re-running deterministic checks... D3: PASS (was FAIL)
Score: 34/38 → 35/38
```

**More example prompts:**

- "Audit the r-stats skill against the full rubric"
- "Run the skill auditor on all skills and generate a gap report"
- "Fix the description for r-visualization based on audit findings"
- "Generate eval criteria for the r-tdd skill"
- "Score my new skill-auditor skill against the 38-check rubric"
