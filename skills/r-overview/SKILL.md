---
name: r-overview
description: >
  Use when the user asks what supeRpowers can do, requests a list or directory
  of available R skills / commands / agents, or asks for an overview of the
  plugin — discovery-only intent, not actual R work. Renders a one-page
  inventory of the 20 skills, 7 commands, and 5 agents shipped here, grouped
  by area, so the user can find the right tool for their next R task.
  Triggers: what can supeRpowers do, what R skills do you have, list
  available R helpers, list R skills, list commands, what does this plugin
  do, R plugin overview, what's in supeRpowers, getting started with the R
  plugin, what tools are available, show me the R helpers.
  Do NOT use for actually doing R work — route to the matching domain skill
  (r-data-analysis, r-stats, r-bayesian, r-shiny, r-tdd, r-debugging, etc.).
  Do NOT use for MCP setup — use r-mcp-setup.
  Do NOT use for generating a skill from a package — use
  r-package-skill-generator.
---

# R Plugin Overview

Discovery skill. Render a concise inventory of the supeRpowers plugin so the
user can locate the right tool for their next R task. **Do not begin any R
workflow, do not dispatch any agent, do not load any reference file.** This
skill is for orientation only — once the user picks a direction, the relevant
domain skill or command takes over.

The same content backs the `/r-overview` slash command, which the user can
invoke explicitly when they want the same orientation on demand.

## What to Output

Render the sections below in order. Keep it scannable — one line per item.
Render the trigger words verbatim so the user learns the vocabulary that
auto-routes to each skill.

---

> **supeRpowers** — R programming plugin for Claude Code. Skills activate
> automatically from intent; commands are user-invoked with `/r-<name>`;
> agents are dispatched by skills/commands or invoked directly.

### Skills (20)

**Data & visualization**

- **r-data-analysis** — tidyverse wrangling, cleaning, joins, reshaping. Triggers: dplyr, tidyr, mutate, filter, pivot, join, clean.
- **r-visualization** — ggplot2 ecosystem, publication figures, multi-panel composition. Triggers: ggplot, plot, chart, facet, KM, volcano, forest, patchwork.
- **r-tables** — gt / gtsummary / gtExtras / reactable for publication tables. Triggers: table, gt, summary table, Table 1, regression table.

**Modeling**

- **r-stats** — frequentist inference, p-values, model diagnostics, effect sizes. Triggers: lm, glm, mixed model, p-value, odds ratio, ANOVA.
- **r-bayesian** — brms / rstanarm / Stan: priors, MCMC, posterior diagnostics. Triggers: brms, MCMC, posterior, Rhat, ESS, divergences, tidybayes.
- **r-tidymodels** — predictive ML pipelines, feature engineering, tuning. Triggers: recipes, tune, cross-validation, classification, xgboost.
- **r-clinical** — biostatistics, CDISC ADaM/SDTM, regulatory TLFs, KM endpoints. Triggers: clinical trial, CDISC, FDA, biomarker, meta-analysis.
- **r-performance** — profile-first optimization, data.table, Rcpp, parallel. Triggers: profile, bench, slow, vectorize, large dataset.

**Engineering**

- **r-tdd** — testthat 3e Red-Green-Refactor, snapshot tests, coverage. Triggers: test, expect_*, test_that, snapshot, covr.
- **r-debugging** — reproduce-isolate-diagnose-fix-test for bugs and errors. Triggers: error, traceback, browser, bug, unexpected behavior.
- **r-package-dev** — full package lifecycle, NAMESPACE, vignettes, CRAN. Triggers: usethis, devtools, roxygen2, pkgdown, CRAN submission.
- **r-shiny** — apps, modules, reactivity, golem / rhino / teal, deployment. Triggers: shiny, reactive, module, bslib, golem, teal, shinytest2.
- **r-targets** — reproducible pipelines with the targets package. Triggers: targets, tar_make, tar_target, branching, dependency graph.
- **r-project-setup** — scaffold any R project type with renv + .Rprofile + git. Triggers: new project, initialize, scaffold, renv, bootstrap.

**Publishing**

- **r-quarto** — qmd documents, revealjs slides, websites, books. Triggers: Quarto, qmd, revealjs, cross-reference, journal template.
- **r-reporting** — Word `.docx` consulting reports via reference-doc + flextable. Triggers: docx, reference-doc, flextable, Pandoc, page break.

**Tooling & meta**

- **r-mcp-setup** — connect Claude Code to a live R session via mcptools/btw. Triggers: mcptools, btw, claude mcp add, live R session.
- **r-package-skill-generator** — turn a GitHub R package into a Claude skill. Triggers: generate skill, learn package, skill from repo.
- **r-overview** — this skill: lists every skill / command / agent.
- **skill-auditor** *(meta)* — score an existing skill against project conventions.

### Commands (7)

| Command | Workflow |
|---|---|
| `/r-tdd-cycle` | Red, Green, Refactor, Review for an R package using testthat 3e. |
| `/r-debug` | Reproduce, isolate, diagnose, fix, regression test, verify. |
| `/r-pkg-release` | Audit deps, test, document, R CMD check, version bump, review, submit. |
| `/r-shiny-app` | Scaffold app, design modules, wire reactivity, test, architecture review. |
| `/r-analysis` | Import, clean, explore, model, visualize, report. |
| `/r-report` | Scaffold a Word `.docx` consulting deliverable from an R analysis. |
| `/r-overview` | Print this same inventory on demand. |

### Agents (5)

| Agent | Purpose |
|---|---|
| `r-code-reviewer` | Style, correctness, and performance review of R code. |
| `r-statistician` | Methodology and model-selection consult. |
| `r-pkg-check` | Diagnose `R CMD check` errors, warnings, and notes. |
| `r-shiny-architect` | Module decomposition, reactivity, performance, security. |
| `r-dependency-manager` | renv audit, Bioconductor coexistence, version conflicts. |

### Hooks

- **Session-start** — detects R project type and surfaces relevant skills.
- **Auto-format** (PostToolUse) — runs `styler::style_file()` after edits to `.R`/`.Rmd`/`.qmd`. Opt out with `SUPERPOWERS_DISABLE_AUTOFORMAT=1`.

---

> **Next steps.** Just describe what you want — for example *"clean and join
> these CSVs"* (→ r-data-analysis), *"fit a hierarchical brms model"*
> (→ r-bayesian), or run `/r-tdd-cycle` to start a TDD cycle on a new
> function. Run `/r-mcp-setup` to connect a live R session.

## After Rendering

Stop. Do not pre-load any domain skill. Wait for the user's next message — at
that point the relevant skill will activate from intent (or the user can
invoke a command explicitly).

If the user's next message is a concrete R task, route to the matching domain
skill rather than re-rendering the inventory.

## Examples

- "What can supeRpowers do?"
- "What R skills do you have available?"
- "List the R helpers I can use here."
- "Give me a tour of this plugin."
- "What's in supeRpowers?"
