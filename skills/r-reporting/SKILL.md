---
name: r-reporting
description: >
  Use when producing Word (.docx) deliverables from R analyses —
  consulting reports, manuscript drafts, client handoffs — where tables,
  figures, and page layout must compose cleanly through Quarto -> Pandoc
  -> Word.
  Covers reference.docx authoring (line spacing, justify, Heading 1 page
  breaks, centered figures and tables, page-number footer), the
  gtsummary -> flextable -> docx pipeline, the RDS cache pattern for
  upstream tables, qmd project layout (resources, execute-dir, path
  helpers), and system2(quarto, ...) rendering.
  Triggers: word document, docx, render to word, reference-doc,
  reference docx, flextable, save_as_docx, consulting report, client
  report, statistical report, page break, page numbers in word, figure
  not centered, table not centered.
  Do NOT use for HTML/PDF output — use r-quarto.
  Do NOT use for table styling without a Word context — use r-tables.
  Do NOT use for regulatory TLFs — use r-clinical.
  Do NOT use for interactive HTML reports or Shiny dashboards — use
  r-shiny.
---

# R Reporting

Quarto-to-Word (.docx) pipeline for R consulting deliverables. Pairs with the
`/r-report` command, which scaffolds an opinionated working pipeline into an
existing R project. All R code uses `|>`, `<-`, snake_case, and double quotes.

> **Boundary:** Word/.docx output. For HTML/PDF, use r-quarto. For regulatory
> TLFs, use r-clinical.

**Lazy references:**
- Read `references/reference-docx-anatomy.md` for styles.xml structure, twentieths-of-a-point units, which Pandoc styles to patch (Normal, docDefaults, Heading 1, Figure, Table, ImageCaption), and the docx-zip "mirror mode" requirement.
- Read `references/quarto-docx-pitfalls.md` for the Quarto/Pandoc/knitr landmines: `!r` not in YAML, `--output` breaking `_files/`, `library(quarto)` eager load, `include_graphics` path resolution, `gtsummary` 2.x argument hygiene.
- Read `references/word-figure-table-patterns.md` for `as_flex_table()`, the RDS cache pattern, `gt -> PNG` fallback, conditional formatting in flextable, figure sizing and ggplot theming for print.
- Read `references/report-content-structure.md` for biostatistical consulting report sections, the ICH E9(R1) estimand framework, prespecification/exploratory labeling, multiplicity (PICOTA), missing-data handling (MCAR/MAR/MNAR), and uncertainty communication. Use when drafting *content*, not formatting.

**Agent dispatch:** For R/qmd code quality, dispatch to **r-code-reviewer**. For statistical content of inline tables, dispatch to **r-statistician**.

**MCP integration (when R session available):**
- Before writing a table-loading chunk: `btw_tool_env_describe_data_frame` on the cached object to confirm shape and column types.
- When uncertain about a flextable function: `btw_tool_docs_help_page` to check the current API.
- When patching `reference.docx`: `btw_tool_docs_help_page` for `xml2` namespace handling.

---

## Pipeline Mental Model

The R analysis writes figures (PNG) and tables (RDS or CSV) to `output/`. The qmd reads those artifacts and assembles the report. Pandoc renders the qmd to docx using a custom `reference.docx` for styles. Path resolution differs by tool: R chunks resolve from the project root via `here::here()`; Pandoc resolves images relative to the qmd; knitr's `include_graphics()` resolves from the qmd unless `opts_knit$set(root.dir = ...)` overrides. Reconciling these three roots is most of the work.

---

## Project Layout

| Project type | qmd location | Reference docx | Render script |
|---|---|---|---|
| R package | `inst/templates/report.qmd` | `inst/templates/reference.docx` | `R/render_report.R` or `analysis/05_report.R` |
| Analysis project | `report/report.qmd` | `report/reference.docx` | `analysis/05_report.R` |
| targets pipeline | `report/report.qmd` | `report/reference.docx` | a `tar_target` calling `system2(quarto, ...)` |

Wherever the qmd lives, three things must align:

1. **`_quarto.yml`** at the project root specifies `execute-dir: project` and a `resources:` glob covering `output/figures/*.png` and `output/tables/*.html`. Without `execute-dir`, `here::here()` fails inside chunks.
2. **The qmd's YAML** specifies `resource-path: [".", "../.."]` (or appropriate relative path back to the project root) so Pandoc can find figures referenced as `output/figures/foo.png`.
3. **The setup chunk** sets `knitr::opts_knit$set(root.dir = here::here())` so `knitr::include_graphics()` resolves correctly.

---

## Path Helpers in the qmd

