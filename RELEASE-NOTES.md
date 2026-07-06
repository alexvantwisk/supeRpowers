# Release Notes

## 0.7.1 (2026-07-06) — dplyr 1.2 currency

Document the dplyr 1.2 elementwise `when_any()` / `when_all()` helpers in the
r-data-analysis reference corpus and correct the dplyr 1.2 release date.
Content/docs only — no skill, agent, hook, or count changes.

### Added

- **`when_any()` / `when_all()` section** in
  `skills/r-data-analysis/references/dplyr-patterns.md` — elementwise OR / AND
  across logical vectors, with the `filter()` / `filter_out()` usage pattern.

### Fixed

- **dplyr 1.2 release date** in `dplyr-patterns.md` corrected from "Feb 2026"
  to "Apr 2026" (CRAN: dplyr 1.2.1 on 2026-04-03).
- **Convention-checker false positives** — `tests/test_conventions.py` now
  strips double-quoted literals before its single-quote scan, so single quotes
  used as regex metacharacters (`[\"']`) or literal search characters
  (`paste0("'", w, "'")`) no longer warn. Suite is warning-clean (651/651).

### Notes

- No new features; skill/agent/rule counts unchanged
  (26 skills / 5 agents / 1 rule).

---

## 0.7.0 (2026-07-05) — Platform Alignment

Align supeRpowers with the 2026 Claude Code plugin spec: migrate the slash
commands into workflow skills, split trigger prose into a `when_to_use`
frontmatter field, add glob `paths` gating, ship skill-creator-style evals with
a deterministic CI-gating layer, and harden CI to a three-OS matrix. Structural
and platform migration only — no new domain content, and every `/r-*` workflow
invokes byte-identically to before.

### Added

- **`when_to_use` frontmatter** on all 20 knowledge skills — trigger phrases now
  live here; `description` keeps the capability sentence and `Do NOT …`
  boundaries. Combined `description` + `when_to_use` is budgeted to ≤ 1536 chars
  (max observed: 995).
- **`paths` gating** on the four file-signature skills: `r-quarto`
  (`**/*.qmd`), `r-shiny` (`app.R`, `server.R`, `ui.R`, `R/mod_*.R`),
  `r-targets` (`_targets.R`), `r-package-dev` (`DESCRIPTION`, `NAMESPACE`).
- **Evals** — `evals/evals.json` for `r-data-analysis`, `r-visualization`,
  `r-package-dev`, `r-stats`, `r-reporting`, plus reproduce-before-fix /
  RED-before-GREEN pressure-scenario sets for `r-debugging` and `r-tdd`.
- **Layer 3 test suite** (`tests/test_evals.py`) — deterministic, offline eval
  validation wired into `run_all.py` and CI (`--layer 3`).
- **`tests/smoke_session_start.py`** — cross-platform smoke test asserting the
  session-start hook emits valid JSON and spawns zero `Rscript` in a non-R dir.
- **CI hardening** — three-OS matrix (ubuntu/macos/windows), a `shellcheck` job
  over the bash hooks, per-OS session-start smoke, and a dedicated eval job.
- **README capability matrix** (by domain) and a **"supeRpowers vs
  posit-dev/skills"** positioning section.

### Changed

- **6 slash commands → workflow skills.** `r-analysis`, `r-debug`,
  `r-pkg-release`, `r-report`, `r-shiny-app`, and `r-tdd-cycle` are now skills
  with `disable-model-invocation: true`, invoked only as `/r-<name>` and never
  intent-routed. Bodies ported byte-for-byte; `/r-*` behavior is unchanged.
- **Test harness** reads triggers from `description` + `when_to_use`; adds
  `frontmatter-budget`, `has-when-to-use`, and workflow-skill assertions; removes
  the command-file checks; routing matrix gains six workflow-no-route guards.
