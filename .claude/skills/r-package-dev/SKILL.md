---
name: r-package-dev
description: >
  Use when creating, developing, documenting, or submitting R packages. Covers
  usethis, devtools, roxygen2, pkgdown, CRAN submission, and CI/CD.
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

Customize `_pkgdown.yml`:

```yaml
url: https://username.github.io/mypkg/

template:
  bootstrap: 5

reference:
  - title: Core Functions
    contents:
      - weighted_summary
      - fit_model
  - title: Utilities
    contents:
      - starts_with("validate_")

articles:
  - title: Getting Started
    contents:
      - getting-started
  - title: Advanced
    contents:
      - advanced-usage

navbar:
  structure:
    left:  [intro, reference, articles, news]
```

Deploy automatically via GitHub Actions (see CI/CD section).

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

## Examples

### 1. Bootstrap a new package from scratch
**Prompt:** "Create a new R package called tidyweather for weather data wrangling."

```r
usethis::create_package("~/projects/tidyweather")
usethis::use_testthat(3)
usethis::use_pipe(type = "base")
usethis::use_roxygen_md()
usethis::use_mit_license()
usethis::use_git()
usethis::use_github()
usethis::use_readme_rmd()
usethis::use_github_action("check-standard")
```

### 2. Add an exported function with full documentation
**Prompt:** "Add a `fetch_forecast()` function that calls a weather API."

Write test first (RED), implement in `R/fetch-forecast.R` with full roxygen2
block (`@param`, `@returns`, `@examples`, `@family`), run `devtools::document()`
then `devtools::check()`.

### 3. Prepare for CRAN submission
**Prompt:** "Get this package ready for CRAN."

Run `devtools::check(cran = TRUE)`, fix all warnings, run `urlchecker::url_check()`,
`spelling::spell_check_package()`, update `NEWS.md`, write `cran-comments.md`,
then `devtools::submit_cran()`.

### 4. Set up pkgdown with custom reference organization
**Prompt:** "Create a pkgdown site grouping functions by topic."

Run `usethis::use_pkgdown()`, configure `_pkgdown.yml` with `reference:` sections,
`pkgdown::build_site()`, then `usethis::use_github_action("pkgdown")` for deploy.

### 5. Add Rcpp for a performance-critical function
**Prompt:** "The rolling_mean() function is too slow in pure R, use C++ via Rcpp."

Run `usethis::use_rcpp()`, write `.cpp` in `src/`, `devtools::document()` to
generate exports, test with `devtools::test()`, benchmark with `bench::mark()`.
