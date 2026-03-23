---
name: r-project-setup
description: >
  Use when setting up, initializing, or scaffolding a new R project, package,
  Shiny app, or Quarto document. Provides best-practice templates for
  directory structure, renv dependency management, .Rprofile configuration,
  git setup, and CI scaffolding for any R project type.
  Triggers: new project, initialize, scaffold, project setup, create project,
  start project, new package, new Shiny app, new Quarto, bootstrap.
  Do NOT use for ongoing package development — use r-package-dev instead.
  Do NOT use for pipeline setup beyond initial scaffold — use r-targets instead.
---

# R Project Setup

Scaffold new R projects with best-practice structure, tooling, and dependency management.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/scaffold-templates.md` for full template file contents (.lintr, .gitignore, .Rprofile, .Rproj, Shiny app.R, Quarto _quarto.yml)

**Agent dispatch:**
- After any scaffold, dispatch to **r-dependency-manager** agent for initial renv review
- For R package scaffolding, defer to the **r-package-dev** skill which provides the authoritative scaffold workflow

---

## Project Type Selection

Infer the type from user context, or ask:

| Type | Trigger Phrases |
|------|----------------|
| Analysis | "analyze data", "new analysis project", "explore a dataset" |
| Package | "create a package", "build an R library", "CRAN package" |
| Shiny | "web app", "dashboard", "Shiny app", "interactive" |
| Quarto | "write a report", "create a website", "make slides", "book" |

---

## Scaffold: Analysis Project

```
project-name/
  project-name.Rproj       # RStudio project file
  .Rprofile                 # source("renv/activate.R")
  R/                        # Analysis scripts
    01-import.R
    02-clean.R
    03-analyze.R
  data/
    raw/                    # Immutable raw data (gitignored)
    processed/              # Cleaned data
  output/                   # Figures, tables, results
  docs/                     # Reports, notes
  .lintr                    # Linter configuration
  .gitignore                # R-specific ignores
  README.md                 # Project description stub
```

After creating the directory structure:

```r
renv::init()
```

See `references/scaffold-templates.md` for `.lintr`, `.gitignore`, `.Rprofile`, and `.Rproj` contents.

---

## Scaffold: R Package

Defer to the **r-package-dev** skill for the authoritative package scaffold workflow.
It uses `usethis::create_package()`, `use_testthat(3)`, `use_pipe(type = "base")`,
`use_roxygen_md()`, and the full modern toolchain.

After the r-package-dev scaffold completes, add `.lintr` if not already present
(see `references/scaffold-templates.md` for the template).

---

## Scaffold: Shiny App

### Basic Mode (Prototyping)

```
app-name/
  app.R                     # Main app file
  R/                        # Module files
    mod_sidebar.R
    mod_main.R
  tests/
    testthat/
      test-mod_sidebar.R
  www/                      # Static assets (CSS, JS, images)
  .lintr
  .gitignore
  README.md
```

See `references/scaffold-templates.md` for a minimal `app.R` using `bslib::page_sidebar()`.

### Production Mode (golem)

```r
golem::create_golem("path/to/appname")
```

golem provides: module stubs, config system, test infrastructure, deployment helpers.

Both modes: initialize renv after scaffold:

```r
renv::init()
```

---

## Scaffold: Quarto Project

### Document

```
project-name/
  _quarto.yml               # format: html / pdf / docx
  index.qmd                 # Main document
  references.bib            # Bibliography stub
  .gitignore
```

### Presentation

```
project-name/
  _quarto.yml               # format: revealjs
  slides.qmd                # Slide content
  .gitignore
```

### Website

```
project-name/
  _quarto.yml               # navbar config
  index.qmd                 # Home page
  about.qmd                 # About page
  .gitignore
```

### Book

```
project-name/
  _quarto.yml               # chapters config
  index.qmd                 # Preface
  01-intro.qmd
  02-methods.qmd
  references.bib
  .gitignore
```

See `references/scaffold-templates.md` for `_quarto.yml` templates for each type.

---

## Common to All Scaffolds

Every scaffold includes:

- **`.lintr`** — tidyverse defaults with `line_length_linter(120)` and `snake_case`
- **`.gitignore`** — R-specific ignores (.Rhistory, .RData, .Rproj.user/, renv/library/, _targets/)
- **`.Rprofile`** — renv activation (for projects using renv)
- **`README.md`** — stub with project name and description placeholder

After scaffold, dispatch to **r-dependency-manager** agent for renv review.

---

## Examples

```
"Set up a new analysis project for exploring the mtcars dataset"
"Create an R package called tidywidgets"
"Scaffold a Shiny dashboard with golem"
"Start a Quarto website for my research group"
```
