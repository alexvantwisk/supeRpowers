---
name: r-shiny
description: >
  Use when building, structuring, testing, or deploying Shiny applications.
  Provides expert guidance on reactivity, modules, UI layout with bslib,
  production frameworks (golem, rhino), integration testing with shinytest2,
  and deployment to Posit Connect, shinyapps.io, or Docker.
  Triggers: Shiny, reactive, module, dashboard, golem, rhino, bslib,
  shinytest2, deployment, server, ui, app, observe, render.
  Do NOT use for standalone ggplot2 plots — use r-visualization instead.
  Do NOT use for Quarto interactive documents — use r-quarto instead.
---

# R Shiny

Comprehensive Shiny application development: reactivity, modules, UI, testing,
and deployment. All code uses base pipe `|>`, `<-` for assignment, and
tidyverse/shiny conventions.

**Lazy references:**
- Read `references/reactivity-guide.md` for deep reactivity patterns and debugging
- Read `references/modules-patterns.md` for module architecture and inter-module communication

**Agent dispatch:** Dispatch to **r-shiny-architect** agent for app structure
review and reactivity audit. If the agent is not yet available, provide
guidance inline.

---

## App Structure

| Structure | When to use |
|-----------|-------------|
| `app.R` single file | Prototypes, small apps (<500 lines) |
| `ui.R` + `server.R` + `global.R` | Medium apps |
| golem (`golem::create_golem()`) | **Default for production** — module conventions, tests, deployment |
| rhino (`rhino::init()`) | Enterprise — box modules, Sass, Cypress |

```r
# Minimal app.R
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

Use golem unless the team already uses rhino or needs box-style imports.

---

## Reactivity Fundamentals

| Type | Creates | Purpose | Lazy? |
|------|---------|---------|-------|
| `input$x` | Source | User input | N/A |
| `reactiveVal()` / `reactiveValues()` | Source | Mutable state | N/A |
| `reactive()` | Conductor | Computed value, cached | Yes |
| `observe()` / `observeEvent()` | Endpoint | Side effects | No |
| `render*()` | Endpoint | Output rendering | Yes |

```r
server <- function(input, output, session) {
  filtered_data <- reactive({ req(input$dataset); mtcars |> filter(cyl == input$cyl) })
  click_count <- reactiveVal(0)
  observeEvent(input$increment, { click_count(click_count() + 1) })
  # bindEvent() — modern alternative to observeEvent
  filtered_result <- reactive({ expensive_computation(input$params) }) |>
    bindEvent(input$go_button)
  # isolate() — read without taking dependency
  observe({ message("Dataset: ", input$dataset, " Cyl: ", isolate(input$cyl)) })
  # req() — short-circuit on NULL/FALSE/empty
  output$plot <- renderPlot({ req(filtered_data()); plot(filtered_data()$mpg) })
}
```

**Decision tree:**
- Computed value for others? -> `reactive()`
- Side effect? -> `observe()` / `observeEvent()`
- Mutable state? -> `reactiveVal()` (single) or `reactiveValues()` (multiple)
- Delay until button? -> `bindEvent()`
- Read without dependency? -> `isolate()`
- Input might be NULL? -> `req()`

Read `references/reactivity-guide.md` for anti-patterns, debugging, and
advanced patterns (bindCache, debounce, throttle).

---

## Modules

Modules encapsulate UI + server logic with namespaced IDs.

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

Read `references/modules-patterns.md` for inter-module communication, nested
modules, testing, and common patterns.

---

## UI with bslib

```r
ui <- page_navbar(
  title = "Dashboard",
  theme = bs_theme(bootswatch = "flatly", primary = "#0073B7"),
  nav_panel("Overview",
    layout_columns(col_widths = c(4, 4, 4),
      value_box("Users", textOutput("n_users")),
      value_box("Revenue", textOutput("revenue")),
      value_box("Growth", textOutput("growth"))
    ),
    layout_columns(col_widths = c(8, 4),
      card(card_header("Trend"), plotOutput("trend_plot")),
      card(card_header("Top Items"), tableOutput("top_table"))
    )
  )
)
```

Key: `page_sidebar()`, `page_navbar()`, `page_fillable()`, `card()`,
`value_box()`, `layout_columns()`, `accordion()`, `navset_card_tab()`.

---

## Dynamic UI

| Method | When to use |
|--------|-------------|
| `update*()` | **Preferred.** Change choices/values/labels of existing inputs. |
| `renderUI()` + `uiOutput()` | Structure changes. Use `session$ns()` in modules. |
| `insertUI()` / `removeUI()` | Surgical additions/removals to DOM. |
| `conditionalPanel()` | Client-side show/hide (no server round-trip). |

---

## Testing

```r
# Module unit tests with testServer
test_that("filter module returns filtered data", {
  testServer(mod_filter_server, args = list(data = reactive(mtcars)), {
    session$setInputs(column = "mpg", range = c(20, 30))
    result <- session$getReturned()()
    expect_true(all(result$mpg >= 20 & result$mpg <= 30))
  })
})

