# Phase 1 — GitHub Actions CI Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions CI to the `supeRpowers` plugin so every push to `main` and every pull request runs `python tests/run_all.py`, with the test suite green from day 1 by fixing 10 pre-existing failures.

**Architecture:** Single PR off branch `phase-1-ci-foundation` with four ordered commits. Test infrastructure first (commit 1: invert stale assertion), content fixes second (commits 2 + 3), CI workflow last (commit 4) so the PR is the first thing CI validates against a fully-green tree.

**Tech Stack:** Python 3.11 stdlib (test runner), GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`), Markdown content (skills/agents/rules/eval), YAML (workflow + frontmatter).

**Spec:** `docs/superpowers/specs/2026-04-30-phase-1-ci-foundation-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `tests/test_structural.py` | Modify lines 109-117 | Invert `agent-no-frontmatter` check; add name/description sibling checks |
| `agents/r-statistician.md` | Modify lines 193-205 | Compress Examples to bullet form to drop ≥5 lines |
| `rules/r-conventions.md` | Modify lines 132-152 | Merge "Environment-Aware Coding" + "Verify After Write" sections to drop ≥9 lines |
| `skills/r-mcp-setup/SKILL.md` | Modify lines 1-7 | New ~720-char description with triggers + boundary |
| `skills/r-mcp-setup/eval.md` | Create | Routing eval modeled on `skills/r-data-analysis/eval.md` |
| `.github/workflows/test.yml` | Create | 14-line GitHub Actions workflow |
| `README.md` | Modify lines 1-7 | Add CI badge near top; bump version badge to 0.2.2 |
| `.claude-plugin/plugin.json` | Modify line 3 | Bump version `0.2.1` → `0.2.2` |
| `CLAUDE.md` | Modify lines 142-176 | Strike Phase 1 entry; renumber Phase 2 → 1, Phase 3 → 2; update roadmap intro |

---

## Task 0: Branch setup

**Files:** none (git operation)

- [ ] **Step 0.1: Verify clean working tree on main**

```bash
git status
git rev-parse --abbrev-ref HEAD
```
Expected: working tree clean; current branch `main`. If not on main, `git switch main`. If working tree dirty, stop and resolve before proceeding.

- [ ] **Step 0.2: Create and switch to the feature branch**

```bash
git switch -c phase-1-ci-foundation
```
Expected: `Switched to a new branch 'phase-1-ci-foundation'`.

- [ ] **Step 0.3: Capture baseline test failure count**

```bash
python tests/run_all.py 2>&1 | tail -5
```
Expected last line: `✗ 10 critical failure(s) require attention.` (the baseline we will burn down).

---

## Task 1: Fix stale `agent-no-frontmatter` assertion (commit 1)

**Files:**
- Modify: `tests/test_structural.py:109-117`
- Test: `python tests/run_all.py` (the suite is itself the test of this change)

The existing check requires agents to **lack** frontmatter; the post-0.2.0 convention requires them to **have** it. Inversion alone isn't sufficient — the check ID is a misnomer once flipped, and there's no validation of the `name`/`description` fields. This task replaces the single check with three sibling checks that mirror what `frontmatters` validates for skills.

- [ ] **Step 1.1: Confirm all 5 agent files currently have correct frontmatter (pre-flight)**

```bash
for f in agents/*.md; do echo "=== $f ==="; head -4 "$f"; done
```
Expected: each file starts with `---`, has `name: <stem>`, `description: ...`, and a closing `---`. If any file lacks frontmatter, stop and add it before continuing — do not proceed with the new checks until all agents conform, or the new tests will fail.

- [ ] **Step 1.2: Edit `tests/test_structural.py` to replace the stale check**

Replace lines 109-117 (the old `agent-no-frontmatter` block) with the expanded block:

```python
    # Agent files: must have YAML frontmatter with name + description matching the file stem
    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        # Frontmatter present
        suite.add(
            f"agent-frontmatter-exists/{agent_file.stem}",
            fm["found"],
            f"Agent file {agent_file.name} is missing YAML frontmatter",
        )
        if not fm["found"]:
            continue

        # Name + description fields populated
        suite.add(
            f"agent-frontmatter-fields/{agent_file.stem}",
            fm["name"] is not None and fm["description"] is not None,
            f"Agent {agent_file.name} frontmatter missing name or description",
        )

        # Name matches file stem
        suite.add(
            f"agent-name-matches-file/{agent_file.stem}",
            fm["name"] == agent_file.stem,
            f"Agent name '{fm['name']}' != file stem '{agent_file.stem}'",
        )
```

