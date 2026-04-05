# Eval: r-quarto

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Do all code chunk options use the `#|` hashpipe syntax (e.g., `#| fig-width: 6`) and never the deprecated knitr-style `{r, fig.width=6}` chunk headers?
2. Does the response use Quarto-native YAML keys (`format:`, `fig-width`, `code-fold`) and never R Markdown equivalents (`output: html_document`, `fig.width`)?
3. When asked to write an R package vignette, does the skill produce an explicit deferral naming r-package-dev instead of generating vignette YAML?
4. Does a Quarto website or book example include `execute: freeze: auto` (or `freeze: true`) in `_quarto.yml`?
5. When cross-references are used, does the output use Quarto-native `@fig-`, `@tbl-`, `@eq-` syntax and never raw LaTeX `\ref{}` or `\autoref{}`?
6. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%`?
7. When asked about parameterized reports, does the response show BOTH the YAML `params:` declaration AND the render-time parameter passing (via `quarto_render()` or CLI `--execute-params`)?

## Test Prompts

### Happy Path

- "Create a parameterized Quarto report with `region` and `year` parameters that renders to both HTML and PDF, with a table of contents and code folding in HTML."
- "Set up a Quarto book project with three chapters, a shared bibliography, and GitHub Pages deployment."

### Edge Cases

- "I need a parameterized quarterly report that renders to HTML, PDF, and Word simultaneously. Each format needs different figure sizing and HTML gets an interactive DT table that PDF and Word skip. Show the YAML and a programmatic render for Q1-Q4." (Must use `format:` list with per-format options and `::: {.content-visible when-format="html"}` divs.)
- "Set up cross-references across chapters in a Quarto book: figures in chapter 2 referenced from chapter 4, and an equation in the appendix referenced from chapter 1." (Must use `@fig-`, `@tbl-`, `@sec-` syntax with correctly prefixed labels; must note cross-chapter refs require the `book` project type.)
- "I want to submit a paper using the JASA (Journal of the American Statistical Association) Quarto journal template. Show me setup and YAML." (Must use `quarto add quarto-journals/jasa`, not `install.packages()`; must mention committing `_extensions/`.)

### Adversarial Cases

- "Write a vignette for my R package `tidywidgets` that will render with `devtools::build_vignettes()` and appear in `browseVignettes()`." (Package vignette. Must defer to r-package-dev. Must NOT produce `VignetteIndexEntry`, `VignetteEngine`, or DESCRIPTION edits.)
- "Build me an interactive Shiny dashboard with reactive filtering and multiple tabs from this Quarto document." (Shiny app. Must defer to r-shiny. May mention `quarto-ext/shinylive` but must NOT architect reactive server logic, `observeEvent()`, or `renderPlot()` chains.)
- "Create a publication-quality multi-panel figure with custom theme, secondary axes, annotations, and inset plots, then embed it in my Quarto doc." (Complex ggplot2. Must defer to r-visualization for the plot construction. May handle chunk options like `#| fig-width` and `#| fig-cap` but must NOT produce multi-geom ggplot2 code with custom `theme()` calls.)

### Boundary Tests

- "Add a vignette to my existing R package that appears in `browseVignettes()`." boundary -> r-package-dev
- "Create a dashboard with Shiny server logic and reactive filtering inside a `.qmd` file." boundary -> r-shiny
- "Build a complex ggplot2 visualization with `patchwork` layout, custom scales, and `ggrepel` labels, then embed it in my report." boundary -> r-visualization

## Success Criteria

- No output contains deprecated knitr-style chunk options: `fig.width`, `fig.height`, `fig.cap`, `results=`, `message=` inside `{r}` headers. All chunk options use `#|` prefix.
- All YAML frontmatter uses `format:` key (not `output:`); sub-keys use kebab-case (`fig-width`, not `fig.width`). Any output containing `output: html_document` is a failure.
- Vignette request produces a deferral naming r-package-dev and does NOT contain `VignetteIndexEntry`, `VignetteEngine`, or `usethis::use_vignette()`.
- Shiny dashboard request produces a deferral naming r-shiny and does NOT contain `shinyApp()`, `server <- function()`, `observeEvent()`, or reactive expression definitions.
- Complex ggplot request defers plot construction to r-visualization and does NOT contain multi-layer ggplot2 code with `theme()` customization, `sec.axis`, or `annotation_custom()`.
- Website/book scaffolds include `freeze: auto` or `freeze: true` under `execute:` in `_quarto.yml`; omitting freeze is a failure.
- Parameterized report response includes BOTH a `params:` YAML block AND a programmatic render call; omitting either is a failure.
- Journal template edge case uses `quarto add` (not `install.packages()`) and mentions committing `_extensions/`.
- No output contains `%>%`, `=` for top-level assignment, or camelCase identifiers.
