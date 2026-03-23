# Eval: r-tidymodels

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use the workflow() → fit_resamples() → collect_metrics() pattern?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid inferential statistics (r-stats territory)?
4. Does output keep preprocessing inside a recipe (no data leakage)?
5. Does output set a random seed before cross-validation splits?

## Test Prompts

1. **Happy path:** "Build a random forest classifier for customer churn with hyperparameter tuning"
2. **Edge case:** "My model predictions are suspiciously good — could there be data leakage?"
3. **Boundary test:** "Test whether the treatment effect is statistically significant" (boundary → r-stats)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
