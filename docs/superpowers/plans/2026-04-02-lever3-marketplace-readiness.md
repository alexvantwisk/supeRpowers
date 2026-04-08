# Lever 3: Marketplace Readiness — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the plugin discoverable on GitHub and in Claude Code marketplaces with minimal effort — README polish, plugin.json metadata, and marketplace submission notes.

**Architecture:** Two files changed (README.md, plugin.json), one file created (marketplace submission notes). No skills, agents, or rules modified.

**Tech Stack:** Markdown, JSON

---

### Task 1: Update plugin.json Metadata

**Files:**
- Modify: `plugin.json`

- [ ] **Step 1: Add repository field and extend keywords**

Replace the full content of `plugin.json` with:

```json
{
  "name": "supeRpowers",
  "version": "0.2.0",
  "description": "Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, and biostatistics.",
  "keywords": [
    "r",
    "rstats",
    "tidyverse",
    "shiny",
    "biostatistics",
    "clinical-trials",
    "tidymodels",
    "targets",
    "ggplot2",
    "package-dev",
    "quarto",
    "renv",
    "mcp",
    "dplyr",
    "data-analysis"
  ],
  "author": "Alexander van Twisk",
  "license": "MIT",
  "repository": "https://github.com/avantwisk/supeRpowers",
  "claude_code": {
    "min_version": "1.0.0",
    "rules": ["rules/r-conventions.md"],
    "skills": ["skills/*/SKILL.md"],
    "agents": ["agents/*.md"],
    "hooks": "hooks/hooks.json"
  }
}
```

**IMPORTANT:** The repository URL (`https://github.com/avantwisk/supeRpowers`) must be confirmed with the user before committing. Ask: "What is the GitHub repository URL for supeRpowers?" and replace the placeholder.

- [ ] **Step 2: Verify JSON is valid**

Run:
```bash
python -c "import json; json.load(open('plugin.json')); print('Valid JSON')"
```
Expected: `Valid JSON`

- [ ] **Step 3: Commit**

```bash
git add plugin.json
git commit -m "chore(plugin): extend keywords and add repository URL"
```

---

### Task 2: Update README.md

The README already exists and is well-structured (90 lines). Updates needed: bump skill count from 15 to 21 (includes workflow commands and skill-auditor), add workflow commands table, add "Works best with" section, polish for marketplace discovery.

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README.md with updated content**

Replace the full content of `README.md` with:

```markdown
# supeRpowers

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-21-purple)
![Agents](https://img.shields.io/badge/agents-5-orange)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)

The deepest R programming plugin for Claude Code. 21 skills, 5 agents, and 5 workflow commands covering tidyverse data analysis, package development, Shiny, statistics, clinical trials, tables, Quarto, machine learning, pipelines, and more.

## Installation

```bash
claude plugin add supeRpowers
```

## How It Works

supeRpowers uses a three-layer architecture:

**Foundation** — `rules/r-conventions.md` enforces tidyverse-first coding: base pipe `|>`, `<-` assignment, snake_case, modern dplyr 1.2.0 functions, and statistical programming style across every R interaction.

**Domain** — 16 knowledge skills and 5 workflow commands cover the full R development spectrum. Knowledge skills activate automatically when your request matches; workflow commands (`/r-cmd-*`) provide step-by-step guided procedures.

**Service** — 5 agents handle code review, statistical consulting, dependency auditing, Shiny architecture review, and R CMD check resolution. Skills dispatch to agents automatically, or invoke them directly.

**Hooks** — A session-start hook detects your R project type (package, Shiny, targets, Quarto, clinical, analysis) and surfaces the most relevant skills and agents.

## Knowledge Skills

| Skill | Domain | Key Packages |
|-------|--------|-------------|
| r-data-analysis | Data wrangling, cleaning, transformation | dplyr, tidyr, readr, stringr, forcats, lubridate |
| r-visualization | Plots, publication-quality figures | ggplot2, plotly, patchwork, viridis |
| r-stats | Statistical modeling, diagnostics, inference | lm, glm, lme4, survival, brms |
| r-clinical | Clinical trials, CDISC, biostatistics | admiral, pwr, gsDesign, pROC, meta |
| r-tables | Publication-quality tables | gt, gtsummary, gtExtras, reactable |
| r-shiny | Web apps, reactivity, modules | shiny, bslib, golem, shinytest2 |
| r-package-dev | Full package lifecycle, CRAN submission | usethis, devtools, roxygen2, pkgdown |
| r-tdd | Test-driven development, testthat 3e | testthat, covr, withr |
| r-debugging | Bug diagnosis, profiling, pitfalls | browser(), rlang, profvis, reprex |
| r-quarto | Documents, presentations, websites | quarto, rmarkdown, tarchetypes |
| r-performance | Profiling, optimization, parallelism | profvis, data.table, Rcpp, furrr, bench |
| r-tidymodels | Machine learning, tuning, evaluation | tidymodels, recipes, tune, yardstick |
| r-targets | Reproducible pipelines, orchestration | targets, tarchetypes, crew |
| r-project-setup | Scaffold new R projects | usethis, renv, golem, quarto |
| r-package-skill-generator | Generate skills from R package repos | (meta-tool) |
| skill-auditor | Audit skill quality against 38-check rubric | (meta-tool) |

## Workflow Commands

| Command | What It Does |
|---------|-------------|
| /r-cmd-analysis | Guided analysis pipeline: import, clean, explore, model, visualize |
| /r-cmd-tdd-cycle | Test-driven development: RED, GREEN, REFACTOR, REVIEW |
| /r-cmd-pkg-release | Package release: test, check, document, version, submit |
| /r-cmd-shiny-app | Shiny app scaffold: structure, modules, reactivity, test |
| /r-cmd-debug | Systematic debugging: reproduce, isolate, diagnose, fix, verify |

## Agents

| Agent | Purpose | Dispatched By |
|-------|---------|--------------|
| r-code-reviewer | Style, correctness, performance, analytical style review | r-debugging, any skill |
| r-statistician | Statistical consulting and model selection | r-stats, r-clinical, r-data-analysis |
| r-pkg-check | R CMD check issue resolution | r-package-dev |
| r-shiny-architect | Shiny app structure and reactivity review | r-shiny |
| r-dependency-manager | renv, dependency auditing, version conflicts | r-package-dev, r-targets |

## Works Best With

- **[btw](https://posit-dev.github.io/btw/)** MCP server — gives skills live access to your R session (data frames, package docs, installed versions). All skills work without it, but are more precise with it.
- **[mcptools](https://posit-dev.github.io/mcptools/)** — R as MCP server/client for deeper integration.

## Quick Start

Just describe what you need — skills activate automatically:

```
"Analyze this CSV file and create visualizations"
"Set up a new R package called tidywidgets"
"Build a predictive model for customer churn using tidymodels"
"Debug why my Shiny app is slow"
"Generate a demographics table for my clinical trial data"
```

Or use workflow commands for guided step-by-step procedures:

```
/r-cmd-tdd-cycle
/r-cmd-pkg-release
/r-cmd-analysis
```

## Requirements

- R >= 4.1.0
- Claude Code >= 1.0.0

## License

MIT — see [LICENSE](LICENSE)
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l README.md
```
Expected: ~110 lines.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): update for 21 skills, workflow commands, and marketplace discovery"
```

---

### Task 3: Create Marketplace Submission Notes

This is a reference doc for the plugin author — not shipped with the plugin. Documents what each marketplace expects so PRs can be submitted later.

**Files:**
- Create: `docs/superpowers/marketplace-submission-notes.md`

- [ ] **Step 1: Write the marketplace notes**

Create `docs/superpowers/marketplace-submission-notes.md` with:

```markdown
# Marketplace Submission Notes

