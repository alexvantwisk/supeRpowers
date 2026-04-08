# MCP Integration Design — mcptools/btw for supeRpowers

**Date:** 2026-03-15
**Status:** Draft
**Scope:** Add mcptools/btw MCP server integration to the supeRpowers plugin

## Problem

Claude Code interacts with R entirely through `Rscript` via Bash. This means:

- Text parsing of console output instead of structured results
- No access to live R session objects (data frames, environments)
- No structured package documentation lookups
- Fragile error handling (exit codes + stderr parsing)

The [mcptools](https://posit-dev.github.io/mcptools/) and [btw](https://posit-dev.github.io/btw/) R packages solve this by exposing R capabilities as native MCP tools that Claude Code can call directly.

## Design Principles

1. **Graceful degradation** — All skills work fully without MCP. MCP enhances but is never required.
2. **Hybrid setup** — Detect current state, explain what will change, ask permission before modifying config.
3. **Lazy loading** — MCP knowledge lives in reference files, loaded only when needed.
4. **Centralized knowledge** — One reference file maps MCP tools to skills. Single update point for API changes.
5. **Consistent with existing architecture** — Follows the three-layer design (foundation, domain, service).

## Prioritized btw Tool Groups

Six of btw's eleven tool groups provide unique R capabilities that Claude Code doesn't have natively. The remaining five (files, git, github, ide, web) duplicate built-in Claude Code tools and are excluded.

| Group | Tools | What It Gives Claude Code |
|-------|-------|--------------------------|
| **docs** | `help_page`, `package_help_topics`, `vignette`, `available_vignettes`, `package_news` | Live R package documentation from installed packages |
| **pkg** | `pkg_test`, `pkg_check`, `pkg_document`, `pkg_coverage` | Structured package dev results (pass/fail, coverage %) |
| **env** | `describe_data_frame`, `describe_environment` | Inspect live R session objects (no equivalent today) |
| **run** | `run_r` | Execute R code in the user's session (experimental) |
| **search** | `search_packages`, `search_package_info` | CRAN package discovery and metadata |
| **session** | `check_package_installed`, `package_info`, `platform_info` | R environment introspection |

## Component 1: `r-mcp-setup` Skill

### Trigger

"Use when the user wants to set up MCP tools for R, connect Claude Code to a live R session, register R-based MCP servers, or when another skill needs MCP tool guidance."

### Workflow

1. **Detection** — Check whether mcptools and btw are installed (`Rscript -e 'requireNamespace("btw")'`). Check whether MCP servers are registered (`claude mcp list` or config files).
2. **Installation guidance** — If packages are missing, guide user through `install.packages(c("mcptools", "btw"))`.
3. **Registration (hybrid)** — Explain what will be registered and why. Ask permission. Then run:
   ```
   claude mcp add -s "project" r-btw -- Rscript -e "btw::btw_mcp_server(tools = btw::btw_tools(c('docs', 'pkg', 'env', 'search', 'session', 'run')))"
   ```
   Scoped to "project" so it doesn't affect other projects.
4. **Session connection** — Guide user to run `mcptools::mcp_session()` in their Positron R console (or add it to `.Rprofile`). This makes the live R session discoverable by the MCP server, enabling `env` tools to inspect objects in that session. Without this step, `env` tools see only the MCP server's own (empty) R process. The `run` + `env` combination is where the real value lies: run code to create/load objects, then inspect them.
5. **Verification** — Confirm MCP server is responding by checking tool availability.

### Reference Files

- `references/mcp-tool-mappings.md` — Maps btw tool groups to skills, with fallback commands
- `references/mcp-troubleshooting.md` — Common issues (Windows paths, renv conflicts, Positron session discovery)

### Scripts

- `hooks/detect-mcp.sh` — Shared helper for MCP detection, used by both the session-start hook and the skill. Lives in `hooks/` (infrastructure layer) since it serves cross-layer needs. Returns JSON to stdout: `{"mcp_registered": bool, "btw_installed": bool, "tool_groups": [...]}`. Exit code 0 always; consumers parse stdout.

## Component 2: MCP Tool Mappings Reference

Central reference file at `skills/r-mcp-setup/references/mcp-tool-mappings.md`.

### Mapping Table

| btw Group | Skills That Benefit | Replaces |
|-----------|-------------------|----------|
| **docs** | All skills | `Rscript -e '?pkg::fun'` + parsing stdout |
| **pkg** | r-tdd, r-package-dev, r-debugging | `Rscript -e 'devtools::test(...)'` |
| **env** | r-data-analysis, r-debugging, r-stats, r-clinical, r-performance, r-targets | No equivalent (static file reads only) |
| **run** | r-data-analysis, r-debugging, r-stats, r-performance, r-tidymodels, r-targets | `Rscript -e '<code>'` |
| **search** | r-package-dev, r-project-setup, r-dependency-manager agent | Web search / guessing |
| **session** | r-project-setup, r-dependency-manager agent | `Rscript -e 'sessionInfo()'` |

### Detection Pattern

Skills follow this logic:

```
If additionalContext contains "MCP: available"
  → Use btw MCP tool (structured result, proper error propagation)
Else
  → Fall back to Bash Rscript -e (parse text output, existing behavior)
```

### Per-Group Fallback Commands

Each tool group entry includes the exact Bash `Rscript -e` fallback command, so skills have a concrete alternative when MCP is unavailable.

## Component 3: Skill-Level Patches

Ten of 15 skills get a 2-3 line addition pointing to the MCP reference:

```markdown
## MCP-Enhanced Workflow (Optional)

When btw MCP tools are available, prefer them over Bash Rscript calls.
Read `skills/r-mcp-setup/references/mcp-tool-mappings.md` for tool selection and fallback logic.
```

### Patched Skills (10)

| Skill | Primary MCP Benefit |
|-------|-------------------|
| r-tdd | `pkg_test`, `pkg_coverage` for structured test results |
| r-package-dev | `pkg_check`, `pkg_document`, `search_packages` |
| r-debugging | `env_describe_data_frame`, `env_describe_environment`, `run_r` |
| r-data-analysis | `env_describe_data_frame`, `run_r` for interactive exploration |
| r-stats | `docs_help_page` for model docs, `run_r` for fitting |
| r-clinical | btw tools alongside existing Clinical Trials + bioRxiv MCP |
| r-project-setup | `session_platform_info`, `search_packages` |
| r-performance | `run_r` for benchmarking, `env_describe_data_frame` |
| r-tidymodels | `docs_help_page`, `run_r` for model fitting |
| r-targets | `run_r` for pipeline execution, `env_describe_environment` |

### Unpatched Skills (5)

r-visualization, r-shiny, r-tables, r-quarto, r-package-skill-generator — primarily about generating code, not running or inspecting R. While r-visualization and r-tables could theoretically benefit from `run_r` (render plots/tables in a live session), this is a niche workflow that doesn't justify the added complexity. These skills can be patched later if demand emerges.

## Component 4: Session-Start Hook Enhancement

### Changes to `hooks/session-start`

Add an MCP detection block (~20-30 lines) alongside existing project type detection. **This block only runs if R was already detected** by the existing project type check — no additional R process launch on non-R projects.

1. **Call shared detection script** — `hooks/detect-mcp.sh` checks MCP registration (config files) and btw installation (single `Rscript` call, reusing the R process from the existing hook checks where possible).
2. **Cache result** — Write detection result to a temp file (`/tmp/superpowers-mcp-status-$USER.json`) with a 5-minute TTL. Subsequent hook invocations (resume, clear, compact) reuse the cached result if fresh.
3. **Inject context** — Append to the `additionalContext` string (which skills receive as plain text):
   - `"MCP: available | groups: docs, pkg, env, run, search, session | session: active"` (when fully configured)
   - `"MCP: not configured. Use the r-mcp-setup skill to enable enhanced R integration."` (when not set up)
   - Skills check for the substring `"MCP: available"` in their context to decide workflow path.

### Shared Detection Script

`hooks/detect-mcp.sh` is used by both the hook and the skill. It outputs JSON to stdout and always exits 0. See Component 1 Scripts section for the interface contract.

### What Doesn't Change

Existing project type detection, skill mapping, and agent mapping remain exactly as-is. The MCP block is purely additive.

## Component 5: Agent Updates

Two of 5 agents get a short MCP-enhanced note in their Procedure section:

### r-dependency-manager

- Can use `session_check_package_installed`, `session_package_info`, `search_package_info`
- Pointer to `mcp-tool-mappings.md` reference

### r-pkg-check

- Can use `pkg_check` for structured results, `pkg_document` to fix docs, `pkg_coverage`
- Pointer to `mcp-tool-mappings.md` reference

### Untouched Agents (3)

r-code-reviewer, r-statistician, r-shiny-architect — static analysis or advisory, don't run R.

## File Inventory

### New Files (4)

| File | Type | Lines (est.) |
|------|------|-------------|
| `skills/r-mcp-setup/SKILL.md` | Skill | ~200 |
| `skills/r-mcp-setup/references/mcp-tool-mappings.md` | Reference | ~150 |
| `skills/r-mcp-setup/references/mcp-troubleshooting.md` | Reference | ~100 |
| `hooks/detect-mcp.sh` | Script | ~50 |

### Modified Files (14)

| File | Change Size |
|------|------------|
| `hooks/session-start` | +20-30 lines (MCP detection block) |
| `plugin.json` | Version bump 0.2.0 → 0.3.0 |
| 10 skill SKILL.md files | +3 lines each |
| `agents/r-dependency-manager.md` | +5 lines |
| `agents/r-pkg-check.md` | +5 lines |

## Version

Plugin version: `0.2.0` → `0.3.0` (new feature addition).

## Sources

- [mcptools CRAN](https://cran.r-project.org/web/packages/mcptools/index.html)
- [mcptools server vignette](https://posit-dev.github.io/mcptools/articles/server.html)
- [btw package reference](https://posit-dev.github.io/btw/reference/)
- [btw_tools docs](https://posit-dev.github.io/btw/reference/btw_tools.html)
- [Tidyverse blog — R and MCP](https://tidyverse.org/blog/2025/07/mcptools-0-1-0/)
- [Simon Couch — Claude Code with R](https://www.simonpcouch.com/blog/2025-07-17-claude-code-2/)
