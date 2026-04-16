# DESCRIPTION Field Reference

Complete reference for every field in `DESCRIPTION`, with CRAN-acceptable
values, common mistakes, and tidyverse/`usethis` conventions.

---

## Required Fields

### Package

The package name. Must match regex `[A-Za-z][A-Za-z0-9.]+`, contain no
underscores, not end with a period, and be unique on CRAN.

```
Package: tidyweather
```

Check availability before settling on a name:

```r
available::available("tidyweather")   # Checks CRAN, Bioconductor, GitHub, urban dictionary
```

### Title

One line, title case, no trailing period, no "R package for" prefix.

```
Title: Tidy Access to Weather Forecast APIs
```

**CRAN rejects:** `"A Package to..."`, `"Tools for..."` followed by period.

### Version

Semantic versioning `MAJOR.MINOR.PATCH` for releases; append `.9000` for
development. Use `usethis::use_version()` to bump.

```
Version: 1.2.0
Version: 1.2.0.9000   # dev
```

### Description

One or more complete sentences. Must end with a period. Avoid repeating
the title verbatim. Reference package names in single quotes.

```
Description: Provides a tidy interface to the 'OpenWeatherMap' API. Supports
    current conditions, hourly and daily forecasts, and historical data.
    Results are returned as tibbles with ISO 8601 timestamps.
```

### License

Use a standard abbreviation, not custom text. For most packages:

```
License: MIT + file LICENSE
License: GPL (>= 3)
License: Apache License (>= 2)
License: CC0                 # Data packages
```

Create the `LICENSE` file with `usethis::use_mit_license()` or similar —
never edit it by hand.

### Authors@R

Always use `Authors@R` with `person()` calls — never the legacy `Author:`
and `Maintainer:` fields.

```
Authors@R: c(
    person("Jane", "Doe", email = "jane@example.com",
           role = c("aut", "cre"),
           comment = c(ORCID = "0000-0001-2345-6789")),
    person("John", "Smith", role = "ctb"),
    person("Acme Corp", role = c("cph", "fnd"))
)
```

**Role codes:**

| Code | Meaning |
|------|---------|
| `aut` | Author (major contributor) |
| `cre` | Creator (maintainer, exactly one, receives CRAN email) |
| `ctb` | Contributor (minor contributions) |
| `cph` | Copyright holder (company, university, etc.) |
| `fnd` | Funder |
| `rev` | Reviewer |
| `ths` | Thesis advisor |

Exactly one `cre` is required. ORCID is optional but encouraged.

---

## Dependency Fields

### Depends

**Use sparingly.** `Depends:` attaches the package to the user's search
path, polluting their namespace. Reserve for:

- Minimum R version: `Depends: R (>= 4.1.0)`
- Packages that fundamentally can't be imported (rare)

```
Depends:
    R (>= 4.1.0)
```

### Imports

The default for almost every dependency. Makes functions available for
use inside your package via `pkg::fun()` or `@importFrom`.

```
Imports:
    cli,
    dplyr (>= 1.1.0),
    rlang (>= 1.1.0),
    tibble
```

**Version constraints:** Only specify `(>= x.y.z)` when you actually use
a feature introduced in that version. Over-specifying slows dependency
resolution.

Use `usethis::use_package("pkg")` to add deps — handles alphabetization
and formatting.

### Suggests

Optional dependencies used only in tests, vignettes, or `@examples`
wrapped in `if (requireNamespace("pkg"))`.

```
Suggests:
    covr,
    knitr,
    rmarkdown,
    testthat (>= 3.0.0),
    withr
```

**Guard suggested packages in function code:**

```r
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  cli::cli_abort("Install {.pkg ggplot2} to use this function.")
}
```

### Enhances

Very rare. Declares that your package enhances another's functionality.
Almost always you want `Imports` or `Suggests` instead.

### LinkingTo

For compiled code dependencies (Rcpp, cpp11, etc.). Populated automatically
by `usethis::use_rcpp()`.

```
LinkingTo:
    cpp11
```

---

## Metadata Fields

### URL and BugReports

Both strongly recommended. URLs comma-separated.

```
URL: https://github.com/user/mypkg, https://user.github.io/mypkg/
BugReports: https://github.com/user/mypkg/issues
```

Set via `usethis::use_github_links()` after `use_github()`.

### SystemRequirements

For non-R system libraries (only when needed). Free-form text — CRAN
reviewers read this.

```
SystemRequirements: GNU make, libssl-dev, Java (>= 8)
```

### Encoding

Always `UTF-8`. Set automatically by `usethis`.

```
Encoding: UTF-8
```

### Language

Set only if the documentation is not in English.

```
Language: en-US
```

### Config/testthat/edition

Opt into testthat 3rd edition (strict warnings, snapshot tests). Set by
`usethis::use_testthat(3)`.

```
Config/testthat/edition: 3
```

### Config/Needs/website

Tells CI which packages are needed to build the pkgdown site without
being runtime deps.

```
Config/Needs/website: pkgdown, tidyverse/tidytemplate
```

### Roxygen

Controls roxygen2 behaviour. Set by `usethis::use_roxygen_md()`.

```
Roxygen: list(markdown = TRUE, load = "pkgload")
RoxygenNote: 7.3.2
```

### LazyData

For packages shipping data in `data/`. Default should be `true`.

```
LazyData: true
```

---

## `Depends` vs `Imports` vs `Suggests` Decision Tree

```
Does the user need the package attached? (e.g., base pipe |>, inherited infix)
  YES -> Depends (rare, only R version in most cases)
  NO  -> Is it needed for core functionality?
    YES -> Imports
    NO  -> Is it needed only for tests/vignettes/optional features?
      YES -> Suggests (guard with requireNamespace())
      NO  -> Remove it
```

---

## Common CRAN Rejections Tied to DESCRIPTION

| Issue | Fix |
|-------|-----|
| Package name in Title not single-quoted | Quote: `'dplyr'`, `'ggplot2'` |
| Description too short or vague | Write 2-3 complete sentences explaining what it does |
| Missing ORCID for `cre` | Add ORCID via `comment = c(ORCID = "...")` |
| No `URL` / `BugReports` | Add both, pointing at GitHub repo |
| Version suffix `.9000` at submission | Bump to release version first |
| Redundant `LazyData: true` without `data/` | Remove if no data files |
| Over-specified dep versions | Relax `(>= x.y.z)` unless actually needed |
| `Depends:` on non-R packages | Move to `Imports:` |
| Missing license file | `usethis::use_mit_license()` etc. |

---

## Minimal Clean DESCRIPTION Template

```
Package: tidyweather
Title: Tidy Access to Weather Forecast APIs
Version: 0.1.0
Authors@R:
    person("Jane", "Doe", email = "jane@example.com",
           role = c("aut", "cre"),
           comment = c(ORCID = "0000-0001-2345-6789"))
Description: Provides a tidy interface to the 'OpenWeatherMap' API. Supports
    current conditions, hourly and daily forecasts, and historical data.
    Results are returned as tibbles with ISO 8601 timestamps.
License: MIT + file LICENSE
URL: https://github.com/janedoe/tidyweather
BugReports: https://github.com/janedoe/tidyweather/issues
Encoding: UTF-8
Depends:
    R (>= 4.1.0)
Imports:
    cli,
    httr2,
    rlang,
    tibble
Suggests:
    knitr,
    rmarkdown,
    testthat (>= 3.0.0),
    withr
Config/testthat/edition: 3
Roxygen: list(markdown = TRUE)
RoxygenNote: 7.3.2
VignetteBuilder: knitr
```
