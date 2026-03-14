# Phase 1: Foundation + Core Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (a pre-installed skill from the superpowers plugin — it orchestrates parallel subagent execution with two-stage review) to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking. **CRITICAL:** When creating any SKILL.md file, you MUST invoke the `superpowers:writing-skills` skill FIRST before writing. This is non-negotiable.

**Goal:** Deliver the foundation layer (plugin manifest + R conventions rule) and four core skills (r-data-analysis, r-visualization, r-tdd, r-debugging) plus one shared agent (r-code-reviewer) for the supeRpowers Claude Code marketplace plugin.

**Architecture:** Layered plugin — a rules file defines shared R conventions inherited by all skills. Each skill is a self-contained directory with SKILL.md (max 300 lines body) and optional references/ directory. The shared agent lives at `.claude/agents/` and can be dispatched from any skill. All R code follows tidyverse-first conventions with base pipe (`|>`).

**Tech Stack:** Claude Code skills/agents (YAML frontmatter + markdown), R >= 4.1.0, tidyverse ecosystem, testthat 3e, styler, lintr, renv.

**Spec:** `.claude/plans/2026-03-15-superpowers-r-plugin-design.md`

**Prerequisites:**
- `superpowers:writing-skills` — Pre-installed skill from the superpowers plugin. Guides proper SKILL.md authoring (frontmatter, structure, validation). Available via `Skill: superpowers:writing-skills`. If unavailable, use the existing `r-package-skill-generator/SKILL.md` as a structural template and ensure YAML frontmatter contains `name` and `description` fields.
- `superpowers:subagent-driven-development` — Pre-installed orchestration skill for parallel task execution.

**Version note:** `plugin.json` uses `0.1.0` (not `1.0.0` from spec) because this is Phase 1 of 4. Version will bump to `1.0.0` when all phases are complete.

**Path convention:** Paths in `plugin.json` are relative to `.claude/`. The Claude Code plugin resolver prepends `.claude/` when installing the plugin subtree. If this assumption proves wrong during testing, update paths to include the `.claude/` prefix.

---

## Chunk 1: Foundation (plugin.json + r-conventions.md)

These two files must exist before any skills, as skills depend on the conventions rule.

### Task 1: Create plugin.json manifest

**Files:**
- Create: `plugin.json`

- [ ] **Step 1: Create plugin.json**

```json
{
  "name": "supeRpowers",
  "version": "0.1.0",
  "description": "Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, and biostatistics.",
  "keywords": ["r", "rstats", "tidyverse", "shiny", "biostatistics", "clinical-trials"],
  "author": "Alexander van Twisk",
  "license": "MIT",
  "claude_code": {
    "min_version": "1.0.0",
    "rules": ["rules/r-conventions.md"],
    "skills": ["skills/*/SKILL.md"],
    "agents": ["agents/*.md"]
  }
}
```

Write this file to the project root: `plugin.json`

- [ ] **Step 2: Commit**

```bash
git add plugin.json
git commit -m "feat: add plugin.json manifest for supeRpowers"
```

### Task 2: Create r-conventions.md rule

**Files:**
- Create: `.claude/rules/r-conventions.md`

This is the foundation rule loaded into every R interaction. Max 150 lines. Concise reference card format.

- [ ] **Step 1: Create the rules directory and r-conventions.md**

Write `.claude/rules/r-conventions.md` with the following content. This is a rules file, NOT a skill — no YAML frontmatter needed. It should be a direct, imperative reference card.

```markdown
# R Conventions

These conventions apply to ALL R code generated, reviewed, or discussed in this project.

## Pipe Operator

ALWAYS use the base pipe `|>`. NEVER use magrittr `%>%`.

```r
# CORRECT
mtcars |>
  filter(cyl == 6) |>
  summarise(mean_mpg = mean(mpg))

# WRONG
mtcars %>%
  filter(cyl == 6) %>%
  summarise(mean_mpg = mean(mpg))
