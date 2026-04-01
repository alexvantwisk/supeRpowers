# Plan 1: Workflow Command Skills

## Summary

Create 5 new workflow command skills (`r-cmd-*`) that orchestrate existing knowledge skills and agents into guided, multi-step R development workflows. Each command is a procedural skill with gates between steps, agent dispatch points, and abort conditions.

**Deliverables:** 5 new `skills/r-cmd-*/SKILL.md` files (100-150 lines each)

## Prerequisites

- Read the design spec: `docs/superpowers/specs/2026-04-01-commands-layer-design.md`
- Understand the command file format (Steps with Skill/Agent/Action/Gate structure)
- Read existing knowledge skills for tone/conventions (r-tdd, r-debugging, r-data-analysis)
- Read `rules/r-conventions.md` — all R code in examples must comply

## Implementation Tasks

### Task 1: Create `skills/r-cmd-tdd-cycle/SKILL.md`

- [ ] Create directory `skills/r-cmd-tdd-cycle/`
- [ ] Write SKILL.md (~120 lines)

**Frontmatter:**
```yaml
---
name: r-cmd-tdd-cycle
description: >
  Use when starting a test-driven development cycle for R code. Orchestrates
  r-tdd and r-debugging skills with the r-code-reviewer agent through a guided
  Red-Green-Refactor-Review workflow. Invoke as /r-cmd-tdd-cycle.
  Triggers: start TDD, TDD cycle, red green refactor, new feature with tests,
  test-first workflow.
  Do NOT use for testthat API reference without a full cycle — use r-tdd instead.
  Do NOT use for debugging existing code — use r-debugging instead.
---
```

**Steps:**
1. **Setup** — Skill: r-tdd. Action: Verify testthat 3e is configured, identify target function and test file. Gate: test file exists or is created.
2. **RED — Write failing test** — Skill: r-tdd. Action: Write `test_that()` block defining desired behavior. Gate: test runs and FAILS.
3. **GREEN — Minimal implementation** — Skill: r-tdd. Action: Write minimum code to pass. Gate: test runs and PASSES.
4. **REFACTOR** — Action: Improve code quality, naming, structure. Gate: all tests still pass.
5. **REVIEW** — Agent: r-code-reviewer (scope: full). Action: Review the new implementation. Gate: no CRITICAL findings.
6. **COVERAGE** — Skill: r-tdd. Action: Run `covr::package_coverage()`. Gate: coverage >= 80%.

**Abort conditions:**
- Test passes on first run (RED phase failed — test is wrong)
- CRITICAL finding in code review that requires architectural change
- Coverage drops below 80% after refactoring

**Examples:** (1) Adding a validation function to an R package. (2) Bug fix with regression test.

**Acceptance criteria:**
- [ ] YAML frontmatter has `name` and `description` only
- [ ] Description starts with "Use when starting..."
- [ ] Each step has Skill/Agent/Action/Gate structure
- [ ] Abort conditions section present
- [ ] 2 examples with Prompt and Flow
- [ ] All R code uses `|>`, `<-`, snake_case, double quotes
- [ ] Under 150 lines

---

### Task 2: Create `skills/r-cmd-pkg-release/SKILL.md`

- [ ] Create directory `skills/r-cmd-pkg-release/`
- [ ] Write SKILL.md (~140 lines)

**Frontmatter:**
```yaml
---
name: r-cmd-pkg-release
description: >
  Use when starting an R package release workflow. Orchestrates r-package-dev
  and r-tdd skills with r-pkg-check, r-dependency-manager, and r-code-reviewer
  agents through a guided check-test-document-build-submit pipeline. Invoke as
  /r-cmd-pkg-release.
  Triggers: release package, CRAN submission, package release, version bump,
  prepare release, submit to CRAN.
  Do NOT use for ongoing package development — use r-package-dev instead.
  Do NOT use for writing new tests — use r-cmd-tdd-cycle instead.
---
```

