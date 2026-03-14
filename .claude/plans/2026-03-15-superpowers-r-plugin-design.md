# supeRpowers — Claude Code Marketplace Plugin for R

**Date:** 2026-03-15
**Status:** Design approved, pending implementation plan

## Overview

supeRpowers is a comprehensive Claude Code marketplace plugin that supercharges R programming for intermediate-to-advanced users. It provides expert-level assistance across the full R development spectrum: data analysis, visualization, package development, Shiny apps, statistical modeling, biostatistics/clinical analysis, table creation, Quarto publishing, and performance optimization.

## Design Principles

- **Tidyverse-first:** Lead with tidyverse idioms. Mention base R or data.table when genuinely better.
- **Base pipe only:** Always `|>`, never `%>%`. Match existing code if it uses magrittr, but suggest migration.
- **Opinionated modern toolchain:** usethis, devtools, testthat 3e, roxygen2, pkgdown, styler, lintr.
- **renv for reproducibility:** Always check for renv.lock. Suggest renv::init() for new projects.
- **R >= 4.1.0:** Target minimum R version (when `|>` was introduced). Flag newer features.

## Target Audience

Intermediate to advanced R users:
- Comfortable with base R, proficient or learning tidyverse
- Package authors, Shiny developers, statisticians, data scientists
- Biostatisticians and clinical trial analysts (deep domain focus)

## Architecture

### Layered Design: Rules + Skills + Agents

```
Foundation Layer (rules/)
  └─ r-conventions.md — shared conventions inherited by all skills

Domain Layer (skills/)
  └─ 12 specialized skills organized by phase

Service Layer (agents/)
  └─ 5 shared agents dispatched from any skill
```

### Why This Architecture

- **DRY:** Conventions defined once in rules, inherited by all skills
- **Modular:** Each skill is self-contained with its own references, scripts, and checklists
- **Reusable:** Agents serve multiple skills (e.g., r-code-reviewer works after any code generation)
- **Scalable:** New skills/agents can be added without touching existing ones
- **Phased delivery:** Independent skills can be built and shipped incrementally

---

## Foundation Layer

### `.claude/rules/r-conventions.md`

A concise reference card (not a textbook) loaded into context for every R interaction.

**Contents:**

| Convention | Rule |
|-----------|------|
| Pipe | `\|>` always, never `%>%` |
| Paradigm | Tidyverse-first, base R or data.table when justified |
| Style | `styler::tidyverse_style()`, `lintr`, snake_case |
| Environment | `renv` for all projects |
| Toolchain | usethis, devtools, roxygen2, testthat 3e, pkgdown |
| R version | >= 4.1.0 |
| Documentation | roxygen2 with markdown, `@examples` mandatory for exports |
| Error handling | `cli::cli_abort()` / `cli::cli_warn()` / `cli::cli_inform()` in packages |
| Tidy eval | `{{ }}` embrace, `.data$col`, `.env$var`, document data-masking |

---

## Domain Layer — Skills

### Phase 1: Core R Development

#### `r-data-analysis/`

Everyday data wrangling and pipeline construction.

- dplyr, tidyr, readr, lubridate, stringr, forcats
- Data cleaning: missing data strategies, type coercion, joins, reshaping
- References: dplyr verb cheat sheet, common recipes (group-summarize, window functions, across patterns)
- Knows when to suggest data.table for large datasets
- Dispatches to `r-statistician` agent when analysis crosses into modeling

#### `r-visualization/`

ggplot2 mastery and beyond.

- Grammar of graphics: aesthetics, geoms, stats, scales, coords, facets, themes
- Publication-quality figures: custom themes, colorblind-safe palettes (viridis), annotation
- Interactive: plotly via `ggplotly()`, htmlwidgets, DT tables
- Domain-specific plots: Kaplan-Meier curves, forest plots, volcano plots, Manhattan plots
- References: layer logic, scale/coord cheat sheet, theme element hierarchy

#### `r-tdd/`

Test-driven development adapted for R.

- testthat 3e: `describe()`/`it()` or `test_that()` with edition 3 features
- TDD cycle: write expectation → `devtools::test()` → implement → pass → refactor
- Snapshot testing for complex outputs (plots, printed tibbles, error messages)
- Fixtures: `setup.R`/`teardown.R`, `helper.R`, test data management
- Coverage: `covr::package_coverage()` with 80% minimum
- Mocking: `testthat::local_mocked_bindings()`

