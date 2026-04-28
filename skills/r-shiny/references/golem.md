# golem Deep Dive

`golem` packages a Shiny app as a production R package. You get
`DESCRIPTION`, `NAMESPACE`, roxygen, `R CMD check`, and a `dev/` lifecycle
on top of base Shiny. Use it when the app must ship as a versioned artifact
on Posit Connect, ShinyProxy, or behind a Docker reverse proxy. See
[`frameworks-decision.md`](frameworks-decision.md) for the picker and
[`testing.md`](testing.md) for the full test layout.

## Why golem

- **Package-as-app.** The app *is* an R package. `devtools::load_all()`,
  `devtools::check()`, and `usethis::use_*()` all work. CI runs
  `R CMD check` against the app like any CRAN candidate.
- **Environment profiles.** `inst/golem-config.yml` separates `default`,
  `production`, and `dev` settings; `R_CONFIG_ACTIVE` selects the profile.
- **Opinionated structure.** `R/app_ui.R`, `R/app_server.R`, `R/run_app.R`,
  plus `R/mod_*.R` for modules and `R/fct_*.R` / `R/utils_*.R` for logic.
- **Deployment-ready.** Built-in helpers for Dockerfiles, ShinyProxy,
  Posit Connect manifests, favicon, and `inst/app/www/` static assets.

## Scaffolding

```r
golem::create_golem(pkg = "myapp", open = FALSE)
```

produces:

```
myapp/
├── DESCRIPTION
├── NAMESPACE
├── R/
│   ├── app_config.R       # get_golem_config() wrapper
│   ├── app_server.R       # top-level server entry
│   ├── app_ui.R           # top-level UI entry + golem_add_external_resources()
│   └── run_app.R          # exported runner; with_golem_options()
├── inst/
│   ├── app/
│   │   └── www/           # static assets shipped with the package
│   │       └── favicon.ico
│   ├── golem-config.yml   # env-aware config
│   └── extdata/           # static data files (created on demand)
├── dev/                   # 01_start.R, 02_dev.R, 03_deploy.R, run_dev.R
└── tests/testthat/
```

`R/run_app.R` exports `run_app()`, which wraps `shinyApp(ui = app_ui,
server = app_server, ...)` inside `golem::with_golem_options()` so
per-run options are available everywhere via `golem::get_golem_options()`.

## Adding modules

```r
golem::add_module(name = "filter", with_test = TRUE)
```

generates `R/mod_filter.R` and `tests/testthat/test-mod_filter.R`. A
production-shaped module file:

```r
#' filter UI Function
#' @noRd
mod_filter_ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("cyl"), "Cylinders", choices = NULL, multiple = TRUE),
    sliderInput(ns("mpg"), "MPG range", min = 0, max = 50, value = c(10, 35))
  )
}

#' filter Server Function
#' @noRd
mod_filter_server <- function(id, data) {
  stopifnot(is.reactive(data))
  moduleServer(id, function(input, output, session) {
    observeEvent(data(), {
      updateSelectInput(
        session, "cyl",
        choices = sort(unique(data()$cyl)),
        selected = sort(unique(data()$cyl))
      )
    })
    reactive({
      req(input$cyl, input$mpg)
      data() |>
        dplyr::filter(
          .data$cyl %in% input$cyl,
          dplyr::between(.data$mpg, input$mpg[1], input$mpg[2])
        )
    })
  })
}
```

Wired from `app_server.R`:

```r
app_server <- function(input, output, session) {
  data_r <- reactive(mtcars)
  filtered_r <- mod_filter_server("filter1", data = data_r)
  output$n_rows <- renderText(nrow(filtered_r()))
}

app_ui <- function(request) {
  tagList(
    golem_add_external_resources(),
    fluidPage(
      mod_filter_ui("filter1"),
      verbatimTextOutput("n_rows")
    )
  )
}
```

## Business logic separation

```r
golem::add_fct("etl")     # R/fct_etl.R   — impure: I/O, DB, network
golem::add_utils("formatting")  # R/utils_formatting.R — pure helpers
```

Rule: **never put business logic in `mod_*`**. Modules wire reactive
plumbing; `fct_*` performs side effects (DB pulls, file reads, API calls);
`utils_*` holds deterministic helpers. This makes unit tests trivial — you
test `fct_load_orders()` and `utils_format_currency()` without spinning up
a session.

## Configuration via `golem-config.yml`

```yaml
default:
  golem_name: myapp
  golem_version: 0.1.0
  app_prod: false
  data_path: !expr golem::app_sys("extdata", "sample.csv")
  log_level: "info"

production:
  app_prod: true
  data_path: "/srv/data/orders.parquet"
  log_level: "warn"
  db_url: !expr Sys.getenv("MYAPP_DB_URL")

dev:
  app_prod: false
  data_path: !expr golem::app_sys("extdata", "sample.csv")
  log_level: "debug"
```

Read values from anywhere in the app:

```r
data_path <- golem::get_golem_config("data_path")
```

The active profile is selected by `R_CONFIG_ACTIVE`; in `dev/run_dev.R`
golem sets it to `"dev"` before sourcing. `golem::app_sys()` resolves
files inside the installed package, never `getwd()` — this is the
golden-path-safe replacement for `system.file()` plus path joining.

