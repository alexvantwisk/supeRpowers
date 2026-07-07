# Eval: r-reporting

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to structure a report, does the response organize it around the ICH E9(R1) estimand framework and explicit sections (summary, methods, results, limitations) rather than jumping to formatting?
2. Does the response distinguish prespecified from exploratory analyses and address multiplicity, rather than presenting post-hoc findings as confirmatory?
3. For an expensive upstream computation, does the response apply the RDS cache pattern (compute in the analysis script, `saveRDS()` to `output/`, `readRDS()` in the qmd) rather than fitting inside the render?
4. Does the response invoke the Quarto CLI via `system2(quarto_bin, ...)` rather than `quarto::quarto_render()` (so the workflow does not require the R quarto package)?
5. When asked for an audit trail, does the render step rename to a timestamped `report_YYYYMMDD_HHMMSS.docx` after exit 0 (and avoid `--output`)?
6. When the prompt is about docx *styling* — reference-doc, `styles.xml`, flextable, figure centering, page breaks — does the response DEFER to r-quarto rather than producing the styling itself?
7. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%`?
8. When asked to scaffold an end-to-end report pipeline, does the response either invoke `/r-report` or produce the pipeline artifacts (qmd template, render wrapper, `_quarto.yml` layout)?

## Test Prompts

### Happy Path

- "Structure a biostatistics consulting report for a two-arm trial and tell me where the estimand and limitations go." (Must lay out sections, state the estimand components before results, label prespecified/exploratory, address multiplicity — content, not formatting.)
- "My model takes 20 minutes; set up the pipeline so re-rendering the Word report doesn't re-fit it." (Must apply the RDS cache pattern: fit in the analysis script, `saveRDS()`, `readRDS()` in the qmd; render stays cheap.)
- "Wire a `system2(quarto)` render that produces a timestamped docx each run for an audit trail." (Must render via the CLI, rename after exit 0, avoid `--output`.)

### Edge Cases

- "How should I report a subgroup finding my client got excited about but that wasn't in the SAP?" (Must label it exploratory/post-hoc, not confirmatory; discuss multiplicity and uncertainty. Content judgment, not formatting.)
- "Survey has 'Not applicable' entries — how do I handle them in the report tables?" (Must recognize structural missingness: recode to `NA`, document with a missingness audit; do NOT impute.)
- "My report.qmd is in `inst/templates/` and `output/figures/foo.png` doesn't render." (Project layout / path resolution: `resources:` glob + `execute-dir: project`; may point to r-quarto for the knitr `root.dir` detail.)

### Adversarial Cases

- "The figures aren't centered in my Word output and I want 1.5 line spacing." (docx styling. Must defer to r-quarto — reference-doc / styles.xml. Must NOT produce the patching code itself.)
- "Convert this gtsummary table to flextable so it renders in docx." (Word table mechanics. Must defer to r-quarto.)
- "Build a TLF package for FDA submission with Tables 14.1.1 through 14.5.3." (Regulatory TLF. Must defer to r-clinical.)
- "Render this report to PDF with a custom journal template." (PDF + journal template. Must defer to r-quarto.)

### Boundary Tests

- "Fix the reference docx so figures center / Heading 1 breaks pages." boundary -> r-quarto
- "Style a gtsummary table for a JAMA manuscript (HTML output)." boundary -> r-tables
- "Build a CONSORT diagram for my Phase III trial report." boundary -> r-clinical (diagram itself r-visualization)
- "Render to HTML with embedded resources." boundary -> r-quarto

## Success Criteria

- Happy-path prompts produce report *content* structure (estimands, sections, labeling) or *pipeline* orchestration (RDS cache, `system2()` render, timestamped output) — not docx styling.
- Edge cases produce content/statistical judgment (missingness, exploratory labeling) or project-layout reasoning.
- Docx-styling, table-mechanics, TLF, and HTML/PDF prompts are deferred to the correct sibling skill (r-quarto, r-clinical, r-tables) within the first reply.
- Zero `%>%`; every R code block uses `<-`, `|>`, snake_case, and double quotes.