```

If existing code uses `%>%`, match it for consistency but suggest migration to `|>`.

Note: `|>` requires R >= 4.1.0. The base pipe does not support the `.` placeholder — use anonymous functions instead: `x |> (\(d) lm(mpg ~ wt, data = d))()`.

## Paradigm

**Tidyverse-first.** Lead with dplyr, tidyr, purrr, ggplot2, readr, stringr, forcats, lubridate.

Mention base R or data.table alternatives when they are genuinely better:
- **data.table:** Large datasets (>1M rows), performance-critical inner loops, memory-constrained environments.
- **Base R:** Zero-dependency packages, simple one-liners where tidyverse is overkill.

## Style

- **Formatter:** `styler::tidyverse_style()`
- **Linter:** `lintr` with default tidyverse rules
- **Naming:** `snake_case` for functions, variables, and file names
- **Assignment:** `<-` for assignment, never `=`
- **Strings:** Double quotes `"` preferred
- **Line length:** 80 characters soft limit, 120 hard limit
- **Spacing:** Space after commas, around `<-`, around infix operators

## Environment Management

- **renv** for all projects. Check for `renv.lock` at project root.
- For new projects: suggest `renv::init()`.
- Before adding packages: `renv::install("pkg")` then `renv::snapshot()`.
- To restore: `renv::restore()`.

## R Version

Target R >= 4.1.0 (base pipe `|>` support). Flag code that requires features from newer R versions (e.g., R 4.2.0 `_` placeholder in pipes — avoid this, use anonymous functions instead).

## Package Development Toolchain

The canonical modern stack:
- `usethis` — project setup, CI, licensing, boilerplate
- `devtools` — development workflow (`load_all()`, `test()`, `check()`, `document()`)
- `roxygen2` — documentation with markdown support enabled (`use_roxygen_md()`)
- `testthat` 3rd edition — testing (`use_testthat(3)`)
- `pkgdown` — documentation sites
- `styler` — code formatting
- `lintr` — static analysis

## Documentation

- roxygen2 with markdown enabled (`Roxygen: list(markdown = TRUE)` in DESCRIPTION)
- `@examples` mandatory for all exported functions
- `@param` for every parameter — no undocumented args
- `@returns` for every function (not `@return`)
- Use `@family` to group related functions
- For tidy eval: use `@inheritParams rlang::args_data_masking` or document with `<data-masking>` / `<tidy-select>` tags

## Error Handling (in packages)

Use the cli package for user-facing messages:
```r
# Errors
cli::cli_abort("Column {.field {col}} not found in {.arg data}.")

# Warnings
cli::cli_warn("NAs introduced by coercion.")

# Information
cli::cli_inform("Processing {.val {n}} rows.")
```

For structured error handling: `rlang::try_fetch()` over `tryCatch()`.

For condition classes: use `rlang::abort(class = "pkg_error_type")` for programmatic catching.

## Tidy Evaluation

- **Embrace:** `{{ }}` for passing column names through functions
- **Data pronoun:** `.data$col` to refer to columns, `.env$var` for environment variables
- **Injection:** `!!` and `!!!` only when `{{ }}` is insufficient
- **Documentation:** Always document whether a function uses data-masking or tidy-select

```r
# CORRECT — embrace pattern
my_summary <- function(data, group_col, value_col) {
  data |>
    group_by({{ group_col }}) |>
    summarise(mean_val = mean({{ value_col }}, na.rm = TRUE))
}

# CORRECT — .data pronoun for string column names
my_filter <- function(data, col_name, threshold) {
  data |>
    filter(.data[[col_name]] > .env$threshold)
}
```

## File Organization

- One primary function per file in `R/`, named to match: `my_function()` lives in `R/my-function.R`
- Utility/helper functions can share a file: `R/utils.R`, `R/utils-validation.R`
- Keep files under 400 lines. Extract if growing beyond that.
```

- [ ] **Step 2: Verify line count is under 150**

```bash
wc -l .claude/rules/r-conventions.md
```

Expected: under 150 lines.

- [ ] **Step 3: Commit**

```bash
git add .claude/rules/r-conventions.md
git commit -m "feat: add r-conventions.md foundation rule"
```

---

## Chunk 2: Core Skills (parallel execution)

These four skills are independent of each other — they should be implemented in parallel using subagent-driven development. Each subagent MUST invoke `superpowers:writing-skills` before creating its SKILL.md.

All skills share these conventions:
- YAML frontmatter with `name` and `description` fields (see spec lines 103-116)
- Body max 300 lines
- Reference files loaded lazily (skill body says "Read `references/X` when user asks about Y")
- 3-5 example prompts in a `## Examples` section
- Follow the existing `r-package-skill-generator/SKILL.md` as a structural template

