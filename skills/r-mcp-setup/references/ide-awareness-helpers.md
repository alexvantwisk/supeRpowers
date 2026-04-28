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
