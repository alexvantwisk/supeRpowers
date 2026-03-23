# gt Formatting Patterns

Advanced gt formatting: conditional coloring, data bars, embedded plots,
grouped headers, stub styling, and export pipelines.

---

## Conditional Formatting

### Color Scale (data_color)

```r
library(gt)

tbl |>
  data_color(
    columns  = value,
    palette  = c("#FFF5F0", "#FEE0D2", "#FC9272", "#DE2D26"),
    domain   = c(0, 100),
    na_color = "#FFFFFF"
  )

# Diverging scale (negative → 0 → positive)
tbl |>
  data_color(
    columns = change,
    palette = c("#2166AC", "#F7F7F7", "#D73027"),
    domain  = c(-50, 50)
  )
```

### Conditional Cell Styles

```r
# Highlight rows where p < 0.05
tbl |>
  tab_style(
    style     = list(
      cell_fill(color = "#FFF3CD"),
      cell_text(weight = "bold")
    ),
    locations = cells_body(
      columns = everything(),
      rows    = p_value < 0.05
    )
  )

# Bold max value per column
tbl |>
  tab_style(
    style     = cell_text(weight = "bold"),
    locations = cells_body(
      columns = score,
      rows    = score == max(score)
    )
  )
```

### Data Bars (gtExtras)

```r
library(gtExtras)

# Normalized bar within the cell
tbl |> gt_plt_bar(
  column     = value,
  color      = "steelblue",
  scale_type = "number",     # "number", "percent", or "normalized"
  width      = 65
)

# Bar chart with positive/negative coloring
tbl |> gt_plt_bar_pct(
  column = pct_change,
  labels = TRUE,
  fill   = "steelblue",
  background = "white"
)
```

---

## Column Spanners and Grouped Headers

```r
# Single spanner
tbl |>
  tab_spanner(
    label   = "Baseline Characteristics",
    columns = c(age, sex, bmi)
  )

# Nested spanners
tbl |>
  tab_spanner(label = "Month 1", columns = c(m1_n, m1_pct), id = "m1") |>
  tab_spanner(label = "Month 6", columns = c(m6_n, m6_pct), id = "m6") |>
  tab_spanner(
    label   = "Follow-up",
    columns = c(m1_n, m1_pct, m6_n, m6_pct),
    id      = "fu",
    level   = 2
  )

# Rename columns after spanning
tbl |>
  cols_label(
    m1_n   = "n",  m1_pct = "%",
    m6_n   = "n",  m6_pct = "%"
  )
```

### Row Groups

```r
# Group rows by a column
data |>
  gt(groupname_col = "category") |>
  tab_style(
    style     = cell_fill(color = "#E8F4FD"),
    locations = cells_row_groups()
  ) |>
  tab_style(
    style     = cell_text(weight = "bold"),
    locations = cells_row_groups()
  ) |>
  summary_rows(
    groups    = everything(),
    fns       = list(Total = ~ sum(., na.rm = TRUE)),
    formatter = fmt_integer
  )
```

---

## Stub and Row Styling

```r
# Use a column as the row stub (row labels)
data |>
  gt(rowname_col = "variable") |>
  tab_stubhead(label = "Variable") |>
  tab_style(
    style     = cell_text(weight = "bold"),
    locations = cells_stub(rows = everything())
  )

# Indent sub-rows (hierarchical display)
tbl |>
  tab_style(
    style     = cell_text(indent = px(20)),
    locations = cells_stub(rows = is_sub_row)
  )
```

---

## Embedding Plots in Cells

```r
library(gtExtras)

# Sparklines
df_nested |>
  gt() |>
  gt_sparkline(
    column     = weekly_values,  # List-column of numeric vectors
    type       = "line",         # "line", "bar", "boxplot", "win_loss"
    same_limit = TRUE,           # Shared y-axis across rows
    palette    = c("steelblue", "red")
  )

# Histogram in cell
df_nested |>
  gt() |>
  gt_plt_dist(
    column  = values,
    type    = "histogram",
    fig_dim = c(5, 30)
  )

# Win/loss plot (binary outcomes)
df_results |>
  gt() |>
  gt_plt_winloss(
    column = outcomes,  # List of 1/0/-1 vectors
    max_wins = 10
  )
```

---

## Export Workflows

### HTML

```r
# Render inline in Quarto / R Markdown — just print
tbl  # auto-renders

# Save standalone HTML
tbl |> gtsave("output/table.html")

# With custom CSS
tbl |>
  opt_css(
    css = "
      .gt_table { font-family: 'Helvetica Neue', sans-serif; }
      .gt_heading { background-color: #003366; color: white; }
    "
  ) |>
  gtsave("output/table_styled.html")
```

### PDF via LaTeX

```r
# Requires: tinytex::install_tinytex() or a full LaTeX installation
tbl |> gtsave("output/table.pdf")

# For inclusion in a LaTeX document — extract LaTeX source
latex_source <- tbl |> as_latex()
```

### Word Document

```r
# gt -> Word (experimental, limited styling support)
tbl |> gtsave("output/table.docx")

# RECOMMENDED: gtsummary -> flextable -> docx (full Word styling)
library(flextable)

gtsummary_tbl |>
  as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit") |>
  flextable::fontsize(size = 10, part = "all") |>
  flextable::save_as_docx(path = "output/table.docx")
```

### PNG / Image Snapshot

```r
# Requires: webshot2 or webshot package
tbl |> gtsave("output/table.png", zoom = 2, expand = 10)
tbl |> gtsave("output/table.svg")
```

### Full Pipeline: HTML → PDF → Word

```r
build_table <- function(data) {
  data |>
    tbl_summary(by = group) |>
    add_p() |>
    bold_labels()
}

tbl <- build_table(trial)

# HTML
tbl |> as_gt() |> gtsave("tables/table1.html")

# PDF
tbl |> as_gt() |> gtsave("tables/table1.pdf")

# Word
tbl |>
  as_flex_table() |>
  flextable::save_as_docx(path = "tables/table1.docx")
```

---

## Integration with R Markdown / Quarto

For Quarto document integration (chunk options, cross-references, format-conditional output), use the **r-quarto** skill.

---

## gt opt_stylize Presets

Quick professional styling without manual `tab_options()`:

```r
tbl |> opt_stylize(style = 1)   # Minimal — light grey alternating rows
tbl |> opt_stylize(style = 2)   # Simple lines — horizontal only
tbl |> opt_stylize(style = 3)   # Filled header + alternating
tbl |> opt_stylize(style = 4)   # Bold borders
tbl |> opt_stylize(style = 5)   # Dark header
tbl |> opt_stylize(style = 6)   # Full grid

# With color accent
tbl |> opt_stylize(style = 6, color = "blue")   # "red", "orange", "yellow",
                                                 # "green", "teal", "blue", "pink"
```

---

## Column Width and Layout

```r
tbl |>
  cols_width(
    variable ~ px(200),
    everything() ~ px(100)
  ) |>
  cols_align(align = "center", columns = everything()) |>
  cols_align(align = "left",   columns = variable) |>
  cols_hide(columns = c(internal_id, row_key)) |>
  cols_move_to_start(columns = variable) |>
  cols_move(columns = p_value, after = ci_upper)
```
