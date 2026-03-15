# Recipe Steps Catalog

Complete reference for `recipes::step_*()` functions organized by category.

---

## Imputation

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_impute_mean()` | Replace NA with column mean | `all_numeric_predictors()` | Quick baseline, MCAR data |
| `step_impute_median()` | Replace NA with column median | `all_numeric_predictors()` | Skewed distributions |
| `step_impute_knn()` | KNN-based imputation | `neighbors = 5` | Preserves multivariate structure |
| `step_impute_bag()` | Bagged tree imputation | `trees = 25` | Mixed types, nonlinear relationships |
| `step_impute_linear()` | Linear model imputation | `impute_with = imp_vars(...)` | Known linear relationships |
| `step_impute_mode()` | Replace NA with mode | `all_nominal_predictors()` | Categorical variables |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_impute_knn(all_numeric_predictors(), neighbors = 5) |>
  step_impute_mode(all_nominal_predictors())
```

---

## Transformation

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_log()` | Log transform | `base = exp(1)`, `offset = 0` | Right-skewed distributions |
| `step_sqrt()` | Square root transform | — | Moderate skew, count data |
| `step_BoxCox()` | Box-Cox power transform | `limits = c(-5, 5)` | Auto-select best power transform |
| `step_YeoJohnson()` | Yeo-Johnson transform | `limits = c(-5, 5)` | Like Box-Cox but handles negatives |
| `step_poly()` | Polynomial expansion | `degree = 2` | Capture nonlinear effects |
| `step_ns()` | Natural spline basis | `deg_free = 3` | Smooth nonlinear effects |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_YeoJohnson(all_numeric_predictors()) |>
  step_ns(age, deg_free = 4)
```

---

## Normalization

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_normalize()` | Center and scale (z-score) | — | Most models (SVM, KNN, neural nets) |
| `step_center()` | Subtract mean only | — | When scale is meaningful |
| `step_scale()` | Divide by SD only | — | When center is meaningful |
| `step_range()` | Scale to [0, 1] | `min = 0, max = 1` | Neural networks, bounded algorithms |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_normalize(all_numeric_predictors())
```

---

## Encoding

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_dummy()` | One-hot encoding | `one_hot = FALSE` | Linear models, most algorithms |
| `step_other()` | Collapse rare levels | `threshold = 0.05` | Before step_dummy, reduce dimensions |
| `step_integer()` | Map to integers | `strict = TRUE` | Ordinal variables |
| `step_novel()` | Handle unseen factor levels | — | Before step_dummy in production |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_novel(all_nominal_predictors()) |>
  step_other(all_nominal_predictors(), threshold = 0.05) |>
  step_dummy(all_nominal_predictors())
```

---

## Feature Selection

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_zv()` | Remove zero-variance columns | — | Always include (safety net) |
| `step_nzv()` | Remove near-zero-variance | `freq_cut = 95/5` | High-cardinality sparse features |
| `step_corr()` | Remove highly correlated | `threshold = 0.9` | Multicollinearity reduction |
| `step_pca()` | Principal component analysis | `num_comp = 5` or `threshold = 0.95` | Dimensionality reduction |
| `step_select()` | Keep only named columns | `all_of(c("x1", "x2"))` | Manual feature selection |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_zv(all_predictors()) |>
  step_corr(all_numeric_predictors(), threshold = 0.9) |>
  step_pca(all_numeric_predictors(), threshold = 0.95)
```

---

## Interaction

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_interact()` | Create interaction terms | `terms = ~ x1:x2` | Known interactions |
| `step_product()` | Element-wise product | `columns` | Simple multiplicative features |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_interact(terms = ~ age:income)
```

---

## Date/Time

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_date()` | Extract date components | `features = c("dow", "month", "year")` | Date columns in data |
| `step_time()` | Extract time components | `features = c("hour", "minute")` | Time-of-day features |
| `step_holiday()` | Binary holiday indicator | `holidays = timeDate::listHolidays()` | Seasonal patterns |

```r
rec <- recipe(outcome ~ ., data = train) |>
  step_date(date_col, features = c("dow", "month", "year")) |>
  step_holiday(date_col) |>
  step_rm(date_col)
```

---

## Text

| Step | Purpose | Key Arguments | When to Use |
|------|---------|--------------|-------------|
| `step_tokenize()` | Tokenize text | `engine = "tokenizers"` | First step for text data |
| `step_stopwords()` | Remove stop words | `language = "en"` | After tokenization |
| `step_tf()` | Term frequency | — | Bag-of-words features |
| `step_tfidf()` | TF-IDF weighting | — | Better than raw TF for most tasks |
| `step_word_embeddings()` | Pre-trained embeddings | `embeddings` | Dense text representations |

```r
library(textrecipes)

rec <- recipe(outcome ~ text_col, data = train) |>
  step_tokenize(text_col) |>
  step_stopwords(text_col) |>
  step_tfidf(text_col, max_tokens = 500)
```
