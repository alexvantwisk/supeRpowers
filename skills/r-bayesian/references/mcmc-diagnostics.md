# MCMC Diagnostics — The Required Battery

Hamiltonian Monte Carlo (HMC) is much more diagnosable than older
samplers (Metropolis, Gibbs). When HMC struggles, it tells you. Don't
ignore the warnings.

All code uses base pipe `|>` and `<-` for assignment.

---

## The Mandatory Four

Run every one. A model that passes only three of these is not validated.

| # | Check | Threshold | Tool |
|---|-------|-----------|------|
| 1 | `Rhat` (potential scale reduction) | `< 1.01` | `posterior::summarise_draws(fit)` |
| 2 | `ess_bulk` (effective sample size, bulk) | `> 400` | same |
| 3 | `ess_tail` (effective sample size, tail) | `> 400` | same |
| 4 | Divergent transitions | `== 0` | `nuts_params()` / message at fit time |
| 5 | Max-treedepth saturations | `== 0` | same |
| 6 | E-BFMI (energy) | `> 0.2` | `bayestestR::diagnostic_posterior()` |
| 7 | Posterior predictive | visual match | `pp_check(fit)` |

---

## 1. Convergence — Rhat & ESS

```r
posterior::summarise_draws(fit) |>
  dplyr::select(variable, mean, rhat, ess_bulk, ess_tail) |>
  dplyr::filter(rhat > 1.01 | ess_bulk < 400 | ess_tail < 400)
```

Empty result → all parameters converged. Any rows → those parameters
need attention.

**`Rhat > 1.01`:**
- Chains have not mixed; posterior summary is unreliable.
- Fix: longer warmup (`warmup = 2000`), tighter priors, or simpler model.

**`ess_bulk < 400`:**
- High autocorrelation; posterior mean / median is noisy.
- Fix: more iterations, non-centered parameterization, or model
  reparameterization.

**`ess_tail < 400`:**
- Tail quantiles (95% CI) are noisy even if bulk is fine.
- Fix: more iterations is usually enough.

---

## 2. HMC Pathology — Divergences

```r
np <- brms::nuts_params(fit)            # tibble: chain, iter, parameter, value
np |>
  dplyr::filter(parameter == "divergent__", value == 1) |>
  nrow()
# Goal: 0
```

**Even one divergence is a stop condition.** Divergences indicate the
sampler entered regions where it could not propagate without overshooting
— the resulting posterior is biased toward where the sampler *could* go.

**Diagnose:**

```r
bayesplot::mcmc_pairs(fit,
                      np = np,
                      pars = c("sd_group__Intercept", "sigma"),
                      off_diag_args = list(size = 0.5))
# Red points = divergences. Cluster shows which geometry caused them.
```

**Fix sequence (try in order):**

1. **Raise `adapt_delta`** — first-line fix. Default is 0.8;
   `0.95` → `0.99` → `0.999` shrinks step size.
2. **Non-centered parameterization** — for hierarchical models with
   small group SD. brms emits this with `backend = "cmdstanr"`.
3. **Tighten priors** — wide priors create flat tails the sampler
   gets lost in.
4. **Simplify model** — drop random slopes, collapse rare levels,
   remove redundant predictors.
5. **Reparameterize** — sometimes the model itself is unidentifiable.

```r
fit2 <- update(fit, control = list(adapt_delta = 0.99,
                                   max_treedepth = 15))
```

---

## 3. Max Treedepth

```r
np |>
  dplyr::filter(parameter == "treedepth__", value >= 10) |>
  nrow()  # number of treedepth saturations at default max=10
```

Max-treedepth hits are usually a *symptom* of the same posterior
geometry that causes divergences, not a separate problem. Fix the
divergences first, then check this.

If divergences are zero but treedepth hits remain: raise
`max_treedepth = 12` or `15`. Cost: each iteration takes longer.

---

## 4. Energy (E-BFMI)

```r
bayestestR::diagnostic_posterior(fit) |>
  dplyr::pull(EBFMI)
# Goal: > 0.2 per chain
```

Low E-BFMI suggests the marginal energy is poorly explored — often a
sign of heavy tails or hierarchical funnel. Same fixes as divergences.

---

## 5. Posterior Predictive Checks (PPC)

```r
pp_check(fit, ndraws = 100)                                    # density overlay
pp_check(fit, type = "stat", stat = "mean", ndraws = 200)
pp_check(fit, type = "stat", stat = "sd",   ndraws = 200)
pp_check(fit, type = "stat_2d", stat = c("mean", "sd"))
pp_check(fit, type = "scatter_avg", ndraws = 100)
```

PPCs are not just diagnostic — they are *the* test of model adequacy.
A model with perfect Rhat / ESS / no divergences can still be wrong if
posterior predictives don't match the data.

**Common PPC failures and their meanings:**

| What you see | Likely cause |
|--------------|--------------|
| Predictive density is symmetric, data is right-skewed | Need a non-Gaussian family (lognormal, gamma) |
| Predictive density misses a mode | Mixture model or unmodeled subgroup |
| Predictive variance is much smaller than data | Missing predictor, ignored heteroscedasticity |
| Predictive variance is much larger than data | Overfitting prior, too-flexible model |
| Predictives clip at boundaries (0, 1) the data don't | Wrong family (Beta/zero-inflated/binomial) |

---

## 6. Trace Plots (Visual Convergence)

```r
bayesplot::mcmc_trace(fit, pars = c("b_Intercept", "sigma"))
bayesplot::mcmc_rank_overlay(fit, pars = c("b_Intercept", "sigma"))
```

Healthy traces look like fuzzy caterpillars overlapping across chains.
Rank overlay (Vehtari et al. 2021) is more sensitive than the classic
trace plot — a uniform-looking rank histogram is the goal.

---

## 7. LOO Pareto-k Diagnostic

When using `loo()` for predictive comparison:

```r
loo_fit <- loo(fit)
plot(loo_fit)
# Each point's k value should be < 0.7. k > 0.7 = unstable LOO estimate.
```

If `k > 0.7` for some observations:

```r
loo_fit_reloo <- reloo(fit, loo_fit)        # exact CV for problem points
```

---

## Quick Diagnostic Helper

```r
diagnose_fit <- function(fit) {
  ds <- posterior::summarise_draws(fit) |>
    dplyr::filter(rhat > 1.01 | ess_bulk < 400 | ess_tail < 400)

  np <- brms::nuts_params(fit)
  divs <- sum(np$value[np$parameter == "divergent__"], na.rm = TRUE)
  td   <- sum(np$value[np$parameter == "treedepth__"] >= 10, na.rm = TRUE)

  cat("Convergence issues:", nrow(ds), "parameters\n")
  cat("Divergences:", divs, "\n")
  cat("Treedepth saturations:", td, "\n")
  invisible(list(bad = ds, divs = divs, td = td))
}

diagnose_fit(fit)
```

---

## When to Stop Tuning

After two or three rounds of `adapt_delta` + reparameterization, if
divergences still appear, the model itself may be unidentified or
mis-specified. Step back: check identifiability with prior predictive,
look for redundant parameters, or consult the r-statistician agent for
methodology guidance.