# Integration tests with shinytest2
test_that("app loads and filters work", {
  app <- AppDriver$new(app_dir = ".", name = "filter-test")
  app$set_inputs(cyl = "6")
  app$expect_values()
  app$stop()
})
```

Strategy: unit test modules with `testServer()`, integration test full app
with `shinytest2::AppDriver`, snapshot outputs with `app$expect_values()`.

---

## Performance and JS Integration

```r
# bindCache — cache expensive computations by input keys
output$plot <- renderPlot({ create_expensive_plot(filtered_data()) }) |>
  bindCache(input$dataset, input$cyl)

# Async: library(promises); library(future); plan(multisession)
# JS: session$sendCustomMessage() (R->JS), Shiny.setInputValue() (JS->R)
```

---

## Deployment

| Target | Command | Notes |
|--------|---------|-------|
| shinyapps.io | `rsconnect::deployApp()` | Managed hosting, free tier |
| Posit Connect | `rsconnect::deployApp(server = "...")` | Enterprise |
| ShinyProxy | Docker + ShinyProxy config | Open source, multi-user |
| Docker | `golem::add_dockerfile()` | Portable containers |

Always use `renv` for reproducible deployments. Pin all package versions.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `renderUI()` for simple input changes | Full UI rebuild is slow; loses input state | Use `update*()` functions (e.g., `updateSelectInput()`) instead |
| Missing `ns()` in module UI | Input IDs are not namespaced; server cannot find them | Wrap every input/output ID with `ns()` in module UI functions |
| `reactiveVal()` inside `observe()` | Creates a new reactive value on every invalidation; previous value lost | Define `reactiveVal()` or `reactiveValues()` outside observers |
| Missing `req()` for NULL inputs | `NULL` inputs propagate and cause cryptic downstream errors | Add `req(input$x)` at the start of reactive expressions |
| Forgetting `session$ns()` in module server dynamic UI | `renderUI()` inside a module generates un-namespaced IDs | Use `session$ns("id")` when building UI in the server function |
| No `isolate()` in `observe()` | Reading multiple inputs without isolation causes infinite reactive loops | Use `isolate()` on inputs you want to read but not depend on |
| Side effects inside `reactive()` | `reactive()` is for computed values; side effects fire unpredictably | Move side effects (DB writes, logging, file I/O) to `observe()` or `observeEvent()` |
| Scope creep | Claude restructures entire app when asked to fix one reactive | Fix only the identified issue; show minimal diff |

---

## Examples

### Happy Path: Basic module with ns() wrapping

**Prompt:** "Create a reusable chart module with namespace-safe inputs."

```r
# Module UI — every ID wrapped in ns()
mod_chart_ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("metric"), "Metric", choices = c("mpg", "hp", "wt")),
    plotOutput(ns("plot"))
  )
}

# Module server — returns nothing, renders output
mod_chart_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    output$plot <- renderPlot({
      req(input$metric)
      ggplot2::ggplot(data(), ggplot2::aes(x = .data[[input$metric]])) +
        ggplot2::geom_histogram(bins = 20)
    })
  })
}

# Wire in app — each call creates an independent instance
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

**More example prompts:**
- "Refactor this 400-line server function into Shiny modules"
- "My app updates the plot twice when I change the dropdown — fix the invalidation"
- "Convert this single-file app to a golem package with shinytest2 tests"
