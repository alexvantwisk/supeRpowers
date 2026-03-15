# Phase 2: Package Development & Shiny Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking. **CRITICAL:** When creating any SKILL.md file, you MUST invoke the `superpowers:writing-skills` skill FIRST before writing.

**Goal:** Deliver two domain skills (r-package-dev, r-shiny) and three shared agents (r-pkg-check, r-shiny-architect, r-dependency-manager) for Phase 2 of the supeRpowers plugin.

**Architecture:** Same layered design as Phase 1. Skills get YAML frontmatter with `name` and `description`. Agents use Inputs/Output/Procedure format without frontmatter. All R code follows `r-conventions.md`.

**Tech Stack:** Claude Code skills/agents (YAML frontmatter + markdown), R >= 4.1.0, tidyverse ecosystem, usethis, devtools, roxygen2, testthat 3e, golem, bslib, shinytest2.

**Spec:** `.claude/plans/2026-03-15-superpowers-r-plugin-design.md` (lines 164-193 for Phase 2)

**Prerequisites:**
- Phase 1 complete (r-conventions.md, 4 core skills, r-code-reviewer agent)
- `superpowers:writing-skills` — for SKILL.md authoring
- **Hook constraint:** Agent .md files in `.claude/agents/` must be created via Bash heredoc (Write tool blocked by hook for that path)

---

## Task 1: Create r-package-dev skill

**Files:**
- Create: `.claude/skills/r-package-dev/SKILL.md`
- Create: `.claude/skills/r-package-dev/references/cran-submission-checklist.md`
- Create: `.claude/skills/r-package-dev/references/class-systems-guide.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-package-dev
description: >
  Use when creating, developing, documenting, or submitting R packages. Covers
  usethis, devtools, roxygen2, pkgdown, CRAN submission, and CI/CD.
---
```

**Body must cover (max 300 lines):**
- Scaffold: `usethis::create_package()`, `use_testthat(3)`, `use_pipe()`, `use_roxygen_md()`, `use_mit_license()`, `use_git()`, `use_github()`
- Dev loop: `devtools::load_all()` → `devtools::test()` → `devtools::check()` → `devtools::document()`
- Documentation: roxygen2 with markdown, `@examples`, `@param`, `@returns`, `@family`, tidy eval tags
- NAMESPACE management: `use_import_from()`, `use_package()`, `@importFrom` vs `pkg::fun()`
- Class systems overview (brief): S3 primary, S4 for Bioconductor, R7 for greenfield, R6 for mutable state
- Compiled code: `usethis::use_rcpp()`, basic Rcpp workflow
- Vignettes: `usethis::use_vignette()`, rmarkdown or quarto
- pkgdown: `usethis::use_pkgdown()`, `pkgdown::build_site()`, customization
- CRAN submission: `devtools::check(cran = TRUE)`, `rhub::check_for_cran()`, NEWS.md, cran-comments.md
- CI/CD: `usethis::use_github_action()` — R CMD check, coverage, pkgdown deploy
- Dispatch to `r-pkg-check` agent after `devtools::check()` for issue resolution
- Dispatch to `r-dependency-manager` agent for dependency questions
- Lazy references: "Read `references/cran-submission-checklist.md`" and "Read `references/class-systems-guide.md`"
- 3-5 example prompts

**Reference: cran-submission-checklist.md** — Step-by-step CRAN submission guide:
- Pre-submission checks, R CMD check must pass with 0 errors/warnings
- Acceptable vs problematic NOTEs
- NEWS.md format, cran-comments.md template
- `urlchecker::url_check()`, `spelling::spell_check_package()`
- Resubmission protocol, reviewer response etiquette
- Common rejection reasons and fixes

**Reference: class-systems-guide.md** — R class system comparison:
- S3: constructor/validator/methods pattern, `UseMethod()`, when to use
- S4: formal classes, `setClass()`, `setGeneric()`, `setMethod()`, Bioconductor requirements
- R7: modern replacement for S3/S4, `new_class()`, `new_generic()`, when to choose
- R6: reference semantics, `R6Class`, when mutable state is needed (caching, connections)
- Decision tree: which system for which use case

---

## Task 2: Create r-shiny skill

**Files:**
- Create: `.claude/skills/r-shiny/SKILL.md`
- Create: `.claude/skills/r-shiny/references/reactivity-guide.md`
- Create: `.claude/skills/r-shiny/references/modules-patterns.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-shiny
description: >
  Use when building, structuring, testing, or deploying Shiny applications.
  Covers reactivity, modules, golem/rhino, bslib, shinytest2, and deployment.
---
```