**Steps:**
1. **Dependency audit** — Agent: r-dependency-manager. Action: Check renv status, flag conflicts. Gate: no CRITICAL dependency issues.
2. **Run tests** — Skill: r-tdd. Action: `devtools::test()`, check coverage. Gate: all tests pass, coverage >= 80%.
3. **Document** — Skill: r-package-dev. Action: `devtools::document()`, check roxygen completeness. Gate: no undocumented exports.
4. **R CMD check** — Agent: r-pkg-check → escalate to r-dependency-manager on version conflicts, escalate to r-code-reviewer on code quality findings. Action: `devtools::check()`. Gate: 0 errors, 0 warnings, notes reviewed.
5. **Version bump** — Skill: r-package-dev. Action: `usethis::use_version()`, update NEWS.md. Gate: version incremented, NEWS updated.
6. **Final review** — Agent: r-code-reviewer (scope: full). Action: Review all changed files. Gate: no CRITICAL or HIGH findings.

**Abort conditions:**
- Failing tests that indicate broken functionality (not just style)
- R CMD check ERRORs that require architectural changes
- Dependency conflicts requiring upstream package updates

**Examples:** (1) Preparing a patch release for CRAN. (2) First CRAN submission of a new package.

---

### Task 3: Create `skills/r-cmd-analysis/SKILL.md`

- [ ] Create directory `skills/r-cmd-analysis/`
- [ ] Write SKILL.md (~130 lines)

**Frontmatter:**
```yaml
---
name: r-cmd-analysis
description: >
  Use when starting a data analysis pipeline in R. Orchestrates r-data-analysis,
  r-visualization, and r-stats skills with the r-statistician agent through a
  guided import-clean-explore-model-visualize workflow. Invoke as /r-cmd-analysis.
  Triggers: start analysis, data analysis pipeline, explore dataset, new analysis,
  analyze data, EDA workflow.
  Do NOT use for data wrangling reference — use r-data-analysis instead.
  Do NOT use for standalone visualization — use r-visualization instead.
---
```

**Steps:**
1. **Import** — Skill: r-data-analysis. Action: Read data with explicit `col_types`, inspect with `glimpse()`. Gate: data loaded, dimensions and types confirmed.
2. **Clean** — Skill: r-data-analysis. Action: Handle missing values, fix types, rename columns. Gate: no unexpected NAs in key columns, types correct.
3. **Explore** — Skill: r-data-analysis + r-visualization. Action: Summary statistics, distributions, correlations. Gate: key patterns identified, questions formed.
4. **Model** — Skill: r-stats. Agent: r-statistician when modeling decisions needed. Action: Fit model, check assumptions, interpret. Gate: assumptions met or documented violations.
5. **Visualize** — Skill: r-visualization. Action: Publication-quality plots of key findings. Gate: plots communicate findings clearly.
6. **Report** — Action: Summarize findings, limitations, next steps. Gate: narrative matches evidence.

**Abort conditions:**
- Data quality too poor to proceed (>50% missing in key variables)
- Model assumptions severely violated with no reasonable alternative
- Statistical findings contradicted by exploratory analysis (re-examine)

**Examples:** (1) Exploratory analysis of a CSV dataset. (2) Regression analysis with visualization.

---

### Task 4: Create `skills/r-cmd-shiny-app/SKILL.md`

- [ ] Create directory `skills/r-cmd-shiny-app/`
- [ ] Write SKILL.md (~140 lines)

**Frontmatter:**
```yaml
---
name: r-cmd-shiny-app
description: >
  Use when starting a new Shiny application. Orchestrates r-project-setup,
  r-shiny, and r-tdd skills with r-shiny-architect and r-code-reviewer agents
  through a guided scaffold-module-wire-test-review workflow. Invoke as
  /r-cmd-shiny-app.
  Triggers: new Shiny app, build dashboard, start Shiny, create Shiny,
  scaffold app, new dashboard.
  Do NOT use for Shiny API reference — use r-shiny instead.
  Do NOT use for project scaffolding without Shiny — use r-project-setup instead.
---
```

