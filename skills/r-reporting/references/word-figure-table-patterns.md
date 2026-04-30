# Figure & Table Patterns for Word

## The gtsummary -> flextable -> docx pipeline

`as_flex_table()` is the canonical exit from gtsummary into Word. After conversion,
apply `set_table_properties()` to enforce autofit layout and centered alignment, then
set a readable font size and bold the header row. Treat these three calls as a
non-negotiable wrapper — apply them on every table in a consulting report.

```r
library(flextable)

readRDS(tbl("01_table_one.rds")) |>
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all") |>
  flextable::bold(part = "header")
```

## gtsummary 2.x argument hygiene

gtsummary 2.x errors when `by = NULL` or `include = NULL` are passed explicitly —
behaviour that 1.x silently ignored. Build the args list conditionally with
`purrr::compact()`, which drops `NULL` entries, and dispatch via `rlang::exec(!!!args)`.
Do NOT use `do.call()`: it forces lazy promises prematurely and breaks gtsummary's
NSE column-type detection. Wrap in a project-level helper so every call site inherits
safe argument hygiene.

```r
build_summary_table <- function(data, stratifier = NULL, keep_vars = NULL) {
  args <- purrr::compact(list(
    data    = data,
    by      = stratifier,
    include = if (length(keep_vars) > 0) keep_vars else NULL
  ))
  rlang::exec(gtsummary::tbl_summary, !!!args) |>
    gtsummary::add_overall() |>
    gtsummary::bold_labels()
}
```

## gt -> docx native (gtsave)

`gt::gtsave("table.docx")` works for simple tables with plain text cells. For
non-trivial cases — conditional cell colours, summary footers, column spanners with
custom fonts — styling fidelity degrades because gt's docx exporter does not
implement the full HTML rendering pipeline. Prefer gtsummary -> `as_flex_table()` ->
docx for production reports. `gtsave()` to docx is acceptable for quick previews.

```r
# Quick preview only — not for production deliverables
my_gt |>
  gt::gtsave(filename = here::here("output", "tables", "preview_table.docx"))
```

## gt -> PNG fallback

When a gt table contains features flextable cannot represent —
`gtExtras::gt_sparkline()`, `gtExtras::gt_plt_bar()`, embedded plots, conditional
images — save it as a high-resolution PNG with `zoom = 2` and include via
`knitr::include_graphics()`. This is a deliberate fallback, not a default: it loses
accessibility (screen readers cannot parse pixel images) and copy-paste of values.
Document it with a code comment so future maintainers know it is intentional.

```r
# Deliberate PNG fallback — flextable cannot represent gtExtras inline graphics
# Tradeoff: loses accessibility and copy-paste of values
gt::gtsave(my_sparkline_tbl,
  filename = here::here("output", "tables", "12_sparklines.png"), zoom = 2)
knitr::include_graphics(fig("12_sparklines.png"))  # in report.qmd
```

## Conditional formatting in flextable

flextable's formula-based selectors are cleaner than gt's `tab_style(cells_body(...))`
for Word output because they generate native docx cell properties rather than inline
HTML styles. Use `bold()`, `color()`, and `bg()` with `i = ~<condition>` to target
rows. The tilde formula is evaluated against the flextable data frame, so column
names must match exactly. Multiple calls are additive in a pipeline.

```r
tbl_ft |>
  flextable::bold(i = ~p_value < 0.05, j = "p_value") |>
  flextable::color(i = ~estimate < 0, j = "estimate", color = "#B22222") |>
  flextable::bg(i = ~group == "Total",
    j = seq_len(ncol(tbl_ft$body$dataset)), bg = "lightgray")
```

## The RDS cache pattern

Build gtsummary table objects in the analysis script and save as RDS; the qmd reads
and converts to flextable. This avoids re-running gtsummary inside the render context
(slower, can produce different output if packages updated between runs) and improves
iteration speed because re-rendering does not re-fit models or re-summarise data.

```r
# 04_model.R — runs once, cached
tbl_one <- trial |>
  gtsummary::tbl_summary(by = "trt") |>
  gtsummary::add_p() |>
  gtsummary::bold_labels()
saveRDS(tbl_one, here::here("output", "tables", "01_table_one.rds"))

# report.qmd — fast, deterministic
readRDS(tbl("01_table_one.rds")) |>
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all") |>
  flextable::bold(part = "header")
```

