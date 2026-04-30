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