### Task 3: Create r-data-analysis skill

**Files:**
- Create: `.claude/skills/r-data-analysis/SKILL.md`
- Create: `.claude/skills/r-data-analysis/references/dplyr-patterns.md`
- Create: `.claude/skills/r-data-analysis/references/join-guide.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

- [ ] **Step 1: Invoke writing-skills**

```
Skill: superpowers:writing-skills
```

Follow the writing-skills workflow to create the skill. Provide this context to writing-skills:

**Skill purpose:** Expert assistant for everyday R data wrangling and pipeline construction. Covers dplyr, tidyr, readr, lubridate, stringr, forcats.

**Frontmatter:**
```yaml
---
name: r-data-analysis
description: >
  Use when working with data wrangling, cleaning, transformation, or pipelines
  in R using dplyr, tidyr, readr, lubridate, stringr, or forcats.
---
```

**Body must cover:**
- Data import with readr (`read_csv()`, `read_tsv()`, spec/col_types)
- dplyr verbs: `filter()`, `select()`, `mutate()`, `summarise()`, `group_by()`, `arrange()`, `slice()`, `across()`, `pick()`, `reframe()`
- tidyr: `pivot_longer()`, `pivot_wider()`, `separate_wider_delim()`, `unnest()`, `nest()`, `fill()`, `replace_na()`
- Joins: `left_join()`, `inner_join()`, `anti_join()`, `semi_join()` with `join_by()`
- String manipulation with stringr
- Factor handling with forcats (`fct_reorder()`, `fct_lump()`, `fct_relevel()`)
- Date/time with lubridate
- Missing data strategies: `is.na()`, `drop_na()`, `replace_na()`, `coalesce()`
- When to suggest data.table (>1M rows, memory-constrained)
- Dispatch to `r-statistician` agent when analysis crosses into modeling (Phase 3 deliverable — include the dispatch instruction but add: "If the r-statistician agent is not yet available, provide basic modeling guidance inline")
- Lazy reference loading: "Read `references/dplyr-patterns.md` for advanced across()/pick() recipes" and "Read `references/join-guide.md` for complex join strategies"
- 3-5 example prompts

**All code examples MUST use `|>` (never `%>%`), follow tidyverse style, use `<-` for assignment.**

- [ ] **Step 2: Create references/dplyr-patterns.md**

Advanced dplyr patterns reference (loaded lazily). Cover:
- `across()` with multiple functions, renaming, .names glue syntax
- `pick()` for selecting columns inside verbs
- `reframe()` for multi-row summaries
- Window functions: `lag()`, `lead()`, `cumsum()`, `row_number()`, `dense_rank()`
- `rowwise()` + `c_across()` patterns
- `.by` argument as alternative to `group_by() |> ... |> ungroup()`
- Common recipes: running totals, group-level deduplication, rolling calculations

- [ ] **Step 3: Create references/join-guide.md**

Join reference (loaded lazily). Cover:
- `join_by()` syntax including inequality joins (`join_by(x >= y)`)
- `left_join()` vs `inner_join()` vs `full_join()` decision tree
- Filtering joins: `semi_join()`, `anti_join()` for existence checks
- `cross_join()` for cartesian products
- Multiple join keys, handling column name conflicts (`.suffix`)
- Common patterns: lookup tables, merging time-stamped data, many-to-many handling

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/r-data-analysis/
git commit -m "feat: add r-data-analysis skill with dplyr/tidyr references"
```

### Task 4: Create r-visualization skill

**Files:**
- Create: `.claude/skills/r-visualization/SKILL.md`
- Create: `.claude/skills/r-visualization/references/ggplot2-layers.md`
- Create: `.claude/skills/r-visualization/references/theme-guide.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

- [ ] **Step 1: Invoke writing-skills**

```
Skill: superpowers:writing-skills
```

Follow the writing-skills workflow to create the skill.

**Skill purpose:** Expert ggplot2 and R visualization assistant. Covers grammar of graphics, publication-quality figures, interactive plots, and domain-specific visualizations.

**Frontmatter:**
```yaml
---
name: r-visualization
description: >
  Use when creating plots, charts, or visualizations in R using ggplot2, plotly,
  or htmlwidgets. Includes publication-quality figures and domain-specific plots.
