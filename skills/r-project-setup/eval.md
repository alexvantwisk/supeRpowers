# Eval: r-project-setup

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use usethis functions for project scaffolding?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid ongoing package development (r-package-dev territory)?
4. Does output initialize renv for dependency management?
5. Does output initialize git with usethis::use_git()?

## Test Prompts

1. **Happy path:** "Set up a new analysis project with renv, git, and a starter script"
2. **Edge case:** "Add renv to my existing R project that has 50 scripts"
3. **Boundary test:** "Add a new exported function to my R package with roxygen docs" (boundary → r-package-dev)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