## Data files

- `inst/extdata/` — static, file-shaped assets (CSV, parquet, JSON,
  shapefiles). Load with `golem::app_sys("extdata", "x.csv")`.
- `data/` — package-level `.rda` for `data(my_dataset)`. Build via
  `usethis::use_data(my_dataset)`; document in `R/data.R`.
- Never read from `getwd()` — it breaks once the package is installed.
- `system.file()` from base R works the same way for installed packages —
  `golem::app_sys()` is a thin wrapper that calls
  `system.file(..., package = pkgload::pkg_name())`. Use `app_sys()` inside
  golem code; reach for `system.file()` when you're outside the package
  context (e.g., a smoke-test script).

```r
orders <- readr::read_csv(golem::app_sys("extdata", "orders.csv"))
```

## Running locally vs production

```r
# local iteration (sets R_CONFIG_ACTIVE = "dev")
source("dev/run_dev.R")

# explicit local run
myapp::run_app(options = list(port = 1234, launch.browser = TRUE))

# production via Posit Connect, ShinyProxy, or Docker:
# the runner is myapp::run_app(); the entrypoint script is `app.R`
# containing only:  myapp::run_app()
```

`golem::with_golem_options()` lets you pass per-run config (e.g. an
override token or a feature flag) without polluting global state. Read
them inside any module via `golem::get_golem_options("flag_name")`.

## Dockerization

```r
golem::add_dockerfile_shinyproxy()  # for ShinyProxy / k8s
golem::add_dockerfile()             # standalone
```

These generate a `Dockerfile`, `.dockerignore`, and a `renv.lock`-aware
build. Snapshot dependencies first so the image is reproducible:

```r
renv::init()      # one-time
renv::snapshot()  # before every image build
```

Multi-stage build (ShinyProxy variant), trimmed for clarity:

```dockerfile
# ---- stage 1: build ----
FROM rocker/r-ver:4.4.1 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev libssl-dev libxml2-dev git && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY renv.lock renv.lock
RUN R -e "install.packages('renv'); renv::restore()"
COPY . .
RUN R CMD INSTALL --no-multiarch --with-keep.source .

# ---- stage 2: runtime ----
FROM rocker/r-ver:4.4.1
# Runtime system libraries — match the build-stage list (see "trimmed for clarity" caveat).
# Packages like httr2, curl, xml2 need libcurl4 / libssl3 / libxml2 at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libcurl4 \
      libssl3 \
      libxml2 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /usr/local/lib/R/site-library /usr/local/lib/R/site-library
EXPOSE 3838
ENV R_CONFIG_ACTIVE=production
CMD ["R", "-e", "options(shiny.port = 3838, shiny.host = '0.0.0.0'); myapp::run_app()"]
```

## Testing layout

`tests/testthat/test-mod_*.R` mirrors `R/mod_*.R` 1:1. Use `testServer()`
for module reactive logic, and `shinytest2::AppDriver` for end-to-end
checks against `run_app()`. See [`testing.md`](testing.md) for the full
matrix and CI snippets.

```r
# tests/testthat/test-mod_filter.R
test_that("mod_filter_server returns filtered rows", {
  testServer(
    mod_filter_server,
    args = list(data = reactive(mtcars)),
    {
      session$setInputs(cyl = c(4, 6), mpg = c(20, 35))
      expect_true(all(session$returned()$cyl %in% c(4, 6)))
    }
  )
})

# tests/testthat/test-app-feature.R
test_that("app boots and renders filter", {
  app <- shinytest2::AppDriver$new(myapp::run_app(), name = "boot")
  app$expect_values()
})
```

## Common gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| Using `getwd()` for data paths | Works in dev, 404s once installed | Always `golem::app_sys("extdata", ...)` |
| `system.file()` without package arg | Returns `""` after install | Use `golem::app_sys()` or `system.file(..., package = "myapp")` |
| Putting assets in `www/` at project root | Not served by the installed package | Move to `inst/app/www/`; golem maps that to `/` automatically |
| Forgotten `ns()` on dynamic UI inside a module | Inputs don't react, IDs collide across instances | Wrap every dynamically created `inputId` with `session$ns()` or module-level `ns <- NS(id)` |
| `enableBookmarking = "url"` without `setBookmarkExclude()` | Sensitive inputs leak into URL state | Set `bookmarkable_state = TRUE` in config and call `setBookmarkExclude()` for tokens / passwords |
| `library()` calls inside `R/` | `R CMD check` warns; deps invisible to `NAMESPACE` | Use `pkg::fun()` qualified calls, declare in `DESCRIPTION` via `usethis::use_package()` |

## When NOT to use golem

- **Pure prototype, single author, <500 lines.** Use a single-file
  `app.R`. Package overhead buys nothing.
- **Need `box::use()` semantics** (no `library()`, file-level imports,
  Sass pipeline, Cypress E2E). Use **rhino** — see
  [`frameworks-decision.md`](frameworks-decision.md).
- **CDISC ADaM/SDTM clinical data with regulated reproducibility.** Use
  **teal** — `teal::init()` plus `teal.data::cdisc_data()` already gives
  you the filter panel, code generation, and validation hooks golem would
  ask you to rebuild from scratch.
