---
name: r-tdd
description: >
  Use when writing or running tests for R code, setting up testthat, or
  following TDD workflow in R packages or scripts. Provides expert guidance on
  the red-green-refactor cycle, testthat 3rd edition, snapshot tests, mocking,
  fixtures, test coverage, and test organization patterns.
  Triggers: test, testthat, TDD, test-driven, unit test, snapshot test, test
  coverage, expect_equal, test_that, mock, fixture.
  Do NOT use for R CMD check or package-level quality gates — use r-package-dev instead.
  Do NOT use for debugging existing code — use r-debugging instead.
---

# R Test-Driven Development

Write tests first, implement second. TDD for R packages using testthat 3rd edition.

## TDD Cycle

```
RED:      Write a failing test that defines desired behavior
GREEN:    Write minimal implementation to pass the test
REFACTOR: Improve code quality while keeping tests green
```

**Iron law:** Never write implementation before its test exists and fails.

**RED:** Create `tests/testthat/test-{feature}.R`, write `test_that()` block, run `devtools::test_active_file()` — MUST fail. If it passes, the test is wrong.

**GREEN:** Write minimal code in `R/{feature}.R`, run `devtools::test_active_file()` — MUST pass. Do NOT add logic beyond what the test requires.

**REFACTOR:** Clean up implementation, run `devtools::test()` — all tests MUST still pass, check coverage with `covr::package_coverage()` — target 80%+.

---

## Setting Up testthat 3e

```r
usethis::use_testthat(3)
```

Creates `tests/testthat/`, `tests/testthat.R`, sets `Config/testthat/edition: 3` in DESCRIPTION.

Edition 3 key changes: `expect_identical()` default, snapshot testing, `expect_error(class=)` preferred, warnings not suppressed, `context()` deprecated.

---

## Test File Conventions

| Source file | Test file |
|-------------|-----------|
| `R/fit-model.R` | `tests/testthat/test-fit-model.R` |
| `R/utils-validation.R` | `tests/testthat/test-utils-validation.R` |

Create with `usethis::use_test("fit-model")`.

| Special file | Purpose |
|------|---------|
| `tests/testthat/setup.R` | Runs before ALL tests — load packages, set options |
| `tests/testthat/helper.R` | Shared utility functions available to all tests |
| `tests/testthat/fixtures/` | Static test data (CSV, RDS, JSON) |

---

## Test Structure

### Standard Style

```r
test_that("fit_model returns a tibble with expected columns", {
  result <- fit_model(mtcars, response = "mpg", predictors = c("wt", "hp"))
  expect_s3_class(result, "tbl_df")
  expect_named(result, c("term", "estimate", "std_error", "p_value"))
  expect_true(nrow(result) > 0)
})
```

### BDD Style (describe/it)

```r
describe("validate_input", {
  it("accepts a valid data frame", {
    df <- tibble::tibble(x = 1:3, y = 4:6)
    expect_no_error(validate_input(df))
  })
  it("rejects NULL input", {
    expect_error(validate_input(NULL), class = "my_pkg_input_error")
  })
  it("rejects zero-row data frames", {
    expect_error(validate_input(tibble::tibble(x = numeric())), "at least one row")
  })
})
```

---

## Core Expectations

```r
# Value comparisons
expect_equal(actual, expected)          # Equal with tolerance (waldo)
expect_identical(actual, expected)      # Exactly identical (type + value)
expect_true(x > 0)                     # Logical TRUE
expect_false(is.null(result))          # Logical FALSE
expect_length(result, 5)               # Length check
expect_named(df, c("a", "b"))          # Names check

# Type and class
expect_type(x, "double")              # typeof() check
expect_s3_class(obj, "tbl_df")        # S3 class check

# Conditions (prefer class matching in 3e)
expect_error(fn(), class = "pkg_error_type")
expect_error(fn(), "column not found") # Message pattern
expect_warning(fn(), "NAs introduced")
expect_message(fn(), "Processing")
expect_no_error(fn())
expect_no_warning(fn())

# Output and side effects
expect_output(print(obj), "some output")
expect_invisible(fn())
```

---

## Snapshot Testing

```r
test_that("summary output is stable", {
  expect_snapshot(summary(model))
})
test_that("error formatting is stable", {
  expect_snapshot(validate_input(NULL), error = TRUE)
})
test_that("computed value is stable", {
  expect_snapshot_value(compute_stats(mtcars), style = "json2")
})
```

Update snapshots: `testthat::snapshot_accept()` or `testthat::snapshot_review()`. Files live in `tests/testthat/_snaps/{test-name}.md`.

---

## Test Fixtures and Temporary State

### withr for Temporary State

```r
test_that("function reads from custom path", {
  withr::local_tempdir()
  writeLines("test data", "input.txt")
  expect_equal(read_my_file("input.txt"), "test data")
})
test_that("function respects option", {
  withr::local_options(list(my_pkg.verbose = TRUE))
  expect_message(my_function(), "Processing")
})
test_that("function uses env var", {
  withr::local_envvar(MY_API_KEY = "test-key-123")
  expect_equal(get_api_key(), "test-key-123")
})
```

### Test Helpers (helper.R)

