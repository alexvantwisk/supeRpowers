---
name: r-debugging
description: >
  Use when diagnosing bugs, errors, or unexpected behavior in R code. Provides
  a systematic reproduce-isolate-diagnose-fix-test workflow covering browser(),
  traceback(), debug(), condition handling, and common R pitfalls for both
  interactive scripts and package code.
  Triggers: debug, error, bug, traceback, browser, breakpoint, unexpected
  behavior, stack trace, warning, object not found, wrong results.
  Do NOT use for performance profiling and optimization — use r-performance instead.
  Do NOT use for writing tests — use r-tdd instead.
  For a guided debugging workflow, invoke /r-cmd-debug instead.
---

# R Debugging

Systematic workflow for diagnosing and fixing bugs in R code:
**REPRODUCE -> ISOLATE -> DIAGNOSE -> FIX -> TEST**.

Ask upfront: *Is this interactive script code or package code?* The strategy
differs -- package code has formal test infrastructure and namespacing;
interactive scripts need ad-hoc reprex and manual verification.

---

## Step 1 -- Reproduce

Create a minimal, self-contained example that triggers the bug.

```r
# Use reprex for shareable reproduction cases
reprex::reprex({
  library(dplyr)
  tibble(x = c(1, NA, 3)) |>
    mutate(y = x + 1)
})
```

**Checklist:**
- Strip to the smallest data and code that still fails
- Pin package versions with `sessionInfo()` or `renv::snapshot()`
- Confirm the error is deterministic (run 3x)

---

## Step 2 -- Isolate

Narrow down where the failure occurs.

**Binary search through a pipeline:** Comment out the bottom half of a pipe
chain. If the error disappears, the bug is in the removed half. Recurse.

**Insert `browser()` at suspect locations:**

```r
transform_data <- function(data) {
  data <- data |>
    filter(!is.na(value))
  browser()
  # Execution pauses here -- inspect `data` in the console
  data |>
    summarise(total = sum(value))
}
```

Inside `browser()`: `n` (next), `s` (step into), `c` (continue), `Q` (quit),
`ls()` (list objects), `str(obj)` (inspect structure).

---

## Step 3 -- Diagnose

Use the right tool for the situation.

### Call Stack Inspection

```r
# After an error occurs:
traceback()

# For rlang-based errors (tidyverse), get a cleaner tree:
rlang::last_trace()
```

Read the stack **bottom-up**: the deepest frame is where the error was thrown;
work upward to find your code's entry point.

### Interactive Breakpoints

Quick reference: `debug(fn)` / `debugonce(fn)` to step through a function,
`trace(fn, tracer = browser, at = 4)` to inject a breakpoint at a specific line,
`options(error = recover)` to drop into browser on any error.

Read `references/debugging-tools.md` for the full breakpoint command reference,
browser() commands table, and package-specific debugging patterns.

---

## Step 4 -- Fix

Apply the fix and verify against the original reprex.

1. Make the minimal change that addresses the root cause
2. Re-run the exact reprex from Step 1 -- error must be gone
3. Check for side effects: run `devtools::check()` for packages, or re-run
   the full script for interactive code

---

## Step 5 -- Test (Regression)

Write a test that would have caught this bug. Future changes must not
re-introduce it.

```r
test_that("transform_data handles NA values without error", {
  input <- tibble::tibble(value = c(1, NA, 3))
  result <- transform_data(input)
  expect_equal(result$total, 4)
})
```

For packages: place in `tests/testthat/test-<relevant-file>.R`.
For scripts: create a lightweight test file or add to an existing test suite.

---

## Gotchas

Top traps to check first:

- **Factor-to-numeric:** `as.numeric(factor_var)` returns codes, not values — use `as.numeric(as.character(x))`
- **NSE scoping:** `filter(col > 20)` looks for column, not variable — use `.data[[col]]` for strings, `{{ var }}` for function args
- **Vector recycling:** `x == c("A", "B")` does element-wise recycling — use `%in%` for set membership
- **NULL propagation:** `list$missing_element` returns `NULL` silently — use `[["key"]]` with `is.null()` check
- **Floating point:** `0.1 + 0.2 == 0.3` is `FALSE` — use `dplyr::near()` or `all.equal()`

Read `references/debugging-tools.md` for the full gotchas table with detailed explanations, performance debugging tools (profvis, bench::mark), and common performance fixes.

---

## Dispatch

When the root cause is a code quality issue (anti-pattern, poor style, NSE
misuse) rather than a logic bug, hand off to the **r-code-reviewer** agent
for a focused review of the problematic code.

---

## Examples

### Happy Path: Function returns wrong result -- isolate with browser()

**Prompt:** "My `calc_growth()` function returns NA for some groups. Help me debug it."

```r
# Input — buggy function
calc_growth <- function(data) {
  data |>
    arrange(date) |>
    mutate(growth = (value - lag(value)) / lag(value) * 100, .by = group)
}

test_data <- tibble(
  group = c("A", "A", "B"),
  date  = as.Date(c("2024-01-01", "2024-02-01", "2024-01-01")),
  value = c(100, 120, 50)
)
calc_growth(test_data)
#> Group B has only 1 row -> lag() returns NA -> growth is NA

# Diagnose — insert browser() to inspect
calc_growth <- function(data) {
  data <- data |> arrange(group, date)
  browser()  # inspect: data |> count(group) reveals single-row groups
  data |> mutate(growth = (value - lag(value)) / lag(value) * 100, .by = group)
}

# Fix — guard against single-row groups
calc_growth <- function(data) {
  data |>
    arrange(group, date) |>
    mutate(
      growth = if (n() > 1) (value - lag(value)) / lag(value) * 100 else NA_real_,
      .by = group
    )
}
```

### Edge Case: Vector recycling producing wrong results without error

**Prompt:** "My filter seems to work but returns wrong rows. No error at all."

```r
# Input — subtle recycling bug
df <- tibble(id = 1:6, status = c("A", "B", "C", "A", "B", "C"))

# BAD: intended to keep A and B, but c("A", "B") recycles to match 6 rows
# R compares element-wise: row1=="A", row2=="B", row3=="A", row4=="B"...
df |> filter(status == c("A", "B"))
#> Returns 4 rows — wrong! Recycling matched positions, not values

# GOOD: use %in% for set membership
df |> filter(status %in% c("A", "B"))
#> Returns 4 rows — the correct 4 (all A and B rows)

# Defensive: always use %in% for multi-value comparisons
# If you must use ==, guard with stopifnot(length(x) == length(y))
```

**More example prompts:**
- "My dplyr pipeline throws 'object not found' for a column I know exists"
- "This function returns NULL instead of a data frame, but only sometimes"
- "My R script runs fine interactively but fails in `Rscript --vanilla`"
- "I'm getting different results on macOS vs Windows for string operations"
- "This summarise call is taking 30 seconds on 100k rows, help me profile it"
