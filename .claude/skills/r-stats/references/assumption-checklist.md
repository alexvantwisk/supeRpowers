# Assumption Verification Checklist

Per-model-family assumption checks with R code. Run these before interpreting
results. All code uses base pipe `|>` and `<-` for assignment.

---

## Linear Model (`lm`)

### Assumptions

| # | Assumption | Consequence if violated |
|---|-----------|------------------------|
| 1 | Linearity | Biased coefficient estimates |
| 2 | Independence of residuals | Inflated Type I error |
| 3 | Homoscedasticity (constant variance) | Inefficient estimates, invalid SEs |
| 4 | Normality of residuals | Unreliable p-values in small samples |
| 5 | No multicollinearity | Inflated SEs, unstable estimates |
| 6 | No influential outliers | Single observations driving results |

### R Code to Check Each

```r
fit <- lm(y ~ x1 + x2 + x3, data = df)

# 1. Linearity — residuals vs fitted should show no pattern
plot(fit, which = 1)                           # Residuals vs Fitted
# Also check component-plus-residual plots
car::crPlots(fit)

# 2. Independence — residuals vs row order (time-series data)
plot(residuals(fit), type = "l")
lmtest::dwtest(fit)                            # Durbin-Watson; DW near 2 = OK

# 3. Homoscedasticity — Scale-Location plot; also Breusch-Pagan test
plot(fit, which = 3)                           # Scale-Location
lmtest::bptest(fit)                            # p > 0.05 = homoscedastic

# 4. Normality of residuals — Q-Q plot; Shapiro-Wilk for n < 5000
plot(fit, which = 2)                           # Normal Q-Q
shapiro.test(residuals(fit))                   # p > 0.05 = consistent with normality
# Note: lm() is robust to mild non-normality with large n

# 5. Multicollinearity — VIF; > 5 is a concern, > 10 is severe
car::vif(fit)
# Remedies: centre predictors, remove correlated vars, PCA, ridge regression

# 6. Influential observations
plot(fit, which = 4)                           # Cook's distance
plot(fit, which = 5)                           # Residuals vs Leverage
car::influencePlot(fit)
# Cook's D > 4/n flags potentially influential obs
```

---

## Generalised Linear Models (`glm`)

### Logistic Regression

| # | Assumption | Check |
|---|-----------|-------|
| 1 | Binary outcome | — (data type) |
| 2 | Independence | Design consideration |
| 3 | No perfect separation | convergence warnings |
| 4 | Linearity of log-odds | component+residual or smoothed plots |
| 5 | No influential observations | Cook's D, leverage |
| 6 | Sample size adequate | ~10–20 events per predictor (EPP) |

```r
fit <- glm(outcome ~ x1 + x2, family = binomial, data = df)

# 3. Separation — check if model converged cleanly
summary(fit)   # very large SEs (>5) on any coefficient suggests separation
# Remedy: Firth logistic regression (logistf package)

# 4. Linearity of log-odds for continuous predictors
car::crPlots(fit)
# Or use GAM with binomial family to assess functional form
library(mgcv)
fit_gam <- gam(outcome ~ s(x1) + x2, family = binomial, data = df)
plot(fit_gam)

# 5. Influential observations
plot(fit, which = 4)   # Cook's distance
car::influencePlot(fit)

# Hosmer-Lemeshow goodness-of-fit (calibration)
ResourceSelection::hoslem.test(df$outcome, fitted(fit))  # p > 0.05 = adequate fit
```

### Poisson / Count Models

| # | Assumption | Check |
|---|-----------|-------|
| 1 | Counts ≥ 0 | — (data type) |
| 2 | Overdispersion absent (Poisson) | deviance / df ≈ 1 |
| 3 | Mean ≈ variance (Poisson) | plot mean vs variance by group |
| 4 | Linearity of log-mean | component+residual plots |
| 5 | No excess zeros | compare observed vs predicted zero count |

```r
fit_pois <- glm(count ~ x1 + x2, family = poisson, data = df)

# 2. Overdispersion
fit_pois$deviance / fit_pois$df.residual    # > 1.5 suggests overdispersion
# Formal test
AER::dispersiontest(fit_pois)               # p < 0.05 = overdispersed

# If overdispersed: use NB or quasipoisson
fit_nb    <- MASS::glm.nb(count ~ x1 + x2, data = df)
fit_quasi <- glm(count ~ x1 + x2, family = quasipoisson, data = df)

# 5. Excess zeros
obs_zeros  <- sum(df$count == 0)
pred_zeros <- sum(dpois(0, fitted(fit_pois)))
# If obs_zeros >> pred_zeros, consider zero-inflated model
```

---

## Mixed Models (`lme4`)

