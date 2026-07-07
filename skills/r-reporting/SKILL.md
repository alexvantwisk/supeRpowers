---
name: r-reporting
description: >
  Use when producing a consulting or clinical Word (.docx) report as a
  deliverable in R — assembling the report's content and wiring the reproducible
  project pipeline that renders it through Quarto.
  Covers report structure and statistical content (sections, the ICH E9(R1)
  estimand framework, prespecification vs exploratory labeling, multiplicity,
  missing-data handling, uncertainty communication, inline prose helpers), the
  qmd project layout (resources, execute-dir, path helpers), the RDS cache
  pattern for expensive upstream tables/models, and system2(quarto, ...)
  rendering with a timestamped audit trail.
  Do NOT use for docx mechanics — reference-doc styling, styles.xml patching,
  flextable tables, figure sizing/centering, docx render traps — use r-quarto.
  Do NOT use for HTML/PDF output — use r-quarto.
  Do NOT use for table styling outside a report context — use r-tables.
  Do NOT use for regulatory TLFs — use r-clinical.
when_to_use: >
  Triggers: consulting report, client report, statistical report, biostatistics report, report structure, report sections, estimand, prespecification, multiplicity adjustment, missing data reporting, uncertainty communication, RDS cache, cached table, expensive model render, docx report pipeline, client deliverable, render report pipeline.
---

# R Reporting

The consulting/clinical Word (.docx) report as a *deliverable*: what goes in it
and the reproducible project pipeline that produces it. Pairs with the
`/r-report` command, which scaffolds an opinionated working pipeline into an
existing R project. All R code uses `|>`, `<-`, snake_case, and double quotes.

> **Boundary:** report *content* + *project pipeline orchestration*. The docx
> *mechanics* — reference-doc styling, `styles.xml` patching, flextable tables in
> Word, figure sizing/centering, docx render traps — belong to **r-quarto**. For
> HTML/PDF, use r-quarto. For regulatory TLFs, use r-clinical. Rule of thumb: what
> goes *in* the report and how the project is wired is here; how docx output is
> produced and styled is r-quarto.

**Lazy references:**
- Read `references/report-content-structure.md` for biostatistical consulting report sections, the ICH E9(R1) estimand framework, prespecification/exploratory labeling, multiplicity (PICOTA), missing-data handling (MCAR/MAR/MNAR), and uncertainty communication. Use when drafting *content*.
- For docx styling, flextable tables, figure centering, and render traps, use the **r-quarto** skill (`reference-docx-anatomy.md`, `word-figure-table-patterns.md`, `quarto-docx-pitfalls.md`).

**Agent dispatch:** For R/qmd code quality, dispatch to **r-code-reviewer**. For statistical content of inline tables, dispatch to **r-statistician**.

**MCP integration (when R session available):**
- Before writing a table-loading chunk: `btw_tool_env_describe_data_frame` on the cached object to confirm shape and column types.
- When drafting statistical prose: `btw_tool_docs_help_page` to confirm a model's summary API before splicing values into text.

---

## Pipeline Mental Model

The analysis writes artifacts — figures (PNG) and tables/models (RDS) — to
`output/`. The qmd reads those artifacts and assembles the report; Quarto renders
it to docx. Keeping computation in the analysis scripts (not the qmd) makes
renders fast, deterministic, and reproducible. The qmd is an *assembler*, not a
place to fit models.

---

## Project Layout

| Project type | qmd location | Reference docx | Render script |
|---|---|---|---|
| R package | `inst/templates/report.qmd` | `inst/templates/reference.docx` | `R/render_report.R` |
| Analysis project | `report/report.qmd` | `report/reference.docx` | `analysis/05_report.R` |
| targets pipeline | `report/report.qmd` | `report/reference.docx` | a `tar_target` calling `system2(quarto, ...)` |

Three things must align (the docx path/resolution details are r-quarto's — see
`quarto-docx-pitfalls.md` there):

1. **`_quarto.yml`** at the project root sets `execute-dir: project` and a
   `resources:` glob covering `output/figures/*.png` and `output/tables/*`.
   Without `execute-dir`, `here::here()` fails inside chunks.
2. **The qmd's YAML** sets `resource-path` back to the project root so figures
   referenced as `output/figures/foo.png` resolve.
3. **The setup chunk** sets `knitr::opts_knit$set(root.dir = here::here())`.

---

## Path Helpers in the qmd

```r
fig <- function(file) file.path("output", "figures", file)   # project-relative for Pandoc
tbl <- function(file) here::here("output", "tables",  file)  # absolute for R chunks
mod <- function(file) here::here("output", "models",  file)  # absolute for R chunks
```

`fig()` returns project-relative paths so Quarto's resource resolver finds
figures under both `quarto render` and `quarto preview`. `tbl()` and `mod()`
return absolute paths because R chunks (`readRDS`, `read_csv`) run from the
project root.

---

## The RDS Cache Pattern

Build expensive objects (models, gtsummary tables) in the analysis script, save
to `output/`, and read them back in the qmd. This avoids re-running slow
computation inside the render context (slower, and can drift with package
versions between runs).

```r
# 04_model.R — runs once, cached
tbl_one <- trial |>
  gtsummary::tbl_summary(by = "trt") |>
  gtsummary::add_p() |>
  gtsummary::bold_labels()
saveRDS(tbl_one, here::here("output", "tables", "01_table_one.rds"))
```

```r
# report.qmd — fast, deterministic; convert to a Word table (flextable = r-quarto)
readRDS(tbl("01_table_one.rds")) |>
  gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center")
```

