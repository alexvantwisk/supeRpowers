---
name: r-quarto
description: >
  Use when creating Quarto documents, presentations, websites, or books in R.
  Covers YAML configuration, code chunks, cross-references, journal templates,
  and multi-format publishing.
---

# R Quarto

Quarto publishing system for R: documents, presentations, websites, books,
and multi-format output. All code uses base pipe `|>`, `<-` for assignment,
and tidyverse/knitr conventions.

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

Content here.

::: {.incremental}
- Point one
- Point two reveals after click
:::

::: {.notes}
Speaker notes here — not shown to audience.
:::

---

## Columns Layout

:::: {.columns}
::: {.column width="60%"}
Left content
:::
::: {.column width="40%"}
Right content
:::
::::
```

Use `##` for slide breaks. `---` for a blank slide break.

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

```yaml
# _quarto.yml
project:
  type: book
book:
  title: "R Cookbook"
  author: "Jane Smith"
  date: today
  chapters:
    - index.qmd
    - chapters/intro.qmd
    - chapters/models.qmd
  references: references.bib
bibliography: references.bib
```

Cross-references work across chapters. Use `@sec-` for section refs,
`@fig-` for figures. Add `bibliography:` for BibTeX citations (`[@key]`).

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

## Parameters

```yaml
---
params:
  region: "North"
  year: 2024
---
```

```r
#| label: setup
params$region  # "North"
params$year    # 2024
```

Render with overrides:
```bash
quarto render report.qmd -P region:South -P year:2023
```

---

## Multi-Format Output

```yaml
format:
  html:
    toc: true
    theme: flatly
    code-fold: true
  pdf:
    documentclass: scrartcl
    cite-method: biblatex
  docx:
    reference-doc: custom-reference.docx
```

Format-conditional content:

```markdown
::: {.content-visible when-format="html"}
Interactive plot shown in HTML only.
:::

::: {.content-hidden when-format="pdf"}
Not in PDF.
:::
```

---

## Examples

**1. Reproducible report:** "Create a Quarto report with EDA, model results,
and figures that renders to both HTML and PDF."

**2. Presentation:** "Convert this Rmd analysis into a revealjs presentation
with incremental bullets, speaker notes, and ggplot figures."

**3. Documentation site:** "Set up a Quarto website for this R package with
a navbar, sidebar, and GitHub Pages deployment."

**4. Journal manuscript:** "Format this analysis as an Elsevier submission
using quarto-journals extension with cross-references and bibliography."

**5. Parameterized report:** "Generate region-specific summaries from a single .qmd template using Quarto parameters."
