# Eval: r-debugging

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output follow the reproduce-isolate-diagnose-fix-test workflow?
2. Does output use `|>` and `<-` in any R code shown?
3. Does output fix only the bug without refactoring surrounding code?
4. Does output identify the specific failure point (not just suggest generic strategies)?
5. Does output include a regression test or verification step?

## Test Prompts

1. **Happy path:** "My function returns NA for some inputs but I don't know which ones"
2. **Edge case:** "This code gives wrong results but no error — vector recycling might be the issue"
3. **Boundary test:** "Profile my code and make it faster" (boundary → r-performance)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