- **Inventory surfaces** (README, CLAUDE.md, `r-overview`, session-start hook)
  reworded from "commands" to "workflow skills". Counts: **26 skills**
  (20 knowledge + 6 workflow), 5 agents, 1 rule, **0 commands**.
- **hooks/session-start** — removed a dead `PLUGIN_ROOT` variable; now
  shellcheck-clean.
- **Version** — 0.6.0 → 0.7.0.

### Removed

- The **`commands/` directory** (all 7 files). Six became workflow skills; the
  seventh, `/r-overview`, is absorbed by the existing `r-overview` knowledge
  skill, which is slash-invocable under the 2026 model.

### Notes

- No new domain content — this is a structural/platform migration.
- Deferred to a post-tag follow-up: community-marketplace distribution. The full
  with/without-skill LLM eval benchmark runs manually/nightly, not in PR-gating CI.

---

## 0.6.0 (2026-07-04)

Currency pass: bring the content corpus from its early-2024 snapshot to
July-2026 reality without changing skill/command/agent counts.

### Changed

- **r-visualization** — ggplot2 4.0 sweep: `legend.position = "inside"` +
  `legend.position.inside`, `coord_transform()`, `transform =` /
  `scales::new_transform()`; removed `legend.title.align`; added a "what
  changed in 4.0" (S7, ink/paper/accent) orientation block to
  `references/theme-guide.md`.
- **r-stats, r-clinical, r-statistician, r-reporting** — migrated all
  Kaplan-Meier / survival plotting from `survminer` to `ggsurvfit`
  (`survfit2()` + `add_confidence_interval()`/`add_risktable()`/`add_pvalue()`);
  replaced `ggcoxdiagnostics`/`ggcoxfunctional` with base-survival residual
  diagnostics. survminer survives only as a one-line legacy note.
- **r-performance** — three explicit large-data tiers (in-RAM;
  arrow `open_dataset()` / duckdb / duckplyr; mirai + `purrr::in_parallel()` /
  crew), with detail offloaded to `references/large-data-tiers.md`; furrr/future
  demoted to a compatibility note.
- **r-shiny** — `ExtendedTask` + `bslib::input_task_button()` is now the primary
  async pattern; fixed the `output$` inside `observe()` anti-pattern in
  `references/reactivity-guide.md`.
- **r-quarto** — added Typst (LaTeX-free PDF), `format: dashboard`, and
  brand.yml via `references/formats-2026.md`; corrected `quarto create document`
  and the knitr `cache.extra` advice.
- **rules/r-conventions, r-project-setup, r-package-dev** — Air-first formatter
  story with styler as the in-R alternative; corrected Air install
  instructions; removed the `setwd()` self-contradiction; Positron
  acknowledgments.
- **r-dependency-manager, r-targets, r-tidymodels** — Bioconductor 3.21–3.23,
  `qs` → `qs2`, `crew.cluster` for HPC, tailor post-processing + `finetune`
  racing.
- **Smaller corrections** — Hosmer-Lemeshow caveat + calibration pointer;
  `GVIF^(1/(2*Df))` adjustment in `check_assumptions.R`; `map_dfr` →
  `map() |> list_rbind()` across the corpus; r-overview names mcp-repl; r-data-analysis
  references `check_join_safety.R`; skill-generator versions marked illustrative.
- **hooks/session-start** — R-version/package probes moved past the project
  early-exit and wrapped in `timeout`/`gtimeout`; a non-R directory now spawns
  zero `Rscript` processes; context gains a `/r-overview` pointer.
- **tests/routing_matrix.json** — added discovery, bayesian↔clinical, bare-KM,
  and project-setup↔targets scaffold seams; enriched the r-targets boundary.
- **Version** — 0.5.1 → 0.6.0.

### Notes

- No new skills, commands, or agents. Counts stay 20 / 7 / 5.
- styler remains the auto-format hook; Air is taught, not wired in.

---

## 0.5.1 (2026-07-04)

