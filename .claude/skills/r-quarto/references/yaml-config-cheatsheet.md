# YAML Configuration Cheatsheet

Complete reference for Quarto YAML front matter and `_quarto.yml` project
configuration. All options use Quarto's native key names.

---

## Document-Level YAML

### Core Metadata

```yaml
---
title: "Document Title"
subtitle: "Optional subtitle"
author:
  - name: Jane Smith
    affiliation: University of R
    email: jane@example.com
  - name: Bob Jones
    affiliation: R Institute
date: today           # or "2024-01-15" or last-modified
date-format: "MMMM D, YYYY"
abstract: |
  Multi-line abstract
  goes here.
keywords: [statistics, R, quarto]
lang: en
---
```

---

## Execution Options (`execute:` block)

Global defaults applied to all chunks unless overridden at chunk level.

```yaml
execute:
  echo: true          # Show source code
  eval: true          # Run code
  output: true        # Show output
  warning: false      # Suppress warnings
  message: false      # Suppress messages
  error: false        # Halt on error (true = show error, continue)
  include: true       # Include chunk in output at all
  cache: false        # Cache chunk results
  freeze: false       # Freeze execution (auto | true | false)
```

**`freeze` vs `cache`:**
- `cache: true` — stored locally in `_cache/`, re-runs on code change
- `freeze: auto` — stored in `_freeze/`, never re-runs unless source changes
  (recommended for project-wide `_quarto.yml` to speed up renders)

```yaml
# In _quarto.yml — freeze all docs unless changed
execute:
  freeze: auto
```

---

## HTML Format Options

```yaml
format:
  html:
    toc: true
    toc-depth: 3
    toc-location: left          # left | right | body
    toc-title: "Contents"
    number-sections: true
    theme: flatly               # cosmo, lumen, pulse, sandstone, etc.
    css: custom.css
    code-fold: true             # Collapsible code blocks
    code-summary: "Show code"
    code-tools: true            # Toggle button for all code
    code-line-numbers: true
    highlight-style: github
    df-print: paged             # kable | tibble | paged | default
    fig-align: center
    fig-width: 7
    fig-height: 5
    self-contained: true        # Embed assets in single HTML file
    embed-resources: true       # Quarto 1.4+ alias for self-contained
    smooth-scroll: true
    anchor-sections: true
    citations-hover: true
    footnotes-hover: true
    link-external-icon: true
    link-external-newwindow: true
```

---

## PDF Format Options

```yaml
format:
  pdf:
    documentclass: article      # article | report | book | scrartcl
    classoption:
      - twocolumn
      - landscape
    geometry:
      - top=30mm
      - left=20mm
      - right=20mm
      - bottom=30mm
    fontsize: 11pt
    mainfont: "Times New Roman"  # Requires xelatex/lualatex
    sansfont: "Helvetica"
    monofont: "Courier New"
    linestretch: 1.5
    toc: true
    toc-depth: 2
    number-sections: true
    colorlinks: true
    linkcolor: blue
    cite-method: biblatex        # natbib | biblatex | citeproc (default)
    keep-tex: false              # Keep intermediate .tex file
    latex-engine: pdflatex       # pdflatex | xelatex | lualatex
    include-in-header: header.tex
    include-before-body: before.tex
```

---

## Word (docx) Format Options

```yaml
format:
  docx:
    reference-doc: custom-reference.docx  # Word template for styles
    toc: true
    toc-depth: 3
    number-sections: false
    highlight-style: github
    fig-width: 6
    fig-height: 4
```

**Creating a reference doc:**
```bash
quarto pandoc -o custom-reference.docx --print-default-data-file reference.docx
```
Open the output file, modify styles (Heading 1, Normal, etc.), save, and
reference it in YAML.

---

## revealjs Presentation Options