#### `r-debugging/`

Systematic debugging for R.

- Workflow: reproduce → isolate → diagnose → fix → test
- Tools: `browser()`, `debug()`/`undebug()`, `traceback()`, `rlang::last_trace()`
- Common pitfalls: NSE scoping, factor surprises, recycling rules, copy-on-modify
- Memory debugging: `lobstr::obj_size()`, `bench::mark()`, `profvis`
- Context-aware: distinguishes interactive script debugging from package code debugging

### Phase 2: Package Development & Shiny

#### `r-package-dev/`

Full package lifecycle with opinionated modern stack.

- **Scaffold:** `usethis::create_package()`, `use_testthat(3)`, `use_pipe()`, `use_roxygen_md()`
- **Dev loop:** `devtools::load_all()` → `devtools::test()` → `devtools::check()` → `devtools::document()`
- **Documentation:** roxygen2 markdown, `@examples`, `@family`, tidy eval documentation tags
- **Class systems:** S3 (primary), S4 (Bioconductor), R7 (greenfield), R6 (mutable state)
- **Compiled code:** Rcpp basics, `.Call()` interface, `usethis::use_rcpp()`
- **Vignettes:** `usethis::use_vignette()`, rmarkdown/quarto
- **pkgdown:** Site generation and configuration
- **CRAN submission:** `devtools::check(cran = TRUE)`, `rhub::check_for_cran()`, NEWS.md, cran-comments.md
- **CI/CD:** GitHub Actions via `usethis::use_github_action()` — R CMD check, coverage, pkgdown deploy
- Dispatches to `r-pkg-check` agent for deep R CMD check issue resolution

#### `r-shiny/`

Full Shiny ecosystem expertise.

- **Reactivity:** reactive expressions, observers, `reactiveVal`/`reactiveValues`, isolation, invalidation
- **Modules:** `moduleServer()` with namespacing, inter-module communication
- **Frameworks:** golem (default recommendation) and rhino (enterprise patterns)
- **UI:** `bslib` theming, responsive layouts, `htmltools`, dynamic UI
- **Testing:** `shinytest2` integration tests, `testServer()` module unit tests
- **JavaScript:** custom input bindings, `Shiny.setInputValue`, htmlwidgets in Shiny
- **Performance:** `bindCache()`, async with promises/future, `shiny::devmode()`
- **Deployment:** shinyapps.io, Posit Connect, ShinyProxy, Docker containerization
- Dispatches to `r-shiny-architect` agent for structure review

### Phase 3: Statistics, Clinical & Publishing

#### `r-stats/`

General statistics with modeling expertise.

- **Linear models:** `lm()`, diagnostics, assumption checking (residuals, Q-Q, VIF)
- **GLMs:** logistic, Poisson, negative binomial, quasi families
- **Mixed models:** `lme4`, `nlme`, random effects structure, convergence troubleshooting
- **Survival:** `survival` package, Kaplan-Meier, Cox PH, time-varying covariates
- **Bayesian:** `brms`/`rstanarm`, prior selection guidance
- **Time series:** `tsibble`/`fable` ecosystem (tidyverse-aligned), ARIMA, state space
- **Multiple testing:** FDR correction, p-value adjustment strategies
- **Model comparison:** AIC/BIC, LRT, cross-validation with `rsample`/`tidymodels`
- Dispatches to `r-statistician` agent for consulting and assumption verification

#### `r-clinical/`

Deep biostatistics and clinical trial analysis.

- **Trial design:** power analysis (`pwr`, `gsDesign`), sample size, adaptive designs
- **CDISC:** ADaM and SDTM dataset structure awareness
- **Regulatory tables:** TLFs (Tables, Listings, Figures) generation patterns
- **Survival endpoints:** OS, PFS, DFS — censoring, competing risks (`cmprsk`)
- **Biomarkers:** ROC curves (`pROC`), cutpoint optimization, subgroup analysis
- **Meta-analysis:** `meta`/`metafor`, forest plots, heterogeneity assessment
- **Genomics bridge:** `DESeq2`, `limma`, enrichment analysis (Bioconductor)
- **MCP integration:** Pulls trial data from Clinical Trials MCP, preprints from bioRxiv MCP
- **References:** ICH guideline awareness, CONSORT flow diagram patterns

