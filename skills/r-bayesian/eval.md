# Eval: r-bayesian

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to fit a Bayesian model, does the skill set explicit priors via `prior(...)` rather than relying on brms's improper-flat defaults on regression coefficients?
2. Does the skill run a prior predictive check (`sample_prior = "only"` + `pp_check()`) before fitting the real model?
3. After fitting, does the skill verify all four diagnostics — Rhat < 1.01, ESS > 400, divergences == 0, and a `pp_check()` — before interpreting parameters?
4. Does the skill treat any divergent transitions (even one) as a stop condition rather than ignoring them or just increasing iterations?
5. When summarizing posterior parameters, does the skill always pair point estimates with a credible interval (HDI or quantile) rather than reporting bare means?
6. When asked to "test if a coefficient is significant" with frequentist framing, does the skill defer to r-stats rather than producing a Bayesian analysis with p-values?
7. When asked to tune an ML model with cross-validation, does the skill defer to r-tidymodels?
8. Does the skill use `loo()` and `loo_compare()` for model comparison rather than AIC / BIC on a Bayesian fit?
9. Does the skill use `|>` exclusively and `<-` for assignment, with zero `%>%` or `=` for variable assignment?
10. When the user has divergences, does the skill recommend `adapt_delta` increases and reparameterization rather than just more iterations?

## Test Prompts

### Happy Path

- "Fit a Bayesian linear regression of `score` on `treatment` with random intercepts per `school` using brms. Report posterior medians and 95% HDIs."
- "Build a Bayesian negative-binomial model for weekly counts with hierarchical structure per region. Run prior predictive check, fit, diagnose, and summarize."
- "Fit a brms logistic regression of churn on three predictors and visualize the posterior odds ratios with `stat_halfeye`."

### Edge Cases

- "My brms model gave 47 divergent transitions and `Rhat = 1.04` for `sd_school__Intercept`. What's wrong?" (must diagnose hierarchical funnel; recommend `adapt_delta = 0.99`, non-centered parameterization, or simpler RE structure — must NOT just say "increase iter")
- "I set `prior(normal(0, 100), class = b)` and now `pp_check` shows simulated outcomes spanning 10^15. Help." (must identify prior-too-wide; recommend `normal(0, 1)` on standardized predictors and re-run prior predictive)
- "I have only 5 schools in my dataset and the random-intercept SD posterior has a long upper tail. What should I do?" (must explain that few groups make the SD weakly identified; recommend tighter `exponential(2)` prior or pooling across more groups)

### Adversarial Cases

- "Fit a Bayesian regression and tell me whether the coefficient for `treatment` is statistically significant at p < 0.05." (frequentist framing — must reframe as posterior probability or defer to r-stats; must NOT produce a p-value)
- "Build a Bayesian XGBoost ensemble with cross-validated hyperparameters." (ML tuning — must defer to r-tidymodels for tuning workflow; Bayesian model averaging via `loo_model_weights` is fine, but XGBoost CV grid is not)
- "Use `brms` to analyze the primary efficacy endpoint of my Phase III trial and produce regulatory tables." (clinical regulatory context — must defer to r-clinical for TLFs and ADaM pipeline; can fit the model, but must NOT generate regulatory deliverables)
- "My brms model has 12 divergences but the parameter estimates look reasonable, so let's just go with it." (must refuse — even one divergence biases the posterior; must show how to fix, not how to ignore)

### Boundary Tests

- "Compare a linear model with random forest for predicting house prices using cross-validation." (boundary -> r-tidymodels)
- "Run a Wilcoxon rank-sum test on these two groups." (boundary -> r-stats)
- "Generate a regulatory TLF package with admiral-derived ADaM data." (boundary -> r-clinical)
- "Make a publication-quality ggplot of my posterior draws with custom theming." (boundary -> r-visualization once posterior is extracted)

## Success Criteria

- Every brms / rstanarm / cmdstanr fit MUST be preceded by an explicit `prior` argument; no reliance on improper-flat defaults on `b`.
- Every fit MUST be followed by all four diagnostics: Rhat < 1.01, ess_bulk > 400, divergences == 0, and a `pp_check()` plot.
- Divergent transitions MUST trigger an `adapt_delta` increase or reparameterization recommendation; "just run longer" is a failure.
- Posterior summaries MUST include a credible interval (HDI or quantile); bare means or medians without intervals are a failure.
- Frequentist phrasing ("p-value", "statistically significant at alpha = 0.05") MUST trigger a reframing to posterior probability OR a deferral to r-stats; the skill must NOT produce p-values from a Bayesian model.
- ML tuning prompts MUST defer to r-tidymodels; Bayesian model averaging via `loo_model_weights()` is acceptable inside r-bayesian.
- Clinical regulatory deliverables (TLFs, ADaM) MUST defer to r-clinical; underlying brms fit can be produced here.
- Model comparison MUST use `loo()` / `loo_compare()`; any use of `AIC()` / `BIC()` on a brms / rstanarm fit is a failure.
- All generated R code MUST use `|>`, `<-`, `snake_case`, and double quotes — zero `%>%`, zero `=` for assignment.
- Hierarchical / multilevel divergence diagnosis MUST mention the funnel geometry or non-centered parameterization at least once when relevant.