The `as_flex_table()` styling belongs to r-quarto (`word-figure-table-patterns.md`);
here the point is the *caching dataflow*.

---

## Inline Prose Helpers

When values are spliced into running prose via inline ``` `r ...` ``` chunks, the
*operator* (`=`, `≤`, `<`) belongs in the helper, not the surrounding text.
Writing ``p `r fmt_p(x)` `` and reading "p 0.042" is awkward. The fix is two
helpers:

```r
fmt_p        <- function(p, d = 3) { ... }                    # "0.042" or "<0.001"
fmt_p_inline <- function(p, op = "=", d = 3) { ... }          # "= 0.042", "≤ 0.002", "< 0.001"
```

The full implementations ship in the `/r-report` template; the key invariant is
that `fmt_p_inline()` collapses the operator to `<` whenever `p < 10^(-d)` so
prose never renders "p ≤ < 0.001".

| Context | Helper | Renders |
|---|---|---|
| A single test in prose | ``p `r fmt_p_inline(t$p)` `` | "p = 0.487" or "p < 0.001" |
| Maximum across a corrected family | ``p `r fmt_p_inline(max(p_holm), op = "≤")` `` | "p ≤ 0.002" |
| Inside a table cell | `fmt_p()` (no operator) | "0.042" — header carries the meaning |

---

## Report Content

The *substance* of a statistical/consulting report — not its formatting. Read
`references/report-content-structure.md` for the full treatment; the essentials:

- **Structure:** executive summary → methods → results → limitations, each
  Heading 1 a self-contained section.
- **Estimands (ICH E9(R1)):** state the target of estimation (population,
  variable, intercurrent-event strategy, summary measure) before the numbers.
- **Prespecified vs exploratory:** label every analysis; never present a
  post-hoc finding as confirmatory.
- **Multiplicity:** declare the correction family and method (PICOTA framing).
- **Missing data:** classify (MCAR/MAR/MNAR), state the handling, run a
  sensitivity analysis when MNAR is plausible.
- **Uncertainty:** report intervals, not just point estimates; avoid "proves".

For the statistical validity of a specific model, dispatch **r-statistician**.

---

## Render Workflow

Use `system2()` against the Quarto CLI, not the R `quarto` package (not required
for rendering):

```r
quarto_bin <- Sys.which("quarto")
if (nzchar(quarto_bin) == 0L) stop("Quarto CLI not on PATH.")

result <- system2(
  quarto_bin,
  args = c("render", shQuote(input_qmd), "--to", "docx",
           "--execute-dir", shQuote(here::here())),
  wait = TRUE
)
if (result != 0L) stop("quarto render failed.")
```

**Timestamped output for an audit trail.** After exit 0, rename the output to
`report_YYYYMMDD_HHMMSS.docx` and copy to `output/` so each render is preserved.
Render with the default name, then `file.rename()` — don't use `--output` (see
r-quarto's `quarto-docx-pitfalls.md`).

The `/r-report` scaffold ships `make_reference_doc.R` (generates the styled
reference doc — the styling technique itself is documented in r-quarto),
`render_to_docx.R`, and `report_template.qmd`.

---

## Verification

After render: exit code 0; the docx exists and is non-empty (a bare scaffold is
~10–15 KB; a real report with figures/tables goes past 50 KB); `file
output/report_*.docx` reports `Microsoft Word 2007+`. Confirm the *content*
invariants — estimands stated, analyses labeled prespecified/exploratory,
uncertainty reported. For visual docx checks (centering, page breaks), see r-quarto.

---

## Gotchas

| Trap | Why It Fails | Fix |
|---|---|---|
| Fitting models / running gtsummary inside the qmd | Slow, non-deterministic renders; version drift | Compute in the analysis script, cache to RDS, read in the qmd |
| `library(quarto)` in `00_setup.R` | Fails on machines without the R quarto package; not required for CLI render | `if (requireNamespace("quarto", quietly = TRUE)) library(quarto)` |
| Presenting a post-hoc result as confirmatory | Misleads on evidence strength | Label prespecified vs exploratory; state the estimand |
| Imputing structural missingness ("Not applicable") | Conflates skip logic with random missingness, inflates counts | Recode to `NA`, document with a missingness audit |
| Reaching here for docx styling / flextable / centering | Those are docx mechanics | Use **r-quarto** |

---

## Examples

### Happy Path: scaffold a docx report pipeline

**Prompt:** "Set up a Quarto-to-Word pipeline for my consulting project."

Invoke `/r-report`. It detects project type, scaffolds `report.qmd`, the render
script, and the reference doc, and runs the first render. Content structure comes
from `references/report-content-structure.md`; docx styling from r-quarto.

### Edge Case: expensive upstream model

**Prompt:** "My model takes 20 minutes; I don't want to re-run it on every render."

Fit it in the analysis script, `saveRDS()` the fitted object (or its summary
table) to `output/`, and `readRDS()` in the qmd. The render then re-reads a cached
artifact instead of re-fitting — fast and reproducible.

### Boundary: docx styling request

**Prompt:** "My figures aren't centered / I need 1.5 line spacing in the Word output."

That's docx styling — route to **r-quarto** (`reference-docx-anatomy.md`,
`word-figure-table-patterns.md`). r-reporting owns the report's content and the
render pipeline, not the reference-doc styles.

**More example prompts:**
- "Structure a biostatistics consulting report with estimands and a limitations section."
- "Cache my gtsummary tables to RDS so re-rendering the Word report is fast."
- "Wire up a `system2(quarto)` render with timestamped docx output for an audit trail."
