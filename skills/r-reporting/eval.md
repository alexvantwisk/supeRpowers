# Eval: r-reporting

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. Does the response specify `format: docx` (not `format: word_document` from R Markdown) when defining the YAML output target?
2. Does the response use `reference-doc:` for Word styling, NOT `--reference-doc` CLI args or `pandoc` invocation directly?
3. When tables flow into Word, does the response use `as_flex_table()` as the canonical exit ramp from gtsummary (not `gtsave("table.docx")` for non-trivial tables)?
4. Does the response invoke the Quarto CLI via `system2(quarto_bin, ...)` rather than `quarto::quarto_render()` (so the workflow does not require the R quarto package)?
5. Does any reference.docx-patching code use BOTH `docDefaults/pPrDefault` AND the `Normal` style as patch targets for body styling?
6. Does any reference.docx-patching code re-zip with `mode = "mirror"` (or equivalent explicit relative-paths approach) — never flattening the docx directory tree?
7. When figures need to be centered in Word, is the fix applied in the reference.docx Figure style — not in the qmd via `\centering` or markdown alignment markup?
8. Does the response use `|>` exclusively and `<-` for assignment, with zero instances of `%>%`?
9. When `--output` is mentioned, does the response warn against using it with `embed-resources` HTML and prefer post-render `file.rename()`?
10. When asked to scaffold an end-to-end Word pipeline, does the response either invoke `/r-report` or produce the four artifacts the command would (qmd template, render wrapper, make_reference_doc.R, _quarto.yml block)?

## Test Prompts

### Happy Path

- "I want to render my analysis report to Word for a client. The figures should be centered and every section should start on a new page. Walk me through the setup." (Must explain the reference.docx mechanism, point to or invoke `make_reference_doc.R`, set `<w:pageBreakBefore/>` on Heading 1, set `<w:jc w:val="center"/>` on the Figure style, and use `system2()` to render.)
- "Set up a Quarto-to-docx pipeline for my consulting project: tables from gtsummary, figures from ggplot, simple page numbers in the footer." (Must scaffold `report.qmd` with `format: docx` + `reference-doc:`, an analysis script using `system2(quarto, ...)`, and `make_reference_doc.R` for the styling.)

### Edge Cases

- "My Heading 1 sections aren't paginating in the Word output even though my YAML has `number-sections: true`." (Must diagnose: `number-sections` controls numbering, not pagination. Fix is `<w:pageBreakBefore/>` on the Heading 1 style in `reference.docx`. Must mention regenerating the reference docx via `make_reference_doc.R`.)
- "I have a complex gt table with sparkline columns from gtExtras — how do I get it into Word?" (Must recognize that flextable can't represent gtExtras sparklines. Recommended fallback: `gtsave("table.png", zoom = 2)` then `knitr::include_graphics()`. Must label this as a deliberate fallback, not a default.)
- "My report.qmd is in `inst/templates/` and `output/figures/foo.png` doesn't render — Pandoc says file not found." (Must diagnose path resolution: Pandoc resolves images relative to the qmd. Fix is `resource-path:` in the YAML or `_quarto.yml`'s `resources:` glob plus `execute-dir: project`. May also mention `knitr::opts_knit$set(root.dir = here::here())` for `include_graphics()`.)

### Adversarial Cases

- "Render this report to PDF using LuaLaTeX with a custom journal template and bibliography." (PDF + journal template + bibliography. Must defer to r-quarto. Must NOT scaffold a docx pipeline or invoke `make_reference_doc.R`.)
- "Build a TLF package for FDA submission with Tables 14.1.1 through 14.5.3 in the standard regulatory format." (Regulatory TLF. Must defer to r-clinical. May mention flextable for table mechanics but must NOT produce a generic consulting-report scaffold.)
- "Make my Shiny dashboard render a Word report when the user clicks a button." (Shiny app + downloadHandler. Must defer to r-shiny for the reactive plumbing. May reference `make_reference_doc.R` and `as_flex_table()` if the inner render uses Quarto, but the orchestration belongs in r-shiny.)

### Boundary Tests

- "Render to HTML with embedded resources." boundary -> r-quarto
- "Style a gtsummary table for a JAMA manuscript (HTML output)." boundary -> r-tables
- "Build a CONSORT diagram for my Phase III trial report." boundary -> r-clinical (and r-visualization for the diagram itself)
- "Convert this Word report to PDF." boundary -> NOT r-reporting (out of scope; suggest `quarto render --to pdf` and refer to r-quarto)

## Success Criteria

- All happy-path prompts produce a working scaffold or a clear walk-through citing the reference.docx mechanism, `as_flex_table()`, and `system2()` rendering.
- Edge-case prompts produce diagnostic reasoning grounded in styles.xml or path-resolution mechanics, not surface-level guesses.
- Adversarial prompts are deferred to the correct sibling skill within the first reply.
- Zero `%>%` in any code block.
- Every R code block uses `<-`, `|>`, snake_case, and double quotes.
