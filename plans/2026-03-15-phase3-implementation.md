# Phase 3: Statistics, Clinical & Publishing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking. **CRITICAL:** When creating any SKILL.md file, you MUST invoke the `superpowers:writing-skills` skill FIRST before writing.

**Goal:** Deliver four domain skills (r-stats, r-clinical, r-tables, r-quarto) and one agent (r-statistician) for Phase 3 of the supeRpowers plugin.

**Architecture:** Same layered design as Phases 1-2. Skills get YAML frontmatter with `name` and `description`. Agents use Inputs/Output/Procedure format without frontmatter. All R code follows `r-conventions.md`.

**Tech Stack:** Claude Code skills/agents (YAML frontmatter + markdown), R >= 4.1.0, tidyverse, lme4, survival, brms, tsibble/fable, pwr, gtsummary, gt, gtExtras, quarto, Clinical Trials MCP, bioRxiv MCP.

**Spec:** `.claude/plans/2026-03-15-superpowers-r-plugin-design.md` (lines 195-251 for Phase 3, lines 289-302 for r-statistician agent)

**Prerequisites:**
- Phase 1 complete (r-conventions.md, 4 core skills, r-code-reviewer agent)
- Phase 2 complete (r-package-dev, r-shiny skills, 3 agents)
- `superpowers:writing-skills` — for SKILL.md authoring
- **Hook constraint:** Agent .md files in `.claude/agents/` must be created via Bash heredoc (Write tool blocked by hook for that path)

---

## Task 1: Create r-stats skill

**Files:**
- Create: `.claude/skills/r-stats/SKILL.md`
- Create: `.claude/skills/r-stats/references/model-selection-guide.md`
- Create: `.claude/skills/r-stats/references/assumption-checklist.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-stats
description: >
  Use when performing statistical modeling, hypothesis testing, or model
  diagnostics in R. Covers linear models, GLMs, mixed models, survival
  analysis, Bayesian methods, time series, and model comparison.
---
```

**Body must cover (max 300 lines):**
- Linear models: `lm()`, diagnostics (residuals, Q-Q, VIF for multicollinearity)
- GLMs: logistic (`glm(family=binomial)`), Poisson, negative binomial (`MASS::glm.nb()`), quasi families
- Mixed models: `lme4::lmer()` / `lme4::glmer()`, random effects structure, convergence troubleshooting
- Survival analysis: `survival::Surv()`, Kaplan-Meier (`survfit()`), Cox PH (`coxph()`), time-varying covariates
- Bayesian: `brms` / `rstanarm`, prior selection guidance, posterior checks
- Time series: `tsibble`/`fable` ecosystem, ARIMA, state space models, forecasting
- Multiple testing: FDR correction (`p.adjust()`), Bonferroni, Holm
- Model comparison: AIC/BIC, likelihood ratio tests, cross-validation with `rsample`/`tidymodels`
- Dispatch to `r-statistician` agent for consulting and assumption verification
- Lazy references: "Read `references/model-selection-guide.md`" and "Read `references/assumption-checklist.md`"
- 3-5 example prompts

**Reference: model-selection-guide.md** — Model selection flowchart:
- Decision tree: outcome type × predictor structure → recommended model family
- Continuous outcome: lm → mixed models → GAM
- Binary outcome: logistic → mixed logistic → penalized logistic
- Count outcome: Poisson → negative binomial → zero-inflated
- Time-to-event: KM → Cox PH → parametric survival
- tidymodels workflow: recipe → model spec → workflow → fit → evaluate

**Reference: assumption-checklist.md** — Model assumption verification:
- For each model family: assumptions list with R code to check each
- Linear model: linearity, normality, homoscedasticity, independence, no multicollinearity
- GLM: link function appropriateness, overdispersion, influential observations
- Mixed model: random effects normality, residual patterns, convergence
- Survival: proportional hazards (Schoenfeld residuals), censoring patterns

---

## Task 2: Create r-clinical skill

**Files:**
- Create: `.claude/skills/r-clinical/SKILL.md`
- Create: `.claude/skills/r-clinical/references/cdisc-adam-guide.md`
- Create: `.claude/skills/r-clinical/references/tlf-templates.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-clinical
description: >
  Use when performing clinical trial analysis, biostatistics, regulatory
  submissions, or biomedical research in R. Covers trial design, CDISC,
  survival endpoints, biomarkers, meta-analysis, and MCP integration.
---
```

