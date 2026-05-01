# Phase 1 — GitHub Actions CI Foundation — Design Spec

**Date:** 2026-04-30
**Author:** Alexander van Twisk (with Claude)
**Status:** Approved (brainstorm complete; pending implementation plan)
**Target:** Add CI to the `supeRpowers` Claude Code plugin and clean up the 10 pre-existing test failures so the first CI run is green.

---

## Goal

Every push to `main` and every pull request runs `python tests/run_all.py` automatically via GitHub Actions, and the suite is green from the first run. After this ships, contributors get automated regression coverage for every change, content drift is caught before merge, and the README carries a CI status badge that signals project health to the marketplace.

## Non-Goals

- **Phase 2 (PostToolUse auto-format hook)** and **Phase 3 (`r-bayesian` skill)** are out of scope. They depend on Phase 1 being green but are independently shippable.
- **Multi-version Python testing.** The test suite uses only the standard library; testing across multiple Python versions adds noise without catching anything.
- **Multi-OS matrix.** Tests are pure Python content validation, not anything OS-specific. Ubuntu-only is sufficient.
- **R installation in CI.** No R code runs during the test suite; tests are static content validation.
- **Caching dependencies.** Tests use stdlib only — there's nothing to cache.
- **Coverage reporting / Codecov.** The tests are themselves the validation; line coverage of test code adds no signal.
- **Pre-commit hooks (local).** Out of scope here; CI catches everything pre-commit would.

## Scope decisions (locked)

| # | Question | Decision |
|---|---|---|
| 1 | Workflow triggers | `push` to `main` + `pull_request` (matches CLAUDE.md verbatim; covers direct-to-main commits and the new PR contribution path) |
| 2 | Runner | `ubuntu-latest` only — no OS matrix |
| 3 | Python version | `3.11` only — no version matrix |
| 4 | Dependency install | None — tests use stdlib only |
| 5 | Commit/PR strategy | Single PR off branch `phase-1-ci-foundation`, four logical commits; CI workflow lands last so the PR validates itself |
| 6 | Stale `agent-no-frontmatter` check | Invert the assertion *and* rename the check ID to `agent-frontmatter-exists`; flip the error message; add a sibling check that verifies `name` + `description` fields and `name` matches the file stem |
| 7 | Trim strategy for r-statistician | Condense the three Examples (lines 193-205) by collapsing each "Input:"/"Output:" pair into a single paragraph; preserves every concrete recommendation |
| 8 | Trim strategy for r-conventions | Defer specific cuts to the implementation plan after reading the full file; constraint is "no rule, no example, no severity level disappears" |
| 9 | r-mcp-setup description | Rewrite to ~700 chars: "Use when..." + 5+ trigger phrases under a `Triggers:` line + "Do NOT use for:" boundary block pointing to domain skills (r-data-analysis, r-stats, etc.) |
| 10 | r-mcp-setup eval.md | Model on `skills/r-data-analysis/eval.md` — ~12 binary questions, 4-5 happy paths, 2-3 edge cases, 2-3 adversarial, 2-3 boundary tests; success criteria block |
| 11 | Version bump | `plugin.json` 0.2.1 → 0.2.2 (patch — infrastructure + bug fixes, no new user-facing features) |
| 12 | README badge | Standard GitHub Actions badge near the top of `README.md`, linking to the workflow runs page |

## Approach

**Single PR off `phase-1-ci-foundation` with four ordered commits.** Each commit leaves the working tree in a state where the test suite passes (or, in the case of commit 1, where the test suite *correctly* identifies the remaining content failures).

The workflow file lands in commit 4 — last — so that opening the PR triggers the very first CI run against a tree where every prior commit is already green. This dogfoods the new contribution path (CONTRIBUTING.md was just merged) and validates the workflow against real content on day one.

## Artifact inventory

```
.github/
  workflows/
    test.yml                              # NEW — 14-line minimal workflow

tests/
  test_structural.py                      # MODIFIED — invert agent-no-frontmatter check, add name/description sibling check

agents/
  r-statistician.md                       # MODIFIED — trim Examples to ≤200 lines

rules/
  r-conventions.md                        # MODIFIED — trim to ≤150 lines (specific cuts in plan)

skills/r-mcp-setup/
  SKILL.md                                # MODIFIED — rewrite description (triggers + boundary + 500-1024 chars)
  eval.md                                 # NEW — modeled on r-data-analysis/eval.md

README.md                                 # MODIFIED — add CI status badge
.claude-plugin/plugin.json                # MODIFIED — version 0.2.1 → 0.2.2
CLAUDE.md                                 # MODIFIED — strike Phase 1 entry from roadmap, mark complete
```

No skills, agents, commands, or rules are removed. No public-facing behavior changes.

## Commit plan (within the PR)

```
phase-1-ci-foundation
  ├─ 1. fix(tests): require agent frontmatter (invert stale check)
  │     • tests/test_structural.py: invert assertion, rename check ID, update error message
  │     • Add sibling check that verifies agent name+description fields, name == file stem
  │     • After this commit: 5 stale failures → 0; 5 real content failures remain
  │
  ├─ 2. fix(content): trim r-statistician and r-conventions to limits
  │     • agents/r-statistician.md: 205 → ≤200 lines (Examples collapsed)
  │     • rules/r-conventions.md: 159 → ≤150 lines (cuts decided in plan)
  │     • After this commit: 2 line-limit failures → 0
  │
  ├─ 3. feat(skill): rewrite r-mcp-setup description and add eval.md
  │     • skills/r-mcp-setup/SKILL.md: new description with triggers + boundary
  │     • skills/r-mcp-setup/eval.md: NEW
  │     • After this commit: 3 r-mcp-setup failures → 0; full suite green locally
  │
  └─ 4. ci: add GitHub Actions test workflow + README badge, bump 0.2.2
        • .github/workflows/test.yml: NEW
        • README.md: add badge near top
        • .claude-plugin/plugin.json: version 0.2.1 → 0.2.2
        • CLAUDE.md: strike Phase 1 from roadmap (mark Phase 1 complete)
        • After this commit: PR opens, CI fires, validates the entire branch
```

