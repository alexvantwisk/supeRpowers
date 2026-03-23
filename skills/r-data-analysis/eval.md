# Eval: r-data-analysis

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use tidyverse functions (dplyr/tidyr) before suggesting alternatives?
2. Does output use `|>` (not `%>%`) and `<-` (not `=`) for all pipes and assignments?
3. Does output avoid statistical modeling (r-stats territory)?
4. Does output handle NA values explicitly when present?
5. Does output correctly use `across()` for column-wise operations?

## Test Prompts

1. **Happy path:** "Clean this CSV: fix column types, handle missing values, reshape from wide to long"
2. **Edge case:** "I have a 500-column dataset and need to apply the same transformation to columns matching a pattern"
3. **Boundary test:** "Run a t-test comparing group means" (boundary → r-stats)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
