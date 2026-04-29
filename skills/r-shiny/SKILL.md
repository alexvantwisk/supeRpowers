---
name: r-shiny
description: >
  Use when building, structuring, testing, or deploying R Shiny apps,
  including framework choice across base Shiny, golem, rhino, and teal
  (pharma-standard for CDISC ADaM/SDTM dashboards). Covers reactivity,
  modules, bslib UI with shinydashboard migration, reactive data-flow,
  render wrappers (Plot/Plotly/DT/Reactable), testServer + shinytest2,
  and deployment to Posit Connect, shinyapps.io, ShinyProxy, or Shiny
  Server with renv. Triggers: Shiny, reactive, module, moduleServer, ns,
  observeEvent, reactiveVal, bindCache, dashboard, golem, rhino, teal,
  bslib, value_box, shinydashboard, shinytest2, AppDriver, testServer,
  Posit Connect, ShinyProxy, app.R, mod_*.R. Do NOT use for standalone
  ggplot2 — use r-visualization. Do NOT use for DT/reactable styling —
  use r-tables. Do NOT use for Quarto docs — use r-quarto. Do NOT use
  for crash debugging — use r-debugging. Do NOT use for ADaM/SDTM
  semantics — use r-clinical. Shiny for Python is out of scope.
  /r-shiny-app scaffolds apps.
---

# R Shiny

End-to-end Shiny: reactivity, modules, UI, testing, deployment. Code uses `|>`,
`<-`, `snake_case`, double quotes. Frameworks: **base Shiny**, **golem**,
**rhino**, **teal** (clinical-trial dashboards on CDISC ADaM/SDTM).

**Lazy references** (`references/`):
- `frameworks-decision.md` — base/golem/rhino/teal decision tree.
- `golem.md` — scaffolds, `mod_*`, Connect deploys.
- `rhino.md` — `box::use()`, `app/view/`, `app/logic/`, Sass.
- `teal.md` — `teal::init()`, `cdisc_data()`, `teal.modules.clinical`.
- `ui-frameworks-alt.md` — bs4Dash, shinyMobile, shiny.semantic.
- `reactivity-guide.md` — anti-patterns, `bindCache`, debounce, throttle.
- `modules-patterns.md` — inter-module communication, nested modules.
- `testing.md` — testServer + shinytest2, CI integration.
- `deployment.md` — Connect, shinyapps.io, ShinyProxy, Shiny Server, renv.

**Agent dispatch:** Dispatch the **r-shiny-architect** agent for app structure
review, reactivity audits, and framework adherence (base/golem/rhino/teal).

**MCP (when R session available):** `btw_tool_env_describe_data_frame` before
UI for data display; `btw_tool_docs_help_page` for current API.
## Framework Picker
| Framework  | When to use                                       | Signature feature                                   |
|------------|---------------------------------------------------|-----------------------------------------------------|
| base Shiny | Prototypes, <500 lines, single-author             | `app.R` / `ui.R`+`server.R`                         |
| golem      | Production package, multi-author, Posit Connect   | `mod_*` modules + `golem-config.yml`                |
| rhino      | Enterprise SPA, box modules, Sass                 | `box::use()` + `app/view/` `app/logic/` split       |
| teal       | Clinical-trial dashboards on CDISC ADaM/SDTM      | Declarative `teal::init()` + `teal.modules.clinical`|

**Decision rule:** CDISC ADaM/SDTM → **teal first**. Production package on
Posit Connect → **golem**. Enterprise SPA with `box::use()` and Sass →
**rhino**. Else → **base Shiny**. See `references/{frameworks-decision,golem,rhino,teal}.md`.
## Minimal app.R
```r
library(shiny)
library(bslib)
ui <- page_sidebar(
  sidebar = sidebar(selectInput("dataset", "Dataset", c("mtcars", "iris"))),
  card(card_header("Preview"), tableOutput("table"))
)
server <- function(input, output, session) {
  data <- reactive({ get(input$dataset, "package:datasets") })
  output$table <- renderTable({ head(data()) })
}
shinyApp(ui, server)
```
## Reactivity Decision Guide
- Computed value for others? -> `reactive()` (lazy+cached)
- Side effect? -> `observe()` / `observeEvent()` (eager)
- Mutable state? -> `reactiveVal()` (single) / `reactiveValues()` (multiple) — define **outside** observers
- Delay until button? -> `bindEvent()` (modern) or `observeEvent()` (classic)
- Read without dependency? -> `isolate()`
- Input might be NULL? -> `req()` at the top

Never put side effects in `reactive()`. See `references/reactivity-guide.md`
for anti-patterns, bindCache, debounce, throttle.
## Modules
Modules encapsulate UI + server with namespaced IDs. The server returns a
reactive (or list) — that is the inter-module contract.

