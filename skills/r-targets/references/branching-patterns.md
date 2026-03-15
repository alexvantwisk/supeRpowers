# Branching Patterns

Decision tree and recipes for static vs dynamic branching in targets.

---

## Decision Tree

```
Do you know the branch values at pipeline definition time?
├── YES → Static branching (tar_map / tarchetypes)
│   ├── One target per value? → tar_map()
│   └── Named variants? → tar_map(names = tidyselect)
└── NO → Dynamic branching (pattern argument)
    ├── One branch per upstream element? → pattern = map(x)
    ├── All combinations of two upstreams? → pattern = cross(x, y)
    └── Subset of elements? → pattern = slice(x, index = 1:5)
```

---

## Static Branching Recipes

### Multiple Datasets

```r
library(tarchetypes)

tar_map(
  values = tibble(
    data_name = c("sales", "inventory", "customers"),
    file_path = c("data/sales.csv", "data/inventory.csv", "data/customers.csv")
  ),
  tar_target(raw, read_csv(file_path, col_types = cols())),
  tar_target(clean, clean_data(raw)),
  tar_target(summary, summarize_data(clean))
)
```

### Parameter Sweep

```r
tar_map(
  values = tibble(
    alpha = c(0.01, 0.05, 0.1, 0.5, 1.0),
    label = paste0("alpha_", alpha)
  ),
  names = "label",
  tar_target(model, fit_model(data, alpha = alpha)),
  tar_target(metrics, evaluate_model(model))
)
```

### Cross-Validation Folds

```r
tar_map(
  values = tibble(fold_id = 1:10),
  tar_target(fold_data, get_fold(data, fold_id)),
  tar_target(fold_model, fit_fold(fold_data)),
  tar_target(fold_metric, score_fold(fold_model, fold_data))
)

tar_target(cv_summary, summarize_cv(c(fold_metric_1, fold_metric_2)))
```

---

## Dynamic Branching Recipes

### File Processing

```r
tar_target(input_files, list.files("data/raw/", full.names = TRUE)),
tar_target(
  processed,
  process_file(input_files),
  pattern = map(input_files)
),
tar_target(combined, bind_rows(processed))
```

### Simulation Replicates

```r
tar_target(rep_ids, seq_len(1000)),
tar_target(
  sim_result,
  run_simulation(rep_ids, params),
  pattern = map(rep_ids)
),
tar_target(sim_summary, summarize_sims(sim_result))
```

### Group-By Analysis

```r
tar_target(
  grouped_data,
  data |> group_by(region) |> tar_group(),
  iteration = "group"
),
tar_target(
  regional_model,
  fit_regional(grouped_data),
  pattern = map(grouped_data)
)
```

---

## Combining Branched Results

```r
# Aggregate dynamic branches into one target
tar_target(
  all_results,
  dplyr::bind_rows(branched_target)
)

# Or use tar_combine for static branches
tar_combine(
  combined_metrics,
  fold_metric,  # references all fold_metric_* targets
  command = dplyr::bind_rows(!!!.x)
)
```

---

## Tips

- **Static branching** creates targets visible in `tar_manifest()` — easier to debug
- **Dynamic branching** creates branches at runtime — more flexible but harder to inspect
- **Combine early:** aggregate branched results into a single target as soon as possible
- **Name your branches:** use `names` in `tar_map()` for readable target names
- Keep branch functions pure — no side effects, return the value
