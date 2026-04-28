# r-package-dev Skill Upgrade — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `skills/r-package-dev/` from 17/17 deterministic-passing to best-in-class for both human and LLM consumers — closing audit-judgment gaps, modernizing tooling references, and tightening sibling boundaries.

**Architecture:** SKILL.md stays ≤300 lines via a tighter "When to use" decision block, strengthened gotchas, scope discipline + feedback loop subsections, and MCP qualification fix. Three new reference files (`modern-toolchain.md`, `release-workflow.md`, `data-and-assets.md`) and four enhanced ones absorb the depth. One new script (`preflight.R`) plus polish on `release_checklist.R` and `audit_deps.R`. Sharpened `eval.md` makes future audits measurable.

**Tech Stack:** R ≥ 4.1.0, tidyverse style, native pipe `|>`, `<-` assignment, snake_case, double quotes. Plugin verification via `python skills/skill-auditor/scripts/score_skill.py`, `verify_batch.py`, `tests/run_all.py`.

**Reference spec:** `docs/superpowers/specs/2026-04-28-r-package-dev-upgrade-design.md`

---

## File Structure

**Created:**
- `skills/r-package-dev/references/modern-toolchain.md` (~200 lines) — `pak`, `air`, `lintr`, `lifecycle`, `cli`, `withr`
- `skills/r-package-dev/references/release-workflow.md` (~150 lines) — `usethis::use_release_issue()` lifecycle
- `skills/r-package-dev/references/data-and-assets.md` (~150 lines) — `data/`, `inst/extdata`, `R/sysdata.rda`
- `skills/r-package-dev/scripts/preflight.R` (~120 lines) — fast pre-check pipeline

**Modified:**
- `skills/r-package-dev/SKILL.md` — restructure top, add scope discipline + feedback loop subsections, qualify MCP refs, add modern toolchain block, rebuild gotchas
- `skills/r-package-dev/references/class-systems-guide.md` — promote S7 to first-class, add migration recipes
- `skills/r-package-dev/references/r-cmd-check-troubleshooting.md` — restructure to Saw/Cause/Fix/Verify quadruples, add 5 modern entries
- `skills/r-package-dev/references/roxygen2-tags.md` — add `@inheritParams`, `@describeIn`, `@rdname`, `@family`, lifecycle badges, Markdown link forms
- `skills/r-package-dev/references/cran-submission-checklist.md` — add resubmission protocol, incoming pending workflow
- `skills/r-package-dev/scripts/release_checklist.R` — add `--with-revdep` flag, platform summary
- `skills/r-package-dev/scripts/audit_deps.R` — add detection of unconditional `Suggests` usage with file:line locations
- `skills/r-package-dev/eval.md` — measurable success criteria + 2 new prompts

**Untouched (already strong):**
- `references/description-fields.md`, `namespace-patterns.md`, `pkgdown-site-config.md`, `revdep-workflow.md`
- `scripts/check_package.R`, `validate_description.R`, `check_docs.R`, `lint_package.R`

---

## Verification Gates (run after every commit)

```bash
python skills/skill-auditor/scripts/score_skill.py skills/r-package-dev \
  --siblings-dir skills --conventions rules/r-conventions.md --max-lines 300 \
  --format table

python skills/skill-auditor/scripts/verify_batch.py skills --all --max-lines 300

grep -rn '%>%' skills/r-package-dev --exclude=eval.md   # must be empty

python tests/run_all.py
```

If any gate fails, do NOT continue to the next task. Fix in place.

---

## Task 1: Restructure SKILL.md top — "When to use" decision block + sibling boundary table

**Files:**
- Modify: `skills/r-package-dev/SKILL.md` (lines 15–50)

- [ ] **Step 1: Read the current SKILL.md top section**

Read lines 1–60 of `skills/r-package-dev/SKILL.md`. Note the existing intro paragraph, lazy reference list, scripts list, agent dispatch, MCP integration block.

- [ ] **Step 2: Replace the intro paragraph with a "When to use" block**

In `skills/r-package-dev/SKILL.md`, replace the current intro (line 15 through "All code uses base pipe `|>`, `<-` for assignment, and tidyverse style." on line 21) with:

```markdown
# R Package Development

Full-lifecycle R package development with the modern toolchain: `usethis`,
`devtools`, `roxygen2`, `testthat` 3e, `pkgdown`, CRAN submission, plus
`pak`, `air`, `lintr`, `lifecycle`, `cli`, `withr`.

All R code uses base pipe `|>`, `<-` for assignment, snake_case, and double
quotes. Target R >= 4.1.0.

## When to use this skill

This skill owns: development loop, documentation, NAMESPACE, dependencies,
class systems, vignettes, pkgdown, R CMD check, CRAN submission, CI/CD.

| You want to... | Use instead |
|----------------|-------------|
| Scaffold a new project (only) | `r-project-setup` |
| Write tests / TDD cycle | `r-tdd` |
| Run an interactive guided release | `/r-cmd-pkg-release` |
| Generate a Claude skill FROM an R package | `r-package-skill-generator` |
| Debug R source code (not the build) | `r-debugging` |
```

- [ ] **Step 3: Remove redundant inline boundary callouts**

Delete the `> **Boundary:**` lines that appear inside individual sections (currently in "Package Scaffold" and "Testing in Packages" sections — search for `> **Boundary:**` and remove those two lines plus the blank line that follows each). The new top-level table replaces them.

- [ ] **Step 4: Run verification gates**

Run all four gates from the "Verification Gates" section above. Score must remain 17/17. Line count must be ≤300.

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/SKILL.md
git commit -m "feat(r-package-dev): add When-to-use decision block, consolidate sibling boundaries"
```

---

## Task 2: SKILL.md — Modern toolchain block + MCP qualification fix

**Files:**
- Modify: `skills/r-package-dev/SKILL.md` (MCP integration block + new Modern Toolchain block)

- [ ] **Step 1: Qualify MCP tool references**

In `skills/r-package-dev/SKILL.md`, find the "MCP integration (when R session available):" block. Replace each bare tool name with the qualified `btw:` prefix:

```markdown
**MCP integration (when R session available):**
- `btw:btw_tool_docs_help_page` — read existing docs before editing roxygen2
- `btw:btw_tool_docs_package_help_topics` — list exported functions before NAMESPACE edits
- `btw:btw_tool_sessioninfo_is_package_installed` — check before adding a dependency
```

- [ ] **Step 2: Add Modern Toolchain block**

Immediately after the existing "Scripts:" lazy-reference list (around line 39, before "Agent dispatch:"), insert a new "Modern toolchain:" block that points at the new reference:

```markdown
**Modern toolchain (lazy reference):**
- `references/modern-toolchain.md` — `pak` for fast installs, `air` formatter,
  `lintr` config, `lifecycle` deprecation badges, `cli` messages, `withr` test
  isolation
- `references/release-workflow.md` — `usethis::use_release_issue()`-driven
  release lifecycle
- `references/data-and-assets.md` — `data/`, `inst/extdata/`, `R/sysdata.rda`,
  `usethis::use_data()` patterns
```

- [ ] **Step 3: Run verification gates**

Run all four gates. Score must remain 17/17.

- [ ] **Step 4: Commit**

```bash
git add skills/r-package-dev/SKILL.md
git commit -m "feat(r-package-dev): qualify MCP refs and add modern-toolchain lazy refs"
```

---

## Task 3: SKILL.md — Strengthened Gotchas + Scope discipline + Feedback loop

**Files:**
- Modify: `skills/r-package-dev/SKILL.md` (Gotchas section through end)

- [ ] **Step 1: Add Feedback Loop subsection**

In `skills/r-package-dev/SKILL.md`, find the "## Development Loop" section. Replace its body with:

```markdown
## Development Loop

The named feedback loop:

```
load_all() -> test() -> document() -> check() -> fix -> repeat
```

```r
devtools::load_all()      # Simulate library(mypkg) from source
devtools::test()          # Run testthat suite
devtools::document()      # Rebuild NAMESPACE + man/ from roxygen2
devtools::check()         # Full R CMD check
```

