# rhino Deep Dive

`rhino` is Appsilon's enterprise Shiny framework. It enforces
file-level imports via `box::use()`, ships a Sass pipeline, opinionated
linters, and a Cypress + shinytest2 testing stack. Reach for it when a
multi-developer team needs SPA-style structure, heavy CSS theming, and
browser E2E baked into CI. See
[`frameworks-decision.md`](frameworks-decision.md) for the picker and
[`testing.md`](testing.md) for the test matrix.

## Why rhino

- **`box::use()` modules** — file-level imports, no `library()`, no
  implicit globals; `box.linters` fails CI on stray `library()`.
- **View / logic split** — `app/view/` for UI + render glue;
  `app/logic/` for pure functions that unit-test without a session.
- **Sass pipeline** — `app/styles/main.scss` compiles on app load;
  partials keep CSS modular with hot reload in dev.
- **Cypress E2E + shinytest2 + testthat** — browser tests in CI,
  R-level snapshots, and pure-logic unit tests, layered.
- **Opinionated linting** — `rhino::lint_r() / lint_sass() / lint_js()`
  enforce style across R, Sass, and JS.

## Scaffolding

`rhino::init("myapp")` produces:

```
myapp/
├── app/
│   ├── main.R              # ui() / server() entry points
│   ├── view/               # box modules: UI + render glue
│   ├── logic/              # box modules: pure functions
│   ├── static/             # images, favicons, JS assets
│   ├── styles/
│   │   ├── main.scss       # entry — imports partials
│   │   └── _filter.scss    # per-component partial
│   └── js/                 # optional custom JS modules
├── tests/
│   ├── cypress/            # Cypress E2E specs (.cy.js)
│   └── testthat/           # R unit + shinytest2 tests
├── rhino.yml               # framework configuration
├── dependencies.R          # declares R deps (renv discovery only)
├── config.yml              # env-aware app config
├── app.R                   # one-liner runner: rhino::app()
└── renv.lock
```

`dependencies.R` is the *only* place `library(...)` appears — it lets
`renv` discover packages; app code under `app/` never calls `library()`.

## The `box::use()` pattern

`box::use()` replaces `library()` with explicit, file-scoped imports.
Each file declares exactly the symbols it needs. Versus
`library(shiny); library(dplyr)` you get no global namespace pollution
(no `dplyr::filter` vs `stats::filter` collision), file-level
dependency clarity, and `box.linters` flagging unused or undeclared
symbols — so "object not found" surfaces in CI, not at runtime.

A view module — `app/view/filter.R`:

```r
box::use(
  shiny[NS, moduleServer, selectInput, sliderInput, tagList,
        observeEvent, updateSelectInput, reactive, req],
  dplyr[filter, between, .data],
)

#' @export
ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("cyl"), "Cylinders", choices = NULL, multiple = TRUE),
    sliderInput(ns("mpg"), "MPG range", min = 0, max = 50, value = c(10, 35)),
  )
}

#' @export
server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    observeEvent(data(), {
      vals <- sort(unique(data()$cyl))
      updateSelectInput(session, "cyl", choices = vals, selected = vals)
    })
    reactive({
      req(input$cyl, input$mpg)
      data() |>
        filter(
          .data$cyl %in% input$cyl,
          between(.data$mpg, input$mpg[1], input$mpg[2]),
        )
    })
  })
}
```

A logic module — `app/logic/data.R`:

```r
box::use(
  dplyr[filter, mutate, .data],
  tibble[as_tibble],
)

#' @export
load_cars <- function(min_mpg = 0) {
  mtcars |>
    as_tibble() |>
    mutate(model = rownames(mtcars)) |>
    filter(.data$mpg >= min_mpg)
}
```

Consume from another module via
`box::use(app/logic/data[load_cars], app/view/filter)`.

## View / logic split

- `app/view/` — UI builders, `moduleServer()` wiring, `render*()` calls;
  imports `shiny` and view-side packages.
- `app/logic/` — pure functions. No `shiny`, no `reactive()`, no
  `session`. Data in, data out.

Test pure logic with `testthat`; view modules with `shiny::testServer()`
or `shinytest2`. The boundary contains reactivity debugging.

## Sass pipeline

`app/styles/main.scss` compiles on app load; partials use a leading
underscore and are `@import`ed:

```scss
// app/styles/main.scss
@import "filter";
@import "theme";
.app-shell { display: grid; grid-template-columns: 280px 1fr; }

// app/styles/_filter.scss
.filter-card { padding: 1rem; border-radius: 8px; background: var(--surface); }
```

In dev, `.scss` edits trigger recompile + browser reload; in
production the compiled CSS ships as a static asset.

## `rhino.yml` configuration

```yaml
sass:
  preset: bootstrap            # or "none" for raw scss
  cache: true
js:
  bundle: true                 # roll up app/js/*.js
  minify: true
reload:
  enabled: true                # hot reload during dev
  ignore: ["tests/**"]
```

`sass.preset: none` drops Bootstrap; `js.bundle: true` activates the
bundler over `app/js/`.

## Testing

rhino layers three test types — see [`testing.md`](testing.md) for the
full table and CI snippets:

- **`tests/testthat/`** — pure logic. Import via
  `box::use(app/logic/data)` and assert on returned values; no session.
- **`tests/testthat/test-shinytest2-*.R`** — R-level E2E via
  `shinytest2::AppDriver$new(rhino::app())`; snapshots UI + values.
- **`tests/cypress/e2e/*.cy.js`** — browser E2E. `rhino::test_e2e()`
  serves the app and runs Cypress on `localhost` for click-flows,
  custom JS, and accessibility checks `shinytest2` can't reach.

## Linting and CI

```r
rhino::lint_r()      # lintr + box.linters across app/ and tests/
rhino::lint_sass()   # stylelint over app/styles/
rhino::lint_js()     # eslint over app/js/ and tests/cypress/
```

CI runs `lint_r()`, `lint_sass()`, `lint_js()`,
`testthat::test_local()`, then `rhino::test_e2e()`. `box.linters` flags
stray `library()` calls, so `library(dplyr)` fails CI immediately.

## Migration from base / golem to rhino

**Pays off when:** 3+ developers share the app and need file-level
import clarity; you want a Sass design system with hot reload; E2E
browser flows (drag/drop, custom JS, charts) are acceptance criteria;
deployment is enterprise SPA (reverse proxy, custom branding, Posit
Connect, k8s).

**Does NOT pay off when:** the goal is a CRAN-style R package with
clean `R CMD check` (use **golem**); contributors are R-only with no
JS/CSS surface (Cypress + Sass + box overhead is pure tax); the app is
regulated CDISC clinical (use **teal**). See
[`frameworks-decision.md`](frameworks-decision.md).

## rhino-specific gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| Forgetting a symbol in `box::use()` | `Error: object 'filter' not found` at runtime | Add the missing symbol to the `box::use()` block at the top of the file |
| Mixing `library()` into `app/` | `box.linters` failure on CI | Convert to `box::use(pkg[symbol1, symbol2])`; declare in `dependencies.R` only |
| Sass change not appearing | Browser shows stale CSS after edit | Confirm `reload.enabled: true` in `rhino.yml`; hard refresh once after restart |
| Importing a module file by accident | `Error: could not find function "ui"` | Use `box::use(app/view/filter)` and call `filter$ui("id")`, or import explicitly: `box::use(app/view/filter[ui, server])` |
| `.data` pronoun missing on tidy-eval calls | `no visible binding for global variable` lint | Add `.data` to the `dplyr` import: `box::use(dplyr[filter, .data])` |
