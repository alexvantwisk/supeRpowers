# supeRpowers

![Version](https://img.shields.io/badge/version-0.2.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-18-purple)
![Commands](https://img.shields.io/badge/commands-6-orange)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)

Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, biostatistics, and more.

## Installation

> **Status:** beta. Verified end-to-end on macOS (Apple Silicon) with Claude Code via the GitHub-marketplace install path. Feedback welcome.

### Prerequisites

- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and authenticated
- R **>= 4.1.0** on your `PATH` (required for the base pipe `|>`)
- Optional but recommended:
  - **Quarto CLI** if you'll use `r-quarto` or `/r-report`
  - **`btw` / `mcptools`** for live R-session awareness — see `/r-mcp-setup` after install

### Install from GitHub (recommended)

Add this repository as a Claude Code marketplace, then install the plugin:

```bash
claude plugin marketplace add alexvantwisk/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

The first command registers `https://github.com/alexvantwisk/supeRpowers` as a single-plugin marketplace; the second installs the `supeRpowers` plugin from it. The `@supeRpowers` suffix disambiguates plugin name from marketplace name (they happen to be identical here).

### Install from a local clone (development)

```bash
git clone https://github.com/alexvantwisk/supeRpowers.git
cd supeRpowers
claude plugin marketplace add .
claude plugin install supeRpowers@supeRpowers
```

Use this path if you want to modify skills or commands locally — Claude Code reloads from the source directory.

### Verify

```bash
claude plugin list
```

You should see `supeRpowers` with the current version. To confirm the session-start hook is wired up, open Claude Code in any directory containing R files and you should see a one-line banner reporting the detected R project type and key skills.

### Update

```bash
claude plugin marketplace update supeRpowers
claude plugin install supeRpowers@supeRpowers
```

### Uninstall

```bash
claude plugin uninstall supeRpowers@supeRpowers
claude plugin marketplace remove supeRpowers
```

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `plugin not found` after `install` | Marketplace not added, or wrong suffix | Run `claude plugin marketplace list`; install with the `@supeRpowers` suffix |
| Slash commands don't autocomplete | Plugin install incomplete | `claude plugin list` — reinstall if `supeRpowers` is missing |
| R skills don't activate on R-flavored prompts | Foundation rule not loaded — usually a stale session | Restart your Claude Code session |
| Session-start banner missing | Hook not enabled in your settings | Confirm `~/.claude/settings.json` doesn't disable plugin hooks |
| `quarto: command not found` during `/r-report` | Quarto CLI not on PATH | Install Quarto from https://quarto.org and re-open the shell |

If something else breaks, please open an issue at https://github.com/alexvantwisk/supeRpowers/issues with the output of `claude plugin list` and a minimal reproducer.

## How It Works

supeRpowers uses a four-layer architecture:

```
Foundation:  rules/r-conventions.md
               (loaded into every R conversation)
                        |
Domain:      18 specialized skills
             (activated by user intent)
                        |
Workflows:   6 slash commands
             (user-invoked: /r-tdd-cycle, /r-debug, ...)
                        |
Service:     5 shared agents
             (dispatched from skills/commands or invoked directly)
```

**Foundation** — `rules/r-conventions.md` enforces tidyverse-first coding: base pipe `|>`, `<-` assignment, snake_case, and modern toolchain conventions across every R interaction.

**Domain** — 18 skills cover the full R development spectrum. Each activates automatically when your request matches its trigger — no commands needed.

**Workflows** — 6 slash commands provide guided multi-step procedures (TDD cycle, debugging, package release, Shiny scaffold, analysis pipeline, Word report scaffold). Invoke explicitly with `/r-<name>`.

**Service** — 5 agents handle specialized tasks like code review, statistical consulting, and dependency auditing. Skills and commands dispatch to agents automatically, or you can invoke them directly.

**Hooks** — A session-start hook detects your R project type (package, Shiny, targets, Quarto, analysis) and surfaces the most relevant skills, commands, and agents.

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
| r-reporting | Word (.docx) consulting reports — reference docx, flextable pipeline, page layout | quarto, flextable, gtsummary, knitr |
| r-performance | Profiling, optimization, parallel processing | profvis, data.table, Rcpp, furrr, bench |
| r-tidymodels | Machine learning, predictive modeling, tuning | tidymodels, recipes, tune, yardstick |
| r-targets | Reproducible pipelines, workflow orchestration | targets, tarchetypes, crew |
| r-project-setup | Scaffold new R projects of any type | usethis, renv, golem, quarto |
| r-mcp-setup | MCP server setup for live R session awareness | btw, mcptools |
| r-package-skill-generator | Generate skills from R package repos | (meta-tool) |

> Plus the `skill-auditor` meta-skill that audits and scores other skills against the project conventions.

## Commands

Slash commands provide guided multi-step workflows. Invoke explicitly with `/r-<name>`:

| Command | Workflow |
|---------|----------|
| /r-tdd-cycle | Test-driven development — Red, Green, Refactor, Review |
| /r-debug | Systematic debugging — reproduce, isolate, diagnose, fix, regression test, verify |
| /r-pkg-release | Package release pipeline — audit deps, test, document, R CMD check, version bump, review, submit |
| /r-shiny-app | Shiny app scaffold — structure, modules, reactivity, test, architecture review |
| /r-analysis | Data analysis pipeline — import, clean, explore, model, visualize, report |
| /r-report | Word report scaffold — generate `reference.docx`, qmd, render script for an R consulting deliverable |

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
"Scaffold a Word consulting report for this analysis"
```

## Requirements

- R >= 4.1.0
- Claude Code >= 1.0.0

## Contributing

supeRpowers is in public beta. Right now contribution is via **issues only** —
bug reports, feature requests, and content suggestions for existing skills are
all welcome. Pull requests are not accepted yet (the conventions are still
moving). See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and issue
templates.

## License

MIT — see [LICENSE](LICENSE)