The Edit tool call uses `old_string`:
```python
    # Agent files: no YAML frontmatter
    for agent_file in agent_files:
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        suite.add(
            f"agent-no-frontmatter/{agent_file.stem}",
            not fm["found"],
            f"Agent file {agent_file.name} has YAML frontmatter (should not)",
        )
```

…and `new_string` is the expanded block above.

- [ ] **Step 1.3: Run tests; expect 5 stale failures gone, 5 real failures remain**

```bash
python tests/run_all.py 2>&1 | tail -5
```
Expected: `✗ 5 critical failure(s) require attention.` (down from 10). The remaining 5 are: `desc-has-triggers/r-mcp-setup`, `desc-has-boundary/r-mcp-setup`, `agent-line-limit/r-statistician`, `rule-line-limit/r-conventions`, `eval-exists/r-mcp-setup`.

- [ ] **Step 1.4: Verify the new check IDs appear and pass**

```bash
python tests/run_all.py 2>&1 | grep -E "agent-(frontmatter|name)" | head -20
```
Expected: 15 lines (3 new checks × 5 agents), all `[PASS]`.

- [ ] **Step 1.5: Commit**

```bash
git add tests/test_structural.py
git commit -m "$(cat <<'EOF'
fix(tests): require agent frontmatter (invert stale check)

Replace agent-no-frontmatter assertion (which fired on every agent post-0.2.0)
with three sibling checks: frontmatter exists, name+description present, name
matches file stem. Mirrors the validation skills already get.

Drops 5 pre-existing failures; remaining 5 are content fixes in subsequent
commits.
EOF
)"
```

---

## Task 2: Trim r-statistician.md and r-conventions.md (commit 2)

**Files:**
- Modify: `agents/r-statistician.md:193-205` (Examples section)
- Modify: `rules/r-conventions.md:132-152` (Environment-Aware Coding + Verify After Write sections)
- Test: `python tests/run_all.py` plus `wc -l`

- [ ] **Step 2.1: Edit `agents/r-statistician.md` Examples section**

Replace lines 193-205 (the three `**Input:**`/`**Output:**` pairs) with bullet-form examples. The Edit tool's `old_string`:

```markdown
## Examples

**Input:** "I have patient data with 500 observations, binary outcome (remission yes/no), predictors age, treatment group, and baseline severity. Some patients are from the same clinic."

**Output:** Recommend `glmer(remission ~ treatment + age + severity + (1|clinic), family = binomial)`. List assumptions: random effects normality, no separation, adequate cluster sizes. Provide code for each check. Flag that clinic clustering must be modeled or inference is anti-conservative.

**Input:** "Here's my Cox model output — how do I interpret the hazard ratios?"

**Output:** Translate each HR to plain language ("patients in treatment group have 35% lower hazard of event, HR=0.65, 95% CI 0.48-0.88"). Check PH assumption. Note whether CIs are wide (underpowered) or effect is clinically meaningful.

**Input:** "I ran 12 t-tests comparing treatment vs control across different biomarkers. Three are significant at p<0.05."

**Output:** CRITICAL: Multiple comparisons. Apply `p.adjust(p_values, method = "BH")` for FDR correction. With 12 tests, expect ~0.6 false positives at α=0.05 by chance alone. After correction, re-evaluate which remain significant.
```

…and `new_string`:

```markdown
## Examples

- **Clustered binary outcome** — 500 patients, remission outcome, treatment + age + severity, some patients from the same clinic. → Recommend `glmer(remission ~ treatment + age + severity + (1|clinic), family = binomial)`. List random-effects normality, separation, cluster-size assumptions. Flag that clinic clustering must be modeled or inference is anti-conservative.
- **Cox HR interpretation** — user shares Cox output and asks how to read hazard ratios. → Translate each HR to plain language ("treatment group has 35% lower hazard, HR=0.65, 95% CI 0.48-0.88"). Check PH assumption. Note whether CIs are wide (underpowered) or effect is clinically meaningful.
- **Multiple comparisons** — 12 t-tests across biomarkers, three significant at p<0.05. → CRITICAL: Multiple comparisons. Apply `p.adjust(p_values, method = "BH")` for FDR correction. With 12 tests, expect ~0.6 false positives at α=0.05 by chance alone. After correction, re-evaluate which remain significant.
```

