# r-mcp-setup IDE-Awareness Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `r-mcp-setup` skill with three R helper functions, project wiring guidance, and one troubleshooting note so Claude Code can see plots, environment state, and tabular previews when working in Positron.

**Architecture:** Ship a real `cc-helpers.R` script under `skills/r-mcp-setup/scripts/`, document the install/wire-up in SKILL.md (one tip extension + one new optional Step 6), add a deep-dive reference at `references/ide-awareness-helpers.md`, and append one diagnostic subsection to `references/mcp-troubleshooting.md`.

**Tech Stack:** R (≥ 4.1.0), tidyverse (ggplot2, purrr, tibble), markdown, project test suite (`python tests/run_all.py`).

**Spec:** `docs/superpowers/specs/2026-04-28-r-mcp-setup-ide-awareness-design.md`

---

## File Structure

| Path | Action | Responsibility |
|------|--------|----------------|
| `skills/r-mcp-setup/scripts/cc-helpers.R` | Create | Three helper functions users source from `.Rprofile` |
| `skills/r-mcp-setup/SKILL.md` | Modify | Extend Step 4 `.Rprofile` tip; add new Step 6 section |
| `skills/r-mcp-setup/references/ide-awareness-helpers.md` | Create | Rationale, function-by-function docs, workflow examples |
| `skills/r-mcp-setup/references/mcp-troubleshooting.md` | Modify | Add `cc_env() shows empty workspace` diagnostic |

No `plugin.json` changes (the existing `skills/*/SKILL.md` glob already loads the skill; `scripts/` and `references/` are static assets referenced by path).

---

## Task 1: Create the helper script

**Files:**
- Create: `skills/r-mcp-setup/scripts/cc-helpers.R`

- [ ] **Step 1: Verify the directory does not yet exist**

Run: `ls skills/r-mcp-setup/scripts/ 2>/dev/null || echo "missing — will create"`
Expected: `missing — will create`

- [ ] **Step 2: Create the script file**

Write to `skills/r-mcp-setup/scripts/cc-helpers.R`:

```r
# cc-helpers.R — IDE-awareness helpers for Claude Code
# Source from .Rprofile to make these available in interactive R sessions.
# Pairs with mcptools::mcp_session() to close the gap with Positron Assistant.

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

- [ ] **Step 3: Confirm no R convention violations**

Run: `grep -n '%>%\|<-.*=\|=[^=].*<-' skills/r-mcp-setup/scripts/cc-helpers.R`
Expected: no output (no `%>%`, no `=` assignments where `<-` belongs).

Also run: `grep -n "'" skills/r-mcp-setup/scripts/cc-helpers.R | grep -v '^.*#'`
Expected: no output (no single-quoted strings outside comments — the `%||%` operator uses backticks which is fine).

- [ ] **Step 4: Run the convention test layer**

Run: `python tests/run_all.py --layer 1b`
Expected: PASS for r-conventions checks (no `%>%`, snake_case, double quotes, `<-`).

If FAIL, read the failure message and fix the offending line in `cc-helpers.R`.

- [ ] **Step 5: Commit**

```bash
git add skills/r-mcp-setup/scripts/cc-helpers.R
git commit -m "feat(r-mcp-setup): add cc-helpers.R for IDE-awareness artifacts"
```

---

## Task 2: Extend SKILL.md Step 4 `.Rprofile` tip

**Files:**
- Modify: `skills/r-mcp-setup/SKILL.md` (lines 124-129)

- [ ] **Step 1: Read the current tip block**

Read `skills/r-mcp-setup/SKILL.md` lines 120-135 to confirm the tip block matches what we expect to replace.

Current content (lines 124-129):
```markdown
**Tip:** Add to `.Rprofile` for auto-start:
```r
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
}
```
```

- [ ] **Step 2: Replace with extended tip**

Use Edit to replace exactly:

```r
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
}
```

with:

```r
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
  try(source(".claude/scripts/cc-helpers.R"), silent = TRUE)
}
```

(Sourcing the helpers from the same block keeps interactive setup in one place. The `silent = TRUE` is intentional — if the user hasn't installed the helpers yet, no warning fires.)

- [ ] **Step 3: Confirm SKILL.md still parses cleanly**

Run: `head -10 skills/r-mcp-setup/SKILL.md`
Expected: frontmatter intact starting with `---`, `name: r-mcp-setup`, `description: ...`.

- [ ] **Step 4: Do not commit yet**

Step 4 of Task 2 and Task 3 share a commit. Hold off on `git commit` until Task 3 finishes.

---

## Task 3: Add SKILL.md Step 6 section

**Files:**
- Modify: `skills/r-mcp-setup/SKILL.md` (insert after the existing Step 5, before "How Skills Use MCP Tools")

- [ ] **Step 1: Locate the insertion point**

Run: `grep -n '^## How Skills Use MCP Tools\|^### Step 5\|^---$' skills/r-mcp-setup/SKILL.md`
Expected output includes the line numbers of `### Step 5: Verify`, the `---` separator after it, and `## How Skills Use MCP Tools`.

