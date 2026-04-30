# Quarto-to-Docx Pitfalls

## Quarto YAML doesn't support !r

`!r Sys.Date()` is R Markdown only; Quarto treats it as a YAML alias directive,
producing `NA` or a parse error. Pass the date through `params` with a default
empty string and resolve it via inline R in the title block.

```yaml
# WRONG — !r is R Markdown only
date: !r Sys.Date()

# RIGHT — params + inline R
params:
  date: ""
# In qmd title block: date: "`r if (nzchar(params$date)) params$date else format(Sys.Date(), '%B %d, %Y')`"
```

## --output breaks _files/ for embed-resources HTML

With `embed-resources: true`, the HTML post-processor looks for `<stem>_files/`
keyed off the *original* filename; `--output report_TS.html` causes it to search
for `report_TS_files/` and fail. Render with the default name, then rename after
exit 0. This only affects HTML; for docx `--output` is fine, but the bundled
wrapper renames post-render for consistency.

```r
# WRONG — breaks embed-resources asset bundling
system2(quarto_bin, args = c("render", shQuote(qmd), "--output", "report_TS.html"))

# RIGHT — render default name, rename after exit 0
result <- system2(quarto_bin, args = c("render", shQuote(qmd)), wait = TRUE)
if (result == 0L) file.rename(
  here::here("report.html"),
  here::here(sprintf("output/report_%s.html", format(Sys.time(), "%Y%m%d_%H%M%S")))
)
```

## library(quarto) eager load

The R `quarto` package is NOT required to render documents; the CLI is sufficient.
Calling `library(quarto)` at the top of a setup script fails on machines without
the package — CI, Docker images, colleague environments. Use `system2()` directly
and guard any optional quarto-package usage with `requireNamespace()`.

```r
# WRONG — fails if R quarto package is absent
library(quarto)
quarto_render("report.qmd")

# RIGHT — guard or skip; use CLI directly
if (requireNamespace("quarto", quietly = TRUE)) quarto::quarto_render("report.qmd")
# or just: system2(Sys.which("quarto"), args = c("render", shQuote("report.qmd")), wait = TRUE)
```

## knitr::include_graphics path resolution

knitr resolves paths from the `.qmd` directory by default, not the project root.
When figures live in `output/figures/` at the root and the qmd is in a
subdirectory, paths fail silently. Fix: set `knitr::opts_knit$set(root.dir =
here::here())` in the setup chunk.

```r
# WRONG — resolves from qmd dir, misses project-root figures
knitr::include_graphics("output/figures/01_flow.png")

# RIGHT — set root.dir first, then use project-relative path
knitr::opts_knit$set(root.dir = here::here())
knitr::include_graphics(file.path("output", "figures", "01_flow.png"))
```

## gtsummary 2.x argument hygiene

gtsummary 2.x errors on `include = NULL` or `by = NULL` passed explicitly (where
1.x ignored them). Build the args list conditionally with `purrr::compact()` and
dispatch via `rlang::exec(!!!args)` — NOT `do.call()`, which forces lazy promises
prematurely and breaks gtsummary's NSE column-type detection.

```r
# WRONG — errors in gtsummary 2.x when by / include are NULL
gtsummary::tbl_summary(data, by = NULL, include = NULL)

# RIGHT — build args conditionally, dispatch with rlang::exec
args <- purrr::compact(list(
  data    = data,
  by      = stratifier,       # NULL entries dropped by compact()
  include = if (length(keep_vars) > 0) keep_vars else NULL
))
tbl <- rlang::exec(gtsummary::tbl_summary, !!!args)
```

## ggplot 4.0 deprecations

`geom_errorbarh()` is deprecated in ggplot2 4.0. Switch to
`geom_errorbar(orientation = "y")` or add `coord_flip()` to a regular
`geom_errorbar()`.

```r
# WRONG — deprecated since ggplot2 4.0
ggplot(df, aes(y = label, xmin = lo, xmax = hi)) + geom_errorbarh()

# RIGHT — orientation argument
ggplot(df, aes(x = label, ymin = lo, ymax = hi)) +
  geom_errorbar(orientation = "y")
```

## cache: true does not invalidate on data change

`cache: true` keys on chunk *code* only; updating the underlying data file does
not bust the cache. Add `cache.extra` keyed on file mtime, or use `freeze: auto`
in `_quarto.yml` for project-level source-tied caching.

```r
#| cache: true
#| cache.extra: !expr digest::digest(file.info(here::here("data", "clean.rds"))$mtime)
df <- readRDS(here::here("data", "clean.rds"))
```

```yaml
# _quarto.yml — invalidates when the qmd source changes
execute:
  freeze: auto
```

## reference.docx path resolution

Pandoc resolves `reference-doc:` relative to the `.qmd` file, not the project
root. With the qmd in `inst/templates/`, place `reference.docx` in the same
directory or use a relative path back up (`../../reference.docx`).

```yaml
# WRONG — reference.docx at root, qmd in inst/templates/
format:
  docx:
    reference-doc: reference.docx

# RIGHT — co-locate, or use explicit relative path
format:
  docx:
    reference-doc: ../../reference.docx   # back to project root
```

## embed-resources is HTML-only

`embed-resources: true` is silently ignored (or warns) for docx output. Pandoc
embeds images in docx by default — the format is inherently self-contained. Remove
this option from your docx format block; it adds confusion without effect.

```yaml
# WRONG — no effect for docx, may warn
format:
  docx:
    embed-resources: true

# RIGHT — omit it
format:
  docx:
    reference-doc: reference.docx
```

## TinyTeX is not needed for docx

`quarto install tinytex` installs a ~250 MB LaTeX distribution required only for
PDF output. docx-only pipelines have zero dependency on LaTeX. Remove TinyTeX
from CI and onboarding docs for Word-only reporting projects.

```bash
# WRONG — wastes 250 MB for a docx pipeline
quarto install tinytex

# RIGHT — verify Quarto + Pandoc are present; that's all docx needs
quarto check
```

## Stale R library state between Rscript invocations

Symptom: one render succeeds, the next fails with "no package called 'dplyr'".
Cause: a parallel package install left the library in an inconsistent state, or
DESCRIPTION `Imports` diverged from installed packages. Do not attempt to repair
the library from inside the analysis pipeline. Capture `sessionInfo()`, restore
with `pak::pak()` or `renv::restore()`, and re-run.

## "Not applicable" as structural NA

Survey skip patterns produce `"Not applicable"` rather than `NA`. This is
structural missingness — do NOT impute it, which conflates skip logic with random
missingness and inflates `tbl_summary()` counts. Replace with `NA` and document
explicitly with a missingness audit.

```r
df <- df |>
  dplyr::mutate(dplyr::across(
    dplyr::where(is.character),
    ~ dplyr::na_if(.x, "Not applicable")   # document: structural NA replacement
  ))
naniar::miss_var_summary(df) |>
  dplyr::filter(n_miss > 0) |>
  print(n = Inf)
```
