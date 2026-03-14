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

### Agent Dispatch Convention

Skills dispatch to shared agents via Claude Code's Agent tool with `subagent_type` referencing the agent by name.

- **Path convention:** Shared agents live at `.claude/agents/<name>.md`. Skill-local agents live at `.claude/skills/<skill>/agents/<name>.md`.
- **Dispatch is skill-initiated:** When a skill determines that a task crosses into an agent's domain, it dispatches automatically (no user confirmation needed). Example: `r-data-analysis` detects modeling questions and dispatches to `r-statistician`.
- **Agent output returns to skill context:** Agents produce structured markdown reports. The dispatching skill incorporates the agent's findings into its response to the user.
- **User can invoke agents directly:** Agents are also available for direct invocation (e.g., "review this R code" triggers `r-code-reviewer` without going through a skill).

### Context Budget

To avoid context window bloat across 12 skills:

- **`r-conventions.md`:** Maximum 150 lines. Concise reference card, not a tutorial.
- **Each `SKILL.md`:** Maximum 300 lines for the skill body (excluding frontmatter).
- **Reference files:** Loaded lazily — only when the user's question requires them. Skills include explicit "Read `references/<file>` when the user asks about X" instructions rather than loading all references upfront.
- **Agent prompts:** Maximum 200 lines each. Focused on procedure, not background knowledge.

### Error Handling Convention

- **Script failures:** Log the error, report to user, suggest manual alternative. Max 2 retries.
- **Agent contradictions:** When agent output conflicts with skill knowledge, flag the conflict to the user rather than silently choosing one.
- **MCP unavailability:** All MCP-dependent features degrade gracefully. Skills must function fully without MCP — MCP enhances but is never required.
- **General retry limit:** Max 2 attempts for any automated operation before asking the user for guidance.

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

### Skill Frontmatter Contracts

Every SKILL.md uses YAML frontmatter with `name` and `description`. The `description` field defines when the skill activates.

| Skill | `name` | `description` (trigger condition) |
|-------|--------|-----------------------------------|
| r-data-analysis | r-data-analysis | Use when working with data wrangling, cleaning, transformation, or pipelines in R using dplyr, tidyr, readr, lubridate, stringr, or forcats. |
| r-visualization | r-visualization | Use when creating plots, charts, or visualizations in R using ggplot2, plotly, or htmlwidgets. Includes publication-quality figures and domain-specific plots. |
| r-tdd | r-tdd | Use when writing or running tests for R code, setting up testthat, or following TDD workflow in R packages or scripts. |
| r-debugging | r-debugging | Use when diagnosing bugs, errors, or unexpected behavior in R code. Covers browser(), traceback(), profiling, and common R pitfalls. |
| r-package-dev | r-package-dev | Use when creating, developing, documenting, or submitting R packages. Covers usethis, devtools, roxygen2, pkgdown, CRAN submission, and CI/CD. |
| r-shiny | r-shiny | Use when building, structuring, testing, or deploying Shiny applications. Covers reactivity, modules, golem/rhino, bslib, shinytest2, and deployment. |
| r-stats | r-stats | Use when fitting statistical models, checking assumptions, or performing inference in R. Covers lm, glm, mixed models, survival, Bayesian, and time series. General methodology regardless of domain. |
| r-clinical | r-clinical | Use when working with clinical trial data, CDISC datasets (ADaM/SDTM), regulatory tables (TLFs), trial design, biomarker analysis, or domain-specific biostatistics workflows. |
| r-tables | r-tables | Use when creating formatted tables in R using gt, gtsummary, or gtExtras. Covers demographic tables, regression tables, and publication-quality output. |
| r-quarto | r-quarto | Use when authoring Quarto documents, presentations, websites, or books with R. Covers YAML config, code chunks, cross-references, journal templates, and multi-format output. |
| r-performance | r-performance | Use when optimizing R code for speed or memory. Covers profiling, data.table, vectorization, Rcpp, and parallel processing. |
| r-package-skill-generator | r-package-skill-generator | Use when generating a Claude Code skill from an R package GitHub repository. Existing meta-tool. |

