# Shiny Integration Template

Guidance for documenting Shiny-specific features when generating a skill from
an R package that includes Shiny components (modules, UI functions, reactive
bindings).

---

## When to Create This File

Create `references/shiny-integration.md` in the generated skill when the
package inventory shows any of:
- Shiny module functions (`*UI()` / `*Server()` or `*_ui()` / `*_server()`)
- Functions returning `shiny.tag` or `htmltools::tag` objects
- Reactive binding helpers or custom input/output bindings
- An `inst/shiny-examples/` directory

---

## Template Structure

```markdown
# {package-name} Shiny Integration

## Module Functions

| Module | UI Function | Server Function |
|--------|-------------|-----------------|
| {name} | `{name}_ui(id)` | `{name}_server(id, ...)` |

### {module_name} Module

UI: `{module_name}_ui(id, label = "Default")`
Server: `{module_name}_server(id, data_reactive)`

\```r
# In app UI
{module_name}_ui("my_module", label = "Select Data")

# In app server
{module_name}_server("my_module", data_reactive = reactive(filtered_data()))
\```

## UI Components

| Function | Returns | Use When |
|----------|---------|----------|
| `pkg_button()` | `shiny.tag` | Need a styled action button |
| `pkg_card()` | `shiny.tag` | Wrapping content in a card layout |

## Reactive Patterns

### Pattern: Connecting Package Output to Shiny Reactives

\```r
server <- function(input, output, session) {
  processed <- reactive({
    req(input$data_file)
    pkg_process(input$data_file$datapath)
  })

  output$result <- renderTable({
    pkg_summarize(processed())
  })
}
\```
```

---

## Key Documentation Points

1. **Module namespace** — document whether modules use `NS(id)` correctly
   and whether they expect namespaced IDs from the caller
2. **Reactive inputs** — which server functions expect reactive values vs
   plain values as arguments
3. **Return values** — what each server function returns (reactive, observer,
   or NULL for side-effect-only modules)
4. **CSS/JS dependencies** — whether the package requires `useShinyjs()`,
   custom CSS, or JavaScript setup in the UI

---

## Gotchas for Shiny Components

| Trap | Fix |
|------|-----|
| Forgetting `NS(id)` in module UI | Always wrap input/output IDs with `ns()` inside module UI functions |
| Passing non-reactive to a module expecting reactive | Wrap with `reactive()`: `module_server("id", reactive(data))` |
| Module output not rendering | Check that the module server returns the reactive, not just computes it |
| Missing CSS/JS dependencies | Add required `use*()` call in UI (e.g., `shinyjs::useShinyjs()`) |
