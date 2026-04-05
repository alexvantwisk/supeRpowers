# Eval: r-shiny

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When generating reactive code, does the skill use `observeEvent()` (not bare `observe()`) for responding to user actions like button clicks?
2. Does the skill avoid storing `reactiveValues` or `reactive()` expressions in the global environment or package-level scope?
3. When asked to create a standalone ggplot2 figure with no Shiny context, does the skill defer to r-visualization?
4. When asked to debug a Shiny app crash (e.g., traceback interpretation), does the skill defer to r-debugging?
5. Does the skill use Shiny modules (`moduleServer`) rather than monolithic server functions when the app has more than one logical component?
6. When generating file upload handling code, does the skill validate file type and size before processing?
7. Does the skill use `|>` and `<-` exclusively (never `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "Create a Shiny app with a sidebar for filtering iris data by species and a main panel showing a scatter plot of Sepal.Length vs Sepal.Width."
- "Add a download button to my Shiny app that exports the currently filtered data as CSV."

### Edge Cases

- "I have a Shiny app where Module A produces a selected row ID and Module B needs to display details for that row. How should I wire the communication?" (deeply nested module communication -- must use returned reactive values from moduleServer, not global reactiveValues)
- "Add a file upload widget that accepts only .csv and .xlsx files under 10MB, validates column names, and shows a preview table." (file upload with validation -- must check file extension, size, and structure before rendering)
- "Users report that one user's filter selection sometimes appears in another user's session. What could cause this?" (cross-session reactivity -- must identify global mutable state as the cause, recommend session-scoped reactiveValues)

### Adversarial Cases

- "Create a ggplot2 bar chart comparing mean values across groups with error bars and a custom color palette." (no Shiny context -- must defer to r-visualization, not wrap in renderPlot unnecessarily)
- "Build a Quarto document with interactive widgets that let readers filter a dataset and see updated plots." (Quarto interactive doc -- must defer to r-quarto, not build a full Shiny app)
- "My Shiny app crashes on startup with 'Error in .getReactiveEnvironment()$currentContext()'. Help me debug this." (debugging task -- must defer to r-debugging for traceback and root cause analysis)

### Boundary Tests

- "Make a publication-quality faceted scatter plot with custom theme and annotation." (boundary -> r-visualization)
- "Create a Quarto dashboard with tabsets and OJS interactive cells." (boundary -> r-quarto)
- "My app throws 'cannot coerce type closure to character' deep in a render function. Walk me through diagnosing this." (boundary -> r-debugging)

## Success Criteria

- Reactive code MUST use `observeEvent()` for discrete user actions (button clicks, input changes with `ignoreInit`); bare `observe()` is only acceptable for continuous side effects with explicit documentation of why.
- Module code MUST use `moduleServer()` with proper namespacing (`ns <- NS(id)`); any app with 2+ logical components that uses a monolithic server function is a failure.
- File upload handlers MUST validate at least file extension and size before processing content.
- Cross-session state bugs MUST be diagnosed as global mutable state; the fix MUST involve session-scoped `reactiveValues` or similar isolation.
- Standalone visualization prompts with zero Shiny context MUST defer to r-visualization; wrapping a non-interactive request in `renderPlot` is a failure.
- Quarto interactive document requests MUST defer to r-quarto; generating a full Shiny `app.R` when the user asked for a Quarto doc is a failure.
- Crash debugging MUST defer to r-debugging; the skill may note the error is reactivity-related but must NOT attempt full root-cause debugging inline.
- All generated R code MUST use `|>`, `<-`, snake_case, and double quotes.
- Generated apps MUST NOT place `reactive()` or `reactiveValues()` calls outside of `server` or `moduleServer` functions.
