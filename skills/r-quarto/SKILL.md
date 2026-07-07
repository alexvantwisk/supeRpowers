---
name: r-quarto
description: >
  Use when creating Quarto documents, presentations, websites, books, reusable
  templates and format extensions, or Word (.docx) output in R.
  Provides expert guidance on YAML configuration, code chunk options,
  cross-references, journal templates, reference docs (docx/pptx), custom format
  extensions, template partials, docx styling (reference-doc, styles.xml
  patching, flextable tables in Word, figure sizing and centering), revealjs
  slides, multi-format publishing, and parameterized reports.
  Do NOT use for R package vignettes — use r-package-dev instead.
  Do NOT use for Shiny apps — use r-shiny instead.
  Do NOT use for consulting report content, estimands, or the project-pipeline orchestration of a Word deliverable — use r-reporting instead.
when_to_use: >
  Triggers: Quarto, qmd, document, presentation, revealjs, website, book, cross-reference, YAML header, code chunk, journal template, multi-format, format extension, quarto create extension, quarto use template, template partials, Typst template, docx, word document, render to word, reference-doc, reference docx, flextable, figure not centered, table not centered, page break in word, page numbers in word.
paths:
  - "**/*.qmd"
---

# R Quarto

Quarto publishing system for R: documents, presentations, websites, books,
and multi-format output. All code uses base pipe `|>`, `<-` for assignment,
and tidyverse/knitr conventions.

> **Boundary:** All Quarto output including **Word (.docx)** — documents, sites, presentations, template/extension machinery, and docx styling (reference-doc, `styles.xml` patching, flextable tables, figure/table centering, footers). For R package vignettes, use r-package-dev. For the *content and project pipeline* of a consulting/clinical Word deliverable — report sections, estimands, prose helpers, the RDS-cache orchestration, the `/r-report` scaffold — use **r-reporting**. Rule of thumb: producing docx output is here; what goes *in* the report and how the project is wired is r-reporting.

**Agent dispatch:** For R code quality in `.qmd` files, dispatch to **r-code-reviewer** agent.

**Lazy references:**
- Read `references/yaml-config-cheatsheet.md` for complete YAML option reference
- Read `references/cross-reference-syntax.md` for figures, tables, equations, sections
- Read `references/formats-2026.md` for Typst (LaTeX-free PDF), `format: dashboard`, and brand.yml
- Read `references/template-creation.md` for reference docs (docx/pptx), `quarto create extension`, template partials, `quarto use template`, and distributing templates
- Read `references/reference-docx-anatomy.md` for programmatic `styles.xml` patching (units, which styles, xml2 idiom, re-zip)
- Read `references/word-figure-table-patterns.md` for flextable tables in Word, figure sizing, and centering
- Read `references/quarto-docx-pitfalls.md` for docx render traps (`!r`, `reference-doc` path, embed-resources, `library(quarto)`)

---

## Document Types

| Type | Format value | Init command |
|------|-------------|--------------|
| Report / manuscript | `html`, `pdf`, `typst`, `docx` | Author a `.qmd` file directly |
| Dashboard | `dashboard` | Author a `.qmd` with `format: dashboard` |
| Presentation | `revealjs` | `quarto create project` (or author a `.qmd`) |
| Website / blog / book | project type `website` \| `blog` \| `book` | `quarto create project <type>` |

---

## Documents

```yaml
---
title: "Analysis Report"
date: today
format:
  html: { toc: true, code-fold: true }
  pdf: { documentclass: article, geometry: margin=1in }
  docx: { reference-doc: custom-reference.docx }
execute: { echo: false, warning: false, message: false }
---
```

Use `format:` list for multi-format output from a single source. Format-specific
content via `::: {.content-visible when-format="html"}` divs. See
`references/yaml-config-cheatsheet.md` for the full per-format option set.

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

ggplot(mtcars, aes(wt, mpg, colour = factor(cyl))) + geom_point()
```

**Key chunk options:**

| Option | Purpose | Common values |
|--------|---------|---------------|
| `label` | Unique ID, drives cross-refs | `fig-`, `tbl-` prefix required for refs |
| `echo` / `eval` / `output` | Show code / run / show output | `true`, `false` |
| `cache` | Cache result | `true`, `false` |
| `fig-width` / `fig-height` / `fig-cap` | Figure dims (inches) / caption | `7` / `5` / string |

**Global defaults** go in the `execute:` block. Set `cache: true` on expensive
chunks (invalidates on code change) or `freeze: auto` in `_quarto.yml` for
project-wide source-tied freeze; force a rebuild with `quarto render --cache-refresh`.

---

## Presentations (revealjs)

```yaml
format:
  revealjs: { theme: solarized, slide-number: true, chalkboard: true }
```

```markdown
## Slide Title

::: {.incremental}
- Point reveals after click
:::

