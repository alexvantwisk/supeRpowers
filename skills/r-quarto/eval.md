# Eval: r-quarto

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output produce valid Quarto YAML and chunk syntax (not knitr-style)?
2. Does output use `|>` and `<-` in R code chunks?
3. Does output avoid package vignette specifics (r-package-dev territory)?
4. Does output use `#|` prefix for chunk options (not `{r, option=value}`)?
5. Does output include cross-reference labels with correct prefixes (fig-, tbl-)?

## Test Prompts

1. **Happy path:** "Create a parameterized Quarto report with year as a parameter that renders to HTML and PDF"
2. **Edge case:** "Set up a Quarto website with 3 pages and GitHub Pages deployment"
3. **Boundary test:** "Write a package vignette for my R package" (boundary → r-package-dev)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
