# Eval: r-tables

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output produce valid gt/gtsummary code?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid generating plots (r-visualization territory)?
4. Does output use `as_gt()` when piping gtsummary to gt functions?
5. Does output handle missing value display explicitly?

## Test Prompts

1. **Happy path:** "Create a demographics Table 1 with gtsummary showing age, sex, BMI by treatment group"
2. **Edge case:** "Merge two gtsummary tables side by side with tbl_merge"
3. **Boundary test:** "Create a bar chart showing patient counts by group" (boundary → r-visualization)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