---
```

**Body must cover:**
- ggplot2 grammar: `ggplot()` + `aes()` → geom layers → scales → coords → facets → theme
- Common geoms: `geom_point()`, `geom_line()`, `geom_col()`, `geom_boxplot()`, `geom_violin()`, `geom_histogram()`, `geom_density()`, `geom_smooth()`, `geom_tile()`, `geom_sf()`
- Scales: `scale_*_continuous()`, `scale_*_discrete()`, `scale_color_viridis_c/d()`, `scale_fill_brewer()`
- Colorblind-safe palettes: viridis family, `scale_*_manual()` with safe palettes
- Faceting: `facet_wrap()`, `facet_grid()`, free scales, labeller functions
- Labels and annotations: `labs()`, `annotate()`, `geom_text()`/`geom_label()`, `ggrepel`
- Publication themes: `theme_minimal()`, `theme_classic()`, custom `theme()` adjustments
- Multi-panel figures with `patchwork` (`+`, `/`, `|`, `plot_layout()`)
- Saving: `ggsave()` with appropriate dimensions, DPI, device settings
- Interactive: `plotly::ggplotly()` for quick interactivity, when to use native plotly
- Domain-specific: Kaplan-Meier curves (`survminer::ggsurvplot()`), forest plots, volcano plots, Manhattan plots
- Lazy reference loading: "Read `references/ggplot2-layers.md` for detailed geom/stat/position reference" and "Read `references/theme-guide.md` for complete theme element hierarchy"
- 3-5 example prompts

- [ ] **Step 2: Create references/ggplot2-layers.md**

Detailed layer reference (loaded lazily). Cover:
- Every common geom with key aesthetics and useful params
- Statistical transformations: `stat_summary()`, `stat_function()`, `stat_ecdf()`
- Position adjustments: `position_dodge()`, `position_jitter()`, `position_stack()`
- Coordinate systems: `coord_flip()`, `coord_polar()`, `coord_sf()`, `coord_fixed()`
- Scale details: continuous vs discrete, log/sqrt transforms, date/time scales, manual scales
- Guide/legend customization: `guides()`, `guide_legend()`, `guide_colorbar()`

- [ ] **Step 3: Create references/theme-guide.md**

Theme element hierarchy reference (loaded lazily). Cover:
- Complete theme element tree: `text`, `line`, `rect` → specific elements
- `element_text()`, `element_line()`, `element_rect()`, `element_blank()` params
- Plot margins: `plot.margin`, spacing between panels
- Legend positioning: `legend.position`, `legend.direction`, custom coordinates
- Strip styling for faceted plots
- Creating reusable custom themes as functions
- Journal-specific theme recipes (Nature, Science, NEJM style)

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/r-visualization/
git commit -m "feat: add r-visualization skill with ggplot2 references"
```

### Task 5: Create r-tdd skill

**Files:**
- Create: `.claude/skills/r-tdd/SKILL.md`
- Create: `.claude/skills/r-tdd/scripts/run_coverage.R`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

- [ ] **Step 1: Invoke writing-skills**

```
Skill: superpowers:writing-skills
```

Follow the writing-skills workflow to create the skill.

**Skill purpose:** Enforce test-driven development workflow for R using testthat 3rd edition. Write tests first, implement minimally, refactor.

**Frontmatter:**
```yaml
---
name: r-tdd
description: >
  Use when writing or running tests for R code, setting up testthat, or
  following TDD workflow in R packages or scripts.
---
```

**Body must cover:**
- TDD cycle for R: RED (write failing test) → GREEN (minimal implementation) → REFACTOR
- testthat 3e setup: `usethis::use_testthat(3)`, edition 3 features
- Test file conventions: `tests/testthat/test-*.R`, naming matches `R/*.R`
- Test structure: `test_that("description", { ... })` with descriptive names
- BDD style: `describe("component", { it("does something", { ... }) })`
- Core expectations: `expect_equal()`, `expect_identical()`, `expect_true()`, `expect_error()`, `expect_warning()`, `expect_message()`, `expect_type()`, `expect_s3_class()`, `expect_length()`
- Snapshot testing: `expect_snapshot()`, `expect_snapshot_output()`, `expect_snapshot_value()` for complex outputs
- Test fixtures: `tests/testthat/setup.R` for shared setup, `withr::local_*()` for temporary state
- Mocking: `testthat::local_mocked_bindings()` for isolating external dependencies
- Test helpers: `tests/testthat/helper.R` for shared utility functions
- Running tests: `devtools::test()`, `devtools::test_active_file()`, `testthat::test_file()`
- Coverage: `covr::package_coverage()`, 80% minimum target
- Coverage script: "Run `scripts/run_coverage.R` for function-level coverage report"
- Common patterns: testing data frames (snapshot or `expect_equal` with tolerance), testing plots (vdiffr), testing error messages
- 3-5 example prompts showing full TDD cycle

