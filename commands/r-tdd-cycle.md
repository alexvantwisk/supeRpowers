---
description: Guided TDD workflow — Red, Green, Refactor, Review for R packages using testthat 3e
---

# TDD Cycle

Guided Red-Green-Refactor-Review workflow for R packages using testthat 3e.

## Prerequisites

- R package with testthat 3e configured (`Config/testthat/edition: 3` in DESCRIPTION)
- If not configured, run `usethis::use_testthat(3)` first
- Clear understanding of the feature or fix to implement

## Progress Tracking

Use TaskCreate at the start of this workflow — one task per phase below. Mark each `in_progress` when starting, `completed` when its gate passes.

- "Phase 1: Setup test file"
- "Phase 2: RED — Write failing test"
- "Phase 3: GREEN — Minimal implementation"
- "Phase 4: REFACTOR"
- "Phase 5: REVIEW"
- "Phase 6: COVERAGE"

The RED→GREEN flip is the state worth surfacing — task progress proves the test failed before passing.

## Steps

### Step 1: Setup
**Skill:** `r-tdd`
**Action:** Identify the target function name and create the test file with `usethis::use_test("feature-name")`. Confirm testthat 3e is active.
**Gate:** Test file exists at `tests/testthat/test-feature-name.R`.

### Step 2: RED — Write failing test
**Skill:** `r-tdd`
**Action:** Write one or more `test_that()` blocks that define the desired behavior. Use `expect_identical()` (3e default), `expect_error(class = ...)` for error cases. Run `devtools::test_active_file()`.
**Gate:** Test runs and FAILS (function does not exist or returns wrong result). If test passes immediately, the test is wrong — rewrite it.

### Step 3: GREEN — Minimal implementation
**Skill:** `r-tdd`
**Action:** Write the minimum code in `R/feature-name.R` to make the test pass. Do NOT add logic beyond what the test requires. Run `devtools::test_active_file()`.
**Gate:** Test runs and PASSES.

### Step 4: REFACTOR
**Action:** Improve code quality — naming, structure, duplication — while keeping tests green. Run `devtools::test()` to verify no regressions across the package.
**Gate:** All tests pass. No new warnings.

### Step 5: REVIEW
**Agent:** `r-code-reviewer` (scope: full)
**Action:** Review the new implementation and test files for style, correctness, and performance.
**Gate:** No CRITICAL findings. HIGH findings addressed.

### Step 6: COVERAGE
**Skill:** `r-tdd`
**Action:** Run `covr::package_coverage()` and check function-level coverage for the new code.
**Gate:** Coverage >= 80% for new functions.

## Abort Conditions

- Test passes on first run in RED phase — the test is wrong, not the code. Rewrite the test before proceeding.
- CRITICAL finding in code review that requires architectural change — stop and re-plan.
- Coverage drops below 80% after refactoring — add tests before continuing.

## Examples

### Example: Adding a validation function

**Prompt:** "Add `validate_input()` that checks a data frame has required columns."

**Flow:** Setup (create test file) → RED (write test for valid input + missing columns) → GREEN (implement with `cli::cli_abort()`) → REFACTOR (clean up) → REVIEW (code reviewer) → COVERAGE (verify 80%+)

```r
# RED — test file
test_that("validate_input errors on missing columns", {
  df <- tibble::tibble(id = 1:3)
  expect_error(
    validate_input(df, required = c("id", "value")),
    class = "pkg_missing_columns"
  )
})

# GREEN — minimal implementation
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
```

### Example: Bug fix with regression test

**Prompt:** "Fix `calc_growth()` — it returns NA for single-row groups."

**Flow:** Setup (open existing test file) → RED (write test exposing the bug — single-row group) → GREEN (add guard for `n() > 1`) → REFACTOR → REVIEW → COVERAGE

```r
# RED — expose the bug
test_that("calc_growth handles single-row groups", {
  df <- tibble::tibble(group = "A", date = as.Date("2024-01-01"), value = 100)
  result <- calc_growth(df)
  expect_true(is.na(result$growth[1]))  # expected NA, not error
})
```
