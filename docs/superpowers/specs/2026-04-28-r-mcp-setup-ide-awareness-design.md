# r-mcp-setup: IDE-Awareness Extension

**Date:** 2026-04-28
**Status:** Draft for review
**Skill:** `skills/r-mcp-setup/`

## Problem

When working in Positron, Claude Code lacks several forms of awareness that
Positron Assistant has natively: the Plots pane, the Environment pane, the
Data Viewer, and ambient knowledge of what the user just ran. The
`r-mcp-setup` skill already covers `mcptools::mcp_session()`, which bridges
Claude into a running R session for stateful inspection — that closes the
runtime-state gap. The remaining gap is visual and tabular: Claude can read
files but can't see the IDE's panes.

PNG and CSV artifacts on disk are something Claude *can* read. A small set of
helper functions that route plots, environment summaries, and tabular previews
into a known scratch directory closes most of the gap with negligible
machinery.

## Goal

Extend `r-mcp-setup` with a documented helper-function workflow that lets
users surface plots, environment state, and tabular previews to Claude Code as
on-disk artifacts. Ship the helpers as a real R script the user can source
from a project `.Rprofile`. Add one diagnostic note to troubleshooting for the
case where `mcp_session()` routing isn't working.

## Non-Goals

The following were considered and explicitly deferred until real friction
emerges from using the basic helpers:

- **Auto-capture wrappers** around `btw_tool_run_r()` that snapshot stdout,
  warnings, and plots without the user calling helpers explicitly
- **Session-side hooks** (`addTaskCallback()`, `setHook("plot.new", ...)`)
  for ambient capture of every console statement
- **STATUS.md surface** consolidating env, last plot, last output into one
  read
- **`/cc-status` slash command** wrapping the above as a workflow command
- **`cc_view_sdtm()` SDTM-aware variant** (better placed in `r-clinical` if
  added later)

The honest framing: the basic helpers close ~90% of the perceived gap. The
residual is discipline — Claude needs to be told to look, while Positron
Assistant does not. Designing speculative auto-capture machinery before
encountering concrete friction would be premature and would add session
overhead, staleness risk, and documentation burden.

## Architecture

Three deliverables in the existing `r-mcp-setup` skill:

```
skills/r-mcp-setup/
  SKILL.md                              MODIFY: extend Step 4 tip; add Step 6
  references/
    mcp-tool-mappings.md                (unchanged)
    mcp-troubleshooting.md              MODIFY: add cc_env() empty workspace section
    ide-awareness-helpers.md            NEW: full rationale + usage docs
  scripts/
    cc-helpers.R                        NEW: shippable helper file
```

No `plugin.json` changes are needed. The existing `skills/*/SKILL.md` glob
already loads the skill; `scripts/cc-helpers.R` is a static asset the skill
references by path (`${CLAUDE_PLUGIN_ROOT}/skills/r-mcp-setup/scripts/cc-helpers.R`),
not a separately registered file.

## Component Specifications

### `scripts/cc-helpers.R`

Three exported functions plus one private helper. Conforms to project R
conventions: `<-`, double quotes, `snake_case`, tidyverse-first.

```r
# cc-helpers.R — IDE-awareness helpers for Claude Code
# Source from .Rprofile to make these available in interactive R sessions.

`%||%` <- function(a, b) if (is.null(a)) b else a

cc_plot <- function(name = NULL, width = 8, height = 5, dpi = 120) {
  dir <- ".claude/scratch/plots"
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  name <- name %||% format(Sys.time(), "%Y%m%d-%H%M%S")
  path <- file.path(dir, paste0(name, ".png"))
  ggplot2::ggsave(path, width = width, height = height, dpi = dpi)
  message("Plot saved: ", path)
  invisible(path)
}

cc_env <- function() {
  objs <- ls(envir = .GlobalEnv)
  if (!length(objs)) {
    cat("(empty)\n")
    return(invisible(NULL))
  }
  out <- purrr::map_dfr(objs, function(x) {
    o <- get(x, envir = .GlobalEnv)
    tibble::tibble(
      name  = x,
      class = paste(class(o), collapse = "/"),
      dim   = if (!is.null(dim(o))) paste(dim(o), collapse = "x") else as.character(length(o)),
      mem   = format(utils::object.size(o), units = "auto")
    )
  })
  print(out, n = Inf)
  invisible(out)
}

cc_view <- function(x, n = 50) {
  nm <- deparse(substitute(x))
  dir <- ".claude/scratch"
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  path <- file.path(dir, paste0(nm, ".csv"))
  utils::write.csv(utils::head(x, n), path, row.names = FALSE)
  message("Preview saved: ", path, " (", nrow(x), " rows total)")
  invisible(path)
}
```

Behavioral contract:

| Function | Inputs | Output (visible) | Output (return) |
|----------|--------|------------------|-----------------|
| `cc_plot(name, width, height, dpi)` | last ggplot on device, optional name | message with file path | path (invisible) |
| `cc_env()` | none | tibble printed to console | tibble (invisible) |
| `cc_view(x, n)` | object `x`, head size `n` | message with file path and total row count | path (invisible) |

Dependencies: `ggplot2`, `purrr`, `tibble`, plus base `utils`. All are
tidyverse-standard for this project.

### SKILL.md changes

**Edit 1 — Step 4 `.Rprofile` tip:** Extend the existing block to include the
helper source line:

