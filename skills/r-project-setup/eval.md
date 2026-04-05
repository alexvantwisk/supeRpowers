# Eval: r-project-setup

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does every scaffolded project include an `renv::init()` call or explicit renv initialization step as part of the setup?
2. Does the generated `.gitignore` include R-specific entries at minimum: `.Rhistory`, `.RData`, `.Rproj.user/`, and `renv/library/`?
3. When the user asks to add roxygen2 documentation to an existing package, does the skill produce an explicit deferral naming r-package-dev?
4. Does the scaffold avoid `setwd()` anywhere, using project-relative paths or `here::here()` instead?
5. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%`?
6. Does the scaffold include an `.Rprofile` that sources `renv/activate.R` for automatic renv activation?
7. When asked to set up a targets pipeline with branching and orchestration logic, does the skill defer to r-targets rather than designing the pipeline?

## Test Prompts

### Happy Path

- "Set up a new data analysis R project for exploring the penguins dataset with renv, git, a starter script, and proper directory structure."
- "Scaffold a new R package with usethis, including a basic DESCRIPTION, NAMESPACE, test infrastructure with testthat, and renv."

### Edge Cases

- "I have an existing R project with 50 scripts and no renv. Add dependency management without breaking my current library." (Must use `renv::init()` with existing package detection; must mention `renv::status()` and `renv::snapshot()` for resolving version conflicts; must warn about potential version discrepancies between system library and renv library.)
- "Generate a GitHub Actions CI/CD scaffold for an R analysis project that runs R CMD check, lints with lintr, and renders a Quarto report on push to main." (Must create `.github/workflows/` with a YAML workflow file; must use `r-lib/actions` for R setup and caching; must not over-engineer with Docker unless asked.)
- "I have a monorepo with three separate R projects in subdirectories: a package, a Shiny app, and an analysis. Set up each with its own renv and a shared CI config." (Must create separate `renv.lock` per subdirectory with per-project `.Rprofile` activation; must NOT merge all dependencies into a single lockfile.)

### Adversarial Cases

- "Add roxygen2 documentation to all exported functions in my existing R package and regenerate the NAMESPACE." (Ongoing package development. Must defer to r-package-dev. Must NOT produce `roxygen2::roxygenise()`, `devtools::document()`, or roxygen comment blocks.)
- "Set up a full targets pipeline with dynamic branching, S3 storage, and parallel execution for my analysis project." (Pipeline orchestration. Must defer to r-targets. May include a stub `_targets.R` as part of initial scaffold but must NOT define actual targets with `tar_target()`, `pattern = map()`, or `tar_option_set(repository = "aws")`.)
- "Configure my Shiny app for deployment to shinyapps.io with authentication, environment variables, and a custom domain." (Shiny deployment. Must defer to r-shiny. Must NOT produce `rsconnect::deployApp()`, `rsconnect::setAccountInfo()`, or authentication configuration.)

### Boundary Tests

- "Add a new exported function with roxygen2 docs and unit tests to my R package." boundary -> r-package-dev
- "Design a targets pipeline with 10 targets, dynamic branching, and crew-based parallelism." boundary -> r-targets
- "Set up rsconnect deployment with environment variables and authentication for my Shiny app." boundary -> r-shiny

## Success Criteria

- Every project scaffold includes `renv::init()` or an explicit renv initialization step; omitting dependency management is a failure.
- Every scaffold includes a `.gitignore` with at least `.Rhistory`, `.RData`, `.Rproj.user/`, and `renv/library/`; a missing or incomplete `.gitignore` is a failure.
- Roxygen2 request produces a deferral naming r-package-dev and does NOT contain `roxygen2::roxygenise()`, `devtools::document()`, `#' @export`, or roxygen comment blocks.
- Targets pipeline request produces a deferral naming r-targets and does NOT contain `tar_target()` with actual function bodies, `pattern = map()`, or `tar_resources_aws()`. A stub `_targets.R` with a comment placeholder is acceptable.
- Shiny deployment request produces a deferral naming r-shiny and does NOT contain `rsconnect::deployApp()`, `rsconnect::setAccountInfo()`, or shinyapps.io configuration.
- No scaffold uses `setwd()` or hard-coded absolute paths; all paths use `here::here()` or project-relative notation.
- CI/CD scaffold includes at least: R version specification, dependency caching with `r-lib/actions`, and the primary check/test/lint command.
- Monorepo edge case creates separate `renv.lock` files per subdirectory, not one shared lockfile; each subdirectory has its own `.Rprofile` sourcing its own `renv/activate.R`.
- Existing-project renv edge case mentions `renv::status()` for conflict detection and does NOT suggest deleting the existing system library.
- No output contains `%>%`, `library(magrittr)`, `=` for top-level assignment, or camelCase identifiers.