**Body must cover (max 300 lines):**
- Reactivity: `reactive()`, `observe()`, `observeEvent()`, `reactiveVal()`, `reactiveValues()`, `isolate()`, `req()`
- Modules: `moduleServer()` with namespacing via `NS()`, inter-module communication patterns
- Frameworks: golem (default recommendation), rhino for enterprise
- UI: `bslib` for theming (`bs_theme()`, `page_sidebar()`, `card()`), responsive layouts, `htmltools`
- Dynamic UI: `renderUI()`/`uiOutput()`, `insertUI()`/`removeUI()`, `conditionalPanel()`
- Testing: `shinytest2` for integration, `testServer()` for module unit tests
- JavaScript integration: custom input bindings, `Shiny.setInputValue()`, htmlwidgets in Shiny
- Performance: `bindCache()`, async with `promises`/`future`, `shiny::devmode()`
- Deployment: shinyapps.io, Posit Connect, ShinyProxy, Docker
- Dispatch to `r-shiny-architect` agent for structure review
- Lazy references: "Read `references/reactivity-guide.md`" and "Read `references/modules-patterns.md`"
- 3-5 example prompts

**Reference: reactivity-guide.md** — Deep reactivity patterns:
- Reactive graph mental model (sources → conductors → endpoints)
- `reactive()` vs `observe()` vs `observeEvent()` decision tree
- Isolation patterns: `isolate()`, `bindEvent()`, debounce/throttle
- `reactiveVal()` vs `reactiveValues()`: when to use each
- Anti-patterns: reactive spaghetti, unnecessary invalidation, `observe()` with side effects
- Debugging reactivity: `reactlog::reactlog_enable()`, reactive graph visualization
- Performance: `bindCache()` patterns, `req()` for short-circuiting

**Reference: modules-patterns.md** — Module architecture:
- Basic module: UI function + server function with `moduleServer()`
- NS() namespacing: how it works, common mistakes
- Inter-module communication: returning reactive values, shared reactiveValues, R6 stores
- Nested modules: parent-child patterns
- Module testing: `testServer()` with module args
- golem module conventions: `mod_*_ui()` / `mod_*_server()`
- Common patterns: CRUD modules, filter modules, display modules

---

## Task 3: Create r-pkg-check agent

**Files:**
- Create: `.claude/agents/r-pkg-check.md`

**Agent format (no YAML frontmatter). Max 200 lines.**

**Must cover:**
- Inputs: R CMD check output (text) or package root path
- Output: Categorized report (ERROR/WARNING/NOTE) with root cause and fix
- Procedure:
  1. Parse check output into categories
  2. For each issue: identify root cause, provide specific fix
  3. Common NOTEs: "no visible binding" → `.data$`, missing imports → `usethis::use_import_from()`, undocumented args → roxygen2
  4. Flag CRAN-specific concerns: acceptable vs problematic NOTEs
  5. Cross-platform issues (Windows paths, encoding)
  6. Suggest correct `usethis::use_*()` calls for structural fixes
- Severity guide for ERROR/WARNING/NOTE

---

## Task 4: Create r-shiny-architect agent

**Files:**
- Create: `.claude/agents/r-shiny-architect.md`

**Agent format (no YAML frontmatter). Max 200 lines.**

**Must cover:**
- Inputs: Shiny app root directory. Optional: specific concern (performance, modularity, security)
- Output: Architecture review with findings by category
- Procedure:
  1. Scan app structure (server.R/ui.R or app.R, modules/, R/, tests/)
  2. Evaluate module decomposition: size, coupling, namespacing
  3. Audit reactivity: reactive spaghetti, unnecessary invalidation, missing `isolate()`
  4. Check performance: unbounded chains, missing `bindCache()`, large session data
  5. Review security: input validation, SQL injection via inputs, file upload handling
  6. Assess architecture: golem/rhino adherence, business logic separation
- Severity levels for findings

---

## Task 5: Create r-dependency-manager agent

**Files:**
- Create: `.claude/agents/r-dependency-manager.md`

**Agent format (no YAML frontmatter). Max 200 lines.**

**Must cover:**
- Inputs: Project root path. Optional: specific concern (conflict, audit, setup)
- Output: State assessment, issues, recommended actions
- Procedure:
  1. Check renv.lock presence and renv status
  2. Audit dependencies: heavy/unnecessary deps, lighter alternatives
  3. Diagnose version conflicts with resolution steps
  4. Handle Bioconductor + CRAN coexistence in renv
  5. Review lock file for concerning pins or missing packages
  6. Recommend `renv::init()`, `renv::snapshot()`, or `renv::restore()`

---

## Execution Strategy

**Tasks 1-2** (Skills): Execute in PARALLEL — fully independent. Each subagent must invoke `superpowers:writing-skills`.

**Tasks 3-5** (Agents): Execute in PARALLEL — fully independent. Created via Bash heredoc due to hook constraint.

**All 5 tasks** are independent and can run simultaneously.

**Git strategy:** Each subagent creates files but does NOT commit. Orchestrator commits all files after verification.

**Verification:** After all tasks complete, verify file existence, line counts, YAML frontmatter, and no `%>%` usage.

```
    ┌──────────┬──────────┬──────────┬──────────┬──────────┐
    │ Task 1   │ Task 2   │ Task 3   │ Task 4   │ Task 5   │
    │ pkg-dev  │ shiny    │ pkg-chk  │ shiny-   │ dep-     │
    │ skill    │ skill    │ agent    │ arch agt │ mgr agt  │
    └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
         └──────────┴──────────┴──────────┴──────────┘
                              │
                         Verification
                         & Commit
```