```yaml
format:
  revealjs:
    theme: solarized            # default | beige | blood | dark | moon | night | serif | simple | sky | solarized
    slide-number: true          # true | false | c/t | h/v | h.v
    chalkboard: true
    multiplex: false
    incremental: false          # Default incremental for all lists
    smaller: false
    scrollable: false
    center: false               # Vertically center content
    controls: true
    progress: true
    history: true
    preview-links: auto
    transition: slide           # none | fade | slide | convex | concave | zoom
    background-transition: fade
    logo: logo.png
    footer: "My Presentation"
    width: 1600
    height: 900
    margin: 0.1
    min-scale: 0.2
    max-scale: 2.0
    css: custom.css
```

---

## Project-Level `_quarto.yml`

### Website Project

```yaml
project:
  type: website
  output-dir: _site

website:
  title: "Site Name"
  description: "Site description"
  favicon: favicon.ico
  site-url: https://example.com
  repo-url: https://github.com/org/repo
  repo-actions: [edit, issue]
  open-graph: true
  twitter-card: true

  navbar:
    background: primary
    left:
      - href: index.qmd
        text: Home
      - text: Articles
        menu:
          - href: articles/one.qmd
          - href: articles/two.qmd
    right:
      - icon: github
        href: https://github.com/org/repo

  sidebar:
    - title: "Guide"
      style: docked
      contents:
        - section: "Getting Started"
          contents:
            - guide/intro.qmd
            - guide/install.qmd

  page-footer:
    center: "© 2024 My Site"

format:
  html:
    theme: [cosmo, custom.scss]
    toc: true
    code-copy: true
    code-overflow: wrap

execute:
  freeze: auto
```

### Book Project

```yaml
project:
  type: book
  output-dir: _book

book:
  title: "Book Title"
  author: "Author Name"
  date: today
  description: "Brief description"
  site-url: https://example.com/book
  repo-url: https://github.com/org/book
  repo-actions: [edit]
  chapters:
    - index.qmd
    - part: "Part I: Introduction"
      chapters:
        - chapters/intro.qmd
        - chapters/setup.qmd
    - part: "Part II: Advanced"
      chapters:
        - chapters/advanced.qmd
  appendices:
    - appendix/notation.qmd
  references: references.bib

bibliography: references.bib
csl: apa.csl

format:
  html:
    theme: cosmo
  pdf:
    documentclass: scrbook
    geometry:
      - top=25mm
      - outer=25mm
      - inner=30mm
      - bottom=30mm

execute:
  freeze: auto
```

---

## Parameters

```yaml
---
params:
  region: "North"
  year: 2024
  threshold: 0.05
  show_details: false
---
```

Access in R: `params$region`, `params$year`.
Override at render: `quarto render doc.qmd -P region:South -P year:2023`.
For multiple reports: loop over `quarto render` calls with different `-P` flags.

---

## Conditional Content

```markdown
::: {.content-visible when-format="html"}
HTML-only content here.
:::

::: {.content-hidden when-format="pdf"}
Shown in everything except PDF.
:::

::: {.content-visible when-profile="advanced"}
Advanced profile content.
:::
```

**Profiles** in `_quarto.yml`:
```yaml
profiles:
  default: [base]
  group:
    - [base, advanced]
```

Render with profile: `quarto render --profile advanced`.

---

## Custom Formats and Profiles

```yaml
# _quarto.yml — define format aliases
format:
  html: default
  my-html:
    inherits: html
    toc: false
    code-fold: false

# Document YAML
format: my-html
```

**Multiple format profiles:**
```bash
quarto render                    # Uses default profile
quarto render --profile print    # Uses print profile options
```

---

## Bibliography and Citations

```yaml
bibliography: references.bib    # BibTeX file
csl: apa.csl                    # Citation Style Language file
link-citations: true
```

In-text citations: `[@smith2020]`, `@smith2020`, `[-@smith2020]` (suppress author).

BibTeX entries in `references.bib` are auto-populated when using Zotero
integration (`zotero: true` in YAML) or by using RStudio's citation tool.