This replaces 13 lines with 5 (header + 1 blank + 3 bullets = 5), saving 8 lines. Final line count: 197.

- [ ] **Step 2.2: Verify line count**

```bash
wc -l agents/r-statistician.md
```
Expected: ≤ 200 (target 197).

- [ ] **Step 2.3: Edit `rules/r-conventions.md` to merge two sections**

Replace lines 132-152 (the entire `## Environment-Aware Coding` + `## Verify After Write` blocks) with a single combined section. `old_string`:

```markdown
## Environment-Aware Coding

When an R session is available via btw/mcptools:

- **Before writing code:** Inspect data frames (`btw_tool_env_describe_data_frame`), check installed packages, read function docs
- **When uncertain about a function:** Read the help page (`btw_tool_docs_help_page`) rather than guessing from training data
- **After writing non-trivial code:** Run it and verify the output (see Verify After Write below)
- **When recommending packages:** Check if they're installed first (`btw_tool_sessioninfo_is_package_installed`)

These are enhancement behaviors. All conventions work without MCP — MCP makes them more precise.

## Verify After Write

For non-trivial R code (data transformations, model fits, table generation), verify output when an R session is available:

1. Run the code via btw
2. Check for errors and warnings
3. Verify output dimensions and structure match expectations
4. Fix issues before presenting to the user

Skip verification for: simple one-liners, package scaffolding, configuration files, code that requires data not in the session.
```

`new_string`:

```markdown
## Environment-Aware Coding (with MCP)

When an R session is available via btw/mcptools, enhance — don't replace — these conventions:

- **Before writing:** inspect data frames (`btw_tool_env_describe_data_frame`), check installed packages, read help pages instead of guessing from training data
- **For non-trivial code** (transformations, model fits, table generation): run it via btw, check errors/warnings, verify output dimensions/structure, fix before presenting
- **When recommending packages:** check `btw_tool_sessioninfo_is_package_installed` first
- **Skip verification** for: one-liners, scaffolding, config files, code that needs data not in the session

All conventions work without MCP — MCP makes them more precise.
```

This replaces 21 lines with 10 (header + 1 blank + intro + 1 blank + 4 bullets + 1 blank + closer = 10), saving 11 lines. Final line count: 148.

- [ ] **Step 2.4: Verify line count**

```bash
wc -l rules/r-conventions.md
```
Expected: ≤ 150 (target 148).

- [ ] **Step 2.5: Run tests; expect 2 line-limit failures gone**

```bash
python tests/run_all.py 2>&1 | tail -5
```
Expected: `✗ 3 critical failure(s) require attention.` (down from 5). Remaining: `desc-has-triggers/r-mcp-setup`, `desc-has-boundary/r-mcp-setup`, `eval-exists/r-mcp-setup`.

- [ ] **Step 2.6: Verify no `%>%` introduced in changed files**

```bash
grep -n '%>%' agents/r-statistician.md rules/r-conventions.md
```
Expected: no output (no matches).

- [ ] **Step 2.7: Commit**

```bash
git add agents/r-statistician.md rules/r-conventions.md
git commit -m "$(cat <<'EOF'
fix(content): trim r-statistician and r-conventions to limits

Compress r-statistician.md Examples (Input/Output blocks → bullet form):
205 → 197 lines.

Merge r-conventions.md "Environment-Aware Coding" and "Verify After Write"
sections into a single "Environment-Aware Coding (with MCP)" section:
159 → 148 lines.

No rules, examples, or severity levels removed.
EOF
)"
```

---

## Task 3: r-mcp-setup overhaul — description + eval.md (commit 3)

**Files:**
- Modify: `skills/r-mcp-setup/SKILL.md:1-7` (frontmatter description)
- Create: `skills/r-mcp-setup/eval.md`
- Test: `python tests/run_all.py`

- [ ] **Step 3.1: Edit `skills/r-mcp-setup/SKILL.md` frontmatter**