- [ ] **Step 2: Create scripts/run_coverage.R**

A helper script that runs coverage and prints a summary:

```r
#!/usr/bin/env Rscript
# Run package test coverage and print function-level summary
# Usage: Rscript scripts/run_coverage.R [package_path]

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) > 0) args[1] else "."

if (!requireNamespace("covr", quietly = TRUE)) {
  cli::cli_abort("Package {.pkg covr} is required. Install with {.code install.packages('covr')}")
}

cov <- covr::package_coverage(path = pkg_path)

# Overall summary
cat("\n=== Coverage Summary ===\n")
pct <- covr::percent_coverage(cov)
cat(sprintf("Overall coverage: %.1f%%\n", pct))

if (pct < 80) {
  cat("WARNING: Coverage below 80% threshold!\n")
}

# Function-level breakdown
cat("\n=== Function-Level Coverage ===\n")
func_cov <- covr::tally_coverage(cov, by = "function")
func_cov <- func_cov[order(func_cov$value), ]
print(func_cov[, c("filename", "functions", "value")], row.names = FALSE)

cat(sprintf("\nTotal: %.1f%% | Threshold: 80%%\n", pct))
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/r-tdd/
git commit -m "feat: add r-tdd skill with coverage script"
```

### Task 6: Create r-debugging skill

**Files:**
- Create: `.claude/skills/r-debugging/SKILL.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

- [ ] **Step 1: Invoke writing-skills**

```
Skill: superpowers:writing-skills
```

Follow the writing-skills workflow to create the skill.

**Skill purpose:** Systematic debugging workflow for R code. Covers interactive debugging tools, common R pitfalls, memory/performance diagnosis.

**Frontmatter:**
```yaml
---
name: r-debugging
description: >
  Use when diagnosing bugs, errors, or unexpected behavior in R code. Covers
  browser(), traceback(), profiling, and common R pitfalls.
---
```

**Body must cover:**
- Debugging workflow: REPRODUCE → ISOLATE → DIAGNOSE → FIX → TEST
- Step 1 — Reproduce: create minimal reprex, use `reprex::reprex()` for sharing
- Step 2 — Isolate: binary search through pipeline, `browser()` insertion
- Step 3 — Diagnose using tools:
  - `traceback()` / `rlang::last_trace()` — read the call stack after an error
  - `browser()` — insert breakpoint, inspect environment, step through code
  - `debug(fun)` / `undebug(fun)` — debug a specific function
  - `debugonce(fun)` — debug only the next call
  - `options(error = recover)` — enter browser on any error
  - `trace(fun, browser, at = N)` — insert browser at specific line
- Step 4 — Fix: apply fix, verify against original reprex
- Step 5 — Test: write a test that would have caught this bug (regression test)
- Common R pitfalls (with symptoms and fixes):
  - **Factor surprises:** `stringsAsFactors` legacy, factor levels dropping, numeric coercion of factors
  - **NSE scoping:** Variable not found inside dplyr verbs, `.data$` vs `{{ }}` confusion
  - **Recycling rules:** Silent vector recycling leading to wrong results
  - **Copy-on-modify:** Unexpected memory spikes when modifying objects
  - **NULL propagation:** `$` on missing list elements returns NULL silently
  - **Floating point:** `0.1 + 0.2 != 0.3`, use `dplyr::near()` or `all.equal()`
  - **Encoding:** UTF-8 issues on Windows, `Encoding()` diagnostics
- Performance debugging:
  - `system.time()` for quick timing
  - `bench::mark()` for comparative benchmarks
  - `profvis::profvis()` for flame graph profiling
  - `lobstr::obj_size()` for memory inspection
- Dispatch: when bug appears to be a code quality issue (anti-pattern, style, NSE misuse), dispatch to `r-code-reviewer` agent for review
- Context-aware: ask whether debugging interactive script or package code — different strategies apply (scripts use `browser()` freely; packages use `testthat` + `debug()`)
- 3-5 example prompts

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/r-debugging/
git commit -m "feat: add r-debugging skill"
```

