---
name: r-mcp-setup
description: >
  Use when the user wants to set up MCP tools for R, connect Claude Code to a
  live R session, register R-based MCP servers, or when another skill needs
  MCP tool guidance.
---

# R MCP Setup

Set up mcptools and btw MCP servers so Claude Code can access R documentation,
run R code, inspect live session objects, and use structured package dev tools
— all as native MCP tools instead of Bash `Rscript -e` calls.

All MCP features are **optional** — every skill works fully without them.
MCP enhances but is never required.

**Lazy references:**
- Read `references/mcp-tool-mappings.md` for btw tool group → skill mapping
  and Bash fallback commands
- Read `references/mcp-troubleshooting.md` for common setup issues

---

## What mcptools and btw Provide

| Package | Purpose |
|---------|---------|
| **mcptools** | Makes R act as an MCP server; connects live R sessions to Claude Code |
| **btw** | Provides default MCP tool groups: docs, pkg, env, run, search, session |

Six btw tool groups give Claude Code unique R capabilities:

| Group | What Claude Code Gets |
|-------|-----------------------|
| **docs** | Help pages, vignettes, NEWS for installed packages |
| **pkg** | Structured test/check/document/coverage results |
| **env** | Inspect data frames and environments in a live R session |
| **run** | Execute R code in the user's session |
| **search** | CRAN package discovery and metadata |
| **session** | Installed package checks, platform info |

---

## Setup Workflow

Follow these 5 steps in order. Skip any step that's already satisfied.

### Step 1: Detect Current State

Run the shared detection script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/detect-mcp.sh"
```

This returns JSON:
```json
{"mcp_registered": false, "btw_installed": false, "mcptools_installed": false, "tool_groups": []}
```

Alternatively, check manually:

```r
requireNamespace("btw", quietly = TRUE)
requireNamespace("mcptools", quietly = TRUE)
```

And check MCP registration:
```bash
claude mcp list
```

### Step 2: Install Packages

If either package is missing:

```r
install.packages(c("mcptools", "btw"))
```

For renv projects, install into the project library:

```r
renv::install("mcptools")
renv::install("btw")
renv::snapshot()
```

### Step 3: Register MCP Server (Hybrid)

**Before running:** Explain to the user what this does and ask for permission.

This registers btw as an MCP server scoped to the current project:

```bash
claude mcp add -s "project" r-btw -- Rscript -e "btw::btw_mcp_server(tools = btw::btw_tools(c('docs', 'pkg', 'env', 'search', 'session', 'run')))"
```

**Key points to communicate:**
- Scoped to `"project"` — does not affect other projects
- Registers 6 tool groups (docs, pkg, env, search, session, run)
- Excludes files/git/github/ide/web (duplicate Claude Code built-ins)
- Server starts automatically when Claude Code opens this project

**Windows:** May need the full path to Rscript.exe. See
`references/mcp-troubleshooting.md` for details.

### Step 4: Connect Live R Session

For `env` tools to inspect objects in the user's running R session (not just
the MCP server's own empty process), the user must run in their Positron or
RStudio console:

```r
mcptools::mcp_session()
```

**Without this:** `env` tools see only the MCP server's own (empty) R process.

**With this:** Claude Code can inspect data frames, environments, and objects
in the user's live session.

**Tip:** Add to `.Rprofile` for auto-start:
```r
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
  try(source(".claude/scripts/cc-helpers.R"), silent = TRUE)
}
```

The `run` + `env` combination is the real value: use `run_r` to execute code,
then `describe_data_frame` to inspect the result.

### Step 5: Verify

After registration, verify the MCP server is responding:

```bash
claude mcp list
```

The output should show `r-btw` with status `connected`. If it shows
`disconnected` or doesn't appear, see `references/mcp-troubleshooting.md`.

### Step 6: Close the IDE-Awareness Gap (Optional)

`mcp_session()` lets Claude inspect live R state, but it still can't see your
Plots pane, Environment pane, or Data Viewer. Three helper functions bridge
that gap by writing artifacts to a scratch directory Claude can read:

| Helper       | Purpose                                                            |
|--------------|--------------------------------------------------------------------|
| `cc_plot()`  | Save the last ggplot to `.claude/scratch/plots/` so Claude can view it |
| `cc_env()`   | Print a workspace summary (name / class / dim / memory)            |
| `cc_view(x)` | Write `head(x)` to `.claude/scratch/<name>.csv` for clean tabular preview |

**Install:**

1. Copy `${CLAUDE_PLUGIN_ROOT}/skills/r-mcp-setup/scripts/cc-helpers.R`
   to `.claude/scripts/cc-helpers.R` in the user's project
2. Source from `.Rprofile` (see Step 4)
3. Add `.claude/scratch/` to `.gitignore` and (for packages) `.Rbuildignore`

Read `references/ide-awareness-helpers.md` for rationale, function signatures,
and usage discipline.

**Honest framing:** these helpers close most of the gap with Positron
Assistant's ambient awareness. The residual difference is that Positron
Assistant doesn't need to be asked — Claude Code does. The discipline is
calling `cc_env()` at the start of a debugging task and `cc_plot()` after
each interesting figure. That habit reproduces ~90% of the "Positron Assistant
feels smarter" effect.

---

## How Skills Use MCP Tools

The session-start hook detects MCP availability and injects context. Skills
check for the substring `"MCP: available"` in their context to decide:

```
MCP available → use btw tool (structured result, proper errors)
MCP not available → fall back to Bash Rscript -e (parse text output)
```

See `references/mcp-tool-mappings.md` for the complete mapping of btw tools
to skills and their Bash fallback commands.

---

## Removing MCP Registration

To unregister the MCP server:

```bash
claude mcp remove r-btw
```

This removes the project-scoped registration. The btw/mcptools packages
remain installed.

---

## Examples

- "Set up MCP tools for my R project"
- "Connect Claude Code to my live R session in Positron"
- "Which btw tools should I register for package development?"
- "My MCP server isn't connecting — help me troubleshoot"
- "What's the difference between mcptools and btw?"
