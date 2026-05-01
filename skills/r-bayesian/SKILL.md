---
name: r-bayesian
description: >
  Use when fitting Bayesian models, specifying priors, running MCMC, or
  summarizing posteriors in R using brms, rstanarm, cmdstanr, posterior, or
  tidybayes. Provides expert guidance on the prior-fit-diagnose-summarize
  workflow, weakly-informative prior choice, prior predictive checks,
  Hamiltonian Monte Carlo diagnostics (Rhat, ESS, divergences, treedepth),
  posterior predictive checks, and tidy posterior summaries.
  Triggers: brms, rstanarm, cmdstanr, Stan, Bayesian, MCMC, posterior, prior,
  Rhat, ESS, divergences, posterior predictive check, pp_check, tidybayes,
  spread_draws, gather_draws, hierarchical model, multilevel Bayes, credible
  interval, HDI, posterior probability.
  Do NOT use for frequentist hypothesis tests, p-values, or AIC-based model
  comparison — use r-stats instead.
  Do NOT use for tidymodels-based ML tuning or cross-validation — use
  r-tidymodels instead.
  Do NOT use for clinical trial regulatory submissions — use r-clinical
  instead.
---

# R Bayesian Modeling

Bayesian inference in R with the Stan ecosystem: priors, MCMC sampling,
HMC diagnostics, posterior predictive checks, and tidy posterior
summaries. All code uses base pipe `|>`, `<-` for assignment, and
tidyverse style.

**Lazy references:**
- Read `references/model-formulas.md` for brms formula syntax (hierarchical,
  distributional, mixture, nonlinear, monotonic, smooth)
- Read `references/prior-choice.md` for weakly-informative defaults, prior
  predictive checks, and sensitivity analysis
- Read `references/mcmc-diagnostics.md` for the full diagnostic playbook —
  Rhat, ESS, divergences, max treedepth, energy, posterior predictive checks
- Read `references/tidybayes-patterns.md` for `spread_draws`, `gather_draws`,
  `linpred_draws`, `epred_draws`, and `ggdist` visualization

**Agent dispatch:** For methodology questions (which family, hierarchical
structure, identifiability, prior elicitation), dispatch to the
**r-statistician** agent. This skill covers *how* to fit and diagnose
Bayesian models; methodology trade-offs go to the agent.

**MCP integration (when R session available):**
- Before recommending brms / rstanarm / cmdstanr: `btw_tool_sessioninfo_is_package_installed` (cmdstanr often needs separate setup via `install_cmdstan()`).
- Before fitting: `btw_tool_env_describe_data_frame` to confirm outcome type, sample size, and grouping factors.
- When uncertain about a brms argument: `btw_tool_docs_help_page`.
- Surface long-running fits to the user before they run a 30-minute model.

> **Boundary:** Bayesian inference and posterior reasoning. For frequentist
> coefficient interpretation or null-hypothesis testing, use r-stats. For
> ML tuning, cross-validation, or workflow sets, use r-tidymodels. For
> regulatory clinical analysis (TLFs, ADaM), use r-clinical.

---

## The Bayesian Workflow

Five steps, in order. Skip none — most Bayesian failures come from
shortcutting the prior or diagnostic steps.

1. **Choose family + prior** (see `references/prior-choice.md`)
2. **Prior predictive check** — `sample_prior = "only"`, `pp_check()` on prior
3. **Fit** — `brm()` / `stan_glm()` / `cmdstan_model()`
4. **Diagnose** — Rhat, ESS, divergences, posterior predictive
5. **Summarize + visualize** — `tidybayes` + `ggdist`

Bad priors fit silently — they are the most common silent failure. Show
the prior predictive check before the user waits 10 min for the real fit.

---

## Engine Choice: brms vs rstanarm vs cmdstanr

| Engine | Use when | Trade-off |
|--------|----------|-----------|
| `rstanarm::stan_glm()` / `stan_glmer()` | Standard GLMs, GLMMs | Pre-compiled — fastest start; limited to built-in families |
| `brms::brm()` | Custom families, distributional, nonlinear, splines, mixtures | Compiles per model (~30s); maximum flexibility |
| `cmdstanr::cmdstan_model()` | Hand-written Stan, latest features, faster sampling | Needs `cmdstanr::install_cmdstan()`; user writes Stan |

**Default to `brms` for new analyses.** Use `backend = "cmdstanr"` if
installed — it ships HMC improvements faster than rstan.

