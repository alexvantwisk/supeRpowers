# Eval: r-stats

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to fit a linear model, does the skill check distributional assumptions (normality, homoscedasticity) BEFORE interpreting coefficients?
2. Does the skill report confidence intervals alongside every point estimate and p-value?
3. When complete separation is detected in logistic regression, does the skill warn and suggest penalized methods (Firth) rather than silently returning infinite coefficients?
4. Does the skill refuse to interpret a p-value as "the probability that the null hypothesis is true"?
5. When asked to predict customer churn using logistic regression with threshold tuning, does the skill defer to r-tidymodels?
6. When asked to analyze a clinical trial primary endpoint, does the skill defer to r-clinical?
7. Does the skill use `|>` and `<-` exclusively (never `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "Fit a linear regression of mpg on wt and hp using mtcars. Check assumptions and report results."
- "Run a two-sample t-test comparing treatment and control groups. Report effect size and CI."

### Edge Cases

- "I ran logistic regression and got a coefficient of 23.7 with SE of 8432. What is happening?" (complete separation -- must identify and recommend Firth logistic regression or exact methods)
- "My lmer model gives a singular fit warning. The random intercept variance is near zero. What should I do?" (must explain boundary estimation, suggest simplifying random structure, NOT ignore the warning)
- "Run a one-way ANOVA on three groups with n=5, n=150, and n=12. Are the results trustworthy?" (unequal sample sizes -- must discuss Welch ANOVA or non-parametric alternatives, not default to standard ANOVA)

### Adversarial Cases

- "Predict customer churn with logistic regression, tune the decision threshold, and evaluate AUC on a test set." (ML prediction workflow -- must defer to r-tidymodels, not attempt train/test split and threshold optimization)
- "Run a t-test on the primary efficacy endpoint from my Phase III trial and determine if we met the pre-specified alpha." (clinical trial analysis -- must defer to r-clinical for regulatory context, multiplicity, and protocol-driven analysis)
- "Fit a mixed-effects model and create a publication-ready coefficient plot with forest-plot styling." (must fit the model but defer visualization to r-visualization; must NOT generate ggplot2 code inline)

### Boundary Tests

- "Build a random forest to predict house prices and compare it to a linear model using cross-validation." (boundary -> r-tidymodels)
- "Create a Table 1 showing regression results formatted for a journal submission." (boundary -> r-tables)
- "Analyze the time-to-event primary endpoint in my oncology trial with stratified log-rank test." (boundary -> r-clinical)

## Success Criteria

- Every model output MUST include assumption checks (at minimum: residual diagnostics for lm/glm, convergence checks for mixed models).
- Every hypothesis test MUST report a confidence interval; bare p-values without CI are a failure.
- Complete separation MUST be identified by name and paired with an actionable fix (Firth, exact logistic, or Bayesian prior).
- Singular fit warnings MUST be explained, not suppressed or ignored.
- Adversarial prompts crossing into r-tidymodels territory (threshold tuning, cross-validation, prediction pipelines) MUST trigger a deferral, not inline ML code.
- Adversarial prompts about clinical trial endpoints MUST trigger a deferral to r-clinical; the skill must NOT perform regulatory-context analysis.
- Visualization requests MUST be handed off to r-visualization; the skill must NOT emit ggplot2 code beyond a bare diagnostic plot (e.g., `plot(model)` is acceptable, custom ggplot theming is not).
- All generated R code MUST use `|>`, `<-`, snake_case, and double quotes.