The new Step 6 goes between the `---` separator after Step 5 and the `## How Skills Use MCP Tools` heading.

- [ ] **Step 2: Insert the new section**

Use Edit to replace exactly:

```markdown
The output should show `r-btw` with status `connected`. If it shows
`disconnected` or doesn't appear, see `references/mcp-troubleshooting.md`.

---

## How Skills Use MCP Tools
```

with:

```markdown
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
```

- [ ] **Step 3: Verify SKILL.md is still under the 300-line cap**

Run: `wc -l skills/r-mcp-setup/SKILL.md`
Expected: a number ≤ 300 (target ~207).

If the count exceeds 300, trim the new Step 6 prose (the "Honest framing" paragraph is the most cuttable) until under the cap.

- [ ] **Step 4: Run the structural test layer**

Run: `python tests/run_all.py --layer 1`
Expected: PASS for SKILL.md size and frontmatter checks.

- [ ] **Step 5: Commit Task 2 + Task 3 together**

```bash
git add skills/r-mcp-setup/SKILL.md
git commit -m "docs(r-mcp-setup): document cc-helpers wiring in Step 4 + Step 6"
```

---

## Task 4: Add `references/mcp-troubleshooting.md` diagnostic

**Files:**
- Modify: `skills/r-mcp-setup/references/mcp-troubleshooting.md` (append at end)

- [ ] **Step 1: Read the current end of the file**

Run: `tail -20 skills/r-mcp-setup/references/mcp-troubleshooting.md`
Expected: shows the current final section. Note its exact last line so the new section can be appended cleanly.

- [ ] **Step 2: Append the new section**

Use Edit to add after the file's current final line (preserving any trailing newline):

```markdown

## `cc_env()` shows an empty workspace via Claude

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

(The heading level is `##` because the existing troubleshooting file uses `##`
for top-level diagnostics. Confirm in Step 1's tail output before committing.
If the existing file uses `###`, downgrade the new heading to `###` to match.)

- [ ] **Step 3: Verify no `%>%` introduced**

Run: `grep -n '%>%' skills/r-mcp-setup/references/mcp-troubleshooting.md`
Expected: no output.

- [ ] **Step 4: Run convention tests**