**Stop conditions:** 0 errors, 0 warnings, 0 notes (CRAN target) OR explicit
user-defined acceptance criteria. Never stop because "it looks fine."

**Quick iteration:** `load_all()` + `testthat::test_active_file()` while
developing a single function. For a fast pre-check that skips R CMD check, run
`Rscript scripts/preflight.R .` (regenerates man/, lints, spell-checks, URL
checks). Run full `check()` before pushing.
```

- [ ] **Step 2: Restructure Gotchas table to If→Do→Verify triplets**

Replace the existing "## Gotchas" section (the table with "Trap | Fix") with this expanded section. The `If you see X` column states the symptom; `Do Y` states the fix; `Verify with Z` states how to confirm:

```markdown
## Gotchas

| If you see... | Do... | Verify with... |
|---|---|---|
| `@import pkg` (whole namespace) | Replace with `@importFrom pkg fn` or `pkg::fn()` | `devtools::document()` then check NAMESPACE diff |
| Stale exports / missing methods after roxygen edit | `devtools::document()` | `git diff NAMESPACE` |
| `library()` or `require()` inside `R/` | Replace with `pkg::fn()` or `@importFrom` | `R CMD check` shows no "library/require call" NOTE |
| Missing `@export` on a public function | Add `@export`, then `document()` | NAMESPACE gains `export(fn)` |
| Hardcoded paths in tests | Use `testthat::test_path()`, `system.file()`, `fs::path_package()` | `devtools::test()` passes outside the source tree |
| Dep used but not declared | `usethis::use_package("dep")` | `Rscript scripts/audit_deps.R .` reports clean |
| `Depends:` instead of `Imports:` | Move to `Imports:` (keep `Depends:` only for R version) | `desc::desc()` confirms Imports |
| Reaching another package with `:::` | Request export upstream or re-implement | `R CMD check --as-cran` rejects `:::` |
| `@docType package` (deprecated) | Replace with `_PACKAGE` sentinel in `R/<pkg>-package.R` | `devtools::document()` regenerates package help |
| S4/S7 method registration silently dropped | Add `@include` and confirm `Collate:` order in DESCRIPTION | `methods::existsMethod()` returns TRUE |
| Lazy data >5 MB blocks CRAN | `usethis::use_data(..., compress = "xz")`; check with `tools::checkRdaFiles("data/")` | Install size NOTE under 5 MB |
| Confused about `data/` vs `inst/extdata/` | Read `references/data-and-assets.md` | Files load via `data()` (R) or `system.file()` (raw) |

For every common ERROR/WARNING/NOTE from `devtools::check()`, see
`references/r-cmd-check-troubleshooting.md`.

## Scope Discipline (mandatory)

- Fix **only** the identified issue. No drive-by refactors.
- Show the **minimal diff**. One issue per session.
- Never re-export, rename, or restructure without an explicit user request.
- Re-run `devtools::check()` (or `scripts/preflight.R` for fast iteration)
  after every fix; do not batch unrelated changes.
```

- [ ] **Step 3: Run verification gates**

Run all four gates. The SKILL.md line count after this task should still be ≤300. If over budget, trim the bottom of an existing section that has redundancy (the "Examples" section can be tightened — verify with the user before cutting examples).

- [ ] **Step 4: Commit**

```bash
git add skills/r-package-dev/SKILL.md
git commit -m "feat(r-package-dev): expand gotchas to triplets, add scope discipline + feedback loop"
```

---

## Task 4: New `references/modern-toolchain.md`

**Files:**
- Create: `skills/r-package-dev/references/modern-toolchain.md`

- [ ] **Step 1: Write the new reference file**

Create `skills/r-package-dev/references/modern-toolchain.md` with the structure below. Each section must contain runnable example code following project conventions (`<-`, `|>`, snake_case, double quotes).

```markdown
# Modern R Package Toolchain

Complementary tools that are now standard in modern R package development
beyond `devtools`/`usethis`/`roxygen2`/`testthat`. Each section is a
self-contained primer — when to use it, how to install, the one or two
commands you actually use, and any gotchas.

**Sources:**
- pak — <https://pak.r-lib.org/>
- air formatter — <https://posit-dev.github.io/air/>
- lintr — <https://lintr.r-lib.org/>
- lifecycle — <https://lifecycle.r-lib.org/>
- cli — <https://cli.r-lib.org/>
- withr — <https://withr.r-lib.org/>

---

## pak — fast, parallel package installs

`pak` resolves and installs in parallel, handles system dependencies, and is
significantly faster than `install.packages()` and `remotes::install_*()`.
Use it especially in CI.

```r
install.packages("pak")
pak::pkg_install("dplyr")              # CRAN
pak::pkg_install("r-lib/usethis")      # GitHub
pak::pkg_install(".")                  # current package + deps
pak::local_install_dev_deps()          # dev deps only
```

GitHub Actions:

```yaml
- uses: r-lib/actions/setup-r-dependencies@v2
  with:
    extra-packages: any::pak
```

`r-lib/actions` v2 already uses `pak` internally; no extra config required
for `R-CMD-check.yaml` generated by `usethis::use_github_action("check-standard")`.

## air — Rust-based R code formatter

`air` is a fast, opinionated R formatter (Rust). Drop-in alternative to
`styler` for `air format`-on-save. Use it for new projects; keep `styler`
on existing projects unless migrating intentionally.

```bash
# Install via npm or cargo (see air docs for current method)
air format R/        # format all files in R/
air format --check . # CI gate: nonzero exit if not formatted
```

Project config: `air.toml` at package root. Pre-commit hook: see air docs.

## lintr — static analysis with `.lintr` config

`lintr` flags style violations and bug-prone patterns. Configure via a
`.lintr` file in package root.

```r
usethis::use_lintr(type = "tidyverse")  # creates .lintr
lintr::lint_package()                   # report all issues
```

`.lintr` minimum recommended config:

```yaml
linters: linters_with_defaults(
    line_length_linter(80L),
    object_name_linter(styles = "snake_case"),
    object_usage_linter = NULL  # noisy with NSE
  )
exclusions: list("R/RcppExports.R", "tests/testthat.R")
```

GitHub Action:

```r
usethis::use_github_action("lint")
```

## lifecycle — soft-deprecation badges and stages

`lifecycle` lets you communicate function maturity and deprecate gracefully
without breaking downstream packages.

Stages: `experimental`, `stable`, `superseded`, `deprecated`, `defunct`.

```r
usethis::use_lifecycle()                # adds badges/, lifecycle to Imports
```

In a function:

```r
#' @param old_arg `r lifecycle::badge("deprecated")` Use `new_arg` instead.
deprecate_example <- function(new_arg, old_arg = lifecycle::deprecated()) {
  if (lifecycle::is_present(old_arg)) {
    lifecycle::deprecate_warn("0.4.0", "fn(old_arg)", "fn(new_arg)")
    new_arg <- old_arg
  }
  new_arg
}
```

Function-level badge in roxygen:

```r
#' @description
#' `r lifecycle::badge("experimental")`
```

## cli — user-facing messages, errors, progress

Use `cli` instead of `message()` / `warning()` / `stop()` for any user-
visible package message. Supports rich formatting, classed conditions,
and progress bars.

```r
usethis::use_package("cli")
```

```r
cli::cli_inform(c(
  "Loaded {.val {n}} rows from {.path {file}}.",
  i = "Use {.fn read_csv} for faster parsing."
))

cli::cli_warn("Column {.var {col}} has {.val {n_na}} missing values.")

cli::cli_abort(
  c(
    "{.arg x} must be numeric.",
    x = "You supplied a {.cls {class(x)}}."
  ),
  class = "mypkg_error_type"
)
```

Progress bar:

```r
cli::cli_progress_along(items, "Processing")
```

## withr — scoped state changes for tests

Use `withr::local_*()` in tests to set state (options, env vars, working
directory, locale) that auto-resets at end of scope. Replaces manual
`on.exit()` + `setwd()` patterns.

```r
test_that("respects locale", {
  withr::local_locale(c("LC_TIME" = "C"))
  # test body — locale resets when test_that() exits
})

test_that("uses temp file", {
  path <- withr::local_tempfile(fileext = ".csv")
  # path auto-deleted at end of scope
})

test_that("with options", {
  withr::local_options(width = 60L)
  # restored after test
})
```

