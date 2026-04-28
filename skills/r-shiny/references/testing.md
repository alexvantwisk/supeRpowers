# Shiny Testing Deep Dive

Two complementary layers cover Shiny apps end-to-end. Use both — neither replaces
the other.

## Two-layer strategy

| Layer | Tool | Scope | Speed | Browser? | Use when |
|-------|------|-------|-------|----------|----------|
| Unit | `shiny::testServer()` | Single module / app server function | Fast (<1s/test) | No | Asserting reactive logic, returns, side effects on `output$x` |
| Integration | `shinytest2::AppDriver` | Whole app, real DOM | Slow (5–30s/test) | Headless Chrome | Asserting end-to-end flows, JS, downloads, screenshots |

Rule of thumb: unit-test every module's server function with `testServer()`,
then write 3–10 `shinytest2` tests for the critical user journeys (load, filter,
download, error path). Do not unit-test the UI function — render it and assert
in the integration layer.

Cross-links: `golem.md` for golem test layout, `rhino.md` for Cypress, `teal.md`
for teal-aware fixtures.

## `testServer()` fundamentals

```r
test_that("filter module returns filtered data", {
  testServer(mod_filter_server, args = list(data = reactive(mtcars)), {
    session$setInputs(column = "mpg", range = c(20, 30))
    result <- session$getReturned()()
    expect_true(all(result$mpg >= 20 & result$mpg <= 30))
  })
})
```

Inside the `testServer()` block you have a synthetic `session` plus everything
the module created (`input`, `output`, internal reactives). Key APIs:

- `session$setInputs(name = value, ...)` — set inputs and flush the reactive
  graph in one shot. Multiple inputs in one call are applied together (avoids
  intermediate invalidation).
- `session$getReturned()` — returns the value the module's server function
  returned. If the module returned a reactive, call it: `session$getReturned()()`.
- `session$elapsed(secs)` — advance time for `invalidateLater()`,
  `reactiveTimer()`, `debounce()`, and `throttle()` without sleeping the test.
- `session$flushReact()` — force the reactive graph to flush manually (rare;
  `setInputs` already flushes).
- `output$x` — read directly to inspect rendered output values. For
  `renderText()` you get the string; for `renderTable()` you get the rendered
  HTML. Wrap with `parse_*()` helpers if you need structured data.
- `session$ns("foo")` — verify namespacing if the module mints child IDs.

`testServer()` does not render UI, does not run JavaScript, and does not call
`htmlwidgets`. If your assertion depends on any of those, use `shinytest2`.

## App-level reactivity tests with `shiny::testServer(app)`

For a top-level `app.R` that has no module split yet (or has app-wide reactives
outside any module), pass the entire app:

```r
test_that("app-level totals refresh", {
  app <- shinyApp(ui = app_ui(), server = app_server)
  testServer(app, {
    session$setInputs(year = 2024)
    expect_equal(output$total, "1,234")
  })
})
```

Same `session` API as the module form. Useful for golem packages where
`app_server()` wires modules together and you want to assert cross-module
behaviour without spinning up Chrome.

## `shinytest2::AppDriver` fundamentals

```r
test_that("filter button updates table", {
  app <- shinytest2::AppDriver$new(app_dir = ".", name = "filter")
  app$set_inputs(species = "setosa")
  app$click("apply")
  app$expect_values(input = TRUE, output = TRUE, export = TRUE)
  app$stop()
})
```

`AppDriver` boots the app in a headless Chromium (via `chromote`) and gives you
a programmatic DOM. Workhorse methods:

- `app$set_inputs(name = value, wait_ = TRUE)` — set inputs and wait for the
  graph to settle.
- `app$click(id)` — click an `actionButton` / `actionLink`.
- `app$wait_for_idle(duration = 100, timeout = 30000)` — block until no
  reactive output has updated for `duration` ms. Use after async work.
- `app$expect_values(input = TRUE, output = TRUE, export = TRUE)` —
  snapshot test of inputs/outputs/exports. First run records, later runs diff.
- `app$expect_screenshot()` — visual snapshot. Pin viewport size to keep stable.
- `app$get_value(input = "x")` / `output = "y"` / `export = "z"` — read a
  single value without a snapshot (cheaper, no review burden).
- `app$get_logs()` — capture R, JS, and chromote logs. Indispensable for flake
  triage.
- `app$expect_download(id, name = "...")` — click a `downloadButton`, capture
  the file, snapshot its contents.
- `app$set_window_size(width, height)` — pin viewport before screenshots.
- `app$stop()` — always close (use `withr::defer(app$stop())` if test may abort).

## Snapshot review workflow

`expect_values()` and `expect_screenshot()` write `_snaps/<test>/` files. After
intentional UI changes:

```r
testthat::snapshot_review()    # opens diff viewer in browser
testthat::snapshot_accept()    # accept all (use sparingly)
```

CI runs `testthat::test_local()` non-interactively; stale snapshots fail the
build. Commit snapshot files to git so reviewers can see the visual diff.

## Mocking external services

Three layers, ordered by preference:

1. **`mockery::stub()`** — replace a function inside a single test. Best for
   database / API helpers called from your module:
   ```r
   mockery::stub(mod_users_server, "fetch_users", tibble(id = 1, name = "x"))
   ```
2. **`httptest2::with_mock_dir("mocks/users", { ... })`** — record-and-replay
   real HTTP calls. Run once with `httptest2::start_capturing()` against the
   live API; subsequent runs replay cached fixtures.
3. **`vcr`** — same idea, YAML cassettes; choose if your team already uses it.

