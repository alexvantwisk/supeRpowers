# Eval: r-tidymodels

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to build a classification model, does the response place ALL preprocessing (imputation, normalization, dummy encoding) inside a `recipe()` and never in standalone `mutate()` or `scale()` calls before the recipe?
2. Does the response evaluate model performance exclusively on held-out data or resamples, never reporting final metrics computed on the training set?
3. When the user asks to "interpret odds ratios from a logistic regression," does the skill produce an explicit deferral naming r-stats instead of generating coefficient tables or confidence intervals?
4. When class imbalance is present, does the response address it via resampling steps (`step_smote()`, `step_downsample()`), stratified splits, or class-appropriate metrics (`pr_auc`, `bal_accuracy`) rather than silently using `accuracy`?
5. When dynamic feature engineering involves date/time columns, does the recipe use `step_date()` / `step_holiday()` inside the recipe rather than manual `mutate()` calls outside it?
6. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%` or `=` for variable assignment?
7. Does the response use `finalize_workflow()` before `last_fit()` or `fit()` after tuning, leaving no unresolved `tune()` placeholders in the final model?

## Test Prompts

### Happy Path

- "Build a random forest classifier for customer churn with 10-fold cross-validation and hyperparameter tuning via Bayesian optimization. The dataset has 20 numeric and 5 categorical features."
- "Compare three model types (logistic regression, XGBoost, elastic net) on this dataset using a workflow set and select the best by ROC AUC."

### Edge Cases

- "I normalized my features before calling `initial_split()`. My AUC is 0.99 on a messy dataset. What is wrong?" (Must identify data leakage; must explain that normalization belongs inside the recipe applied per resample fold, not before the split.)
- "My binary outcome has 95% negatives and 5% positives. Build me a tidymodel." (Must address class imbalance in preprocessing or metric selection; must not use `accuracy` as the primary metric.)
- "Set up nested cross-validation so I can get an unbiased estimate of tuned model performance." (Must show two distinct resampling layers -- inner loop for tuning, outer loop for honest performance estimation -- and not conflate them.)

### Adversarial Cases

- "Interpret the odds ratios from my logistic regression model and tell me which predictors are statistically significant." (Inference task. Must defer to r-stats. Must NOT produce p-values, confidence intervals, or coefficient interpretation.)
- "Evaluate whether the primary endpoint of my Phase III trial shows superiority using tidymodels." (Clinical trial. Must defer to r-clinical. Must NOT produce hazard ratios, survival curves, or regulatory analysis.)
- "Evaluate my model's performance -- it's running too slowly on a large dataset." (Ambiguous. If the user means execution speed, must defer to r-performance. If predictive performance, stay in scope. Response must clarify or default to deferral for the profiling aspect.)

### Boundary Tests

- "Run a paired t-test to compare two models' cross-validation AUCs for statistical significance." boundary -> r-stats
- "Calculate the hazard ratio for my survival analysis trial endpoint." boundary -> r-clinical
- "My `tune_grid()` call takes 45 minutes. Profile it and tell me which recipe step is the bottleneck." boundary -> r-performance

## Success Criteria

- All recipe steps appear inside `recipe() |> step_*()` chains; no preprocessing via standalone `mutate()`, `scale()`, or `normalize()` before the recipe. Any output that transforms data prior to `initial_split()` is a failure.
- Model evaluation uses `collect_metrics()` on resamples or `augment()` + yardstick on the test set; training-set metrics never appear as final results.
- Adversarial prompt about odds ratios produces an explicit deferral statement naming r-stats and does NOT contain `tidy()` with `exponentiate = TRUE`, `confint()`, or p-value tables.
- Clinical trial prompt produces an explicit deferral statement naming r-clinical and does NOT contain `survfit()`, `coxph()`, or hazard ratio output.
- Ambiguous performance prompt either clarifies the user's intent or defers the profiling aspect to r-performance; it does NOT contain `Rprof()`, `profvis()`, or `bench::mark()`.
- Class imbalance edge case includes at least one of: recipe resampling step, stratified split via `strata =`, or class-weighted metric; output must NOT use `accuracy` as the sole metric.
- Nested CV response shows two distinct resampling layers (inner and outer) and does not conflate tuning with evaluation.
- No output contains `%>%`, `library(magrittr)`, `=` for top-level assignment, or camelCase identifiers.
