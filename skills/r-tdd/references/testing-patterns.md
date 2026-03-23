# Testing Patterns Reference

Deep-dive reference for testthat expectations, common testing patterns, and
test isolation techniques using withr.

---

## Core Expectations Reference

### Equality and Identity

| Function | Use When |
|----------|----------|
| `expect_identical(x, y)` | Default in 3e — exact match including type |
| `expect_equal(x, y)` | Numeric comparison needing tolerance (floats) |
| `expect_equal(x, y, tolerance = 1e-4)` | Custom tolerance for approximate comparison |
| `expect_setequal(x, y)` | Same elements regardless of order |
| `expect_mapequal(x, y)` | Same named elements regardless of order |

### Type and Class

| Function | Use When |
|----------|----------|
| `expect_type(x, "double")` | Check base type (typeof) |
| `expect_s3_class(x, "tbl_df")` | Check S3 class |
| `expect_s4_class(x, "MyClass")` | Check S4 class |
| `expect_true(x)` / `expect_false(x)` | Boolean assertions |
| `expect_null(x)` | Value should be NULL |
| `expect_length(x, 5)` | Check vector/list length |
| `expect_named(x, c("a", "b"))` | Check names |

### Output and Side Effects

| Function | Use When |
|----------|----------|
| `expect_output(f(), "pattern")` | Function prints to console |
| `expect_message(f(), "pattern")` | Function emits a message |
| `expect_warning(f(), "pattern")` | Function emits a warning |
| `expect_error(f(), class = "err_type")` | Function signals a typed error |
| `expect_no_error(f())` | Function runs cleanly |
| `expect_no_warning(f())` | Function runs without warnings |
| `expect_no_message(f())` | Function runs without messages |
| `expect_condition(f(), class = "cond")` | Match any condition class |

### Snapshots

| Function | Use When |
|----------|----------|
| `expect_snapshot(expr)` | Capture console output |
| `expect_snapshot(expr, error = TRUE)` | Capture error output |
| `expect_snapshot_value(expr, style = "json2")` | Capture computed value |
| `expect_snapshot_file(path)` | Capture file contents |

---

## Testing Plots with vdiffr

Visual regression testing for ggplot2 output.

### Setup

```r
usethis::use_package("vdiffr", type = "Suggests")
```

### Basic Usage

```r
test_that("plot_scatter produces expected output", {
  p <- plot_scatter(mtcars, x = "wt", y = "mpg")
  vdiffr::expect_doppelganger("scatter-wt-mpg", p)
})
```

### Managing Visual Snapshots

- First run creates reference SVGs in `tests/testthat/_snaps/`
- Subsequent runs compare against references
- Review changes: `vdiffr::manage_cases()` opens a Shiny app for visual diff
- Accept changes: `testthat::snapshot_accept()`

### Tips

- Name doppelgangers descriptively — they become filenames
- Test with a fixed theme to avoid system-dependent font differences
- Set `options(device = "png")` in `setup.R` if SVG rendering varies across CI

---

## Testing Error Messages

Capture and inspect structured error conditions.

### Pattern: Capture and Inspect

```r
test_that("validate_column errors with informative message", {
  df <- tibble::tibble(a = 1, b = 2)
  err <- expect_error(
    validate_column(df, "nonexistent"),
    class = "pkg_column_not_found"
  )
  expect_match(conditionMessage(err), "nonexistent")
})
```

### Pattern: Test Multiple Error Properties

```r
test_that("process_data provides actionable error details", {
  err <- expect_error(
    process_data(NULL),
    class = "pkg_invalid_input"
  )
  # Check the message
  expect_match(conditionMessage(err), "non-NULL")
  # Check custom condition fields (if using cli::cli_abort with extra data)
  expect_equal(err$expected_type, "data.frame")
})
```

### Prefer class= Over Regex

```r
# GOOD — stable, refactor-proof
expect_error(fn(), class = "pkg_error_type")

# BAD — breaks if message wording changes
expect_error(fn(), "column .* not found")
```

---

## Test Isolation with withr

Every test should be independent — withr provides scoped state changes that
automatically revert when the test completes.

### Temporary Files and Directories

```r
test_that("function reads from custom path", {
  withr::local_tempdir()
  writeLines("test data", "input.txt")
  expect_equal(read_my_file("input.txt"), "test data")
})

test_that("function writes output file", {
  tmp <- withr::local_tempfile(fileext = ".csv")
  write_my_csv(data, tmp)
  expect_true(file.exists(tmp))
})
```

### Options and Environment Variables

```r
test_that("function respects option", {
  withr::local_options(list(my_pkg.verbose = TRUE))
  expect_message(my_function(), "Processing")
})

test_that("function uses env var", {
  withr::local_envvar(MY_API_KEY = "test-key-123")
  expect_equal(get_api_key(), "test-key-123")
})
```

### Working Directory

```r
test_that("function resolves relative paths", {
  withr::local_dir(withr::local_tempdir())
  writeLines("content", "file.txt")
  expect_equal(my_read("file.txt"), "content")
})
```

### Common withr Functions

| Function | Scoped Change |
|----------|--------------|
| `local_tempfile()` | Creates temp file, deleted on exit |
| `local_tempdir()` | Changes working dir to temp dir, reverts on exit |
| `local_dir(path)` | Changes working dir, reverts on exit |
| `local_options(list(...))` | Sets options, reverts on exit |
| `local_envvar(...)` | Sets env vars, reverts on exit |
| `local_seed(42)` | Sets RNG seed, reverts on exit |
| `local_locale(...)` | Sets locale, reverts on exit |
| `local_timezone("UTC")` | Sets timezone, reverts on exit |
| `local_par(list(mar = c(1,1,1,1)))` | Sets graphics params, reverts on exit |
| `defer(expr)` | Custom cleanup — runs expr on test exit |

### Test Helpers (helper.R)

Put shared factory functions in `tests/testthat/helper.R` — available to all test files automatically.

```r
# tests/testthat/helper.R
make_test_data <- function(n = 10) {
  tibble::tibble(
    id = seq_len(n),
    value = rnorm(n),
    group = sample(c("A", "B"), n, replace = TRUE)
  )
}
```

Use in any test file without sourcing:

```r
test_that("summarize handles small data", {
  result <- summarize_data(make_test_data(5))
  expect_equal(nrow(result), 2)  # one row per group
})
```