```r
# tests/testthat/helper.R
make_test_data <- function(n = 10) {
  tibble::tibble(x = rnorm(n), y = rnorm(n),
                 group = sample(c("a", "b"), n, replace = TRUE))
}
```

---

## Mocking

```r
test_that("fetch_data handles API failure", {
  local_mocked_bindings(call_api = function(...) stop("Connection refused"))
  expect_null(fetch_data("endpoint"))
})
test_that("process uses correct API response", {
  local_mocked_bindings(call_api = function(...) list(status = 200, body = "ok"))
  expect_equal(process_response(), "ok")
})
# Mock from another package
local_mocked_bindings(read_csv = function(...) tibble::tibble(x = 1:3), .package = "readr")
```

---

## Running Tests

```r
devtools::test()                          # All tests
devtools::test_active_file()              # Current file in IDE
testthat::test_file("tests/testthat/test-fit-model.R")  # Specific file
devtools::test(filter = "fit-model")      # Tests matching pattern
```

---

## Coverage

```r
covr::package_coverage()                  # Full package coverage
covr::report()                            # HTML report in browser
```

**Minimum target: 80% coverage.** Run `scripts/run_coverage.R` for function-level coverage report:

```bash
Rscript scripts/run_coverage.R            # From package root
Rscript scripts/run_coverage.R /path/to/pkg  # Specify path
```

---

## Common Patterns

### Testing Data Frames

```r
test_that("transform_data returns correct structure", {
  input <- tibble::tibble(x = 1:3, y = c("a", "b", "c"))
  result <- transform_data(input)
  expect_s3_class(result, "tbl_df")
  expect_named(result, c("x", "y", "x_squared"))
  expect_equal(result$x_squared, c(1, 4, 9))
})
```

### Testing Plots (vdiffr)

```r
test_that("plot_scatter produces expected output", {
  vdiffr::expect_doppelganger("scatter-wt-mpg", plot_scatter(mtcars, x = "wt", y = "mpg"))
})
```

Setup: `usethis::use_package("vdiffr", type = "Suggests")`

### Testing Error Messages

```r
test_that("validate_column errors with informative message", {
  df <- tibble::tibble(a = 1, b = 2)
  expect_error(validate_column(df, "nonexistent"), class = "pkg_column_not_found")
  err <- expect_error(validate_column(df, "nonexistent"))
  expect_match(conditionMessage(err), "nonexistent")
})
```

### Testing with Temporary Files

```r
test_that("export_results writes correct CSV", {
  tmp <- withr::local_tempfile(fileext = ".csv")
  data <- tibble::tibble(x = 1:3, y = 4:6)
  export_results(data, tmp)
  expect_equal(readr::read_csv(tmp, show_col_types = FALSE), data)
})
```

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Implementation written before its test | Tests-after prove nothing about design; you test what you built, not what you need | Write the test first — if it passes immediately, the test is wrong |
| Skipping the RED phase (test never fails) | A test that never failed never proved anything; it may be tautological | Run the test before implementation, confirm failure, read the error message |
| `test_active_file()` exits silently outside a package | `devtools::test_active_file()` requires a package context with DESCRIPTION | Use `testthat::test_file()` directly for standalone scripts, or wrap code in a package |
| Tests pass alone but fail in `devtools::test()` | Fixture ordering or shared state between test files; `setup.R` side effects leak | Each test must be self-contained; use `withr::local_*()` for temporary state |
| Snapshot collisions across branches | Two branches update the same `_snaps/*.md` file, causing merge conflicts | Accept snapshots on one branch, rebase, re-run `snapshot_review()` on the other |
| "Too simple to test" | Simple code breaks too — off-by-one, NULL input, empty vector edge cases | If you wrote it, test it; trivial tests run in milliseconds and catch regressions |
| Mocking the wrong binding scope | `local_mocked_bindings()` mocks in the test package namespace, not the target package | Set `.package = "targetpkg"` to mock where the function is actually called |
| Writing exhaustive test suites when user asked for one test | Scope creep wastes time and overwhelms the user with unnecessary coverage | Deliver exactly what was requested; suggest additional tests as follow-up |

---

## Example Prompts — Full TDD Cycle

**1. New validation function:** "Add `validate_input()` that checks a data frame has required columns and at least one row." Steps: create test file, write tests for valid/invalid inputs, run (RED), implement in `R/validate-input.R` (GREEN), refactor error messages with cli (REFACTOR).

**2. Fixing a bug:** "Bug: `summarise_groups()` drops groups with all NA values." Steps: write test reproducing bug (RED), fix `na.rm` logic (GREEN), run full suite for regressions.

**3. Adding a plot function:** "Create `plot_distribution()` with histogram + density overlay." Steps: test returns ggplot, correct layers, vdiffr snapshot (RED), implement (GREEN), extract theme helper (REFACTOR).

**4. Refactoring:** "Split `R/utils.R` into `R/utils-validation.R` and `R/utils-formatting.R`." Steps: run existing suite (baseline GREEN), move functions, run suite (still GREEN), add missing coverage.

**5. API integration:** "Test `fetch_weather()` calling external API." Steps: write tests with `local_mocked_bindings()` for success/failure/malformed (RED), implement (GREEN), add skipped-on-CI integration test.
