# roxygen2 Tag Reference

Complete reference for roxygen2 tags with examples. Markdown mode enabled
via `Roxygen: list(markdown = TRUE)` in `DESCRIPTION`.

**Sources:**
- roxygen2 documentation — <https://roxygen2.r-lib.org/>
- `vignette("rd", package = "roxygen2")` — Rd-generation tag reference
- `vignette("rd-formatting", package = "roxygen2")` — markdown mode
- `vignette("namespace", package = "roxygen2")` — NAMESPACE directives
- R Packages 2e ch. 16 "Function documentation" — <https://r-pkgs.org/man.html>
- Writing R Extensions §2 (Rd format) — <https://cran.r-project.org/doc/manuals/r-release/R-exts.html#Writing-R-documentation-files>

---

## Core Function Tags

### `@param name description`

Document each function argument. One `@param` per argument. Wrap on column
80; continuation lines indented by two spaces.

```r
#' @param data A data frame or tibble.
#' @param weights Numeric vector of sampling weights, one per row of `data`.
#'   If `NULL` (default), each row receives equal weight.
```

**Tidy eval types:** Use angle-bracket syntax with link for data-masking
and tidy-select arguments.

```r
#' @param col <[`data-masking`][rlang::args_data_masking]> Column to filter.
#' @param cols <[`tidy-select`][dplyr::dplyr_tidy_select]> Columns to summarise.
```

### `@returns value` (preferred) or `@return value`

Document what the function returns. Required for every exported function.
CRAN requires `\value` in Rd, which either tag produces.

```r
#' @returns A tibble with columns:
#'   * `date`: Date of observation.
#'   * `temp`: Numeric, temperature in Celsius.
#'   * `source`: Character, API provider.
```

### `@examples`

Required for every exported function. Examples must run without error
during `R CMD check`.

```r
#' @examples
#' # Basic usage
#' df <- data.frame(x = 1:10, y = rnorm(10))
#' summarise_data(df)
#'
#' \donttest{
#' # Slow example (> 5 seconds)
#' large_df <- simulate_data(n = 1e6)
#' summarise_data(large_df)
#' }
#'
#' \dontrun{
#' # Only when absolutely necessary (network, credentials, interactive)
#' fetch_live_data(token = Sys.getenv("API_TOKEN"))
#' }
```

**`\donttest{}` vs `\dontrun{}`:**

| Marker | When to use |
|--------|-------------|
| `\donttest{}` | Example works but takes > 5s. Skipped by CRAN but still run by `devtools::check()`. |
| `\dontrun{}` | Example truly cannot run (auth, network, interactive). Never executed. |

CRAN strongly prefers `\donttest{}`. Use `\dontrun{}` only as last resort.

### `@export`

Adds the function to `NAMESPACE`. Without it, function is internal.

```r
#' @export
my_public_fn <- function() ...
```

### `@title` and `@description` (implicit)

The first sentence of a roxygen block is the title; subsequent paragraph(s)
are the description. Both are optional explicit forms:

```r
#' @title Compute weighted summary
#' @description
#' Calculates mean and standard deviation of a column,
#' optionally weighted by a second column.
```

Prefer implicit form (just write them as the first line and paragraph).

### `@details`

Longer explanation below parameters. Use for algorithm details, gotchas,
or behaviour notes.

```r
#' @details
#' Weights are normalised to sum to one before computation. `NA` values
#' in either `value_col` or `weight_col` are removed pairwise.
```

---

## Cross-Reference Tags

### `@family group-name`

Groups related functions. roxygen2 auto-generates "See also" links between
all functions sharing a family.

```r
#' @family summary functions
```

### `@seealso`

Manual references — useful for pointing to external help or unrelated
functions.

```r
#' @seealso [stats::sd()], [weighted_mean()], <https://example.com/docs>
```

### `@inheritParams other_fn`

Inherits `@param` documentation from another function. Great for avoiding
duplication when arguments match.

```r
#' @inheritParams summarise_data
#' @param extra_arg New argument specific to this function.
plot_summary <- function(data, value_col, extra_arg = TRUE) ...
```

### `@inherit other_fn` (sections)

Inherits specific sections from another function.

```r
#' @inherit summarise_data return
#' @inherit summarise_data examples
```

### `@describeIn name description`

Documents a method or variant under another topic. Generates a bulleted
list.

```r
#' @describeIn weighted_summary Specialised version for time series.
weighted_summary_ts <- function(data, time_col, value_col) ...
```

