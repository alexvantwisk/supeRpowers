# Eval: r-package-skill-generator

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output follow the 4-step process (scan → dispatch agents → synthesize → hand off)?
2. Does output focus on primary package workflows rather than listing every function?
3. Does output avoid manually writing skill content (uses skill-creator for handoff)?
4. Does output check for existing skills before generating a new one?
5. Does generated SKILL.md stay under 300 lines?

## Test Prompts

1. **Happy path:** "Generate a skill for the janitor R package: https://github.com/sfirke/janitor"
2. **Edge case:** "Create a skill for data.table — it has over 200 exported functions"
3. **Boundary test:** "Write a new skill from scratch for my custom workflow" (boundary → skill-creator)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