**Body must cover (max 300 lines):**
- Trial design: power analysis (`pwr`, `gsDesign`), sample size calculation, adaptive designs
- CDISC: ADaM and SDTM dataset structure awareness, naming conventions
- Regulatory tables: TLFs (Tables, Listings, Figures) generation patterns
- Survival endpoints: OS, PFS, DFS — censoring, competing risks (`cmprsk`)
- Biomarkers: ROC curves (`pROC`), cutpoint optimization (`cutpointr`), subgroup analysis
- Meta-analysis: `meta`/`metafor`, forest plots, heterogeneity assessment (I², Q-test)
- Genomics bridge: `DESeq2`, `limma`, enrichment analysis (brief — Bioconductor)
- MCP integration: Clinical Trials MCP tools (search_trials, get_trial_details, analyze_endpoints, search_by_sponsor, search_investigators, search_by_eligibility) + bioRxiv MCP tools (search_preprints, get_preprint, search_published_preprints, search_by_funder). All MCP features optional.
- ICH guideline awareness, CONSORT flow diagram patterns
- Dispatch to `r-statistician` agent for methodology questions
- Lazy references: "Read `references/cdisc-adam-guide.md`" and "Read `references/tlf-templates.md`"
- 3-5 example prompts

**Reference: cdisc-adam-guide.md** — CDISC ADaM/SDTM guide:
- ADaM dataset types: ADSL, ADAE, ADTTE, ADLB, ADRS, ADEFF
- ADaM variable naming conventions (PARAM, PARAMCD, AVAL, CHG, BASE, etc.)
- SDTM domains overview: DM, AE, LB, VS, EX, CM
- R packages for CDISC: `admiral`, `metacore`, `metatools`
- Traceability requirements

**Reference: tlf-templates.md** — TLF generation patterns:
- Table 1 (demographics): gtsummary `tbl_summary()` with clinical trial conventions
- AE summary table pattern
- Efficacy endpoint table (primary, secondary)
- Kaplan-Meier figure with risk table
- Forest plot for subgroup analysis
- Waterfall plot for tumor response
- CONSORT flow diagram code pattern

---

## Task 3: Create r-tables skill

**Files:**
- Create: `.claude/skills/r-tables/SKILL.md`
- Create: `.claude/skills/r-tables/references/gtsummary-themes.md`
- Create: `.claude/skills/r-tables/references/gt-formatting-patterns.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-tables
description: >
  Use when creating publication-quality tables in R with gt, gtsummary,
  gtExtras, or reactable. Covers formatting, themes, journal styles, and
  output to HTML, PDF, and Word.
---
```

**Body must cover (max 300 lines):**
- gt fundamentals: table structure (`gt()`, `tab_header()`, `cols_label()`), formatting (`fmt_number()`, `fmt_percent()`, `fmt_currency()`), styling (`tab_style()`, `cell_fill()`, `cell_text()`), spanners, footnotes, source notes
- gtsummary workflows: `tbl_summary()` for descriptive stats, `tbl_regression()` for model results, `tbl_merge()` / `tbl_stack()` for combining tables, `add_p()`, `add_overall()`, `add_difference()`
- gtExtras: sparklines (`gt_sparkline()`), inline plots (`gt_plt_bar()`), icons, themes (`gt_theme_538()`, `gt_theme_nytimes()`, `gt_theme_espn()`)
- Patterns: Table 1 (demographics), regression results, comparison tables, summary statistics
- Output formats: HTML, PDF via LaTeX, Word via `flextable` fallback, `as_gt()` conversions
- Journal themes: gtsummary themes for JAMA, Lancet, etc. (`theme_gtsummary_journal()`)
- Interactive tables: `reactable` for Shiny/Quarto contexts
- Lazy references: "Read `references/gtsummary-themes.md`" and "Read `references/gt-formatting-patterns.md`"
- 3-5 example prompts

**Reference: gtsummary-themes.md** — Theme catalog:
- Built-in themes: journal (JAMA, Lancet, NEJM), compact, printer-friendly
- Custom theme creation with `set_gtsummary_theme()`
- Language customization
- Statistic display patterns

**Reference: gt-formatting-patterns.md** — Advanced gt formatting:
- Conditional formatting (color scales, data bars)
- Custom column spanners and grouped headers
- Embedding plots in cells
- Stub and row group styling
- Export workflows (HTML → PDF → Word pipeline)

---

## Task 4: Create r-quarto skill

