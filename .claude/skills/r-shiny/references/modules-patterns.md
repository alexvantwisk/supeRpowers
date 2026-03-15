# Module Patterns

Architecture patterns for Shiny modules: namespacing, communication,
testing, and common reusable patterns. All code uses base pipe `|>`,
`<-` for assignment, and snake_case naming.

---

## Basic Module Pattern

Every module has two functions: UI and server.

```r
# R/mod_summary.R

#' Summary Module UI
#' @param id Module namespace ID
mod_summary_ui <- function(id) {
  ns <- NS(id)
  tagList(
    selectInput(ns("variable"), "Variable", choices = NULL),
    verbatimTextOutput(ns("stats"))
  )
}

#' Summary Module Server
#' @param id Module namespace ID
#' @param data Reactive data frame
mod_summary_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    observe({
      req(data())
      updateSelectInput(session, "variable", choices = names(data()))
    })

    output$stats <- renderPrint({
      req(input$variable)
      summary(data()[[input$variable]])
    })
  })
}
```

**Usage in app:**
```r
# UI
mod_summary_ui("summary1")

# Server
mod_summary_server("summary1", data = raw_data)
```

---

## NS() Namespacing

`NS(id)` creates a function `ns()` that prefixes input IDs with the
module's namespace.

```r
ns <- NS("filter1")
ns("column")    # returns "filter1-column"
ns("range")     # returns "filter1-range"
```

### How it works

- UI function wraps all input/output IDs with `ns()`
- `moduleServer()` automatically strips the prefix when reading `input$*`
- This prevents ID collisions when the same module is used multiple times

### Common mistakes

```r
# BAD: forgot ns() — input ID is global, will collide
mod_filter_ui <- function(id) {
  ns <- NS(id)
  selectInput("column", "Column", choices = NULL)  # WRONG: no ns()
}

# GOOD
mod_filter_ui <- function(id) {
  ns <- NS(id)
  selectInput(ns("column"), "Column", choices = NULL)
}

# BAD: forgot ns() in renderUI inside module
output$dynamic <- renderUI({
  numericInput("threshold", "Threshold", value = 0)  # WRONG
})

# GOOD: use session$ns inside server-side UI generation
output$dynamic <- renderUI({
  numericInput(session$ns("threshold"), "Threshold", value = 0)
})
```

**Rule:** Every `*Input()`, `*Output()`, and `actionButton()` ID in a module
UI must be wrapped with `ns()`. Inside `renderUI()` in server, use
`session$ns()`.

---

## Returning Values from Modules

### Return a single reactive

```r
mod_filter_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    # Return filtered data as last expression
    reactive({
      req(input$column, input$range)
      data() |>
        filter(
          .data[[input$column]] >= input$range[1],
          .data[[input$column]] <= input$range[2]
        )
    })
  })
}

# Parent captures the return value
filtered <- mod_filter_server("filter1", data = raw_data)
# filtered is a reactive — call filtered() to get value
```

### Return a list of reactives

```r
mod_form_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    is_valid <- reactive({
      nchar(input$name) > 0 && input$age > 0
    })

    form_data <- reactive({
      req(is_valid())
      list(name = input$name, age = input$age)
    })

    # Return named list of reactives
    list(
      data = form_data,
      valid = is_valid
    )
  })
}

# Parent destructures the return
form <- mod_form_server("user_form")
# form$data() returns the form data
# form$valid() returns TRUE/FALSE
```

---

## Inter-Module Communication Patterns

### Pattern 1: Parent passes reactive to child (argument)

The most common pattern. Parent owns the data, children receive it.

```r
app_server <- function(input, output, session) {
  raw_data <- reactive({ read_csv("data.csv") })

  # Parent passes data reactive to both children
  filtered <- mod_filter_server("filter1", data = raw_data)
  mod_table_server("table1", data = filtered)
  mod_plot_server("plot1", data = filtered)
}
```

### Pattern 2: Child returns reactive to parent (return value)

Child computes something, parent wires it to other children.

```r
app_server <- function(input, output, session) {
  # Child returns selected row
  selected <- mod_table_server("table1", data = raw_data)

  # Parent passes selection to detail module
  mod_detail_server("detail1", selected_row = selected)
}
```

