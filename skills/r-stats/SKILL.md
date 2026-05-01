---
name: r-stats
description: >
  Use when performing statistical modeling, hypothesis testing, or model
  diagnostics in R. Provides expert guidance on linear models, GLMs, mixed
  models, survival analysis, time series, model comparison, assumption
  checking, and effect-size reporting.
  Triggers: statistical model, hypothesis test, regression, ANOVA, t-test,
  chi-squared, lm, glm, mixed model, survival analysis, p-value, confidence
  interval, diagnostics, significantly different, statistical test, odds ratio,
  effect size, model assumptions, Cox model.
  Do NOT use for machine learning or predictive modeling — use r-tidymodels instead.
  Do NOT use for clinical trial-specific analysis — use r-clinical instead.
  Do NOT use for Bayesian MCMC fitting, prior choice, or posterior diagnostics — use r-bayesian instead.
---

# R Statistics & Modeling

Statistical modeling, hypothesis testing, and diagnostics in R.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/model-selection-guide.md` for outcome-type decision trees and tidymodels workflow
- Read `references/assumption-checklist.md` for per-family assumption verification with R code

**Agent dispatch:** For methodology questions, assumption audits, or interpreting
complex outputs, dispatch to the **r-statistician** agent.

**MCP integration (when R session available):**
- Before recommending a model from a specific package: `btw_tool_sessioninfo_is_package_installed` to verify availability
- When choosing between model families: `btw_tool_docs_help_page` to read the actual function signatures and arguments
- Before fitting a model: `btw_tool_env_describe_data_frame` to check outcome variable type and sample size

---

## Linear Models & Diagnostics

Always use `broom::tidy(fit, conf.int = TRUE)` for tidy output, `broom::glance()` for model-level stats, `broom::augment()` for per-row fitted values.

**Assumption workflow (required before interpreting results):**
1. `par(mfrow = c(2, 2)); plot(fit)` — residuals vs fitted, Q-Q, scale-location, leverage
2. `car::vif(fit)` — VIF > 5 is concern, > 10 is severe multicollinearity
3. `car::influencePlot(fit)` — identify high-leverage outliers

Read `references/assumption-checklist.md` for the full per-family checklist.

---

## GLM Family Selection

| Outcome | Family | Key detail |
|---------|--------|------------|
| Binary | `binomial(link = "logit")` | Always specify `family =`; default is gaussian |
| Count | `poisson` | Check overdispersion: `deviance / df.residual >> 1` -> use `quasipoisson` or `MASS::glm.nb()` |
| Count (overdispersed) | `MASS::glm.nb()` or `quasipoisson` | NB adds a dispersion parameter |

Use `exponentiate = TRUE` in `broom::tidy()` for odds ratios (logistic) or rate ratios (Poisson). Use `offset(log(exposure))` for rate models.

---

## Mixed Models (lme4)

Use `performance::icc()` to check if random effects are warranted. Convergence failures: try `lme4::allFit()` to compare optimizers, then simplify random effects structure if needed.

---

## Survival Analysis

> **Boundary:** General survival methodology (Cox, KM, time-varying covariates). For clinical trial endpoints (OS, PFS, DFS), use r-clinical instead.

```r
library(survival)

# Kaplan-Meier
km <- survfit(Surv(time, event) ~ group, data = df)
summary(km)
survminer::ggsurvplot(km, data = df, risk.table = TRUE, pval = TRUE)

# Cox proportional hazards
fit_cox <- coxph(Surv(time, event) ~ x1 + x2 + strata(center), data = df)
broom::tidy(fit_cox, exponentiate = TRUE, conf.int = TRUE)   # HRs

# Test proportional hazards assumption
cox.zph(fit_cox)      # Schoenfeld residuals — p < 0.05 flags violation

# Time-varying covariates
df_tv <- survival::tmerge(df, df, id = id, event = event(time, status))
df_tv <- survival::tmerge(df_tv, tv_data, id = id, x_tv = tdc(change_time, new_val))
fit_tv <- coxph(Surv(tstart, tstop, event) ~ x_tv, data = df_tv)
```

---

## Bayesian Models — Defer to r-bayesian

> **Boundary:** Any time the user mentions `brms`, `rstanarm`, `cmdstanr`,
> Stan, MCMC, posterior, prior, Rhat, divergences, or `pp_check`, use
> r-bayesian instead. That skill covers prior choice, MCMC diagnostics,
> tidybayes summaries, and the full Bayesian workflow.

---

## Time Series

```r
library(tsibble); library(fable)

# Convert to tsibble
ts_df <- df |>
  mutate(month = yearmonth(date)) |>
  as_tsibble(index = month, key = series_id)

# Visualise
ts_df |> autoplot(value)
ts_df |> ACF(value) |> autoplot()     # autocorrelation
ts_df |> PACF(value) |> autoplot()    # partial autocorrelation

# Fit models
fit_ts <- ts_df |>
  model(
    arima  = ARIMA(value),             # auto ARIMA
    ets    = ETS(value),               # state space / exponential smoothing
    naive  = NAIVE(value)              # baseline
  )

# Forecast
fc <- fit_ts |> forecast(h = "12 months")
fc |> autoplot(ts_df, level = c(80, 95))