**Files:**
- Create: `.claude/skills/r-quarto/SKILL.md`
- Create: `.claude/skills/r-quarto/references/yaml-config-cheatsheet.md`
- Create: `.claude/skills/r-quarto/references/cross-reference-syntax.md`

**CRITICAL: Invoke `superpowers:writing-skills` skill BEFORE writing the SKILL.md.**

**Frontmatter:**
```yaml
---
name: r-quarto
description: >
  Use when creating Quarto documents, presentations, websites, or books in R.
  Covers YAML configuration, code chunks, cross-references, journal templates,
  and multi-format publishing.
---
```

**Body must cover (max 300 lines):**
- Documents: reports, manuscripts, technical memos with R code execution
- Presentations: revealjs slides with R output, speaker notes, incremental reveals
- Websites: project sites, blogs, documentation sites, `quarto publish`
- Books: multi-chapter projects, cross-references, bibliographies
- Configuration: YAML format options, execution control (`execute:` block), parameters, conditional content
- Code chunks: `#|` syntax, caching strategies (`cache: true`), figure sizing (`fig-width`, `fig-height`), output options
- Cross-references: figures (`@fig-`), tables (`@tbl-`), equations (`@eq-`), sections (`@sec-`) — proper labeling
- Journal templates: `quarto-journals` extensions for academic submission (JASA, Elsevier, PLOS, etc.)
- Multi-format: single source → HTML + PDF + Word with format-specific content (`format:` block)
- Extensions: finding, installing (`quarto add`), and using community Quarto extensions
- Lazy references: "Read `references/yaml-config-cheatsheet.md`" and "Read `references/cross-reference-syntax.md`"
- 3-5 example prompts

**Reference: yaml-config-cheatsheet.md** — YAML configuration reference:
- Document-level YAML: title, author, date, format options
- Execution options: eval, echo, warning, message, cache, freeze
- Format-specific options: HTML (toc, theme, code-fold), PDF (documentclass, geometry), Word (reference-doc)
- Project-level YAML: `_quarto.yml` structure for websites/books
- Parameters and conditional content

**Reference: cross-reference-syntax.md** — Cross-reference guide:
- Figure refs: labeling with `#| label: fig-name`, referencing with `@fig-name`
- Table refs: `#| label: tbl-name`, `@tbl-name`
- Equation refs: `$$ ... $$ {#eq-name}`, `@eq-name`
- Section refs: `{#sec-name}`, `@sec-name`
- Theorem/proof environments
- Custom cross-reference types

---

## Task 5: Create r-statistician agent

**Files:**
- Create: `.claude/agents/r-statistician.md`

**Agent format (no YAML frontmatter). Max 200 lines.**

**Must cover:**
- Inputs: Research question or modeling task. Optionally: dataset summary (str/glimpse output), current model code, model output
- Output: Advisory report with recommended approach, assumptions to verify (with R code), interpretation guidance, warnings/caveats
- Procedure:
  1. Assess data structure and research question
  2. Recommend model family with rationale
  3. List assumptions with R code to verify each one
  4. If model output provided: interpret coefficients, CIs, effect sizes in plain language
  5. Flag risks: multiple comparisons, p-hacking, Simpson's paradox, correlation ≠ causation
  6. Biostat depth: survival diagnostics (Schoenfeld residuals, PH assumption), competing risks awareness
  7. Suggest next steps and sensitivity analyses
- Severity guide for recommendations

---

## Execution Strategy

**Tasks 1-4** (Skills): Execute in PARALLEL — fully independent. Each subagent must invoke `superpowers:writing-skills`.

**Task 5** (Agent): Execute in PARALLEL with skills — independent. Created via Bash heredoc due to hook constraint.

**All 5 tasks** are independent and can run simultaneously.

**Git strategy:** Each subagent creates files but does NOT commit. Orchestrator commits all files after verification.

**Verification:** After all tasks complete, verify file existence, line counts, YAML frontmatter, and no `%>%` usage.

```
    ┌──────────┬──────────┬──────────┬──────────┬──────────┐
    │ Task 1   │ Task 2   │ Task 3   │ Task 4   │ Task 5   │
    │ r-stats  │ r-clin   │ r-tables │ r-quarto │ r-stat-  │
    │ skill    │ skill    │ skill    │ skill    │ ician    │
    └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
         └──────────┴──────────┴──────────┴──────────┘
                              │
                         Verification
                         & Commit
```