**Boundary: `r-stats` vs `r-clinical`:** `r-stats` covers general statistical methodology (model fitting, diagnostics, inference) regardless of application domain. `r-clinical` covers domain-specific workflows: CDISC data structures, regulatory TLFs, trial design, ICH guidelines. Survival analysis methodology lives in `r-stats`; applying survival analysis to a clinical trial endpoint with ADaM data lives in `r-clinical`.

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
- Dispatches to `r-code-reviewer` agent when the bug appears to stem from a code quality issue (style, anti-pattern, NSE misuse)

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

**Integration note:** Generated skills should conform to supeRpowers conventions (tidyverse-first, base pipe, consistent frontmatter format). The skill generator's synthesis step should reference `r-conventions.md` to ensure generated skills align with the plugin's style. The existing `skill-creator` external dependency is retained for the drafting step.

---

## Service Layer — Shared Agents

### `r-code-reviewer.md`

Opinionated R code review dispatched after code generation from any skill.

- **Inputs:** File paths to review, or inline code block. Optionally: review scope (style-only, full, performance).
- **Output:** Markdown report with categorized findings. Format: severity (CRITICAL/HIGH/MEDIUM), location (file:line), issue description, suggested fix.
- **Invocation:** Auto-dispatched by skills after code generation. Also directly invocable by user ("review this R code").
- **Procedure:**
  1. Read target files
  2. Check styler compliance, lintr rules, naming conventions, base pipe enforcement
  3. Check NSE hygiene (`{{ }}`, `.data$`, `.env$`), roxygen2 completeness
  4. Flag known slow patterns (growing vectors, rbind in loops)
  5. Return findings sorted by severity

### `r-statistician.md`

Statistical consulting agent.

- **Inputs:** Research question or modeling task description. Optionally: dataset summary (str/glimpse output), current model code, model output.
- **Output:** Markdown advisory report. Format: recommended approach with rationale, assumptions to verify (with R code to check each), interpretation guidance, warnings/caveats.
- **Invocation:** Dispatched by `r-stats`, `r-clinical`, or `r-data-analysis` when analysis crosses into modeling. Also directly invocable.
- **Procedure:**
  1. Assess data structure and research question
  2. Recommend model family with rationale
  3. List assumptions with R code to verify each one
  4. If model output provided: interpret coefficients, CIs, effect sizes in plain language
  5. Flag risks: multiple comparisons, p-hacking, Simpson's paradox, correlation ≠ causation
  6. Biostat depth: survival diagnostics (Schoenfeld residuals, PH assumption), competing risks

### `r-pkg-check.md`

R CMD check issue resolver.

- **Inputs:** R CMD check output (text), or package root path to run check.
- **Output:** Markdown report. Format: categorized issues (ERROR/WARNING/NOTE), each with: issue text, root cause, fix (specific code/command), and whether CRAN reviewers would flag it.
- **Invocation:** Dispatched by `r-package-dev` after `devtools::check()`. Also directly invocable.
- **Procedure:**
  1. Parse check output into ERROR/WARNING/NOTE categories
  2. For each issue: identify root cause, provide specific fix
  3. Common NOTEs: "no visible binding" → `.data$`, missing imports → `usethis::use_import_from()`, undocumented args → roxygen2 update
  4. Flag CRAN-specific concerns: acceptable vs problematic NOTEs
  5. Note cross-platform issues (Windows paths, encoding)
  6. Suggest correct `usethis::use_*()` calls for structural fixes

### `r-shiny-architect.md`

Shiny app structure reviewer.

- **Inputs:** Shiny app root directory path. Optionally: specific concern (performance, modularity, security).
- **Output:** Markdown architecture review. Format: findings by category (modules, reactivity, performance, security), each with severity, location, and recommendation.
- **Invocation:** Dispatched by `r-shiny` for structure review. Also directly invocable.
- **Procedure:**
  1. Scan app structure (server.R/ui.R or app.R, modules/, R/, tests/)
  2. Evaluate module decomposition: size, coupling, namespacing
  3. Audit reactivity: identify reactive spaghetti, unnecessary invalidation, missing `isolate()`
  4. Check performance: unbounded reactive chains, missing `bindCache()`, large session data
  5. Review security: input validation, SQL injection via inputs, file upload handling
  6. Assess architecture: golem/rhino structure adherence, business logic separation

### `r-dependency-manager.md`

renv and dependency management expert.

