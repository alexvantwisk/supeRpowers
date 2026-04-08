# Lever 1: MCP-Aware Skills

## Problem

Claude has btw/mcptools MCP tools available in most R sessions but skills never instruct it to use them. Claude writes R code based on training data — guessing at column names, data types, package versions, and function signatures. This produces code that looks right but fails on contact with reality.

## Goal

Make skills proactively leverage the R session (when available) to inspect data, verify packages, read docs, and confirm output — without breaking anything for users who don't have MCP configured.

## Design Principle

**Graceful degradation.** Every MCP dispatch line is conditional: "If an R session is available via btw..." Skills remain fully functional without MCP, just less precise.

## Three Integration Points

### 1. Session-Start Hook Enhancement

**File:** `hooks/session-start`

Extend the existing project-type detection to also capture runtime context:

- R version and platform via `btw_tool_sessioninfo_platform`
- Key package versions (dplyr, ggplot2, tidyr, etc.) via `btw_tool_sessioninfo_package`
- Project type signals already detected (DESCRIPTION, app.R, _targets.R, _quarto.yml)

This context is injected once at session start. Every skill knows what's installed without asking.

**Output format** (appended to existing hook output):

```
R session detected:
  R version: 4.4.1
  Platform: x86_64-w64-mingw32
  Key packages: dplyr 1.2.0, ggplot2 3.5.1, tidyr 1.3.1, ...
```

**Fallback:** If no R session is running, skip this section. The hook already handles this.

### 2. MCP Dispatch Lines in Skills

Same pattern as existing agent dispatch lines. Each skill gets 3-5 conditional MCP instructions.

**Skills to update and their MCP dispatch lines:**

| Skill | MCP Action | Tool | When |
|-------|-----------|------|------|
| r-data-analysis | Inspect data frames before joins/transforms | `btw_tool_env_describe_data_frame` | Before writing non-trivial data manipulation |
| r-data-analysis | Check column names and types | `btw_tool_env_describe_data_frame` | Before referencing specific columns |
| r-stats | Verify target package is installed | `btw_tool_sessioninfo_is_package_installed` | Before recommending a model from a specific package |
| r-stats | Read model function docs | `btw_tool_docs_help_page` | When choosing between model families |
| r-visualization | Describe data to choose geoms | `btw_tool_env_describe_data_frame` | Before writing ggplot code |
| r-package-dev | Read existing roxygen docs | `btw_tool_docs_help_page` | Before writing or updating documentation |
| r-package-dev | Check package help topics | `btw_tool_docs_package_help_topics` | When working on exports or NAMESPACE |
| r-shiny | Describe reactive data sources | `btw_tool_env_describe_data_frame` | Before building UI for data display |
| r-clinical | Verify CDISC package availability | `btw_tool_sessioninfo_is_package_installed` | Before recommending admiral/pharmaverse functions |
| r-tidymodels | Check installed engines | `btw_tool_sessioninfo_is_package_installed` | Before specifying parsnip model engines |
| r-tables | Describe data before table design | `btw_tool_env_describe_data_frame` | Before writing gt/gtsummary code |
| r-targets | Read target function docs | `btw_tool_docs_help_page` | When uncertain about targets API |

**Format in SKILL.md files** (added to existing Orchestration / Agent Dispatch section):

```markdown
## MCP Integration (when R session available)

Before writing data transformations, inspect the actual data:
- `btw_tool_env_describe_data_frame` on input data frames — verify column names, types, dimensions
- `btw_tool_docs_help_page` for unfamiliar functions — read actual installed docs, not training data
```

### 3. Verify-After-Write Pattern

**File:** `rules/r-conventions.md` (new section)

A convention that instructs Claude to verify non-trivial R code after writing it:

```markdown
## Verify After Write

For non-trivial R code (data transformations, model fits, table generation), verify output when an R session is available:

1. Run the code via btw
2. Check for errors and warnings
3. Verify output dimensions and structure match expectations
4. Fix issues before presenting to the user

Skip verification for: simple one-liners, package scaffolding, configuration files, code that requires data not in the session.
```

**File:** `rules/r-conventions.md` (new section)

```markdown
## Environment-Aware Coding

When an R session is available via btw/mcptools:

- **Before writing code:** Inspect actual data frames, check installed packages, read function docs
- **When uncertain about a function:** Read the help page rather than guessing from training data
- **After writing non-trivial code:** Run it and verify the output
- **When recommending packages:** Check if they're installed first

These are enhancement behaviors. All skills and conventions work without MCP — MCP makes them more precise.
```

## Files Changed

| File | Change | Lines Added |
|------|--------|-------------|
| `hooks/session-start` | Add R version + package version detection | ~15 |
| `rules/r-conventions.md` | Add "Environment-Aware Coding" section | ~15 |
| `rules/r-conventions.md` | Add "Verify After Write" section | ~10 |
| `skills/r-data-analysis/SKILL.md` | Add MCP dispatch lines | ~5 |
| `skills/r-stats/SKILL.md` | Add MCP dispatch lines | ~5 |
| `skills/r-visualization/SKILL.md` | Add MCP dispatch lines | ~4 |
| `skills/r-package-dev/SKILL.md` | Add MCP dispatch lines | ~5 |
| `skills/r-shiny/SKILL.md` | Add MCP dispatch lines | ~4 |
| `skills/r-clinical/SKILL.md` | Add MCP dispatch lines | ~4 |
| `skills/r-tidymodels/SKILL.md` | Add MCP dispatch lines | ~4 |
| `skills/r-tables/SKILL.md` | Add MCP dispatch lines | ~4 |
| `skills/r-targets/SKILL.md` | Add MCP dispatch lines | ~4 |

## Files NOT Changed

- No new skills or agents created
- btw/mcptools NOT declared as plugin dependencies (user-configured)
- Existing skill content preserved — MCP lines are additive

## Verification

- [ ] All MCP dispatch lines use conditional language ("when R session available")
- [ ] Skills still make sense when read without MCP context
- [ ] Session-start hook gracefully handles missing R session
- [ ] No SKILL.md exceeds 300-line limit after additions
- [ ] Verify-after-write section has clear skip criteria