Never stub `shiny::reactive`, `observeEvent`, or `session`. Mock the boundary
(DB driver, HTTP client, file reader), not Shiny.

## Headless Chrome on CI

`shinytest2` uses `chromote`, which needs a real Chrome/Chromium binary. On
GitHub Actions Ubuntu runners:

```yaml
- uses: r-lib/actions/setup-r-dependencies@v2
  with:
    extra-packages: |
      any::shinytest2
      any::chromote
- name: Set Chrome path
  run: echo "CHROMOTE_CHROME=$(which google-chrome)" >> $GITHUB_ENV
```

Cache the renv / pak library on `chromote` and `shinytest2` versions to avoid
re-downloading Chromium-driver assets each run. macOS runners usually find
Chrome automatically; Windows runners need `CHROMOTE_CHROME` pointed at
`chrome.exe`.

## Fixtures

- **Small in-package fixtures** — ship as `inst/extdata/test-data.csv` and
  load with `readr::read_csv(system.file("extdata", "test-data.csv", package = "myapp"))`.
- **HTTP recordings** — `httptest2` or `vcr` cassettes under
  `tests/testthat/_mocks/`. Re-record yearly or on API contract changes.
- **Large data** — fetch once with `pins::board_*()` or `piggyback::pb_download()`
  in a `setup-*.R` test helper; never commit binaries >1 MB.
- **Clinical fixtures** — `teal.modules.clinical::ex_adsl`, `ex_adtte`,
  `ex_adlb`, etc. give CDISC-shaped tibbles for free; see `teal.md`.

## golem-specific testing layout

Mirror `R/` one-to-one in `tests/testthat/`:

```
R/mod_filter.R        ->  tests/testthat/test-mod_filter.R
R/mod_plot.R          ->  tests/testthat/test-mod_plot.R
R/app_server.R        ->  tests/testthat/test-app_server.R
                          tests/testthat/test-app.R   # shinytest2 full-app
```

`usethis::use_test("mod_filter")` scaffolds the file. Run with
`devtools::test()`; coverage with `covr::package_coverage()`. See `golem.md`
for the broader package layout.

## rhino-specific testing layout

rhino splits R-side from JS-side:

- `tests/testthat/` — module unit tests via `testServer()`.
- `tests/cypress/` — Cypress specs driving the running app.
- `rhino::test_r()` — runs the R suite via `box`-aware loader.
- `rhino::test_e2e()` — boots the app with `shiny::runApp()` and runs Cypress.

In CI run `rhino::test_r()` first (fast); only run `rhino::test_e2e()` on PRs
to main. See `rhino.md` for the full toolchain.

## teal app testing

`teal::init()` returns a list with `ui` and `server`. Hand that to `AppDriver`
via the inline-app form to skip filesystem boilerplate:

```r
test_that("teal filter panel propagates", {
  app_obj <- teal::init(
    data    = teal_data(IRIS = iris),
    modules = modules(example_module())
  )
  app <- shinytest2::AppDriver$new(
    shiny::shinyApp(app_obj$ui, app_obj$server),
    name = "teal-filter"
  )
  app$set_inputs(`teal-main_ui-filter_panel-active-IRIS-Species` = "setosa")
  app$wait_for_idle()
  expect_match(app$get_value(output = "teal-main_ui-module-table"), "setosa")
  app$stop()
})
```

teal namespaces are deep — copy IDs from the running app via the browser
inspector rather than guessing. See `teal.md` for fixture datasets.

## Flake patterns

- **Race on `wait_for_idle`** — bump `duration = 500` and `timeout = 60000` for
  apps with chained promises; assert on a sentinel output rather than time.
- **Locale-dependent snapshots** — set `Sys.setenv(LANG = "C", LC_ALL = "C")`
  in `tests/testthat/setup.R` so number/date formatting is reproducible.
- **Timezone drift** — `withr::local_envvar(TZ = "UTC")` per test, or globally
  in setup.
- **Viewport-dependent screenshots** — pin `app$set_window_size(1280, 800)`
  before every `expect_screenshot()`.
- **Promise pool size** — `Sys.setenv(R_PARALLELLY_AVAILABLECORES_FALLBACK = 1)`
  forces deterministic single-worker behaviour in `future`/`promises`.
- **Random data** — seed with `set.seed(1)` inside the test, never globally.

## GitHub Actions matrix snippet

```yaml
name: R-CMD-check
on: [push, pull_request]
jobs:
  check:
    runs-on: ${{ matrix.config.os }}
    strategy:
      fail-fast: false
      matrix:
        config:
          - { os: ubuntu-latest,  r: "release" }
          - { os: ubuntu-latest,  r: "devel"   }
          - { os: macos-latest,   r: "release" }
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-r@v2
        with: { r-version: ${{ matrix.config.r }} }
      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: |
            any::shinytest2
            any::chromote
            any::covr
      - name: Set Chrome path
        if: runner.os == 'Linux'
        run: echo "CHROMOTE_CHROME=$(which google-chrome)" >> $GITHUB_ENV
      - uses: r-lib/actions/check-r-package@v2
      - name: Upload snapshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: shinytest2-snapshots-${{ matrix.config.os }}
          path: tests/testthat/_snaps/
```

## Coverage goal

Target 80% line coverage minimum across `R/`. For golem packages:

```r
covr::package_coverage()
covr::report()                 # interactive HTML
covr::codecov(token = "...")   # upload to Codecov
```

Module server functions should hit 90%+; UI functions 60%+ is acceptable
because most assertions live in shinytest2. Track coverage on PRs via
Codecov's status check; block merges below threshold.