```r
fit <- brm(
  y ~ x1 + x2 + (1 | group),
  data    = df,
  family  = gaussian(),
  prior   = c(prior(normal(0, 1), class = "b"),
              prior(exponential(1), class = "sd"),
              prior(exponential(1), class = "sigma")),
  chains  = 4, cores = 4, iter = 2000, warmup = 1000, seed = 42,
  backend = "cmdstanr"
)
```

---

## Prior Choice — Weakly Informative Defaults

> **Always set priors explicitly.** brms defaults are improper flat priors
> on regression coefficients — they sample but offer zero regularization
> and can cause divergences on small data.

**On standardized predictors (mean 0, SD 1):**

| Parameter | Default prior | Rationale |
|-----------|---------------|-----------|
| Regression coefficient `b` | `normal(0, 1)` | 95% mass in [-2, 2] SD |
| Intercept | `normal(<outcome_mean>, <outcome_sd>)` | Centered on data |
| Group-level SD `sd` | `exponential(1)` | Half-distribution; favors smaller variance |
| Residual SD `sigma` | `exponential(1)` | Same |
| Cholesky correlation `cor` | `lkj(2)` | Mildly favors zero correlation |

Inspect defaults: `prior_summary(fit)` or `get_prior(formula, data, family)`.

**Prior predictive check (mandatory before fitting):**

```r
prior_only <- brm(formula, data = df, prior = my_priors,
                  sample_prior = "only", chains = 2, iter = 1000)
pp_check(prior_only, ndraws = 100)
```

If simulated outcomes span 10^15, your priors are too wide. Read
`references/prior-choice.md` for family-specific guidance and sensitivity.

---

## MCMC Diagnostics — The Required Battery

After every fit, before interpreting anything:

```r
posterior::summarise_draws(fit)    # Rhat < 1.01, ess_bulk > 400, ess_tail > 400
brms::nuts_params(fit)             # divergent__ == 0, treedepth__ < max
pp_check(fit, ndraws = 100)        # posterior predictive
pp_check(fit, type = "stat_2d", stat = c("mean", "sd"))
```

**Failure decoder (most common):**

| Symptom | Likely cause | First fix |
|---------|--------------|-----------|
| `Rhat > 1.01` | Chains have not mixed | Run longer warmup; tighten priors |
| `ess_bulk < 400` | High autocorrelation | Increase `iter`; reparameterize (non-centered) |
| Divergences > 0 | Posterior geometry too curved for current step size | Raise `adapt_delta = 0.99`; non-centered parameterization for hierarchical models |
| Max treedepth hits | Step size too small for model | Raise `max_treedepth = 15`; usually a symptom, not the bug |
| `pp_check` shows mismatch | Wrong family or missing predictor | Change family or add interaction; do not just keep increasing iter |

Read `references/mcmc-diagnostics.md` for the full playbook.

---

## Posterior Summaries — tidybayes + ggdist

Never report bare posterior means. Report a credible interval (HDI or
quantile) and a graphical summary. Use 89% (McElreath) or 95% intervals
— conventions, not theorems.

```r
library(tidybayes)
library(ggdist)

# Tidy draws — one row per (parameter, draw)
fit |>
  spread_draws(b_Intercept, b_x1, sd_group__Intercept) |>
  median_hdi(.width = c(0.50, 0.89, 0.95))

# Predictions on outcome scale (epred = expectation of posterior predictive)
df |>
  add_epred_draws(fit, ndraws = 200) |>
  ggplot(aes(x = x1, y = .epred)) +
  stat_lineribbon(.width = c(0.50, 0.89, 0.95)) +
  scale_fill_brewer()
```

Read `references/tidybayes-patterns.md` for `linpred_draws`,
`predicted_draws`, group-level forest plots, `compare_levels`, and ROPE.

---

## Model Comparison — LOO, WAIC, Bayes Factors

```r
# Leave-one-out cross-validation (preferred)
loo1 <- loo(fit1)
loo2 <- loo(fit2)
loo_compare(loo1, loo2)        # elpd_diff and SE; |elpd_diff| / se_diff > 2 is meaningful

# Pareto-k diagnostics — k > 0.7 means LOO estimate is unstable
plot(loo1)                     # check that all k < 0.7

# Stacking weights for ensembling
loo_model_weights(list(fit1, fit2, fit3))
```

> **Avoid Bayes factors** unless you have informative priors and the user
> explicitly asks for them — they are exquisitely sensitive to prior
> width on the parameter being tested.

---

## Hierarchical Models — Non-Centered Parameterization