#### `r-tables/`

Publication-quality tables.

- **gt:** table structure, formatting, styling, spanners, footnotes, source notes
- **gtsummary:** `tbl_summary()`, `tbl_regression()`, `tbl_merge()`, `tbl_stack()`
- **gtExtras:** sparklines, inline plots, icons, themes (`gt_theme_538`, `gt_theme_nytimes`)
- **Patterns:** demographic tables (Table 1), regression results, comparison tables
- **Output formats:** HTML, PDF (LaTeX), Word (`flextable` fallback when needed)
- **Journal themes:** gtsummary themes for JAMA, Lancet, etc.
- **Interactive:** `reactable` for Shiny/Quarto contexts

#### `r-quarto/`

Modern R publishing and communication.

- **Documents:** reports, manuscripts, technical memos with code execution
- **Presentations:** revealjs slides with R output, speaker notes, incremental reveals
- **Websites:** project sites, blogs, documentation sites, `quarto publish`
- **Books:** multi-chapter projects, cross-references, bibliographies
- **Configuration:** YAML format options, execution control, parameters, conditional content
- **Code chunks:** `#|` syntax, caching strategies, figure sizing
- **Cross-references:** figures, tables, equations, sections — proper labeling
- **Journal templates:** `quarto-journals` extensions for academic submission
- **Multi-format:** single source → HTML + PDF + Word with format-specific content
- **Extensions:** finding, installing, and using community Quarto extensions

### Phase 4: Performance & Meta

#### `r-performance/`

When speed matters.

- **Profiling:** `profvis`, `bench::mark()`, bottleneck identification
- **data.table:** translation from dplyr, when/why to switch, reference semantics
- **Vectorization:** replacing loops, `vapply`/`map` patterns
- **Memory:** copy-on-modify, `data.table::setDT()`, chunked reading
- **Rcpp:** hot-path optimization, C++ for inner loops
- **Parallel:** `furrr` (tidyverse-aligned parallel), `future` backends

#### `r-package-skill-generator/` (existing)

Meta-tool that generates Claude skills from any R package GitHub repo. Already implemented with multi-agent exploration (API, Architecture, Idiom, Edge-Case agents) and synthesis pipeline.

---

## Service Layer — Shared Agents

### `r-code-reviewer.md`

Opinionated R code review dispatched after code generation from any skill.

- Style: styler compliance, lintr rules, naming conventions, base pipe enforcement
- Correctness: NSE hygiene (`{{ }}`, `.data$`, `.env$`), roxygen2 completeness
- Performance: flags known slow patterns (growing vectors, rbind in loops)
- Severity: CRITICAL (bugs) → HIGH (style violations) → MEDIUM (suggestions)

### `r-statistician.md`

Statistical consulting agent.

- Model selection guidance based on data structure and research question
- Assumption checking prompts (normality, homoscedasticity, independence, linearity)
- Interpretation: coefficients, CIs, effect sizes in plain language
- Warnings: multiple comparisons, p-hacking, Simpson's paradox, correlation ≠ causation
- Power analysis and sample size guidance
- Biostat depth: survival diagnostics (Schoenfeld residuals, PH assumption), competing risks

### `r-pkg-check.md`

R CMD check issue resolver.

- Parses check output, categorizes ERROR/WARNING/NOTE
- Knows fixes for common NOTEs ("no visible binding" → `.data$`, missing imports, undocumented args)
- CRAN-specific: acceptable NOTEs, reviewer expectations
- Cross-platform: Windows path/encoding issues, macOS/Linux differences
- Suggests correct `usethis::use_*()` calls for structural fixes

### `r-shiny-architect.md`

Shiny app structure reviewer.

- Module decomposition: size, coupling, namespacing
- Reactivity audit: reactive spaghetti, unnecessary invalidation, missing `isolate()`
- Performance: unbounded reactive chains, missing `bindCache()`, large session data
- Security: input validation, SQL injection via inputs, file upload handling
- Architecture: golem structure adherence, business logic separation

### `r-dependency-manager.md`

renv and dependency management expert.