Trust release. Fixes every verified-broken or fabricated API in the content
corpus and every documentation claim contradicted by the code, so a user's
first contact never hits a runtime error, a dead end, or a false instruction.
Content and documentation only — no new features, no hook behavior changes.

### Fixed

- **r-clinical** — replaced the `sfu = sfO'Brien-Fleming` parse error with
  `sfu = sfLDOF` (Lan-DeMets O'Brien-Fleming); rewrote the subgroup-analysis
  scaffold so it iterates observed `(subgroup, level)` pairs and fits a Cox
  model per stratum (the old scaffold referenced an undefined `level`);
  swapped the deprecated `geom_errorbarh()` in the forest-plot template for
  `geom_errorbar(orientation = "y")`.
- **r-tables** — removed two fabricated gtsummary APIs: the invalid
  `theme_gtsummary_journal("bmj")` (gtsummary 2.5.0 supports only `jama`,
  `lancet`, `nejm`, `qjecon`) and the nonexistent
  `theme_gtsummary_printer_friendly()`.
- **r-tdd** — `vdiffr::manage_cases()` (removed in vdiffr 1.0) →
  `testthat::snapshot_review()`; corrected the `withr::local_tempdir()`
  claim (it does not change the working directory) and switched the example
  to `withr::local_dir(withr::local_tempdir())`.
- **r-package-dev** — defunct `rhub::check_for_cran()` → `rhub::rhub_check()`
  (rhub v2, GitHub Actions runners), in SKILL.md and both reference files;
  moved "no visible global function definition" from the ERRORs section to
  NOTEs (the shown excerpt is a NOTE).
- **r-data-analysis** — replaced deprecated `across(..., na.rm = TRUE)`
  dots-passing with anonymous-function form (`\(x) mean(x, na.rm = TRUE)`).
- **r-bayesian** — corrected the non-centered-parameterization guidance:
  brms emits non-centered group-level effects by default regardless of
  backend, so a backend switch is not a divergence fix; renamed the
  "Mandatory Four" heading that sat above a seven-row table.
- **r-shiny / r-debugging** — fixed the `isolate()`/`observe()` gotcha
  (infinite loops come from an observer writing a value it also reads) and
  the vector-recycling reprex (`filter(status == c("A","B"))` returns 2 rows,
  not 4).
- **Docs** — README verify step and troubleshooting no longer promise a
  visible session-start "banner" (the hook injects `additionalContext`);
  CONTRIBUTING, the PR template, and tests/README now state the suite must
  pass cleanly (exit 0) and drop the stale "141/141" / "ten pre-existing
  failures" language; CLAUDE.md hook description aligned to the
  `startup|clear|compact` matcher.
- **Detection / hygiene** — `hooks/detect-mcp.sh` now checks `~/.claude.json`
  (where `claude mcp add -s user` writes), so user-scoped registrations are
  seen; the issue-template config now welcomes PRs; the skill-suggestion
  example no longer names a real person.

### Notes

- No skill / command / agent counts change. No files created or deleted.

---

## 0.5.0 (2026-05-19)

Persistent R sessions. Extends `r-mcp-setup` with
[posit-dev/mcp-repl](https://github.com/posit-dev/mcp-repl) (Posit; Rust;
Apache-2.0) as a second supported MCP path alongside btw/mcptools — an
agent-owned, headless R session for autonomous work, complementing the
IDE-attached btw/mcptools pairing path.

### Added

- **`skills/r-mcp-setup/references/mcp-repl-setup.md`** — install and
  registration guide for the mcp-repl server.
- **`hooks/detect-mcp.sh`** — `mcp_repl_installed` and `mcp_repl_registered`
  booleans; session-start tips branch on which paths are active. Both paths
  can be registered at once since their tool names don't collide.

### Changed

- **`skills/r-mcp-setup/SKILL.md`** — restructured into a two-paths decision
  table (mcp-repl for agent-owned headless work, btw/mcptools for
  IDE-attached pairing).
- **Routing matrix** — six positive `r-mcp-setup` entries added (first-time
  coverage).
- **`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`** —
  version bump to `0.5.0`.

### Notes

- Skill count unchanged (additive within the existing `r-mcp-setup` skill).

---

## 0.4.0 (2026-05-01)

Discovery surface for users coming in cold. Adds an `r-overview` skill that
fires on plain-English orientation questions ("what can supeRpowers do?",
"what R skills do you have?", "list available R helpers") and a matching
`/r-overview` slash command for explicit invocation. Both render the same
grouped inventory of every skill, command, and agent shipped here, so the
unfamiliar-user path is obvious in two complementary ways — explicit
(typed `/`) and conversational (asked in plain English).

Counts move 19 → 20 skills and 6 → 7 commands.

The tradeoff considered against broadening the session-start hook to fire on
any `Rscript` presence: the broader hook adds noise for users who have R
installed but aren't asking about R. The discovery surface only renders when
explicitly invoked or asked for, so the quiet-mode behavior of the
session-start hook is preserved.

### Added

- **`skills/r-overview/SKILL.md`** — low-trigger discovery skill. Description
  is intentionally narrow ("Use when the user asks what supeRpowers can do,
  requests a list or directory of available R skills / commands / agents…")
  with explicit boundaries against actual R work and against the closest
  meta-skills (r-mcp-setup, r-package-skill-generator). Body renders a
  grouped inventory (Data & visualization / Modeling / Engineering /
  Publishing / Tooling & meta) with trigger words per skill so the user
  learns the routing vocabulary while orienting.
- **`skills/r-overview/eval.md`** — 10 binary eval questions plus
  happy / edge / adversarial / boundary prompts. Boundary tests cover
  the two highest-risk over-fire cases: concrete domain tasks
  (e.g. "fit a brms model") that should bypass the inventory, and
  meta-tasks that belong to sibling skills (MCP setup, skill generation).
- **`commands/r-overview.md`** — thin command that invokes the
  `r-overview` skill so the rendered inventory stays in lockstep with the
  on-disk skill content. No multi-step workflow; explicit "stop after
  rendering" guard.

### Changed

- **`README.md`** — skills badge 19 → 20, commands badge 6 → 7,
  architecture diagram, skills table (new `r-overview` row in the meta-tool
  group), commands table (new `/r-overview` row). Quick-Start prose
  updated.
- **`CLAUDE.md`** — project structure listing adds `r-overview/` under
  meta skills and `r-overview.md` under commands. Roadmap "Shipped" log
  gains 0.3.1 (manifest patch) and 0.4.0 (discovery surface) entries.
- **`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`** —
  version bump to `0.4.0`.

### Notes

- This release is purely additive on the content surface. No existing skill
  triggers, command bodies, or agent definitions were touched, so 0.3.x
  users see no behavior change unless they invoke `/r-overview` or ask the
  plugin what it can do.

---

## 0.3.1 (2026-05-01)

Manifest validation patch. The `repository` field in `.claude-plugin/plugin.json`
must be a string under the current Claude Code plugin schema, not the
npm-style `{type, url}` object. The 0.3.0 manifest used the object form, which
caused `/doctor` to flag the plugin with `repository: Invalid input: expected
string, received object`. This release ships the corrected manifest under a
new version so cached installs refresh.

### Fixed

- **`.claude-plugin/plugin.json`** — `repository` now a plain URL string
  (`"https://github.com/alexvantwisk/supeRpowers"`). No behavior change beyond
  clearing the manifest validation error.

### Notes

- If you installed 0.3.0 and saw `/doctor` errors, run
  `claude plugin marketplace update supeRpowers` followed by
  `claude plugin install supeRpowers@supeRpowers` to pick up 0.3.1.

---

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