Centered parameterization (`(1 | group)`) often diverges when group-level
SD is small (the *funnel*). brms emits non-centered Stan code under
`backend = "cmdstanr"`. If divergences persist after `adapt_delta = 0.99`,
switch backends or simplify the random-effects structure.

Read `references/model-formulas.md` for multi-level grouping syntax,
distributional models (`sigma ~ x`), and mixture / monotonic / spline
patterns.

---

## Verification

After fit: confirm Rhat, ESS, divergences, treedepth — all four. After any
prior change: re-run prior predictive check. After predictions: cross-check
posterior summaries against `pp_check` to catch family mis-specification.

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Reporting posterior mean without an interval | A point estimate hides posterior uncertainty — the whole reason to go Bayesian | Always pair with `median_hdi()` or `median_qi()` at 50/89/95% |
| Skipping the prior predictive check | Wide priors generate impossible simulated outcomes; user discovers only after fitting | Always run `sample_prior = "only"` and `pp_check()` before the real fit |
| Trusting fits with divergences | Divergences mean the sampler couldn't traverse part of the posterior — estimates are biased | Treat *any* divergence as a stop condition; raise `adapt_delta`, reparameterize, or simplify |
| Ignoring `Rhat = 1.02` because "it's close to 1" | Rhat > 1.01 signals chains have not converged; posterior summaries are unreliable | Run more warmup or tighten priors until Rhat < 1.01 on every parameter |
| Using AIC/BIC on a Bayesian fit | AIC needs an MLE; Bayesian models have a posterior, not a point estimate | Use `loo()` and `loo_compare()` for predictive comparison |
| Setting flat / improper priors on regression coefficients | brms defaults look harmless but prevent regularization and amplify divergences on small data | Always set explicit `normal(0, 1)` priors on standardized `b` |
| Interpreting a 95% credible interval as "95% chance the parameter is in this range, frequentist-style" | Conditional on model + priors only; not unconditional probability | State assumptions: "given this model and these priors, ..." |
| Fitting `brm()` with `chains = 1, iter = 1000` to "speed it up" | One chain cannot show convergence; no Rhat is computable | Always run ≥4 chains with ≥2000 iter (1000 warmup + 1000 sampling) |
| Producing full hierarchical Bayesian analysis when user asked "is this significant?" | Scope creep — wastes tokens and confuses the user | Match complexity to question; escalate to Bayesian only if asked or if it materially helps |

## Examples

### Happy Path: Hierarchical linear model with diagnostics

**Prompt:** "Fit a Bayesian linear model of `score` on `treatment` with random
intercepts per `school`. Report posterior summaries with 95% HDI."

```r
library(brms)
library(tidybayes)

fit <- brm(
  score ~ treatment + (1 | school),
  data    = students,
  family  = gaussian(),
  prior   = c(
    prior(normal(0, 1), class = "b"),
    prior(normal(0, 5), class = "Intercept"),
    prior(exponential(1), class = "sd"),
    prior(exponential(1), class = "sigma")
  ),
  chains  = 4, cores = 4, iter = 2000, warmup = 1000,
  seed    = 42, backend = "cmdstanr"
)

# Diagnostics — must all pass before reporting
posterior::summarise_draws(fit)        # Rhat < 1.01, ESS > 400
pp_check(fit, ndraws = 100)            # posterior predictive
# nuts_params: zero divergences, no max-treedepth hits

# Posterior summaries
fit |>
  spread_draws(b_Intercept, b_treatment, sd_school__Intercept, sigma) |>
  median_hdi(.width = 0.95)
```

### Edge Case: Divergences in a hierarchical model with small group SD

**Prompt:** "My brms model has 47 divergent transitions. What should I do?"

```r
# WRONG — silently increase iter and hope. More iterations spread the bias.
# fit <- brm(..., iter = 8000)

# CORRECT — diagnose first, then fix
bayesplot::mcmc_pairs(fit, np = nuts_params(fit),
                      pars = c("sd_group__Intercept", "sigma"))
# Divergences usually cluster in the funnel between sd and individual effects.

# First-line fix: raise adapt_delta
fit2 <- update(fit, control = list(adapt_delta = 0.99, max_treedepth = 15))

# If still diverging: non-centered (cmdstanr backend) or simplify the
# random-effects structure.
```

**More example prompts:**

- "Fit a brms logistic regression of `passed` on `study_hours` and report the posterior odds ratio with 89% HDI."
- "Build a Bayesian negative-binomial model of weekly counts with a hierarchical structure per region. Run prior predictive first."
- "Compare two brms models by LOO and tell me which one predicts better."
- "Fit a brms distributional model where `sigma` depends on `group`."