For non-test scoped state inside package functions, use `withr::with_*()`:

```r
withr::with_dir(tmp, do_work())
```
```

- [ ] **Step 2: Verify line count**

Run `wc -l skills/r-package-dev/references/modern-toolchain.md`. Should be 150–230 lines.

- [ ] **Step 3: Verify no `%>%` and conventions hold**

```bash
grep -n '%>%' skills/r-package-dev/references/modern-toolchain.md   # empty
grep -n ' = ' skills/r-package-dev/references/modern-toolchain.md   # only function args, not assignment
```

- [ ] **Step 4: Run verification gates**

Run all four gates.

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/references/modern-toolchain.md
git commit -m "feat(r-package-dev): add modern-toolchain reference (pak, air, lintr, lifecycle, cli, withr)"
```

---

## Task 5: New `references/release-workflow.md`

**Files:**
- Create: `skills/r-package-dev/references/release-workflow.md`

- [ ] **Step 1: Write the new reference file**

Create `skills/r-package-dev/references/release-workflow.md`:

```markdown
# Release Workflow

The `usethis::use_release_issue()`-driven workflow for shipping a CRAN release.
Complements `cran-submission-checklist.md` (which covers the check gauntlet);
this file covers the lifecycle around it.

**Sources:**
- R Packages 2e ch. 22 "Releasing to CRAN" — <https://r-pkgs.org/release.html>
- usethis release helpers — <https://usethis.r-lib.org/reference/use_release_issue.html>
- Keep a Changelog — <https://keepachangelog.com/>
- Semantic Versioning — <https://semver.org/>

---

## Lifecycle Overview

```
Dev (0.4.0.9000) -> Pre-release PR -> use_release_issue() -> Submit -> Tag -> Post-release bump
```

A package in active development carries a `.9000` dev suffix on its version
(e.g. `0.4.0.9000`). The release process strips the suffix, tests, submits,
and post-release bumps to the next `.9000`.

---

## Phase 1: Pre-release PR

Open a single PR that contains all release-prep changes:

```r
usethis::use_version("minor")          # 0.4.0.9000 -> 0.5.0
usethis::use_news_md()                 # if not already present
```

Update `NEWS.md`:

- New top-level header: `# mypkg 0.5.0`
- Subsections: `## New features`, `## Bug fixes`, `## Breaking changes`,
  `## Deprecations`
- One bullet per user-facing change. Reference issue/PR numbers.
- Move all bullets from the previous `# mypkg (development version)`
  header into the new release header.

Update `README.Rmd` (or `README.md`) if needed for new features. Re-knit:

```r
devtools::build_readme()
```

Update vignettes if API changed.

## Phase 2: Open the release issue

```r
usethis::use_release_issue()
```

This opens a GitHub issue with a checklist tailored to your package
(devtools/usethis introspect your CI status, whether it has revdeps, etc.).

The issue typically contains, in order:

1. Update `NEWS.md` ✓ (done in Phase 1)
2. Run `devtools::check()` and `urlchecker::url_check()`
3. Run `devtools::check_win_devel()` and `devtools::check_mac_release()`
4. Run `revdepcheck::revdep_check()` (only if revdeps exist)
5. Update `cran-comments.md`
6. `devtools::submit_cran()`
7. Approve email (CRAN sends a confirmation)
8. (After acceptance) tag the release
9. Post-release: `usethis::use_dev_version()`

Tick each item as you complete it. The issue is your audit trail.

## Phase 3: Pre-submission checks

Run the full gauntlet (this skill ships `scripts/release_checklist.R` for it):

```bash
Rscript skills/r-package-dev/scripts/release_checklist.R .
# or for revdeps:
Rscript skills/r-package-dev/scripts/release_checklist.R . --with-revdep
```

Required outcome: 0 errors, 0 warnings, 0 notes — across all platforms.

`cran-comments.md` minimum content:

```markdown
## R CMD check results

0 errors | 0 warnings | 0 notes

## Test environments

* local R 4.4.0, macOS 14.5
* win-builder R-devel
* mac-builder R-release
* GitHub Actions: ubuntu-latest, windows-latest, macos-latest, R-release

## Reverse dependencies

We checked 12 reverse dependencies. No new problems were detected.
```

## Phase 4: Submit

```r
devtools::submit_cran()
```

Approve the confirmation email CRAN sends to the maintainer address.

## Phase 5: Post-acceptance

After CRAN accepts (typically 1–7 days):

```r
usethis::use_github_release()    # tag + GitHub release with NEWS body
usethis::use_dev_version()       # bump 0.5.0 -> 0.5.0.9000
```

Commit the dev-version bump on `main` directly (not via PR).

Open a fresh `# mypkg (development version)` block at the top of `NEWS.md`.

## Rejection Protocol

If CRAN rejects:

1. Read the rejection email carefully — quote each issue in `cran-comments.md`.
2. Fix every flagged issue. Do not push back unless you genuinely disagree.
3. Add a "Resubmission" section to the top of `cran-comments.md`:

```markdown
## Resubmission

This is a resubmission. Compared to the previous submission:

* Fixed `\dontrun{}` examples flagged by Uwe — now use `\donttest{}`
  with `if (interactive())` guards (responses to comments dated YYYY-MM-DD).
* Added missing `\value{}` documentation for `internal_helper()`.
```

4. Re-run the gauntlet and resubmit with `devtools::submit_cran()`.

Most rejections are policy-related (description text, examples, file
modifications outside `tempdir()`), not code-correctness.

## Versioning

Follow Semantic Versioning:

| Change | Bump |
|---|---|
| Breaking API change | major (`0.4.0` -> `1.0.0`) |
| New feature, backward-compatible | minor (`0.4.0` -> `0.5.0`) |
| Bug fix only | patch (`0.4.0` -> `0.4.1`) |
| Active development | `.9000` suffix on the next planned version |

Pre-1.0 packages may break API freely between minor versions, but state this
in NEWS.md.
```

- [ ] **Step 2: Verify line count and conventions**

```bash
wc -l skills/r-package-dev/references/release-workflow.md   # 130-180 lines expected
grep -n '%>%' skills/r-package-dev/references/release-workflow.md   # empty
```

- [ ] **Step 3: Run verification gates**

- [ ] **Step 4: Commit**

```bash
git add skills/r-package-dev/references/release-workflow.md
git commit -m "feat(r-package-dev): add release-workflow reference (use_release_issue lifecycle)"
```

---

## Task 6: New `references/data-and-assets.md`

**Files:**
- Create: `skills/r-package-dev/references/data-and-assets.md`

- [ ] **Step 1: Write the new reference file**

Create `skills/r-package-dev/references/data-and-assets.md`:

```markdown
# Data and Assets in R Packages

Where to put data, how to access it, and how to keep CRAN happy.

**Sources:**
- R Packages 2e ch. 7 "Data" — <https://r-pkgs.org/data.html>
- Writing R Extensions §1.1.6 "Data in packages" — <https://cran.r-project.org/doc/manuals/r-release/R-exts.html#Data-in-packages>
- usethis::use_data — <https://usethis.r-lib.org/reference/use_data.html>

---

## The Three Data Locations

| Location | Use for | Access via |
|---|---|---|
| `data/*.rda` | R objects users can load with `data()` | `data(name)` |
| `R/sysdata.rda` | R objects internal to your package | direct symbol |
| `inst/extdata/` | Raw files (CSV, JSON, images, parquet, etc.) | `system.file()` |

Plus `data-raw/`: scripts that produce the artifacts above. Not shipped.

---

## `data/` — Exported R Datasets

Lazy-loaded R objects available via `data()`. Each `.rda` file holds one
named object with the same name as the file.

Create with `usethis::use_data()`:

```r
my_dataset <- tibble::tibble(x = 1:10, y = letters[1:10])
usethis::use_data(my_dataset)
# writes data/my_dataset.rda
```

Document in `R/data.R`:

