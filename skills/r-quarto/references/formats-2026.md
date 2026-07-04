# Quarto 2026 formats: Typst, dashboards, brand.yml

Anchored to Quarto 1.9. Confirm exact feature availability with `quarto check`.

## Typst — PDF without LaTeX

Typst is a modern typesetting engine bundled with Quarto; it renders PDF with no
TeX installation.

```yaml
format:
  typst:
    papersize: a4
    margin:
      x: 2cm
      y: 2cm
```

Render: `quarto render report.qmd --to typst`. Use it when you need PDF but do
not want TinyTeX/LaTeX. LaTeX-only features (custom `.sty`, some journal
templates) still require the `pdf` (LaTeX) format.

## Dashboards (`format: dashboard`)

```yaml
format: dashboard
```

Each level-2 header (`##`) becomes a row; code chunks become cards. Add
`#| content: valuebox` to a chunk for a KPI tile, and `.sidebar`/`.tabset`
fenced divs for navigation.

## brand.yml — shared branding

A single `_brand.yml` at the project root defines colours, fonts, and logo;
Quarto applies it across html, dashboard, revealjs, and typst outputs.

```yaml
# _brand.yml
color:
  palette:
    brand-blue: "#0072B2"
  primary: brand-blue
typography:
  base: Inter
logo: assets/logo.png
```

## One-line niceties (Quarto 1.9)

- `llms.txt` output for LLM-friendly site indexes.
- PDF/UA tagging for accessible PDF (`pdf` and `typst`).