---

## Chunk 3: Shared Agent

### Task 7: Create r-code-reviewer agent

**Files:**
- Create: `.claude/agents/r-code-reviewer.md`

This is an agent file, NOT a skill — it does not use YAML frontmatter. It follows the agent format established in the existing `r-package-skill-generator/agents/` files.

- [ ] **Step 1: Create agents directory and r-code-reviewer.md**

Write `.claude/agents/r-code-reviewer.md`:

```markdown
# R Code Reviewer Agent

Opinionated R code reviewer. Checks style, correctness, performance, and documentation against supeRpowers conventions.

## Inputs

- **Required:** File paths to review (one or more `.R` files), OR inline R code block
- **Optional:** Review scope — one of `full` (default), `style-only`, `performance`

## Output

Markdown report with categorized findings, sorted by severity.

### Report Format

```
## R Code Review: {file(s) reviewed}

### CRITICAL (must fix)
- **{file}:{line}** — {issue description}
  Fix: {specific code change}

### HIGH (should fix)
- **{file}:{line}** — {issue description}
  Fix: {specific code change}

### MEDIUM (consider)
- **{file}:{line}** — {issue description}
  Suggestion: {improvement}

### Summary
- {N} critical, {N} high, {N} medium issues found
- Overall assessment: {PASS | NEEDS WORK | FAILING}
```

## Procedure

### 1. Read the code

Read all target files. If inline code was provided, work with that directly.

### 2. Check style compliance

- **Pipe:** `|>` only, flag any `%>%` usage
- **Assignment:** `<-` only, flag `=` used for assignment
- **Naming:** snake_case for functions and variables, flag camelCase or dot.case
- **Formatting:** Consistent with `styler::tidyverse_style()` — spacing, indentation, line length (120 hard limit)
- **Strings:** Double quotes preferred

### 3. Check correctness

- **NSE hygiene:**
  - Functions accepting column names must use `{{ }}` (embrace), not bare names
  - `.data$col` for column references from strings, `.env$var` for environment values
  - No unquoted column names leaking outside of dplyr/tidyr context
- **Error handling:**
  - Package code: uses `cli::cli_abort()` / `cli::cli_warn()`, not `stop()` / `warning()`
  - Condition classes present for programmatic catching
- **roxygen2 completeness (for package code):**
  - All exported functions have roxygen2 documentation
  - `@param` for every parameter
  - `@returns` present
  - `@examples` present for exported functions
  - Tidy eval documented where applicable
- **Common bugs:**
  - `ifelse()` with dates (strips class) — suggest `dplyr::if_else()`
  - `sapply()` with inconsistent return types — suggest `vapply()` or `purrr::map_*()`
  - `T`/`F` instead of `TRUE`/`FALSE`
  - `1:length(x)` when `x` might be empty — suggest `seq_along(x)`

### 4. Check performance

- **Growing vectors in loops:** `c(result, new_value)` pattern — suggest pre-allocation or `purrr::map()`
- **`rbind()` in loops:** — suggest `dplyr::bind_rows()` on a list
- **Unnecessary copies:** Repeated subsetting creating copies — suggest pipeline approach
- **`apply()` family misuse:** `apply()` on data frames (coerces to matrix) — suggest `dplyr::across()` or `purrr::map()`
- **Large object in global:** Suggest scoping inside functions

### 5. Return findings

Sort by severity (CRITICAL first). Include specific file:line references and concrete fix suggestions.

## Severity Guide

| Severity | Criteria |
|----------|----------|
| CRITICAL | Will cause bugs, data loss, or incorrect results |
| HIGH | Violates core conventions (pipe, naming, docs), maintainability risk |
| MEDIUM | Style improvement, minor performance, optional enhancement |

## Examples

**Input:** "Review `R/clean-data.R` for style and correctness"
**Output:** Report with findings categorized by severity

**Input:** "Review this code: `df %>% mutate(x = ifelse(date > today(), TRUE, FALSE))`"
**Output:** CRITICAL: Use `|>` not `%>%`. HIGH: Use `dplyr::if_else()` not `ifelse()` (preserves type). MEDIUM: Simplify to `mutate(x = date > today())`.
```

