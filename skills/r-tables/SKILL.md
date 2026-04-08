---
name: r-tables
description: >
  Use when creating publication-quality tables in R with gt, gtsummary,
  gtExtras, or reactable. Provides expert guidance on summary tables,
  regression tables, demographic Table 1 layouts, journal themes, conditional
  formatting, sparklines, and multi-format output to HTML, PDF, and Word.
  Triggers: table, gt, gtsummary, gtExtras, reactable, summary table,
  regression table, Table 1, demographics table, publication table, formatting.
  Do NOT use for plots or charts — use r-visualization instead.
  Do NOT use for Shiny interactive tables embedded in apps — use r-shiny instead.
---

# R Tables

Publication-quality tables for manuscripts, reports, and dashboards using gt,
gtsummary, gtExtras, and reactable. All code uses base pipe `|>` and `<-`.

> **Boundary:** Formatted publication tables. For plots and charts, use r-visualization instead. For regulatory TLFs in clinical context, use r-clinical instead.

**Agent dispatch:** For statistical table review, dispatch to **r-statistician** agent. For code quality, dispatch to **r-code-reviewer** agent.

**MCP integration (when R session available):**
- Before designing a table: `btw_tool_env_describe_data_frame` to inspect column names, types, and cardinality for grouping/stratification decisions
- When uncertain about gt or gtsummary functions: `btw_tool_docs_help_page` to check current API and arguments

**Lazy references:**
- Read `references/gtsummary-themes.md` for journal themes, custom theme creation, and statistic display patterns
- Read `references/gt-formatting-patterns.md` for conditional formatting, embedded plots, and export workflows

---

## gt Conventions

Pipeline: `data |> gt() |> cols_label() |> fmt_*() |> tab_header() |> tab_spanner() |> tab_footnote() |> tab_source_note()`. Use `fmt_*()` functions for all formatting — never pre-format data as character. Conditional styling uses `tab_style()` with `cells_body(rows = ..., columns = ...)` targeting.

Read `references/gt-formatting-patterns.md` for conditional formatting, embedded plots, and export workflows.

---

## gtsummary Workflows

### Table 1 — Demographics

```r
library(gtsummary)

trial |>
  tbl_summary(
    by        = trt,
    include   = c(age, grade, stage, response),
    label     = list(age ~ "Age, years", grade ~ "Tumor Grade"),
    statistic = list(
      all_continuous()  ~ "{mean} ({sd})",
      all_categorical() ~ "{n} ({p}%)"
    ),
    missing   = "no"
  ) |>
  add_overall() |>
  add_p() |>
  add_difference() |>
  bold_labels() |>
  modify_header(label ~ "**Variable**")
```

### Regression Results

```r
glm(response ~ trt + age + grade, data = trial, family = binomial) |>
  tbl_regression(
    exponentiate = TRUE,
    label        = list(trt ~ "Treatment", age ~ "Age")
  ) |>
  add_global_p() |>
  bold_p(t = 0.05) |>
  bold_labels()
```

### Combining Tables

```r
# Side by side
tbl_merge(
  tbls        = list(tbl_unadj, tbl_adj),
  tab_spanner = c("**Unadjusted**", "**Adjusted**")
)

# Stack vertically
tbl_stack(
  tbls        = list(tbl_os, tbl_pfs),
  group_header = c("Overall Survival", "Progression-Free Survival")
)
```

Always add `bold_labels()` to publication tables. Use `tbl_merge()` for side-by-side, `tbl_stack()` for vertical combination. Use `add_p()`, `add_overall()`, `add_difference()` as needed.

---

## gtExtras

Use gtExtras for inline visualizations in gt tables: `gt_sparkline()` for trends, `gt_plt_bar()` for bar charts, `gt_color_rows()` for heatmaps, `gt_theme_538()` / `gt_theme_espn()` for pre-built themes.

---

## Journal Themes (gtsummary)

```r
# Apply journal theme before building table
theme_gtsummary_journal("jama")   # JAMA
theme_gtsummary_journal("lancet") # Lancet
theme_gtsummary_journal("nejm")   # NEJM
theme_gtsummary_journal("qjecon") # Econ journals

# Compact for supplementary material
theme_gtsummary_compact()

# Reset
reset_gtsummary_theme()
```

