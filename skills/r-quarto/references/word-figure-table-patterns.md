# Figures & Tables in Quarto docx Output

How to make figures and tables render correctly in Quarto's `format: docx`. All
styling that persists across renders lives in the `reference-doc` (see
`reference-docx-anatomy.md`); this file covers the R-side conversion and sizing.

## gtsummary / gt → flextable → docx

`flextable` produces *native, editable* Word tables (real docx table XML), so it
is the canonical exit for tables destined for docx. `gtsummary::as_flex_table()`
converts a gtsummary object; apply `set_table_properties()` for autofit +
centered layout, then set a readable size and bold the header:

```r
library(flextable)

my_tbl |>                                   # a gtsummary object
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all") |>
  flextable::bold(part = "header")
```

Print the flextable as the chunk's output and Quarto embeds it in the docx.

## gt → docx native (gtsave)

`gt::gtsave("table.docx")` works for simple tables with plain-text cells. For
conditional cell colours, summary footers, or spanners with custom fonts, styling
fidelity degrades — gt's docx exporter doesn't implement its full HTML pipeline.
Prefer `as_flex_table()` for anything non-trivial; `gtsave()` to docx is fine for
quick previews.

## gt → PNG fallback

When a table uses features flextable can't represent — `gtExtras::gt_sparkline()`,
`gt_plt_bar()`, embedded plots — save a high-res PNG (`zoom = 2`) and include it
with `knitr::include_graphics()`. This is a deliberate fallback: it loses
accessibility and copy-paste of values. Mark it with a comment.

```r
# Deliberate PNG fallback — flextable cannot represent gtExtras inline graphics
gt::gtsave(my_sparkline_tbl, "12_sparklines.png", zoom = 2)
knitr::include_graphics("12_sparklines.png")
```

## gtsummary 2.x argument hygiene

gtsummary 2.x errors on `by = NULL` / `include = NULL` passed explicitly (1.x
ignored them). Build args conditionally with `purrr::compact()` and dispatch via
`rlang::exec(!!!args)` — not `do.call()`, which forces lazy promises early and
breaks gtsummary's NSE column-type detection.

```r
args <- purrr::compact(list(data = data, by = stratifier, include = keep_vars))
tbl  <- rlang::exec(gtsummary::tbl_summary, !!!args)
```

## Conditional formatting in flextable

flextable's formula selectors generate native docx cell properties (cleaner than
gt's inline-HTML `tab_style()` for Word). Use `bold()`, `color()`, `bg()` with
`i = ~<condition>`; the tilde formula is evaluated against the flextable data, so
column names must match. Calls are additive.

```r
tbl_ft |>
  flextable::bold(i = ~p_value < 0.05, j = "p_value") |>
  flextable::color(i = ~estimate < 0, j = "estimate", color = "#B22222")
```

## Multi-table merging

For side-by-side tables, `gtsummary::tbl_merge()` before `as_flex_table()` handles
column-label dedup natively. Within a flextable, `merge_h()` / `merge_v()` span
cells and `flextable::compose()` builds rich header cells.

```r
gtsummary::tbl_merge(list(tbl_a, tbl_b), tab_spanner = c("**A**", "**B**")) |>
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center")
```

## Figure sizing for letter / A4

Set execute defaults in `_quarto.yml`, override per chunk. Good starting points:
8" × 5" single-panel, 8" × 7" two-row patchwork, 8" × 9" three-row. Heights above
9" risk pagination glitches in Word.

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
patchwork::wrap_plots(p1, p2, p3, ncol = 1)
```

## ggplot theming for print

Word embeds figures on a white page — set an explicit opaque white background so
they don't show a transparent wash. Use `base_size >= 11` for legibility after
scaling, and colour-blind-safe palettes (viridis, Color Brewer).

```r
ggplot2::ggplot(df, ggplot2::aes(week, hba1c, colour = arm)) +
  ggplot2::geom_line() +
  ggplot2::scale_colour_brewer(palette = "Set1") +
  ggplot2::theme_minimal(base_size = 11) +
  ggplot2::theme(
    plot.background   = ggplot2::element_rect(fill = "white", colour = NA),
    legend.background = ggplot2::element_rect(fill = "white", colour = NA)
  )
```

## Centering in Word (styles, not markup)

Figure centering is controlled entirely by the `Figure` paragraph style in the
reference doc — set `<w:jc w:val="center"/>` in its `<w:pPr>`. Adding `\centering`
or a Quarto `:::` div to the qmd does **not** work; Pandoc strips unsupported
attributes for docx. Table centering wants defence in depth: flextable's
`align = "center"` **and** the `Table` style centred in `styles.xml`, since
different Pandoc versions honour one or the other. See `reference-docx-anatomy.md`.

## Figure captions and cross-references

Label chunks `#| label: fig-foo` + `#| fig-cap: "..."`, then reference with
`@fig-foo`. Quarto resolves these to numbered figure links in docx. Captions
render below the figure using the `ImageCaption` style from the reference doc —
change caption font/spacing by editing `ImageCaption` in `styles.xml`, not in the
qmd.

## Including pre-built figures from disk

When figures are produced by an upstream script and live under the project root
while the qmd is in a subdirectory, knitr resolves paths from the *qmd* directory
by default and misses them. Set `knitr::opts_knit$set(root.dir = here::here())` in
the setup chunk, then use a project-relative path — never also wrap it in
`here::here()`, which double-roots the path.

```r
knitr::opts_knit$set(root.dir = here::here())
knitr::include_graphics(file.path("output", "figures", "01_flow.png"))  # RIGHT
```
