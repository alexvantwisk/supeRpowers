# supeRpowers Phase 5 — Infrastructure, New Skills & Marketplace Readiness

**Date:** 2026-03-15
**Status:** Design approved, pending implementation plan

## Overview

Phase 5 adds infrastructure and polish to make supeRpowers a production-grade marketplace plugin. It covers four areas:

1. **Hooks system** — Session-start hook that detects R project type and surfaces relevant context
2. **r-project-setup skill** — Scaffold new R projects (analysis, package, Shiny, Quarto)
3. **r-tidymodels & r-targets skills** — Two major R ecosystem gaps filled
4. **Marketplace readiness** — README, LICENSE, RELEASE-NOTES, marketplace.json

## Design Principles

All Phase 5 additions follow the existing architecture:

- Layered design: rules → skills → agents
- Context budget: skills ≤300 lines, agents ≤200 lines, rules ≤150 lines
- Lazy-loaded references for deep content
- Tidyverse-first, base pipe `|>`, `<-` assignment, R >= 4.1.0
- Skills dispatch to shared agents, agents are also directly invocable

---

## 1. Hooks System

### Purpose

Inject R project context at session start so Claude immediately knows what kind of R project it's working in and which skills are most relevant.

### Architecture

```
hooks/
  hooks.json          # Hook configuration (SessionStart matcher)
  session-start       # Bash detection script
  run-hook.cmd        # Cross-platform polyglot wrapper (bash + batch)
```

### hooks.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

**Fires on:** startup, resume, clear, compact — ensuring context survives session resets.

### session-start Script

**Step 1 — Detect plugin root:**
Resolve `CLAUDE_PLUGIN_ROOT` environment variable. Fall back to script directory traversal.

**Step 2 — Detect R project type:**
Scan the current working directory for R project indicators, in priority order:

| Indicator | Project Type |
|-----------|-------------|
| `DESCRIPTION` + `NAMESPACE` | R package |
| `DESCRIPTION` + `app.R` or `ui.R` | Shiny app (package-based, e.g., golem) |
| `app.R` or `ui.R` + `server.R` | Shiny app (basic) |
| `_targets.R` | targets pipeline |
| `_quarto.yml` or `*.qmd` files | Quarto project |
| `.Rproj` file (no DESCRIPTION) | R analysis project |
| `*.R` files only | R scripts (no project structure) |
| None of the above | Not an R project — inject minimal context only |

When multiple indicators are present (e.g., a package with `_targets.R` and `.qmd` files), report the primary type and note secondary features.

**Step 3 — Check R environment (if R project detected):**

| Check | Method | Purpose |
|-------|--------|---------|
| R version | `R --version 2>/dev/null` (first line) | Verify >= 4.1.0 for base pipe |
| renv status | Check for `renv.lock` file existence | Flag if renv not initialized |
| testthat | Check for `tests/testthat/` directory | Flag if no tests |
| Package health | Parse `DESCRIPTION` for `Package:`, `Version:` fields | Report package identity |

All checks are **fast and non-blocking** — file existence checks and one shell command. No R session startup.

**Step 4 — Generate context output:**

Output format via `hookSpecificOutput.additionalContext`:

```
supeRpowers active. Detected: R package (myPkg 0.2.1), R 4.3.2, renv active, testthat 3e.
Relevant skills: r-package-dev, r-tdd, r-debugging, r-code-reviewer agent.
```

For non-R projects:
```
supeRpowers active. No R project detected in current directory. R skills available on demand.
```

### run-hook.cmd (Cross-Platform Wrapper)

Polyglot file that works as both Windows batch and Unix bash:
- **Windows:** Discovers bash via Git for Windows, MSYS2, Cygwin, or system PATH. Silent exit if bash not found.
- **Unix/macOS:** Treats leading `:` as no-op, executes directly as bash.