### Pattern 3: Shared reactiveValues (R6 store)

For complex apps where many modules need shared mutable state.

```r
# R/app_store.R
AppStore <- R6::R6Class("AppStore",
  public = list(
    state = NULL,
    initialize = function() {
      self$state <- reactiveValues(
        selected_ids = character(),
        filters = list(),
        theme = "light"
      )
    },
    set_selection = function(ids) {
      self$state$selected_ids <- ids
    },
    get_selection = function() {
      self$state$selected_ids
    }
  )
)

# app_server.R
app_server <- function(input, output, session) {
  store <- AppStore$new()
  mod_sidebar_server("sidebar", store = store)
  mod_main_server("main", store = store)
}

# Inside any module
mod_sidebar_server <- function(id, store) {
  moduleServer(id, function(input, output, session) {
    observeEvent(input$select, {
      store$set_selection(input$select)
    })
  })
}
```

**Use sparingly.** Prefer patterns 1 and 2 for simple apps. The R6 store
is for apps with 5+ modules sharing complex state.

### Pattern 4: Event-driven trigger

For "notify sibling" without shared state.

```r
mod_editor_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    save_trigger <- reactiveVal(0)

    observeEvent(input$save, {
      write_csv(data(), "output.csv")
      save_trigger(save_trigger() + 1)  # increment to trigger
    })

    # Return the trigger
    list(data = data, saved = save_trigger)
  })
}

# Parent wires trigger to another module
app_server <- function(input, output, session) {
  editor <- mod_editor_server("editor", data = raw_data)

  # Refresh module reacts to save trigger
  mod_refresh_server("status", trigger = editor$saved)
}
```

---

## Nested Modules

Modules can contain other modules. Namespaces chain automatically.

```r
# Parent module contains child modules
mod_dashboard_ui <- function(id) {
  ns <- NS(id)
  tagList(
    mod_filter_ui(ns("filter")),    # ID becomes "dashboard1-filter"
    mod_table_ui(ns("table")),      # ID becomes "dashboard1-table"
    mod_plot_ui(ns("plot"))         # ID becomes "dashboard1-plot"
  )
}

mod_dashboard_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    filtered <- mod_filter_server("filter", data = data)
    mod_table_server("table", data = filtered)
    mod_plot_server("plot", data = filtered)
  })
}

# App level
app_server <- function(input, output, session) {
  raw_data <- reactive({ mtcars })
  mod_dashboard_server("dashboard1", data = raw_data)
}
```

**Namespace chain:** `"dashboard1"` -> `"dashboard1-filter"` ->
`"dashboard1-filter-column"`. Each level adds its prefix.

**Important:** In the parent module's UI function, wrap child module IDs
with `ns()`. In the parent module's server function, use bare strings
(moduleServer handles the namespace).

---

## Module Testing with testServer()

### Basic test

```r
test_that("filter module filters data correctly", {
  testServer(mod_filter_server, args = list(
    data = reactive(mtcars)
  ), {
    # Set inputs
    session$setInputs(column = "mpg", range = c(20, 30))

    # Get return value
    result <- session$getReturned()()

    # Assertions
    expect_true(all(result$mpg >= 20))
    expect_true(all(result$mpg <= 30))
    expect_lt(nrow(result), nrow(mtcars))
  })
})
```

### Testing returned reactives

```r
test_that("form module returns valid data", {
  testServer(mod_form_server, {
    session$setInputs(name = "", age = 0)
    form <- session$getReturned()
    expect_false(form$valid())

    session$setInputs(name = "Alice", age = 30)
    expect_true(form$valid())
    expect_equal(form$data()$name, "Alice")
  })
})
```

### Testing with reactive arguments

```r
test_that("display module reacts to data changes", {
  data_val <- reactiveVal(mtcars)

  testServer(mod_display_server, args = list(data = data_val), {
    expect_equal(nrow(session$getReturned()()), 32)

    # Simulate parent changing data
    data_val(mtcars |> filter(cyl == 4))
    session$flushReact()

    expect_equal(nrow(session$getReturned()()), 11)
  })
})
```

