# Eval: r-tdd

> Development-only. Not loaded by the plugin (plugin.json globs match SKILL.md only).

## Binary Eval Questions

Answer YES or NO after running the skill on a test prompt.

1. Does output follow RED-GREEN-REFACTOR cycle (test first, then implement)?
2. Does output use `|>` and `<-` per conventions?
3. Does output avoid R CMD check or package quality gates (r-package-dev territory)?
4. Does output write the failing test BEFORE any implementation code?
5. Does output use testthat 3e conventions (test_that + expect_* pattern)?

## Test Prompts

1. **Happy path:** "Write tests for a function that validates email addresses, then implement it"
2. **Edge case:** "Test a function that writes to a temporary file — how do I clean up?"
3. **Boundary test:** "Run R CMD check on my package" (boundary → r-package-dev)

## Success Criteria

- Score ≥4/5 on binary eval questions
- Boundary test correctly defers to sibling skill or states boundary
- All output code follows r-conventions (|>, <-, snake_case, double quotes)
- Output stays within skill's territory (no Overachiever drift)