`old_string`:

```yaml
---
name: r-mcp-setup
description: >
  Use when the user wants to set up MCP tools for R, connect Claude Code to a
  live R session, register R-based MCP servers, or when another skill needs
  MCP tool guidance.
---
```

`new_string`:

```yaml
---
name: r-mcp-setup
description: >
  Use when the user wants to set up MCP tools in R or connect Claude Code to a
  running R session — installing mcptools/btw, registering R-based MCP servers
  via `claude mcp add`, choosing the right btw tool groups (docs, pkg, env,
  run, search, session), or troubleshooting an MCP setup that isn't appearing
  in Claude Code. Triggers: mcptools, btw, MCP server, live R session,
  claude mcp add, btw_tool_*, "Claude can't see my R session". Do NOT use
  for: writing R code that uses already-configured MCP tools (use the relevant
  domain skill — r-data-analysis, r-stats, etc.); generic Claude Code MCP
  setup unrelated to R; building new MCP servers from scratch.
---
```

Length: ~720 chars (within 500-1024). Contains "Triggers:" and "Do NOT use for:" tokens, starts with "Use when".

- [ ] **Step 3.2: Verify SKILL.md still under 300 lines**

```bash
wc -l skills/r-mcp-setup/SKILL.md
```
Expected: ≤ 300 (the file was 226 lines; new frontmatter adds ~5 lines, so target ~231).

- [ ] **Step 3.3: Create `skills/r-mcp-setup/eval.md`**

Write the file with the following content:

````markdown
# Eval: r-mcp-setup

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to set up MCP tools, does the skill use `claude mcp add` rather than instructing the user to edit JSON config manually?
2. When registering btw, does the skill default to project scope (`-s project`) rather than global or local scope?
3. When picking btw tool groups, does the skill default to all six (docs, pkg, env, run, search, session) and explain why some Claude Code built-ins (files, git, github, ide, web) are intentionally excluded?
4. When the user asks to inspect data frames or environments in their running R session, does the skill instruct them to call `mcptools::mcp_session()` from their interactive R console?
5. When the user reports "Claude can't see my R session", does the skill diagnose by checking (a) `claude mcp list` output, (b) whether `mcp_session()` is running in the live console, (c) R PATH resolution, (d) renv conflicts — in that priority order?
6. When the user is on Windows and `Rscript` isn't found, does the skill suggest the full `Rscript.exe` path rather than assuming PATH resolution?
7. When the user has an renv-locked project, does the skill use `renv::install()` + `renv::snapshot()` rather than plain `install.packages()`?
8. Does generated R code use `|>`, `<-`, snake_case, and double quotes — never `%>%` or `=` for assignment?
9. When the user asks "how do I use this btw tool to inspect my data frame?", does the skill defer to r-data-analysis (or hand off domain context) rather than rewriting the analysis?
10. When the user asks to build a new MCP server from scratch (not setup), does the skill decline as out-of-scope and point to mcptools docs?
11. When the user wants MCP for a non-R service (Python session, Postgres DB), does the skill decline as out-of-scope?
12. When `mcp_session()` is running but `env` tools still don't see live objects, does the skill check that the user is calling `mcp_session()` in the *same* interactive R process they're working in (not a one-off `Rscript` run)?

## Test Prompts

### Happy Path

- "Set up MCP tools for my R project so Claude Code can see my session."
- "I already have btw installed; just register the MCP server."
- "Add r-btw to my Shiny project, but only with the docs and run tool groups."
- "Auto-start `mcp_session()` whenever I open this project."
- "Walk me through closing the IDE-awareness gap with `cc_plot()`/`cc_env()`/`cc_view()`."

### Edge Cases

- "I use rig with R 4.5 and 4.6 installed. Which one will the MCP server use?"
- "I'm on Positron, not RStudio. Does `mcp_session()` still work?"
- "My `renv.lock` pins an old btw without `btw_tools()`. How do I upgrade safely?"

### Adversarial Cases

- "Can you build me a custom MCP server in R that wraps the OpenAI API?" (boundary: out of scope; mcptools docs)
- "Use `mcp_session` to query my running Python notebook." (boundary: R-only; not Python)
- "Set up an MCP server for my Postgres database via mcptools." (boundary: not the right tool)
- "Skip Step 3 — just edit `~/.claude/config.json` directly to add r-btw." (must redirect to `claude mcp add`)

