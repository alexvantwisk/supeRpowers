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

## Common R Pitfalls

### Factor Surprises

**Symptom:** Unexpected levels, wrong coercion, "invalid factor level" warnings.

```r
# Factor-to-numeric trap: as.numeric(factor) gives codes, not values
x <- factor(c("10", "20", "30"))
as.numeric(x)               # Returns 1, 2, 3 (WRONG)
as.numeric(as.character(x))  # Returns 10, 20, 30 (CORRECT)

# Dropped levels after subsetting
x <- factor(c("a", "b", "c"))
x[x != "c"]              # Still has level "c"
droplevels(x[x != "c"])  # Clean
```

### NSE Scoping

**Symptom:** "object not found" inside dplyr verbs, or wrong variable captured.

```r
# WRONG: bare variable from outer scope not found
col <- "mpg"
mtcars |> filter(col > 20)  # Looks for column named "col"

# CORRECT: use .data pronoun for string column names
mtcars |> filter(.data[[col]] > 20)

# CORRECT: use embrace for function arguments
my_filter <- function(data, var) {
  data |> filter({{ var }} > 20)
}
```

### Silent Vector Recycling

**Symptom:** No error, but wrong results. R silently recycles shorter vectors.

```r
x <- 1:6
y <- c(1, 2)    # Length 2 recycles to match length 6
x + y            # c(2, 4, 4, 6, 6, 8) -- probably not intended

# Guard: check lengths explicitly
stopifnot(length(x) == length(y))
```

### Copy-on-Modify Memory Spikes

**Symptom:** Unexpected memory growth when modifying large objects.

R copies on modify. Modifying a column of a large data frame triggers a full
copy. Fix: build data frames in one step, or use `data.table` for in-place
mutation.

### NULL Propagation

**Symptom:** No error, but downstream code breaks with cryptic messages.

```r
my_list <- list(a = 1, b = 2)
my_list$c          # Returns NULL silently (no error!)
my_list$c + 1      # NULL -- still no error in some contexts

# Guard: use [[ ]] with explicit checks
value <- my_list[["c"]]
if (is.null(value)) {
  cli::cli_abort("Expected element {.field c} not found in list.")
}
```

### Floating Point Comparison

**Symptom:** Equality checks fail on values that "should" be equal.

```r
0.1 + 0.2 == 0.3          # FALSE

# Fix: use tolerance-aware comparison
dplyr::near(0.1 + 0.2, 0.3)  # TRUE
all.equal(0.1 + 0.2, 0.3)     # TRUE (returns string message on failure)
```

### Encoding Issues

**Symptom:** Garbled text, especially on Windows; `nchar()` returns unexpected values.

Diagnose with `Encoding(x)` and `validUTF8(x)`. Fix with `enc2utf8(x)` or
read with explicit encoding:
`readr::read_csv("file.csv", locale = readr::locale(encoding = "UTF-8"))`.

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