# Accuracy
accuracy(fit_ts)
```

---

## Multiple Testing Correction

```r
# p.adjust methods: "BH" (Benjamini-Hochberg / FDR), "bonferroni", "holm"
p_values <- c(0.01, 0.04, 0.2, 0.001, 0.08)
p.adjust(p_values, method = "BH")        # FDR — default for exploratory work
p.adjust(p_values, method = "bonferroni")  # conservative, FWER control
p.adjust(p_values, method = "holm")      # less conservative than Bonferroni

# In a tidy pipeline
results |>
  mutate(p_adj = p.adjust(p_value, method = "BH")) |>
  filter(p_adj < 0.05)
```

---

## Model Comparison

> **Boundary:** Inference-focused model comparison (AIC, BIC, LRT). For ML prediction/tuning workflows, use r-tidymodels instead.

```r
# AIC / BIC (lower is better; ΔAIC > 2 is meaningful)
AIC(fit1, fit2, fit3)
BIC(fit1, fit2, fit3)

# Likelihood ratio test (nested models only)
anova(fit_reduced, fit_full, test = "LRT")

# Cross-validation with rsample / tidymodels
library(tidymodels)

cv_folds <- vfold_cv(df, v = 10)
rec <- recipe(y ~ ., data = df) |> step_normalize(all_numeric_predictors())
spec <- linear_reg() |> set_engine("lm")
wf <- workflow() |> add_recipe(rec) |> add_model(spec)
cv_results <- fit_resamples(wf, resamples = cv_folds, metrics = metric_set(rmse, rsq))
collect_metrics(cv_results)
```

---

## Verification

After model fit: check assumptions (`plot()` diagnostics). After fixing assumption violation: re-run diagnostics to confirm fix. After multiple testing: verify correction applied.

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Not checking model assumptions before interpreting | Coefficients/p-values are unreliable if normality, homoscedasticity, or linearity are violated | Run `plot(fit)` diagnostics and `car::vif()` before reporting results |
| Using `anova()` for non-nested model comparison | `anova()` requires nested models; misleading on non-nested pairs | Use `AIC()` / `BIC()` for non-nested models; `anova()` only for nested |
| Forgetting `na.action = na.exclude` in model fit | `predict()` / `augment()` return fewer rows than input data, breaking joins | Pass `na.action = na.exclude` to `lm()` / `glm()` so predictions align |
| Interpreting p-values without multiple testing correction | 5% false positive rate per test compounds across many tests | Apply `p.adjust(method = "BH")` before filtering on significance |
| Forgetting `family = binomial` for logistic regression | `glm()` defaults to `gaussian` — silently fits linear model on 0/1 outcome | Always specify `family = binomial(link = "logit")` for binary outcomes |
| Confusing `predict(type = "response")` vs `type = "link"` in GLMs | `"link"` returns log-odds (logistic) or log-rate (Poisson); `"response"` returns probabilities or counts | Use `type = "response"` for interpretable predictions; `"link"` for CIs on transformed scale |
| Producing full Bayesian analysis when user asked "is this significant?" | Scope creep wastes tokens and confuses the user | Match complexity to the question — start with `t.test()` or `lm()` and escalate only if asked |

## Examples

### Happy Path: Linear model with diagnostics and tidy output

**Prompt:** "Fit a linear model of salary on years_exp and department, check assumptions, and report results."

```r
# Input
fit <- lm(salary ~ years_exp + department, data = employees)

# Check assumptions
car::vif(fit)                            # VIF < 5 = OK
par(mfrow = c(2, 2)); plot(fit)          # residual diagnostics

# Output — tidy summary with CIs
broom::tidy(fit, conf.int = TRUE)
#> # A tibble: 4 x 7
#>   term              estimate std.error statistic  p.value conf.low conf.high
#>   <chr>                <dbl>     <dbl>     <dbl>    <dbl>    <dbl>     <dbl>
#> 1 (Intercept)        32000.     1200.      26.7  1.2e-45   29600.    34400.
#> 2 years_exp           2150.      180.      11.9  3.4e-22    1790.     2510.
#> 3 departmentSales    -1800.      950.      -1.89 6.0e-02   -3680.      80.
#> 4 departmentEng       4200.      980.       4.29 3.1e-05    2260.     6140.
```

### Edge Case: Logistic regression forgetting family = binomial

**Prompt:** "Predict churn (binary) from usage and plan_type."

```r
# WRONG — glm() defaults to gaussian; silently fits linear model on 0/1
fit_bad <- glm(churn ~ usage + plan_type, data = customers)

# CORRECT — specify family for binary outcome
fit <- glm(churn ~ usage + plan_type, family = binomial, data = customers)
broom::tidy(fit, exponentiate = TRUE, conf.int = TRUE)
#> # A tibble: 3 x 7
#>   term           estimate std.error statistic p.value conf.low conf.high
#>   <chr>             <dbl>     <dbl>     <dbl>   <dbl>    <dbl>     <dbl>
#> 1 (Intercept)       0.12      0.45     -4.72  2.3e-06   0.049      0.28
#> 2 usage             1.03      0.008     3.91  9.2e-05   1.02       1.05
#> 3 plan_typePro      0.54      0.21     -2.93  3.4e-03   0.36       0.82
```

**More example prompts:**
- "Test treatment effect on pain score with repeated measurements per patient."
- "Compare survival by treatment arm and fit a Cox model with age."
- "We ran 50 tests; apply FDR correction."
