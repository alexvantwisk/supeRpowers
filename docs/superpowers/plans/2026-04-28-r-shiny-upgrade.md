# r-shiny Skill Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `skills/r-shiny/` to cover the four production frameworks (base, golem, rhino, teal) with structured deployment + testing references, an expanded trigger surface, and refreshed eval coverage — without exceeding skill size limits.

**Architecture:** Single-skill rewrite (Approach B from the spec). Keep two existing references (`reactivity-guide.md`, `modules-patterns.md`) untouched, add seven new lazy-loaded references, rewrite `SKILL.md` under a new outline, refresh `eval.md`, and make two small additions to the `r-shiny-architect` agent. Implementation runs in a dedicated git worktree on `feature/r-shiny-upgrade`.

**Tech Stack:** Markdown (skill content), Python 3 (test harness `tests/run_all.py`), Bash (verification), R (illustrative code blocks inside skill content — `|>`, `<-`, snake_case, double quotes only).

**Spec:** `docs/superpowers/specs/2026-04-28-r-shiny-upgrade-design.md`

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `.claude/worktrees/r-shiny-upgrade/` | Create (worktree) | Isolated working directory for the upgrade |
| `skills/r-shiny/SKILL.md` | Rewrite | New 18-section outline, ≤290 lines, expanded triggers + boundary lines |
| `skills/r-shiny/eval.md` | Modify | Add 5 binary questions, 7 prompts, 5 success criteria; preserve existing content verbatim |
| `skills/r-shiny/references/reactivity-guide.md` | Keep | No changes |
| `skills/r-shiny/references/modules-patterns.md` | Keep | No changes |
| `skills/r-shiny/references/frameworks-decision.md` | Create | Side-by-side base / golem / rhino / teal comparison |
| `skills/r-shiny/references/golem.md` | Create | golem deep dive (scaffolding, modules, config, dockerfile) |
| `skills/r-shiny/references/rhino.md` | Create | rhino deep dive (box, Sass, view/logic split) |
| `skills/r-shiny/references/teal.md` | Create | teal deep dive — clinical-trial dashboards on CDISC ADaM/SDTM |
| `skills/r-shiny/references/ui-frameworks-alt.md` | Create | bs4Dash / shinyMobile / shiny.semantic / argonDash short reference |
| `skills/r-shiny/references/testing.md` | Create | testServer + shinytest2 deep dive, golem/teal test conventions, CI |
| `skills/r-shiny/references/deployment.md` | Create | Posit Connect, shinyapps.io, Docker+ShinyProxy, Shiny Server, renv |
| `skills/r-shiny/scripts/check_modules.R` | Keep | No changes |
| `agents/r-shiny-architect.md` | Modify | Two surgical additions (teal pattern detection in step 1, teal subsection in step 6) |
| `tests/routing_matrix.json` | Modify (optional) | Add positive r-shiny routing tests (golem, teal, deployment, testing) |

---

## Conventions Reminder (apply to ALL new content)

Every R code block, every example, every line must use:
- `|>` (base pipe) — never `%>%` (magrittr).
- `<-` for assignment — never `=` (except inside function arguments).
- `snake_case` for all identifiers.
- Double quotes for strings — never single quotes.
- Tidyverse-first (dplyr, tidyr, purrr, ggplot2, readr, stringr, forcats, lubridate).
- Target R ≥ 4.1.0.

After every file write, run a local convention check (commands embedded in each task).

---

## Task 1: Set up isolated worktree

**Files:**
- Create: `.claude/worktrees/r-shiny-upgrade/` (worktree root)
- Branch: `feature/r-shiny-upgrade` (created off `main`)

- [ ] **Step 1: Verify clean working tree on main**

Run from `/Users/alexandervantwisk/Desktop/Projects/supeRpowers`:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
```

Expected: empty output (or only untracked `.claude/worktrees/`, `.vscode/`); current branch `main`.

- [ ] **Step 2: Create the worktree**

Run from the repo root:

```bash
git worktree add -b feature/r-shiny-upgrade .claude/worktrees/r-shiny-upgrade main
```

Expected: `Preparing worktree (new branch 'feature/r-shiny-upgrade')` then `HEAD is now at <sha> ...`.

- [ ] **Step 3: Verify worktree**

```bash
git worktree list
ls .claude/worktrees/r-shiny-upgrade/skills/r-shiny/
```

Expected: worktree path listed; r-shiny directory visible inside the worktree (SKILL.md, eval.md, references/, scripts/).

- [ ] **Step 4: Switch into the worktree for all subsequent work**

All subsequent tasks operate inside `.claude/worktrees/r-shiny-upgrade/`. Treat that path as the new working directory; do not edit files in the main checkout.

```bash
cd .claude/worktrees/r-shiny-upgrade
pwd
```

Expected: `/Users/alexandervantwisk/Desktop/Projects/supeRpowers/.claude/worktrees/r-shiny-upgrade`.

---

## Task 2: Write `references/frameworks-decision.md`

**Files:**
- Create: `skills/r-shiny/references/frameworks-decision.md`
- Target: ~120 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Shiny Framework Decision Guide`

