# Release Notes

## 0.3.0 (2026-05-01)

`r-bayesian` skill — Bayesian inference with the Stan ecosystem. Adds 19th
domain skill covering the prior-fit-diagnose-summarize workflow for
`brms`, `rstanarm`, `cmdstanr`, `posterior`, and `tidybayes`. Aimed at the
common silent failure modes: improper-flat priors on regression
coefficients, ignored divergences, bare posterior means without intervals,
and AIC/BIC misuse on Bayesian fits.

### Added

- **`skills/r-bayesian/SKILL.md`** — 5+ trigger phrases (`brms`, `MCMC`,
  `posterior`, `Stan`, `Bayesian`, `divergences`, `Rhat`, `tidybayes`,
  `pp_check`); explicit negative boundaries against r-stats (frequentist
  inference), r-tidymodels (ML tuning), and r-clinical (regulatory). Body
  covers engine choice (brms vs rstanarm vs cmdstanr), the mandatory
  five-step workflow, and the four-diagnostic battery (Rhat, ESS,
  divergences, posterior predictive).
- **Four lazy references:**
  - `references/model-formulas.md` — multilevel, distributional,
    nonlinear, mixture, monotonic, ordinal, censored, multivariate.
  - `references/prior-choice.md` — weakly-informative defaults table,
    family-specific guidance, mandatory prior predictive check, sensitivity
    analysis pattern.
  - `references/mcmc-diagnostics.md` — Rhat / ESS thresholds, divergence
    diagnosis with `mcmc_pairs`, `adapt_delta` escalation, treedepth,
    E-BFMI, posterior predictive failure decoder, LOO Pareto-k.
  - `references/tidybayes-patterns.md` — `spread_draws` /
    `gather_draws`, `add_epred_draws` / `add_linpred_draws` /
    `add_predicted_draws`, `ggdist` visualization, ROPE,
    `compare_levels`.
- **`skills/r-bayesian/eval.md`** — 10 binary eval questions plus
  happy / edge / adversarial / boundary test prompts and ten success
  criteria including frequentist-deferral and divergence-handling rules.
- **Session-start hook** detects Bayesian projects: `.stan` files,
  `_brms_*.rds` cache artifacts, and `brms` / `rstanarm` / `cmdstanr` /
  `posterior` / `tidybayes` in `DESCRIPTION`. Surfaces `/r-bayesian` and
  the `r-statistician` agent.

### Changed

- **r-stats** — Bayesian section replaced with a hard boundary deferring
  to r-bayesian; description trigger list trimmed to remove "Bayesian
  methods"; negative-boundary line added.
- **r-tidymodels** — negative-boundary line added pointing at r-bayesian.
- **r-clinical** — negative-boundary line added pointing at r-bayesian
  (clinical Bayesian work outside regulatory submissions belongs there).
- **Routing matrix** (`tests/routing_matrix.json`) — six new entries
  under category `bayesian-routing`: brms multilevel + HDI; divergence
  diagnosis; prior predictive check; tidybayes spread_draws + forest plot;
  frequentist p-value framing stays in r-stats; XGBoost tuning stays in
  r-tidymodels.
- **README / CLAUDE.md** — skill count bumped 18 → 19 in badge, four-layer
  diagram, and skill table; r-bayesian row added to skill table; project
  structure list updated.

### Notes

- The skill works fully without `cmdstanr`, but the SKILL.md and
  references recommend `backend = "cmdstanr"` because it ships HMC
  improvements faster than rstan. Surface `cmdstanr::install_cmdstan()`
  to users before they fit if it isn't installed.
- All R code in the new content uses `|>`, `<-`, `snake_case`, and double
  quotes. Verified with `grep -rn '%>%' skills/r-bayesian/ --exclude=eval.md`.

---

## 0.2.3 (2026-05-01)

PostToolUse auto-format hook. Whenever Claude edits an `.R`, `.r`, `.Rmd`,
`.rmd`, `.Rmarkdown`, or `.qmd` file via `Edit`, `Write`, or `MultiEdit`, the
plugin now runs `styler::style_file()` on it automatically — keeping on-disk
code tidyverse-styled without anyone remembering to run it. When the file
actually changes, Claude is nudged to re-read before further edits so shifted
line numbers don't cause stale-edit errors.

### Added

