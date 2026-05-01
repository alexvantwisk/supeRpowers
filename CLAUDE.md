# supeRpowers Plugin — Development Guide

## What This Is

A Claude Code marketplace plugin providing expert-level R programming assistance. It ships 18 skills, 6 commands, 5 agents, and 1 rule — covering data analysis, visualization, statistics, clinical trials, Shiny, package development, tables, Quarto publishing, Word reporting, performance, machine learning, pipelines, TDD, debugging, MCP setup, and guided workflow commands.

## Project Structure

```
.claude-plugin/
  plugin.json            # Plugin manifest (name, version, author, license)
hooks/                   # Session lifecycle hooks
  hooks.json             # SessionStart hook configuration
  session-start          # R project detection script
  detect-mcp.sh          # MCP server detection helper
  run-hook.cmd           # Cross-platform wrapper
rules/                   # Foundation rules (loaded into every R conversation)
  r-conventions.md       # Base pipe |>, tidyverse-first, style guide
commands/                # Slash commands (user-invoked via /<name>)
  r-analysis.md          r-debug.md             r-pkg-release.md
  r-report.md            r-shiny-app.md         r-tdd-cycle.md
skills/                  # Skills (SKILL.md + optional references/, scripts/, eval.md)
  Domain skills:
    r-data-analysis/       r-visualization/       r-tdd/
    r-debugging/           r-package-dev/         r-shiny/
    r-stats/               r-clinical/            r-tables/
    r-quarto/              r-reporting/           r-performance/
    r-tidymodels/          r-targets/             r-project-setup/
    r-mcp-setup/           r-package-skill-generator/
  Meta skills:
    skill-auditor/
agents/                  # Shared agents (YAML frontmatter required)
  r-code-reviewer.md     r-statistician.md      r-pkg-check.md
  r-shiny-architect.md   r-dependency-manager.md
docs/                    # Reference documentation (e.g. docs/superpowers/)
tests/                   # Routing, structural, and convention test suites
```

## Content Formats

### Skills (`skills/*/SKILL.md`)

- YAML frontmatter with exactly two fields: `name` and `description`
- `description` starts with "Use when..." followed by third-person capability description, 5+ trigger phrases, and negative boundaries referencing sibling skills. Target 500 chars, hard limit 1024 chars.
- Body: max 300 lines (including frontmatter)
- Optional `references/` subdirectory for deep-dive content (lazy-loaded)
- Optional `scripts/` subdirectory for helper scripts

### Commands (`commands/*.md`)

- YAML frontmatter with a single field: `description` (one-line, shown in `/` autocomplete)
- Filename (without `.md`) is the slash command name (e.g. `commands/r-tdd-cycle.md` → `/r-tdd-cycle`)
- Body is the prompt that runs when the user invokes the command
- Max 200 lines (including frontmatter)
- May reference skills and agents inline ("Skill: r-tdd", "Agent: r-code-reviewer") to delegate domain knowledge

### Agents (`agents/*.md`)

- YAML frontmatter with exactly two fields: `name` and `description`
- `description` starts with "Use when..." and explains when to dispatch the agent
- Format below frontmatter: title, summary, Inputs, Output, Procedure sections
- Max 200 lines (including frontmatter)
- Severity guide table at the end

### Rules (`rules/*.md`)

- NO YAML frontmatter
- Max 150 lines
- Imperative reference card style, not prose

## R Code Conventions (Non-Negotiable)

All R code in this project — in skills, agents, rules, references, and examples — must follow:

- `|>` only, never `%>%` (magrittr)
- `<-` for assignment, never `=` (except in function arguments)
- Tidyverse-first: dplyr, tidyr, purrr, ggplot2, readr, stringr, forcats, lubridate
- `snake_case` for all identifiers
- Double quotes for strings
- Target R >= 4.1.0

Run this to check for violations (eval.md files reference `%>%` inside eval
questions and should be excluded):
```bash
grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md
```

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with the frontmatter format above
2. Add reference files to `skills/<name>/references/` if needed
3. Keep SKILL.md under 300 lines — offload detail to references
4. Include lazy reference pointers: `Read \`references/foo.md\` for...`
5. Include agent dispatch lines if the skill hands off to an agent
6. Include 3-5 example prompts at the end
7. Verify: no `%>%`, line count, frontmatter format

## Adding a New Command

1. Create `commands/<name>.md` with frontmatter `description: <one-line summary>`
2. Body is the prompt that runs on `/<name>` — Prerequisites, Progress Tracking, Steps, Abort Conditions, Examples
3. Reference skills and agents inline (e.g. `**Skill:** r-tdd`) so Claude dispatches them at the right step
4. Keep under 200 lines (including frontmatter)
5. No eval.md — commands are explicit invocations, not intent-routed

## Adding a New Agent

1. Create `agents/<name>.md` with YAML frontmatter (`name`, `description`) and Inputs/Output/Procedure format
2. `description` starts with "Use when..." so Claude Code knows when to dispatch
3. Keep under 200 lines (including frontmatter)
4. Include a severity guide table
5. Include 2-3 examples at the end

## Verification Checklist

Before committing any content changes:

- [ ] No `%>%` in skills/, commands/, agents/, rules/ (excluding `eval.md` files)
- [ ] SKILL.md files are ≤300 lines with correct frontmatter
- [ ] Command files are ≤200 lines with `description` frontmatter
- [ ] Agent files are ≤200 lines with `name` + `description` frontmatter
- [ ] Rule files are ≤150 lines with no frontmatter
- [ ] All R code uses `<-`, `|>`, snake_case, double quotes
- [ ] `claude plugin validate .` passes (warnings acceptable)
- [ ] Tests pass: `python tests/run_all.py`