This follows the polyglot .cmd pattern used by the [obra/superpowers](https://github.com/obra/superpowers) Claude Code plugin — proven cross-platform approach in production (v5.0.2).

### Skill Relevance Mapping

The session-start hook maps project type to most relevant skills:

| Project Type | Primary Skills | Primary Agents |
|-------------|---------------|----------------|
| R package | r-package-dev, r-tdd, r-debugging | r-code-reviewer, r-pkg-check, r-dependency-manager |
| Shiny app | r-shiny, r-tdd, r-debugging | r-shiny-architect, r-code-reviewer |
| targets pipeline | r-targets, r-data-analysis | r-code-reviewer, r-dependency-manager |
| Quarto project | r-quarto, r-visualization, r-tables | — |
| Analysis project | r-data-analysis, r-visualization, r-stats | r-statistician |
| R scripts | r-data-analysis, r-debugging | r-code-reviewer |

### plugin.json Update

Add hooks directory to the manifest:

```json
{
  "claude_code": {
    "min_version": "1.0.0",
    "rules": ["rules/r-conventions.md"],
    "skills": ["skills/*/SKILL.md"],
    "agents": ["agents/*.md"],
    "hooks": "hooks/hooks.json"
  }
}
```

---

## 2. r-project-setup Skill

### Trigger

`"Use when setting up, initializing, or scaffolding a new R project, package, Shiny app, or Quarto document."`

### Skill Structure

```
skills/r-project-setup/
  SKILL.md
  references/
    scaffold-templates.md
```

### Content Sections

**Project type selection** — Ask user or infer from context:

| Type | When to suggest |
|------|----------------|
| Analysis | "I need to analyze some data", "new analysis project" |
| Package | "I want to create a package", "build an R library" |
| Shiny | "I need a web app", "build a dashboard", "Shiny app" |
| Quarto | "I want to write a report", "create a website", "make slides" |

**Scaffold: Analysis Project**

```
project-name/
  project-name.Rproj
  .Rprofile                 # source("renv/activate.R")
  R/
    01-import.R
    02-clean.R
    03-analyze.R
  data/
    raw/                    # Immutable raw data (gitignored)
    processed/
  output/
  docs/
  .lintr
  .gitignore
  README.md
```

After scaffold: `renv::init()` to initialize dependency management.

**Scaffold: R Package**

For R package scaffolding, defer to the `r-package-dev` skill which provides the authoritative scaffold workflow. `r-project-setup` detects the user wants a package and dispatches to `r-package-dev` for the actual scaffold, then adds `.lintr` configuration if not already present.

**Scaffold: Shiny App**

Two modes:
- **Basic** (prototyping): `app.R` + `R/` modules directory + `tests/` + `www/`
- **Production** (golem): `golem::create_golem()` with module stubs, config, tests

Both include: `.lintr`, `.gitignore`, `renv::init()`.

**Scaffold: Quarto Project**

Based on output type:
- **Document:** `index.qmd` + `_quarto.yml` (html/pdf/docx)
- **Presentation:** `slides.qmd` + `_quarto.yml` (revealjs)
- **Website:** `_quarto.yml` (navbar) + `index.qmd` + `about.qmd`
- **Book:** `_quarto.yml` (chapters) + numbered `.qmd` files

All include: `references.bib` stub, `.gitignore`.

**Common to all scaffolds:**
- `.lintr` with tidyverse defaults
- `.gitignore` tailored to R
- `.Rprofile` for renv activation (if applicable)
- `README.md` stub

**Dispatch:** To `r-dependency-manager` agent after scaffold for initial renv review.

### References

`references/scaffold-templates.md` — Full file contents for `.lintr`, `.gitignore`, `.Rprofile`, and `.Rproj` templates.

### Examples

```
"Set up a new analysis project for exploring the mtcars dataset"
"Create an R package called tidywidgets"
"Scaffold a Shiny dashboard with golem"
"Start a Quarto website for my research group"
```

---

## 3. r-tidymodels Skill

### Trigger

`"Use when building machine learning models, predictive modeling, or model tuning in R using tidymodels, recipes, workflows, tune, or yardstick."`

### Skill Structure

```
skills/r-tidymodels/
  SKILL.md
  references/
    recipe-steps-catalog.md
    parsnip-engines.md
```

### Content Sections

**Core packages overview:**

| Package | Role |
|---------|------|
| rsample | Data splitting, resampling |
| recipes | Feature engineering |
| parsnip | Model specification |
| workflows | Bundle recipe + model |
| tune | Hyperparameter tuning |
| yardstick | Model evaluation metrics |
| broom | Tidy model output |
| stacks | Model ensembling |

**Data splitting with rsample:**

- `initial_split()` with `prop` and `strata` arguments
- `training()` / `testing()` extraction
- `vfold_cv()` for cross-validation (default 10-fold)
- `bootstraps()`, `validation_split()`, `group_vfold_cv()`
- Always stratify on outcome for classification: `strata = outcome_var`

**Feature engineering with recipes:**

- `recipe(outcome ~ ., data = train)` formula interface
- Key steps: `step_normalize()`, `step_dummy()`, `step_impute_mean()`, `step_impute_knn()`, `step_interact()`, `step_ns()`, `step_pca()`, `step_corr()`, `step_zv()`, `step_nzv()`
- Role assignments: `update_role()`, `step_rm()`
- Selectors: `all_predictors()`, `all_numeric_predictors()`, `all_nominal_predictors()`, `all_outcomes()`
- Order matters: impute → transform → normalize → encode

**Model specification with parsnip:**

| Model | Function | Common Engines |
|-------|----------|---------------|
| Linear regression | `linear_reg()` | lm, glmnet, stan |
| Logistic regression | `logistic_reg()` | glm, glmnet, stan |
| Random forest | `rand_forest()` | ranger, randomForest |
| Boosted trees | `boost_tree()` | xgboost, lightgbm |
| SVM | `svm_rbf()`, `svm_linear()` | kernlab |
| KNN | `nearest_neighbor()` | kknn |
| Neural network | `mlp()` | nnet, brulee |

- `set_engine("xgboost")` + `set_mode("classification")` or `set_mode("regression")`
- Tunable parameters marked with `tune()`: `mtry = tune()`, `trees = tune()`

**Workflows:**

```r
wf <- workflow() |>
  add_recipe(my_recipe) |>
  add_model(my_model)

wf |> fit(data = train)
```

- `workflow_set()` for comparing multiple model/recipe combinations
- `workflow_map()` to tune across all combinations

**Hyperparameter tuning:**

- `tune_grid()` — grid search (regular or random)
- `tune_bayes()` — Bayesian optimization (preferred for expensive models)
- `grid_regular()`, `grid_random()`, `grid_latin_hypercube()`
- `select_best()`, `select_by_one_std_err()`, `select_by_pct_loss()`
- `finalize_workflow()` to lock in best parameters

**Evaluation with yardstick:**

| Task | Key Metrics |
|------|------------|
| Classification | `accuracy`, `roc_auc`, `f_meas`, `precision`, `recall`, `mn_log_loss` |
| Regression | `rmse`, `rsq`, `mae`, `mape` |
| Multi-class | `roc_auc(estimator = "macro")`, `bal_accuracy` |

- `collect_metrics()` from tuning results
- `conf_mat()` + `autoplot(type = "heatmap")`
- `roc_curve()` + `autoplot()`
- Custom metric sets: `metric_set(rmse, rsq, mae)`

**Model stacking with stacks:**

```r
stack <- stacks() |>
  add_candidates(lm_results) |>
  add_candidates(rf_results) |>
  add_candidates(xgb_results) |>
  blend_predictions() |>
  fit_members()
```

**Integration with targets:**

```r
list(
  tar_target(data_raw, read_csv("data/raw/dataset.csv")),
  tar_target(data_split, initial_split(data_raw, strata = outcome)),
  tar_target(recipe, build_recipe(training(data_split))),
  tar_target(model_spec, build_model_spec()),
  tar_target(tune_results, tune_model(recipe, model_spec, data_split)),
  tar_target(final_fit, finalize_and_fit(tune_results, data_split))
)
```

**Dispatch:** To `r-statistician` agent for model selection methodology questions.

### Line Budget Strategy

The SKILL.md must stay under 300 lines. To achieve this, offload the parsnip model/engine table to `references/parsnip-engines.md` and keep only a summary in the skill body. The stacking section should be a brief pointer to a reference. The skill body should include: rsample (brief), recipes (key steps + order), parsnip (summary + pointer), workflows, tuning, evaluation, targets integration, dispatch, and examples.

### Boundary: r-tidymodels vs r-stats

`r-tidymodels` covers the tidymodels framework for predictive modeling. `r-stats` covers inferential statistics. Overlap in linear/logistic regression: `r-stats` for inference on coefficients, `r-tidymodels` for prediction performance.

### References

**`references/recipe-steps-catalog.md`** — Complete `step_*` reference by category (imputation, transformation, encoding, normalization, feature selection, date/time, text).

**`references/parsnip-engines.md`** — Engine comparison table for each model type: engine name, R package, speed, interpretability, tunable parameters, strengths.

### Examples

```
"Build a classification model to predict customer churn"
"Set up a tidymodels workflow with xgboost and hyperparameter tuning"
"Create a recipe for preprocessing survey data with missing values"
"Compare random forest vs gradient boosting on this dataset"
"Tune an elastic net model with cross-validation"
```

---

## 4. r-targets Skill

### Trigger

`"Use when creating reproducible analysis pipelines, managing computational workflows, or using the targets package for pipeline orchestration in R."`

### Skill Structure

```
skills/r-targets/
  SKILL.md
  references/
    branching-patterns.md
    targets-integration-recipes.md
```

### Content Sections

**Pipeline fundamentals:**

```r
library(targets)

tar_option_set(
  packages = c("dplyr", "ggplot2", "readr"),
  format = "qs"
)

list(
  tar_target(data_raw, read_csv("data/raw/input.csv", col_types = cols())),
  tar_target(data_clean, clean_data(data_raw)),
  tar_target(model, fit_model(data_clean)),
  tar_target(report, render_report(model), format = "file")
)
```

**Core workflow commands:**

| Command | Purpose |
|---------|---------|
| `tar_make()` | Run pipeline (only outdated targets) |
| `tar_read(name)` | Load a target's value |
| `tar_load(name)` | Load into environment |
| `tar_visnetwork()` | Visualize dependency graph |
| `tar_outdated()` | List outdated targets |
| `tar_manifest()` | List all targets |
| `tar_progress()` | Check running status |
| `tar_invalidate(name)` | Force re-run |

**Target formats:**

| Format | When to use |
|--------|------------|
| `"qs"` | Default — fast serialization (recommended) |
| `"rds"` | Fallback if qs not available |
| `"feather"` | Arrow for cross-language interop |
| `"parquet"` | Columnar for large datasets |
| `"file"` | External files (plots, reports) |

**Static branching:**

```r
tar_map(
  values = tibble(dataset = c("train", "test", "validation")),
  tar_target(data, load_data(dataset)),
  tar_target(model, fit_model(data))
)
```

**Dynamic branching:**

```r
tar_target(files, list.files("data/", full.names = TRUE)),
tar_target(processed, process_file(files), pattern = map(files))
```

**Error handling:**

- `tar_workspace(name)` — load target's deps for debugging
- `tar_meta() |> filter(!is.na(error))` — find failures
- `error = "continue"` — don't stop on failure
- `tar_traceback(name)` — get failure traceback

**Integration: targets + Quarto**

```r
library(tarchetypes)
list(
  tar_target(data, load_data()),
  tar_target(model, fit_model(data)),
  tar_quarto(report, path = "report.qmd")
)
```

**Integration: targets + tidymodels**

```r
list(
  tar_target(raw, read_csv("data.csv", col_types = cols())),
  tar_target(split, initial_split(raw, strata = outcome)),
  tar_target(recipe, build_recipe(training(split))),
  tar_target(spec, build_model_spec()),
  tar_target(wf, workflow() |> add_recipe(recipe) |> add_model(spec)),
  tar_target(folds, vfold_cv(training(split), v = 10)),
  tar_target(tuned, tune_grid(wf, resamples = folds, grid = 20)),
  tar_target(final, finalize_workflow(wf, select_best(tuned)) |> last_fit(split))
)
```

**Integration: targets + renv**

- `renv.lock` + `_targets.R` + `R/` = full reproducibility
- `_targets/` goes in `.gitignore`

**Parallel execution:**

```r
library(crew)
tar_option_set(controller = crew_controller_local(workers = 4))
```

**Anti-patterns:**

| Anti-pattern | Fix |
|-------------|-----|
| One giant target | Break into focused targets |
| Side-effect-only targets | Return values or use `format = "file"` |
| Hard-coded paths in functions | Pass as target inputs |
| Functions in `_targets.R` | Move to `R/` directory |
| `_targets/` in git | Add to `.gitignore` |

### References

**`references/branching-patterns.md`** — Static vs dynamic decision tree with recipes.

**`references/targets-integration-recipes.md`** — Copy-paste pipeline patterns for ML, reports, simulations.

**Dispatch:** To `r-dependency-manager` agent for renv + targets reproducibility questions.

### Examples

```
"Set up a targets pipeline for my data analysis project"
"Convert my scripts into a reproducible pipeline with targets"
"Add Quarto report rendering as a target"
"Set up parallel execution for branched targets"
"Debug a failing target in my pipeline"
```

---

## 5. Marketplace Readiness

### Versioning Note

Version 0.2.0 reflects pre-1.0 development status. Version 1.0.0 will be the marketplace launch release after all content is stable and tested. The original design spec's 1.0.0 target remains the goal.

### README.md

**Structure:**

```
# supeRpowers

[badges: version, license, skills count, R >= 4.1.0]

One-line description + installation command.

## How It Works

Architecture explanation with text diagram:
  Foundation (rules/) → Domain (skills/) → Service (agents/)
Brief explanation of each layer.

## Skills

Table: skill name | trigger summary | key packages
(15 rows — all skills)

## Agents

Table: agent name | purpose | dispatched by
(5 rows — all agents)

## Quick Start

5-6 example prompts showing what users can ask.

## Requirements

R >= 4.1.0, Claude Code >= 1.0.0

## License

MIT
```

**Badges** (shields.io format): `v0.2.0`, `MIT`, `15 skills`, `R >= 4.1.0`

### LICENSE

MIT license file, copyright 2026 Alexander van Twisk.

### RELEASE-NOTES.md

```
## 0.2.0 (2026-03-15)
- Hooks: session-start R project detection
- Skills: r-project-setup, r-tidymodels, r-targets
- Marketplace: README, LICENSE, badges

## 0.1.0 (2026-03-15)
- Phase 1: r-data-analysis, r-visualization, r-tdd, r-debugging
- Phase 2: r-package-dev, r-shiny + r-code-reviewer, r-dependency-manager agents
- Phase 3: r-stats, r-clinical, r-tables, r-quarto + r-statistician, r-pkg-check, r-shiny-architect agents
- Phase 4: r-performance, r-package-skill-generator
- Foundation: r-conventions rule, CLAUDE.md
```

### marketplace.json (if required)

`.claude-plugin/marketplace.json` with categories, icon, pricing. Research Claude Code marketplace requirements during implementation — omit if not needed.

---

## Updated plugin.json

```json
{
  "name": "supeRpowers",
  "version": "0.2.0",
  "description": "Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, and biostatistics.",
  "keywords": ["r", "rstats", "tidyverse", "shiny", "biostatistics", "clinical-trials", "tidymodels", "targets"],
  "author": "Alexander van Twisk",
  "license": "MIT",
  "claude_code": {
    "min_version": "1.0.0",
    "rules": ["rules/r-conventions.md"],
    "skills": ["skills/*/SKILL.md"],
    "agents": ["agents/*.md"],
    "hooks": "hooks/hooks.json"
  }
}
```

---

## Updated Directory Structure

```
supeRpowers/
  plugin.json
  README.md                      # NEW
  LICENSE                        # NEW
  RELEASE-NOTES.md               # NEW
  CLAUDE.md                      # Updated
  hooks/                         # NEW
    hooks.json
    session-start
    run-hook.cmd
  rules/
    r-conventions.md
  skills/
    r-project-setup/             # NEW
    r-tidymodels/                # NEW
    r-targets/                   # NEW
    r-data-analysis/
    r-visualization/
    r-tdd/
    r-debugging/
    r-package-dev/
    r-shiny/
    r-stats/
    r-clinical/
    r-tables/
    r-quarto/
    r-performance/
    r-package-skill-generator/
  agents/
    r-code-reviewer.md
    r-statistician.md
    r-pkg-check.md
    r-shiny-architect.md
    r-dependency-manager.md
  plans/
```

---

## Boundary Definitions

**r-tidymodels vs r-stats:** Predictive modeling framework vs inferential statistics.

**r-targets vs r-data-analysis:** Pipeline orchestration vs data transformations inside targets.

**r-project-setup vs r-package-dev:** Initial scaffolding vs ongoing development lifecycle.

---

## Skill Chaining Updates

- **ML pipeline:** `r-project-setup` → `r-targets` → `r-tidymodels` → `r-visualization`
- **Reproducible analysis:** `r-project-setup` → `r-targets` → `r-data-analysis` → `r-quarto`
- **New package:** `r-project-setup` → `r-package-dev` → `r-tdd` → `r-code-reviewer` agent

---

## Original Design Spec Updates

The following changes must be made to `plans/2026-03-15-superpowers-r-plugin-design.md`:

1. **Skill Frontmatter Contracts table (line ~103):** Add r-project-setup, r-tidymodels, r-targets trigger entries
2. **Directory Structure (line ~411):** Add r-project-setup/, r-tidymodels/, r-targets/ under skills/
3. **Skill Chaining section (line ~379):** Add ML pipeline and reproducible analysis chains
4. **Phase section:** Add Phase 5 entry

The following changes must be made to `CLAUDE.md`:

1. Update skill count from "12 skills" to "15 skills"
2. Correct agent count (currently says "6 agents" in header but lists 5 — resolve to 5)
3. Add hooks/ to the project structure
4. Add new skills to the directory listing
5. Add hooks section explaining the session-start hook

---

## Success Criteria

- [ ] Session-start hook detects R project type and injects context
- [ ] Hook works cross-platform (macOS/Linux + Windows polyglot wrapper)
- [ ] r-project-setup scaffolds all four project types
- [ ] r-tidymodels covers split → recipe → model → tune → evaluate
- [ ] r-targets covers pipeline definition, branching, debugging, integrations
- [ ] All new skills ≤300 lines, correct frontmatter, 3-5 examples
- [ ] README.md with badges, architecture, catalogs, quick start
- [ ] LICENSE (MIT) and RELEASE-NOTES.md present
- [ ] plugin.json updated with hooks and version 0.2.0
- [ ] No `%>%` in any new files
- [ ] All R code uses `<-`, `|>`, snake_case, double quotes
- [ ] CLAUDE.md updated to reflect new skills and hooks