::: {.notes}
Speaker notes — not shown to audience.
:::
```

`##` starts a slide, `---` a blank break; `:::: {.columns}` / `::: {.column
width="60%"}` for side-by-side layouts.

---

## Websites & Books

Both are project types set in `_quarto.yml`. **Website:** `project: type: website`
+ a `website:` block (`title`, `navbar:`, `sidebar:` with nested `contents:`).
**Book:** `project: type: book` + a `book:` block (`title`, `author`, `chapters:`,
`bibliography:`); cross-refs work across chapters (`@sec-`, `@fig-`, `@tbl-`) with
`[@key]` citations. See `references/yaml-config-cheatsheet.md` for full scaffolds.
Always add `execute: freeze: auto` so pages re-render only on change.

Deploy: `quarto publish gh-pages` (also `quarto-pub`, `netlify`, `connect`).

---

## Using Templates & Extensions

```bash
quarto use template <gh-org>/<repo>   # new project seeded from a template + its example
quarto add <gh-org>/<repo>            # add an extension to an existing project
quarto list extensions                # list installed
quarto remove <name>                  # remove
```

Journal templates are ordinary format extensions: `quarto add quarto-journals/jasa`
(also `elsevier`, `plos`, `agu`, …), then set `format: jasa-pdf`. Utility
extensions: `quarto-ext/fontawesome`, `quarto-ext/lightbox`, `quarto-ext/shinylive`.
Extensions land in `_extensions/` — **commit that directory** so collaborators and
CI don't refetch. Browse: https://quarto.org/docs/extensions/listing-journals.html

---

## Creating Templates

Two mechanisms, chosen by output format. Read `references/template-creation.md`
for full detail (extension anatomy, partial names, Typst, distribution).

**Reference docs (docx / pptx).** Office outputs copy *named styles* from a
reference file. Generate a starting file, edit its styles in Word/PowerPoint,
wire it in:

```bash
quarto pandoc -o custom-reference.docx --print-default-data-file reference.docx
```

```yaml
format:
  docx: { reference-doc: custom-reference.docx }   # pptx uses reference-doc too
```

Edit the *style definitions* (Heading 1, Body Text, Figure, Table…), not local
formatting — Pandoc copies only styles. `.docx` matches paragraph styles; `.pptx`
matches slide *layouts* by name (`Title and Content`, `Section Header`, …). For
docx tables, figures, and code-patched styling, see **Word (docx) output** below.

**Format extensions (`quarto create extension`).** Bundle a reference doc /
partials / metadata into a reusable, distributable unit. Run `quarto create
extension format:docx` (or `format:html|pdf|revealjs`; pick `typst` from the
interactive `quarto create extension format` picker). It fills
`_extensions/<name>/_extension.yml` (`title`, `author`, `version`,
`quarto-required`, `contributes: formats:`) plus a `template.qmd`. Select it as
`format: <name>-docx`; distribute via GitHub for `quarto add` / `quarto use template`.

**Template partials (html / pdf / typst / revealjs — not docx/pptx).** Override
part of Pandoc's template without replacing it:

```yaml
format:
  html: { template-partials: [title-block.html] }
```

Prefer `template-partials:` (or `include-in-header:`) over full `template:`
replacement, which you must then maintain across Quarto upgrades.

---

## Word (docx) output

r-quarto owns Word output end to end. Style it two ways: **edit the reference doc
in Word** (Creating Templates, above) or **patch `styles.xml` in code** for
reproducible/CI styling — `references/reference-docx-anatomy.md` covers units,
which styles, the xml2 idiom, and `zip::zip(mode = "mirror")`. Centering and page
breaks live in styles, never qmd markup — Pandoc strips `\centering` / `:::` divs
for docx.

For native, editable Word **tables**, exit gtsummary/gt through flextable:

```r
my_tbl |> gtsummary::as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center")
```

**Figures:** size via chunk options (`fig-width`/`fig-height`, ~8"×5"), center via
the reference doc's `Figure` style. See `references/word-figure-table-patterns.md`
and `references/quarto-docx-pitfalls.md`. For report *content* and the project
pipeline, use **r-reporting**.

---

## Parameters

Define in YAML with `params:`, access as `params$name` in R chunks.
Override at render: `quarto render report.qmd -P region:South -P year:2023`.

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
| Using `template-partials:` to style docx/pptx output | Office formats have no text template — they copy styles from a reference file | Style docx/pptx via `reference-doc:`; partials are html/pdf/typst/revealjs only |
| Cache not invalidating when data changes but chunk code stays the same | knitr's `cache: true` keys on the chunk code, not the data | Add `#| cache.extra: !expr digest::digest(data)` to key the cache on a data hash; or use `freeze: auto` in `_quarto.yml`, force a rebuild with `quarto render --cache-refresh`, or move heavy data steps into a `targets` pipeline |
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

### Edge Case: Custom Word template for Quarto docx output

**Prompt:** "I want my Quarto reports to use our company's Word styling."

```bash
quarto pandoc -o custom-reference.docx --print-default-data-file reference.docx
# Open in Word, edit the STYLE DEFINITIONS (Heading 1, Body Text, Figure, Table), save
```

Wire it in with `format: docx: { reference-doc: custom-reference.docx }`. For a
reusable version wrap it in `quarto create extension format:docx`; for
code-patched, CI-reproducible styling see `references/reference-docx-anatomy.md`.

**More example prompts:**
- "Create a Quarto report rendering to both HTML and PDF."
- "Convert this Rmd into a revealjs presentation with speaker notes."
- "Format this analysis for Elsevier using quarto-journals extension."
- "Build a reusable Quarto format extension bundling our house docx styling."
- "Override just the title block in my Quarto HTML with a template partial."
