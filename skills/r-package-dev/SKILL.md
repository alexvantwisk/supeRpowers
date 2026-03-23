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
---

# R Package Development

Full lifecycle R package development using the modern toolchain:
usethis, devtools, roxygen2, testthat 3e, pkgdown, and CRAN submission.

All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/cran-submission-checklist.md` for step-by-step CRAN submission guide
- Read `references/class-systems-guide.md` for detailed R class system comparison

**Agent dispatch:**
- Dispatch to **r-pkg-check** agent after `devtools::check()` for deep issue resolution
- Dispatch to **r-dependency-manager** agent for dependency questions

---

## Package Scaffold

```r
usethis::create_package("path/to/mypkg")

# Inside the new package:
usethis::use_testthat(3)
usethis::use_pipe(type = "base")       # Adds |> re-export, sets min R >= 4.1.0
usethis::use_roxygen_md()              # Enables markdown in roxygen2 comments
usethis::use_mit_license()             # Or use_gpl3_license(), use_cc0_license()
usethis::use_git()
usethis::use_github()                  # Creates remote, pushes initial commit
usethis::use_readme_rmd()              # README.Rmd -> README.md via knit
usethis::use_news_md()                 # NEWS.md for changelog
```

Creates `DESCRIPTION`, `NAMESPACE`, `R/`, `man/`, `tests/testthat/`, `LICENSE`,
`.Rbuildignore`. Fill `Title`, `Description`, `Authors@R` (use `person()`),
`URL`, `BugReports` immediately.

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
#' Calculates mean and standard deviation of a column, optionally weighted.
#'
#' @param data A data frame or tibble.
#' @param value_col <[`data-masking`][rlang::args_data_masking]> Column
#'   containing numeric values to summarise.
#' @param weight_col <[`data-masking`][rlang::args_data_masking]> Optional
#'   column of weights. If `NULL` (default), unweighted statistics are returned.
#' @param na_rm Logical. Remove `NA` values before computation? Default `TRUE`.
#'
#' @returns A tibble with columns `mean` and `sd`.
#'
#' @examples
#' mtcars |> weighted_summary(mpg)
#' mtcars |> weighted_summary(mpg, weight_col = wt)
#'
#' @family summary functions
#' @export
weighted_summary <- function(data, value_col, weight_col = NULL, na_rm = TRUE) {
  # implementation
}
```

**Rules:**
- `@param` for every parameter, `@returns` for every function (not `@return`)
- `@examples` mandatory for all exported functions
- `@family` to group related functions
- Tidy eval: use `<data-masking>` or `<tidy-select>` tags as shown above

---

## NAMESPACE Management

### Adding dependencies

```r
usethis::use_package("dplyr")                   # Adds to Imports
usethis::use_package("ggplot2", type = "Suggests")  # Optional dep
usethis::use_import_from("rlang", ".data")      # Selective import
usethis::use_import_from("rlang", c("abort", "warn", "inform"))
```

### `pkg::fun()` vs `@importFrom`

| Strategy | When to use |
|----------|-------------|
| `pkg::fun()` | Default. Clear provenance, no NAMESPACE clutter. |
| `@importFrom pkg fun` | Hot loops (avoids `::` lookup), frequently used (>10 calls). |
| `use_import_from()` | Operators (`|>`, `.data`) and infix functions. |

**Never** use `@import pkg` (imports entire namespace, collision risk).

---

## Class Systems (Overview)

| System | When to use | Key trait |
|--------|-------------|-----------|
| **S3** | Most packages | Simple, informal, `UseMethod()` dispatch |
| **S4** | Bioconductor, formal interfaces | Slots, validity, multiple dispatch |
| **R7** | Greenfield projects | Modern S3/S4 successor, properties |
| **R6** | Mutable state (caching, connections) | Reference semantics, `$new()` |

Read `references/class-systems-guide.md` for constructors, methods, and
decision tree for each system.

---

## Compiled Code with Rcpp

