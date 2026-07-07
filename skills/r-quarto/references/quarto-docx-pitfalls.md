# Quarto docx Pitfalls

Traps specific to rendering Quarto `format: docx`. For table/figure conversion
see `word-figure-table-patterns.md`; for reference-doc styling see
`reference-docx-anatomy.md`.

## Quarto YAML doesn't support `!r`

`!r Sys.Date()` is R Markdown only; Quarto treats it as a YAML alias directive,
producing `NA` or a parse error. Pass the value through `params` and resolve it
with inline R in the title block.

```yaml
# WRONG — !r is R Markdown only
date: !r Sys.Date()

# RIGHT — params + inline R
params:
  date: ""
# title block: date: "`r if (nzchar(params$date)) params$date else format(Sys.Date(), '%B %d, %Y')`"
```

## `reference-doc:` path resolves from the qmd, not the project root

Pandoc resolves `reference-doc:` relative to the `.qmd` file. With the qmd in a
subdirectory, co-locate the reference doc or use an explicit relative path.

```yaml
# qmd in inst/templates/, reference doc at project root
format:
  docx:
    reference-doc: ../../custom-reference.docx
```

## `embed-resources: true` is HTML-only

Silently ignored (or warns) for docx — Pandoc embeds images in docx by default,
the format is inherently self-contained. Remove it from the docx block.

```yaml
format:
  docx:
    reference-doc: custom-reference.docx   # not embed-resources
```

## TinyTeX is not needed for docx

`quarto install tinytex` installs a ~250 MB LaTeX distribution required only for
PDF output. A docx-only pipeline has zero LaTeX dependency — `quarto check` is all
you need. Drop TinyTeX from CI/onboarding for Word-only projects.

## `library(quarto)` eager load

The R `quarto` package is NOT required to render — the CLI is sufficient. Calling
`library(quarto)` at the top of a script fails on machines without it (CI, Docker,
colleagues). Render via the CLI (`system2(Sys.which("quarto"), ...)`) and guard
any optional package use with `requireNamespace()`.

```r
if (requireNamespace("quarto", quietly = TRUE)) quarto::quarto_render("report.qmd")
# or: system2(Sys.which("quarto"), args = c("render", shQuote("report.qmd")), wait = TRUE)
```

## `--output` breaks `_files/` for embed-resources HTML

(Relevant when the same render script also emits HTML.) With
`embed-resources: true`, the HTML post-processor looks for `<stem>_files/` keyed
off the *original* filename; `--output report_TS.html` makes it search
`report_TS_files/` and fail. Render with the default name, then rename after exit
0. docx is unaffected, but renaming post-render keeps one code path.

```r
result <- system2(quarto_bin, args = c("render", shQuote(qmd)), wait = TRUE)
if (result == 0L) file.rename("report.docx",
  sprintf("output/report_%s.docx", format(Sys.time(), "%Y%m%d_%H%M%S")))
```

## `knitr::include_graphics()` path resolution

knitr resolves paths from the `.qmd` directory by default, not the project root.
Figures under `output/figures/` at the root fail silently when the qmd is nested.
Set `knitr::opts_knit$set(root.dir = here::here())` in the setup chunk, then use a
project-relative path (don't also wrap in `here::here()` — that double-roots it).

## `cache: true` doesn't invalidate on data change

`cache: true` keys on chunk *code* only; updating the underlying data file does
not bust it. Add `cache.extra` keyed on file mtime, or use `freeze: auto` in
`_quarto.yml` for project-level, source-tied freezing.

```r
#| cache: true
#| cache.extra: !expr digest::digest(file.info(here::here("data", "clean.rds"))$mtime)
df <- readRDS(here::here("data", "clean.rds"))
```
