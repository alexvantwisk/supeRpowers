---
name: r-package-dev
description: >
  Use when creating, developing, documenting, or submitting R packages. Provides
  full-lifecycle guidance on usethis, devtools, roxygen2, pkgdown, NAMESPACE
  management, DESCRIPTION metadata, vignettes, CRAN submission, and CI/CD
  workflows.
  Triggers: R package, usethis, devtools, roxygen2, NAMESPACE, DESCRIPTION,
  pkgdown, CRAN submission, vignette, R CMD check, package development.
  Do NOT use for initial project scaffolding only — use r-project-setup instead.
  Do NOT use for writing package tests — use r-tdd instead.
  For a guided release workflow, invoke /r-cmd-pkg-release instead.
---

# R Package Development

Full lifecycle R package development using the modern toolchain:
usethis, devtools, roxygen2, testthat 3e, pkgdown, and CRAN submission.

All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- `references/description-fields.md` — every DESCRIPTION field, valid values, CRAN-safe templates
- `references/roxygen2-tags.md` — complete roxygen2 tag reference with examples
- `references/namespace-patterns.md` — `@importFrom` vs `::`, re-exports, conflict resolution
- `references/class-systems-guide.md` — S3, S4, S7, R6 comparison with decision tree
- `references/pkgdown-site-config.md` — `_pkgdown.yml` layout, theming, GitHub Pages deploy
- `references/r-cmd-check-troubleshooting.md` — every common ERROR/WARNING/NOTE and how to fix it
- `references/cran-submission-checklist.md` — step-by-step CRAN submission workflow
- `references/revdep-workflow.md` — reverse dependency checking with `revdepcheck`

**Scripts:**
- `scripts/check_package.R` — run `devtools::check()` and print summary
- `scripts/release_checklist.R` — full pre-release gauntlet (check, URLs, spelling, DESCRIPTION, NEWS)
- `scripts/validate_description.R` — validate DESCRIPTION fields against CRAN rules
- `scripts/audit_deps.R` — find unused imports, missing deps, unguarded Suggests
- `scripts/check_docs.R` — verify roxygen2 coverage for every exported function
- `scripts/lint_package.R` — run lintr with tidyverse-style linters

**Agent dispatch:**
- Dispatch to **r-pkg-check** agent after `devtools::check()` for deep issue resolution
- Dispatch to **r-dependency-manager** agent for dependency questions

**MCP integration (when R session available):**
- `btw_tool_docs_help_page` — read existing docs before editing roxygen2
- `btw_tool_docs_package_help_topics` — list exported functions before NAMESPACE edits
- `btw_tool_sessioninfo_is_package_installed` — check before adding a dependency

---

## Package Scaffold

> **Boundary:** Package scaffold as part of ongoing development. For initial project scaffolding only, use r-project-setup instead.

```r
usethis::create_package("path/to/mypkg")
usethis::use_testthat(3)
usethis::use_pipe(type = "base")       # |> re-export, R >= 4.1.0
usethis::use_roxygen_md()              # Markdown in roxygen
usethis::use_mit_license()             # Or use_gpl3_license()
usethis::use_git(); usethis::use_github()
usethis::use_readme_rmd(); usethis::use_news_md()
```

Fill `Title`, `Description`, `Authors@R` (use `person()`), `URL`,
`BugReports` immediately. See `references/description-fields.md` for
every field's rules. Validate with
`Rscript scripts/validate_description.R .`.

---

## Development Loop

```
load_all() -> test() -> document() -> check()
```

```r
devtools::load_all()      # Simulate library(mypkg) from source
devtools::test()          # Run testthat suite
devtools::document()      # Rebuild NAMESPACE + man/ from roxygen2
devtools::check()         # Full R CMD check (run before every commit)
```

**Quick iteration:** `load_all()` + `test_active_file()` while developing a
single function. Run full `check()` before pushing.

---

## Documentation with roxygen2

Markdown enabled via `Roxygen: list(markdown = TRUE)` in DESCRIPTION.

```r
#' Compute weighted summary statistics
#'
#' @param data A data frame or tibble.
#' @param value_col <[`data-masking`][rlang::args_data_masking]> Column to summarise.
#' @param weight_col <[`data-masking`][rlang::args_data_masking]> Optional weights.
#' @param na_rm Logical. Remove `NA` values before computation? Default `TRUE`.
#' @returns A tibble with columns `mean` and `sd`.
#' @examples
#' mtcars |> weighted_summary(mpg)
#' @family summary functions
#' @export
weighted_summary <- function(data, value_col, weight_col = NULL, na_rm = TRUE) {
  # implementation
}
```

**Rules:** `@param` for every argument, `@returns` + `@examples` mandatory
for all exported functions, `<data-masking>` / `<tidy-select>` tags for
tidy eval arguments. Run `Rscript scripts/check_docs.R .` to verify
coverage. See `references/roxygen2-tags.md` for the full tag reference.

---

## NAMESPACE and Dependencies

```r
usethis::use_package("dplyr")                   # Adds to Imports
usethis::use_package("ggplot2", type = "Suggests")  # Optional dep
usethis::use_import_from("rlang", ".data")      # Selective import
```

| Strategy | When to use |
|----------|-------------|
| `pkg::fun()` | Default. Clear provenance, no NAMESPACE clutter. |
| `@importFrom pkg fun` | Hot loops, or used > 10 times in one file. |
| `use_import_from()` | Operators (`|>`, `:=`, `.data`) and infix functions. |