## Multi-table merging

For side-by-side gtsummary tables, call `tbl_merge()` before `as_flex_table()`.
gtsummary handles column label deduplication natively, which would be laborious to
reproduce in flextable. Within a flextable, use `merge_h()` for horizontal spans and
`merge_v()` for vertical spans. Use `flextable::compose()` to build rich header
cells with mixed formatting.

```r
gtsummary::tbl_merge(
  tbls        = list(tbl_safety, tbl_efficacy),
  tab_spanner = c("**Safety**", "**Efficacy**")
) |>
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all")

# For cell merges within a single flextable:
ft |> flextable::merge_v(j = "group") |> flextable::merge_h(i = 1, part = "header")
```

## Figure sizing for letter/A4

Recommended defaults: 8" × 5" at 150 dpi for single-panel; 8" × 7" for two-row
patchwork; 8" × 9" for three-row. Heights above 9" risk pagination glitches in
Word. Set execute defaults in `_quarto.yml` and override per chunk.

```yaml
# _quarto.yml
execute:
  fig-width: 8
  fig-height: 5
  fig-dpi: 150
```

```r
#| label: fig-forest
#| fig-width: 8
#| fig-height: 9
#| fig-cap: "Three-panel forest plot."

patchwork::wrap_plots(p_primary, p_secondary, p_subgroup, ncol = 1)
```

## ggplot theming for print

Set an explicit white opaque background so figures don't have a transparent wash
when embedded. Use `base_size >= 11` for legible labels after scaling. Prefer
viridis or Color Brewer palettes for colour-blind safety. Include explicit axis
titles with units and make legend backgrounds opaque.

```r
ggplot2::ggplot(df, ggplot2::aes(x = week, y = hba1c, colour = arm)) +
  ggplot2::geom_line() +
  ggplot2::scale_colour_brewer(palette = "Set1") +
  ggplot2::labs(x = "Week", y = "HbA1c (%)", colour = "Treatment arm") +
  ggplot2::theme_minimal(base_size = 11) +
  ggplot2::theme(
    plot.background   = ggplot2::element_rect(fill = "white", colour = NA),
    legend.background = ggplot2::element_rect(fill = "white", colour = NA)
  )
```

## Including pre-built figures

Use `knitr::include_graphics(fig("foo.png"))` with the `fig()` helper returning a
project-relative path. This is correct once `knitr::opts_knit$set(root.dir = here::here())`
is set in the setup chunk. Never pass `here::here(...)` absolute paths to
`include_graphics()` when `root.dir` is set: knitr prepends `root.dir` again,
double-rooting the path and breaking resolution.

```r
knitr::opts_knit$set(root.dir = here::here())
fig <- function(file) file.path("output", "figures", file)

# WRONG — double-rooted when root.dir is set
knitr::include_graphics(here::here("output", "figures", "01_flow.png"))

# RIGHT
knitr::include_graphics(fig("01_flow.png"))
```

## Centering in Word

Figure centering is controlled entirely by the `Figure` paragraph style in
`reference.docx` — set `<jc w:val="center"/>` in that style's `<w:pPr>`. Adding
`\centering` or Quarto `:::` div markup to the qmd does not work; Pandoc strips
unsupported attributes for docx output. Table centering requires defence in depth:
flextable's `align = "center"` in `set_table_properties()` AND the `Table` style
in `styles.xml` centred — different Pandoc versions honour one or the other
inconsistently, so both layers are needed.

## Figure captions and cross-references

Label chunks with `#| label: fig-foo` and `#| fig-cap: "..."`, then use `@fig-foo`
in body text. Quarto resolves references to numbered figure links in docx output.
Captions appear below the figure using the `ImageCaption` paragraph style from
`reference.docx`. To change caption font or spacing, edit `ImageCaption` in
`styles.xml` — not inline formatting in the qmd.

```r
#| label: fig-km
#| fig-cap: "Kaplan-Meier survival curves by treatment arm."
#| fig-width: 8
#| fig-height: 5

survminer::ggsurvplot(fit = km_fit, data = df_surv, palette = "Set1")
```
