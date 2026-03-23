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

```r
# Debug every call to a function
debug(my_function)
my_function(data)
undebug(my_function)

# Debug only the next call
debugonce(my_function)

# Insert browser at a specific line inside a function
trace(my_function, tracer = browser, at = 4)
untrace(my_function)
```

### Automatic Recovery on Error

```r
# Drop into browser on ANY error (great for interactive exploration)
options(error = recover)

# Reset to default behavior
options(error = NULL)
```

With `recover`, R presents a numbered list of frames after an error. Select a
frame number to inspect its environment.

### Package Code Specifics

For debugging inside a package under development:

```r
devtools::load_all()
debugonce(pkg::internal_function)
# Or set options(error = recover) then trigger the bug
```

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

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `as.numeric(factor_var)` | Returns internal codes (1, 2, 3), not actual values | Use `as.numeric(as.character(x))` or `readr::parse_number()` |
| NSE scoping: bare string var in `filter()` | `filter(col > 20)` looks for column named `col`, not the variable's value | Use `.data[[col]]` for strings, `{{ var }}` for function arguments |
| Silent vector recycling | R recycles shorter vectors with no error, producing wrong results | Guard with `stopifnot(length(x) == length(y))` |
| Copy-on-modify memory spikes | Modifying one column copies the entire data frame | Build data frames in one step, or use `data.table` for in-place mutation |
| `list$missing_element` returns `NULL` | No error on missing list element; `NULL` propagates silently | Use `[["key"]]` with explicit `is.null()` check |
| `0.1 + 0.2 == 0.3` is `FALSE` | Floating point representation; equality check fails | Use `dplyr::near()` or `all.equal()` with tolerance |
| Encoding issues on Windows | Garbled text, unexpected `nchar()` values | Diagnose with `Encoding(x)`; fix with `enc2utf8()` or explicit locale in `read_csv()` |
| Scope creep | Claude refactors surrounding code when asked to fix one bug | Fix only the identified bug; show minimal diff |

---

## Performance Debugging

When the bug is "it's too slow" or "it uses too much memory."

```r
system.time({ result <- slow_function(data) })                # Quick timing
bench::mark(base = vapply(x, f, numeric(1)), purrr = map_dbl(x, f))  # Compare
profvis::profvis({ slow_function(data) })                     # Flame graph
lobstr::obj_size(large_object)                                # Memory check
```

**Common fixes:** vectorize loops, `vapply()` over `sapply()`, pre-allocate
outputs, `data.table`/`collapse` for >1M rows.

---

## Dispatch

When the root cause is a code quality issue (anti-pattern, poor style, NSE
misuse) rather than a logic bug, hand off to the **r-code-reviewer** agent
for a focused review of the problematic code.

---

## Examples

- "My dplyr pipeline throws 'object not found' for a column I know exists"
- "This function returns NULL instead of a data frame, but only sometimes"
- "My R script runs fine interactively but fails in `Rscript --vanilla`"
- "I'm getting different results on macOS vs Windows for string operations"
- "This summarise call is taking 30 seconds on 100k rows, help me profile it"
