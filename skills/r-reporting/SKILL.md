---
name: r-reporting
description: >
  Use when producing Word (.docx) deliverables from R analyses —
  consulting reports, manuscript drafts, client handoffs — where tables,
  figures, and page layout must compose cleanly through Quarto -> Pandoc
  -> Word.
  Covers reference.docx authoring (line spacing, justify, Heading 1 page
  breaks, centered figures and tables, page-number footer), the
  gtsummary -> flextable -> docx pipeline, the RDS cache pattern for
  upstream tables, qmd project layout (resources, execute-dir, path
  helpers), and system2(quarto, ...) rendering.
  Triggers: word document, docx, render to word, reference-doc,
  reference docx, flextable, save_as_docx, consulting report, client
  report, statistical report, page break, page numbers in word, figure
  not centered, table not centered.
  Do NOT use for HTML/PDF output — use r-quarto.
  Do NOT use for table styling without a Word context — use r-tables.
  Do NOT use for regulatory TLFs — use r-clinical.
  Do NOT use for interactive HTML reports or Shiny dashboards — use
  r-shiny.
---

# R Reporting

Quarto-to-Word (.docx) pipeline for R consulting deliverables. Pairs with the
`/r-report` command, which scaffolds an opinionated working pipeline into an
existing R project. All R code uses `|>`, `<-`, snake_case, and double quotes.

> **Boundary:** Word/.docx output. For HTML/PDF, use r-quarto. For regulatory
> TLFs, use r-clinical.

(Body content fills in during Task 5.)
