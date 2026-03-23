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
  model tuning, feature engineering.
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

**Boundary:** `r-tidymodels` = prediction performance. `r-stats` = inferential statistics.
Overlap on linear/logistic regression: use `r-stats` for coefficient interpretation,
`r-tidymodels` for prediction workflows.

---

## Core Packages

| Package | Role |
|---------|------|
| rsample | Data splitting, resampling |
| recipes | Feature engineering (preprocessing) |
| parsnip | Model specification (unified interface) |
| workflows | Bundle recipe + model |
| tune | Hyperparameter tuning |
| yardstick | Model evaluation metrics |
| broom | Tidy model output |
| stacks | Model ensembling |

---

## Data Splitting (rsample)

```r
library(tidymodels)

data_split <- initial_split(df, prop = 0.75, strata = outcome)
train <- training(data_split)
test  <- testing(data_split)

# Cross-validation folds
folds <- vfold_cv(train, v = 10, strata = outcome)
```

Always stratify on the outcome for classification tasks.
Other resampling: `bootstraps()`, `validation_split()`, `group_vfold_cv()`.

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

| Task | Key Metrics |
|------|------------|
| Classification | `accuracy`, `roc_auc`, `f_meas`, `precision`, `recall` |
| Regression | `rmse`, `rsq`, `mae`, `mape` |
| Multi-class | `roc_auc(estimator = "macro")`, `bal_accuracy` |

```r
collect_metrics(tune_results)

# Confusion matrix
final_fit |> collect_predictions() |> conf_mat(truth = outcome, estimate = .pred_class)

# ROC curve
final_fit |> collect_predictions() |> roc_curve(truth = outcome, .pred_Yes) |> autoplot()

# Custom metric set
my_metrics <- metric_set(rmse, rsq, mae)
```

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

## Examples

```
"Build a classification model to predict customer churn"
"Set up a tidymodels workflow with xgboost and hyperparameter tuning"
"Create a recipe for preprocessing survey data with missing values"
"Compare random forest vs gradient boosting on this dataset"
"Tune an elastic net model with cross-validation"
```
