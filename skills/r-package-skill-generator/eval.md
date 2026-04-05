# Eval: r-package-skill-generator

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the generated SKILL.md include a `description` field that starts with "Use when..." and contains at least 5 trigger phrases?
2. Does the generated SKILL.md include at least one "Do NOT use for..." negative boundary referencing a sibling skill?
3. Does the generated SKILL.md (including frontmatter) stay within the 300-line hard limit, with reference files also each under 300 lines?
4. When the user asks to "explain how to use dplyr," does the skill produce an explicit deferral naming r-data-analysis instead of generating a skill file?
5. Does the response use `|>` exclusively and `<-` for assignment in all generated R code examples, with zero instances of `%>%`?
6. When the user asks to develop or maintain an R package (write functions, add tests, manage NAMESPACE), does the skill defer to r-package-dev?
7. Does the generated skill include lazy reference pointers (`Read \`references/...\` for...`) when reference files are created?

## Test Prompts

### Happy Path

- "Generate a Claude skill from this R package: https://github.com/tidyverse/dplyr"
- "Make Claude an expert at using the gt package. Here's the repo: https://github.com/rstudio/gt"

### Edge Cases

- "Generate a skill from a package that exports 200+ functions (e.g., data.table). How do you prioritize what goes in the SKILL.md vs. references?" (Must demonstrate a triage strategy: core workflows in SKILL.md, grouped reference files by topic, explicit omission of internal/deprecated functions. Must NOT dump all 200+ functions into SKILL.md.)
- "Generate a skill from a Bioconductor package with a deep S4 class hierarchy (e.g., SummarizedExperiment). How do you handle the OOP complexity?" (Must document the class structure and key methods/accessors, not just top-level function signatures. Must address slot access patterns and inheritance.)
- "Generate a skill from a package that is mostly C++ internals with thin R wrappers (e.g., RcppArmadillo). How do you handle the documentation gap?" (Must focus on the R-facing API, acknowledge the C++ internals without trying to document them, and flag functions with minimal R-level documentation.)

### Adversarial Cases

- "Explain how to use dplyr for data manipulation -- filter, mutate, group_by, summarize with examples." (Package usage question. Must defer to r-data-analysis. Must NOT initiate the clone-explore-synthesize skill generation pipeline.)
- "I want to write a skill manually for my internal package. Walk me through the SKILL.md format and frontmatter requirements." (Manual skill authoring. Must defer to skill-creator. Must NOT run the automated generation pipeline.)
- "Help me develop my R package: add exported functions, write unit tests, set up CI, and submit to CRAN." (Package development. Must defer to r-package-dev. Must NOT treat this as a skill generation request.)

### Boundary Tests

- "Show me how to use purrr::map() to iterate over a list of data frames." boundary -> r-data-analysis
- "Create an R package from scratch with usethis and devtools." boundary -> r-package-dev
- "Review this skill I wrote and tell me if it follows the plugin format correctly." boundary -> skill-auditor

## Success Criteria

- Generated SKILL.md has valid YAML frontmatter with exactly two fields: `name` and `description`. The `description` starts with "Use when..." and contains 5+ comma-separated trigger phrases and at least one "Do NOT use for..." boundary. Missing trigger phrases or missing negative boundaries is a failure.
- Generated SKILL.md is 300 lines or fewer; each generated reference file is 300 lines or fewer. Exceeding either limit is a failure.
- Package usage questions ("explain how to use X," "show me how to do Y with Z package") produce a deferral naming the appropriate domain skill (r-data-analysis, r-visualization, etc.) and do NOT initiate repository cloning or skill generation.
- Manual skill writing requests produce a deferral naming skill-creator and do NOT run the automated generation workflow.
- Package development requests produce a deferral naming r-package-dev and do NOT produce SKILL.md output.
- For packages with 200+ exports, the response demonstrates explicit triage: core functions in SKILL.md body, secondary functions grouped into topical reference files, internal/deprecated functions omitted with justification. A flat list of all exports is a failure.
- For S4/R5/R6 class hierarchies, the generated skill documents class constructors, key accessors/methods, and inheritance relationships, not just function names.
- For C++-heavy packages, the generated skill focuses on the R API surface and flags thin-wrapper functions with limited documentation.
- Generated reference files are organized by topic (not alphabetically by function name) and each includes a brief description of when to consult that reference.
- All R code examples in generated skills use `|>`, `<-`, `snake_case`, and double quotes. Any `%>%`, `=` for assignment, or camelCase in generated output is a failure.
