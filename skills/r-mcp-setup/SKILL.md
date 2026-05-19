---
name: r-mcp-setup
description: >
  Use when the user wants to set up MCP tools for R — connecting Claude Code
  to a persistent agent-owned R session via mcp-repl, or to a live IDE R
  session via mcptools + btw. Covers installing mcp-repl (prebuilt binary or
  `cargo install`), registering R-based MCP servers via `claude mcp add`,
  sandbox flags, choosing btw tool groups (docs, pkg, env, run, search,
  session), `mcptools::mcp_session()` wiring, and troubleshooting an MCP
  setup that isn't appearing in Claude Code. Triggers: mcp-repl, persistent
  R session, REPL session for Claude, repl_reset, mcptools, btw, MCP server,
  live R session, claude mcp add, btw_tool_*, "Claude can't see my R
  session". Do NOT use for: writing R code that uses already-configured MCP
  tools (use the relevant domain skill — r-data-analysis, r-stats, etc.);
  generic Claude Code MCP setup unrelated to R; building new MCP servers
  from scratch.
---

# R MCP Setup

Two supported paths for connecting Claude Code to R as native MCP tools
instead of one-shot Bash `Rscript -e` calls:

- **mcp-repl** — Claude owns a long-lived R subprocess; state persists
  across tool calls. Headless, no IDE required.
- **btw + mcptools** — Claude connects to *your* running R session in
  RStudio / Positron; inspects the same objects you can see.

All MCP features are **optional** — every skill works fully without them.
Both paths can be registered at the same time; tool names don't collide.

**Lazy references:**
- Read `references/mcp-repl-setup.md` for the full mcp-repl walkthrough
  (install options, sandbox tradeoff, `repl_reset` semantics, comparison
  table)
- Read `references/mcp-tool-mappings.md` for the tool → skill mapping and
  Bash fallback commands
- Read `references/mcp-troubleshooting.md` for common setup issues
- Read `references/ide-awareness-helpers.md` for `cc_plot()`, `cc_env()`,
  and `cc_view()` (closes the Positron Assistant visual-awareness gap)

---

## Two Paths — Which One?

| Path | Process owner | Best for | Survives IDE restart | Sandbox |
|------|---------------|----------|----------------------|---------|
| **mcp-repl** | Claude Code | Headless agent work, autonomous analysis | N/A (no IDE) | Built-in (`--sandbox`) |
| **btw + mcptools** | You (RStudio/Positron) | Pairing inside an IDE; inspecting your env pane objects | Requires re-running `mcptools::mcp_session()` | None |

Lead with mcp-repl when the work is "let Claude run R for me." Reach for
btw + mcptools when you want Claude to see what *you* are doing in your
own console.

---

## Path A — mcp-repl (default for agent work)

Quick-start (full detail in `references/mcp-repl-setup.md`):

