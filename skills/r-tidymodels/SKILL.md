---
name: r-tidymodels
description: >
  Use when building machine learning models, predictive modeling, or model
  tuning in R using tidymodels, recipes, workflows, tune, or yardstick.
  Provides expert guidance on the split-preprocess-model-tune-evaluate
  pipeline, feature engineering with recipes, hyperparameter tuning,
  cross-validation, and model performance assessment.
  Triggers: tidymodels, machine learning, predictive model, recipes, parsnip,
  workflows, tune, yardstick, cross-validation, hyperparameter, rsample,
  model tuning, feature engineering, classification, random forest, xgboost,
  model comparison, train test split, predict.
  Do NOT use for inferential statistics or hypothesis testing — use r-stats instead.
  Do NOT use for clinical trial endpoints — use r-clinical instead.
---

# R Tidymodels — Machine Learning

Predictive modeling with the tidymodels ecosystem: split, preprocess, model, tune, evaluate.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/recipe-steps-catalog.md` for the complete step_* function reference
- Read `references/parsnip-engines.md` for the full engine comparison table

**Agent dispatch:** When the question is about *which* model family to use
(methodology, assumptions, inference), hand off to the **r-statistician** agent.
This skill covers *how* to implement models with tidymodels, not *which* model is
statistically appropriate.

> **Boundary:** Prediction performance and ML tuning workflows. For inferential statistics and coefficient interpretation, use r-stats instead. For clinical trial endpoints, use r-clinical instead.

---

## Core Packages

`library(tidymodels)` loads rsample, recipes, parsnip, workflows, tune, yardstick, broom. Add `stacks` separately for ensembling.

## Data Splitting — Conventions

**Always stratify** on the outcome for classification: `initial_split(df, strata = outcome)`.
Use `group_vfold_cv()` when observations are clustered (e.g., repeated measures per patient).

---

## Feature Engineering (recipes)

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_impute_knn(all_numeric_predictors()) |>
  step_log(skewed_var, base = 10) |>
  step_normalize(all_numeric_predictors()) |>
  step_dummy(all_nominal_predictors()) |>
  step_zv(all_predictors()) |>
  step_corr(all_numeric_predictors(), threshold = 0.9)
```

**Step ordering rule:** impute → transform → normalize → encode → filter

Key selectors: `all_predictors()`, `all_numeric_predictors()`,
`all_nominal_predictors()`, `all_outcomes()`.

See `references/recipe-steps-catalog.md` for the complete step_* catalog.

---

## Model Specification (parsnip)

```r
# Linear regression
lm_spec <- linear_reg() |> set_engine("lm")

# Random forest with tunable parameters
rf_spec <- rand_forest(mtry = tune(), trees = 500, min_n = tune()) |>
  set_engine("ranger") |>
  set_mode("classification")

# Gradient boosting
xgb_spec <- boost_tree(trees = tune(), tree_depth = tune(), learn_rate = tune()) |>
  set_engine("xgboost") |>
  set_mode("regression")
```

See `references/parsnip-engines.md` for the full engine comparison table
covering linear_reg, logistic_reg, rand_forest, boost_tree, svm_rbf,
nearest_neighbor, and mlp.

---

## Workflows

```r
wf <- workflow() |>
  add_recipe(rec) |>
  add_model(rf_spec)

# Fit to training data
fit <- wf |> fit(data = train)

# Compare multiple model/recipe combos
wf_set <- workflow_set(
  preproc = list(basic = rec),
  models = list(rf = rf_spec, xgb = xgb_spec, lm = lm_spec)
)
results <- wf_set |> workflow_map("tune_grid", resamples = folds, grid = 10)
```

---

## Hyperparameter Tuning

```r
# Grid search
tune_results <- wf |>
  tune_grid(resamples = folds, grid = 20)

# Bayesian optimization (preferred for expensive models)
tune_results <- wf |>
  tune_bayes(resamples = folds, initial = 10, iter = 25)

# Select best and finalize
best_params <- select_best(tune_results, metric = "roc_auc")
final_wf <- finalize_workflow(wf, best_params)
final_fit <- final_wf |> last_fit(data_split)
```

Grid helpers: `grid_regular()`, `grid_random()`, `grid_latin_hypercube()`.
Selection: `select_best()`, `select_by_one_std_err()`, `select_by_pct_loss()`.

---

## Evaluation (yardstick)

Standard metrics — Claude already knows these. Key patterns:

```r
# Custom metric set — pass to tune_grid(metrics = my_metrics) for focused tuning
my_metrics <- metric_set(rmse, rsq, mae)

# Multi-class: must specify estimator
roc_auc(data, truth = outcome, .pred_A:.pred_C, estimator = "macro")
```

Use `collect_metrics()` on tune/fit results. Use `collect_predictions() |> conf_mat()` for confusion matrices.

---

## Model Stacking