**Steps:**
1. **Scaffold** — Skill: r-project-setup. Action: Choose framework (golem/rhino/basic), initialize project structure. Gate: project structure created, app runs with placeholder UI.
2. **Module design** — Skill: r-shiny. Action: Identify modules from requirements, create `mod_*` files with UI and server functions. Gate: modules created with placeholder content.
3. **Wire reactivity** — Skill: r-shiny. Action: Connect modules, set up reactive data flow, implement server logic. Gate: app runs with functional reactivity.
4. **Test** — Skill: r-tdd. Action: Write shinytest2 tests for critical user flows. Gate: tests pass, key interactions covered.
5. **Architecture review** — Agent: r-shiny-architect → escalate to r-code-reviewer for implementation issues. Action: Review module structure, reactivity patterns, performance. Gate: no CRITICAL findings.

**Abort conditions:**
- Requirements too vague to identify modules (go back to user)
- Framework choice conflicts with deployment target
- Architecture review reveals fundamental reactivity design flaw

**Examples:** (1) Building a data exploration dashboard with golem. (2) Adding a new module to an existing Shiny app.

---

### Task 5: Create `skills/r-cmd-debug/SKILL.md`

- [ ] Create directory `skills/r-cmd-debug/`
- [ ] Write SKILL.md (~120 lines)

**Frontmatter:**
```yaml
---
name: r-cmd-debug
description: >
  Use when starting a systematic debugging session for R code. Orchestrates
  r-debugging and r-tdd skills with the r-code-reviewer agent through a guided
  reproduce-isolate-diagnose-fix-verify workflow. Invoke as /r-cmd-debug.
  Triggers: debug this, find bug, fix error, diagnose issue, start debugging,
  something is wrong, unexpected behavior.
  Do NOT use for debugging tool reference — use r-debugging instead.
  Do NOT use for writing tests outside a bug fix — use r-cmd-tdd-cycle instead.
---
```

**Steps:**
1. **Reproduce** — Skill: r-debugging. Action: Create minimal reprex that triggers the bug. Gate: bug reproduced deterministically (3x).
2. **Isolate** — Skill: r-debugging. Action: Binary search through pipeline, insert `browser()`. Gate: failure narrowed to specific function/line.
3. **Diagnose** — Skill: r-debugging. Action: Inspect call stack, check common gotchas (NSE, recycling, factor-to-numeric). Gate: root cause identified and documented.
4. **Fix** — Action: Apply minimal change addressing root cause. Gate: reprex from Step 1 no longer fails.
5. **Regression test** — Skill: r-tdd. Action: Write test that would have caught this bug. Gate: test passes with fix, fails without.
6. **Verify** — Agent: r-code-reviewer (scope: full). Action: Review fix for correctness and side effects. Gate: no CRITICAL findings, fix is minimal.

**Abort conditions:**
- Cannot reproduce the bug (ask user for more context)
- Root cause is in an external package (file upstream issue)
- Fix requires architectural change beyond scope of bug fix

**Examples:** (1) Function returns wrong results for edge case. (2) Error only in non-interactive mode (`Rscript --vanilla`).

---

## Verification Checklist

After all 5 commands are created:

- [ ] All 5 files exist: `skills/r-cmd-{tdd-cycle,pkg-release,analysis,shiny-app,debug}/SKILL.md`
- [ ] All files have YAML frontmatter with exactly `name` and `description`
- [ ] All descriptions start with "Use when starting..."
- [ ] All descriptions include "Do NOT use for..." boundaries
- [ ] All steps have the Skill/Agent/Action/Gate structure
- [ ] All files have Abort Conditions section
- [ ] All files have 2 Examples
- [ ] No `%>%` anywhere: `grep -rn '%>%' skills/r-cmd-*/`
- [ ] All files under 150 lines: `wc -l skills/r-cmd-*/SKILL.md`
- [ ] All files have correct `name` matching directory name
- [ ] `plugin.json` glob `skills/*/SKILL.md` discovers all 5 new skills
