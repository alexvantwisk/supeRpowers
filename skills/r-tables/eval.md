# Eval: r-tables

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the skill include a source note or footnote on summary tables that describes the statistics displayed (e.g., "Mean (SD); n (%)")?
2. Does the skill avoid hardcoding column widths when the output targets multiple formats (HTML, PDF, Word)?
3. When asked to create a bar chart or plot from table data, does the skill defer to r-visualization?
4. When asked to embed a table in a Shiny app with reactive filtering, does the skill defer to r-shiny?
5. When asked for an FDA-submission demographics table, does the skill defer to r-clinical?
6. Does the skill use `|>` and `<-` exclusively (never `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "Create a summary Table 1 for the iris dataset grouped by Species, showing mean and SD for each numeric variable, using gtsummary."
- "Build a gt table of regression coefficients from a linear model with confidence intervals, p-values, and bolded significant rows."

### Edge Cases

- "Merge two gt tables side by side -- one for the treatment group and one for the control group -- into a single table with a spanning header." (side-by-side gt merge -- must use `gt::cols_merge()` or manual column binding with group spanners, not two separate rendered tables)
- "Apply conditional formatting to a gt table: cells above the 90th percentile in green, below the 10th in red, with a continuous color gradient for values in between." (conditional formatting with color scales -- must use `gt::data_color()` with a palette function, not manual cell-by-cell styling)
- "Export the same gt table to HTML for a website, PDF for a journal, and Word for collaborators. Make sure it looks right in all three." (multi-format export -- must NOT hardcode pixel widths or HTML-only styling; must use relative widths or format-aware logic)

### Adversarial Cases

- "Plot a bar chart showing the mean values from this summary table, with error bars for the confidence intervals." (visualization request -- must defer to r-visualization; rendering a bar chart as a gt table or using gt's plotting features as a substitute is a failure)
- "Create a reactable table inside my Shiny app that updates when the user changes a filter dropdown." (Shiny-embedded reactive table -- must defer to r-shiny for the app wiring; may advise on reactable configuration but must NOT generate server/ui code)
- "Create a demographics Table 1 for my Phase III clinical trial that meets FDA CDISC standards with stratification by site and treatment arm." (regulatory table -- must defer to r-clinical for CDISC compliance, stratification rules, and regulatory formatting requirements)

### Boundary Tests

- "Visualize these summary statistics as a grouped bar chart with custom colors." (boundary -> r-visualization)
- "Display this table in a Shiny module with row selection and editing capabilities." (boundary -> r-shiny)
- "Format the adverse events table for our FDA submission package with MedDRA coding." (boundary -> r-clinical)

## Success Criteria

- Summary tables MUST include a source note or footnote describing the summary statistics shown (e.g., "Median (IQR)" or "n (%)"). A summary table with no statistical annotation is a failure.
- Multi-format output MUST NOT use hardcoded pixel widths, `px()` column sizing, or HTML-only CSS that breaks in PDF/Word. The code must either use relative units or include format-detection logic.
- Conditional formatting MUST use programmatic approaches (`data_color()`, `tab_style()` with conditions) rather than manual per-cell styling for more than 3 cells.
- Side-by-side table merges MUST produce a single unified table object with proper spanning headers, not two tables rendered adjacently.
- Bar chart or plot requests MUST be deferred to r-visualization; the skill must NOT use `gt_plt_bar()` or `gtExtras` plotting as a substitute for a proper ggplot2 visualization when the user asks for a "chart" or "plot."
- Shiny-embedded table prompts MUST defer to r-shiny for the reactive layer; the skill may recommend `reactable` or `DT` configuration but must NOT generate `shinyApp()`, `server`, or `ui` code.
- Regulatory/FDA/CDISC table requests MUST defer to r-clinical; the skill must NOT attempt CDISC-compliant formatting without clinical-domain guidance.
- All generated R code MUST use `|>`, `<-`, snake_case, and double quotes.
