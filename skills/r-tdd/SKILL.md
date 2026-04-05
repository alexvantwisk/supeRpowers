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
  Do NOT use for statistical hypothesis testing — use r-stats instead.
---

# R Test-Driven Development

Write tests first, implement second. TDD for R packages using testthat 3rd edition.

> **Boundary:** Test writing and TDD workflow. For R CMD check and package-level quality gates, use r-package-dev instead.

**Agent dispatch:** After REFACTOR phase, dispatch to **r-code-reviewer** for implementation quality. For R CMD check validation, dispatch to **r-pkg-check** agent.

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

Creates `tests/testthat/`, `tests/testthat.R`, sets `Config/testthat/edition: 3` in DESCRIPTION. Edition 3 key changes: `expect_identical()` default, snapshot testing, `expect_error(class=)` preferred, warnings not suppressed, `context()` deprecated.

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
    expect_no_error(validate_input(tibble::tibble(x = 1:3)))
  })
  it("rejects NULL input", {
    expect_error(validate_input(NULL), class = "my_pkg_input_error")
  })
})
```

---

## Expectations — Project Conventions

- **3e default:** `expect_identical()` is the default; use `expect_equal()` only when tolerance matters (floats)
- **Error matching:** Always use `class =` argument, not regex: `expect_error(fn(), class = "pkg_error_type")`
- **Negative assertions:** Prefer `expect_no_error()` / `expect_no_warning()` over `expect_silent()`
- **Snapshots:** `expect_snapshot(expr)` for console output, `expect_snapshot_value(expr, style = "json2")` for computed values. Update with `snapshot_accept()`.

Read `references/testing-patterns.md` for the full expectations reference table, vdiffr visual testing patterns, error message testing, and withr isolation techniques.

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
devtools::test(filter = "fit-model")      # Tests matching pattern
```

---

## Coverage

```r
covr::package_coverage()                  # Full package coverage
covr::report()                            # HTML report in browser
```

**Minimum target: 80% coverage.** Use `scripts/run_coverage.R` from package root for function-level report.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Implementation written before its test | Tests-after prove nothing about design | Write the test first — if it passes immediately, the test is wrong |
| Skipping the RED phase (test never fails) | A test that never failed never proved anything | Run the test before implementation, confirm failure |
| Tests pass alone but fail in `devtools::test()` | Shared state between test files leaks | Each test must be self-contained; use `withr::local_*()` |
| Snapshot collisions across branches | Two branches update the same `_snaps/*.md` file | Accept on one branch, rebase, re-run `snapshot_review()` |
| Mocking the wrong binding scope | `local_mocked_bindings()` mocks in test namespace | Set `.package = "targetpkg"` to mock the actual call site |
| Writing exhaustive test suites when user asked for one test | Scope creep wastes time | Deliver exactly what was requested; suggest extras as follow-up |

---

## Examples

### Happy Path: RED-GREEN-REFACTOR for a Validation Function

**Prompt:** "Add `validate_input()` that checks a data frame has required columns."

```r
# RED — write the failing test first
# tests/testthat/test-validate-input.R
test_that("validate_input accepts a valid data frame", {
  df <- tibble::tibble(id = 1:3, value = c(10, 20, 30))
  expect_no_error(validate_input(df, required = c("id", "value")))
})

test_that("validate_input errors on missing columns", {
  df <- tibble::tibble(id = 1:3)
  expect_error(
    validate_input(df, required = c("id", "value")),
    class = "pkg_missing_columns"
  )
})
# Run: devtools::test_active_file()
# Result: FAIL — validate_input does not exist yet. Good.

# GREEN — minimal implementation
# R/validate-input.R
validate_input <- function(df, required) {
  missing <- setdiff(required, names(df))
  if (length(missing) > 0) {
    cli::cli_abort(
      "Column{?s} {.val {missing}} not found in data.",
      class = "pkg_missing_columns"
    )
  }
  invisible(df)
}
# Run: devtools::test_active_file()
# Result: PASS — both tests green.

# REFACTOR — check coverage, clean up
# covr::package_coverage() -> target 80%+
```

### Edge Case: Testing a Function with Side Effects Using withr

**Prompt:** "Test `write_report()` that writes a CSV and respects an option for the delimiter."

```r
# tests/testthat/test-write-report.R
test_that("write_report writes CSV with default comma separator", {
  tmp <- withr::local_tempfile(fileext = ".csv")
  data <- tibble::tibble(x = 1:3, y = c("a", "b", "c"))
  write_report(data, tmp)
  result <- readr::read_csv(tmp, show_col_types = FALSE)
  expect_equal(result, data)
})

test_that("write_report respects mypkg.delim option for TSV", {
  withr::local_options(list(mypkg.delim = "\t"))
  tmp <- withr::local_tempfile(fileext = ".tsv")
  data <- tibble::tibble(x = 1:2, y = c("a", "b"))
  write_report(data, tmp)
  result <- readr::read_tsv(tmp, show_col_types = FALSE)
  expect_equal(result, data)
})
```

**More example prompts:**
- "Bug: `summarise_groups()` drops groups with all NA values — write a failing test first."
- "Test `fetch_weather()` calling an external API using mocked bindings."