## Hooks

The plugin includes a session-start hook (`hooks/session-start`) that fires on startup, resume, clear, and compact. It detects the R project type in the current directory (package, Shiny, targets, Quarto, analysis, scripts), detects available MCP servers via `hooks/detect-mcp.sh`, and injects context about relevant skills and agents. Configuration is in `hooks/hooks.json`; cross-platform invocation goes through `hooks/run-hook.cmd`.

## Tests

The `tests/` directory contains the plugin evaluation framework:

- `test_routing.py` — verifies skill routing against `routing_matrix.json`
- `test_structural.py` — checks file size limits and frontmatter shape
- `test_conventions.py` — enforces R code conventions
- `run_all.py` — runs the full suite

See `tests/README.md` for usage.

## Roadmap (next 2 priorities)

Phase 1 (GitHub Actions CI) shipped in 0.2.2. The remaining two phases are independently shippable.

### Phase 1 — PostToolUse auto-format hook

**Goal:** When Claude edits a `.R`, `.Rmd`, or `.qmd` file via Edit/Write, the file is auto-formatted with `styler` afterwards. Optional: `lintr` results surfaced as a system reminder.

**Why second:** Highest daily-impact lever. Every R interaction produces tidier code without anyone remembering to run `styler`. Self-contained — no skill or content changes.

**Scope:**

1. `hooks/post-tool-use-format` shell script:
   - Read tool name + file path from hook stdin
   - Skip unless `Edit`/`Write` and path matches `*.R|*.Rmd|*.qmd`
   - Detect `styler` availability (`Rscript -e 'requireNamespace("styler")'`); skip silently if missing
   - Run `Rscript -e 'styler::style_file("<path>")'` with a 5s timeout
   - Optional second pass: `lintr::lint("<path>")` → emit findings as a `<system-reminder>` so Claude sees them
2. Extend `hooks/run-hook.cmd` to dispatch `post-tool-use-format`.
3. Register a `PostToolUse` matcher in `hooks/hooks.json` for `Edit|Write`.
4. Document opt-out via `~/.claude/settings.json` in README.
5. Manual smoke test on a sample R project.

**Effort:** ~half a day.

**Risk:** Low. Two design questions to nail down: (a) when styler changes line counts, the hook should announce the format ran so Claude re-reads the file; (b) start with lintr output silent, escalate to surfacing later if useful.

**Release:** Patch bump to 0.2.3 (or fold into 0.3.0).

### Phase 2 — `r-bayesian` skill

**Goal:** A new domain skill covering Bayesian modeling with `brms`, `rstanarm`, `cmdstanr`, `posterior`, and `tidybayes`. SKILL.md plus 3–4 references.

**Why third:** Largest single content gap. Bayesian is a major statistical paradigm where Claude's defaults are notably weaker than for frequentist work — priors, MCMC diagnostics, and posterior summarization are full of subtle traps the plugin can encode. Builds on stable CI + hook foundations.

**Scope:**

1. `skills/r-bayesian/SKILL.md` — frontmatter with 5+ trigger phrases (`brms`, `MCMC`, `posterior`, `stan`, `Bayesian`), boundaries against r-stats (frequentist) and r-tidymodels (ML); body covering the brms workflow.
2. `skills/r-bayesian/references/`:
   - `model-formulas.md` — brms formula syntax: hierarchical, distributional, mixture, nonlinear
   - `prior-choice.md` — weakly informative defaults, prior predictive checks, sensitivity
   - `mcmc-diagnostics.md` — Rhat, ESS bulk/tail, divergences, max treedepth, posterior predictive checks
   - `tidybayes-patterns.md` — `gather_draws` / `spread_draws`, `ggdist` visualization, `linpred_draws` for predictions
3. Update r-stats negative-boundary line to point at r-bayesian; same for r-clinical and r-tidymodels.
4. Routing matrix — 4–6 new entries (positive: brms / MCMC / posterior; negative against r-stats and r-tidymodels).
5. README + CLAUDE.md — bump skill count 18 → 19 in badge, table, architecture diagram, ship line.
6. Session-start hook — detect `.stan` files, `_brms_*.rds` artifacts, and `brms`/`posterior` in `DESCRIPTION` / `Imports`.
7. `eval.md` — 10 binary eval questions + happy/edge/adversarial/boundary prompts.
8. Release notes — 0.3.0 entry.

**Effort:** ~2–3 days for high-quality content with references.

**Risk:** Low on infra (additive skill). Some content judgment needed on prior-choice guidance.

**Release:** Minor bump to 0.3.0 (new skill = minor bump).

### Sequencing

```
Phase 1  →  Phase 2
  hook        Bayesian
  ~0.5 day    ~2–3 days
```

Each phase is independently shippable. Phase 1 is ~half a day; Phase 2 is the biggest content win.

### Deferred (revisit after Phase 3)

- `r-timeseries`, `r-spatial`, `r-causal` skills — comparable value to Bayesian but lower differentiation per unit effort
- `/r-deploy`, `/r-bench`, `/r-renv` commands — pull from real user requests
- Docker / rocker / pkgdown CI patterns — production-readiness; warrants its own brainstorm
- Example gallery / FAQ — seed from user feedback once it arrives
