# R Conventions

These conventions apply to ALL R code generated, reviewed, or discussed in this project.

## Pipe Operator

ALWAYS use the base pipe `|>`. NEVER use magrittr `%>%`.

```r
# CORRECT
mtcars |>
  filter(cyl == 6) |>
  summarise(mean_mpg = mean(mpg))

# WRONG
mtcars %>%
  filter(cyl == 6) %>%
  summarise(mean_mpg = mean(mpg))
```

If existing code uses `%>%`, migrate it to `|>` when touching that code.

Note: `|>` requires R >= 4.1.0. The base pipe does not support the `.` placeholder — use anonymous functions instead: `x |> (\(d) lm(mpg ~ wt, data = d))()`.

## Paradigm

**Tidyverse-first.** Lead with dplyr, tidyr, purrr, ggplot2, readr, stringr, forcats, lubridate.

Mention base R or data.table alternatives when they are genuinely better:
- **data.table:** Large datasets (>1M rows), performance-critical inner loops, memory-constrained environments.
- **Base R:** Zero-dependency packages, simple one-liners where tidyverse is overkill.

## Style

- **Formatter:** `styler::tidyverse_style()`
- **Linter:** `lintr` with default tidyverse rules
- **Naming:** `snake_case` for functions, variables, and file names
- **Assignment:** `<-` for assignment, never `=`
- **Strings:** Double quotes `"` always (single quotes only inside double-quoted strings)
- **Line length:** 80 characters soft limit, 120 hard limit
- **Spacing:** Space after commas, around `<-`, around infix operators

## Environment Management

- **renv** for all projects. Check for `renv.lock` at project root.
- For new projects: suggest `renv::init()`.
- Before adding packages: `renv::install("pkg")` then `renv::snapshot()`.
- To restore: `renv::restore()`.

## R Version

Target R >= 4.1.0 (base pipe `|>` support). Flag code that requires features from newer R versions (e.g., R 4.2.0 `_` placeholder in pipes — avoid this, use anonymous functions instead).

## Package Development Toolchain

The canonical modern stack:
- `usethis` — project setup, CI, licensing, boilerplate
- `devtools` — development workflow (`load_all()`, `test()`, `check()`, `document()`)
- `roxygen2` — documentation with markdown support enabled (`use_roxygen_md()`)
- `testthat` 3rd edition — testing (`use_testthat(3)`)
- `pkgdown` — documentation sites
- `styler` — code formatting
- `lintr` — static analysis

## Documentation

- roxygen2 with markdown enabled (`Roxygen: list(markdown = TRUE)` in DESCRIPTION)
- `@examples` mandatory for all exported functions
- `@param` for every parameter — no undocumented args
- `@returns` for every function (not `@return`)
- Use `@family` to group related functions
- For tidy eval: use `@inheritParams rlang::args_data_masking` or document with `<data-masking>` / `<tidy-select>` tags

## Error Handling (in packages)

Use the cli package for user-facing messages:
```r
# Errors
cli::cli_abort("Column {.field {col}} not found in {.arg data}.")

# Warnings
cli::cli_warn("NAs introduced by coercion.")

# Information
cli::cli_inform("Processing {.val {n}} rows.")
```

For structured error handling: `rlang::try_fetch()` over `tryCatch()`.

For condition classes: use `rlang::abort(class = "pkg_error_type")` for programmatic catching.

## Tidy Evaluation

- **Embrace:** `{{ }}` for passing column names through functions
- **Data pronoun:** `.data$col` to refer to columns, `.env$var` for environment variables
- **Injection:** `!!` and `!!!` only when `{{ }}` is insufficient
- **Documentation:** Always document whether a function uses data-masking or tidy-select

```r
# CORRECT — embrace pattern
my_summary <- function(data, group_col, value_col) {
  data |>
    group_by({{ group_col }}) |>
    summarise(mean_val = mean({{ value_col }}, na.rm = TRUE))
}

# CORRECT — .data pronoun for string column names
my_filter <- function(data, col_name, threshold) {
  data |>
    filter(.data[[col_name]] > .env$threshold)
}
```

## File Organization

- One primary function per file in `R/`, named to match: `my_function()` lives in `R/my-function.R`
- Utility/helper functions can share a file: `R/utils.R`, `R/utils-validation.R`
- Keep files under 400 lines. Extract if growing beyond that.

## Quick Reference — Anti-Patterns

| Never | Always |
|-------|--------|
| `sapply()` | `vapply()` or `purrr::map_*()` — type-safe |
| `ifelse()` | `dplyr::if_else()` — preserves type, strict |
| `T` / `F` | `TRUE` / `FALSE` — T and F can be overwritten |
| `1:length(x)` | `seq_along(x)` — safe when `x` is empty |
| `library()` in functions | `pkg::fn()` or `@importFrom` — explicit deps |
| `setwd()` / `rm(list=ls())` | `here::here()` / restart R session |
| Modify input in place | Return new object — immutability preferred |

## Environment-Aware Coding (with MCP)

When an R session is available via btw/mcptools, enhance — don't replace — these conventions:

- **Before writing:** inspect data frames (`btw_tool_env_describe_data_frame`), check installed packages, read help pages instead of guessing from training data
- **For non-trivial code** (transformations, model fits, table generation): run it via btw, check errors/warnings, verify output dimensions/structure, fix before presenting
- **When recommending packages:** check `btw_tool_sessioninfo_is_package_installed` first
- **Skip verification** for: one-liners, scaffolding, config files, code that needs data not in the session

All conventions work without MCP — MCP makes them more precise.

## Function Design

- Prefer pure functions: same inputs → same outputs, no side effects
- Use `withr::local_*()` / `withr::defer()` for temporary side effects (tempfiles, options, env vars)
- Return values explicitly; use `invisible()` for side-effect functions
- Keep functions under 50 lines; extract helpers when growing beyond that