---

## golem Conventions

golem enforces consistent module naming and file structure.

```
R/
  app_config.R         # golem config
  app_server.R         # main server
  app_ui.R             # main UI
  mod_filter.R         # mod_filter_ui() + mod_filter_server()
  mod_table.R          # mod_table_ui() + mod_table_server()
  mod_plot.R           # mod_plot_ui() + mod_plot_server()
  utils_helpers.R      # shared utilities
  fct_data.R           # business logic (non-reactive)
```

**Naming convention:** `mod_*_ui()` and `mod_*_server()` in `R/mod_*.R`.
Business logic (non-reactive) goes in `R/fct_*.R`. Utilities in
`R/utils_*.R`.

**Add a module:**
```r
golem::add_module(name = "filter")
# Creates R/mod_filter.R with boilerplate
```

**Add JS/CSS:**
```r
golem::add_js_file("custom")    # inst/app/www/custom.js
golem::add_css_file("styles")   # inst/app/www/styles.css
```

---

## Common Module Patterns

### CRUD Module

Handles create, read, update, delete for a data entity.

```r
mod_crud_server <- function(id, store) {
  moduleServer(id, function(input, output, session) {
    # Read
    items <- reactive({ store$get_all() })

    output$table <- renderDT({ items() })

    # Create
    observeEvent(input$create, {
      new_item <- list(name = input$name, value = input$value)
      store$insert(new_item)
    })

    # Update
    observeEvent(input$update, {
      store$update(input$selected_id, list(
        name = input$edit_name, value = input$edit_value
      ))
    })

    # Delete
    observeEvent(input$delete, {
      req(input$selected_id)
      store$delete(input$selected_id)
    })

    items
  })
}
```

### Filter Module

Accepts data, returns filtered subset.

```r
mod_filter_server <- function(id, data) {
  moduleServer(id, function(input, output, session) {
    observe({
      choices <- data() |> select(where(is.numeric)) |> names()
      updateSelectInput(session, "column", choices = choices)
    })

    observe({
      req(input$column)
      vals <- data()[[input$column]]
      updateSliderInput(session, "range",
        min = min(vals, na.rm = TRUE),
        max = max(vals, na.rm = TRUE),
        value = range(vals, na.rm = TRUE)
      )
    })

    reactive({
      req(input$column, input$range)
      data() |>
        filter(
          .data[[input$column]] >= input$range[1],
          .data[[input$column]] <= input$range[2]
        )
    })
  })
}
```

### Display Module

Accepts a data reactive, renders output. No return value.

```r
mod_display_server <- function(id, data, title = reactive("Results")) {
  moduleServer(id, function(input, output, session) {
    output$title <- renderText({ title() })
    output$count <- renderText({ paste(nrow(data()), "rows") })
    output$table <- renderDT({
      req(data())
      datatable(data(), options = list(pageLength = 10))
    })
  })
}
```

### Form Module

Collects input, validates, returns data on submit.

```r
mod_form_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    is_valid <- reactive({
      nchar(input$name) >= 2 &&
        !is.na(input$email) &&
        grepl("@", input$email)
    })

    # Visual feedback
    observe({
      if (is_valid()) {
        shinyjs::enable("submit")
      } else {
        shinyjs::disable("submit")
      }
    })

    submitted <- reactiveVal(NULL)

    observeEvent(input$submit, {
      req(is_valid())
      submitted(list(
        name = input$name,
        email = input$email,
        timestamp = Sys.time()
      ))
    })

    # Return: reactive that is NULL until submitted
    list(
      data = submitted,
      valid = is_valid
    )
  })
}
```

---

## Communication Pattern Summary

| Scenario | Pattern | Complexity |
|----------|---------|------------|
| Parent -> Child data flow | Pass reactive as argument | Low |
| Child -> Parent result | Return reactive | Low |
| Sibling A -> Sibling B | Return from A, pass to B via parent | Medium |
| Many modules, shared state | R6 store with reactiveValues | High |
| Event notification | reactiveVal trigger counter | Low |
| Dynamic module count | Module + `insertUI()`/`removeUI()` | High |
