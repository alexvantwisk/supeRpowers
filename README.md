# supeRpowers

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-15-purple)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)

Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, biostatistics, and more.

## Installation

Add this repo as a Claude Code plugin marketplace, then install the plugin:

```bash
claude plugin marketplace add alexvantwisk/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

Or from a local clone (handy for development):

```bash
claude plugin marketplace add /path/to/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

Verify it's installed:

```bash
claude plugin list
```

## How It Works

supeRpowers uses a three-layer architecture:

```
Foundation:  rules/r-conventions.md
               (loaded into every R conversation)
                        |
Domain:      15 specialized skills
             (activated by user intent)
                        |
Service:     5 shared agents
             (dispatched from skills or invoked directly)
```

**Foundation** — `rules/r-conventions.md` enforces tidyverse-first coding: base pipe `|>`, `<-` assignment, snake_case, and modern toolchain conventions across every R interaction.

**Domain** — 15 skills cover the full R development spectrum. Each activates automatically when your request matches its trigger — no commands needed.

**Service** — 5 agents handle specialized tasks like code review, statistical consulting, and dependency auditing. Skills dispatch to agents automatically, or you can invoke them directly.

**Hooks** — A session-start hook detects your R project type (package, Shiny, targets, Quarto, analysis) and surfaces the most relevant skills and agents.

## Skills

| Skill | What It Does | Key Packages |
|-------|-------------|-------------|
| r-data-analysis | Data wrangling, cleaning, transformation, pipelines | dplyr, tidyr, readr, stringr, forcats, lubridate |
| r-visualization | Plots, charts, publication-quality figures | ggplot2, plotly, patchwork, viridis |
| r-tdd | Test-driven development, testthat 3e, coverage | testthat, covr, withr |
| r-debugging | Bug diagnosis, profiling, common R pitfalls | browser(), rlang, profvis, reprex |
| r-package-dev | Full package lifecycle, CRAN submission | usethis, devtools, roxygen2, pkgdown |
| r-shiny | Web apps, reactivity, modules, deployment | shiny, bslib, golem, shinytest2 |
| r-stats | Statistical modeling, diagnostics, inference | lm, glm, lme4, survival, brms |
| r-clinical | Clinical trials, CDISC, biostatistics | admiral, pwr, gsDesign, pROC, meta |
| r-tables | Publication-quality tables | gt, gtsummary, gtExtras, reactable |
| r-quarto | Documents, presentations, websites, books | quarto, rmarkdown, tarchetypes |
| r-performance | Profiling, optimization, parallel processing | profvis, data.table, Rcpp, furrr, bench |
| r-tidymodels | Machine learning, predictive modeling, tuning | tidymodels, recipes, tune, yardstick |
| r-targets | Reproducible pipelines, workflow orchestration | targets, tarchetypes, crew |
| r-project-setup | Scaffold new R projects of any type | usethis, renv, golem, quarto |
| r-package-skill-generator | Generate skills from R package repos | (meta-tool) |

## Agents

| Agent | Purpose | Dispatched By |
|-------|---------|--------------|
| r-code-reviewer | Style, correctness, and performance review | r-debugging, any skill after code generation |
| r-statistician | Statistical consulting and model selection | r-stats, r-clinical, r-data-analysis |
| r-pkg-check | R CMD check issue resolution | r-package-dev |
| r-shiny-architect | Shiny app structure and reactivity review | r-shiny |
| r-dependency-manager | renv, dependency auditing, version conflicts | r-package-dev, r-project-setup, r-targets |

## Quick Start

Just describe what you need — skills activate automatically:

```
"Analyze this CSV file and create visualizations"
"Set up a new R package called tidywidgets"
"Build a predictive model for customer churn using tidymodels"
"Create a reproducible pipeline with targets for my analysis"
"Debug why my Shiny app is slow"
"Generate a demographics table for my clinical trial data"
```

## Requirements

- R >= 4.1.0
- Claude Code >= 1.0.0

## License

MIT — see [LICENSE](LICENSE)