```r
mod_filter_ui <- function(id) {
  ns <- NS(id)
  tagList(selectInput(ns("column"), "Column", choices = NULL),
          sliderInput(ns("range"), "Range", min = 0, max = 100, value = c(0, 100)))
}
mod_filter_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    observe({ updateSelectInput(session, "column",
      choices = data() |> dplyr::select(where(is.numeric)) |> names()) })
    reactive({
      req(input$column, input$range)
      data() |> dplyr::filter(.data[[input$column]] >= input$range[1],
                               .data[[input$column]] <= input$range[2])
    })
  })
}
# Wire: filtered <- mod_filter_server("filter1", data = reactive(mtcars))
```

See `references/modules-patterns.md` for inter-module communication, nesting, testing.
## UI with bslib (and shinydashboard migration)
Use bslib pages — never `fluidPage()`: `page_sidebar()`, `page_navbar()`,
`page_fillable()`. Compose with `card()`, `value_box()`, `layout_columns()`,
`accordion()`, `navset_card_tab()`; theme via `bs_theme(bootswatch = "flatly")`.

| shinydashboard            | bslib equivalent                            |
|---------------------------|---------------------------------------------|
| dashboardPage             | page_navbar() / page_sidebar()              |
| dashboardHeader           | page_navbar(title = ...)                    |
| dashboardSidebar          | sidebar()                                   |
| dashboardBody             | page body content                           |
| box(title, ...)           | card(card_header(...), ...)                 |
| valueBox(value, subtitle) | value_box(title = subtitle, value = value)  |
| tabBox                    | navset_card_tab()                           |
| infoBox                   | value_box() with showcase                   |

Non-bslib alternatives (bs4Dash, shinyMobile, shiny.semantic): `references/ui-frameworks-alt.md`.
## Dynamic UI
| Method                      | When to use                                                    |
|-----------------------------|----------------------------------------------------------------|
| `update*()`                 | **Preferred.** Change choices/values/labels of existing inputs.|
| `renderUI()` + `uiOutput()` | Structure changes. Use `session$ns()` in modules.              |
| `insertUI()` / `removeUI()` | Surgical additions/removals to DOM.                            |
| `conditionalPanel()`        | Client-side show/hide (no server round-trip).                  |
## Reactive Data-Flow Idiom
```r
server <- function(input, output, session) {
  data_raw <- reactive({
    req(input$file)
    readr::read_csv(input$file$datapath)
  })
  data_filtered <- reactive({
    req(data_raw(), input$species)
    data_raw() |> dplyr::filter(species %in% input$species)
  }) |> bindCache(input$species)
  data_summary <- reactive({
    req(data_filtered())
    validate(need(nrow(data_filtered()) > 0, "No rows after filter."))
    data_filtered() |> dplyr::summarise(.by = species, mean_len = mean(sepal_length))
  })
  output$tbl <- renderTable(data_summary())
}
```

dplyr basics → **r-data-analysis**; this idiom captures *where* `req()`,
`validate()`, `bindCache()` go — Shiny-specific placement.
## Outputs Cheat Sheet
| Output    | Render fn           | Boundary for content/styling   |
|-----------|---------------------|--------------------------------|
| ggplot    | `renderPlot()`      | r-visualization                |
| plotly    | `renderPlotly()`    | r-visualization (interactive)  |
| DT        | `renderDT()`        | r-tables                       |
| reactable | `renderReactable()` | r-tables                       |

Cache plots: `renderPlot(...) |> bindCache(input$x, input$y)`. Hidden tabs: `outputOptions(output, "id", suspendWhenHidden = FALSE)`.
## Performance and JS Integration
```r
output$plot <- renderPlot({ create_expensive_plot(filtered_data()) }) |>
  bindCache(input$dataset, input$cyl)
# Async: library(promises); library(future); plan(multisession)
# JS: session$sendCustomMessage() (R -> JS), Shiny.setInputValue() (JS -> R)
```

See `references/reactivity-guide.md` for `debounce()` / `throttle()` and async.
## Testing
| Layer       | Tool                    | Use for                                              |
|-------------|-------------------------|------------------------------------------------------|
| Unit        | `shiny::testServer()`   | Module reactives, return-value contracts, edge cases |
| Integration | `shinytest2::AppDriver` | Full-app flows, snapshots, regression detection      |

```r
testServer(mod_filter_server, args = list(data = reactive(mtcars)), {
  session$setInputs(column = "mpg", range = c(20, 30))
  result <- session$getReturned()()
  expect_true(all(result$mpg >= 20 & result$mpg <= 30))
})
app <- shinytest2::AppDriver$new(app_dir = ".", name = "filter-test")
app$set_inputs(cyl = "6"); app$expect_values(); app$stop()
```

