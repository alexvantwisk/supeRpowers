# Targets Integration Recipes

Copy-paste pipeline patterns for common workflows.

---

## Recipe 1: Data Import + Cleaning

### _targets.R

```r
library(targets)

tar_option_set(
  packages = c("dplyr", "readr", "tidyr"),
  format = "qs"
)

tar_source()

list(
  tar_target(raw, read_csv("data/raw/dataset.csv", col_types = cols())),
  tar_target(validated, validate_data(raw)),
  tar_target(clean, clean_data(validated)),
  tar_target(
    processed_file,
    save_processed(clean, "data/processed/clean.qs"),
    format = "file"
  )
)
```

### R/functions.R

```r
validate_data <- function(df) {
  stopifnot(nrow(df) > 0)
  stopifnot(!any(duplicated(df$id)))
  df
}

clean_data <- function(df) {
  df |>
    filter(!is.na(key_var)) |>
    mutate(date = lubridate::ymd(date_string)) |>
    select(-date_string)
}

save_processed <- function(df, path) {
  qs::qsave(df, path)
  path
}
```

---

## Recipe 2: ML Pipeline (tidymodels)

### _targets.R

```r
library(targets)

tar_option_set(
  packages = c("tidymodels", "dplyr", "readr"),
  format = "qs"
)

tar_source()

list(
  tar_target(raw, read_csv("data/dataset.csv", col_types = cols())),
  tar_target(split, initial_split(raw, prop = 0.75, strata = outcome)),
  tar_target(rec, build_recipe(training(split))),
  tar_target(spec, build_model_spec()),
  tar_target(wf, workflow() |> add_recipe(rec) |> add_model(spec)),
  tar_target(folds, vfold_cv(training(split), v = 10, strata = outcome)),
  tar_target(tuned, tune_grid(wf, resamples = folds, grid = 20)),
  tar_target(best, select_best(tuned, metric = "roc_auc")),
  tar_target(final, finalize_workflow(wf, best) |> last_fit(split)),
  tar_target(metrics, collect_metrics(final))
)
```

### R/modeling.R

```r
build_recipe <- function(train_data) {
  recipe(outcome ~ ., data = train_data) |>
    step_impute_knn(all_numeric_predictors()) |>
    step_normalize(all_numeric_predictors()) |>
    step_dummy(all_nominal_predictors()) |>
    step_zv(all_predictors())
}

build_model_spec <- function() {
  boost_tree(
    trees = tune(),
    tree_depth = tune(),
    learn_rate = tune()
  ) |>
    set_engine("xgboost") |>
    set_mode("classification")
}
```

---

## Recipe 3: Report Generation (Quarto)

### _targets.R

```r
library(targets)
library(tarchetypes)

tar_option_set(
  packages = c("dplyr", "ggplot2", "readr"),
  format = "qs"
)

tar_source()

list(
  tar_target(data, load_and_clean("data/raw/input.csv")),
  tar_target(analysis, run_analysis(data)),
  tar_target(fig_main, create_main_figure(analysis)),
  tar_quarto(report, path = "report.qmd")
)
```

### report.qmd

```markdown
---
title: "Analysis Report"
format: html
---

\```{r}
library(targets)
tar_load(analysis)
tar_load(fig_main)
\```

## Results

\```{r}
fig_main
\```

\```{r}
analysis |> summary()
\```
```

---

## Recipe 4: Simulation Study

### _targets.R

```r
library(targets)

tar_option_set(
  packages = c("dplyr", "ggplot2", "purrr"),
  format = "qs"
)

tar_source()

list(
  tar_target(params, define_params()),
  tar_target(rep_ids, seq_len(1000)),
  tar_target(
    sim_result,
    run_one_sim(rep_ids, params),
    pattern = map(rep_ids)
  ),
  tar_target(summary, summarize_sims(sim_result)),
  tar_target(
    fig_convergence,
    plot_convergence(sim_result),
    format = "file"
  )
)
```

### R/simulation.R

```r
define_params <- function() {
  list(
    n = 100,
    effect_size = 0.5,
    alpha = 0.05
  )
}

run_one_sim <- function(rep_id, params) {
  x <- rnorm(params$n)
  y <- params$effect_size * x + rnorm(params$n)
  model <- lm(y ~ x)
  tibble(
    rep = rep_id,
    estimate = coef(model)[["x"]],
    p_value = summary(model)$coefficients["x", "Pr(>|t|)"]
  )
}

summarize_sims <- function(results) {
  results |>
    summarise(
      mean_estimate = mean(estimate),
      power = mean(p_value < 0.05),
      coverage = mean(abs(estimate - 0.5) < 1.96 * sd(estimate))
    )
}

plot_convergence <- function(results) {
  path <- "output/convergence.png"
  p <- results |>
    mutate(cum_mean = cumsum(estimate) / row_number()) |>
    ggplot(aes(x = rep, y = cum_mean)) +
    geom_line() +
    geom_hline(yintercept = 0.5, linetype = "dashed", color = "red") +
    labs(title = "Estimate Convergence", x = "Replicate", y = "Cumulative Mean")
  ggsave(path, p, width = 8, height = 5)
  path
}
```

---

## Recipe 5: Multi-Dataset Analysis

### _targets.R

```r
library(targets)
library(tarchetypes)

tar_option_set(
  packages = c("dplyr", "readr", "ggplot2"),
  format = "qs"
)

tar_source()

tar_map(
  values = tibble(
    dataset_name = c("site_a", "site_b", "site_c"),
    file_path = c("data/site_a.csv", "data/site_b.csv", "data/site_c.csv")
  ),
  names = "dataset_name",
  tar_target(raw, read_csv(file_path, col_types = cols())),
  tar_target(clean, clean_site_data(raw, dataset_name)),
  tar_target(model, fit_site_model(clean)),
  tar_target(metrics, extract_metrics(model, dataset_name))
)

list(
  tar_combine(
    comparison,
    metrics,
    command = dplyr::bind_rows(!!!.x)
  ),
  tar_target(
    comparison_table,
    format_comparison(comparison),
    format = "file"
  )
)
```

### R/analysis.R

```r
clean_site_data <- function(df, site) {
  df |>
    mutate(site = site) |>
    filter(!is.na(outcome))
}

fit_site_model <- function(df) {
  lm(outcome ~ predictor_1 + predictor_2, data = df)
}

extract_metrics <- function(model, site) {
  broom::glance(model) |>
    mutate(site = site)
}

format_comparison <- function(df) {
  path <- "output/comparison.csv"
  readr::write_csv(df, path)
  path
}
```