Each commit is independently revertable. Commit 1 has the most architectural value (a real test fix); commit 4 is the smallest, mechanical, but the most visible (the badge).

## Test workflow file content

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

`run_all.py` already exits non-zero on suite failure (`sys.exit(1 if failures else 0)` pattern in the existing runner), so no extra wiring is needed.

## r-mcp-setup description (target text)

Target ~700 chars, passes all four checks (`desc-starts-use-when`, `desc-length` 500-1024, `desc-has-triggers`, `desc-has-boundary`):

```
Use when the user wants to set up MCP tools in R or connect Claude Code to a
running R session — installing mcptools/btw, registering R-based MCP servers
via `claude mcp add`, choosing the right btw tool groups (docs, pkg, env,
run, search, session), or troubleshooting an MCP setup that isn't appearing
in Claude Code. Triggers: mcptools, btw, MCP server, live R session,
claude mcp add, btw_tool_*, "Claude can't see my R session". Do NOT use
for: writing R code that uses already-configured MCP tools (use the relevant
domain skill — r-data-analysis, r-stats, etc.); generic Claude Code MCP
setup unrelated to R; building new MCP servers from scratch.
```

## eval.md scope (r-mcp-setup)

Following the structure of `skills/r-data-analysis/eval.md`:

**Binary eval questions (~12):**
1. Setup mechanics — does it use `claude mcp add` rather than editing JSON manually?
2. Setup mechanics — does it pick stdio transport for mcptools?
3. Setup mechanics — does it know `btw::btw_mcp_server()` is the entrypoint?
4. Tool group choice — does it match `pkg` group to r-package-dev, `env` to data inspection, etc.?
5. Tool group choice — does it default to `docs + pkg + env + run` for general R work, not all six?
6. Troubleshooting — does it diagnose "tools not appearing" by checking transport + claude config?
7. Troubleshooting — does it surface renv/library path issues when MCP server fails to start?
8. Troubleshooting — does it handle R-not-on-PATH on macOS/Windows?
9. Conventions — does generated R code use `|>`, `<-`, snake_case, double quotes?
10. Boundary — does it defer to r-data-analysis when the user is *using* MCP tools, not setting them up?
11. Boundary — does it decline to build a new MCP server from scratch (out of scope)?
12. Boundary — does it decline to set up non-R MCP servers (out of scope)?

**Test prompts:**
- Happy path (4-5): fresh install on macOS, adding btw to existing setup, picking groups for a Shiny project, troubleshooting "Claude can't see R", reconfiguring after upgrading R.
- Edge cases (2-3): user has multiple R installs (rig); user runs Positron not RStudio; renv-locked project conflicts.
- Adversarial (2-3): user asks to build a custom MCP server; user wants to use mcptools to query a *Python* session; user wants MCP for a database.
- Boundary tests (2-3): "Use the R session to fit a model" → r-stats; "Show package check results" → r-package-dev; "Set up MCP for a Postgres DB" → out of scope.

**Success criteria block:** generated R code passes conventions; setup commands use `claude mcp add` not manual JSON; troubleshooting steps in priority order (config → transport → R PATH → renv); refuses out-of-scope politely with a pointer.

## r-statistician trim (target ≤200 lines, currently 205)

Lines 193-205 are three Examples in `Input:` / `Output:` block format (~13 lines). Collapsing each pair into a single paragraph trims ~5-7 lines and preserves every concrete recommendation. Target final length: ~198 lines.

**Constraint:** no example removed; every Severity level retained; every methodological recommendation kept verbatim.

## r-conventions trim (target ≤150 lines, currently 159)

Specific cuts deferred to the implementation plan after reading the full file. **Constraint:** no rule, no severity, no convention removed. The cuts are formatting / verbosity reductions only.

## Verification

After each commit on the branch (and again before opening the PR):

```bash
python tests/run_all.py        # must show 484/484 passed (no failures, warnings OK)
claude plugin validate .       # must pass (warnings acceptable)
```

After the PR opens, GitHub Actions runs `test.yml` against the merge-result tree. The PR is mergeable when CI is green.

Pre-merge sanity checks on the PR:
- Workflow status badge points to the right URL (`alexvantwisk/supeRpowers`)
- The PR template (newly added) renders correctly
- No `%>%` introduced (`grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md`)

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Trim cuts something load-bearing | Low | Constraint stated above; specific cuts surfaced for review if they touch a rule/example |
| eval.md questions don't match actual SKILL.md guidance | Low | Read SKILL.md fully before drafting eval; cross-check each binary question against a section |
| New `name` + `description` agent check fires unexpected failures | Medium | All 5 agent files already have correct frontmatter (verified during exploration); the check is a guard for future drift |
| README badge URL wrong | Low | Resolved from `git remote -v` (`alexvantwisk/supeRpowers`) before writing |
| GitHub Actions cache hit on stale workflow | N/A | No caching; workflow is stateless |

## Sequencing & follow-up

This spec is Phase 1 of three. After merge:

1. **Phase 1 complete** — strike from `CLAUDE.md` roadmap (commit 4)
2. **Phase 2** — separate spec when ready (PostToolUse auto-format hook)
3. **Phase 3** — separate spec when ready (`r-bayesian` skill)

Each phase is independently shippable. Phase 1 unblocks the others by giving them a green CI baseline.
