# Eval: r-targets

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the `_targets.R` file include `tar_option_set(packages = ...)` declaring all packages used in target functions, rather than relying on `library()` calls inside those functions?
2. Are all target functions free of side effects -- no `write.csv()`, `saveRDS()`, `write_rds()`, or `sink()` to paths outside `tar_path()` / `_targets/` unless using `format = "file"`?
3. When the user asks to set up a brand-new R project from scratch, does the skill produce an explicit deferral naming r-project-setup?
4. Does the response place reusable functions in `R/` and load them via `tar_source()`, never defining multi-line functions inline in `_targets.R`?
5. Does the response avoid calling `tar_load()` or `tar_read()` inside target functions (invisible dependency that breaks the DAG)?
6. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%` or `drake` references?
7. When dynamic branching is shown, does the response use `pattern = map(...)` or `pattern = cross(...)` inside `tar_target()` and explain what each branch iterates over?

## Test Prompts

### Happy Path

- "Convert this analysis script into a targets pipeline: it reads a CSV, cleans data, fits a linear model, and generates a Quarto report with the results."
- "Show me how to use `tar_visnetwork()` to inspect my pipeline dependency graph and identify outdated targets."

### Edge Cases

- "I need dynamic branching to fit a separate model for each of 50 countries in my dataset, then aggregate all results into a single summary target." (Must use `pattern = map()` on the country-level target; must show aggregation back into a single target via `tar_combine()` or a downstream target that takes the branched output.)
- "Configure my targets pipeline to store intermediate results in AWS S3 instead of the local `_targets/` directory." (Must use `tar_option_set(repository = "aws")` with `tar_resources(aws = tar_resources_aws(...))`; must mention credentials configuration via environment variables.)
- "I use renv alongside targets for full reproducibility. What files do I commit and what do I gitignore?" (Must explicitly state: commit `renv.lock`, `.Rprofile`, `renv/activate.R`, `renv/settings.json`, `_targets.R`, `R/`; gitignore `_targets/`, `renv/library/`, `renv/staging/`.)

### Adversarial Cases

- "Set up a brand new R project from scratch with git, renv, a README, directory structure, and then add a targets pipeline." (Project scaffolding. Must defer to r-project-setup for the project scaffold. May describe `_targets.R` creation but must NOT generate `.gitignore`, `.Rprofile`, full directory trees, or call `usethis::use_git()`.)
- "Inside my `clean_data()` target function, I need to pivot_longer, left_join three tables, mutate 10 columns, and handle missing values. Write the full data wrangling code." (Data wrangling. Must defer to r-data-analysis. May show the target definition wrapper but must NOT provide detailed multi-step dplyr/tidyr transformation chains exceeding 5 verbs.)
- "My `fit_model` target takes 30 minutes. Profile it line-by-line and tell me which expression is the bottleneck." (Code profiling. Must defer to r-performance. May suggest pipeline-level parallelism via `tar_make_future()` or crew, but must NOT provide `profvis()`, `Rprof()`, or `bench::mark()` code.)

### Boundary Tests

- "Create a new R project with git, renv, .gitignore, and proper directory structure." boundary -> r-project-setup
- "Write complex dplyr code for cleaning and reshaping messy survey data inside a target function." boundary -> r-data-analysis
- "Profile my slowest target and suggest code-level optimizations to cut its runtime in half." boundary -> r-performance

## Success Criteria

- Every `_targets.R` output includes `tar_option_set(packages = c(...))` with all packages needed by target functions; omitting this is a failure.
- No target function contains `write.csv()`, `saveRDS()`, `write_rds()`, `sink()`, or any file write to a user-specified path; all persistent output uses the targets store or `format = "file"` with `tar_path()`.
- Project scaffolding requests produce a deferral naming r-project-setup; the response does NOT contain `usethis::create_project()`, `usethis::use_git()`, or full `.gitignore` generation.
- Data wrangling requests produce a deferral naming r-data-analysis; the response does NOT contain multi-step dplyr pipelines with more than 5 chained verbs inside a target function body.
- Profiling requests produce a deferral naming r-performance; the response does NOT contain `profvis()`, `Rprof()`, or `bench::mark()`. It may suggest `crew` or `tar_make_future()` for parallelism.
- Dynamic branching edge case uses `pattern = map()` inside `tar_target()` and shows how branches are aggregated downstream.
- S3 storage edge case references `tar_resources_aws()` and environment variable credentials, not ad-hoc `aws.s3::put_object()` calls.
- renv integration edge case explicitly lists which files to commit vs. gitignore.
- No target function calls `tar_load()` or `tar_read()` internally.
- No output contains `%>%`, `library(magrittr)`, `drake::`, `=` for top-level assignment, or camelCase identifiers.