```r
library(stacks)

stack <- stacks() |>
  add_candidates(lm_results) |>
  add_candidates(rf_results) |>
  add_candidates(xgb_results) |>
  blend_predictions() |>
  fit_members()
```

---

## Integration with targets

```r
# In _targets.R
list(
  tar_target(raw, read_csv("data.csv", col_types = cols())),
  tar_target(split, initial_split(raw, strata = outcome)),
  tar_target(rec, build_recipe(training(split))),
  tar_target(spec, build_model_spec()),
  tar_target(tuned, tune_model(rec, spec, split)),
  tar_target(final, finalize_and_fit(tuned, split))
)
```

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Leaking test data into preprocessing | Fitting the recipe on the full dataset causes data leakage; inflated metrics | Always `prep()` the recipe on training data only; `workflow()` handles this automatically |
| Forgetting `prep()` and `bake()` outside workflows | A recipe object is a blueprint, not transformed data; using it raw gives the original data | Call `prep(rec, training = train)` then `bake(prepped, new_data = test)` for manual use |
| Using `set_mode("regression")` on a classification task | Model trains but predictions are numeric, not class labels; metrics crash | Match `set_mode()` to the outcome type; check with `class(train$outcome)` |
| Forgetting `finalize_workflow()` after tuning | `select_best()` returns a tibble of parameters, not a fitted model; calling `fit()` on unfinalized workflow uses `tune()` placeholders | Always call `finalize_workflow(wf, best_params)` before `last_fit()` or `fit()` |
| Not setting seed before `vfold_cv()` | Folds are random; results differ every run, making comparisons meaningless | Call `set.seed()` before `vfold_cv()`, `initial_split()`, and any resampling |
| Confusing `fit()` vs `fit_resamples()` | `fit()` trains one model on all data; `fit_resamples()` trains on each fold for evaluation only | Use `fit_resamples()` or `tune_grid()` for evaluation; use `fit()` only for the final model |
| Building full ML pipeline when user asked to tune one model | Scope creep introduces unnecessary recipes, stacks, or workflow sets | Deliver what was requested; suggest pipeline extensions as follow-up |

---

## Verification

After tune: check `autoplot(tune_results)` for convergence. After finalize: compare test metrics vs CV estimates. After recipe: inspect `prep()` output for unexpected columns.

## Examples

### Happy Path: Full Split-Recipe-Model-Tune-Evaluate Workflow

**Prompt:** "Build a classification model to predict customer churn with tuning."

```r
library(tidymodels)

set.seed(42)
data_split <- initial_split(churn_df, prop = 0.75, strata = churn)
train <- training(data_split)
test  <- testing(data_split)

# Recipe — preprocessing blueprint
rec <- recipe(churn ~ ., data = train) |>
  step_impute_median(all_numeric_predictors()) |>
  step_normalize(all_numeric_predictors()) |>
  step_dummy(all_nominal_predictors()) |>
  step_zv(all_predictors())

# Model spec with tunable parameters
xgb_spec <- boost_tree(trees = tune(), learn_rate = tune()) |>
  set_engine("xgboost") |>
  set_mode("classification")

# Bundle into workflow
wf <- workflow() |> add_recipe(rec) |> add_model(xgb_spec)

# Tune with cross-validation
folds <- vfold_cv(train, v = 5, strata = churn)
tune_results <- wf |> tune_grid(resamples = folds, grid = 20)

# Finalize and evaluate on held-out test set
best_params <- select_best(tune_results, metric = "roc_auc")
final_fit <- finalize_workflow(wf, best_params) |> last_fit(data_split)
collect_metrics(final_fit)
# # A tibble: 2 x 4
#   .metric  .estimator .estimate .config
#   accuracy binary         0.841 Preprocessor1_Model1
#   roc_auc  binary         0.897 Preprocessor1_Model1
```

### Edge Case: Data Leakage from Preprocessing Outside the Recipe

**Prompt:** "Why are my cross-validation metrics suspiciously high?"

```r
# WRONG — normalizing BEFORE splitting leaks test info into training
# all_data_scaled <- all_data |>
#   mutate(across(where(is.numeric), scale))
# split <- initial_split(all_data_scaled, strata = outcome)
# Metrics will be inflated because test data influenced scaling parameters.

# CORRECT — all preprocessing inside the recipe
set.seed(99)
split <- initial_split(raw_data, strata = outcome)
train <- training(split)

rec <- recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors()) |>
  step_dummy(all_nominal_predictors())

# workflow() handles prep(train) + bake(test) automatically
wf <- workflow() |> add_recipe(rec) |> add_model(logistic_reg())
final_fit <- wf |> last_fit(split)
collect_metrics(final_fit)
# Metrics now reflect true out-of-sample performance.
```

**More example prompts:**
- "Create a recipe for preprocessing survey data with missing values"
- "Compare random forest vs gradient boosting on this dataset"
- "Tune an elastic net model with cross-validation"