- **`hooks/post-tool-use-format`** — bash hook that parses the hook payload
  with `python3` (preferred) or a `grep`/`sed` fallback, runs styler under
  `timeout`/`gtimeout` (default 15s, configurable via
  `SUPERPOWERS_AUTOFORMAT_TIMEOUT`), hashes the file before/after to detect
  real changes, and emits `additionalContext` only when something was
  reformatted.
- **`hooks/hooks.json`** — `PostToolUse` matcher for `Edit|Write|MultiEdit`
  wired through the existing `run-hook.cmd` polyglot dispatcher.
- **README** — new "Hooks" section, troubleshooting rows for the auto-format
  hook, and opt-out instructions (env var, hooks.json edit, settings.json).

### Behavior notes

- Skips silently when `Rscript` or `styler` is not installed (no install nag).
- Skips silently on non-R file extensions and on non-write tools.
- Disable per-shell with `export SUPERPOWERS_DISABLE_AUTOFORMAT=1`.
- Output JSON shape adapts to host (Claude Code, Cursor, Copilot CLI).

### Skipped from initial design

- `lintr::lint()` second pass — design called for it to be silent by default,
  so the simpler choice is to not ship it until there's a clear need. Open an
  issue if you'd find it useful.

---

## 0.2.1 (2026-04-30)

Documentation patch. Adds an evidence-based content-structure reference to
`r-reporting`, distilled from biostatistical reporting literature
(ICH E9(R1), CONSORT, STROBE, JAMA SAP, ASA, TIER, NASEM). Lazy-loaded; no
behavior changes for existing users.

### Added

- **`skills/r-reporting/references/report-content-structure.md`** — 12-section
  spine for consulting reports, ICH E9(R1) five-attribute estimand framework,
  prespecification labeling vocabulary, PICOTA multiplicity framework,
  MCAR/MAR/MNAR missing-data handling with required sensitivity analyses,
  R-flavored reproducibility appendix template, uncertainty-communication
  language replacements, and the consultant-vs-client interpretation
  boundary.
- **`docs/compass_artifact_*.md`** — source research artifact behind the
  reference, kept for traceability.

### Changed

- **`skills/r-reporting/SKILL.md`** — one-line pointer added to the lazy
  references list. The skill description, frontmatter, and routing matrix are
  unchanged; the new reference loads only when explicitly read.

### Notes

- The companion editorial-template skill (CONSORT/STROBE/TRIPOD-aware Quarto
  scaffolds with section-by-section prompt text) remains on the deferred
  scope list in `docs/superpowers/specs/2026-04-30-r-reporting-design.md`.

---

## 0.2.0 (2026-04-29)

First marketplace-ready release. supeRpowers is now a four-layer R programming plugin for Claude Code: 17 skills, 5 slash commands, 5 agents, 1 foundation rule, and a session-start hook — installable with one command.

### Highlights

- **Slash commands.** Five guided workflows are now first-class plugin commands: `/r-tdd-cycle`, `/r-debug`, `/r-pkg-release`, `/r-shiny-app`, `/r-analysis`. Each orchestrates the right skills and agents for a multi-step task.
- **Marketplace install.** Add the repo as a marketplace and install with two commands. Verified end-to-end on macOS.
- **Project-aware session start.** A hook detects R project type (package, Shiny, targets, Quarto, analysis, scripts) and surfaces the most relevant skills, commands, and agents for that project. Cross-platform via a polyglot runner.
- **Toolchain breadth.** Coverage now spans data analysis, visualization, statistics, biostatistics, Shiny, package development, tables, Quarto, performance, machine learning (tidymodels), pipelines (targets), MCP setup, TDD, debugging, and package-skill generation.

### Installation

```bash
claude plugin marketplace add alexvantwisk/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

Or from a local clone:

```bash
claude plugin marketplace add /path/to/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

### Added

#### Skills (4 new since 0.1.0)

- **r-project-setup** — scaffold analysis projects, packages, Shiny apps, Quarto documents (`usethis`, `renv`, `golem`, `quarto`)
- **r-tidymodels** — machine learning workflow: recipes, workflows, tune, yardstick
- **r-targets** — reproducible pipelines, branching, crew integration
- **r-mcp-setup** — MCP server setup for live R session awareness (`btw`, `mcptools`)

(Plus the 13 skills shipped in 0.1.0: r-data-analysis, r-visualization, r-tdd, r-debugging, r-package-dev, r-shiny, r-stats, r-clinical, r-tables, r-quarto, r-performance, r-package-skill-generator, and the meta-skill r-skill-auditor.)

#### Commands (5 new — first appearance)