Read `references/gtsummary-themes.md` for custom theme creation and stacking.

---

## Output Formats

```r
# HTML (default — inline in R Markdown / Quarto)
tbl |> as_gt() |> gtsave("table.html")

# PDF via LaTeX — requires gt + tinytex
tbl |> as_gt() |> gtsave("table.pdf")

# PNG snapshot
tbl |> as_gt() |> gtsave("table.png", zoom = 2)

# Word — gtsummary -> flextable -> docx
tbl |>
  as_flex_table() |>
  flextable::save_as_docx(path = "table.docx")

# Quarto / R Markdown — just print
tbl         # gtsummary prints via knitr
tbl |> as_gt()  # gt renders via knitr
```

---

## Interactive Tables (reactable)

Use `reactable` for Shiny/Quarto HTML interactive tables (filtering, sorting, pagination). Use gt/gtsummary for static/print output. Do not mix the two — they have separate styling systems.

---

## Verification

After gtsummary theme: verify `reset_gtsummary_theme()` called. After export: confirm output renders in target format.

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| Using `gt()` on columns with spaces in names | `gt` can't resolve bare column names with spaces; errors in `cols_label()` and `fmt_*()` | Rename columns first with `rename()` or use backtick-quoted names |
| Forgetting `as_gt()` when piping gtsummary to gt functions | `tbl_summary` objects are not gt objects; gt functions silently fail or error | Pipe through `as_gt()` before any `tab_*()`, `fmt_*()`, or `gt_*()` calls |
| `tbl_summary()` defaulting to median for continuous variables | Default statistic is `"{median} ({p25}, {p75})"` — users often expect mean | Set `statistic = list(all_continuous() ~ "{mean} ({sd})")` explicitly if mean is wanted |
| Forgetting `bold_labels()` for publication formatting | Labels look like plain text; reviewers and journals expect bold variable names | Add `bold_labels()` to every publication table pipeline |
| `gtsave()` PNG requires webshot2/chromote; PDF requires tinytex | `gtsave("table.png")` errors with cryptic message if chromote is missing | Install `webshot2` + Chrome/Chromium for PNG; `tinytex::install_tinytex()` for PDF |
| `theme_gtsummary_journal()` has global side effects | Theme persists across all subsequent tables in the session | Call `reset_gtsummary_theme()` after building the themed table |
| Building full data pipeline when user asked to format one table | Scope creep — user wants table styling, not data wrangling | Format the data provided; suggest upstream changes only if asked |

## Examples

### Happy Path: Demographics Table 1 with gtsummary

**Prompt:** "Create a demographics Table 1 comparing treatment vs control with p-values for JAMA."

```r
# Input
library(gtsummary)
theme_gtsummary_journal("jama")

tbl1 <- trial |>
  tbl_summary(
    by        = trt,
    include   = c(age, grade, stage),
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     all_categorical() ~ "{n} ({p}%)"),
    missing   = "no"
  ) |>
  add_overall() |>
  add_p() |>
  bold_labels()

# Output — rendered gt table with JAMA styling
tbl1

reset_gtsummary_theme()
```

### Edge Case: Merging two gtsummary tables with duplicate column names

**Prompt:** "Combine unadjusted and adjusted regression tables side by side."

```r
# Input — two models produce tables with identical stat column names
tbl_unadj <- glm(response ~ trt, data = trial, family = binomial) |>
  tbl_regression(exponentiate = TRUE)

tbl_adj <- glm(response ~ trt + age + grade, data = trial, family = binomial) |>
  tbl_regression(exponentiate = TRUE)

# WRONG — piping gtsummary directly to gt functions without as_gt()
# tbl_unadj |> tab_header(title = "Model")   # ERROR

# CORRECT — tbl_merge handles column deduplication automatically
tbl_merged <- tbl_merge(
  tbls        = list(tbl_unadj, tbl_adj),
  tab_spanner = c("**Unadjusted**", "**Adjusted**")
)
tbl_merged
```

**More example prompts:**
- "Build a gt table with sparkline trend columns using gtExtras."
- "Export a gtsummary table to Word for my manuscript."
- "Color p-values red when < 0.05 and add data bars to effect sizes."