```r
fig <- function(file) file.path("output", "figures", file)   # project-relative for Pandoc
tbl <- function(file) here::here("output", "tables",  file)  # absolute for R chunks
mod <- function(file) here::here("output", "models",  file)  # absolute for R chunks
```

`fig()` returns project-relative paths so Pandoc / Quarto's resource resolver can find figures under both `quarto render` and `quarto preview --output-dir <tmp>`. `tbl()` and `mod()` return absolute paths because they are read by R chunks (`readRDS`, `read_csv`) which run from the project root.

---

## Tables in Word

`as_flex_table()` is the canonical exit from gtsummary. Apply set_table_properties for autofit + centered alignment:

```r
library(flextable)

readRDS(tbl("01_table_one.rds")) |>
  as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all")
```

**The RDS cache pattern.** Build the table object in the analysis script, save it to `output/tables/`, read it back in the qmd:

```r
# In 04_model.R — runs once, cached
tbl_one <- trial |>
  gtsummary::tbl_summary(by = trt) |>
  gtsummary::add_p() |>
  gtsummary::bold_labels()
saveRDS(tbl_one, here::here("output", "tables", "01_table_one.rds"))
```

```r
# In report.qmd — fast, deterministic
readRDS(tbl("01_table_one.rds")) |>
  as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center")
```

This avoids re-running gtsummary inside the qmd render context (slower, can hit different package versions).

For gt-only features (gtExtras sparklines, embedded plots) that flextable can't represent, fall back to `gtsave("table.png", zoom = 2)` and `knitr::include_graphics()` — labelled as a deliberate fallback, not a default.

---

## Figures in Word

YAML defaults: `fig-width: 8`, `fig-height: 5`, `dpi: 150`. For wide multipanel patchwork plots, use 8" × 7" or 8" × 9". Heights above 9" risk pagination glitches.

ggplot theming for print: white backgrounds (`theme_minimal(base_size = 11) + theme(plot.background = element_rect(fill = "white", colour = NA))`), opaque legends, contrast-safe palettes (viridis, Color Brewer), font size ≥ 10pt.

**Figure centering happens in the reference.docx Figure style, not in the qmd.** If figures aren't centering, regenerate `reference.docx` — don't add `\centering` or alignment markup to the qmd (Pandoc strips it for docx output).

For pre-built figures from upstream scripts:

```r
knitr::include_graphics(fig("01_attrition_flow.png"))
```

Requires `knitr::opts_knit$set(root.dir = here::here())` in the setup chunk.

---

## Inline Prose Helpers

When values are spliced into running prose via inline ``` `r ...` ``` chunks, the *operator* (`=`, `≤`, `<`) belongs in the helper, not in the surrounding text. Writing ``p `r fmt_p(x)` `` and reading the result as "p 0.042" is awkward; appending "or smaller" to fake an inequality is worse. The fix is two helpers:

```r
fmt_p        <- function(p, d = 3) { ... }                    # "0.042" or "<0.001"
fmt_p_inline <- function(p, op = "=", d = 3) { ... }          # "= 0.042", "≤ 0.002", "< 0.001"
```

The full implementations ship in the `/r-report` template; the key invariant is that `fmt_p_inline()` collapses the operator to `<` whenever `p < 10^(-d)` so prose never renders "p ≤ < 0.001".

Usage:

| Context | Helper | Renders |
|---|---|---|
| A single test in prose | ``p `r fmt_p_inline(t$p)` `` | "p = 0.487" or "p < 0.001" |
| The maximum across a corrected family | ``p `r fmt_p_inline(max(p_holm), op = "≤")` `` | "p ≤ 0.002" |
| Inside a parenthesised list of three p-values | ``BMI `r fmt_p(...)` `` | "BMI 0.231" — context already implies `=` |
| Inside a table cell | `fmt_p()` (no operator) | "0.042" — column header carries the meaning |

**Why two helpers, not one with `op = ""`.** Tables and parenthesised lists collapse better with bare values; running prose reads better with the operator attached. Keeping them separate prevents call sites from accidentally producing a leading space (`" 0.042"`).

---

## Reference.docx

Pandoc applies styles from a `reference.docx` you supply via YAML:

```yaml
format:
  docx:
    reference-doc: reference.docx   # resolved relative to the qmd's directory
```

Pandoc's default reference docx ships with neutral defaults. To get the five style invariants (1.5 line spacing + full justify + Calibri 11pt body, Heading 1 starts a new page bold centered, figures centered, tables centered, simple page-number footer), patch the styles.xml inside the docx zip.

**Generate via the bundled script:**

```r
source(here::here("analysis", "make_reference_doc.R"))
```