```r
# .Rprofile
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
  try(source(".claude/scripts/cc-helpers.R"), silent = TRUE)
}
```

**Edit 2 — new section after Step 5, before "How Skills Use MCP Tools":**

```markdown
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
```

After both edits SKILL.md is approximately 207 lines (current 182 plus ~25
added), comfortably under the 300-line limit.

### `references/ide-awareness-helpers.md`

A new reference (~80 lines) covering:

1. **Rationale** — what Positron Assistant has that Claude Code doesn't, and
   why on-disk artifacts close the gap
2. **`cc_plot()` usage** — ggplot vs. base graphics (note `dev.copy(png, path); dev.off()`
   for base), naming conventions, default dimensions
3. **`cc_env()` usage** — when to call it (start of debugging, before asking
   "why is this NA"), what the columns mean
4. **`cc_view()` usage** — round-trip-via-CSV reasoning (Claude reads CSV
   cleanly; `print()` and `glimpse()` truncate and lose alignment), `n`
   parameter for very wide rows
5. **`.Rprofile` and ignore-file wiring** — full snippets
6. **Workflow patterns** — three short examples mapping to the three modes
   (interactive analysis, authoring, debugging)
7. **Discipline note** — when to reach for which helper

### `references/mcp-troubleshooting.md` addition

One new short subsection:

```markdown
### `cc_env()` shows an empty workspace via Claude

Symptom: you have objects in your Positron R session, but when Claude calls
`cc_env()` through `r-btw`, it returns `(empty)`.

Cause: `btw_tool_run_r()` is hitting a fresh R subprocess, not the Positron
session bridged by `mcptools::mcp_session()`.

Fix:
1. Confirm `mcptools::mcp_session()` is running in the Positron console (check
   the startup message — declaring it in `.Rprofile` is not enough if the
   session was launched before the line was added)
2. Confirm `.mcp.json` registers `mcptools::mcp_server()` for stateful tools
   (not a bare `Rscript -e "btw::btw_mcp_server(...)"` which spawns its own
   process)
3. Restart Claude Code so the MCP connection re-establishes against the
   running session
```

## Data Flow

```
User in Positron console
     |
     v
calls cc_plot() / cc_env() / cc_view(df)
     |
     v
helper writes to .claude/scratch/{plots,*.csv}
     |
     v
helper prints message with file path
     |
     v
User tells Claude (or Claude reads via mcp_session() messages):
"see .claude/scratch/plots/latest.png" / "check .claude/scratch/df.csv"
     |
     v
Claude uses Read (CSV) or view (PNG) tool on the artifact
```

The flow has one intentional manual step: the user (or `mcp_session()`-routed
console output) tells Claude where to look. This is the "discipline" the
non-goals section names. Removing this step is the deferred auto-capture
work.

## Error Handling

- `cc_plot()` — relies on `ggplot2::ggsave()` which errors clearly if no plot
  is on the device. No custom handling needed.
- `cc_env()` — empty workspace prints `(empty)` and returns invisibly. No
  errors expected for normal use.
- `cc_view()` — `utils::write.csv()` errors clearly on non-tabular input
  (e.g., a list that won't coerce). No custom handling needed; the error
  message is informative.

All three use `dir.create(..., showWarnings = FALSE, recursive = TRUE)` so
re-runs don't warn.

## Testing

The supeRpowers test suite covers structural and convention checks. The
relevant tests after these changes:

1. **`test_structural.py`** — verifies SKILL.md ≤ 300 lines and frontmatter
   format. After edit, SKILL.md is ~207 lines. PASS expected.
2. **`test_conventions.py`** — verifies no `%>%` in `skills/`, `agents/`,
   `rules/` (excluding `eval.md`); `<-` for assignment; `snake_case`; double
   quotes. The new `cc-helpers.R` and new markdown content must comply.
3. **`test_routing.py`** — verifies skill routing matrix. No new triggers
   added; existing `r-mcp-setup` routing unaffected.

No new tests are added by this change. The helpers themselves are not
exercised by the suite — they're a shippable artifact, not skill logic.

## Verification Checklist

Before declaring the implementation complete:

- [ ] No `%>%` in any new content
- [ ] All R code uses `<-`, `|>`, `snake_case`, double quotes
- [ ] SKILL.md is ≤ 300 lines
- [ ] `cc-helpers.R` runs without error in a clean interactive session with
      `ggplot2`, `purrr`, `tibble` available
- [ ] Sourcing the file from `.Rprofile` exposes `cc_plot`, `cc_env`,
      `cc_view` in the global environment
- [ ] `python tests/run_all.py` passes

## Out-of-Scope Future Work

If after using the basic helpers for a meaningful period the following
friction emerges, these are the deferred follow-ups in priority order:

1. **`/cc-status` slash command** — a new workflow command skill
   (`r-cmd-cc-status/`) that wraps `cc_env()` plus listings of recent plots
   and CSVs into one user-invocable command. Reach for this if the user finds
   themselves typing `cc_env(); cc_plot()` repeatedly.
2. **Auto-capture wrapper** — a `cc_run(expr)` helper that captures stdout,
   warnings, messages, the value, and any plot opened during evaluation into
   a single artifact. Reach for this if the user finds Claude debugging
   sessions repeatedly stalling on missing console output.
3. **`cc_view_sdtm()` SDTM variant** — pivots long-format SDTM domains to one
   row per `USUBJID × VISITNUM` for scannable preview. Should live in
   `r-clinical`, not here.