- **Inputs:** Project root path. Optionally: specific concern (conflict resolution, audit, setup).
- **Output:** Markdown report. Format: current state assessment, issues found with fixes, recommended actions.
- **Invocation:** Dispatched by `r-package-dev` or `r-data-analysis` for dependency questions. Also directly invocable.
- **Procedure:**
  1. Check for renv.lock presence and renv status
  2. Audit dependencies: identify heavy/unnecessary deps, suggest lighter alternatives
  3. Diagnose version conflicts with resolution steps
  4. Handle mixed repos: Bioconductor + CRAN coexistence in renv configuration
  5. Review lock file for concerning version pins or missing packages
  6. Recommend `renv::init()`, `renv::snapshot()`, or `renv::restore()` as appropriate

---

## Integration Points

### MCP Server Integration

The `r-clinical` skill leverages connected MCP servers. All MCP features are optional — the skill functions fully without them.

**Clinical Trials MCP — workflow mapping:**

| Clinical Workflow | MCP Tool | Usage |
|------------------|----------|-------|
| Look up a specific trial | `get_trial_details` | Fetch protocol, endpoints, locations by NCT ID |
| Find trials for a condition | `search_trials` | Discover relevant trials by condition/intervention |
| Analyze competitor pipelines | `search_by_sponsor` | Company pipeline analysis |
| Compare endpoint designs | `analyze_endpoints` | Systematic endpoint comparison across trials |
| Find trial investigators | `search_investigators` | PI and site identification |
| Match patient eligibility | `search_by_eligibility` | Demographic/clinical criteria matching |

**bioRxiv MCP — workflow mapping:**

| Clinical Workflow | MCP Tool | Usage |
|------------------|----------|-------|
| Literature search | `search_preprints` | Find preprints by keyword, author, date |
| Preprint deep dive | `get_preprint` | Full details for a specific DOI |
| Check publication status | `search_published_preprints` | Find if preprints have been peer-reviewed |
| Funding analysis | `search_by_funder` | Research funding patterns in a field |

The `r-statistician` agent can reference MCP data when advising on methodology.

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

## Plugin Packaging

### Manifest

The plugin ships as a Git repository with a `plugin.json` manifest at root:

```json
{
  "name": "supeRpowers",
  "version": "1.0.0",
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

### Installation

Users install via Claude Code marketplace. The plugin installs its `.claude/` subtree (rules, skills, agents) into the user's project. All components install as a unit — no partial installation.

### Versioning

Semantic versioning (major.minor.patch):
- **Major:** Breaking changes to skill triggers, agent contracts, or conventions
- **Minor:** New skills/agents, new reference material, expanded capabilities
- **Patch:** Bug fixes, improved prompts, reference updates

### Dependencies

- No external runtime dependencies beyond R itself (>= 4.1.0)
- Python 3 required only for `r-package-skill-generator` scripts
- MCP servers (Clinical Trials, bioRxiv) are optional enhancements, not requirements

---

## Implementation Phases

### Phase 1: Foundation + Core (First delivery)
- `plugin.json` manifest
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
- `agents/r-dependency-manager.md`

### Phase 3: Statistics, Clinical & Publishing
- `r-stats/`
- `r-clinical/`
- `r-tables/`
- `r-quarto/`
- `agents/r-statistician.md`

### Phase 4: Performance
- `r-performance/`

Each phase is independently deliverable and testable. Later phases build on the foundation but don't require changes to earlier phases.

---

## Quality Assurance

Each skill and agent includes 3-5 example prompts with expected behavior descriptions in a `## Examples` section of its SKILL.md or agent markdown. These serve as:
- A lightweight test suite during development (run the prompt, verify the output matches expectations)
- Documentation for users on what the skill/agent can do
- Regression checks when updating skill prompts

---

## Success Criteria

- Every skill has YAML frontmatter with `name` and `description` (trigger condition)
- Every agent has defined input/output contracts and procedure
- R conventions rule is under 150 lines, comprehensive but concise
- Each SKILL.md body is under 300 lines; reference files loaded lazily
- Skills produce idiomatic, modern R code conforming to `r-conventions.md`
- Statistical advice is sound and includes appropriate caveats
- MCP integration enhances but is never required — graceful degradation
- Plugin is installable from Claude Code marketplace as a single unit via `plugin.json`
- `r-debugging` dispatches to `r-code-reviewer` when code quality issues are suspected
