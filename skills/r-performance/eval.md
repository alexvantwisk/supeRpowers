# Eval: r-performance

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output profile before suggesting optimizations?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid general data wrangling (r-data-analysis territory)?
4. Does output benchmark with `bench::mark()` to verify improvement?
5. Does output address the actual bottleneck (not premature optimization)?

## Test Prompts

1. **Happy path:** "This function takes 30 seconds on 1M rows — profile and optimize it"
2. **Edge case:** "Convert this dplyr pipeline to data.table for a 50M row dataset"
3. **Boundary test:** "Clean and reshape this CSV file" (boundary → r-data-analysis)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