Reference for submitting supeRpowers to Claude Code marketplaces and awesome-lists.

## Target Marketplaces

### 1. anthropics/claude-plugins-official

- **Format:** PR adding plugin entry to their directory
- **URL:** https://github.com/anthropics/claude-plugins-official
- **Requirements:** Valid plugin.json, public GitHub repo
- **Action:** Submit PR after repo is public

### 2. kivilaid/plugin-marketplace

- **Format:** PR adding plugin.json to their collection
- **URL:** https://github.com/kivilaid/plugin-marketplace
- **Requirements:** Valid plugin.json with description, keywords
- **Action:** Submit PR with our plugin.json

### 3. christopherkenny/awesome-rstats-skills

- **Format:** PR adding list entry
- **URL:** https://github.com/christopherkenny/awesome-rstats-skills
- **Entry format:** `- [supeRpowers](https://github.com/<user>/supeRpowers) — 21 R skills for Claude Code: tidyverse, clinical trials, Shiny, package dev, and more`
- **Action:** Submit PR after repo is public

### 4. rohitg00/awesome-claude-code-toolkit

- **Format:** PR adding entry to plugins section
- **URL:** https://github.com/rohitg00/awesome-claude-code-toolkit
- **Entry format:** Plugin entry with name, description, link
- **Action:** Submit PR after repo is public

## Pre-Submission Checklist

- [ ] GitHub repo is public
- [ ] plugin.json has repository field pointing to correct URL
- [ ] README.md is clear and scannable
- [ ] LICENSE file exists
- [ ] No secrets or credentials in the repo
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/marketplace-submission-notes.md
git commit -m "docs: add marketplace submission notes for future PR submissions"
```

---

### Task 4: Final Verification

- [ ] **Step 1: Verify plugin.json is valid**

Run:
```bash
python -c "import json; json.load(open('plugin.json')); print('Valid JSON')"
```
Expected: `Valid JSON`

- [ ] **Step 2: Verify README renders correctly**

Run:
```bash
head -5 README.md
```
Expected: `# supeRpowers` header with badges.

- [ ] **Step 3: Verify skill count matches README claim**

Run:
```bash
ls -1 skills/*/SKILL.md | wc -l
```
Expected: 21 (matching the "21 skills" claim in README).

- [ ] **Step 4: Verify agent count**

Run:
```bash
ls -1 agents/*.md | wc -l
```
Expected: 5 (matching the "5 agents" claim in README).
