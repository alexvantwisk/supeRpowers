# Eval: r-shiny

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use proper Shiny module patterns with `ns()` wrapping?
2. Does output use `|>` and `<-` in server code?
3. Does output avoid generating standalone ggplot code without Shiny context (r-visualization territory)?
4. Does output include `req()` for input validation?
5. Does output correctly handle reactive invalidation?

## Test Prompts

1. **Happy path:** "Build a Shiny module that takes a dataset and renders a filtered table"
2. **Edge case:** "My module's renderUI output doesn't respond to input changes"
3. **Boundary test:** "Create a publication-quality ggplot2 figure with custom theme" (boundary → r-visualization)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
