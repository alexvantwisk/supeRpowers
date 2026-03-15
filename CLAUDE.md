# supeRpowers Plugin — Development Guide

## What This Is

A Claude Code marketplace plugin providing expert-level R programming assistance. It ships 15 skills, 5 agents, and 1 rule — covering data analysis, visualization, statistics, clinical trials, Shiny, package development, tables, Quarto publishing, performance, machine learning, pipelines, TDD, and debugging.

## Project Structure

```
plugin.json              # Plugin manifest — declares rules, skills, agents, hooks
hooks/                   # Session lifecycle hooks
  hooks.json             # SessionStart hook configuration
  session-start          # R project detection script
  run-hook.cmd           # Cross-platform wrapper
rules/                   # Foundation rules (loaded into every R conversation)
  r-conventions.md       # Base pipe |>, tidyverse-first, style guide
skills/                  # Domain skills (SKILL.md + optional references/)
  r-data-analysis/       r-visualization/       r-tdd/
  r-debugging/           r-package-dev/         r-shiny/
  r-stats/               r-clinical/            r-tables/
  r-quarto/              r-performance/         r-package-skill-generator/
  r-project-setup/       r-tidymodels/          r-targets/
agents/                  # Shared agents (no YAML frontmatter)
  r-code-reviewer.md     r-statistician.md      r-pkg-check.md
  r-shiny-architect.md   r-dependency-manager.md
plans/                   # Implementation plans and design spec (historical)
```

## Content Formats

### Skills (`skills/*/SKILL.md`)

- YAML frontmatter with exactly two fields: `name` and `description`
- `description` starts with "Use when..." and describes triggering conditions only
- Body: max 300 lines (including frontmatter)
- Optional `references/` subdirectory for deep-dive content (lazy-loaded)
- Optional `scripts/` subdirectory for helper scripts

### Agents (`agents/*.md`)

- NO YAML frontmatter
- Format: title, description, Inputs, Output, Procedure sections
- Max 200 lines
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

Run this to check for violations:
```bash
grep -rn '%>%' skills/ agents/ rules/
```

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with the frontmatter format above
2. Add reference files to `skills/<name>/references/` if needed
3. Keep SKILL.md under 300 lines — offload detail to references
4. Include lazy reference pointers: `Read \`references/foo.md\` for...`
5. Include agent dispatch lines if the skill hands off to an agent
6. Include 3-5 example prompts at the end
7. Verify: no `%>%`, line count, frontmatter format

## Adding a New Agent

1. Create `agents/<name>.md` with Inputs/Output/Procedure format
2. No YAML frontmatter
3. Keep under 200 lines
4. Include a severity guide table
5. Include 2-3 examples at the end

## Design Spec

The full design lives at `plans/2026-03-15-superpowers-r-plugin-design.md`. It covers the architecture, skill trigger table, agent I/O contracts, MCP integration mappings, and skill chaining workflows. Read it before making architectural changes.

## Verification Checklist

Before committing any content changes:

- [ ] No `%>%` anywhere in skills/, agents/, rules/
- [ ] SKILL.md files are ≤300 lines with correct frontmatter
- [ ] Agent files are ≤200 lines with no frontmatter
- [ ] Rule files are ≤150 lines with no frontmatter
- [ ] All R code uses `<-`, `|>`, snake_case, double quotes
- [ ] plugin.json glob patterns still match new files

## Hooks

The plugin includes a session-start hook (`hooks/session-start`) that fires on startup, resume, clear, and compact. It detects the R project type in the current directory and injects context about relevant skills and agents. Configuration is in `hooks/hooks.json`.
