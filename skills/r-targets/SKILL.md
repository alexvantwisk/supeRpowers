---
name: r-targets
description: >
  Use when creating reproducible analysis pipelines, managing computational
  workflows, or using the targets package for pipeline orchestration in R.
  Provides expert guidance on target definitions, static and dynamic branching,
  dependency graphs, caching, cloud storage backends, and integration with
  renv for fully reproducible workflows.
  Triggers: targets, pipeline, workflow, reproducible, tar_make, tar_read,
  tar_target, branching, dependency graph, pipeline orchestration, make-like.
  Do NOT use for initial project setup — use r-project-setup instead.
  Do NOT use for general data wrangling within a target — use r-data-analysis instead.
---

# R Targets — Pipeline Orchestration

Reproducible analysis pipelines with the targets package. Define targets once,
re-run only what changed. All code uses base pipe `|>`, `<-` for assignment,
and tidyverse style.

**Lazy references:**
- Read `references/branching-patterns.md` for static vs dynamic branching decision tree and recipes
- Read `references/targets-integration-recipes.md` for copy-paste pipeline patterns (ML, reports, simulations)

**Agent dispatch:** For renv + targets reproducibility questions, hand off to
the **r-dependency-manager** agent.

---

## Pipeline Fundamentals

The `_targets.R` file defines the pipeline:

```r
library(targets)

tar_option_set(
  packages = c("dplyr", "ggplot2", "readr"),
  format = "qs"
)

# Source functions from R/ directory
tar_source()

list(
  tar_target(data_raw, read_csv("data/raw/input.csv", col_types = cols())),
  tar_target(data_clean, clean_data(data_raw)),
  tar_target(model, fit_model(data_clean)),
  tar_target(report, render_report(model), format = "file")
)
```

Each `tar_target()` is a cacheable unit. targets tracks dependencies via static
code analysis — only outdated targets re-run on `tar_make()`.

---

## Core Workflow Commands

| Command | Purpose |
|---------|---------|
| `tar_make()` | Run pipeline (only outdated targets) |
| `tar_read(name)` | Load a target's cached value |
| `tar_load(name)` | Load into current environment |
| `tar_visnetwork()` | Visualize dependency graph |
| `tar_outdated()` | List targets that need re-running |
| `tar_manifest()` | List all targets with metadata |
| `tar_progress()` | Check status of running pipeline |
| `tar_invalidate(name)` | Force a target to re-run |

---

## Target Formats

| Format | When to Use |
|--------|------------|
| `"qs"` | Default — fast R object serialization (recommended) |
| `"rds"` | Fallback if qs not available |
| `"feather"` | Arrow format for cross-language interop |
| `"parquet"` | Columnar format for large datasets |
| `"file"` | External files (plots, reports, data exports) |

Set globally: `tar_option_set(format = "qs")`

---

## Static Branching

Map targets over known values at definition time:

```r
library(tarchetypes)

tar_map(
  values = tibble(dataset = c("train", "test", "validation")),
  tar_target(data, load_data(dataset)),
  tar_target(model, fit_model(data))
)
```

See `references/branching-patterns.md` for detailed recipes.

---

## Dynamic Branching

Map targets over values computed at runtime:

```r
tar_target(files, list.files("data/", full.names = TRUE)),
tar_target(
  processed,
  process_file(files),
  pattern = map(files)
)
```

Patterns: `map()` (1:1), `cross()` (all combinations), `slice()` (subset).

---

## Error Handling and Debugging

```r
# Load a failed target's dependencies for interactive debugging
tar_workspace(failed_target_name)

# Find failed targets
tar_meta() |> dplyr::filter(!is.na(error))

# Continue pipeline despite failures
tar_target(x, risky_fn(), error = "continue")

# Get traceback for a failure
tar_traceback(failed_target_name)
```

---

## Integration: targets + Quarto

```r
library(tarchetypes)

list(
  tar_target(data, load_data()),
  tar_target(model, fit_model(data)),
  tar_quarto(report, path = "report.qmd")
)
```

In `report.qmd`, access pipeline results with `targets::tar_read(model)`.

---

## Integration: targets + tidymodels

```r
list(
  tar_target(raw, read_csv("data.csv", col_types = cols())),
  tar_target(split, initial_split(raw, strata = outcome)),
  tar_target(rec, build_recipe(training(split))),
  tar_target(spec, build_model_spec()),
  tar_target(wf, workflow() |> add_recipe(rec) |> add_model(spec)),
  tar_target(folds, vfold_cv(training(split), v = 10, strata = outcome)),
  tar_target(tuned, tune_grid(wf, resamples = folds, grid = 20)),
  tar_target(best, select_best(tuned, metric = "roc_auc")),
  tar_target(final, finalize_workflow(wf, best) |> last_fit(split))
)
```

---

## Integration: targets + renv

Full reproducibility stack:

- `renv.lock` — pinned package versions (version controlled)
- `_targets.R` — pipeline definition (version controlled)
- `R/` — function definitions (version controlled)
- `_targets/` — pipeline cache (**gitignored**)

---

## Parallel Execution

```r
library(crew)

tar_option_set(
  controller = crew_controller_local(workers = 4)
)
```

`crew` is the recommended backend. Workers execute independent targets in parallel.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| One giant target that does everything | No caching granularity; any change reruns the whole thing | Break into small, focused targets with single responsibilities |
| Targets that return invisible side effects | targets caches return values; invisible side effects are not tracked | Return the value explicitly, or use `format = "file"` for side-effect targets |
| Hard-coded file paths inside functions | targets cannot detect the dependency; file changes are invisible to the graph | Pass paths as target inputs so targets tracks them |
| Functions defined inside `_targets.R` | `tar_make()` re-sources `_targets.R` each run; functions pollute the pipeline definition | Move functions to `R/` directory; `tar_source()` loads them |
| `_targets/` committed to git | Cache is machine-specific and large; bloats repo, causes merge conflicts | Add `_targets/` to `.gitignore` |
| Using `tar_load()` inside a target function | Breaks reproducibility — the loaded target is invisible to the dependency graph | Pass the value as a function argument; targets wires dependencies automatically |
| Non-serializable objects (DB connections, R6 with env refs) | `format = "qs"` or `"rds"` cannot serialize them; target fails on cache write | Return data, not connections; reconnect inside the target that needs the connection |
| NULL-returning targets silently skipped | A target returning `NULL` appears up-to-date but carries no value downstream | Return a sentinel value or empty tibble; use `tar_assert_*()` to guard |
| `tar_source()` loading files in non-deterministic order | If `R/` files depend on load order (e.g., one sources another), results vary | Make each file self-contained; declare dependencies via function calls, not file order |
| Redesigning entire pipeline when user asked to add one target | Scope creep wastes time and risks breaking a working pipeline | Add the requested target, verify with `tar_visnetwork()`, suggest improvements as follow-up |

---

## Examples

```
"Set up a targets pipeline for my data analysis project"
"Convert my analysis scripts into a reproducible pipeline with targets"
"Add Quarto report rendering as a target in my pipeline"
"Set up parallel execution for my branched targets"
"Debug a failing target in my pipeline"
```
