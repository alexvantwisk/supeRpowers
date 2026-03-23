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

> **Boundary:** Initial package creation only. For ongoing package development after scaffold, use r-package-dev instead.

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

## Scaffold: Pipeline (targets)

> **Boundary:** Initial `_targets.R` scaffold only. For pipeline design beyond initial scaffold, use r-targets instead.

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

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Creating package scaffold without `usethis::create_package()` | Missing DESCRIPTION, NAMESPACE, and `.Rbuildignore`; `devtools::load_all()` fails | Always use `usethis::create_package()` for packages; defer to r-package-dev skill |
| Forgetting `renv::init()` for dependency management | Project works on your machine but breaks elsewhere; no lockfile for reproducibility | Run `renv::init()` immediately after scaffold; commit `renv.lock` |
| Using `setwd()` instead of project-relative paths | Breaks on any other machine or when project directory moves; fragile and non-portable | Use `here::here()` or RStudio project root; never call `setwd()` in scripts |
| Not initializing git | No version history from the start; first commit contains everything with no meaningful diff | Run `usethis::use_git()` as part of scaffold, or `git init` before first file creation |
| Creating Quarto project without checking Quarto CLI installed | `quarto render` fails with "command not found"; user has no way to build the document | Check `Sys.which("quarto")` or `quarto::quarto_path()` first; advise installation if missing |
| `.Rproj` BuildType set to "Package" for analysis projects | RStudio shows Build pane with `R CMD check` button; confuses users, triggers spurious check errors | Set `BuildType: Custom` or omit BuildType entirely for non-package projects |
| Configuring full CI/CD when user asked to scaffold a project | Scope creep adds GitHub Actions, Docker, pkgdown before the user has any code | Scaffold the directory structure only; suggest CI/CD as a follow-up step |

---

## Examples

### Happy Path: Scaffold an Analysis Project with renv, git, and README

**Prompt:** "Set up a new analysis project for exploring the mtcars dataset."

```r
# 1. Create directory structure
dir.create("mtcars-analysis", recursive = TRUE)
setwd("mtcars-analysis")

dirs <- c("R", "data/raw", "data/processed", "output", "docs")
lapply(dirs, dir.create, recursive = TRUE)

# 2. Create starter analysis script
writeLines(c(
  "library(dplyr)",
  "library(ggplot2)",
  "",
  'raw <- readr::read_csv(here::here("data", "raw", "mtcars.csv"))',
  "clean <- raw |> filter(!is.na(mpg))"
), "R/01-import.R")

# 3. Initialize renv and git
renv::init()
usethis::use_git()

# 4. Verify scaffold
fs::dir_tree()
# mtcars-analysis/
# ├── .Rprofile           <- source("renv/activate.R")
# ├── .gitignore
# ├── R/
# │   └── 01-import.R
# ├── data/
# │   ├── processed/
# │   └── raw/
# ├── docs/
# ├── output/
# ├── renv/
# ├── renv.lock
# └── README.md
```

### Edge Case: Add renv to an Existing Project Mid-Development

**Prompt:** "I have a project that's been running for weeks without renv. Add it now."

```r
# In an existing project with packages already installed system-wide:
renv::init()
# renv detects packages used in R/ and .qmd files via renv::dependencies().
# It creates renv.lock capturing current versions from your library.

# If renv misses a package (e.g., loaded via `library()` in an un-scanned file):
renv::install("janitor")
renv::snapshot()

# Common pitfall: renv::init() may find version conflicts.
# Check the lockfile for unexpected versions:
renv::status()
# The following package(s) are out of sync:
#   janitor  [installed 2.2.0, lockfile 2.1.0]

# Fix with:
renv::snapshot()   # update lockfile to match installed
# or
renv::restore()    # downgrade installed to match lockfile

# Add renv files to git
# .gitignore already includes renv/library/ (machine-specific)
# Commit: renv.lock, .Rprofile, renv/activate.R, renv/settings.json
```

**More example prompts:**
- "Create an R package called tidywidgets"
- "Scaffold a Shiny dashboard with golem"
- "Start a Quarto website for my research group"