```r
#' Sample dataset for demonstrating x and y
#'
#' @format A tibble with 10 rows and 2 columns:
#' \describe{
#'   \item{x}{Integer values 1-10.}
#'   \item{y}{Lowercase letters a-j.}
#' }
#' @source Generated with `data-raw/my_dataset.R` from `mtcars`.
"my_dataset"
```

Access (user-facing):

```r
data(my_dataset, package = "mypkg")
mypkg::my_dataset       # also works thanks to LazyData: true
```

DESCRIPTION must include:

```dcf
LazyData: true
```

## `R/sysdata.rda` — Internal Data

Use for lookup tables, pre-computed constants, etc. that your package code
needs but should not expose to users.

```r
internal_lookup <- c("a" = 1L, "b" = 2L, "c" = 3L)
usethis::use_data(internal_lookup, internal = TRUE)
# writes R/sysdata.rda
```

Access from package code with the bare symbol:

```r
my_function <- function(key) {
  internal_lookup[[key]]
}
```

## `inst/extdata/` — Raw Files

Use for non-R files: CSV, JSON, parquet, images, fixtures, schemas.
Files in `inst/<x>/` end up at `system.file("<x>/", package = "mypkg")`
in the installed package.

```bash
mkdir -p inst/extdata
cp config_schema.json inst/extdata/
```

Access:

```r
schema_path <- system.file("extdata", "config_schema.json", package = "mypkg")
fs::path_package("mypkg", "extdata", "config_schema.json")  # equivalent
```

For test fixtures, prefer `tests/testthat/fixtures/` (loaded via
`testthat::test_path()`) — those don't ship in the installed package.

---

## `data-raw/` — Reproducible Data Prep

Scripts that produce `data/*.rda` and `R/sysdata.rda`. Not shipped to users.

```r
usethis::use_data_raw("my_dataset")
# creates data-raw/my_dataset.R + .Rbuildignore entry
```

Each script ends with `usethis::use_data(name, overwrite = TRUE)`. Re-run
when the source changes; commit both the script and the regenerated `.rda`.

`.Rbuildignore` must contain `^data-raw$` (added by `use_data_raw()`).

---

## CRAN Size Limits

| Limit | Source |
|---|---|
| Total package size | 5 MB (CRAN policy) |
| Single file in `inst/extdata` | unbounded but counts toward 5 MB |
| `data/*.rda` lazy-load | counts toward 5 MB |

Diagnose:

```r
tools::checkRdaFiles("data/")
```

Output shows compression and size for each `.rda`. Fix oversized files:

```r
usethis::use_data(big_dataset, overwrite = TRUE, compress = "xz")
# Try compress = "xz", "bzip2", "gzip" and pick the smallest.
```

If still too large, host data in a separate "data package" (e.g.,
`mypkgdata`) on a drat repo or use `pins`/`piggyback` for >5 MB files.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Editing `.rda` directly in `data/` | Edit `data-raw/*.R` and rerun `use_data()` |
| Using `read.csv()` on `inst/extdata` at package load | Use `system.file()` lazily inside functions |
| Committing intermediate files in `data-raw/` | Add to `.gitignore` and `.Rbuildignore` |
| Missing `LazyData: true` for `data/` | `usethis::use_lazy_data()` |
| Hard-coded path like `data/file.csv` | `system.file("extdata", "file.csv", package = "mypkg")` |
| Object name in `data/foo.rda` differs from file name | Rename — they must match |
| Documenting datasets via `@docType data` | Use the `"name"` literal pattern shown above |
```

- [ ] **Step 2: Verify**

```bash
wc -l skills/r-package-dev/references/data-and-assets.md   # 130-170 lines
grep -n '%>%' skills/r-package-dev/references/data-and-assets.md   # empty
```

- [ ] **Step 3: Run verification gates**

- [ ] **Step 4: Commit**

```bash
git add skills/r-package-dev/references/data-and-assets.md
git commit -m "feat(r-package-dev): add data-and-assets reference (data/, inst/extdata, sysdata)"
```

---

## Task 7: Promote S7 in `class-systems-guide.md`

**Files:**
- Modify: `skills/r-package-dev/references/class-systems-guide.md`

- [ ] **Step 1: Read current file**

Read `skills/r-package-dev/references/class-systems-guide.md` end to end. Note the existing decision tree (lines ~17–27) and the section on S7.

- [ ] **Step 2: Replace the decision tree**

Replace the current decision tree block (lines starting with the code fence after "## Decision Tree" through "Rule of thumb: Start with S3 unless you have a specific reason not to.") with:

```markdown
## Decision Tree

```
Need mutable state (caching, connections, environments)?
  YES -> R6
  NO  -> Bioconductor package or interfacing with existing S4 ecosystem?
    YES -> S4
    NO  -> Greenfield class hierarchy?
      YES -> S7 (default for new code in 2025+)
      NO  -> S3 (one-off methods on existing classes; minimal ceremony)
```

**Rule of thumb (2025+):** S7 for new class hierarchies. S3 for adding a
method or two to an existing object. R6 only when you genuinely need
reference semantics. S4 only for Bioconductor compatibility.
```

- [ ] **Step 3: Replace/expand the S7 section**

Find the existing S7 section (search for `## S7` or `### S7`). Replace its body with a complete primer:

```markdown
## S7 — Modern Successor to S3 / S4

`S7` is the R Consortium's modern class system. It is on CRAN and intended
as the long-term successor to S3 and S4. Use it for new class hierarchies
unless you have a specific reason to use one of the others.

### Constructor: `new_class()`

```r
library(S7)

range_class <- new_class("range",
  properties = list(
    min = class_double,
    max = class_double
  ),
  validator = function(self) {
    if (length(self@min) != 1 || length(self@max) != 1) {
      "@min and @max must be length 1"
    } else if (self@min > self@max) {
      "@min must be <= @max"
    }
  }
)

x <- range_class(min = 1, max = 10)
x@min                                # 1
```

Properties replace S4 slots and S3 attributes. Access via `@`. Validation
runs on construction and on any property assignment.

### Methods: `new_generic()` + `method()`

```r
range_print <- new_generic("range_print", "x")
method(range_print, range_class) <- function(x) {
  cat(sprintf("[%g, %g]\n", x@min, x@max))
}

range_print(x)                       # [1, 10]
```

Generic registration is explicit — no `UseMethod()` magic, no S4
`setGeneric()` ceremony.

### Inheritance

```r
positive_range <- new_class("positive_range",
  parent = range_class,
  validator = function(self) {
    if (self@min < 0) "@min must be >= 0"
  }
)
```

Multiple inheritance is not supported (intentional simplification vs S4).

### S3 → S7 Migration

| S3 | S7 |
|---|---|
| `structure(list(...), class = "foo")` | `foo_class <- new_class("foo", properties = list(...))` |
| `attr(x, "name")` / `x$name` | `x@name` |
| `print.foo <- function(x, ...) {}` | `method(print, foo_class) <- function(x, ...) {}` |
| `UseMethod("fn")` | `new_generic("fn", "x")` |

Migrate incrementally: register S7 methods on `class_any` to handle existing
S3 objects, then re-shape internals over time. `S7::S7_dispatch()` interops
with both directions.

### S4 → S7 Migration

| S4 | S7 |
|---|---|
| `setClass("foo", representation(...))` | `foo_class <- new_class("foo", properties = list(...))` |
| Slots (`@`) | Properties (`@`, same syntax) |
| `setValidity` | `validator = function(self) {}` |
| `setGeneric` + `setMethod` | `new_generic` + `method()` |
| `@include` for collation order | Same — S7 still requires Collate when generics depend on classes defined later |
| Multiple dispatch | Use multi-arg generics: `new_generic("fn", c("x", "y"))` |

S7 was designed to make S4-style packages migrateable. The `methods` import
goes away; `S7` becomes the single dependency.

### When NOT to Use S7

- Mutable state needed → use R6.
- Bioconductor package (interop with `BiocGenerics`/`SummarizedExperiment`/
  etc.) → use S4.
- Adding one or two methods to an existing S3 object → just write S3 methods.
```

- [ ] **Step 4: Verify**