- **/r-tdd-cycle** — Red, Green, Refactor, Review for testthat 3e packages
- **/r-debug** — reproduce, isolate, diagnose, fix, regression test, verify
- **/r-pkg-release** — audit deps, test, document, R CMD check, version bump, review, submit
- **/r-shiny-app** — scaffold, design modules, wire reactivity, test, architecture review
- **/r-analysis** — import, clean, explore, model, visualize, report

#### Plugin infrastructure

- `.claude-plugin/plugin.json` — manifest in the location required by the current Claude Code plugin schema
- `.claude-plugin/marketplace.json` — declares the repo as a Claude Code marketplace so `claude plugin install` works
- `hooks/session-start` — R project type detection + MCP server probing, cross-platform via `hooks/run-hook.cmd`
- `hooks/detect-mcp.sh` — MCP availability helper used by the session-start hook
- All 5 agents now have YAML frontmatter (`name`, `description`) so Claude Code can dispatch them on intent

#### Documentation

- README with version/license/skills/commands/R badges, four-layer architecture diagram, full skill and command tables, agent catalog, quick-start prompts, install verified end-to-end
- CLAUDE.md development guide covering content formats (skills, commands, agents, rules), R coding conventions, and a verification checklist
- LICENSE (MIT)

### Changed

- **Plugin layout migrated to `commands/`.** The 5 workflow files that previously lived as `skills/r-cmd-*/SKILL.md` are now native plugin commands at `commands/r-*.md`. The redundant `cmd-` infix was dropped: `/r-cmd-tdd-cycle` → `/r-tdd-cycle`, etc. Body content is unchanged — these are the same workflows in a more idiomatic location.
- **Manifest schema updated.** Removed the legacy `claude_code` wrapper from `plugin.json`; content is auto-discovered from the standard directories. `author` is now the object form the validator expects.
- **CLAUDE.md content formats** — agents now require frontmatter (`name`, `description`); commands documented as a new content type alongside skills, rules, and agents.
- **Sibling skill cross-references** updated so the negative-boundary text in `r-data-analysis`, `r-debugging`, `r-tdd`, `r-shiny`, and `r-package-dev` points at the new `/r-*` slash commands.
- **Session-start hook** recommends the new slash command names, not the deprecated `/r-cmd-*` form.

### Fixed

- `tests/test_structural.py` no longer references the removed `claude_code` wrapper. The obsolete glob-coverage and hook-presence tests were dropped (auto-discovery makes the first redundant; `claude plugin validate` covers the second).
- `tests/test_structural.py` gained a new "Command Files" section that validates frontmatter, required `description` field, and the 200-line limit on every file in `commands/`.

### Deprecated / Removed

- The 5 `skills/r-cmd-*/` directories were removed in this release. They had no installed users — the plugin had not yet been published to a marketplace before now. Any prior in-development reference to `/r-cmd-<name>` should be updated to `/r-<name>`.

### Known Issues

- The plugin name `supeRpowers` is not kebab-case. Claude Code accepts it for local and GitHub-marketplace installs (verified in this release), but the public claude.ai marketplace sync requires kebab-case. A future major version may rename for that purpose.
- A small number of pre-existing test failures remain in `python tests/run_all.py` (e.g. `agent-no-frontmatter` checks that conflict with the new requirement, `r-mcp-setup` description format gaps, a couple of line-limit overruns). These do not affect plugin behavior at runtime; tracked for the 0.2.x patch series.

### Documentation Pointers

- Migration plan and rationale: `docs/superpowers/plans/2026-04-29-cmd-skills-to-commands-migration.md`
- Superseded design: `docs/superpowers/specs/2026-04-01-commands-layer-design.md` (kept for historical context — the assumption that plugins didn't support a `commands/` directory turned out to be wrong)
- Development conventions: `CLAUDE.md`

---

## 0.1.0 (2026-03-15)

Initial scaffold release.

### Added

- **Foundation:** r-conventions rule (base pipe, tidyverse-first, style guide)
- **Phase 1:** r-data-analysis, r-visualization, r-tdd, r-debugging skills
- **Phase 2:** r-package-dev, r-shiny skills + r-code-reviewer, r-dependency-manager agents
- **Phase 3:** r-stats, r-clinical, r-tables, r-quarto skills + r-statistician, r-pkg-check, r-shiny-architect agents
- **Phase 4:** r-performance, r-package-skill-generator skills
- **Docs:** CLAUDE.md development guide
- **Config:** plugin.json manifest