Run: `python tests/run_all.py --layer 1b`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/r-mcp-setup/references/mcp-troubleshooting.md
git commit -m "docs(r-mcp-setup): add cc_env empty-workspace troubleshooting note"
```

---

## Task 5: Create `references/ide-awareness-helpers.md`

**Files:**
- Create: `skills/r-mcp-setup/references/ide-awareness-helpers.md`

- [ ] **Step 1: Confirm the file does not yet exist**

Run: `ls skills/r-mcp-setup/references/ide-awareness-helpers.md 2>/dev/null || echo "missing — will create"`
Expected: `missing — will create`.

- [ ] **Step 2: Write the reference file**

Write to `skills/r-mcp-setup/references/ide-awareness-helpers.md`:

````markdown
# IDE-Awareness Helpers

`cc_plot()`, `cc_env()`, and `cc_view()` close the gap between Claude Code
and Positron Assistant for in-IDE R awareness. This file explains the
rationale, the contract for each helper, and the workflow patterns that make
them feel ambient rather than ceremonial.

## Why these helpers exist

`mcptools::mcp_session()` already routes Claude into your running R session,
so `ls()`, `str(df)`, and `summary()` inspect the same environment you are
working in. That closes the runtime-state gap. What remains is visual and
tabular: Claude cannot see your Plots pane, your Environment pane, or your
Data Viewer.

PNGs and CSVs on disk are something Claude *can* read. Each helper writes a
file Claude can open with its `view` (PNG) or `Read` (CSV) tool, then prints
the path so you can paste it into chat — or so the `mcp_session()`-routed
console output carries it forward automatically.

## `cc_plot(name = NULL, width = 8, height = 5, dpi = 120)`

Saves the last ggplot on the device to `.claude/scratch/plots/<name>.png`. If
`name` is omitted, uses a `YYYYMMDD-HHMMSS` timestamp.

```r
ggplot(mtcars, aes(wt, mpg)) + geom_point()
cc_plot()
# Plot saved: .claude/scratch/plots/20260428-153822.png
```

Tell Claude: "see `.claude/scratch/plots/latest.png`" — Claude reads PNGs
natively.

**Base graphics:** `ggsave()` only works for ggplots. For base graphics, swap
in:

```r
dev.copy(png, ".claude/scratch/plots/diag.png", width = 800, height = 500)
dev.off()
```

## `cc_env()`

Prints a one-row-per-object summary of the global environment: name, class,
dim (or length for non-array objects), memory footprint. Returns the tibble
invisibly so you can pipe it into `dplyr` for filtering.

```r
cc_env()
# # A tibble: 3 x 4
#   name  class      dim       mem
#   <chr> <chr>      <chr>     <chr>
# 1 df    data.frame 1000x12   78 Kb
# 2 model lm         12        45 Kb
# 3 plot  gg/ggplot  9         12 Kb
```

This is the workspace map Claude needs at the start of any debugging or
"why is this NA" question.

## `cc_view(x, n = 50)`

Writes `head(x, n)` to `.claude/scratch/<name>.csv`. The variable name is
captured via `deparse(substitute(x))` so the file name matches the object
name in your session.

```r
cc_view(orders)
# Preview saved: .claude/scratch/orders.csv (12483 rows total)
```

Why CSV instead of `print()` or `glimpse()`? Two reasons. First, `print()`
truncates wide frames and loses column alignment in monospace-but-not-quite
markdown rendering. Second, Claude reads CSVs cleanly with type-aware parsing
— column types come through, NA stays NA, dates stay dates.

## Wiring

Drop the helper file in your project, then source it from a project-local
`.Rprofile`:

```r
# .Rprofile
if (interactive()) {
  try(mcptools::mcp_session(), silent = TRUE)
  try(source(".claude/scripts/cc-helpers.R"), silent = TRUE)
}
```

Add to `.gitignore`:

```
.claude/scratch/
```

If your project is an R package, also add to `.Rbuildignore`:

```
^\.claude/scratch/$
```

## Workflow patterns

**Interactive analysis.** You're exploring a new dataset. Run your first
loading and shaping pipeline, then `cc_env()` to give Claude a workspace map.
Make a plot, `cc_plot()`, point Claude at the file. Find an interesting
slice, `cc_view(slice)`, ask Claude what it sees.

**Authoring.** You're writing a script or `.qmd` chunk. Source it
interactively, `cc_env()`, then ask Claude to extend it — Claude now writes
code that matches your real column names and shapes instead of guessing.

**Debugging.** Something broke. `cc_env()` first — sometimes the answer is
"that object isn't what you think it is." Then `cc_view()` the offending
input and `cc_plot()` any diagnostic figure. Claude reads the artifacts
together with the error message and proposes a fix grounded in actual state.

## Discipline

The honest residual gap with Positron Assistant: it has *passive* awareness —
it sees what you just ran without being told. Claude Code needs to be
pointed at things. The fix is not more machinery; it is the small habit of
calling `cc_env()` once per task and `cc_plot()` after each figure that
matters. That reproduces about 90% of "Positron Assistant feels smarter."

If you find yourself routinely forgetting and re-typing the calls, that is
the signal to design a `/cc-status` slash command or an auto-capture
wrapper around `btw_tool_run_r()`. Until then, the discipline is cheaper
than the machinery.
````

- [ ] **Step 3: Verify no `%>%` and `<-`/`|>` conventions hold**

Run: `grep -n '%>%\| = ' skills/r-mcp-setup/references/ide-awareness-helpers.md`
Expected: no output for `%>%`. The ` = ` matches will be in function arguments only — review and confirm no `=` is used where `<-` belongs.

- [ ] **Step 4: Run all test layers**

Run: `python tests/run_all.py`
Expected: all layers PASS.

If any layer fails, read the message and fix the offending content.

- [ ] **Step 5: Commit**

```bash
git add skills/r-mcp-setup/references/ide-awareness-helpers.md
git commit -m "docs(r-mcp-setup): add ide-awareness-helpers reference"
```

---

## Task 6: Final verification

**Files:** none modified

- [ ] **Step 1: Run the full test suite**

Run: `python tests/run_all.py`
Expected: all layers PASS, summary shows "All critical checks passed!".

- [ ] **Step 2: Confirm SKILL.md line count is under cap**

Run: `wc -l skills/r-mcp-setup/SKILL.md`
Expected: ≤ 300.

- [ ] **Step 3: Confirm cc-helpers.R sources cleanly in interactive R**

Run (only if R is on PATH and `ggplot2`, `purrr`, `tibble` are installed):

```bash
Rscript -e 'source("skills/r-mcp-setup/scripts/cc-helpers.R"); cat("loaded:", exists("cc_plot"), exists("cc_env"), exists("cc_view"), "\n")'
```

Expected: `loaded: TRUE TRUE TRUE`.

If R is not available locally, skip this step and note that the script will
be exercised the first time a user sources it.

- [ ] **Step 4: Confirm `git status` is clean**

Run: `git status`
Expected: "nothing to commit, working tree clean" — all four task commits
landed.

- [ ] **Step 5: Show the final commit log**

Run: `git log --oneline -6`
Expected: four new commits (helper script, SKILL.md docs, troubleshooting
note, ide-awareness-helpers reference) on top of the spec commit.
