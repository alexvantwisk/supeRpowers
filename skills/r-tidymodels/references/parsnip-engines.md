# Parsnip Engine Comparison

Complete engine reference for parsnip model types.

---

## linear_reg()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| lm | stats | fast | high | none | Baseline, small data, inference |
| glmnet | glmnet | fast | high | `penalty`, `mixture` | Regularization needed, many predictors |
| stan | rstanarm | slow | high | `prior` (external) | Bayesian inference, uncertainty quantification |

```r
linear_reg(penalty = tune(), mixture = tune()) |> set_engine("glmnet")
```

---

## logistic_reg()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| glm | stats | fast | high | none | Baseline binary classification |
| glmnet | glmnet | fast | high | `penalty`, `mixture` | Regularized logistic, feature selection |
| stan | rstanarm | slow | high | `prior` (external) | Bayesian classification |

```r
logistic_reg(penalty = tune(), mixture = 1) |> set_engine("glmnet")
```

---

## rand_forest()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| ranger | ranger | fast | medium | `mtry`, `trees`, `min_n` | General purpose, fast training |
| randomForest | randomForest | medium | medium | `mtry`, `trees`, `min_n` | Legacy compatibility |

```r
rand_forest(mtry = tune(), trees = 500, min_n = tune()) |>
  set_engine("ranger") |>
  set_mode("classification")
```

---

## boost_tree()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| xgboost | xgboost | medium | low | `trees`, `tree_depth`, `learn_rate`, `mtry`, `min_n`, `loss_reduction`, `sample_size` | Best performance on structured data |
| lightgbm | bonsai | fast | low | `trees`, `tree_depth`, `learn_rate`, `mtry`, `min_n` | Large datasets, native categorical support |

```r
boost_tree(trees = tune(), tree_depth = tune(), learn_rate = tune()) |>
  set_engine("xgboost") |>
  set_mode("classification")
```

---

## svm_rbf() / svm_linear()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| kernlab | kernlab | medium | low | `cost`, `rbf_sigma` (rbf only) | Small-medium data, clear margin separation |

```r
svm_rbf(cost = tune(), rbf_sigma = tune()) |>
  set_engine("kernlab") |>
  set_mode("classification")
```

---

## nearest_neighbor()

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| kknn | kknn | fast (small data) | high | `neighbors`, `weight_func`, `dist_power` | Small data, local patterns, baseline |

```r
nearest_neighbor(neighbors = tune(), weight_func = "optimal") |>
  set_engine("kknn") |>
  set_mode("classification")
```

---

## mlp() (Neural Network)

| Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|--------|-----------|-------|-----------------|-------------------|----------------|
| nnet | nnet | fast | low | `hidden_units`, `penalty` | Simple single-layer network |
| brulee | brulee | medium | low | `hidden_units`, `epochs`, `learn_rate`, `penalty` | Modern torch backend, deeper networks |

```r
mlp(hidden_units = tune(), penalty = tune(), epochs = 100) |>
  set_engine("brulee") |>
  set_mode("classification")
```

---

## Model Selection Quick Guide

| Scenario | Start With | Why |
|----------|-----------|-----|
| Baseline | `linear_reg()` / `logistic_reg()` | Simple, interpretable, fast |
| Structured data, best accuracy | `boost_tree(engine = "xgboost")` | Consistently top performer |
| Large dataset (>100K rows) | `boost_tree(engine = "lightgbm")` | Fast training, memory efficient |
| Mixed types, minimal tuning | `rand_forest(engine = "ranger")` | Robust default, handles mixed types |
| Small data (<1K rows) | `nearest_neighbor()` or `svm_rbf()` | No distribution assumptions |
| Need uncertainty | `linear_reg(engine = "stan")` | Full posterior distributions |