```r
usethis::use_rcpp()       # Sets up src/, Makevars, roxygen tags
usethis::use_rcpp_armadillo()  # For linear algebra (RcppArmadillo)
```

After creating a `.cpp` file in `src/`:

```r
devtools::document()      # Generates RcppExports.R and RcppExports.cpp
devtools::load_all()      # Compiles and loads
```

Tag the package-level documentation file with `@useDynLib mypkg, .registration = TRUE`.

---

## Vignettes

```r
usethis::use_vignette("getting-started")    # Rmarkdown vignette
usethis::use_vignette("advanced-usage")
```

Creates `vignettes/getting-started.Rmd` with correct YAML header. Build with
`devtools::build_vignettes()`. For quarto: create `.qmd` files in `vignettes/`
and add `VignetteEngine: quarto::html` to the YAML header.

**Tip:** Keep vignettes focused. One topic per vignette. Use `@seealso` in
function docs to link to relevant vignettes.

---

## pkgdown Site

```r
usethis::use_pkgdown()
pkgdown::build_site()
```

Customize `_pkgdown.yml` with `reference:` sections (group by topic),
`articles:` for vignettes, and `navbar:` for navigation. Use Bootstrap 5
(`template: bootstrap: 5`). Deploy via GitHub Actions (see CI/CD section).

---

## CRAN Submission

**Pre-submission checklist:**

```r
devtools::check(cran = TRUE)          # Must be 0 errors, 0 warnings
rhub::check_for_cran()                # Test on multiple platforms
urlchecker::url_check()               # Validate all URLs
spelling::spell_check_package()       # Catch typos
```

Prepare `cran-comments.md` at package root documenting test environments and
R CMD check results. Update `NEWS.md` with user-facing changes.

```r
devtools::submit_cran()               # Or submit via web form
```

Read `references/cran-submission-checklist.md` for the full step-by-step guide,
common rejection reasons, and resubmission protocol.

---

## CI/CD with GitHub Actions

```r
usethis::use_github_action("check-standard")    # R CMD check on 3 OSes
usethis::use_github_action("test-coverage")     # covr + codecov
usethis::use_github_action("pkgdown")           # Build and deploy site
usethis::use_github_action("lint")              # lintr checks
```

These create `.github/workflows/*.yaml` files. The `check-standard` action
runs `R CMD check` on ubuntu, macOS, and Windows with current R and R-devel.

Add status badges:

```r
usethis::use_github_actions_badge("R-CMD-check")
```

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `@import pkg` instead of `@importFrom pkg fun` | Imports entire namespace; causes collisions with other packages | Use `@importFrom pkg fun` or `pkg::fun()` — never `@import` |
| Forgetting `devtools::document()` after roxygen changes | `NAMESPACE` and man pages are stale; exports don't update | Run `devtools::document()` after every roxygen edit |
| `library()` in package code | Attaches entire package to search path; violates CRAN policy | Use `pkg::fun()` or `@importFrom pkg fun` in `R/` files |
| Missing `@export` tag | Function exists but users cannot access it after `library(pkg)` | Add `@export` to roxygen block, then `devtools::document()` |
| Hardcoded file paths | Paths break on other machines and in `R CMD check` | Use `testthat::test_path()`, `system.file()`, or `fs::path_package()` |
| Forgetting `usethis::use_package("dep")` | Dependency not in `DESCRIPTION`; `R CMD check` fails with "not available" | Run `usethis::use_package()` for every new dependency |
| `Depends:` instead of `Imports:` | Forces package onto user's search path; pollutes namespace | Use `Imports:` for almost all deps; `Depends:` only for data packages or tight coupling |
| Scope creep | Claude adds features or refactors unrelated code during a focused fix | Fix only the identified issue; show minimal diff |

---

## Examples

- "Create a new R package called tidyweather for weather data wrangling."
- "Add a `fetch_forecast()` function with full roxygen2 docs and tests."
- "Get this package ready for CRAN submission."
- "Create a pkgdown site grouping functions by topic."
- "The rolling_mean() function is too slow in pure R, use C++ via Rcpp."