Required sections (in order):
1. **At-a-glance comparison table** — columns: framework, file layout, learning curve, deployment fit, signature feature.
2. **base Shiny (`app.R`, `ui.R`/`server.R`)** — when to use (prototypes, <500 lines, single-author), exit signals (need modules across files, need tests, ≥3 logical components).
3. **golem** — when to use (production R package, multi-author teams, deployment to Posit Connect/Docker, want CRAN-style structure), exit signals (need box-style imports, need first-class Sass, single-page enterprise UI).
4. **rhino** — when to use (Appsilon-style enterprise apps, want box modules, Sass pipeline, Cypress E2E, opinionated linting), exit signals (team unfamiliar with `box::use()`, want CRAN-publishable artifact).
5. **teal** — when to use (clinical-trial dashboards on CDISC ADaM/SDTM, declarative module pipelines, integrated filter panel, validated regulated environments), exit signals (data is not CDISC-shaped, need fully custom UX outside teal's frame).
6. **Decision tree (text)** — `Is your data CDISC ADaM/SDTM?` → teal; else `Production package + Posit Connect?` → golem; else `Enterprise SPA with box modules?` → rhino; else base Shiny.
7. **Migration cheat sheet** — base → golem (`golem::create_golem(pkg = "myapp")`, move `ui.R`/`server.R` into `R/app_ui.R`/`R/app_server.R`, wrap modules with `golem::add_module`); base → teal (define `teal.data::cdisc_data()`, register modules via `teal::init()`).

Required cross-links: link to `golem.md`, `rhino.md`, `teal.md` for deep dives; link to `../SKILL.md` for the picker entry point.

- [ ] **Step 2: Convention check on the file**

```bash
grep -n '%>%' skills/r-shiny/references/frameworks-decision.md
grep -nE '^[^#]*[A-Za-z_][A-Za-z0-9_]* = [^=]' skills/r-shiny/references/frameworks-decision.md | grep -v 'function('
wc -l skills/r-shiny/references/frameworks-decision.md
```

Expected: zero `%>%` hits; zero `=`-as-assignment hits in R code (matches inside function calls and frontmatter ignored manually); line count between 80 and 140.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/frameworks-decision.md
git commit -m "docs(r-shiny): add frameworks-decision reference

Side-by-side comparison of base, golem, rhino, and teal with a
decision tree and migration cheat sheet."
```

---

## Task 3: Write `references/golem.md`

**Files:**
- Create: `skills/r-shiny/references/golem.md`
- Target: ~250 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# golem Deep Dive`

Required sections (in order):
1. **Why golem** — package-as-app, env profiles, opinionated structure, deployment-ready.
2. **Scaffolding** — `golem::create_golem(pkg = "myapp")`, the `R/app_ui.R` / `R/app_server.R` / `R/run_app.R` layout, `inst/golem-config.yml`, `inst/app/www/`.
3. **Adding modules** — `golem::add_module(name = "filter")` produces `R/mod_filter.R` with `mod_filter_ui()` / `mod_filter_server()`. Show full generated structure plus a wired example calling `mod_filter_server("filter1", data = reactive(mtcars))`.
4. **Business logic separation** — `golem::add_fct("etl")` for impure functions, `golem::add_utils("formatting")` for pure helpers; rule: never put business logic in `mod_*`.
5. **Configuration via `golem-config.yml`** — env profiles (default / production / dev), reading values with `golem::get_golem_config()`, golden-path-safe paths via `golem::app_sys()`.
6. **Data files** — `inst/extdata/` for static, `data/` for package-level rda; load with `system.file()` or `golem::app_sys()`.
7. **Running locally vs production** — `run_app(options = list(port = 1234))`, dev profile, `golem::with_golem_options()`.
8. **Dockerization** — `golem::add_dockerfile()` (basic), `golem::add_dockerfile_shinyproxy()`, multi-stage build pattern, `renv::snapshot()` requirement.
9. **Testing layout** — `tests/testthat/test-mod_*.R` mirrors `R/mod_*.R`; uses `testServer()` for module reactives + `shinytest2::AppDriver` for the app entry point. Cross-link to `testing.md`.
10. **Common gotchas** — table form: golden-path violations (using `getwd()`), missing `golem::app_sys()` on installed package, `inst/app/www/` vs `www/` confusion, namespacing forgotten on dynamic UI inside modules, `bookmarkable_state = TRUE` requirements.
11. **When NOT to use golem** — pure prototype (use single-file), need `box::use()` semantics (use rhino), CDISC ADaM data (use teal).

Required code blocks:
- `golem::create_golem("myapp")` complete output structure (tree).
- One full module file (`R/mod_filter.R`) — UI + server, properly namespaced.
- One `golem-config.yml` example with three profiles.
- Skeleton multi-stage `Dockerfile` (shinyproxy variant).

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/golem.md
wc -l skills/r-shiny/references/golem.md
```

Expected: zero `%>%`; line count 200–280.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/golem.md
git commit -m "docs(r-shiny): add golem deep-dive reference

Covers scaffolding, module addition, business logic separation,
golem-config.yml profiles, dockerfile generation, testing layout,
and common gotchas."
```

---

## Task 4: Write `references/rhino.md`

**Files:**
- Create: `skills/r-shiny/references/rhino.md`
- Target: ~180 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# rhino Deep Dive`

Required sections (in order):
1. **Why rhino** — Appsilon's enterprise framework: box modules, Sass, opinionated linting, Cypress + shinytest2.
2. **Scaffolding** — `rhino::init("myapp")`. Show generated tree: `app/main.R`, `app/view/`, `app/logic/`, `app/static/`, `app/styles/`, `tests/`, `rhino.yml`, `dependencies.R`, `config.yml`.
3. **`box::use()` pattern** — explain `box::use(shiny[...], dplyr[...])`, contrast with `library()`, why box gives explicit imports per file. Show an `app/view/filter.R` and `app/logic/data.R` with realistic `box::use()` blocks.
4. **View / logic split** — view modules (UI + render glue) live in `app/view/`; pure functions in `app/logic/`. The rule: no `library()` calls anywhere — every file declares its imports.
5. **Sass pipeline** — `app/styles/main.scss` compiled automatically; per-component partials with `_filter.scss`. Hot reload during dev.
6. **`rhino.yml` configuration** — sass options, JS options, reload behaviour.
7. **Testing** — Cypress (E2E browser tests in `tests/cypress/`), shinytest2 (R-level), unit tests via testthat in `tests/testthat/`. Cross-link to `testing.md`.
8. **Linting and CI** — `rhino::lint_r()`, `rhino::lint_sass()`, `rhino::lint_js()`; opinionated: `lintr`, `box.linters`.
9. **Migration from base/golem to rhino** — when it pays off (large enterprise team, heavy CSS), when it doesn't (CRAN package goal, R-only contributors).
10. **rhino-specific gotchas** — forgetting to declare a `box::use()` import → "object not found"; mixing `library()` with rhino → CI lint failure; module reload after Sass change.

Required code blocks:
- `app/view/filter.R` skeleton with `box::use()` block + UI/server functions.
- `app/logic/data.R` with `box::use(dplyr[filter, mutate])` and a pure function returning a tibble.
- Snippet of `rhino.yml`.

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/rhino.md
wc -l skills/r-shiny/references/rhino.md
```

Expected: zero `%>%`; line count 150–210.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/rhino.md
git commit -m "docs(r-shiny): add rhino deep-dive reference

Covers box::use() imports, view/logic split, Sass pipeline,
rhino.yml, Cypress + shinytest2 testing, and migration signals."
```

---

## Task 5: Write `references/teal.md`

**Files:**
- Create: `skills/r-shiny/references/teal.md`
- Target: ~330 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# teal Deep Dive — Clinical-Trial Dashboards on CDISC Data`

Required sections (in order):
1. **What teal is** — Roche/Genentech NEST framework for declarative clinical-trial dashboards. Built on Shiny modules; assumes CDISC ADaM/SDTM-shaped data.
2. **Package ecosystem** — table:
   | Package | Purpose |
   |---|---|
   | `teal` | Core framework, `init()` |
   | `teal.data` | Dataset definitions, joining keys, `cdisc_data()`, `cdisc_dataset()` |
   | `teal.slice` | Filter panel (range, date, multi-select, regex) |
   | `teal.transform` | `data_extract_spec()` for variable selectors and filtering UI |
   | `teal.modules.general` | Standard non-clinical modules (table, scatterplot, regression) |
   | `teal.modules.clinical` | Clinical-specific modules (`tm_a_patient_profile`, `tm_t_summary`, `tm_g_km`, `tm_a_mmrm`, etc.) |
   | `teal.code` | Reproducible R code log of every interaction |
   | `teal.logger` | Structured logging |
3. **Defining datasets — `teal.data::cdisc_data()`** — Show full example wrapping `ADSL`, `ADAE`, `ADTTE` with proper join keys (`USUBJID`, `STUDYID`). Include `cdisc_dataset(dataname, x, keys = c("STUDYID", "USUBJID"))`. Discuss why join keys matter for cross-module filtering.
4. **Initialising the app — `teal::init()`** — Declarative pipeline:
   ```r
   app <- teal::init(
     data = teal_data,
     modules = modules(
       teal.modules.general::tm_data_table("Data"),
       teal.modules.clinical::tm_t_summary("Summary", dataname = "ADSL", arm_var = "ARM"),
       teal.modules.clinical::tm_g_km(
         "Kaplan-Meier",
         dataname = "ADTTE",
         arm_var = teal.transform::choices_selected(c("ARM", "ACTARM"), "ARM"),
         time_var = teal.transform::choices_selected("AVAL", "AVAL"),
         cnsr_var = teal.transform::choices_selected("CNSR", "CNSR")
       )
     ),
     filter = teal.slice::teal_slices(
       teal.slice::teal_slice(dataname = "ADSL", varname = "AGE", selected = c(18, 100))
     )
   )
   shiny::shinyApp(app$ui, app$server)
   ```
5. **Standard `teal.modules.clinical` modules** — bullet list with one-line descriptions: `tm_a_patient_profile`, `tm_t_summary`, `tm_t_ae`, `tm_g_km`, `tm_a_mmrm`, `tm_a_ancova`, `tm_t_logistic`, `tm_t_shift_by_grade`. Note: each has its own `args()` for variable selectors.
6. **`teal.transform::choices_selected()`** — wraps a variable selector input. Show with both eager and lazy choices via `data_extract_spec()` for cross-dataset references.
7. **`teal.slice::teal_slices()`** — pre-set filter state. Show single-variable, multi-variable, and locked filters.
8. **Custom module authoring — `teal::module()`** — Required signature:
   ```r
   tm_my_custom <- function(label = "My module", dataname = "ADSL", ...) {
     teal::module(
       label = label,
       server = function(id, data) {
         moduleServer(id, function(input, output, session) {
           # access reactive ADSL via data()[["ADSL"]]
         })
       },
       ui = function(id, ...) {
         ns <- NS(id)
         # UI here
       },
       datanames = dataname
     )
   }
   ```
   Note: never construct teal modules with raw `moduleServer` — always wrap in `teal::module()` so they integrate with filter panel and reproducibility log.
9. **Reproducibility log (`teal.code`)** — every user interaction emits R code; users can download the script that recreates the displayed analysis. Critical for regulated environments.
10. **Validation reports** — link to NEST CRAN releases; mention FDA/EMA-aware validation status varies by sponsor; teal apps deployed to Posit Connect with renv lockfiles are the standard pharma path.
11. **Bridge to `r-clinical`** — for *what* ADSL/ADAE/ADTTE *contain* (USUBJID semantics, AVAL/AVALC, AVISIT, CNSR), the standard ADaM Implementation Guide (ADaMIG), and SDTM domain definitions, defer to the `r-clinical` skill. teal handles the *app structure*; r-clinical handles the *domain*.
12. **Common gotchas** — table form:
    | Trap | Why It Fails | Fix |
    |---|---|---|
    | "no datasets defined" error | Forgot to wrap data in `cdisc_dataset()` or omitted `keys` | Use `cdisc_data(adsl = cdisc_dataset("ADSL", ADSL, keys = c("STUDYID", "USUBJID")))` |
    | Module shows empty selectors | `choices_selected()` referencing a variable not in `dataname` | Verify variable exists; pass correct dataname |
    | Filter panel ignores my pre-set | Mismatched dataname in `teal_slice()` | Match `dataname` exactly |
    | Custom module reactivity broken | Wrote raw `moduleServer` instead of `teal::module()` | Wrap with `teal::module()` |
    | Cross-module filter not propagating | Missing join keys in `teal.data::cdisc_data()` | Define keys; teal joins on shared keys |
    | Reproducibility log empty | Used `renderPlot` etc directly instead of `teal_reactive()` | Use teal-aware reactives so code is captured |
13. **When NOT to use teal** — non-CDISC data shapes, fully custom UX outside teal's filter-panel + module-tab paradigm, prototypes (use base Shiny first).

Required code blocks (full and runnable, not skeletons):
- A complete `app.R` using `teal::init()` with three modules over ADSL/ADAE/ADTTE.
- A custom-module skeleton using `teal::module()`.

Cross-links: `frameworks-decision.md`, `testing.md`, `deployment.md`, and the `r-clinical` skill (`../../r-clinical/SKILL.md`).

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/teal.md
wc -l skills/r-shiny/references/teal.md
```

Expected: zero `%>%`; line count 280–360.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/teal.md
git commit -m "docs(r-shiny): add teal deep-dive reference for clinical dashboards

Covers teal.data CDISC dataset definition, teal::init() declarative
pipelines, standard teal.modules.clinical modules, custom module
authoring, teal.slice filter pre-sets, teal.code reproducibility log,
and the bridge to r-clinical for ADaM/SDTM domain semantics."
```

---

## Task 6: Write `references/ui-frameworks-alt.md`

**Files:**
- Create: `skills/r-shiny/references/ui-frameworks-alt.md`
- Target: ~70 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Alternative UI Frameworks`

Required sections — one short subsection per framework (~12–15 lines each):
1. `bs4Dash` — Bootstrap 4 dashboard look-alike (AdminLTE 3). Install: `install.packages("bs4Dash")`. Hello-world snippet (`bs4Dash::dashboardPage(...)`). When to pick: want shinydashboard look on Bootstrap 4 without bslib redesign. Gotcha: not Bootstrap 5; cannot mix with bslib's `page_navbar()`.
2. `shinyMobile` — Framework7-based mobile-optimised UI. Install: `install.packages("shinyMobile")`. Hello-world snippet (`shinyMobile::f7Page(...)`). When to pick: targeting mobile-first apps (field data capture). Gotcha: heavy JS bundle; not for rich dashboards.
3. `shiny.semantic` — Semantic UI / Fomantic UI. Install: `install.packages("shiny.semantic")`. Hello-world snippet (`shiny.semantic::semanticPage(...)`). When to pick: design team committed to Semantic UI. Gotcha: smaller component ecosystem than bslib; some bslib idioms don't translate.
4. `argonDash` — Creative Tim Argon design. Install: `install.packages("argonDash")`. Hello-world snippet (`argonDash::argonDashPage(...)`). When to pick: marketing-style dashboards. Gotcha: low maintenance velocity; verify last release date before adopting.

Closing line: "Default remains bslib (Bootstrap 5). Pick an alternative only if a hard requirement forces it."

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/ui-frameworks-alt.md
wc -l skills/r-shiny/references/ui-frameworks-alt.md
```

Expected: zero `%>%`; line count 50–90.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/ui-frameworks-alt.md
git commit -m "docs(r-shiny): add alternative UI frameworks reference

Short reference for bs4Dash, shinyMobile, shiny.semantic, and
argonDash with install, hello-world, and pick-criteria. Reinforces
bslib as the default."
```

---

## Task 7: Write `references/testing.md`

**Files:**
- Create: `skills/r-shiny/references/testing.md`
- Target: ~250 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Shiny Testing Deep Dive`

Required sections (in order):
1. **Two-layer strategy** — `testServer()` for module reactives (fast, no browser), `shinytest2::AppDriver` for full-app integration (real browser, slower). Decision table when to use which.
2. **`testServer()` fundamentals** — full code block:
   ```r
   test_that("filter module returns filtered data", {
     testServer(mod_filter_server, args = list(data = reactive(mtcars)), {
       session$setInputs(column = "mpg", range = c(20, 30))
       result <- session$getReturned()()
       expect_true(all(result$mpg >= 20 & result$mpg <= 30))
     })
   })
   ```
   Cover: `session$setInputs()`, `session$getReturned()`, `session$elapsed()` for time travel, `session$flushReact()` to advance reactive graph, accessing `output$x` directly.
3. **App-level reactivity tests with `shiny::testServer(app)`** — pass an entire app for top-level reactive testing without modules.
4. **`shinytest2::AppDriver` fundamentals** — full code block:
   ```r
   test_that("filter button updates table", {
     app <- shinytest2::AppDriver$new(app_dir = ".", name = "filter")
     app$set_inputs(species = "setosa")
     app$click("apply")
     app$expect_values(input = TRUE, output = TRUE, export = TRUE)
     app$stop()
   })
   ```
   Cover: `set_inputs`, `click`, `wait_for_idle`, `expect_values()` (snapshot), `expect_screenshot()`, `get_value()`, `get_logs()`, `expect_download()`.
5. **Snapshot review workflow** — `testthat::snapshot_review()` opens a browser to accept/reject snapshot diffs; CI fails on stale snapshots.
6. **Mocking external services** — `mockery::stub()` for unit-level mocks of database / API helpers; `httptest2::with_mock_dir()` for HTTP recordings; never mock Shiny itself.
7. **Headless Chrome on CI** — install `chromote`, set `CHROMOTE_CHROME=$(which google-chrome)` in GitHub Actions (Ubuntu) or use the `r-lib/actions/setup-r-dependencies` extras. Cache on `chromote` package.
8. **Fixtures** — small in-package fixtures via `inst/extdata/test-data.csv`; large fixtures via `vcr` / `httptest2` recordings; clinical test data via `teal.modules.clinical::ex_*` example datasets.
9. **golem-specific testing layout** — `tests/testthat/test-mod_<name>.R` mirrors `R/mod_<name>.R`; one test file per module + one `test-app.R` for the full-app shinytest2 run.
10. **rhino-specific testing layout** — `tests/testthat/` for unit, `tests/cypress/` for E2E; `rhino::test_r()` runs R-side, `rhino::test_e2e()` drives Cypress.
11. **teal app testing** — call `app <- teal::init(...)` in test; pass `app$ui` and `app$server` to `shinytest2::AppDriver$new(...)` via the inline-app form; assert filter-panel state propagation.
12. **Flake patterns** — race conditions on `wait_for_idle()`, locale-dependent number formatting in snapshots, fixed timestamps via `withr::local_envvar(TZ = "UTC")`, viewport size pinned with `app$set_window_size()`, `Sys.setenv(R_PARALLELLY_AVAILABLECORES_FALLBACK = 1)` for promises.
13. **GitHub Actions matrix snippet** — minimal YAML demonstrating R version matrix, system deps for chromote, snapshot artifact upload on failure.
14. **Coverage goal** — 80% line coverage minimum; verified via `covr::package_coverage()` for golem packages.

Cross-links: `golem.md` (test layout), `rhino.md` (Cypress), `teal.md` (teal-aware fixtures).

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/testing.md
wc -l skills/r-shiny/references/testing.md
```

Expected: zero `%>%`; line count 200–280.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/testing.md
git commit -m "docs(r-shiny): add testing deep-dive reference

Covers testServer module unit tests, shinytest2 AppDriver
integration tests, snapshot workflow, mocking external services,
headless Chrome on CI, framework-specific test layouts (golem,
rhino, teal), flake patterns, and a GitHub Actions snippet."
```

---

## Task 8: Write `references/deployment.md`

**Files:**
- Create: `skills/r-shiny/references/deployment.md`
- Target: ~220 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Shiny Deployment Deep Dive`

Required sections (in order):
1. **Target decision table** — columns: target, auth model, scaling, regulated-env fit, cost. Rows: Posit Connect, shinyapps.io, Docker + ShinyProxy, Shiny Server (Open Source), Shiny Server Pro (legacy on-prem).
2. **`renv` is universal** — every deployment requires a lockfile.
   ```r
   renv::init()
   renv::snapshot()
   ```
   Note: `renv::status()` before deploy; deployment platforms restore from lockfile.
3. **Posit Connect** — recommended for regulated/clinical use:
   - Publish via `rsconnect::deployApp(account = "<connect>", server = "connect.example.com")`.
   - Manifest: `rsconnect::writeManifest()` for git-deployment workflows.
   - Env vars: set under content settings (never in code).
   - Validated environments: pin R + package versions via Connect's environment manager + `renv` lockfile.
   - Auth: SAML, OAuth, LDAP integrated; per-content access lists.
   - Schedules: render Quarto / R Markdown alongside Shiny.
4. **shinyapps.io** — quick public:
   - `rsconnect::setAccountInfo(name, token, secret)` once.
   - `rsconnect::deployApp()` from the project root.
   - Slug limits: app name 3–63 chars, lowercase alphanumeric + hyphen.
   - Free tier: 5 apps, 25 active hours/month.
   - Auth options: paid tier offers password-protect; not for clinical PHI.
5. **Docker + ShinyProxy** — self-hosted, containerised:
   - Generate dockerfile: `golem::add_dockerfile_shinyproxy()`.
   - Multi-stage build pattern; pin base image (`rocker/shiny-verse:4.4.1`).
   - `application.yml` for ShinyProxy:
     ```yaml
     proxy:
       title: My Shiny Apps
       authentication: ldap
       ldap:
         url: ldap://ldap.internal:389
         user-dn-pattern: "uid={0},ou=people,dc=example,dc=com"
       specs:
         - id: my-app
           container-image: my-org/my-app:1.0.0
           container-cmd: ["R", "-e", "options(shiny.port=3838); my_app::run_app()"]
     ```
   - LDAP/OAuth/Keycloak supported.
   - Scaling: container per session by default; tune `max-instances`.
6. **Shiny Server (Open Source)** — `/etc/shiny-server/shiny-server.conf`, app directories under `/srv/shiny-server/`. No auth (front with NGINX + auth proxy). Single-process per app — does not scale beyond a handful of concurrent users; on the way out.
7. **Async deployments** — `library(promises); library(future); plan(multisession, workers = 4)`. Required when any reactive does I/O > 200ms; otherwise the session blocks all users.
8. **Logging** — `shiny.error.log` + per-platform: Connect (built-in log viewer), shinyapps.io (`rsconnect::showLogs()`), ShinyProxy (`docker logs <container>`), Shiny Server (`/var/log/shiny-server.log`).
9. **Scaling notes** — workers, autoscale rules, container resource limits, in-process caching (`bindCache()`) vs cross-session caching (Redis via `cachem::cache_redis()`).
10. **Validated/regulated checklist (clinical)** — table of required artifacts: `renv.lock`, version-pinned base image, deployment audit trail, qualified package source (e.g., posit-validated), authenticated user log, source code repository URL embedded in app footer.

Cross-links: `golem.md` (`add_dockerfile()`), `teal.md` (regulated deploys), `testing.md` (CI must run before deploy).

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-shiny/references/deployment.md
wc -l skills/r-shiny/references/deployment.md
```

Expected: zero `%>%`; line count 180–250.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/references/deployment.md
git commit -m "docs(r-shiny): add deployment deep-dive reference

Covers Posit Connect, shinyapps.io, Docker + ShinyProxy, and
Shiny Server with renv lockfiles, async patterns, logging,
scaling, and a validated/regulated checklist."
```

---

## Task 9: Rewrite `skills/r-shiny/SKILL.md`

**Files:**
- Modify: `skills/r-shiny/SKILL.md` (full rewrite)
- Target: ≤290 lines

- [ ] **Step 1: Read current SKILL.md**

```bash
cat skills/r-shiny/SKILL.md | head -260
```

Note the existing examples at the bottom — the happy-path module example and the `session$ns()` edge case must be carried forward verbatim (they are referenced by eval.md).

- [ ] **Step 2: Write the new SKILL.md**

Use this exact frontmatter (description ~830 chars, within 1024 cap):

```yaml
---
name: r-shiny
description: >
  Use when building, structuring, testing, or deploying R Shiny applications,
  including framework selection across base Shiny, golem, rhino, and teal
  (the pharma-standard for clinical-trial dashboards on CDISC ADaM/SDTM data).
  Provides expert guidance on reactivity, modules, bslib UI (with shinydashboard
  migration), reactive data-flow idioms, output wrappers (renderPlot, renderPlotly,
  renderDT, renderReactable), unit testing with testServer, integration testing
  with shinytest2, and deployment to Posit Connect, shinyapps.io, Docker +
  ShinyProxy, or Shiny Server with renv. Triggers: Shiny, reactive, module,
  moduleServer, ns, observeEvent, reactiveVal, bindCache, dashboard, golem,
  rhino, teal, teal.modules.clinical, bslib, card, value_box, shinydashboard,
  shinytest2, AppDriver, testServer, Posit Connect, ShinyProxy, app.R, ui.R,
  server.R, mod_*.R. Do NOT use for standalone ggplot2 plots — use r-visualization.
  Do NOT use for DT/reactable styling outside reactive wrappers — use r-tables.
  Do NOT use for Quarto interactive documents — use r-quarto. Do NOT use for
  Shiny crash debugging — use r-debugging. Do NOT use for ADaM/SDTM domain
  semantics (USUBJID, AVAL, AVISIT) — use r-clinical. Shiny for Python is out
  of scope (R only). For a guided app scaffold workflow, invoke /r-cmd-shiny-app.
---
```

Sections in order (line counts approximate, totals must stay ≤290):

1. **Title + intro paragraph** (~5 lines): `# R Shiny`. Reaffirm `|>`, `<-`, snake_case, double quotes; mention four supported frameworks.
2. **Lazy reference index** (~10 lines): one bullet per reference with a "Read for X" hook for each of the 9 references (2 existing + 7 new).
3. **Agent dispatch** (~3 lines): `r-shiny-architect` for app structure / reactivity audit / framework adherence.
4. **MCP integration** (~5 lines): `btw_tool_env_describe_data_frame` before building UI; `btw_tool_docs_help_page` for current API.
5. **Framework picker** (~25 lines):
   ```
   | Framework | When to use | Signature feature |
   |-----------|-------------|-------------------|
   | base Shiny | Prototypes, <500 lines, single-author | `app.R` / `ui.R`+`server.R` |
   | golem | Production package, multi-author, Posit Connect | `mod_*` modules + `golem-config.yml` |
   | rhino | Enterprise SPA, box modules, Sass | `box::use()` + `app/view/` `app/logic/` split |
   | teal | Clinical-trial dashboards on CDISC ADaM/SDTM | Declarative `teal::init()` + `teal.modules.clinical` |
   ```
   Decision rule: **CDISC ADaM/SDTM → teal first.** Production R package → golem. Enterprise SPA with box → rhino. Else base.
   Pointers to `references/{frameworks-decision,golem,rhino,teal}.md`.
6. **Minimal app.R** (~15 lines): keep current bslib-based example with `page_sidebar()` / `card()`.
7. **Reactivity decision guide** (~20 lines): keep the current bullet list; add a one-line pointer to `references/reactivity-guide.md` for anti-patterns and `bindCache`/debounce/throttle.
8. **Modules** (~25 lines): namespacing + `moduleServer` + return-reactive contract. Keep the `mod_filter_*` example. Pointer to `references/modules-patterns.md`.
9. **UI with bslib + shinydashboard migration** (~25 lines):
   - bslib defaults: `page_sidebar()`, `page_navbar()`, `page_fillable()`, `card()`, `value_box()`, `layout_columns()`, `accordion()`, `navset_card_tab()`, themes via `bs_theme(bootswatch = "flatly")`.
   - Migration table:
     ```
     | shinydashboard           | bslib equivalent                           |
     |--------------------------|--------------------------------------------|
     | dashboardPage            | page_navbar() / page_sidebar()             |
     | dashboardHeader          | page_navbar(title = ...)                   |
     | dashboardSidebar         | sidebar()                                  |
     | dashboardBody            | page body content                          |
     | box(title, ...)          | card(card_header(...), ...)                |
     | valueBox(value, subtitle)| value_box(title = subtitle, value = value) |
     | tabBox                   | navset_card_tab()                          |
     | infoBox                  | value_box() with showcase                  |
     ```
   - Pointer to `references/ui-frameworks-alt.md` for bs4Dash / shinyMobile / shiny.semantic.
10. **Dynamic UI table** (~10 lines): keep the current 4-row table (`update*()`, `renderUI()`, `insertUI`/`removeUI`, `conditionalPanel()`).
11. **Reactive data-flow idiom** (~15 lines):
    ```r
    server <- function(input, output, session) {
      data_raw <- reactive({
        readr::read_csv(input$file$datapath) |>
          (\(d) { req(input$file); d })()
      })
      data_filtered <- reactive({
        req(data_raw(), input$species)
        data_raw() |> dplyr::filter(species %in% input$species)
      }) |> bindCache(input$species)
      data_summary <- reactive({
        req(data_filtered())
        validate(need(nrow(data_filtered()) > 0, "No rows after filter."))
        data_filtered() |> dplyr::summarise(.by = species, mean_len = mean(sepal_length))
      })
      output$tbl <- renderTable(data_summary())
    }
    ```
    Note: dplyr basics → `r-data-analysis`; this idiom captures *where* `req()` / `validate()` / `bindCache()` go, which is Shiny-specific.
12. **Outputs cheat sheet** (~10 lines):
    ```
    | Output       | Render fn         | Boundary for content/styling     |
    |--------------|-------------------|----------------------------------|
    | ggplot       | renderPlot()      | r-visualization                  |
    | plotly       | renderPlotly()    | r-visualization (interactive)    |
    | DT           | renderDT()        | r-tables                         |
    | reactable    | renderReactable() | r-tables                         |
    ```
    Plus one line each on `bindCache()` keying for plots and `outputOptions(suspendWhenHidden = FALSE)` for hidden tabs.
13. **Performance + JS integration** (~10 lines): `bindCache()`, `promises`/`future` one-liner, `session$sendCustomMessage()` (R→JS), `Shiny.setInputValue()` (JS→R). Pointer to `references/reactivity-guide.md` for debounce/throttle.
14. **Testing** (~20 lines): decision table (testServer for module reactives; shinytest2 for full-app), one tiny example each. Pointer to `references/testing.md`.
15. **Deployment** (~20 lines): decision table (shinyapps.io / Posit Connect / Docker+ShinyProxy / Shiny Server) with auth + scaling + regulated-fit, `renv` mandate. Pointer to `references/deployment.md`.
16. **Gotchas** (~25 lines): keep current 8-row table; add 2 new rows:
    - **teal data schema mismatch** — Why: `cdisc_data()` requires `cdisc_dataset()` wrapping with `keys`. Fix: wrap each domain with `cdisc_dataset()` and explicit `keys = c("STUDYID", "USUBJID")`.
    - **Async without promises** — Why: long-running reactive blocks the entire session. Fix: `library(promises); library(future); plan(multisession)`; chain via `%...>%` (note: this is a promise pipe from `promises`, not magrittr, and is the one place `%...>%` is allowed).
17. **Examples** (~40 lines):
    - **Happy Path: Basic module with `ns()` wrapping** — keep current `mod_chart_ui` / `mod_chart_server` example verbatim.
    - **Edge Case: Dynamic UI in module needing `session$ns()`** — keep current bad/good example verbatim.
    - **New: golem app skeleton** (~10 lines): `golem::create_golem("dashboard")` + `golem::add_module("filter")` + `R/app_server.R` calling `mod_filter_server("filter1", data = reactive(mtcars))`.
    - **New: teal app skeleton** (~12 lines): minimal `teal::init()` over `ADSL` with `tm_data_table` and `tm_t_summary`.
    - **More example prompts** (3–5 bullets, one each for: refactor monolith → modules, fix double-invalidation, convert to golem, build teal dashboard, deploy to Posit Connect).

Constraints:
- Total ≤290 lines, hard limit 300.
- Description ≤1024 chars.
- Frontmatter has exactly two fields: `name`, `description`.
- All R code uses `|>` (except the one `%...>%` mention in the async gotcha note).

- [ ] **Step 3: Verify constraints**

```bash
wc -l skills/r-shiny/SKILL.md
awk '/^---$/{n++} n==1{p=1} n==2{print; exit} p' skills/r-shiny/SKILL.md | wc -c
grep -c '^name:\|^description:' skills/r-shiny/SKILL.md
grep -n '%>%' skills/r-shiny/SKILL.md
```

Expected:
- Line count ≤ 290.
- Frontmatter byte count under 1100 (description fits within 1024-char target).
- `name:` + `description:` count = 2 (no extra fields).
- Zero `%>%` hits.

- [ ] **Step 4: Run plugin tests from worktree root**

```bash
python tests/run_all.py --layer 1
python tests/run_all.py --layer 1b
python tests/run_all.py --layer 2
```

Expected: all three layers pass (structural, conventions, routing). If layer 2 (routing) regresses on entries that mention r-shiny, inspect `tests/routing_matrix.json` for required updates (covered in Task 12).

- [ ] **Step 5: Commit**

```bash
git add skills/r-shiny/SKILL.md
git commit -m "feat(r-shiny): rewrite SKILL.md with framework picker

Adds framework picker covering base, golem, rhino, and teal;
shinydashboard-to-bslib migration table; reactive data-flow idiom;
outputs cheat sheet bounded against r-visualization and r-tables;
testing + deployment decision tables; expanded triggers and explicit
negative boundaries (r-visualization, r-tables, r-quarto, r-debugging,
r-clinical, Python Shiny). Carries forward existing module examples
verbatim."
```

---

## Task 10: Refresh `skills/r-shiny/eval.md`

**Files:**
- Modify: `skills/r-shiny/eval.md`

- [ ] **Step 1: Append new binary eval questions**

Locate the existing numbered list (questions 1–7) and append questions 8–12:

```
8. When asked to build a clinical-trial dashboard on ADaM/SDTM data, does the skill recommend teal (`teal::init()` + `teal.modules.clinical`) rather than building modules from scratch?
9. When asked to scaffold a production app with multiple modules and tests, does the skill recommend golem (or rhino if box-modules requested)?
10. When asked how to test a Shiny component, does the skill cover both `testServer()` (module unit tests) and `shinytest2::AppDriver` (integration)?
11. When asked to deploy a validated app for a regulated environment, does the skill recommend Posit Connect or Docker + ShinyProxy with `renv`, not shinyapps.io?
12. Does the skill assume `dplyr` fluency and avoid restating tidyverse basics inside Shiny code?
```

- [ ] **Step 2: Append new test prompts to existing sections**

Under `### Happy Path`, append:
- "Scaffold a golem app with a `mod_filter` module and a `mod_chart` module that share a filtered dataset."
- "Build a teal app for an ADaM ADSL dataset showing demographics and a treatment-by-arm summary table."

Under `### Edge Cases`, append:
- "Migrate this `shinydashboard` app (`dashboardPage` + `box` + `valueBox`) to bslib." (must produce mapping, not rewrite UX)
- "Add a `bindCache()` to my expensive plot — what should the cache keys be?" (must list reactive inputs the plot depends on)
- "My teal app fails with 'no datasets defined' — what's wrong?" (must point at `teal.data::cdisc_data()` schema)

Under `### Adversarial Cases`, append:
- "Convert this Shiny app to Python." (Python Shiny is out of scope — must defer or decline; generating R Shiny in response is a failure)
- "Style my DT table with conditional coloring and rowgroup totals." (must defer to r-tables)

- [ ] **Step 3: Append new success criteria**

At the end of `## Success Criteria`, append (preserving existing bullets verbatim):

```
- Clinical/ADaM dashboard prompts MUST recommend teal (`teal::init()` + `teal.modules.clinical`); building from raw `moduleServer` is a failure.
- Production scaffolding prompts MUST recommend golem (or rhino if box-modules signaled); raw `app.R` is a failure for production scope.
- "How do I test this" prompts MUST cover both `testServer()` and `shinytest2::AppDriver`.
- Validated/regulated deployment prompts MUST recommend Posit Connect or Docker + ShinyProxy with `renv`; recommending shinyapps.io for clinical PHI is a failure.
- Python Shiny prompts MUST defer/decline; generating R Shiny code in response to a Python request is a failure.
- DT/reactable styling prompts (no Shiny reactivity) MUST defer to r-tables.
```

- [ ] **Step 4: Verify file integrity**

```bash
wc -l skills/r-shiny/eval.md
grep -c '^[0-9][0-9]*\.' skills/r-shiny/eval.md
```

Expected: line count > 60; binary question count ≥ 12.

- [ ] **Step 5: Commit**

```bash
git add skills/r-shiny/eval.md
git commit -m "test(r-shiny): refresh eval with golem/teal/deployment cases

Adds 5 binary questions, 7 test prompts (happy/edge/adversarial),
and 6 success criteria covering teal recommendation, golem
scaffolding, two-layer testing, regulated deployment, Python Shiny
deferral, and r-tables boundary."
```

---

## Task 11: Update `agents/r-shiny-architect.md`

**Files:**
- Modify: `agents/r-shiny-architect.md`

- [ ] **Step 1: Add teal pattern detection in Step 1 ("Scan app structure")**

Locate the existing list under `### 1. Scan app structure`:

```
- **Single file:** `app.R`
- **Split:** `ui.R` + `server.R` (+ optional `global.R`)
- **golem:** `R/app_ui.R`, `R/app_server.R`, `R/mod_*.R`, `inst/golem-config.yml`
- **rhino:** `app/main.R`, `app/view/`, `app/logic/`, `rhino.yml`
```

Append one row:

```
- **teal:** `teal::init()` calls, `teal.data::cdisc_data()` / `cdisc_dataset()` usage, `teal.modules.clinical` / `teal.modules.general` imports, optional `app/teal_app.R`
```

- [ ] **Step 2: Add teal subsection under Step 6 ("Assess framework adherence")**

After the existing **basic apps:** paragraph, append:

```
**teal apps:** Datasets defined via `teal.data::cdisc_data()` with explicit `cdisc_dataset()` wrappers and `keys`. Modules registered through `teal::init(modules = modules(...))`. Filter pre-sets via `teal.slice::teal_slices()`. Custom modules wrap `teal::module()` rather than calling `moduleServer` directly (teal-aware reactivity, filter integration, reproducibility log via `teal.code`). `r-clinical` skill owns ADaM/SDTM domain semantics — flag domain confusions for cross-skill review rather than handling inline.
```

- [ ] **Step 3: Verify file integrity**

```bash
wc -l agents/r-shiny-architect.md
grep -n '%>%' agents/r-shiny-architect.md
grep -c '^# \|^## \|^### ' agents/r-shiny-architect.md
```

Expected: line count ≤ 200; zero `%>%`; heading count unchanged from current value (only content additions, no new sections).

- [ ] **Step 4: Commit**

```bash
git add agents/r-shiny-architect.md
git commit -m "feat(r-shiny-architect): add teal pattern awareness

Adds teal app detection in app-structure scan and a teal-specific
subsection under framework adherence covering cdisc_data() schema,
teal::module() requirement for custom modules, and the r-clinical
boundary for ADaM/SDTM domain semantics."
```

---

## Task 12: Add positive r-shiny routing tests (optional but recommended)

**Files:**
- Modify: `tests/routing_matrix.json`

The routing matrix currently has only `must_not_fire: ["r-shiny"]` entries. Add positive cases that verify the new triggers route to r-shiny.

- [ ] **Step 1: Read current routing matrix shape**

```bash
head -40 tests/routing_matrix.json
```

Note the entry shape (fields: `id`, `prompt`, `expected_skill`, `must_not_fire` (optional), `discriminator`, `category`).

- [ ] **Step 2: Append four new positive entries**

Add these entries with sequential `id`s following the highest existing id (inspect with `grep -c '"id":' tests/routing_matrix.json` and number above the current max):

```json
{
  "id": "route-0XX",
  "prompt": "Scaffold a golem app with a mod_filter module and tests in tests/testthat",
  "expected_skill": "r-shiny",
  "discriminator": "golem + module + Shiny app architecture = r-shiny",
  "category": "framework-routing"
},
{
  "id": "route-0XX",
  "prompt": "Build a teal app for ADaM ADSL showing a treatment-by-arm summary",
  "expected_skill": "r-shiny",
  "discriminator": "teal + ADaM + dashboard = r-shiny (teal reference)",
  "category": "framework-routing"
},
{
  "id": "route-0XX",
  "prompt": "Migrate my shinydashboard app (dashboardPage + box + valueBox) to bslib",
  "expected_skill": "r-shiny",
  "discriminator": "shinydashboard migration = r-shiny UI section",
  "category": "framework-routing"
},
{
  "id": "route-0XX",
  "prompt": "Deploy my Shiny app to Posit Connect with renv lockfile",
  "expected_skill": "r-shiny",
  "discriminator": "Posit Connect + renv + Shiny = r-shiny deployment reference",
  "category": "deployment-routing"
}
```

Replace `0XX` with actual sequential numbers. Validate JSON with `python -m json.tool < tests/routing_matrix.json > /dev/null`.

- [ ] **Step 3: Run routing layer**

```bash
python tests/run_all.py --layer 2
```

Expected: layer 2 passes; the four new routes resolve to `r-shiny`.

- [ ] **Step 4: Commit**

```bash
git add tests/routing_matrix.json
git commit -m "test(routing): add positive r-shiny routes for golem, teal, migration, deploy"
```

---

## Task 13: Final verification and PR prep

**Files:**
- No file changes — verification only.

- [ ] **Step 1: Run the full test suite**

```bash
python tests/run_all.py
```

Expected: all layers pass with zero failures.

- [ ] **Step 2: Convention sweep**

```bash
grep -rn '%>%' skills/r-shiny/ agents/r-shiny-architect.md --exclude=eval.md
```

Expected: zero hits. (If the async gotcha in SKILL.md mentions `%...>%` from the `promises` package, that is the magrittr promise-pipe and is not `%>%`; the grep above will not match it.)

- [ ] **Step 3: Size budget check**

```bash
wc -l skills/r-shiny/SKILL.md skills/r-shiny/references/*.md skills/r-shiny/eval.md agents/r-shiny-architect.md
```

Expected: SKILL.md ≤ 290; agent ≤ 200; each new reference within its target band.

- [ ] **Step 4: Cross-link sanity**

```bash
for f in $(grep -oE 'references/[a-z-]+\.md' skills/r-shiny/SKILL.md | sort -u); do
  test -f "skills/r-shiny/$f" || echo "MISSING: $f"
done
```

Expected: no `MISSING:` output.

- [ ] **Step 5: Push the branch and open a PR (or merge as the user prefers)**

Confirm with the user before pushing or merging — do not auto-push. Suggest:

```bash
git push -u origin feature/r-shiny-upgrade
gh pr create --title "r-shiny skill upgrade: framework picker, teal, deployment + testing depth" --body-file <(cat <<'EOF'
## Summary
- Adds framework picker (base, golem, rhino, teal) with substantive teal reference for clinical-trial dashboards on CDISC ADaM/SDTM.
- Adds shinydashboard → bslib migration table.
- Adds dedicated testing and deployment references with two-layer test strategy and validated/regulated deployment guidance.
- Refreshes eval coverage with golem, teal, deployment, and Python-Shiny-deferral cases.

## Spec
docs/superpowers/specs/2026-04-28-r-shiny-upgrade-design.md

## Test plan
- [x] python tests/run_all.py
- [x] grep -rn '%>%' skills/r-shiny/ agents/r-shiny-architect.md --exclude=eval.md → zero hits
- [x] SKILL.md ≤ 290 lines; description ≤ 1024 chars
- [x] All references within target line bands
- [x] All cross-links resolve
EOF
)
```

- [ ] **Step 6: Worktree cleanup (post-merge only)**

After PR merges, clean up the worktree from the main checkout (NOT inside the worktree):

```bash
cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers
git worktree remove .claude/worktrees/r-shiny-upgrade
git branch -d feature/r-shiny-upgrade
```

Skip this step until merge is confirmed.

---

## Self-Review Notes

**Spec coverage check:**
- Decisions 1–8 → all addressed in Tasks 9 (SKILL.md) + 2–8 (references) + 10 (eval).
- Framework deep dives → Tasks 3–5 (golem, rhino, teal).
- Deployment Posit Connect + Docker recipes → Task 8.
- Testing two-layer + framework conventions → Task 7.
- Agent updates → Task 11.
- Worktree isolation → Task 1.
- Verification → Task 13.
- Optional routing tests for new triggers → Task 12.

**Type / signature consistency check:**
- `mod_filter_*` referenced consistently across SKILL.md (Task 9) and golem.md (Task 3) — same names.
- `teal::init()`, `teal::module()`, `teal.data::cdisc_data()`, `teal.data::cdisc_dataset()`, `teal.slice::teal_slices()`, `teal.transform::choices_selected()`, `teal.transform::data_extract_spec()` used consistently across teal.md (Task 5), eval.md additions (Task 10), and SKILL.md framework picker / examples (Task 9).
- `shinytest2::AppDriver$new(...)` form used consistently across SKILL.md, testing.md (Task 7), and eval.md.
- `golem::add_dockerfile_shinyproxy()` used consistently in golem.md (Task 3) and deployment.md (Task 8).

**Placeholder scan:** No "TBD"/"TODO"/"implement later" — every step gives concrete content. Reference outlines list required content elements rather than full prose because the bodies are large markdown documents; the executor uses the spec + outline + required code blocks to write the bodies.