1. **Install the binary.** Prebuilt for macOS arm64 / Linux x86_64 /
   Windows x86_64 from
   [github.com/posit-dev/mcp-repl/releases](https://github.com/posit-dev/mcp-repl/releases).
   Or build from source: `cargo install --git https://github.com/posit-dev/mcp-repl --locked`.

2. **Verify:** `mcp-repl --help` should resolve.

3. **Register with Claude Code** (project-scoped, sandbox on):

   ```bash
   claude mcp add -s "project" mcp-repl -- mcp-repl --sandbox
   ```

4. **Verify connection:** `claude mcp list` shows `mcp-repl` as
   `connected`.

5. **Use it.** Two tools become available:
   - `repl(code)` — execute R; variables, packages, models persist across calls
   - `repl_reset()` — drop the subprocess and start fresh

**Sandbox note:** `--sandbox` blocks network and restricts FS writes.
Install packages from your normal R session (RStudio / terminal); the
agent only consumes what's already installed. For one-off agent-driven
installs, re-register without `--sandbox` for that session.

**Large outputs:** add `--oversized-output` to the registration line if
Claude needs to see full `summary()` / `head(df, 100)` output.

---

## Path B — btw + mcptools (IDE integration)

For users working in RStudio or Positron who want Claude to see live
session state, plots, and tabular previews from the same console they're
typing in.

### What mcptools and btw Provide

| Package | Purpose |
|---------|---------|
| **mcptools** | Makes R act as an MCP server; bridges Claude Code into your live R console |
| **btw** | Provides six MCP tool groups: docs, pkg, env, run, search, session |

| Group | What Claude Code Gets |
|-------|-----------------------|
| **docs** | Help pages, vignettes, NEWS for installed packages |
| **pkg** | Structured test/check/document/coverage results |
| **env** | Inspect data frames and environments in a live R session |
| **run** | Execute R code in the user's session |
| **search** | CRAN package discovery and metadata |
| **session** | Installed package checks, platform info |

### Setup steps

Use TaskCreate when running the full setup — one task per step. Mark each
`in_progress` when starting, `completed` when its gate passes.

**B.1 — Detect current state.** Run the shared detection script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/detect-mcp.sh"
```

Returns JSON with `btw_installed`, `mcptools_installed`, `mcp_registered`,
`mcp_repl_installed`, `mcp_repl_registered`, and `tool_groups`.

Alternatively check manually:

```r
requireNamespace("btw", quietly = TRUE)
requireNamespace("mcptools", quietly = TRUE)
```

```bash
claude mcp list
```

**B.2 — Install packages.** If either is missing:

```r
install.packages(c("mcptools", "btw"))
```

For renv projects:

```r
renv::install("mcptools")
renv::install("btw")
renv::snapshot()
```

**B.3 — Register the MCP server** (project-scoped):

```bash
claude mcp add -s "project" r-btw -- Rscript -e "btw::btw_mcp_server(tools = btw::btw_tools(c('docs', 'pkg', 'env', 'search', 'session', 'run')))"
```

Excludes files/git/github/ide/web (duplicate Claude Code built-ins).
Server starts automatically when Claude Code opens this project.

**Windows:** may need the full path to `Rscript.exe` — see
`references/mcp-troubleshooting.md`.

**B.4 — Connect your live R session.** In Positron / RStudio:

```r
mcptools::mcp_session()
```

Without this, `env` tools see only the MCP server's own empty R process.

Add to `.Rprofile` for auto-start:

```r
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
  try(source(".claude/scripts/cc-helpers.R"), silent = TRUE)
}
```

**B.5 — Verify.** `claude mcp list` should show `r-btw` as `connected`.

**B.6 — (Optional) close the IDE-awareness gap.** `cc_plot()`, `cc_env()`,
and `cc_view()` write artifacts to `.claude/scratch/` so Claude can read
your plots, workspace summary, and tabular previews. Install:

1. Copy `${CLAUDE_PLUGIN_ROOT}/skills/r-mcp-setup/scripts/cc-helpers.R`
   to `.claude/scripts/cc-helpers.R` in your project
2. Source from `.Rprofile` (see B.4)
3. Add `.claude/scratch/` to `.gitignore` (and `.Rbuildignore` for
   packages)

Detail in `references/ide-awareness-helpers.md`.

---

## Using Both Paths Together

mcp-repl and btw + mcptools can be registered simultaneously. Tool names
don't collide: mcp-repl exposes `repl` and `repl_reset`; btw exposes
`btw_tool_*`. Common pattern: use `repl` for agent-owned stateful
execution, and `btw_tool_env_describe_data_frame` to introspect data
frames that you yourself loaded in your IDE.

---

## How Skills Use MCP Tools

The session-start hook detects MCP availability and injects context.
Skills check for `"MCP: available"` in their context to choose execution
path:

```
MCP available → use mcp-repl `repl` or btw tools (structured result)
MCP not available → fall back to Bash `Rscript -e` (parse text output)
```

`repl` is the persistent-execution path; `btw_tool_run_r` is the
single-call path against the user's IDE session. See
`references/mcp-tool-mappings.md` for the full mapping.

---

## Removing MCP Registration

```bash
claude mcp remove mcp-repl       # drops the mcp-repl registration
claude mcp remove r-btw          # drops the btw/mcptools registration
```

Both leave the underlying binaries / packages installed.

---

## Examples

- "Set up mcp-repl for persistent R sessions in Claude Code"
- "How do I install the Posit mcp-repl binary"
- "Connect Claude Code to my live R session in Positron"
- "Which btw tools should I register for package development?"
- "My MCP server isn't connecting — help me troubleshoot"
- "What's the difference between mcp-repl, mcptools, and btw?"
