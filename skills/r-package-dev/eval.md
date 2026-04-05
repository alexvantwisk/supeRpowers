# Eval: r-package-dev

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked only to scaffold a new R package from scratch with no further development, does the skill defer to r-project-setup?
2. When asked to write unit tests for package functions, does the skill defer to r-tdd rather than producing testthat code itself?
3. When the user asks to generate a Claude Code skill from an existing R package, does the skill defer to r-package-skill-generator?
4. Does the skill recommend `R CMD check` (or `devtools::check()`) as a mandatory step before any CRAN submission guidance?
5. When documenting exported functions, does the skill use roxygen2 `@export` tags rather than manual NAMESPACE editing?
6. When the user needs to access an internal function from another package, does the skill recommend `::` or re-exporting rather than `:::`?
7. Does all generated code use `|>` and `<-` exclusively (no `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "I have a package with 5 functions. Add roxygen2 documentation to all exported functions, update the NAMESPACE, and set up a pkgdown site."
- "Prepare my package for CRAN submission. Walk me through the checklist: DESCRIPTION fields, LICENSE, NEWS.md, R CMD check, and any common pitfalls."

### Edge Cases

- "I'm getting NAMESPACE conflicts -- my package exports a function called `filter` and it clashes with dplyr. How do I handle this without renaming my function?"
- "I have S4 classes with methods that need proper registration. The `setMethod()` calls work interactively but `R CMD check` says the methods aren't found."
- "Before I submit my update to CRAN, I need to run reverse dependency checks. My package has 47 reverse dependencies. Walk me through the process."

### Adversarial Cases

- "Create a new R package called 'mytools' with a basic structure -- just the skeleton, no functions yet." (boundary: pure scaffolding should defer to r-project-setup)
- "Write comprehensive testthat tests for the three exported functions in my package: parse_config(), validate_schema(), and transform_data()." (boundary: test writing should defer to r-tdd)
- "I have an R package called 'surveyor'. Generate a Claude Code skill YAML and SKILL.md from its exported API." (boundary: should defer to r-package-skill-generator)

### Boundary Tests

- "Set up a new R project with renv, git, and a standard directory layout." boundary -> r-project-setup
- "Create a test file with edge case tests for my string parsing function." boundary -> r-tdd
- "Turn my internal R package into a plugin skill for Claude Code." boundary -> r-package-skill-generator

## Success Criteria

- Happy path roxygen2 response MUST include `@export`, `@param`, `@return`, and `@examples` tags and MUST use `devtools::document()` to regenerate NAMESPACE.
- CRAN submission response MUST include `devtools::check()` with zero errors/warnings/notes as a gate, and MUST mention `urlchecker`, `rhub`, or `win-builder` for cross-platform validation.
- NAMESPACE conflict response MUST discuss `.conflicts.OK`, selective importing via `@importFrom`, or package-level conflict resolution -- not just "rename your function."
- S4 method registration response MUST address `setGeneric()`/`setMethod()` collation order, `@include` roxygen tags, or Collate field in DESCRIPTION.
- Reverse dependency check response MUST reference `revdepcheck::revdep_check()` or an equivalent workflow, not suggest manually installing all 47 packages.
- Pure scaffolding prompt MUST be deferred to r-project-setup; response must NOT produce `usethis::create_package()` code.
- Test-writing prompt MUST be deferred to r-tdd; response must NOT contain `test_that()` blocks.
- Skill generation prompt MUST be deferred to r-package-skill-generator; response must NOT produce SKILL.md content.
- Response must NOT use `:::` to access internal functions in other packages; it must recommend `::` or re-exporting.
- Response must NOT skip or downplay `R CMD check`; every workflow that touches NAMESPACE or exports MUST include a check step.
- Response must NOT use `%>%`, `=` for assignment, or single quotes for strings.
