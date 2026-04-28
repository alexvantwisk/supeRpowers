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
8. When asked about S7 vs S4 for a new class hierarchy, does the skill recommend S7 as the default for greenfield work?
9. When asked about a release workflow, does the skill mention `usethis::use_release_issue()` rather than walking through manual steps?

## Test Prompts

### Happy Path

- "I have a package with 5 functions. Add roxygen2 documentation to all exported functions, update the NAMESPACE, and set up a pkgdown site."
- "Prepare my package for CRAN submission. Walk me through the checklist: DESCRIPTION fields, LICENSE, NEWS.md, R CMD check, and any common pitfalls."

### Edge Cases

- "I'm getting NAMESPACE conflicts -- my package exports a function called `filter` and it clashes with dplyr. How do I handle this without renaming my function?"
- "I have S4 classes with methods that need proper registration. The `setMethod()` calls work interactively but `R CMD check` says the methods aren't found."
- "Before I submit my update to CRAN, I need to run reverse dependency checks. My package has 47 reverse dependencies. Walk me through the process."
- "I have an S4 class hierarchy with three classes (Animal, Dog extends Animal, Cat extends Animal) plus methods. Walk me through migrating to S7 step-by-step."
- "Open a release issue using `usethis::use_release_issue()` and walk me through the checklist for a 0.4.0 minor release. My package has no reverse dependencies."

### Adversarial Cases

- "Create a new R package called 'mytools' with a basic structure -- just the skeleton, no functions yet." (boundary: pure scaffolding should defer to r-project-setup)
- "Write comprehensive testthat tests for the three exported functions in my package: parse_config(), validate_schema(), and transform_data()." (boundary: test writing should defer to r-tdd)
- "I have an R package called 'surveyor'. Generate a Claude Code skill YAML and SKILL.md from its exported API." (boundary: should defer to r-package-skill-generator)

### Boundary Tests

- "Set up a new R project with renv, git, and a standard directory layout." boundary -> r-project-setup
- "Create a test file with edge case tests for my string parsing function." boundary -> r-tdd
- "Turn my internal R package into a plugin skill for Claude Code." boundary -> r-package-skill-generator

## Success Criteria

### Required content (positive criteria)

- Happy-path roxygen response MUST include **all five** of:
  - `@param` for every argument
  - `@returns` (or `@return`)
  - `@examples`
  - `@export`
  - An explicit `devtools::document()` invocation
- CRAN-readiness response MUST include **all five** of:
  - `devtools::check(cran = TRUE)` (or `R CMD check --as-cran`)
  - `urlchecker::url_check()` (or `urlchecker`)
  - `spelling::spell_check_package()` (or `spelling`)
  - `cran-comments.md`
  - `NEWS.md`
- NAMESPACE conflict response MUST mention **at least two** of:
  - selective `@importFrom`
  - `pkg::fn()` qualified calls
  - `usethis::use_import_from()`
  - package-level conflict resolution (`conflicted` or `.conflicts.OK`)
- S4 method registration response MUST mention **at least two** of:
  - `setGeneric()` / `setMethod()`
  - `@include` collation tag
  - `Collate:` field in `DESCRIPTION`
  - `methods::existsMethod()` for verification
- Reverse dependency response MUST reference one of: `revdepcheck::revdep_check()`,
  `revdepcheck` package, or `--with-revdep` flag of `release_checklist.R`.
- S7 migration response MUST mention **all three** of: `S7::new_class`,
  property syntax (`@prop`), `S7::method()`-style generic registration.

### Forbidden content (negative criteria)

- Pure scaffolding prompt MUST be deferred to `r-project-setup`; response
  MUST NOT contain `usethis::create_package()`.
- Test-writing prompt MUST be deferred to `r-tdd`; response MUST NOT contain
  `test_that()` blocks.
- Skill-generation prompt MUST be deferred to `r-package-skill-generator`;
  response MUST NOT contain SKILL.md content.
- Response MUST NOT use `:::` to access internal functions in other packages.
- Response MUST NOT skip or downplay `R CMD check` for any workflow that
  touches NAMESPACE or exports.
- Response MUST NOT use `%>%`, `=` for assignment, or single quotes for strings.
- Response MUST NOT recommend `@docType package` (deprecated) — must use
  `_PACKAGE` sentinel.
