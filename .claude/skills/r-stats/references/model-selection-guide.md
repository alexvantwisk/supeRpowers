# Model Selection Guide

Decision trees for choosing the right model family based on outcome type and
predictor structure. All code uses base pipe `|>` and `<-` for assignment.

---

## Primary Decision Tree

```
What is your outcome variable?
│
├── Continuous (numeric, unbounded)
│   └── → Start with lm()
│       ├── Clustered / repeated measures? → lme4::lmer()
│       ├── Non-linear relationship? → mgcv::gam()
│       └── Many predictors, regularisation? → glmnet (ridge / lasso)
│
├── Binary (0/1, yes/no, event/no event)
│   └── → glm(family = binomial)
│       ├── Clustered data? → lme4::glmer(family = binomial)
│       ├── Many predictors? → glmnet with family = "binomial"
│       └── Rare outcome (<5%)? → consider Firth logistic (logistf)
│
├── Count (non-negative integer)
│   └── → glm(family = poisson)
│       ├── Overdispersed (deviance/df >> 1)? → MASS::glm.nb()
│       ├── Excess zeros? → pscl::zeroinfl() or pscl::hurdle()
│       └── Clustered? → lme4::glmer(family = poisson)
│
├── Time-to-event (survival)
│   └── → survival::survfit() for KM, survival::coxph() for regression
│       ├── Competing risks? → cmprsk::crr() or tidycmprsk
│       ├── PH violated? → parametric: survival::survreg() or flexsurv
│       └── Time-varying covariates? → tmerge() + coxph()
│
├── Ordinal (ordered categories)
│   └── → MASS::polr() (proportional odds)
│       └── Clustered? → ordinal::clmm()
│
└── Multinomial (unordered categories, >2 levels)
    └── → nnet::multinom()
```

---

## Continuous Outcome Path

### 1. Linear Model (`lm`)

**When:** Continuous outcome, independent observations, ~normal residuals.

```r
fit <- lm(y ~ x1 + x2 + x3, data = df)
summary(fit)
broom::tidy(fit, conf.int = TRUE)
```

**Upgrade triggers:**
- Residuals clearly non-normal → check transformation (log, sqrt) first
- Observations nested/clustered → move to mixed model
- Non-linear predictors detected (residual plots) → GAM

### 2. Linear Mixed Model (`lme4::lmer`)

**When:** Repeated measures, hierarchical data (students in schools, patients
in clinics), or any correlation structure within groups.

```r
# Choose random effects structure based on design
# Random intercept only — groups differ in baseline
fit <- lmer(y ~ x + (1 | group), data = df)

# Random intercept + slope — groups differ in baseline AND effect of x
fit <- lmer(y ~ x + (x | group), data = df)

# Crossed random effects (e.g., items and subjects)
fit <- lmer(y ~ x + (1 | subject) + (1 | item), data = df)
```

**Random effects selection principle:** Start maximal (include all random
effects justified by design), then simplify if convergence fails.
See Barr et al. (2013) for keep-it-maximal rationale.

**Convergence troubleshooting:**
```r
lme4::allFit(fit)           # compare all optimisers
# If estimates agree across optimisers, results are trustworthy despite warnings
# If not, simplify: remove correlations first (x || group), then slopes
```

### 3. Generalised Additive Model (`mgcv::gam`)

**When:** Non-linear relationship between predictors and outcome that lm
cannot capture even with polynomial terms.

```r
library(mgcv)
fit_gam <- gam(y ~ s(x1) + s(x2) + x3, data = df, method = "REML")
plot(fit_gam, pages = 1)   # visualise smooth terms
gam.check(fit_gam)         # diagnostic plots
```

---

## Binary Outcome Path

### 1. Logistic Regression

```r
fit <- glm(outcome ~ x1 + x2, family = binomial(link = "logit"), data = df)
broom::tidy(fit, exponentiate = TRUE, conf.int = TRUE)  # odds ratios
```

**Probit link:** use `link = "probit"` when latent normal assumption is
theoretically justified (psychometrics, dose-response).

**Separation / convergence issues (rare outcome or perfect predictor):**
```r
library(logistf)
fit_firth <- logistf(outcome ~ x1 + x2, data = df)  # Firth penalised likelihood
```

### 2. Mixed Logistic Regression

```r
fit <- lme4::glmer(outcome ~ x1 + x2 + (1 | cluster), family = binomial, data = df)
```

Requires adequate cluster count (>10 clusters, >5 obs per cluster as rough guide).

### 3. Penalised Logistic Regression (high-dimensional)

```r
library(glmnet)
x_mat <- model.matrix(outcome ~ . - 1, data = df)
fit_cv <- cv.glmnet(x_mat, df$outcome, family = "binomial", alpha = 1)  # lasso
coef(fit_cv, s = "lambda.1se")
```

---

## Count Outcome Path

### 1. Poisson Regression