The script extracts Pandoc's default `reference.docx`, patches `styles.xml` (Normal, docDefaults, Heading 1, Figure, Table, ImageCaption) and `word/footer1.xml` (centered PAGE field), and re-zips with `mode = "mirror"`. Read `references/reference-docx-anatomy.md` for the XML internals and parameterisation arguments.

---

## Render Workflow

Use `system2()` against the Quarto CLI, not the R `quarto` package. The R package is not required for rendering:

```r
quarto_bin <- Sys.which("quarto")
if (nzchar(quarto_bin) == 0L) stop("Quarto CLI not on PATH.")

result <- system2(
  quarto_bin,
  args = c(
    "render", shQuote(input_qmd),
    "--to", "docx",
    "--execute-dir", shQuote(here::here())
  ),
  stdout = "", stderr = "",
  wait = TRUE
)
if (result != 0L) stop("quarto render failed.")
```

**Timestamped output for audit trail.** After a successful render, rename the default output file to `report_YYYYMMDD_HHMMSS.docx` and copy to `output/` so each render is preserved.

**Don't use `--output`.** With `embed-resources` HTML it breaks `_files/` resolution. With docx it works but the bundled wrapper takes the safer post-render rename path.

---

## Verification

After render: exit code 0; the docx file exists and is non-empty (a bare scaffold renders to ~10-15 KB; real reports with figures and tables go well past 50 KB); opening the docx shows figures embedded, tables centered, Heading 1 sections starting on new pages, page numbers in footer. Run `file output/report_*.docx` — should report `Microsoft Word 2007+`.

---

## Gotchas

| Trap | Why It Fails | Fix |
|---|---|---|
| `date: !r Sys.Date()` in YAML | `!r` is R Markdown only; Quarto doesn't honor it | Use a plain string in `params` and resolve via inline R in the title field |
| `--output report_TS.html` with `embed-resources: true` | Post-process still looks for `report_files/`, not `report_TS_files/` | Render with default name; `file.rename()` after exit 0 |
| `library(quarto)` in `00_setup.R` | Fails on machines without the R quarto package; not required for CLI render | `if (requireNamespace("quarto", quietly = TRUE)) library(quarto)` |
| `knitr::include_graphics(fig("foo.png"))` resolves from qmd dir | knitr defaults to qmd's directory, not project root | Set `knitr::opts_knit$set(root.dir = here::here())` in setup chunk |
| `tbl_summary(by = NULL)` in gtsummary 2.x | gtsummary 2.x errors on NULL passed to `by`/`include` | Build args list conditionally; `rlang::exec(!!!args)` (NOT `do.call`) |
| `geom_errorbarh()` in ggplot 4.0 | Deprecated; loud warnings | `geom_errorbar(orientation = "y")` or `coord_flip()` |
| Re-zipping reference.docx with flat directory | Word rejects the file | `zip::zip(..., mode = "mirror")` preserves the directory tree |
| `cache: true` not invalidating on data change | `cache: true` keys on chunk code only | Use `cache.extra = digest::digest(data_path)` or `freeze: auto` in `_quarto.yml` |
| `embed-resources: true` in docx YAML | HTML-only; ignored or warned for docx | Drop it. Pandoc embeds images in docx by default |
| Figure centering markup in qmd (`\centering`, ::: divs) | Pandoc strips for docx | Center via the Figure style in `reference.docx` |

---

## Examples

### Happy Path: scaffold a docx pipeline

**Prompt:** "Set up a Quarto-to-Word pipeline for my consulting project."

Invoke `/r-report`. The command detects project type, scaffolds `report.qmd`, `make_reference_doc.R`, and a render script, generates the reference docx with minimalist defaults, and runs the first render.

### Edge Case: figures rendered but not centered

**Prompt:** "My figures show up in the Word output but they're left-aligned."

Diagnose: Pandoc routes images through the `Figure` paragraph style. Centering is a styles.xml fix, not a qmd fix. Regenerate `reference.docx` (the bundled `make_reference_doc.R` patches the Figure style by default) and re-render.

### Boundary: complex table with gtExtras sparklines

**Prompt:** "I have a gt table with `gt_sparkline()` and `gt_plt_bar()` columns — how do I get it into Word?"

flextable cannot represent gtExtras inline graphics. Use the PNG fallback:

```r
gt::gtsave(my_gt_tbl, here::here("output", "tables", "10_summary.png"), zoom = 2)
# In qmd:
knitr::include_graphics(fig("10_summary.png"))
```

Document this as a deliberate fallback. For ordinary gtsummary tables, prefer `as_flex_table()`.
