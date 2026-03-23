# Skill Orchestration Map

**Date:** 2026-03-23

## Territory Boundaries

| Skill | Owns | Does NOT Own | Hands Off To |
|-------|------|-------------|--------------|
| r-data-analysis | Data wrangling, cleaning, transformation with tidyverse | Statistical modeling, performance optimization | r-stats (modeling), r-performance (large data) |
| r-visualization | Static/interactive plots with ggplot2/plotly | Shiny dashboards, data tables | r-shiny (dashboards), r-tables (formatted tables) |
| r-debugging | Error diagnosis, troubleshooting, R pitfalls | Performance optimization, writing tests | r-performance (profiling), r-tdd (tests) |
| r-package-dev | Full R package lifecycle (devtools/roxygen2/CRAN) | Initial scaffolding only, test methodology | r-project-setup (scaffold), r-tdd (testing) |
| r-shiny | Shiny app development, reactivity, modules, deployment | Standalone plots, Quarto documents | r-visualization (plots), r-quarto (docs) |
| r-stats | Inferential statistics, hypothesis testing, model diagnostics | ML/prediction pipelines, clinical trials | r-tidymodels (ML), r-clinical (trials) |
| r-clinical | Clinical trial analysis, biostatistics, regulatory | General stats methodology, general survival | r-stats (general methods) |
| r-tables | Publication tables with gt/gtsummary/reactable | Plots/charts, Shiny app tables, clinical TLFs | r-visualization (plots), r-shiny (app tables), r-clinical (TLFs) |
| r-quarto | Quarto documents/presentations/websites/books | Package vignettes, Shiny apps, table styling | r-package-dev (vignettes), r-shiny (apps), r-tables (styling) |
| r-performance | Code optimization, profiling, data.table, Rcpp, parallel | Normal-scale data wrangling, error debugging | r-data-analysis (wrangling), r-debugging (errors) |
| r-tdd | Test writing, TDD workflow, testthat, coverage | R CMD check, package quality gates, debugging | r-package-dev (R CMD check), r-debugging (bugs) |
| r-targets | Pipeline orchestration with targets package | Initial project setup, data wrangling in targets | r-project-setup (init), r-data-analysis (wrangling) |
| r-tidymodels | ML/prediction with tidymodels ecosystem | Inferential statistics, clinical endpoints | r-stats (inference), r-clinical (endpoints) |
| r-package-skill-generator | Generating skills from R package GitHub repos | Manual skill editing, general package dev | skill-creator (manual editing), r-package-dev (dev) |
| r-project-setup | Initial project/package/app scaffolding | Ongoing development, pipeline design | r-package-dev (ongoing dev), r-targets (pipelines) |

## Overlap Zones — Resolution

| Zone | Skills | Rule |
|------|--------|------|
| Survival analysis | r-stats, r-clinical | r-clinical owns clinical trial endpoints (OS, PFS, DFS). r-stats owns general survival methodology (Cox, KM outside trials). |
| Model selection | r-stats, r-tidymodels | r-tidymodels owns prediction/tuning workflows. r-stats owns inference and diagnostics. |
| data.table | r-data-analysis, r-performance | r-data-analysis mentions data.table as alternative. r-performance owns optimization-focused usage. |
| Interactive plots | r-visualization, r-shiny | r-visualization owns standalone plotly. r-shiny owns plots with Shiny reactivity. |
| Tables | r-tables, r-visualization | r-tables owns formatted publication tables. r-visualization owns plot-based output (heatmaps, etc). |
| Testing | r-package-dev, r-tdd | r-tdd owns test writing and TDD workflow. r-package-dev owns R CMD check and quality gates. |
| Package scaffold | r-project-setup, r-package-dev | r-project-setup owns initial creation. r-package-dev owns everything after scaffold exists. |
| Pipeline init | r-project-setup, r-targets | r-project-setup owns initial _targets.R scaffold. r-targets owns pipeline design and execution. |
| TLF tables | r-tables, r-clinical | r-clinical owns regulatory-context TLF generation. r-tables owns general table formatting. |

## Agent Dispatch

| Agent | Dispatched From | When |
|-------|----------------|------|
| r-statistician | r-stats, r-clinical, r-tidymodels, r-data-analysis | Methodology questions, model selection |
| r-code-reviewer | r-debugging | After fix is applied |
| r-pkg-check | r-package-dev | Before CRAN submission |
| r-shiny-architect | r-shiny | Complex app architecture decisions |
| r-dependency-manager | r-package-dev, r-targets, r-project-setup | Dependency resolution, renv issues |