- Workflow: `renv::init()` → `renv::snapshot()` → `renv::restore()`
- Dependency audit: heavy/unnecessary deps, lighter alternatives
- Version conflicts: diagnosis and resolution
- Mixed repos: Bioconductor + CRAN coexistence in renv
- Lock file review: concerning pins, missing packages

---

## Integration Points

### MCP Server Integration

The `r-clinical` skill leverages connected MCP servers:

- **Clinical Trials MCP:** Pull trial design details (endpoints, sample sizes, eligibility) to inform analysis. E.g., "look up NCT04012345 and help me replicate the primary endpoint analysis"
- **bioRxiv MCP:** Search preprints for methodology or disease area context. E.g., "find recent preprints on adaptive enrichment designs in oncology"
- The `r-statistician` agent can reference MCP data when advising on methodology

### Skill Chaining — Natural Workflows

Skills don't call each other directly, but natural workflows cross skill boundaries:

- **Analysis to publication:** `r-data-analysis` → `r-visualization` → `r-tables` → `r-quarto`
- **Package development loop:** `r-package-dev` → `r-tdd` → `r-code-reviewer` agent
- **Clinical pipeline:** `r-stats` → `r-clinical` → `r-tables` → `r-quarto`
- **Shiny development loop:** `r-shiny` → `r-shiny-architect` agent → `r-tdd`

### Scripts & Utilities

Lightweight helper scripts where beneficial:

- `r-package-dev/scripts/` — R CMD check output parser for `r-pkg-check` agent
- `r-tdd/scripts/` — Coverage report parser for function-level coverage
- `r-shiny/scripts/` — Shiny app scaffolder using golem conventions

### Per-Skill References

Each skill bundles reference material loaded into context when needed:

- `r-data-analysis/references/` — dplyr verb patterns, across() recipes, join decision tree
- `r-visualization/references/` — ggplot2 layer logic, theme element map, color palette guide
- `r-stats/references/` — model selection flowchart, assumption checklist, effect size guide
- `r-clinical/references/` — CDISC ADaM naming, TLF templates, ICH endpoint definitions
- `r-tables/references/` — gtsummary theme catalog, gt formatting patterns
- `r-quarto/references/` — YAML config cheat sheet, chunk options, cross-reference syntax

---

## Directory Structure

```
.claude/
  rules/
    r-conventions.md
  skills/
    r-data-analysis/
      SKILL.md
      references/
    r-visualization/
      SKILL.md
      references/
    r-tdd/
      SKILL.md
      scripts/
    r-debugging/
      SKILL.md
    r-package-dev/
      SKILL.md
      references/
      scripts/
    r-shiny/
      SKILL.md
      references/
      scripts/
    r-stats/
      SKILL.md
      references/
    r-clinical/
      SKILL.md
      references/
    r-tables/
      SKILL.md
      references/
    r-quarto/
      SKILL.md
      references/
    r-performance/
      SKILL.md
      references/
    r-package-skill-generator/   # existing
      SKILL.md
      agents/
      references/
      scripts/
  agents/
    r-code-reviewer.md
    r-statistician.md
    r-pkg-check.md
    r-shiny-architect.md
    r-dependency-manager.md
```

---

## Implementation Phases

### Phase 1: Foundation + Core (First delivery)
- `rules/r-conventions.md`
- `r-data-analysis/`
- `r-visualization/`
- `r-tdd/`
- `r-debugging/`
- `agents/r-code-reviewer.md`

### Phase 2: Package Development & Shiny
- `r-package-dev/`
- `r-shiny/`
- `agents/r-pkg-check.md`
- `agents/r-shiny-architect.md`

### Phase 3: Statistics, Clinical & Publishing
- `r-stats/`
- `r-clinical/`
- `r-tables/`
- `r-quarto/`
- `agents/r-statistician.md`

### Phase 4: Performance & Advanced
- `r-performance/`
- `agents/r-dependency-manager.md`

Each phase is independently deliverable and testable. Later phases build on the foundation but don't require changes to earlier phases.

---

## Success Criteria

- Every skill has a clear trigger condition (when to invoke)
- Every agent has defined input/output contracts
- R conventions rule is comprehensive but concise (loadable in context without bloat)
- Skills produce idiomatic, modern R code that passes styler/lintr
- Statistical advice is sound and includes appropriate caveats
- MCP integration provides genuine value for clinical workflows
- Plugin is installable from Claude Code marketplace as a single unit
