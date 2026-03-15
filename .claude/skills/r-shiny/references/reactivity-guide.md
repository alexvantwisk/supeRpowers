# Reactivity Guide

Deep patterns for Shiny's reactive programming model. All code uses
base pipe `|>`, `<-` for assignment, and snake_case naming.

---

## Reactive Graph Mental Model

Shiny's reactivity is a **directed acyclic graph (DAG)**:

```
Sources           Conductors         Endpoints
-----------       -----------        ----------
input$x      -->  reactive()    -->  output$y (render*)
reactiveVal()     reactive()    -->  observe()
reactiveValues()                -->  observeEvent()
```

- **Sources** produce values: `input$*`, `reactiveVal()`, `reactiveValues()`
- **Conductors** compute derived values: `reactive()` — lazy, cached
- **Endpoints** consume values: `render*()`, `observe()`, `observeEvent()`

**Key rule:** Endpoints pull from conductors/sources. When a source
invalidates, only the dependent conductors and endpoints re-execute.

---

## reactive() vs observe() vs observeEvent()

### Decision tree

1. Does it **return a value** used by other reactives/outputs?
   -> `reactive()`

2. Does it perform a **side effect** (DB write, file save, notification, log)?
   -> Is it triggered by a **specific event** (button click, single input)?
      - Yes -> `observeEvent(trigger, { ... })`
      - No (runs whenever any dependency changes) -> `observe({ ... })`

3. Do you need `reactive()` but **only on a trigger**?
   -> `reactive({ ... }) |> bindEvent(trigger)`

### reactive() — lazy computed value

```r
# Cached until input$cyl changes. Only re-runs when accessed AND invalid.
filtered <- reactive({
  req(input$cyl)
  mtcars |> filter(cyl == input$cyl)
})

# Multiple outputs can depend on the same reactive — computed only once
output$table <- renderTable({ filtered() })
output$plot <- renderPlot({ plot(filtered()$mpg, filtered()$wt) })
```

### observe() — eager side effect

```r
# Runs whenever ANY dependency changes. No return value.
observe({
  # Logs every time input$dataset or input$cyl changes
  log_info("User selected dataset={input$dataset}, cyl={input$cyl}")
})
```

### observeEvent() — controlled side effect

```r
# Only runs when input$save is clicked
observeEvent(input$save, {
  write_csv(filtered_data(), "output/filtered.csv")
  showNotification("Data saved!", type = "message")
})

# ignoreNULL = FALSE to also fire on NULL (e.g., app startup)
observeEvent(input$tab, {
  update_sidebar(input$tab)
}, ignoreNULL = FALSE)

# ignoreInit = TRUE to skip first execution
observeEvent(input$refresh, {
  fetch_new_data()
}, ignoreInit = TRUE)
```

---

## Isolation Patterns

### isolate() — read without dependency

```r
observe({
  # Takes dependency on input$dataset only
  data <- get(input$dataset, "package:datasets")
  # Reads input$n_rows but does NOT re-trigger when n_rows changes
  n <- isolate(input$n_rows)
  output$preview <- renderTable({ head(data, n) })
})
```

### bindEvent() — modern replacement for observeEvent pattern

```r
# Reactive that only updates when button is clicked
expensive_result <- reactive({
  run_slow_model(input$param_a, input$param_b, input$param_c)
}) |> bindEvent(input$run_model)

# Can also bind renders to events
output$plot <- renderPlot({
  plot(expensive_result())
}) |> bindEvent(input$show_plot)
```

`bindEvent()` is composable and more flexible than `observeEvent()`.
Prefer it for new code.

### debounce() and throttle()

```r
# debounce — wait until input stops changing for N ms
search_term <- reactive({ input$search }) |> debounce(300)

# throttle — execute at most every N ms
mouse_pos <- reactive({ input$mouse }) |> throttle(100)

# Use debounce for text input (wait for typing to stop)
# Use throttle for continuous input (mouse, slider dragging)
```

### reactiveTimer() — periodic invalidation

```r
# Poll every 5 seconds
auto_refresh <- reactiveTimer(5000)

live_data <- reactive({
  auto_refresh()  # takes dependency on timer
  fetch_from_database()
})
```

---

## reactiveVal() vs reactiveValues()

### reactiveVal() — single mutable value

```r
counter <- reactiveVal(0)
counter()        # read: returns 0
counter(5)       # write: sets to 5

# Common: accumulate state
observeEvent(input$increment, {
  counter(counter() + 1)
})
```

### reactiveValues() — named list of mutable values

```r
state <- reactiveValues(
  selected_ids = character(),
  filter_active = FALSE,
  last_updated = Sys.time()
)

state$selected_ids               # read
state$selected_ids <- c("a", "b") # write

# Caution: individual fields are reactive
observe({
  # Re-runs when filter_active changes (not when selected_ids changes)
  if (state$filter_active) {
    showNotification("Filter is on")
  }
})
```

**When to use which:**
- Single value that changes -> `reactiveVal()`
- Multiple related values -> `reactiveValues()`
- Return from module -> `reactiveVal()` or `reactive()` (not `reactiveValues()`)

---

## Anti-Patterns and Fixes

### 1. Reactive spaghetti

