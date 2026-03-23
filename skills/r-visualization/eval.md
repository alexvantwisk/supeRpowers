# Eval: r-visualization

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output produce syntactically correct ggplot2 code with proper `+` layer chaining?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid generating Shiny reactive code (r-shiny territory)?
4. Does output use a colorblind-safe palette?
5. Does output include appropriate labels, theme, and figure dimensions?

## Test Prompts

1. **Happy path:** "Create a faceted scatterplot of mpg vs weight by cylinder count"
2. **Edge case:** "Plot 100,000 points without overplotting"
3. **Boundary test:** "Create an interactive dashboard with filters" (boundary → r-shiny)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