- [ ] **Step 2: Verify line count is under 200**

```bash
wc -l .claude/agents/r-code-reviewer.md
```

Expected: under 200 lines.

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/r-code-reviewer.md
git commit -m "feat: add r-code-reviewer shared agent"
```

---

## Chunk 4: Integration Verification

### Task 8: Verify Phase 1 completeness

- [ ] **Step 1: Verify all files exist**

```bash
ls -la plugin.json
ls -la .claude/rules/r-conventions.md
ls -la .claude/skills/r-data-analysis/SKILL.md
ls -la .claude/skills/r-data-analysis/references/dplyr-patterns.md
ls -la .claude/skills/r-data-analysis/references/join-guide.md
ls -la .claude/skills/r-visualization/SKILL.md
ls -la .claude/skills/r-visualization/references/ggplot2-layers.md
ls -la .claude/skills/r-visualization/references/theme-guide.md
ls -la .claude/skills/r-tdd/SKILL.md
ls -la .claude/skills/r-tdd/scripts/run_coverage.R
ls -la .claude/skills/r-debugging/SKILL.md
ls -la .claude/agents/r-code-reviewer.md
```

All 12 files should exist.

- [ ] **Step 2: Verify line counts**

```bash
echo "=== Line counts ==="
wc -l .claude/rules/r-conventions.md
wc -l .claude/skills/r-data-analysis/SKILL.md
wc -l .claude/skills/r-visualization/SKILL.md
wc -l .claude/skills/r-tdd/SKILL.md
wc -l .claude/skills/r-debugging/SKILL.md
wc -l .claude/agents/r-code-reviewer.md
```

Verify:
- `r-conventions.md` < 150 lines
- Each SKILL.md < 300 lines (body, excluding frontmatter)
- `r-code-reviewer.md` < 200 lines

- [ ] **Step 3: Verify YAML frontmatter in all skills**

```bash
head -10 .claude/skills/r-data-analysis/SKILL.md
head -10 .claude/skills/r-visualization/SKILL.md
head -10 .claude/skills/r-tdd/SKILL.md
head -10 .claude/skills/r-debugging/SKILL.md
```

Each should have:
```yaml
---
name: <skill-name>
description: >
  <trigger condition>
---
```

- [ ] **Step 4: Verify no `%>%` usage in any generated content**

```bash
grep -r '%>%' .claude/skills/ .claude/rules/ .claude/agents/ || echo "PASS: No magrittr pipes found"
```

Expected: "PASS: No magrittr pipes found" (or only in "WRONG" examples showing what NOT to do).

- [ ] **Step 5: Final commit with all Phase 1 files**

Only if any files were missed or fixed during verification:

```bash
git add -A .claude/ plugin.json
git status
git commit -m "feat: complete Phase 1 — foundation + core skills + code reviewer agent"
```

---

## Execution Strategy

**Tasks 1-2** (Foundation): Execute sequentially — Task 2 depends on understanding the conventions.

**Git commit strategy for parallel tasks:** Each subagent creates its files but does NOT commit. The orchestrator commits all skill files in a single sequential step after all subagents complete. The per-task commit steps are illustrative — the orchestrator sequences them to avoid git lock contention.

**Tasks 3-6** (Skills): Execute in PARALLEL using subagent-driven development. Each skill is fully independent. Each subagent MUST:
1. Read `.claude/rules/r-conventions.md` for context
2. Read `.claude/skills/r-package-skill-generator/SKILL.md` as a structural example
3. Invoke `superpowers:writing-skills` before creating any SKILL.md
4. Follow the task steps exactly

**Task 7** (Agent): Can execute in parallel with Tasks 3-6.

**Task 8** (Verification): Execute after all other tasks complete.

```
Task 1 (plugin.json)  ──┐
Task 2 (conventions)  ──┤
                        │
                        ▼
        ┌───────────────┼───────────────┐
        │               │               │
   Tasks 3-6        Task 7          (parallel)
   (4 skills)     (1 agent)
        │               │
        └───────────────┤
                        ▼
                    Task 8
                 (verification)
```