**Problem:** Too many interdependent reactives creating a tangled graph.

```r
# BAD: chain of reactives that all depend on each other
a <- reactive({ input$x + 1 })
b <- reactive({ a() * 2 })
c <- reactive({ b() + a() })
d <- reactive({ c() - b() + a() })
```

**Fix:** Combine related computations into fewer, well-named reactives.

```r
# GOOD: one reactive with clear purpose
processed_data <- reactive({
  x <- input$x + 1
  scaled <- x * 2
  list(value = scaled + x, adjusted = scaled + x - scaled + x)
})
```

### 2. Unnecessary invalidation

**Problem:** Reading reactive values you do not actually need.

```r
# BAD: output re-renders when input$title changes even though title
# is only used in the plot title (minor visual change triggers full re-render)
output$table <- renderTable({
  message("Title is: ", input$title)  # unnecessary dependency!
  head(mtcars, input$n_rows)
})
```

**Fix:** Use `isolate()` for values you want to read but not depend on.

```r
output$table <- renderTable({
  message("Title is: ", isolate(input$title))
  head(mtcars, input$n_rows)
})
```

### 3. observe() writing to output

**Problem:** Using `observe()` to assign output instead of `render*()`.

```r
# BAD: loses Shiny's lazy evaluation and caching
observe({
  output$table <- renderTable({ head(mtcars, input$n) })
})
```

**Fix:** Use `render*()` directly.

```r
# GOOD
output$table <- renderTable({ head(mtcars, input$n) })
```

### 4. Nested observe() calls

**Problem:** Creating observers inside observers — accumulates observers on
each trigger, causing memory leaks and repeated execution.

```r
# BAD: creates a new observer every time input$dataset changes
observe({
  data <- get(input$dataset, "package:datasets")
  observe({  # NEW observer created each time!
    output$summary <- renderPrint({ summary(data) })
  })
})
```

**Fix:** Use `reactive()` for data, `render*()` for output.

```r
# GOOD
selected_data <- reactive({ get(input$dataset, "package:datasets") })
output$summary <- renderPrint({ summary(selected_data()) })
```

### 5. Large reactiveValues as catch-all state

**Problem:** One giant `reactiveValues()` holding all app state, causing
unrelated outputs to invalidate together.

```r
# BAD
state <- reactiveValues(data = NULL, filters = list(), theme = "light",
                         selected_row = NULL, modal_open = FALSE)
```

**Fix:** Use separate `reactiveVal()` for unrelated state.

```r
# GOOD
app_data <- reactiveVal(NULL)
selected_row <- reactiveVal(NULL)
modal_open <- reactiveVal(FALSE)
```

---

## Debugging Reactivity

### Enable reactlog

```r
# Before running app
reactlog::reactlog_enable()
options(shiny.reactlog = TRUE)

# Run app, interact, then press Cmd+F3 (Mac) or Ctrl+F3 (Windows)
# Or after stopping:
shiny::reactlogShow()
```

The reactive graph visualization shows:
- Which reactives are connected
- Execution order and timing
- Which invalidations trigger which re-computations

### Debugging tips

```r
# Add browser() inside reactive for step-through debugging
filtered <- reactive({
  browser()  # pauses here in RStudio

  mtcars |> filter(cyl == input$cyl)
})

# Trace reactive execution
observe({
  message("[DEBUG] filtered() has ", nrow(filtered()), " rows")
})

# shiny::devmode() for enhanced error messages
shiny::devmode()
```

### Common symptoms and causes

| Symptom | Likely cause |
|---------|-------------|
| Output updates too often | Unnecessary dependency — use `isolate()` |
| Output never updates | Missing dependency — forgot to call reactive |
| App hangs on startup | Circular dependency in reactives |
| Memory grows over time | Nested `observe()` creating new observers |
| Stale data displayed | `req()` short-circuiting silently |

---

## Performance Patterns

### bindCache() — server-side caching

```r
# Cache plot by input values — identical inputs return cached result
output$plot <- renderPlot({
  create_expensive_plot(input$dataset, input$method)
}) |> bindCache(input$dataset, input$method)

# Cache reactive computation
model_result <- reactive({
  fit_model(filtered_data(), input$formula)
}) |> bindCache(input$dataset, input$cyl, input$formula)

# Custom cache (e.g., disk cache for large apps)
shinyOptions(cache = cachem::cache_disk("./app-cache"))
```

### req() short-circuiting

```r
# Prevents downstream computation when inputs are not ready
filtered <- reactive({
  req(input$dataset)                    # NULL check
  req(input$min_val < input$max_val)    # logical condition
  req(nchar(input$search) >= 3)         # minimum input length
  perform_filter(input$dataset, input$min_val, input$max_val)
})
```

`req()` silently stops reactive execution without error — downstream
outputs show nothing rather than erroring.

### Rate limiting for text/continuous inputs

```r
# User types in search box — wait 500ms after last keystroke
search_query <- reactive({ input$search }) |> debounce(500)

# Use debounced value in downstream reactives
search_results <- reactive({
  req(nchar(search_query()) >= 2)
  search_database(search_query())
})
```

This prevents expensive computations from firing on every keystroke.
