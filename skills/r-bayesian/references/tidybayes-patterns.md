# tidybayes & ggdist Patterns

Tidy posterior summaries and visualizations. These are the modern way
to extract and plot draws from brms / rstanarm / cmdstanr fits.

All code uses base pipe `|>` and `<-` for assignment.

---

## The Two Key Verbs

| Verb | Returns | Use when |
|------|---------|----------|
| `spread_draws()` | One row per draw, columns = parameters | Working with named parameters or indexed vectors |
| `gather_draws()` | One row per (draw, parameter) | Comparing many parameters or facet plotting |

```r
library(tidybayes)

# spread — wide format
fit |> spread_draws(b_Intercept, b_x1, sigma)
#> # A tibble: 4,000 x 6
#>    .chain .iteration .draw b_Intercept   b_x1 sigma

# gather — long format
fit |> gather_draws(b_Intercept, b_x1, sigma)
#> # A tibble: 12,000 x 5
#>    .chain .iteration .draw .variable    .value
```

---

## Indexed Parameters (Random Effects)

Group-level effects come in as `r_group[level, term]`. Use `[level, term]`
syntax inside `spread_draws`:

```r
# All school-level intercepts
fit |> spread_draws(r_school[school_id, term])

# Combined with global intercept
fit |>
  spread_draws(b_Intercept, r_school[school_id, ]) |>
  mutate(school_intercept = b_Intercept + r_school)
```

---

## Posterior Summaries

```r
draws <- fit |> spread_draws(b_Intercept, b_x1)

# Median + Highest-density interval (asymmetric)
draws |> median_hdi(.width = c(0.50, 0.89, 0.95))

# Median + quantile interval (symmetric)
draws |> median_qi(.width = 0.95)

# Mean + standard deviation interval
draws |> mean_sdi()

# Mode + HDI (for skewed posteriors)
draws |> mode_hdi(.width = 0.95)
```

| Function | Best for |
|----------|----------|
| `median_qi()` | Symmetric, well-behaved posteriors |
| `median_hdi()` | Skewed posteriors; reports the densest region |
| `mode_hdi()` | Multimodal or heavy-tail posteriors |

---

## The Three "Add" Verbs (Predictions)

```r
# linpred — linear predictor scale (log-odds, log-rate, identity)
df |> add_linpred_draws(fit, ndraws = 200)

# epred — expectation of posterior predictive (response scale)
#         e.g. probability for logistic, rate for Poisson
df |> add_epred_draws(fit, ndraws = 200)

# predicted — full posterior predictive (includes residual noise)
df |> add_predicted_draws(fit, ndraws = 200)
```

| Use | Verb |
|-----|------|
| Coefficient interpretation, group-level shrinkage | `add_linpred_draws` |
| Plotting the *expected* response curve | `add_epred_draws` |
| Generating new data that looks like observed | `add_predicted_draws` |

`add_epred_draws` and `add_linpred_draws` differ for non-Gaussian families;
they're the same for Gaussian.

---

## Visualizing Predictions with ggdist

```r
library(ggplot2)
library(ggdist)

# Spaghetti-plus-band: classic posterior fit visualization
df |>
  add_epred_draws(fit, ndraws = 200) |>
  ggplot(aes(x = x1, y = .epred)) +
  stat_lineribbon(.width = c(0.50, 0.89, 0.95), alpha = 0.5) +
  geom_point(aes(y = y), data = df, size = 0.5) +
  scale_fill_brewer(palette = "Blues")

# Half-eye: density + interval for a single parameter
fit |>
  spread_draws(b_x1) |>
  ggplot(aes(x = b_x1)) +
  stat_halfeye()

# Forest plot of group-level effects
fit |>
  spread_draws(r_group[group_id, ]) |>
  median_hdi(.width = c(0.66, 0.95)) |>
  ggplot(aes(y = group_id, x = r_group, xmin = .lower, xmax = .upper)) +
  geom_pointinterval()
```

---

## ROPE (Region of Practical Equivalence)

Decide if a parameter is "practically zero" — usually clearer than
testing exact-null point hypotheses.

```r
fit |>
  spread_draws(b_treatment) |>
  summarise(
    p_lt_zero  = mean(b_treatment < 0),
    p_in_rope  = mean(abs(b_treatment) < 0.1),    # ROPE = +/- 0.1
    p_gt_rope  = mean(b_treatment > 0.1)
  )
```

For a more formal version, see `bayestestR::rope()` and
`bayestestR::p_direction()`.

---

## Compare Levels of a Factor

```r
fit |>
  spread_draws(r_treatment[treatment, ]) |>
  compare_levels(r_treatment, by = treatment, comparison = "control") |>
  median_hdi()
```

Other comparisons: `pairwise`, `ordered`, custom function returning a
list of pairs.

---

## Posterior of a Derived Quantity

Bayesian inference shines when you derive new quantities. Compute on
draws, then summarize:

```r
fit |>
  spread_draws(b_Intercept, b_dose) |>
  mutate(
    response_at_dose10 = b_Intercept + b_dose * 10,
    response_at_dose20 = b_Intercept + b_dose * 20,
    diff               = response_at_dose20 - response_at_dose10
  ) |>
  median_hdi(diff)
```

---

## Fitted vs Predicted on the Outcome Scale

```r
# What the model thinks the *expected* outcome is, given X
df |>
  add_epred_draws(fit, re_formula = NULL) |>      # include random effects
  group_by(x1) |>
  mean_qi(.epred)

# What new data would look like (with residual noise)
df |>
  add_predicted_draws(fit, re_formula = NA) |>    # ignore random effects
  group_by(x1) |>
  mean_qi(.prediction)
```

Use `re_formula = NA` to predict for a *new* group (population-level
prediction). Use `re_formula = NULL` (default) to include the fitted
group-level effects.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `posterior_predict()` raw output | Pipe through `add_predicted_draws()` for tidy format |
| Confusing `linpred` vs `epred` for non-Gaussian | `epred` is on response scale; `linpred` on link scale |
| Forgetting `re_formula = NA` for marginal predictions | Default includes fitted random effects, which is conditional |
| Reporting `.epred` mean without an interval | Always pair with `.lower`/`.upper` from `mean_qi()` or `median_hdi()` |
| Comparing groups with `tidy()` from broom | Use `compare_levels()` — keeps the posterior intact |

---

## Connecting to brms helpers

| brms function | tidybayes equivalent |
|--------------|---------------------|
| `posterior_summary(fit)` | `spread_draws() \|> median_qi()` |
| `posterior_predict(fit)` | `add_predicted_draws()` |
| `posterior_epred(fit)` | `add_epred_draws()` |
| `posterior_linpred(fit)` | `add_linpred_draws()` |
| `conditional_effects(fit)` | `add_epred_draws()` + `stat_lineribbon()` |

`conditional_effects()` is fine for quick exploration; `tidybayes` is
preferred for paper-quality figures and custom summaries.
