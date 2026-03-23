# Eval: r-targets

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output produce a valid _targets.R file with tar_target calls?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid initial project scaffolding (r-project-setup territory)?
4. Does output keep tar_load() out of target functions?
5. Does output include tar_visnetwork() for pipeline visualization?

## Test Prompts

1. **Happy path:** "Convert this analysis script into a targets pipeline"
2. **Edge case:** "Add dynamic branching to fit separate models for each country"
3. **Boundary test:** "Set up a new R project from scratch with git and renv" (boundary → r-project-setup)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