```bash
wc -l skills/r-package-dev/references/class-systems-guide.md   # should now be 380-420
grep -n '%>%' skills/r-package-dev/references/class-systems-guide.md   # empty
grep -n 'S7' skills/r-package-dev/references/class-systems-guide.md | wc -l   # > 10
```

- [ ] **Step 5: Run verification gates**

- [ ] **Step 6: Commit**

```bash
git add skills/r-package-dev/references/class-systems-guide.md
git commit -m "feat(r-package-dev): promote S7 to first-class with migration recipes"
```

---

## Task 8: Restructure `r-cmd-check-troubleshooting.md` to Saw/Cause/Fix/Verify

**Files:**
- Modify: `skills/r-package-dev/references/r-cmd-check-troubleshooting.md`

- [ ] **Step 1: Read the current file**

Read all 411 lines of `skills/r-package-dev/references/r-cmd-check-troubleshooting.md`.

- [ ] **Step 2: Restructure existing entries**

Each entry currently has heading + Cause + Fix. Restructure to a 4-block format. For every existing entry, ensure all four blocks appear under the heading:

```markdown
### "<exact error string from R CMD check>"

**Saw:** verbatim output that triggered this entry.

**Cause:** one sentence root cause.

**Fix:**

```r
# code that fixes it
```

**Verify:** the exact command that proves the fix worked.
```

For example, the existing "no visible global function definition for 'fn'" entry becomes:

```markdown
### "no visible global function definition for 'fn'"

**Saw:**

```
* checking R code for possible problems ... NOTE
  my_fn: no visible global function definition for 'mutate'
```

**Cause:** `mutate()` used without an import declaration; R CMD check cannot
resolve the symbol at parse time.

**Fix:**

```r
# Preferred — explicit at call site
my_fn <- function() {
  data |> dplyr::mutate(x = 1)
}

# Alternative — declare in roxygen
usethis::use_import_from("dplyr", "mutate")
devtools::document()
```

**Verify:**

```r
devtools::check()       # NOTE gone
```
```

Repeat the Saw/Cause/Fix/Verify pattern for every existing entry in the file.

- [ ] **Step 3: Add the 5 new modern entries**

Append (in the appropriate section: ERRORs / WARNINGs / NOTEs) these five entries using the same 4-block format. Drop them in the WARNINGs/NOTEs sections appropriately:

```markdown
### "installed size of XX MB exceeds CRAN limits"

**Saw:**

```
* checking installed package size ... NOTE
  installed size is  6.2Mb
  sub-directories of 1Mb or more:
    data  4.5Mb
    R     1.1Mb
