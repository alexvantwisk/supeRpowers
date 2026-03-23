# Eval: r-clinical

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use correct clinical trial conventions (CDISC terminology, CNSR coding)?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid general statistical methodology (r-stats territory)?
4. Does output specify censoring correctly in `Surv()` calls?
5. Does output address regulatory requirements when applicable?

## Test Prompts

1. **Happy path:** "Create a Kaplan-Meier survival curve for OS by treatment arm with log-rank test"
2. **Edge case:** "Analyze time-to-event with competing risks (death vs relapse)"
3. **Boundary test:** "Fit a Cox proportional hazards model with time-varying covariates" (boundary → r-stats)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