### `@rdname topic`

Forces multiple functions into one Rd file.

```r
#' @rdname arithmetic
#' @export
add <- function(x, y) x + y

#' @rdname arithmetic
#' @export
subtract <- function(x, y) x - y
```

---

## Import Tags

### `@importFrom pkg fn1 fn2`

Selective imports from another package. Preferred over `@import`.

```r
#' @importFrom rlang .data abort warn
#' @importFrom stats setNames
```

### `@import pkg`

**Avoid.** Imports entire package namespace, causing collisions. Only
acceptable if you use dozens of functions from one package.

### `@useDynLib pkg, .registration = TRUE`

For packages with compiled code. Place on package-level doc (usually
`R/pkg-package.R`). `usethis::use_rcpp()` handles this.

```r
#' @useDynLib mypkg, .registration = TRUE
#' @importFrom Rcpp sourceCpp
NULL
```

---

## S3 / S4 / S7 Tags

### `@method generic class`

Usually unnecessary in modern roxygen2 (inferred from function name
`generic.class`). Only needed if the class has dots in its name.

```r
#' @method print data.frame.custom
print.data.frame.custom <- function(x, ...) ...
```

### `@export` on S3 methods

You export the generic and the class; methods are registered via S3method
directives in NAMESPACE (auto-generated).

```r
#' @export
print.temperature <- function(x, ...) { ... }
```

### `@exportMethod name` (S4)

Explicitly export an S4 method.

```r
#' @exportMethod show
setMethod("show", "GenomicRange", function(object) { ... })
```

### `@exportClass name` (S4)

Export an S4 class definition for use by other packages.

```r
#' @exportClass GenomicRange
setClass("GenomicRange", ...)
```

### `@include file.R`

Controls collation order — needed when one file depends on objects
defined in another (e.g., S4 class in file A referenced in file B).
roxygen2 populates the `Collate:` field in DESCRIPTION.

```r
#' @include classes.R
setMethod("width", "GenomicRange", function(x) ...)
```

---

## Package-Level Documentation

Create `R/mypkg-package.R` (generated by `usethis::use_package_doc()`):

```r
#' @keywords internal
"_PACKAGE"

## usethis namespace: start
## usethis namespace: end
NULL
```

This produces `?mypkg` help landing page with package metadata, plus
a conventional location for `@importFrom` directives that apply globally.

---

## Data Documentation

Document datasets in `R/data.R`:

```r
#' Daily weather observations for major cities
#'
#' A tibble containing daily high and low temperatures for 20 major cities
#' between 2020-01-01 and 2023-12-31.
#'
#' @format A tibble with 29,200 rows and 4 variables:
#' \describe{
#'   \item{date}{Date of observation.}
#'   \item{city}{Character, city name.}
#'   \item{temp_high}{Numeric, daily high in Celsius.}
#'   \item{temp_low}{Numeric, daily low in Celsius.}
#' }
#' @source <https://example.com/weather-api>
"weather_daily"
```

---

## Re-Export

Re-export a function from a dependency so your users can call it without
attaching the other package. Common for `tibble()`, `as_tibble()`, and
similar helpers.

```r
#' @importFrom tibble tibble
#' @export
tibble::tibble
```

The base pipe `|>` is a language operator (R >= 4.1.0) and needs no
re-export.

---

## Other Useful Tags

| Tag | Purpose |
|-----|---------|
| `@keywords internal` | Hide from pkgdown reference index (use for helpers) |
| `@noRd` | Skip Rd generation entirely (for internal functions) |
| `@section Custom Heading:` | Add arbitrary section to the help page |
| `@md` | Force markdown on single block (rarely needed with global markdown) |
| `@concept keyword` | Tag for search/discovery in help system |
| `@aliases alias1 alias2` | Additional help topics pointing to this page |

### `@keywords internal` vs `@noRd`

```r
# @keywords internal: generates .Rd, callable by package authors
#' @keywords internal
helper_fn <- function() ...

# @noRd: no .Rd file at all, purely a comment block
#' @noRd
really_internal <- function() ...
```

---

## Style Conventions

- First line is the title — capitalised, no trailing period
- Blank `#'` line separates title / description / details / tags
- Parameters documented in function-argument order
- Backticks for `code`, brackets `[fn()]` for auto-linked functions
- `<https://...>` for explicit URLs
- Keep lines ≤ 80 characters
- Always run `devtools::document()` after editing roxygen2