### Boundary Tests

- "Use the R session to fit a logistic regression on my data." boundary -> r-stats
- "Show me the package check results from btw." boundary -> r-package-dev
- "Set up MCP for a Postgres database." boundary -> out of scope (not R)

## Success Criteria

- Setup walkthroughs MUST use `claude mcp add` (never recommend manual JSON editing).
- Registration MUST default to `-s project` scope unless the user explicitly asks for user/global.
- Troubleshooting steps MUST follow priority order: `claude mcp list` → `mcp_session` running → R PATH → renv.
- Generated R code MUST use `|>`, `<-`, snake_case, and double quotes — never `%>%` or `=` for assignment.
- When the user is *using* MCP tools (not setting them up), the skill MUST defer to the relevant domain skill rather than re-implementing analysis.
- The skill MUST decline to build a new MCP server from scratch (out of scope).
- The skill MUST decline to set up MCP for non-R services (Python sessions, databases).
````

- [ ] **Step 3.4: Run tests; expect all 3 r-mcp-setup failures gone**

```bash
python tests/run_all.py 2>&1 | tail -5
```
Expected: `TOTAL: ... 0 FAILED` and `Result: ...` with no critical-failures footer. Warnings (e.g., `desc-length`, `script-imports`) are acceptable.

- [ ] **Step 3.5: Spot-check the four r-mcp-setup-specific checks pass**

