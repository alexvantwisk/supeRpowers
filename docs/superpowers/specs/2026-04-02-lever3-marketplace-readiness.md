# Lever 3: Marketplace Readiness

## Problem

The plugin isn't listed anywhere. With ~10,000 Claude Code repos indexed across awesome-lists and 6+ community marketplaces, organic discovery requires minimum metadata and a README.

## Goal

Get the plugin discoverable with minimal effort. No community building, no tutorials — just enough for someone to find it, understand it, and install it.

## Three Deliverables

### 1. README.md

A sharp, scannable README (~60-80 lines) answering three questions:

**What is this?**
One paragraph: "The deepest R programming plugin for Claude Code. 21 skills, 5 agents, 5 workflow commands covering tidyverse, package development, Shiny, statistics, clinical trials, and more."

**What do I get?**
Three tables:

Skills table (knowledge skills):
| Skill | Domain |
|-------|--------|
| r-data-analysis | dplyr/tidyr/readr data manipulation |
| r-visualization | ggplot2, patchwork, publication figures |
| r-stats | Linear models, GLMs, mixed, survival, Bayesian |
| ... | ... |

Workflow commands table:
| Command | What it does |
|---------|-------------|
| /r-cmd-analysis | Guided analysis pipeline |
| /r-cmd-tdd-cycle | Test-driven development cycle |
| ... | ... |

Agents table:
| Agent | Role |
|-------|------|
| r-code-reviewer | Style + correctness review |
| r-statistician | Statistical methodology consulting |
| ... | ... |

**How do I install it?**
```
/plugin install <github-url>
```

Plus a "Works best with" note: btw MCP server for environment-aware coding.

**Does NOT include:** tutorials, lengthy examples, prose, badges, screenshots, contributing guide.

### 2. plugin.json Polish

Current plugin.json is already well-structured. Check and fill:

- `description` — already good, verify it's under marketplace character limits
- `keywords` — already present, add: `"ggplot2"`, `"package-dev"`, `"quarto"`, `"renv"`, `"mcp"` if not already there
- `repository` — add GitHub URL field
- `license` — already `"MIT"`

Minimal changes expected. This is a verification pass, not a rewrite.

### 3. Marketplace Submission Prep

Research the submission format for the most impactful marketplaces:

| Marketplace | Format | Action |
|------------|--------|--------|
| anthropics/claude-plugins-official | PR with plugin entry | Prepare PR-ready entry |
| kivilaid/plugin-marketplace | PR with plugin.json | Prepare PR-ready entry |
| christopherkenny/awesome-rstats-skills | PR with list entry | Prepare PR-ready entry |
| rohitg00/awesome-claude-code-toolkit | PR with list entry | Prepare PR-ready entry |

Deliverable: notes on what each marketplace expects, so PRs can be submitted after the plugin is public. No PRs created as part of this spec — just preparation.

## Files Changed

| File | Change |
|------|--------|
| `README.md` | New file (~60-80 lines) |
| `plugin.json` | Add `repository` field, verify/extend `keywords` |

## Files NOT Changed

- No skills, agents, rules, or hooks modified
- No new directories created

## Verification

- [ ] README.md is scannable in under 30 seconds
- [ ] Install command is copy-pasteable
- [ ] plugin.json is valid JSON after edits
- [ ] Keywords cover all major domains the plugin serves
- [ ] No marketing fluff — factual claims only
