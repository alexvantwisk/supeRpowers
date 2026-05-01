# Prior Choice for Bayesian Models in R

Weakly-informative defaults, prior predictive checks, and sensitivity
analysis. All code uses base pipe `|>` and `<-` for assignment.

---

## The Default Workflow

1. **Standardize predictors** — `mutate(across(all_of(num_vars), \(x) as.numeric(scale(x))))`. Priors below assume mean-0, SD-1 predictors.
2. **Choose weakly informative priors** — see table below.
3. **Prior predictive check** — simulate outcomes from prior alone.
4. **Sensitivity analysis** — refit with tighter and wider priors; compare.

---

## Default Prior Table — Weakly Informative

For standardized continuous predictors and `lm`/`glm`-style models:

| Parameter class | brms `class` | Default prior | Notes |
|----------------|--------------|---------------|-------|
| Regression coefficient | `b` | `normal(0, 1)` | 95% mass in [-2, 2] SD on standardized scale |
| Intercept | `Intercept` | `normal(<y_mean>, <y_sd>)` | Centered on outcome's empirical scale |
| Group-level SD | `sd` | `exponential(1)` | Half-distribution; mean 1 SD on outcome scale |
| Residual SD | `sigma` | `exponential(1)` | For Gaussian families |
| LKJ correlation (random slopes) | `cor` | `lkj(2)` | Mildly favors zero correlation |
| Shape (negbin) | `shape` | `gamma(0.01, 0.01)` (default) or `exponential(1)` | Default is improper-ish; tighten on small data |
| `nu` (Student-t) | `nu` | `gamma(2, 0.1)` | Default; lower bound 1 |

---

## Family-Specific Guidance

### Gaussian linear regression

```r
prior(normal(0, 1), class = "b") +
prior(normal(<y_mean>, <y_sd>), class = "Intercept") +
prior(exponential(1), class = "sigma")
```

### Logistic regression

Coefficients are on the log-odds scale, where `normal(0, 1)` corresponds
to odds ratios in [0.14, 7.4] — already informative. For complete
separation problems, tighten further:

```r
prior(normal(0, 1.5), class = "b") +              # weakly informative
prior(student_t(7, 0, 2.5), class = "Intercept")  # a la Gelman
```

### Poisson / Negative Binomial

Coefficients are on the log-rate scale. `normal(0, 1)` allows up to ~10x
multiplicative effects per SD — usually wider than needed:

```r
prior(normal(0, 0.5), class = "b") +
prior(exponential(1), class = "shape")            # negbin overdispersion
```

### Hierarchical models

The hardest part is the group-level SD. Watch for:

- `exponential(1)` is reasonable on outcome-SD scale.
- For very few groups (≤ 5), `exponential(1)` lets the SD shoot up.
  Tighten to `exponential(2)` or use `student_t(3, 0, 1)` half-distribution.
- Avoid `cauchy(0, 5)` historical default — too wide on small data.

---

## Inspecting Defaults

```r
# Before fitting — show what brms will use
get_prior(formula, data = df, family = ...)
# Returns one row per parameter class with default prior.

# After fitting — show what was actually used
prior_summary(fit)
```

Always check both. Several brms classes default to flat (`(uniform)`) priors —
those are the silent failure modes.

---

## Prior Predictive Check

```r
prior_only <- brm(formula, data = df,
                  prior = my_priors,
                  sample_prior = "only",
                  chains = 2, iter = 1000, seed = 42)

pp_check(prior_only, ndraws = 100)
pp_check(prior_only, type = "stat", stat = "mean")
pp_check(prior_only, type = "stat_2d", stat = c("mean", "sd"))
```

**What to look for:**

| Symptom | Diagnosis |
|---------|-----------|
| Simulated outcomes spanning 10^10+ | Priors on coefficients or sigma too wide |
| All simulated outcomes nearly identical | Priors too tight |
| Mean of simulated outcomes ~ 0 when truth is 50 | Intercept prior misspecified |
| Bimodal / weird distribution | Family or link function mismatch |

A good prior predictive check shows simulated outcomes that are
*plausible but not constrained to truth*.

---

## Sensitivity Analysis

```r
priors_loose  <- c(prior(normal(0, 5), class = "b"))
priors_med    <- c(prior(normal(0, 1), class = "b"))
priors_tight  <- c(prior(normal(0, 0.3), class = "b"))

fits <- list(
  loose = update(fit, prior = priors_loose),
  med   = update(fit, prior = priors_med),
  tight = update(fit, prior = priors_tight)
)

# Compare posterior of key parameter
fits |>
  purrr::map_dfr(\(f) tidybayes::spread_draws(f, b_x1) |>
                       tidybayes::median_hdi(),
                 .id = "prior") |>
  print()
```

If the posterior moves substantially between `med` and `tight`, the data
are not very informative — you must report what you assumed. If `med` and
`loose` give nearly identical posteriors, the prior is doing little
work and you can use either with confidence.

---

## When to Use Informative Priors

Defaults to weakly informative, but consider truly informative priors when:

- Prior studies provide a posterior you can summarize as a Normal mean+SD.
- Domain experts can defend a plausible range with a story.
- Hard biological / physical constraints exist (probability, rate, mass).
- You're doing sequential / online updating.

Always report informative priors transparently; never tune them post-hoc
to get a desired answer (this is *prior hacking*).

---

## Avoiding Prior Pathologies

| Pitfall | Fix |
|---------|-----|
| Improper flat priors silently set on `b` | Always set explicit prior on `b` |
| `cauchy()` on group SD on small data | Use `exponential()` or half-`student_t(3, 0, 1)` |
| Wide `lkj(1)` on tall random-effect structures | Use `lkj(2)` or higher to favor weak correlations |
| Setting priors on un-standardized predictors | Always standardize, or scale priors per predictor |
| Forgetting `lb = 0` on parameters that must be positive | brms handles defaults; for nonlinear params, always check |

---

## Tools

```r
# Visualize prior shapes before fitting
ggdist::geom_dots()  # for prior samples
brms::stanvar()      # for custom user-defined parameters

# Reusable prior set
my_priors <- c(
  prior(normal(0, 1), class = "b"),
  prior(exponential(1), class = "sd"),
  prior(exponential(1), class = "sigma"),
  prior(lkj(2), class = "cor")
)
```
