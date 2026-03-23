# Eval: r-package-dev

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output use `usethis`/`devtools` workflow correctly?
2. Does output use `|>` and `<-` in code examples?
3. Does output avoid writing test methodology (r-tdd territory)?
4. Does output use `@importFrom` instead of `@import`?
5. Does output include `devtools::document()` and `devtools::check()` steps?

## Test Prompts

1. **Happy path:** "Create a new R package with one exported function, roxygen docs, and a vignette"
2. **Edge case:** "My NAMESPACE has conflicts between tidy eval and another package"
3. **Boundary test:** "Write testthat tests for my function using TDD" (boundary → r-tdd)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
