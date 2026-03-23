# Eval: r-stats

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output check model assumptions before interpreting results?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid ML prediction pipelines (r-tidymodels territory)?
4. Does output use `broom::tidy()` for clean coefficient output?
5. Does output report confidence intervals alongside point estimates?

## Test Prompts

1. **Happy path:** "Fit a linear model of mpg ~ wt + hp, check assumptions, report results"
2. **Edge case:** "My logistic regression has complete separation — what do I do?"
3. **Boundary test:** "Tune an XGBoost model with cross-validation" (boundary → r-tidymodels)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