```

**Cause:** Total package install size > 5 MB (CRAN policy). Usually large
`data/*.rda`, vignette outputs, or compiled object files.

**Fix:**

```r
# Compress data/
usethis::use_data(my_dataset, overwrite = TRUE, compress = "xz")
tools::checkRdaFiles("data/")   # see resulting sizes

# For files > 5 MB total: split into a separate data package.
```

**Verify:**

```r
devtools::check()    # NOTE about install size gone
```

### "package requires R (>= 4.1.0)"

**Saw:**

```
* using R version 4.0.5 (2021-03-31)
* checking package dependencies ... ERROR
  Packages required but not available: ...
  Cannot import 'mypkg' because it depends on R 4.1.0
```

**Cause:** Code uses native `|>` (R >= 4.1.0) or `\(x)` lambda (R >= 4.1.0)
without declaring the version constraint.

**Fix:** in `DESCRIPTION`:

```dcf
Depends:
    R (>= 4.1.0)
```

**Verify:**

```r
desc::desc()$get("Depends")    # shows R (>= 4.1.0)
devtools::check()               # ERROR gone
```

### "Authors@R: ... missing required fields"

**Saw:**

```
* checking DESCRIPTION meta-information ... WARNING
  Malformed Authors@R field: ...
```

**Cause:** `Authors@R` field is malformed — common: missing `role`, missing
`email` for the maintainer, ORCID without `comment`.

**Fix:**

```dcf
Authors@R: c(
    person("Ada", "Lovelace", , "ada@example.com",
           role = c("aut", "cre"),
           comment = c(ORCID = "0000-0002-1825-0097")),
    person("Charles", "Babbage", role = "ctb"))
```

The maintainer must have role `cre`. ORCID format is the bare `0000-...` ID.

**Verify:**

```r
desc::desc()$get_authors()      # shows valid person objects
devtools::check()                # WARNING gone
```

### "Description does not end with a full stop"

**Saw:**

```
* checking DESCRIPTION meta-information ... WARNING
  Malformed Description field: should contain one or more complete sentences.
```

**Cause:** `Description` field doesn't end with a period (.), question mark
(?), or exclamation point (!).

**Fix:** in `DESCRIPTION` — make sure the field ends with a period:

```dcf
Description: Tools for fetching weather forecasts from public APIs and
    summarising them as tibbles.
```

**Verify:**

```r
devtools::check()    # WARNING gone
```

### "vignette engine X registered but no vignettes"

**Saw:**

```
* checking package vignettes in 'inst/doc' ... WARNING
  Package vignette(s) declared in DESCRIPTION but none found
```

**Cause:** `VignetteBuilder` declared in DESCRIPTION but `vignettes/` is
empty or missing the engine declaration in `.Rmd` YAML.

**Fix:** ensure each vignette `.Rmd` has the engine in its YAML:

```yaml
---
title: "Getting started"
output: rmarkdown::html_vignette
vignette: >
  %\VignetteIndexEntry{Getting started}
  %\VignetteEngine{knitr::rmarkdown}
  %\VignetteEncoding{UTF-8}
---
```

And DESCRIPTION:

```dcf
VignetteBuilder: knitr
Suggests: knitr, rmarkdown
```

**Verify:**

```r
devtools::build_vignettes()    # produces inst/doc/*.html
devtools::check()               # WARNING gone
```
```

- [ ] **Step 4: Verify**

```bash
wc -l skills/r-package-dev/references/r-cmd-check-troubleshooting.md   # 480-540 expected
grep -c '^**Saw:**' skills/r-package-dev/references/r-cmd-check-troubleshooting.md   # > 15
grep -c '^**Verify:**' skills/r-package-dev/references/r-cmd-check-troubleshooting.md  # > 15
grep -n '%>%' skills/r-package-dev/references/r-cmd-check-troubleshooting.md   # empty
```

- [ ] **Step 5: Run verification gates**

- [ ] **Step 6: Commit**

```bash
git add skills/r-package-dev/references/r-cmd-check-troubleshooting.md
git commit -m "feat(r-package-dev): restructure check troubleshooting to Saw/Cause/Fix/Verify + 5 modern entries"
```

---

## Task 9: Expand `roxygen2-tags.md`

**Files:**
- Modify: `skills/r-package-dev/references/roxygen2-tags.md`

- [ ] **Step 1: Read the current file**

Read all 356 lines of `skills/r-package-dev/references/roxygen2-tags.md`.

- [ ] **Step 2: Add new tag entries**

Append a new section "## Cross-reference and Reuse Tags" (or insert in the appropriate place if a similar section exists). Each entry follows the existing format (heading, prose, code example):

```markdown
### `@inheritParams source`

Reuse `@param` definitions from another function to avoid duplication.

```r
#' Filter forecast by precipitation
#' @inheritParams fetch_forecast
#' @param min_mm Numeric. Minimum precipitation in mm.
#' @export
filter_forecast <- function(city, days = 3L, min_mm = 0) { ... }
```

`@inheritParams` reuses every `@param` from `fetch_forecast()` that isn't
explicitly overridden in this block.

### `@describeIn obj`

Document multiple methods on one Rd page (typically S3/S4/S7 method dispatch).

```r
#' Print a forecast
#' @export
print.forecast <- function(x, ...) { ... }

#' @describeIn print.forecast Compact one-line summary
#' @export
format.forecast <- function(x, ...) { ... }
```

Both end up on `?print.forecast` with sub-sections.

### `@rdname name`

Combine multiple functions into one Rd file.

```r
#' Add or remove a column
#'
#' @param data A tibble.
#' @rdname column_ops
#' @export
add_column <- function(data, ...) { ... }

#' @rdname column_ops
#' @export
remove_column <- function(data, ...) { ... }
```

Both functions documented together at `?column_ops`.

### `@family family-name`

Group related functions in a "See also" section automatically.

```r
#' @family summary functions
weighted_mean <- function(...) { ... }

#' @family summary functions
weighted_sd <- function(...) { ... }
```

Each gets a `See also: weighted_sd` (or vice versa) link.

### `@srrstats "X.Y.Z"`

For rOpenSci statistical software peer review — record which standards
your code fulfills.

```r
#' Compute weighted mean
#' @srrstats {G2.1, G2.4} explicit input/output checking
weighted_mean <- function(x, w) { ... }
```

Only relevant if you submit to rOpenSci stats review; ignored otherwise.
```

Then append "## Lifecycle Badges" section:

```markdown
## Lifecycle Badges

Use the `lifecycle` package to communicate function maturity in roxygen.

```r
#' Compute experimental thing
#'
#' @description
#' `r lifecycle::badge("experimental")`
#'
#' Detail goes here.
#' @export
experimental_thing <- function(x) { ... }
```

Stages: `experimental`, `stable`, `superseded`, `deprecated`, `defunct`.
The expanded badge appears as an SVG image at the top of the help page.

For deprecated arguments specifically:

```r
#' @param old_arg `r lifecycle::badge("deprecated")` Use `new_arg` instead.
```

See `references/modern-toolchain.md` for the full lifecycle workflow.
```

Then append "## Markdown Link Forms" section:

```markdown
## Markdown Link Forms

With `Roxygen: list(markdown = TRUE)` in DESCRIPTION:

| Syntax | Renders as |
|---|---|
| `[fn()]` | Link to local function `fn` |
| `[pkg::fn()]` | Link to function in another package |
| `[topic][pkg::topic]` | Custom link text to topic |
| `<https://example.com>` | Auto-link URL |
| `[See guide][https://example.com]` | Custom-text URL |

Inside `@param`, `@return`, `@description`:

```r
#' @param method One of `"glm"` or `"lm"`. See [stats::glm()] and
#'   [stats::lm()] for details.
#' @return A [tibble::tibble()].
```

Wrapping with backticks renders as code; without renders as text.
```

- [ ] **Step 3: Verify**

```bash
wc -l skills/r-package-dev/references/roxygen2-tags.md   # 430-490 expected
grep -c '^### `@' skills/r-package-dev/references/roxygen2-tags.md   # > 15
grep -n '%>%' skills/r-package-dev/references/roxygen2-tags.md   # empty
```

- [ ] **Step 4: Run verification gates**

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/references/roxygen2-tags.md
git commit -m "feat(r-package-dev): add @inheritParams, @describeIn, @rdname, @family, lifecycle badges, Markdown link forms"
```

---

## Task 10: Add resubmission protocol to `cran-submission-checklist.md`

**Files:**
- Modify: `skills/r-package-dev/references/cran-submission-checklist.md`

- [ ] **Step 1: Read the current file**

Read `skills/r-package-dev/references/cran-submission-checklist.md`.

- [ ] **Step 2: Append a new section**

Add at the end of the file (or before any closing "Sources" footer):

```markdown
## Phase 5: After Submission

### CRAN Incoming Pending

After `submit_cran()`, your package sits in CRAN "incoming" pending review.
Status pages:

- <https://cran.r-project.org/web/packages/check.html> — package check status
- <https://cran.r-project.org/incoming/> — manual queue (HTTP 403 unless you're a maintainer of a queued package — the page is mostly informational)

Typical timeline: 1–7 business days. Some packages auto-accept (no policy
issues, no NOTEs); others get a human reviewer's email.

### `--as-cran` vs `devtools::check(cran = TRUE)`

These are not identical:

```bash
R CMD check --as-cran mypkg_1.0.0.tar.gz
```

vs

```r
devtools::check(cran = TRUE)
```

`devtools::check(cran = TRUE)` sets `_R_CHECK_CRAN_INCOMING_=true` and a few
related env vars, then runs `R CMD check`. It is functionally equivalent
**most** of the time. Differences:

- `--as-cran` runs the CRAN incoming checks (`installed size`, `URL check`
  via `urlchecker`, etc.) — `cran = TRUE` runs all of these too.
- `--as-cran` requires an installed package tarball; `devtools::check()`
  builds one for you.

For the final pre-submission check, **build the tarball and run
`R CMD check --as-cran` on it directly**. This matches what CRAN itself
runs on submission:

```bash
R CMD build .
R CMD check --as-cran mypkg_*.tar.gz
```

### Resubmission Protocol

If CRAN rejects (you'll receive an email from a CRAN maintainer):

1. **Read carefully.** Quote each issue verbatim into a new "Resubmission"
   section at the **top** of `cran-comments.md`.
2. **Do not push back** unless you genuinely disagree on policy interpretation
   — and even then, fix what you can and ask politely about the rest.
3. **Address every flagged issue.** Don't selectively fix.
4. **Update `cran-comments.md`:**

```markdown
## Resubmission

This is a resubmission. Compared to the previous submission:

* Replaced `\dontrun{}` with `\donttest{}` for examples that are slow but
  runnable (per Uwe's comment dated 2026-04-15).
* Added missing `\value{}` for `internal_helper()`.
* Ensured no example writes outside `tempdir()`.

## R CMD check results

0 errors | 0 warnings | 0 notes
```

5. **Re-run the gauntlet:**

```r
devtools::check(cran = TRUE)
urlchecker::url_check()
spelling::spell_check_package()
```

6. **Resubmit:**

```r
devtools::submit_cran()
```

Most rejections fall into a small set of buckets:

| Bucket | Typical fix |
|---|---|
| `\dontrun{}` overuse | Use `\donttest{}` or guard with `if (interactive())` |
| Writing outside `tempdir()` | Use `tempfile()` / `withr::local_tempdir()` |
| Modifying user environment | Use `withr::local_options()` and friends |
| Missing `\value{}` | Add `@returns` to roxygen, `document()` |
| `\dontrun{}` with side effects | Often fine but explain why in `cran-comments.md` |
| URL not reachable | Fix or remove; rerun `urlchecker::url_check()` |
| Description text issues | Quote function/package names with backticks; add full stops |
| `LICENSE` mismatch | Match `License:` field to actual `LICENSE` file content |

If a reviewer asks for clarification (not a rejection), reply in the email
thread within a few days. Do not resubmit until they ask you to.
```

- [ ] **Step 3: Verify**

```bash
wc -l skills/r-package-dev/references/cran-submission-checklist.md   # 350-410 expected
grep -n '%>%' skills/r-package-dev/references/cran-submission-checklist.md   # empty
```

- [ ] **Step 4: Run verification gates**

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/references/cran-submission-checklist.md
git commit -m "feat(r-package-dev): add resubmission protocol and incoming-pending workflow"
```

---

## Task 11: New `scripts/preflight.R`

**Files:**
- Create: `skills/r-package-dev/scripts/preflight.R`

- [ ] **Step 1: Write the script**

Create `skills/r-package-dev/scripts/preflight.R`:

```r
#!/usr/bin/env Rscript
# preflight.R -- Fast pre-check pipeline for an R package.
#
# Usage:  Rscript preflight.R [path/to/package]
#
# Runs, in order, the fast checks that should pass on every commit:
#   1. roxygen2::roxygenize()        -- regenerates man/ + NAMESPACE
#   2. lintr::lint_package()         -- style and bug-prone patterns
#   3. spelling::spell_check_package -- typos
#   4. urlchecker::url_check         -- URL validity
#
# Skips the slow R CMD check. Use scripts/check_package.R for that.
# Exits 0 on success, 1 on any failure.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

pkg_path <- normalizePath(pkg_path, mustWork = FALSE)
if (!dir.exists(pkg_path)) {
  stop(sprintf("Directory not found: %s", pkg_path))
}
desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) {
  stop(sprintf("No DESCRIPTION in %s -- not an R package.", pkg_path))
}

need <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf(
      "Package '%s' required. Install with install.packages(\"%s\").",
      pkg, pkg
    ))
  }
}

results <- list()
record <- function(name, ok, details = "") {
  results[[name]] <<- list(ok = ok, details = details)
  status <- if (ok) "PASS" else "FAIL"
  cat(sprintf("[%s] %s%s\n", status, name,
              if (nzchar(details)) paste0(" -- ", details) else ""))
}

cat(sprintf("\n=== Preflight: %s ===\n\n", pkg_path))

# ---- 1. roxygen2::roxygenize() ----
cat(">> Regenerating man/ and NAMESPACE...\n")
need("roxygen2")
rox_result <- tryCatch(
  roxygen2::roxygenize(pkg_path),
  error = function(e) e
)
if (inherits(rox_result, "error")) {
  record("roxygenize", FALSE, conditionMessage(rox_result))
} else {
  record("roxygenize", TRUE, "man/ + NAMESPACE up to date")
}

# ---- 2. lintr::lint_package() ----
if (requireNamespace("lintr", quietly = TRUE)) {
  cat("\n>> Linting...\n")
  lints <- tryCatch(
    lintr::lint_package(pkg_path),
    error = function(e) e
  )
  if (inherits(lints, "error")) {
    record("lintr", FALSE, conditionMessage(lints))
  } else {
    n <- length(lints)
    record("lintr", n == 0L,
           if (n > 0L) sprintf("%d lint(s); see lintr::lint_package() output", n)
           else "")
  }
} else {
  record("lintr", FALSE, "lintr not installed -- skipping")
}

# ---- 3. spelling::spell_check_package() ----
if (requireNamespace("spelling", quietly = TRUE)) {
  cat("\n>> Spell-checking...\n")
  typos <- tryCatch(
    spelling::spell_check_package(pkg_path),
    error = function(e) e
  )
  if (inherits(typos, "error")) {
    record("spelling", FALSE, conditionMessage(typos))
  } else {
    n <- nrow(typos)
    record("spelling", is.null(n) || n == 0L,
           if (!is.null(n) && n > 0L)
             sprintf("%d potential typos -- review inst/WORDLIST", n)
           else "")
  }
} else {
  record("spelling", FALSE, "spelling not installed -- skipping")
}

# ---- 4. urlchecker::url_check() ----
if (requireNamespace("urlchecker", quietly = TRUE)) {
  cat("\n>> Checking URLs...\n")
  urls <- tryCatch(
    urlchecker::url_check(pkg_path),
    error = function(e) e
  )
  if (inherits(urls, "error")) {
    record("url_check", FALSE, conditionMessage(urls))
  } else {
    n <- nrow(urls)
    record("url_check", is.null(n) || n == 0L,
           if (!is.null(n) && n > 0L) sprintf("%d problematic URLs", n)
           else "")
  }
} else {
  record("url_check", FALSE, "urlchecker not installed -- skipping")
}

# ---- Summary ----
cat("\n=== Summary ===\n")
n_pass <- sum(vapply(results, function(r) isTRUE(r$ok), logical(1)))
n_fail <- length(results) - n_pass
cat(sprintf("%d passed, %d failed of %d checks.\n",
            n_pass, n_fail, length(results)))

if (n_fail > 0L) {
  cat("\nFailures:\n")
  for (name in names(results)) {
    if (!isTRUE(results[[name]]$ok)) {
      cat(sprintf("  * %s: %s\n", name, results[[name]]$details))
    }
  }
  cat("\nResult: PREFLIGHT FAILED.\n")
  quit(status = 1L)
}

cat("\nResult: preflight clean. Run devtools::check() before push.\n")
quit(status = 0L)
```

- [ ] **Step 2: Make executable and verify**

```bash
chmod +x skills/r-package-dev/scripts/preflight.R
wc -l skills/r-package-dev/scripts/preflight.R   # 110-130 expected
grep -n '%>%' skills/r-package-dev/scripts/preflight.R   # empty
grep -n ' = ' skills/r-package-dev/scripts/preflight.R   # only function args
```

- [ ] **Step 3: Run verification gates**

- [ ] **Step 4: Commit**

```bash
git add skills/r-package-dev/scripts/preflight.R
git commit -m "feat(r-package-dev): add preflight.R for fast pre-check (lint, spell, urls)"
```

---

## Task 12: Polish `release_checklist.R` — `--with-revdep` flag

**Files:**
- Modify: `skills/r-package-dev/scripts/release_checklist.R`

- [ ] **Step 1: Read current arg parsing**

Read lines 14–25 of `skills/r-package-dev/scripts/release_checklist.R`.

- [ ] **Step 2: Add flag parsing**

Replace the args block at the top of the file:

```r
args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."
```

with:

```r
args <- commandArgs(trailingOnly = TRUE)
with_revdep <- "--with-revdep" %in% args
args <- args[!startsWith(args, "--")]
pkg_path <- if (length(args) >= 1) args[1] else "."
```

- [ ] **Step 3: Add a revdep step before the Summary block**

Find the comment `# ---- Summary ----` (around line 170). Immediately before it, insert:

```r
# ---- 7. Reverse dependency check (opt-in) ----
if (with_revdep) {
  if (requireNamespace("revdepcheck", quietly = TRUE)) {
    cat("\n>> Running revdepcheck::revdep_check() -- this can take an hour+...\n")
    revdep_result <- tryCatch(
      revdepcheck::revdep_check(pkg_path, num_workers = 4L),
      error = function(e) e
    )
    if (inherits(revdep_result, "error")) {
      record("revdepcheck", FALSE, conditionMessage(revdep_result))
    } else {
      record("revdepcheck", TRUE,
             "see revdep/ for per-package results")
    }
  } else {
    record("revdepcheck", FALSE,
           "revdepcheck not installed -- run pak::pkg_install(\"r-lib/revdepcheck\")")
  }
} else {
  cat("\n>> Skipping revdepcheck (pass --with-revdep to run; takes 30+ min).\n")
}
```

- [ ] **Step 4: Verify**

```bash
wc -l skills/r-package-dev/scripts/release_checklist.R   # 200-230 expected
grep -n '%>%' skills/r-package-dev/scripts/release_checklist.R   # empty
grep -n -- '--with-revdep' skills/r-package-dev/scripts/release_checklist.R   # 2-3 hits
```

- [ ] **Step 5: Run verification gates**

- [ ] **Step 6: Commit**

```bash
git add skills/r-package-dev/scripts/release_checklist.R
git commit -m "feat(r-package-dev): add --with-revdep flag to release_checklist.R"
```

---

## Task 13: Polish `audit_deps.R` — file:line reporting for unguarded Suggests

**Files:**
- Modify: `skills/r-package-dev/scripts/audit_deps.R`

- [ ] **Step 1: Read current Suggests check**

Read lines 123–150 of `skills/r-package-dev/scripts/audit_deps.R`. The current code reports a Suggests package as unguarded but does not say where.

- [ ] **Step 2: Replace `check_guards` and the reporting block**

Replace the `check_guards <- function(files, suggested) { ... }` definition and the loop that prints results with this version that returns and prints file:line locations:

```r
check_guards <- function(files, suggested) {
  results <- list()
  if (length(suggested) == 0L || length(files) == 0L) return(results)
  for (p in suggested) {
    locations <- list()
    guarded <- FALSE
    for (f in files) {
      lines <- readLines(f, warn = FALSE)
      use_idx <- grep(paste0("\\b", p, "::"), lines)
      guard_idx <- grep(
        paste0("requireNamespace\\(\\s*[\"']", p, "[\"']"),
        lines
      )
      if (length(guard_idx) > 0L) guarded <- TRUE
      if (length(use_idx) > 0L) {
        for (i in use_idx) {
          locations[[length(locations) + 1L]] <- list(
            file = f, line = i, text = trimws(lines[i])
          )
        }
      }
    }
    results[[p]] <- list(
      uses = length(locations) > 0L,
      guarded = guarded,
      locations = locations
    )
  }
  results
}

r_guard <- check_guards(r_files, suggests_pkgs)
any_issue <- FALSE
for (p in names(r_guard)) {
  info <- r_guard[[p]]
  if (isTRUE(info$uses) && !isTRUE(info$guarded)) {
    cat(sprintf("  * %s -- used in R/ but NOT guarded by requireNamespace():\n",
                p))
    for (loc in info$locations) {
      rel_file <- sub(paste0("^", pkg_path, "/"), "",
                      normalizePath(loc$file, mustWork = FALSE))
      cat(sprintf("      %s:%d  %s\n",
                  rel_file, loc$line, loc$text))
    }
    cat(sprintf(
      "    Fix: wrap with `if (!requireNamespace(\"%s\", quietly = TRUE))`\n",
      p
    ))
    any_issue <- TRUE
  }
}
if (!any_issue) cat("  (all Suggests used in R/ appear guarded)\n")
cat("\n")
```

- [ ] **Step 3: Verify**

```bash
wc -l skills/r-package-dev/scripts/audit_deps.R   # 195-220 expected
grep -n '%>%' skills/r-package-dev/scripts/audit_deps.R   # empty
```

- [ ] **Step 4: Run verification gates**

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/scripts/audit_deps.R
git commit -m "feat(r-package-dev): report file:line for unguarded Suggests in audit_deps.R"
```

---

## Task 14: Sharpen `eval.md`

**Files:**
- Modify: `skills/r-package-dev/eval.md`

- [ ] **Step 1: Replace Success Criteria section**

In `skills/r-package-dev/eval.md`, replace the current "Success Criteria" section with:

```markdown
## Success Criteria

### Required content (positive criteria)

- Happy-path roxygen response MUST include **all five** of:
  - `@param` for every argument
  - `@returns` (or `@return`)
  - `@examples`
  - `@export`
  - An explicit `devtools::document()` invocation
- CRAN-readiness response MUST include **all five** of:
  - `devtools::check(cran = TRUE)` (or `R CMD check --as-cran`)
  - `urlchecker::url_check()` (or `urlchecker`)
  - `spelling::spell_check_package()` (or `spelling`)
  - `cran-comments.md`
  - `NEWS.md`
- NAMESPACE conflict response MUST mention **at least two** of:
  - selective `@importFrom`
  - `pkg::fn()` qualified calls
  - `usethis::use_import_from()`
  - package-level conflict resolution (`conflicted` or `.conflicts.OK`)
- S4 method registration response MUST mention **at least two** of:
  - `setGeneric()` / `setMethod()`
  - `@include` collation tag
  - `Collate:` field in `DESCRIPTION`
  - `methods::existsMethod()` for verification
- Reverse dependency response MUST reference one of: `revdepcheck::revdep_check()`,
  `revdepcheck` package, or `--with-revdep` flag of `release_checklist.R`.
- S7 migration response MUST mention **all three** of: `S7::new_class`,
  property syntax (`@prop`), `S7::method()`-style generic registration.

### Forbidden content (negative criteria)

- Pure scaffolding prompt MUST be deferred to `r-project-setup`; response
  MUST NOT contain `usethis::create_package()`.
- Test-writing prompt MUST be deferred to `r-tdd`; response MUST NOT contain
  `test_that()` blocks.
- Skill-generation prompt MUST be deferred to `r-package-skill-generator`;
  response MUST NOT contain SKILL.md content.
- Response MUST NOT use `:::` to access internal functions in other packages.
- Response MUST NOT skip or downplay `R CMD check` for any workflow that
  touches NAMESPACE or exports.
- Response MUST NOT use `%>%`, `=` for assignment, or single quotes for strings.
- Response MUST NOT recommend `@docType package` (deprecated) — must use
  `_PACKAGE` sentinel.
```

- [ ] **Step 2: Add new test prompts**

Append to the "### Edge Cases" section (or appropriate place):

```markdown
- "I have an S4 class hierarchy with three classes (Animal, Dog extends Animal, Cat extends Animal) plus methods. Walk me through migrating to S7 step-by-step."

- "Open a release issue using `usethis::use_release_issue()` and walk me through the checklist for a 0.4.0 minor release. My package has no reverse dependencies."
```

Append to the "## Binary Eval Questions" section two new questions:

```markdown
8. When asked about S7 vs S4 for a new class hierarchy, does the skill recommend S7 as the default for greenfield work?
9. When asked about a release workflow, does the skill mention `usethis::use_release_issue()` rather than walking through manual steps?
```

- [ ] **Step 3: Verify**

```bash
wc -l skills/r-package-dev/eval.md
grep -c '^- ' skills/r-package-dev/eval.md   # > 25
```

- [ ] **Step 4: Run verification gates**

Eval.md is excluded from `%>%` grep but still counted by `verify_batch.py`.

- [ ] **Step 5: Commit**

```bash
git add skills/r-package-dev/eval.md
git commit -m "feat(r-package-dev): sharpen eval.md success criteria + S7 and release-issue prompts"
```

---

## Task 15: Final verification gauntlet

**Files:** none modified — verification only

- [ ] **Step 1: Re-read SKILL.md end-to-end**

Read `skills/r-package-dev/SKILL.md` from line 1 to end. Verify:

- All references mentioned in lazy-reference lists exist in `references/`
- All scripts mentioned exist in `scripts/`
- No broken cross-references (`references/<name>.md` → file present)
- No contradictions between sections (e.g., "Use S3 by default" vs "Use S7 by default")
- Decision tree at top is consistent with class systems guide

- [ ] **Step 2: Run all verification gates**

```bash
python skills/skill-auditor/scripts/score_skill.py skills/r-package-dev \
  --siblings-dir skills --conventions rules/r-conventions.md --max-lines 300 \
  --format table

python skills/skill-auditor/scripts/verify_batch.py skills --all --max-lines 300

grep -rn '%>%' skills/r-package-dev --exclude=eval.md

python tests/run_all.py
```

Expected:
- Score: 17/17 PASS
- All file size checks pass
- `%>%` grep returns no matches
- All plugin tests pass

- [ ] **Step 3: Verify line count budget**

```bash
wc -l skills/r-package-dev/SKILL.md   # <= 300
wc -l skills/r-package-dev/references/*.md   # each <= 500 (project soft cap)
wc -l skills/r-package-dev/scripts/*.R       # each <= 250
```

- [ ] **Step 4: Manual judgment-check spot review**

Re-run the audit's judgment criteria against the upgraded skill:

| Check | Target |
|---|---|
| G3 edge cases | Now covered by `If you see X → do Y` triplets in Gotchas |
| G5 ambiguity | Vague phrases removed; specific triggers everywhere |
| G6 scope constraints | New "Scope Discipline" section in SKILL.md |
| E1 I/O pairs | Not changed (judgment) — accept as-is |
| V1 feedback loop | Named loop in Development Loop subsection |
| V5 MCP qualification | All `btw:` prefixed |
| T4 success criteria | Measurable with N-of-M counts |

- [ ] **Step 5: Final commit (if any cleanup needed)**

If the spot review surfaced any issues, fix them in a single cleanup commit:

```bash
git add -A
git commit -m "chore(r-package-dev): final cleanup from verification spot review"
```

If no cleanup needed, skip this step.

- [ ] **Step 6: Push and offer to merge**

The worktree branch is `worktree-upgrade-r-package-dev`. Show the user:

```bash
git log --oneline main..HEAD
```

Confirm with the user before pushing or merging back to main.

---

## Self-Review Notes (post-write)

- Spec coverage: every section in `2026-04-28-r-package-dev-upgrade-design.md` maps to one or more tasks (Section 3.1 → Tasks 1-3; 3.2 → Tasks 4-6; 3.3 → Tasks 7-10; 3.4 → Tasks 11-13; 3.5 → Task 14; 3.6 → Task 1; 3.7 verification → Task 15 + each task's gates).
- No placeholders. Every code block is concrete content the engineer can paste.
- Type/name consistency: `preflight.R`, `release_checklist.R`, `audit_deps.R` referenced consistently throughout. `references/modern-toolchain.md`, `release-workflow.md`, `data-and-assets.md` — all three names used identically across SKILL.md update (Task 2) and creation tasks (Tasks 4-6).
- Verification gates explicitly scripted at every commit, not just at the end.
- Line-count budget tracked per task with exact `wc -l` expectations.