| # | Assumption | Check |
|---|-----------|-------|
| 1 | Normality of random effects | QQ plot of BLUPs |
| 2 | Normality of residuals | QQ plot of residuals |
| 3 | Homoscedasticity of residuals | residuals vs fitted |
| 4 | Independence of random effects from predictors | scatter ranef vs predictors |
| 5 | Convergence | no warnings; allFit() consistent |

```r
library(lme4)
fit <- lmer(y ~ x + (1 | group), data = df)

# 1. Normality of random effects (BLUPs)
ranef_vals <- ranef(fit)$group[, 1]
qqnorm(ranef_vals); qqline(ranef_vals)

# 2 & 3. Residual diagnostics
plot(fit)                               # residuals vs fitted (base lme4 plot)
qqnorm(residuals(fit)); qqline(residuals(fit))

# Or use DHARMa for simulation-based diagnostics (recommended)
library(DHARMa)
sim_res <- simulateResiduals(fit, n = 500)
plot(sim_res)                           # QQ + residual vs fitted in one call
testDispersion(sim_res)
testOutliers(sim_res)

# 5. Convergence
lme4::allFit(fit)                       # run all optimisers; compare estimates
# Check: do all optimisers give similar fixed-effect estimates?
# If yes: convergence warning is benign
# If no: simplify random effects structure

# Singular fit (variance ~0): simplify by removing correlations or slopes
isSingular(fit)                         # TRUE = singular; simplify model
```

---

## Survival Models

### Cox Proportional Hazards

| # | Assumption | Check |
|---|-----------|-------|
| 1 | Proportional hazards (PH) | Schoenfeld residuals, log-log plot |
| 2 | Log-linearity of continuous covariates | Martingale residuals |
| 3 | Independence of censoring | Substantive / design consideration |
| 4 | No influential observations | dfbeta residuals |

```r
library(survival)
fit_cox <- coxph(Surv(time, event) ~ x1 + x2 + x3, data = df)

# 1. Proportional hazards — Schoenfeld residuals
ph_test <- cox.zph(fit_cox)
print(ph_test)         # p < 0.05 for a covariate flags PH violation
plot(ph_test)          # should show flat, horizontal smoother over time

# Remedies for PH violation:
# a) Add time-interaction: coxph(Surv(t,e) ~ x1 + x1:log(time), data = df)
# b) Stratify: coxph(Surv(t,e) ~ strata(x1) + x2, data = df)
# c) Use parametric model (flexsurv)

# 2. Log-linearity (functional form of continuous predictors)
mg_res <- residuals(fit_cox, type = "martingale")
plot(df$x1, mg_res)                            # LOESS smoother should be linear
# Or use ggcoxfunctional() from survminer

# 3. Influential observations
dfbeta_res <- residuals(fit_cox, type = "dfbeta")
for (j in seq_len(ncol(dfbeta_res))) {
  plot(dfbeta_res[, j], main = paste("dfbeta:", colnames(dfbeta_res)[j]))
  abline(h = 0, lty = 2)
}

# 4. Censoring pattern check
km_censor <- survfit(Surv(time, 1 - event) ~ 1, data = df)
plot(km_censor, main = "Censoring distribution")
# Censoring should be non-informative — discuss with study team
```

### Kaplan-Meier Checks

```r
# Log-rank test (compares KM curves across groups)
survdiff(Surv(time, event) ~ group, data = df)

# Check: does KM curve cross between groups?
# Crossing suggests non-proportional hazards — use weighted log-rank or
# restricted mean survival time (RMST) instead
km <- survfit(Surv(time, event) ~ group, data = df)
survminer::ggsurvplot(km, data = df, risk.table = TRUE)
```

---

## Quick-Reference: Which Diagnostic for Which Problem

| Symptom | Diagnostic | Remedy |
|---------|-----------|--------|
| Heteroscedastic residuals in lm | `bptest()`, Scale-Location plot | WLS, robust SEs (`sandwich`) |
| Non-normal residuals in lm | QQ plot, `shapiro.test()` | Transform outcome, use GLM |
| High VIF in lm | `car::vif()` | Centre, remove, PCA, ridge |
| Overdispersion in Poisson | deviance/df, `dispersiontest()` | NB, quasi-Poisson |
| Separation in logistic | Large SEs | Firth logistic |
| Singular fit in lmer | `isSingular()` | Simplify RE structure |
| Convergence warnings in lmer | `allFit()` | Compare optimisers; simplify if inconsistent |
| PH violated in Cox | `cox.zph()` | Time-interaction, stratify, parametric |
| Excess zeros in counts | Compare obs vs pred zeros | Zero-inflated, hurdle |
| Non-linear predictor in any GLM | `car::crPlots()`, GAM | Splines, polynomials, GAM |
