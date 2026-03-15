---
name: r-tables
description: >
  Use when creating publication-quality tables in R with gt, gtsummary,
  gtExtras, or reactable. Covers formatting, themes, journal styles, and
  output to HTML, PDF, and Word.
---

# R Tables

Publication-quality tables for manuscripts, reports, and dashboards using gt,
gtsummary, gtExtras, and reactable. All code uses base pipe `|>` and `<-`.

**Lazy references:**
- Read `references/gtsummary-themes.md` for journal themes, custom theme creation, and statistic display patterns
- Read `references/gt-formatting-patterns.md` for conditional formatting, embedded plots, and export workflows

---

## gt Fundamentals

```r
library(gt)

mtcars |>
  head(10) |>
  gt() |>
  tab_header(
    title    = "Motor Trend Car Road Tests",
    subtitle = "First 10 observations"
  ) |>
  cols_label(mpg = "MPG", cyl = "Cylinders", wt = "Weight") |>
  fmt_number(columns = c(mpg, wt), decimals = 1) |>
  tab_spanner(label = "Performance", columns = c(mpg, hp, qsec)) |>
  tab_footnote(
    footnote  = "Miles per US gallon.",
    locations = cells_column_labels(columns = mpg)
  ) |>
  tab_source_note("Source: Motor Trend, 1974")
```

### Formatting Functions

| Function | Use |
|----------|-----|
| `fmt_number(decimals = 2)` | Numeric with decimal places |
| `fmt_percent(decimals = 1)` | Proportions as % |
| `fmt_currency(currency = "USD")` | Dollar amounts |
| `fmt_integer()` | Whole numbers with comma sep |
| `fmt_date(date_style = "yMMMd")` | Dates |
| `fmt_missing(rows = everything())` | Replace NA display |

### Styling

```r
tbl |>
  tab_style(
    style     = cell_fill(color = "#F0F0F0"),
    locations = cells_body(rows = cyl == 6)
  ) |>
  tab_style(
    style     = cell_text(weight = "bold", color = "#C00000"),
    locations = cells_body(columns = mpg, rows = mpg < 15)
  ) |>
  tab_options(
    table.font.size      = 12,
    column_labels.font.weight = "bold",
    heading.align        = "left"
  )
```

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

### Key Modifiers Quick Reference

| Function | Purpose |
|----------|---------|
| `add_p()` | P-values for group comparisons |
| `add_overall()` | Overall column (ignores `by =`) |
| `add_difference()` | Mean/proportion difference + CI |
| `add_n()` | Sample size per group |
| `bold_labels()` | Bold row labels |
| `italicize_levels()` | Italicize level labels |
| `modify_spanning_header()` | Custom spanning headers |

---

## gtExtras

```r
library(gtExtras)

# Sparkline column
df |>
  gt() |>
  gt_sparkline(trend_col, type = "line", same_limit = FALSE)

# Inline bar chart
df |>
  gt() |>
  gt_plt_bar(value_col, color = "steelblue", scale_type = "number")

# Built-in themes
tbl |> gt_theme_538()
tbl |> gt_theme_nytimes()
tbl |> gt_theme_espn()
tbl |> gt_theme_guardian()

# Color-scale column
tbl |>
  gt_color_rows(
    columns  = value,
    palette  = c("#FFF5F0", "#C00000"),
    domain   = c(0, 100)
  )
```

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

```r
library(reactable)

reactable(
  mtcars,
  filterable  = TRUE,
  searchable  = TRUE,
  pagination  = TRUE,
  defaultPageSize = 15,
  columns = list(
    mpg = colDef(name = "MPG", format = colFormat(digits = 1)),
    cyl = colDef(name = "Cylinders", filterable = TRUE)
  ),
  theme = reactableTheme(
    borderColor     = "#dfe2e5",
    stripedColor    = "#f6f8fa",
    highlightColor  = "#f0f5ff"
  )
)
```

Use `reactable` for Shiny and Quarto HTML output; use gt/gtsummary for
static/print contexts.

---

## Examples

### 1. Table 1 for a clinical paper
**Prompt:** "Create a demographics Table 1 comparing treatment vs control with
p-values, styled for JAMA submission."

### 2. Regression table with multiple models
**Prompt:** "Make a publication table showing unadjusted and adjusted odds
ratios side by side from two logistic regression models."

### 3. Summary statistics with sparklines
**Prompt:** "Build a gt table of monthly sales by region with sparkline
trend columns using gtExtras."

### 4. Export table to Word
**Prompt:** "I have a gtsummary tbl_summary — export it to a Word document
for my manuscript."

### 5. Conditional formatting
**Prompt:** "Color the p-value column red when < 0.05 and add data bars to
the effect size column."
