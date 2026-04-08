---
name: r-cmd-shiny-app
description: >
  Use when starting a new Shiny application. Orchestrates r-project-setup,
  r-shiny, and r-tdd skills with r-shiny-architect and r-code-reviewer agents
  through a guided scaffold-module-wire-test-review workflow. Invoke as
  /r-cmd-shiny-app.
  Triggers: new Shiny app, build dashboard, start Shiny, create Shiny,
  scaffold app, new dashboard, build interactive app.
  Do NOT use for Shiny API reference — use r-shiny instead.
  Do NOT use for project scaffolding without Shiny — use r-project-setup instead.
---

# Shiny App

Guided workflow: scaffold, design modules, wire reactivity, test, review.

## Prerequisites

- Clear requirements for what the app should do (inputs, outputs, user flows)
- Deployment target identified (local, shinyapps.io, Posit Connect, Docker)
- Decision on framework: golem (recommended for production), rhino, or basic Shiny

## Steps

### Step 1: Scaffold
**Skill:** `r-project-setup`
**Action:** Initialize project structure with chosen framework. For golem: `golem::create_golem("appname")`. For rhino: `rhino::init("appname")`. For basic: create `app.R` with `renv::init()`.
**Gate:** Project structure created. App runs with placeholder UI (`shiny::runApp()`).

### Step 2: Module design
**Skill:** `r-shiny`
**Action:** Decompose requirements into modules. Create `mod_*` files (golem: `golem::add_module("name")`, rhino: `app/view/name.R`). Each module gets UI and server functions with clear input/output contracts.
**Gate:** Module files created. Each module has documented inputs and outputs.

### Step 3: Wire reactivity
**Skill:** `r-shiny`
**Action:** Connect modules in the main server. Set up reactive data flow — shared reactive values, module communication via return values. Implement business logic.
**Gate:** App runs with functional reactivity. User can interact with all modules.

### Step 4: Test
**Skill:** `r-tdd`
**Action:** Write shinytest2 tests for critical user flows. Test module server functions with `testServer()`. Test reactive logic in isolation.
**Gate:** Tests pass. Key user interactions covered.

### Step 5: Architecture review
**Agent:** `r-shiny-architect` → escalate to `r-code-reviewer` for implementation-level code quality issues
**Action:** Review module structure, reactivity patterns, performance (avoid reactive invalidation storms), and security (input validation, auth).
**Gate:** No CRITICAL findings. Architecture supports the deployment target.

## Abort Conditions

- Requirements too vague to identify modules — ask user to clarify the core user flows before designing modules.
- Framework choice conflicts with deployment target (e.g., rhino targeting shinyapps.io without proper config) — revisit framework selection.
- Architecture review reveals fundamental reactivity design flaw — restructure modules before adding more features.

## Examples

### Example: Data exploration dashboard with golem

**Prompt:** "Build a dashboard that lets users upload CSV data, filter rows, and see summary plots."

**Flow:** Scaffold (golem) → Modules: mod_upload (file input + validation), mod_filter (dynamic filter UI), mod_summary (ggplot2 output) → Wire (upload returns reactive df, filter takes df and returns filtered, summary takes filtered) → Test (shinytest2: upload → filter → verify plot updates) → Architecture review

```r
# Module skeleton — mod_upload
mod_upload_ui <- function(id) {
  ns <- shiny::NS(id)
  shiny::tagList(
    shiny::fileInput(ns("file"), "Upload CSV", accept = ".csv"),
    shiny::tableOutput(ns("preview"))
  )
}

mod_upload_server <- function(id) {
  shiny::moduleServer(id, function(input, output, session) {
    data <- shiny::reactive({
      req(input$file)
      readr::read_csv(input$file$datapath, show_col_types = FALSE)
    })
    output$preview <- shiny::renderTable(head(data()))
    data
  })
}
```

### Example: Adding a module to an existing app

**Prompt:** "Add a download report module to our existing golem dashboard."

**Flow:** Skip scaffold (app exists) → Module: mod_download (parameters input + download handler) → Wire (connect to existing filtered data reactive) → Test → Architecture review (focused on new module integration)
