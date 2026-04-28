# Eval: r-visualization

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the skill apply a non-default theme (e.g., `theme_minimal()`, `theme_bw()`, or a custom theme) for any figure described as publication-quality?
2. Does the skill avoid producing misleading axis scales (e.g., truncated y-axis on bar charts, dual y-axes without explicit user request)?
3. When asked to build a Shiny dashboard with interactive plots, does the skill defer to r-shiny?
4. When asked to create a formatted summary table, does the skill defer to r-tables?
5. When rendering 10k+ points, does the skill address overplotting (via alpha, jitter, hex bins, or density)?
6. Does the skill use `|>` and `<-` exclusively (never `%>%` or `=` for assignment)?
7. Does the skill prefer `ggsurvfit` over `survminer` for new KM code?
8. Does the skill use `scales::label_*` over hand-rolled `formatC` / `sprintf` for axis labels?
9. Does the skill prefer `geom_col()` over `geom_bar(stat = "identity")`?
10. When asked for markdown / bold / italic in axis or title text, does the skill route through `ggtext::element_markdown()`?
11. When asked for a raincloud plot, does the skill use `ggdist`?
12. When asked for ridgeline / stacked density plots, does the skill use `ggridges`?
13. For >100k points, does the skill suggest `geom_hex()` / aggregation / `plot_ly` WebGL rather than dropping a static `plotly::ggplotly`?
14. For a multi-panel paper figure, does the skill reach for `patchwork` and use `&` for composition-wide theme?
15. Does the skill use `linewidth` (not `size`) on line geoms in any new code (ggplot2 ≥3.4 convention)?

## Test Prompts

### Happy Path

- "Create a scatter plot of mpg vs wt from mtcars, colored by cyl, with a smooth line and publication-ready styling."
- "Make a faceted histogram of Sepal.Length by Species from iris, with a clean theme and labeled axes."
- "Build a raincloud plot of Sepal.Length by Species using ggdist."
- "Make a ridgeline plot of diamond price by cut using ggridges."
- "Compose a 2x2 paper figure of four scatter plots with a shared legend at the bottom using patchwork."
- "Highlight the top three time series in this 30-line plot using gghighlight."
- "Add markdown formatting (bold, italic, superscript units) to my axis title using ggtext."
- "Plot a Kaplan-Meier survival curve with a risktable using ggsurvfit."
- "Swap my plot's colors to the NEJM palette using ggsci."
- "Make my static ggplot interactive for an HTML report using ggiraph."
- "Animate a scatter plot over years using gganimate."
- "Build nested facets (Region > Country) using ggh4x."

### Edge Cases

- "Plot 150,000 GPS coordinate points on a map-like scatter. The points overlap heavily." (overplotting -- must use alpha transparency, hex bins, or 2D density; raw `geom_point()` on 150k points is a failure)
- "Create a 4x3 faceted plot where each panel has a different y-axis range and the panels are ordered by descending median." (free scales + custom ordering -- must use `facet_wrap(scales = "free_y")` with a reordered factor, not fixed scales that obscure variation)
- "Build a custom ggplot2 theme for my lab that uses Palatino font, specific hex colors for a 5-level discrete palette, and adjusts all text sizes." (custom theme creation -- must produce a reusable `theme_*()` function, not inline theme calls)

### Adversarial Cases

- "Build a Shiny dashboard with a sidebar that lets users pick variables and dynamically updates a scatter plot and a histogram." (interactive dashboard -- must defer to r-shiny; generating a standalone ggplot script is wrong, generating a full Shiny app inline is also wrong)
- "Create a formatted comparison table showing mean, SD, and p-value for each variable by treatment group." (formatted data table -- must defer to r-tables; rendering this as a ggplot table or text grob is a failure)
- "Create a Kaplan-Meier survival curve for the overall survival endpoint in my Phase III oncology trial, with number-at-risk table and median survival annotation." (clinical-context KM plot -- must flag r-clinical for trial-specific requirements like stratification and regulatory formatting; may assist with the ggplot mechanics but must not handle the clinical analysis)

### Boundary Tests

- "Build a reactive Shiny app that shows a bar chart filtered by user input." (boundary -> r-shiny)
- "Create a gt table with sparkline columns summarizing trends." (boundary -> r-tables)
- "Plot the Kaplan-Meier curve for my FDA submission with stratified confidence bands." (boundary -> r-clinical)
- "Build a Shiny dashboard with an animated bar chart that updates on user input." (boundary -> r-shiny)
- "Render a styled table with sparkline columns using gt." (boundary -> r-tables)
- "Generate a Kaplan-Meier curve formatted to FDA submission standards with stratification." (boundary -> r-clinical for analytical layer; this skill handles ggplot mechanics only)

## Success Criteria

- Publication figures MUST use a non-default theme; any figure described as "publication-ready" or "for a manuscript" that uses the default grey ggplot2 theme is a failure.
- Bar charts MUST start the y-axis at zero unless the user explicitly requests otherwise; a truncated y-axis on a bar chart is a failure.
- Dual y-axes MUST NOT be generated unless the user explicitly requests them; unsolicited `sec_axis()` is a failure.
- Datasets with 10k+ points MUST include an overplotting mitigation strategy in the code; raw `geom_point()` without alpha, jitter, or aggregation is a failure.
- Faceted plots with heterogeneous ranges MUST use `scales = "free"` or `scales = "free_y"/"free_x"` as appropriate; forcing identical scales that compress most panels is a failure.
- Custom theme requests MUST produce a reusable function (e.g., `theme_lab <- function(...) { theme(...) + ... }`), not one-off inline `theme()` calls scattered in the plot code.
- Shiny dashboard prompts MUST be deferred to r-shiny; the skill must NOT generate `shinyApp()`, `ui`, or `server` code.
- Formatted table prompts MUST be deferred to r-tables; the skill must NOT render tabular data as a plot-based table.
- Clinical trial KM plots MUST flag r-clinical for the analytical and regulatory layer; the skill may provide ggplot2/ggsurvfit mechanics but must NOT perform the clinical analysis (stratification choices, endpoint definitions, regulatory formatting).
- All generated R code MUST use `|>`, `<-`, snake_case, and double quotes.
- New KM code MUST use `ggsurvfit`. Generating `survminer::ggsurvplot` for a new request without explicit user preference is a failure.
- Markdown text in titles/labels MUST route through `ggtext::element_markdown()` (or `element_textbox`); using `parse = TRUE` plotmath instead is a failure when markdown is requested.
- Raincloud requests MUST use `ggdist::stat_halfeye` / `stat_dots` (with optional `geom_boxplot`); a violin-only or box-only plot is a failure.
- Ridgeline requests MUST use `ggridges`; stacking densities with `position = "stack"` is a failure.
- Multi-panel paper-figure requests MUST use `patchwork` (or `cowplot::plot_grid` only when explicitly asked); using `gridExtra::grid.arrange` for new code is a failure.
- Composition-wide theming MUST use `&`, not `+`. Applying `theme()` with `+` to a patchwork object and expecting it on every panel is a failure.
- Line / segment / smooth geoms MUST use `linewidth` for line widths in any new code (ggplot2 ≥3.4); using `size` on lines is a failure.
- Highlight requests SHOULD use `gghighlight`; manually filtering and re-plotting twice is acceptable but suboptimal.
