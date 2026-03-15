---
name: r-stats
description: >
  Use when performing statistical modeling, hypothesis testing, or model
  diagnostics in R. Covers linear models, GLMs, mixed models, survival
  analysis, Bayesian methods, time series, and model comparison.
---

# R Statistics & Modeling

Statistical modeling, hypothesis testing, and diagnostics in R.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/model-selection-guide.md` for outcome-type decision trees and tidymodels workflow
- Read `references/assumption-checklist.md` for per-family assumption verification with R code

**Agent dispatch:** For methodology questions, assumption audits, or interpreting
complex outputs, dispatch to the **r-statistician** agent.

---

## Linear Models

```r
fit <- lm(y ~ x1 + x2 + x1:x2, data = df)
summary(fit)
confint(fit)                          # 95% CIs on coefficients
broom::tidy(fit, conf.int = TRUE)     # tidy tibble output
broom::glance(fit)                    # model-level stats (R², AIC, etc.)
broom::augment(fit)                   # fitted values, residuals per row
```

### Diagnostics

```r
# Base plots: residuals vs fitted, Q-Q, scale-location, leverage
par(mfrow = c(2, 2)); plot(fit)

# Multicollinearity — VIF > 5 is a concern, > 10 is severe
car::vif(fit)

# Influence measures
car::influencePlot(fit)
```

Read `references/assumption-checklist.md` for the full linear model checklist.

---

## Generalized Linear Models

```r
# Logistic regression (binary outcome)
fit_logit <- glm(outcome ~ x1 + x2, family = binomial(link = "logit"), data = df)

# Poisson regression (count outcome)
fit_pois <- glm(count ~ x1 + offset(log(exposure)), family = poisson, data = df)

# Negative binomial (overdispersed counts)
fit_nb <- MASS::glm.nb(count ~ x1 + x2, data = df)

# Quasi families for overdispersion without NB
fit_quasi <- glm(count ~ x1, family = quasipoisson, data = df)

# Check overdispersion in Poisson: ratio >> 1 indicates problem
fit_pois$deviance / fit_pois$df.residual

# Odds ratios / rate ratios
broom::tidy(fit_logit, exponentiate = TRUE, conf.int = TRUE)
```

---

## Mixed Models

```r
library(lme4)

# Random intercept
fit_lmer <- lmer(y ~ x1 + x2 + (1 | subject), data = df)

# Random intercept + slope
fit_lmer2 <- lmer(y ~ time + (time | subject), data = df)

# GLMM (binary outcome)
fit_glmer <- glmer(outcome ~ x1 + (1 | site), family = binomial, data = df)

summary(fit_lmer)
lme4::ranef(fit_lmer)                  # BLUPs for random effects
performance::icc(fit_lmer)            # intraclass correlation

# Convergence troubleshooting
lme4::allFit(fit_lmer)                 # try all optimisers; compare estimates
# Simplify random effects structure if convergence warnings persist
```

---

## Survival Analysis

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

## Bayesian Models

```r
library(brms)

# Linear model with default weakly-informative priors
fit_brm <- brm(y ~ x1 + x2, data = df, family = gaussian(),
               chains = 4, iter = 2000, cores = 4)

# Custom priors
priors <- c(prior(normal(0, 1), class = b),
            prior(exponential(1), class = sigma))
fit_brm2 <- brm(y ~ x1, data = df, prior = priors, family = gaussian())

# Posterior checks
pp_check(fit_brm)                     # overlay of data vs posterior predictive
bayesplot::mcmc_trace(fit_brm)        # check mixing / convergence
posterior::summarise_draws(fit_brm)   # Rhat < 1.01, ESS > 400

# rstanarm (faster for standard models, same Stan backend)
fit_stan <- rstanarm::stan_glm(y ~ x1 + x2, data = df, family = gaussian())
```

**Prior guidance:** Start with weakly-informative priors (normal(0,1) on scaled
predictors, exponential(1) for scale parameters). Use `prior_summary()` to
inspect defaults. Conduct prior predictive checks with `brm(..., sample_prior = "only")`.

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

## Examples

### 1. Linear model with diagnostics
**Prompt:** "Fit a linear model of salary on years_exp and department, check assumptions."

```r
fit <- lm(salary ~ years_exp + department, data = employees)
car::vif(fit)
par(mfrow = c(2, 2)); plot(fit)
broom::tidy(fit, conf.int = TRUE)
```

### 2. Logistic regression with odds ratios
**Prompt:** "Predict churn (binary) from usage and plan_type, report ORs."

```r
fit <- glm(churn ~ usage + plan_type, family = binomial, data = customers)
broom::tidy(fit, exponentiate = TRUE, conf.int = TRUE)
```

### 3. Mixed model for repeated measures
**Prompt:** "Test treatment effect on pain score with repeated measurements per patient."

```r
fit <- lmer(pain ~ time * treatment + (time | patient_id), data = trial_df)
summary(fit)
lmerTest::anova(fit)     # F-tests with Satterthwaite df
```

### 4. Kaplan-Meier + Cox PH
**Prompt:** "Compare survival by treatment arm and fit a Cox model with age adjustment."

```r
km <- survfit(Surv(os_time, os_event) ~ treatment, data = trial_df)
survminer::ggsurvplot(km, data = trial_df, pval = TRUE, risk.table = TRUE)
fit_cox <- coxph(Surv(os_time, os_event) ~ treatment + age, data = trial_df)
broom::tidy(fit_cox, exponentiate = TRUE, conf.int = TRUE)
cox.zph(fit_cox)          # verify PH assumption
```

### 5. Correct for multiple comparisons
**Prompt:** "We ran 50 tests; apply FDR correction."

```r
results |>
  mutate(p_fdr = p.adjust(p_value, method = "BH"),
         significant = p_fdr < 0.05)
```
