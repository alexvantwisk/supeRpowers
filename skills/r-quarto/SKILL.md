---
name: r-quarto
description: >
  Use when creating Quarto documents, presentations, websites, or books in R.
  Provides expert guidance on YAML configuration, code chunk options,
  cross-references, journal templates, revealjs slides, multi-format
  publishing, and parameterized reports.
  Triggers: Quarto, qmd, document, presentation, revealjs, website, book,
  cross-reference, YAML header, code chunk, journal template, multi-format.
  Do NOT use for R package vignettes — use r-package-dev instead.
  Do NOT use for Shiny apps — use r-shiny instead.
---

# R Quarto

Quarto publishing system for R: documents, presentations, websites, books,
and multi-format output. All code uses base pipe `|>`, `<-` for assignment,
and tidyverse/knitr conventions.

> **Boundary:** Quarto documents, sites, and presentations. For R package vignettes, use r-package-dev instead. For Word/.docx deliverables (reference docx, page breaks, footers, figure/table centering), use **r-reporting**.

**Agent dispatch:** For R code quality in `.qmd` files, dispatch to **r-code-reviewer** agent.

**Lazy references:**
- Read `references/yaml-config-cheatsheet.md` for complete YAML option reference
- Read `references/cross-reference-syntax.md` for figures, tables, equations, sections

---

## Document Types

| Type | Format value | Init command |
|------|-------------|--------------|
| Report / manuscript | `html`, `pdf`, `docx` | `quarto create document` |
| Presentation | `revealjs` | `quarto create presentation` |
| Website | project type `website` | `quarto create project website` |
| Blog | project type `blog` | `quarto create project blog` |
| Book | project type `book` | `quarto create project book` |

---

## Documents

```yaml
---
title: "Analysis Report"
author: "Jane Smith"
date: today
format:
  html:
    toc: true
    code-fold: true
  pdf:
    documentclass: article
    geometry: margin=1in
  docx:
    reference-doc: template.docx
execute:
  echo: false
  warning: false
  message: false
---
```

Use `format:` list for multi-format output from a single source. Format-specific
content via `:::  {.content-visible when-format="html"}` divs.

---

## Code Chunks

Use `#|` syntax for chunk options (Quarto native — preferred over knitr `{}` options):

```r
#| label: fig-mtcars
#| fig-cap: "MPG vs weight by cylinders"
#| fig-width: 7
#| fig-height: 4
#| echo: false
#| cache: true

library(ggplot2)

mtcars |>
  ggplot(aes(wt, mpg, colour = factor(cyl))) +
  geom_point() +
  labs(colour = "Cylinders")
```

**Key chunk options:**

| Option | Purpose | Common values |
|--------|---------|---------------|
| `label` | Unique ID, drives cross-refs | `fig-`, `tbl-` prefix required for refs |
| `echo` | Show code | `true`, `false`, `fenced` |
| `eval` | Run code | `true`, `false` |
| `output` | Show output | `true`, `false`, `asis` |
| `cache` | Cache result | `true`, `false` |
| `fig-width` / `fig-height` | Figure dims (inches) | `7` / `5` |
| `fig-cap` | Figure caption | string |

**Global defaults** go in the `execute:` block in YAML front matter.

**Caching:** Set `cache: true` on expensive chunks. Invalidates when chunk code
changes. Use `freeze: auto` in `_quarto.yml` for project-wide freeze (re-runs
only on change). Clear cache with `quarto render --cache-refresh`.

---

## Presentations (revealjs)

```yaml
---
title: "My Talk"
format:
  revealjs:
    theme: solarized
    slide-number: true
    chalkboard: true
    incremental: false
---
```

```markdown
## Slide Title

::: {.incremental}
- Point one
- Point two reveals after click
:::

::: {.notes}
Speaker notes — not shown to audience.
:::
```

Use `##` for slide breaks, `---` for blank breaks. Use `:::: {.columns}` /
`::: {.column width="60%"}` for side-by-side layouts.

---

## Websites

`_quarto.yml` at project root:

```yaml
project:
  type: website

website:
  title: "My Site"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: about.qmd
        text: About
  sidebar:
    contents:
      - section: "Analysis"
        contents:
          - analysis/eda.qmd
          - analysis/model.qmd

format:
  html:
    theme: cosmo
    toc: true
```

Deploy: `quarto publish gh-pages`, `quarto publish quarto-pub`, `quarto publish netlify`, or `quarto publish connect`.

---

## Books