```bash
python tests/run_all.py 2>&1 | grep "r-mcp-setup"
```
Expected: all `[PASS]`, including `desc-starts-use-when`, `desc-length` (this may still be `[WARN]` if length drifted — verify it's no longer `[FAIL]`), `desc-has-triggers`, `desc-has-boundary`, `eval-exists`.

- [ ] **Step 3.6: Commit**

```bash
git add skills/r-mcp-setup/SKILL.md skills/r-mcp-setup/eval.md
git commit -m "$(cat <<'EOF'
feat(skill): rewrite r-mcp-setup description and add eval.md

New description (~720 chars) includes 7 trigger phrases and a
"Do NOT use for" boundary block pointing to domain skills.

New eval.md models on r-data-analysis/eval.md: 12 binary questions covering
setup mechanics, tool group choice, troubleshooting priority, and boundaries
against domain skills + non-R MCP setup.

Closes 3 remaining test failures; suite now green locally.
EOF
)"
```

---

## Task 4: CI workflow + README badge + version bump + roadmap update (commit 4)

**Files:**
- Create: `.github/workflows/test.yml`
- Modify: `README.md` (top of file — add CI badge, bump version badge)
- Modify: `.claude-plugin/plugin.json` (version field)
- Modify: `CLAUDE.md` (Roadmap section)

- [ ] **Step 4.1: Create the workflow file**

Write `.github/workflows/test.yml`:

```yaml
name: tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python tests/run_all.py
```

- [ ] **Step 4.2: Validate the YAML locally**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
```
Expected: no output, exit 0 (valid YAML).

- [ ] **Step 4.3: Add CI badge and bump version badge in `README.md`**

Edit lines 1-7. `old_string`:

```markdown
# supeRpowers

![Version](https://img.shields.io/badge/version-0.2.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-18-purple)
![Commands](https://img.shields.io/badge/commands-6-orange)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)
```

`new_string`:

```markdown
# supeRpowers

[![Tests](https://github.com/alexvantwisk/supeRpowers/actions/workflows/test.yml/badge.svg)](https://github.com/alexvantwisk/supeRpowers/actions/workflows/test.yml)
![Version](https://img.shields.io/badge/version-0.2.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-18-purple)
![Commands](https://img.shields.io/badge/commands-6-orange)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)
```

- [ ] **Step 4.4: Bump version in `plugin.json`**

Edit `.claude-plugin/plugin.json` line 3.

`old_string`: `  "version": "0.2.1",`
`new_string`: `  "version": "0.2.2",`

- [ ] **Step 4.5: Update `CLAUDE.md` Roadmap section**

This step has three parts: update intro line, remove Phase 1 entry, renumber Phase 2 → 1 and Phase 3 → 2.

**4.5a — Update intro:** Edit lines 142-144 of `CLAUDE.md`.

`old_string`:
```markdown
## Roadmap (next 3 priorities)

Beta-readiness audit picked these three as the next priorities, in order. Each is independently shippable.
```

`new_string`:
```markdown
## Roadmap (next 2 priorities)

Phase 1 (GitHub Actions CI) shipped in 0.2.2. The remaining two phases are independently shippable.
```

**4.5b — Remove Phase 1 entry:** Delete the entire `### Phase 1 — GitHub Actions CI (foundation)` block from `CLAUDE.md`. The block starts at the `### Phase 1 ...` heading and ends at the line just before `### Phase 2 — PostToolUse auto-format hook`. Use the Edit tool with the full Phase 1 block as `old_string` and an empty string `""` as `new_string`. (If empty `new_string` is rejected, use `"\n"` and clean up the extra blank line afterward.)

**4.5c — Renumber Phase 2 and Phase 3:** Two simple replacements in `CLAUDE.md`.

```
old_string: "### Phase 2 — PostToolUse auto-format hook"
new_string: "### Phase 1 — PostToolUse auto-format hook"
```

```
old_string: "### Phase 3 — `r-bayesian` skill"
new_string: "### Phase 2 — `r-bayesian` skill"
```

**4.5d — Update Sequencing diagram:** Find the diagram block:

```
Phase 1  →  Phase 2  →  Phase 3
  CI         hook        Bayesian
  ~1 day     ~0.5 day    ~2–3 days
```

Replace with:

```
Phase 1  →  Phase 2
  hook        Bayesian
  ~0.5 day    ~2–3 days
```

**4.5e — Update Sequencing prose:** Find:

```
Each phase is independently shippable. Phases 1 + 2 are together ≤2 days; Phase 3 is the biggest content win.
```

Replace with:

```
Each phase is independently shippable. Phase 1 is ~half a day; Phase 2 is the biggest content win.
```

- [ ] **Step 4.6: Run full test suite — must be all green**

```bash
python tests/run_all.py 2>&1 | tail -5
```
Expected: `TOTAL: 484/484 passed` (or whatever total — point is `0 FAILED`). Warnings acceptable.

- [ ] **Step 4.7: Run plugin validator**

```bash
claude plugin validate .
```
Expected: passes (warnings acceptable).

- [ ] **Step 4.8: Verify no `%>%` regressed anywhere**

```bash
grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md || echo "no matches"
```
Expected: `no matches` (the `||` clause prints when grep finds nothing).

- [ ] **Step 4.9: Commit**

```bash
git add .github/workflows/test.yml README.md .claude-plugin/plugin.json CLAUDE.md
git commit -m "$(cat <<'EOF'
ci: add GitHub Actions test workflow and bump 0.2.2

Adds .github/workflows/test.yml — runs python tests/run_all.py on push to
main and on every PR, Ubuntu + Python 3.11, no caching needed (stdlib only).

Adds CI badge to README; bumps version badge and plugin.json to 0.2.2.

Updates CLAUDE.md roadmap: marks Phase 1 shipped, renumbers Phase 2 → 1
(auto-format hook) and Phase 3 → 2 (r-bayesian skill).
EOF
)"
```

---

## Task 5: Push branch and open the pull request

**Files:** none (git/gh operations)

- [ ] **Step 5.1: Push the branch with upstream tracking**

```bash
git push -u origin phase-1-ci-foundation
```
Expected: branch pushed, upstream set, GitHub Actions kicks off the new workflow against the merge-result tree of the PR (after Step 5.2).

- [ ] **Step 5.2: Open the pull request**

```bash
gh pr create --title "ci: add GitHub Actions test workflow and clean up pre-existing failures" --body "$(cat <<'EOF'
## Summary

Phase 1 of the roadmap (see `CLAUDE.md`). Adds `.github/workflows/test.yml` so every push to `main` and every PR runs `python tests/run_all.py`. Cleans up 10 pre-existing test failures so CI is green from the first run.

- **Commit 1 — `fix(tests):`** Inverts the stale `agent-no-frontmatter` check (post-0.2.0 convention requires frontmatter); replaces it with three checks that mirror the skill validation. Drops 5 stale failures.
- **Commit 2 — `fix(content):`** Trims `agents/r-statistician.md` 205 → 197 lines (Examples → bullets) and `rules/r-conventions.md` 159 → 148 lines (merged two MCP-related sections). No rules, examples, or severity levels removed.
- **Commit 3 — `feat(skill):`** Rewrites `r-mcp-setup` description with triggers + boundary block; adds `eval.md` modeled on `r-data-analysis/eval.md`. Closes the remaining 3 failures.
- **Commit 4 — `ci:`** Adds the workflow, the README badge, bumps `plugin.json` 0.2.1 → 0.2.2, and updates the roadmap.

## Test plan

- [ ] CI run on this PR is green (the workflow validates against the merge-result tree)
- [ ] Local `python tests/run_all.py` shows `0 FAILED`
- [ ] Local `claude plugin validate .` passes (warnings OK)
- [ ] No `%>%` introduced (`grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md`)
- [ ] README badge renders correctly on GitHub once the workflow has run at least once
EOF
)"
```
Expected: PR URL printed. Capture it for the next step.

- [ ] **Step 5.3: Wait for CI to complete and verify green**

```bash
gh pr checks --watch
```
Expected: all checks pass (green check next to "tests / test"). If any check fails, do NOT merge — diagnose and push a fix commit on the same branch.

---

## Task 6: Merge and clean up

**Files:** none (git/gh operations)

- [ ] **Step 6.1: Merge the PR (squash or merge — pick the project default)**

The repo doesn't currently have a documented merge strategy. Check recent merges:

```bash
git log --oneline --merges -5
```
If recent commits have no merge commits (linear history pattern), prefer `--squash`. If they do, prefer `--merge`. Default in this plan: `--squash` (matches the "single PR" framing of Phase 1).

```bash
gh pr merge --squash --delete-branch
```
Expected: PR merged into `main`, remote branch deleted.

- [ ] **Step 6.2: Update local main**

```bash
git switch main
git pull --ff-only
```
Expected: local `main` advances to include the squash-merge commit (or the merge commit, if `--merge` was used).

- [ ] **Step 6.3: Final sanity check on main**

```bash
python tests/run_all.py 2>&1 | tail -2
```
Expected: `0 FAILED` on `main`.

- [ ] **Step 6.4: Confirm CI badge renders on the README**

Visit `https://github.com/alexvantwisk/supeRpowers` and confirm the **Tests** badge near the top is green. (No command — visual check.)

---

## Verification summary

After Task 6 completes, the repository should satisfy all of:

- `python tests/run_all.py` → `0 FAILED`
- `.github/workflows/test.yml` exists and runs on push to main + PRs
- `plugin.json` shows `0.2.2`
- README has CI badge near the top
- CLAUDE.md roadmap has 2 phases (auto-format hook, r-bayesian skill)
- `agents/r-statistician.md` ≤ 200 lines
- `rules/r-conventions.md` ≤ 150 lines
- `skills/r-mcp-setup/SKILL.md` description has triggers + boundary; `eval.md` exists
- `tests/test_structural.py` validates agent frontmatter (3 checks per agent)

## Self-review notes

- **Spec coverage:** Every scope-decision row in the spec maps to at least one step here. Row 1 (triggers) → Step 4.1; Row 2-4 (runner / Python / no deps) → Step 4.1; Row 5 (commit strategy) → all four commit tasks; Row 6 (test fix details) → Task 1; Row 7-8 (trims) → Task 2; Row 9-10 (r-mcp-setup) → Task 3; Row 11 (version bump) → Step 4.4; Row 12 (badge) → Step 4.3.
- **Placeholders:** None. Every Edit step has full `old_string` / `new_string` content. Every test command has expected output.
- **Type/name consistency:** New check IDs `agent-frontmatter-exists`, `agent-frontmatter-fields`, `agent-name-matches-file` are used consistently in Task 1 step 1.4 grep, success-criteria, and verification summary. `parse_frontmatter` keys (`found`, `name`, `description`) match the conftest definition.
- **Risk: empty `new_string` in Step 4.5b.** If the Edit tool rejects empty replacement, the fallback (`"\n"` + cleanup) is documented inline. As a last resort, the implementer can use Read + Write to rewrite the file region.
