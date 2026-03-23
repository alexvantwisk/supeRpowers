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
  # reactive() — lazy computed value, cached
  filtered_data <- reactive({
    req(input$dataset)
    mtcars |> filter(cyl == input$cyl)
  })

  # reactiveVal() — mutable single value
  click_count <- reactiveVal(0)

  # observeEvent() — side effect on trigger
  observeEvent(input$increment, { click_count(click_count() + 1) })

  # bindEvent() — modern alternative to observeEvent

  filtered_result <- reactive({
    expensive_computation(input$params)
  }) |> bindEvent(input$go_button)

  # isolate() — read without taking dependency
  observe({
    message("Dataset: ", input$dataset)
    message("Cyl (no dep): ", isolate(input$cyl))
  })

  # req() — short-circuit on NULL/FALSE/empty
  output$plot <- renderPlot({
    req(filtered_data(), nrow(filtered_data()) > 0)
    plot(filtered_data()$mpg)
  })
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
# R/mod_filter.R
mod_filter_ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("column"), "Filter column", choices = NULL),
    sliderInput(ns("range"), "Range", min = 0, max = 100, value = c(0, 100))
  )
}

mod_filter_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    observe({
      cols <- data() |> select(where(is.numeric)) |> names()
      updateSelectInput(session, "column", choices = cols)
    })
    # Return filtered data as reactive
    reactive({
      req(input$column, input$range)
      data() |> filter(
        .data[[input$column]] >= input$range[1],
        .data[[input$column]] <= input$range[2]
      )
    })
  })
}

# Wire modules in app_server.R
app_server <- function(input, output, session) {
  raw_data <- reactive({ mtcars })
  filtered <- mod_filter_server("filter1", data = raw_data)
  mod_table_server("table1", data = filtered)
}
```

Read `references/modules-patterns.md` for inter-module communication, nested
modules, testing, and common patterns (CRUD, form, display).

---

## UI with bslib

```r
ui <- page_navbar(
  title = "Dashboard",
  theme = bs_theme(bootswatch = "flatly", primary = "#0073B7"),
  nav_panel("Overview",
    layout_columns(
      col_widths = c(4, 4, 4),
      value_box("Users", textOutput("n_users"), showcase = bsicons::bs_icon("people")),
      value_box("Revenue", textOutput("revenue"), showcase = bsicons::bs_icon("currency-dollar")),
      value_box("Growth", textOutput("growth"), showcase = bsicons::bs_icon("graph-up"))
    ),
    layout_columns(
      col_widths = c(8, 4),
      card(card_header("Trend"), plotOutput("trend_plot")),
      card(card_header("Top Items"), tableOutput("top_table"))
    )
  )
)
```

Key components: `page_sidebar()`, `page_navbar()`, `page_fillable()`,
`card()`, `value_box()`, `layout_columns()`, `accordion()`, `navset_card_tab()`.

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

## JavaScript Integration

Use `session$sendCustomMessage()` (R -> JS) and `Shiny.setInputValue()` (JS -> R)
for custom communication. Register handlers with `Shiny.addCustomMessageHandler()`.
For complex JS, use `htmltools::htmlDependency()` to manage external JS/CSS.

---

## Performance

```r
# bindCache — cache expensive computations by input keys
output$plot <- renderPlot({ create_expensive_plot(filtered_data()) }) |>
  bindCache(input$dataset, input$cyl)

# Async with promises + future
library(promises); library(future); plan(multisession)
output$result <- renderTable({ future_promise({ slow_computation(isolate(input$params)) }) })

# Dev tools
shiny::devmode()                    # auto-reload, enhanced logging
profvis::profvis({ runApp() })      # profile bottlenecks
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

### 1. Quick dashboard prototype
**Prompt:** "Create a Shiny dashboard showing mtcars data with sidebar filters
for cylinders and a scatter plot."

### 2. Module extraction
**Prompt:** "Refactor this 400-line server function into Shiny modules with
proper namespacing and inter-module communication."

### 3. Reactivity debugging
**Prompt:** "My Shiny app updates the plot twice when I change the dropdown.
Help me find and fix the unnecessary invalidation."

### 4. Production deployment
**Prompt:** "Convert this single-file Shiny app to a golem package with shinytest2 tests and Docker deployment."

### 5. Performance optimization
**Prompt:** "This Shiny app is slow when many users connect. Add caching and async processing for the expensive database query."