**Never** use `@import pkg` (imports entire namespace, collision risk).
Read `references/namespace-patterns.md` for re-exports, S4 collation
order, and conflict resolution with downstream packages. Audit an
existing package with `Rscript scripts/audit_deps.R .`.

---

## Class Systems (Overview)

| System | When to use | Key trait |
|--------|-------------|-----------|
| **S3** | Most packages | Simple, informal, `UseMethod()` dispatch |
| **S4** | Bioconductor, formal interfaces | Slots, validity, multiple dispatch |
| **S7** | Greenfield projects | Modern S3/S4 successor, properties |
| **R6** | Mutable state (caching, connections) | Reference semantics, `$new()` |

Read `references/class-systems-guide.md` for constructors, methods, and
decision tree for each system.

---

## Compiled Code with Rcpp

```r
usethis::use_rcpp()                # Sets up src/, Makevars, roxygen tags
usethis::use_rcpp_armadillo()      # For linear algebra
# After editing src/*.cpp: devtools::document() then devtools::load_all()
```

Tag the package-level doc with `@useDynLib mypkg, .registration = TRUE`.

---

## Vignettes and pkgdown

```r
usethis::use_vignette("getting-started")    # vignettes/*.Rmd
usethis::use_pkgdown()                      # Sets up pkgdown site
usethis::use_pkgdown_github_pages()         # Auto-deploy via GitHub Pages
```

One topic per vignette. For `_pkgdown.yml` layout, theming, and deployment,
read `references/pkgdown-site-config.md`.

---

## Testing in Packages

> **Boundary:** R CMD check and package-level quality gates. For TDD workflow, test-first methodology, and snapshot tests, use r-tdd instead.

Package-level gates (not test authoring):

```r
devtools::test()                      # Run testthat suite
covr::package_coverage()              # Coverage report
testthat::skip_on_cran()              # Use for slow / networked tests
```

For diagnosing check failures, read `references/r-cmd-check-troubleshooting.md`
or run `Rscript scripts/check_package.R` against your package.

---

## CRAN Submission

Run the gauntlet: `Rscript scripts/release_checklist.R .`. It chains:

```r
devtools::check(cran = TRUE)          # 0 errors, 0 warnings mandatory
rhub::check_for_cran()                # Multi-platform
urlchecker::url_check()               # URL validity
spelling::spell_check_package()       # Typos
revdepcheck::revdep_check()           # For updates — see references/revdep-workflow.md
```

Prepare `cran-comments.md` with test environments and check results.
Update `NEWS.md`. Then `devtools::submit_cran()`. Read
`references/cran-submission-checklist.md` for the full guide, rejection
reasons, and resubmission protocol.

---

## CI/CD with GitHub Actions

```r
usethis::use_github_action("check-standard")    # R CMD check on 3 OSes + R-devel
usethis::use_github_action("test-coverage")     # covr + codecov
usethis::use_github_action("pkgdown")           # Build and deploy site
usethis::use_github_action("lint")              # lintr checks
```

Creates `.github/workflows/*.yaml`. Badge with
`usethis::use_github_actions_badge("R-CMD-check")`.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `@import pkg` (whole namespace) | Use `@importFrom pkg fun` or `pkg::fun()` |
| Forgetting `document()` after roxygen edits | Run `document()` after every edit |
| `library()` inside `R/` | Use `pkg::fun()` or `@importFrom` |
| Missing `@export` on public function | Add `@export`, then `document()` |
| Hardcoded paths | `testthat::test_path()`, `system.file()`, `fs::path_package()` |
| Dep used but not declared | `usethis::use_package("dep")` |
| `Depends:` instead of `Imports:` | `Imports:` for almost everything; `Depends:` only for R version |
| Reaching into another package with `:::` | CRAN rejects; request export or re-implement |
| Scope creep | Fix only the identified issue; show minimal diff |

See `references/r-cmd-check-troubleshooting.md` for every common
ERROR/WARNING/NOTE.

---

## Examples

### Happy Path: New package with a documented function

**Prompt:** "Create a new R package called tidyweather with a documented function."

```r
usethis::create_package("~/tidyweather")
usethis::use_testthat(3); usethis::use_pipe(type = "base")
usethis::use_mit_license(); usethis::use_package("httr2")

# R/fetch_forecast.R
#' Fetch weather forecast for a city
#' @param city Character. City name to query.
#' @param days Integer. Number of forecast days (1-7). Default `3`.
#' @returns A tibble with columns `date`, `temp_high`, `temp_low`.
#' @examples fetch_forecast("London", days = 5)
#' @export
fetch_forecast <- function(city, days = 3L) {
  stopifnot(is.character(city), length(city) == 1L, days >= 1L, days <= 7L)
  # ... implementation using httr2
}

devtools::document()   # Regenerates NAMESPACE + man/
devtools::check()      # 0 errors, 0 warnings -> ready
```

### Edge Case: NAMESPACE conflict from .data in dplyr NSE

**Prompt:** "R CMD check warns about .data not found in NAMESPACE."

```r
# Input — .data[[var]] used but NAMESPACE has no import
filter_column <- function(data, col, min_val) {
  data |> dplyr::filter(.data[[col]] >= min_val)
}

# Fix — import .data from rlang (NOT dplyr)
usethis::use_import_from("rlang", ".data")
devtools::document()
# NAMESPACE gains: importFrom(rlang,.data); check passes.
```

**More example prompts:**
- "Add a `fetch_forecast()` function with full roxygen2 docs and tests"
- "Get this package ready for CRAN submission"
- "Create a pkgdown site grouping functions by topic"
- "Audit my package's dependencies — anything unused or missing?"