In `_quarto.yml`, set `project: type: book` with a `book:` block containing
`title`, `author`, `chapters:` (list of `.qmd` files), and `bibliography:`.
Cross-references work across chapters: `@sec-`, `@fig-`, `@tbl-`. Use BibTeX
citations via `[@key]`.

---

## Journal Templates (Extensions)

```bash
# Install a journal extension
quarto add quarto-journals/jasa       # JASA
quarto add quarto-journals/elsevier   # Elsevier
quarto add quarto-journals/plos       # PLOS ONE
quarto add quarto-journals/agu        # AGU
```

After installing, set `format: jasa-pdf` (or the journal-specific key) in YAML.
Extensions land in `_extensions/` — commit this directory.

Browse templates: https://quarto.org/docs/extensions/listing-journals.html

---

## Extensions

```bash
quarto add <gh-org>/<repo>    # Install from GitHub
quarto list extensions        # List installed
quarto remove <name>          # Remove
```

Common extensions: `quarto-ext/fontawesome`, `quarto-ext/lightbox`,
`quarto-ext/shinylive`, `grantmcdermott/quarto-revealjs-clean`.

---

## Parameters & Multi-Format Output

Define in YAML with `params:`, access as `params$name` in R chunks.
Override at render: `quarto render report.qmd -P region:South -P year:2023`.
List multiple formats under `format:` (html, pdf, docx) with per-format options.
Use conditional divs: `::: {.content-visible when-format="html"}`.

---

## Verification

After render: check `quarto check` passes, cross-references resolve (no `?fig-` artifacts), multi-format output opens correctly.

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| YAML indentation errors (tabs or wrong nesting) | Quarto YAML parser fails silently or produces unexpected output | Use spaces only (2-space indent); validate with `quarto check` before rendering |
| Using knitr-style `{r, eval=FALSE}` chunk options | Quarto ignores old-style knitr options in `{}` header; code runs unexpectedly | Use `#| eval: false` (hashpipe syntax) inside the chunk body |
| Cross-reference labels missing type prefix | `@fig-plot` only works if the chunk label is `fig-plot`; bare labels produce broken refs | Always prefix labels: `fig-` for figures, `tbl-` for tables, `sec-` for sections |
| Forgetting `embed-resources: true` for self-contained HTML | Shared HTML files have broken images/CSS because assets are separate files | Add `embed-resources: true` under `format: html:` for portable single-file output |
| PDF output fails without LaTeX installation | Quarto calls `pdflatex`/`xelatex` which is not bundled | Install TinyTeX: `quarto install tinytex` or `tinytex::install_tinytex()` |
| Installing extensions via `install.packages()` instead of `quarto add` | Quarto extensions are not R packages; CRAN install does nothing | Use `quarto add <gh-org>/<repo>` from the terminal |
| Cache not invalidating when data changes but chunk code stays the same | `cache: true` keys on chunk code only; stale results persist | Use `cache.extra` to depend on data hash, or use `freeze: auto` in `_quarto.yml` instead |
| Rewriting entire document structure when user asked for one fix | Scope creep — user wants a YAML tweak, not a full document redesign | Make the minimal targeted change; suggest broader restructuring only if asked |

## Examples

### Happy Path: Parameterized report with render command

**Prompt:** "Generate region-specific summaries from a single .qmd template."

```yaml
# Input — report.qmd YAML header
---
title: "Regional Summary"
params:
  region: "North"
  year: 2024
format:
  html:
    toc: true
    embed-resources: true
execute:
  echo: false
---
```

```r
# In code chunk — access params
df_filtered <- sales |>
  dplyr::filter(region == params$region, year == params$year)
```

```bash
# Output — render for each region
quarto render report.qmd -P region:North -P year:2024
quarto render report.qmd -P region:South -P year:2024
```

### Edge Case: Cross-reference broken by missing fig- prefix

**Prompt:** "My @fig-scatter reference shows '?fig-scatter' in the output."

```markdown
# WRONG — chunk label missing required fig- prefix; cross-ref breaks
{r scatter}
#| fig-cap: "MPG vs weight"
plot(mtcars$wt, mtcars$mpg)

See @fig-scatter for details.
<!-- renders as: See ?fig-scatter for details. -->

# CORRECT — label starts with fig- so Quarto links it
{r fig-scatter}
#| fig-cap: "MPG vs weight"
plot(mtcars$wt, mtcars$mpg)

See @fig-scatter for details.
<!-- renders as: See Figure 1 for details. -->
```

**More example prompts:**
- "Create a Quarto report rendering to both HTML and PDF."
- "Convert this Rmd into a revealjs presentation with speaker notes."
- "Format this analysis for Elsevier using quarto-journals extension."