```r
# With offset for rate modelling
fit <- glm(count ~ x1 + offset(log(exposure)), family = poisson, data = df)

# Check overdispersion
fit$deviance / fit$df.residual   # >> 1 means overdispersion
```

### 2. Negative Binomial (overdispersed counts)

```r
fit_nb <- MASS::glm.nb(count ~ x1 + x2, data = df)
# Compare AIC to Poisson
AIC(fit_pois, fit_nb)
```

### 3. Zero-Inflated Models (excess zeros)

```r
library(pscl)
# Two-part model: binary (zero vs non-zero) + count
fit_zi <- zeroinfl(count ~ x1 + x2 | x1, data = df, dist = "negbin")
# Hurdle model (different zero-generating mechanism assumption)
fit_hurdle <- hurdle(count ~ x1 + x2, data = df, dist = "negbin")
```

Prefer zero-inflated when structural zeros are plausible (e.g., non-users of
service will always have 0 counts). Prefer hurdle when the crossing-zero
process is clearly distinct from the count process.

---

## Time-to-Event Path

### 1. Kaplan-Meier (non-parametric, descriptive)

```r
km <- survfit(Surv(time, event) ~ group, data = df)
summary(km)                           # median survival, CIs
survminer::ggsurvplot(km, data = df, risk.table = TRUE, pval = TRUE)
```

### 2. Cox Proportional Hazards (semi-parametric)

```r
fit_cox <- coxph(Surv(time, event) ~ x1 + x2 + strata(x3), data = df)
broom::tidy(fit_cox, exponentiate = TRUE, conf.int = TRUE)  # HRs
cox.zph(fit_cox)   # test PH assumption; plot(cox.zph(fit_cox)) for diagnostics
```

`strata()` allows each stratum a separate baseline hazard (non-proportional
covariate) without estimating an HR for it.

### 3. Parametric Survival (when PH violated or extrapolation needed)

```r
library(flexsurv)
# Fit multiple distributions and compare by AIC
fit_weib <- flexsurvreg(Surv(time, event) ~ x1, data = df, dist = "weibull")
fit_gg   <- flexsurvreg(Surv(time, event) ~ x1, data = df, dist = "gengamma")
AIC(fit_weib, fit_gg)
```

### 4. Competing Risks

```r
library(tidycmprsk)
# Fine-Gray subdistribution hazard model
fit_cr <- crr(Surv(time, factor(event_type)) ~ x1 + x2, data = df)
```

Use competing risks when other events preclude the primary event (e.g.,
non-cancer death precluding cancer-specific death).

---

## tidymodels Workflow

Standard workflow for any model family with cross-validation and evaluation.

```r
library(tidymodels)

# 1. Split data
set.seed(42)
split <- initial_split(df, prop = 0.8, strata = outcome)
train_df <- training(split)
test_df  <- testing(split)

# 2. Recipe (preprocessing)
rec <- recipe(outcome ~ ., data = train_df) |>
  step_impute_median(all_numeric_predictors()) |>
  step_normalize(all_numeric_predictors()) |>
  step_dummy(all_nominal_predictors())

# 3. Model specification
spec <- logistic_reg(penalty = tune(), mixture = 1) |>   # tunable lasso
  set_engine("glmnet") |>
  set_mode("classification")

# 4. Workflow
wf <- workflow() |>
  add_recipe(rec) |>
  add_model(spec)

# 5. Tune with cross-validation
cv_folds <- vfold_cv(train_df, v = 10, strata = outcome)
tune_grid <- grid_regular(penalty(), levels = 20)
tune_results <- tune_grid(wf, resamples = cv_folds, grid = tune_grid,
                          metrics = metric_set(roc_auc, accuracy))

# 6. Select best and finalise
best_params <- select_best(tune_results, metric = "roc_auc")
final_wf <- finalize_workflow(wf, best_params)

# 7. Fit on training, evaluate on test
final_fit <- last_fit(final_wf, split)
collect_metrics(final_fit)
collect_predictions(final_fit) |> roc_curve(outcome, .pred_1) |> autoplot()
```

---

## Quick-Reference Table

| Outcome | Structure | Package | Function |
|---------|-----------|---------|----------|
| Continuous | Independent | stats | `lm()` |
| Continuous | Clustered | lme4 | `lmer()` |
| Continuous | Non-linear | mgcv | `gam()` |
| Binary | Independent | stats | `glm(family=binomial)` |
| Binary | Clustered | lme4 | `glmer(family=binomial)` |
| Count | Independent | stats | `glm(family=poisson)` |
| Count (overdispersed) | Independent | MASS | `glm.nb()` |
| Count (zero-inflated) | Independent | pscl | `zeroinfl()` |
| Time-to-event | Descriptive | survival | `survfit()` |
| Time-to-event | Regression | survival | `coxph()` |
| Time-to-event | Parametric | flexsurv | `flexsurvreg()` |
| Competing risks | — | tidycmprsk | `crr()` |
| Ordinal | Independent | MASS | `polr()` |
| Multinomial | Independent | nnet | `multinom()` |