See `references/testing.md` for fixtures, CI patterns, snapshot review.
## Deployment
| Target              | Auth           | Scaling            | Regulated fit                 |
|---------------------|----------------|--------------------|-------------------------------|
| shinyapps.io        | Posit auth     | Per-app workers    | Low (public/SaaS only)        |
| Posit Connect       | LDAP/SAML/OIDC | Per-app processes  | High (validated environments) |
| Docker + ShinyProxy | OIDC/Keycloak  | Container per user | High (self-hosted, auditable) |
| Shiny Server (OSS)  | Reverse proxy  | Single process     | Medium (manual hardening)     |

Pin packages with `renv::snapshot()` before each deploy. `golem::add_dockerfile()`
for golem apps. See `references/deployment.md` for secrets, sizing, observability.
## Gotchas
| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `renderUI()` for simple input changes | Full UI rebuild is slow; loses input state | Use `update*()` (e.g., `updateSelectInput()`) |
| Missing `ns()` in module UI | Input IDs not namespaced; server cannot find them | Wrap every input/output ID with `ns()` |
| `reactiveVal()` inside `observe()` | New reactive value on every invalidation | Define outside observers |
| Missing `req()` for NULL inputs | NULL propagates and causes cryptic errors | Add `req(input$x)` at top of reactives |
| Forgetting `session$ns()` in module dynamic UI | `renderUI()` inside module makes un-namespaced IDs | Use `session$ns("id")` inside `renderUI()` |
| No `isolate()` in `observe()` | Reading multiple inputs causes infinite loops | Use `isolate()` on inputs you don't depend on |
| Side effects inside `reactive()` | Side effects fire unpredictably | Move to `observe()` / `observeEvent()` |
| Scope creep | Restructuring whole app to fix one reactive | Fix only the identified issue; minimal diff |
| teal data schema mismatch | `cdisc_data()` requires each domain wrapped in `cdisc_dataset()` with `keys` | Wrap each domain with `cdisc_dataset()` and `keys = c("STUDYID", "USUBJID")` |
| Async without promises | Long-running reactive blocks the entire session | `library(promises); library(future); plan(multisession)`; chain via the promise pipe `%...>%` from the `promises` package (NOT magrittr — the one place this project allows that token) |
## Examples
### Happy Path: Basic module with ns() wrapping
**Prompt:** "Create a reusable chart module with namespace-safe inputs."
```r
mod_chart_ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("metric"), "Metric", choices = c("mpg", "hp", "wt")),
    plotOutput(ns("plot"))
  )
}
mod_chart_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    output$plot <- renderPlot({
      req(input$metric)
      ggplot2::ggplot(data(), ggplot2::aes(x = .data[[input$metric]])) +
        ggplot2::geom_histogram(bins = 20)
    })
  })
}
app_server <- function(input, output, session) {
  raw <- reactive(mtcars)
  mod_chart_server("chart1", data = raw)
  mod_chart_server("chart2", data = raw)
}
```
### Edge Case: Dynamic UI in module needing session$ns()
**Prompt:** "My renderUI inside a module creates inputs that the server cannot find."
```r
# BAD — renderUI without session$ns(): IDs are not namespaced
mod_dynamic_server <- function(id, choices) {
  moduleServer(id, function(input, output, session) {
    output$controls <- renderUI({
      selectInput("dynamic_var", "Variable", choices = choices())
      # input$dynamic_var is NULL — ID not namespaced!
    })
  })
}
# GOOD — use session$ns() inside renderUI
mod_dynamic_server <- function(id, choices) {
  moduleServer(id, function(input, output, session) {
    output$controls <- renderUI({
      selectInput(session$ns("dynamic_var"), "Variable", choices = choices())
    })
    observe({ req(input$dynamic_var); message("Selected: ", input$dynamic_var) })
  })
}
```
### golem skeleton
```r
golem::create_golem("dashboard")
golem::add_module(name = "filter")
# R/app_server.R
app_server <- function(input, output, session) {
  filtered <- mod_filter_server("filter1", data = reactive(mtcars))
  observe(print(head(filtered())))
}
# R/app_ui.R uses bslib::page_sidebar() + mod_filter_ui("filter1")
```
### teal skeleton
```r
library(teal)
library(teal.modules.clinical)
adsl <- random.cdisc.data::cadsl
data <- cdisc_data(cdisc_dataset("ADSL", adsl, keys = c("STUDYID", "USUBJID")))
app <- init(
  data = data,
  modules = modules(
    tm_data_table(label = "ADSL table"),
    tm_t_summary(label = "Demographics", dataname = "ADSL",
                 arm_var = choices_selected("ARM"),
                 summarize_vars = choices_selected(c("AGE", "SEX", "RACE")))
  )
)
shinyApp(app$ui, app$server)
```

**More example prompts:**
- "Refactor this 400-line server function into Shiny modules."
- "My app updates the plot twice when I change the dropdown — fix the invalidation."
- "Convert this single-file app into a golem package with shinytest2 tests."
- "Build a teal dashboard showing demographics and AE summaries on ADSL/ADAE."
- "Deploy this golem app to Posit Connect with renv-locked dependencies."
