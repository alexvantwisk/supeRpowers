# r-reporting Skill + /r-report Command — Design Spec

**Date:** 2026-04-30
**Author:** Alexander van Twisk (with Claude)
**Status:** Approved (brainstorm complete; pending implementation plan)
**Target:** new `skills/r-reporting/` skill and `commands/r-report.md` command in the `supeRpowers` Claude Code plugin

---

## Goal

Make the Quarto-to-Word pipeline a one-command setup, with reusable plugin content that teaches Claude how to repair, extend, and explain it. After this ships, an R consulting project should be able to run `/r-report`, get a working `report.qmd` + `reference.docx` + render wrapper, and produce a clean, minimalist `.docx` deliverable on first render.

The friction motivating this spec is concrete: in the Robyn Blain MHSc consulting project (Apr 29-30, 2026), 28+ render iterations were needed to settle the docx output, including a hand-rolled 153-line `make_reference_doc.R` script that unzips the Pandoc reference docx, patches `styles.xml` with `xml2`, and re-zips. The plugin's existing `r-quarto` skill mentions `reference-doc:` in one line and never explains how to build one. `r-tables` shows the `gtsummary → as_flex_table → flextable::save_as_docx` exit ramp but doesn't tie it into a project-wide workflow. The lessons captured in that project's `tasks/lessons.md` (Quarto YAML doesn't support `!r`; `--output` breaks `_files/`; `library(quarto)` eager load; `knitr::include_graphics` path resolution; gtsummary 2.x `include = NULL`) are all reusable but uncodified.

## Non-Goals

- **Editorial structure of consulting reports** (CONSORT/STROBE sections, ICH E9(R1) estimands, prespecification documentation, missing-data templates). The compass artifact in `docs/compass_artifact_wf-485b38b3-0576-4506-a6bf-efe7d5866ca2_text_markdown.md` is the seed for that work; it is **deferred to a separate brainstorm** and gets its own spec when ready.
- HTML/PDF format tuning beyond a passing mention. `r-quarto` already covers multi-format basics.
- Posit Connect / `quarto publish` workflows (already in `r-quarto`).
- Shiny apps, dashboards, or interactive HTML reports (`r-shiny`).
- Regulatory TLF formatting (`r-clinical`).
- Microsoft Word automation via COM/AppleScript. Pandoc reference.docx is the only styling mechanism.

## Scope decisions (locked)

| # | Question | Decision |
|---|---|---|
| 1 | Skill or command or both? | **Both.** New `r-reporting` skill (mechanics) + new `/r-report` command (orchestrator that scaffolds the pipeline). |
| 2 | Compass artifact integration | **Out of scope this spec.** Deferred to a separate `r-consulting-report` (or similar) brainstorm. Mentioned only as a forward pointer in the SKILL.md "See also." |
| 3 | Reference.docx generator | **Ship one.** `skills/r-reporting/scripts/make_reference_doc.R`, parameterized but with minimalist defaults baked in. Patches `styles.xml` (and `word/footer1.xml` for page numbers). |
| 4 | Heading 1 page break | **Yes — every Heading 1 starts a new page** via `<w:pageBreakBefore/>` in the Heading 1 style. Override per-heading is documented as a Pandoc raw-block escape hatch. |
| 5 | Page numbers / footer | **Simple.** Bottom-centered page number, nothing else. Patches `word/footer1.xml` with the minimal `PAGE` field. No header, no date, no client name, no chapter title. Gated behind `page_numbers = TRUE` arg (default `TRUE`). |
| 6 | Project layout | **Detect, don't dictate.** `/r-report` inspects project type (package, analysis, targets) and picks the right qmd location: `inst/templates/report.qmd` for packages, `report/report.qmd` otherwise. The skill explains the trade-offs so Claude can adapt to atypical layouts. |
| 7 | Render mechanism | **`system2()` against the Quarto CLI**, not the R `quarto` package. Matches the Robyn project's working pattern; works without installing the R quarto package; tolerates `library(quarto)` not being eagerly loadable. |
| 8 | Table-in-Word path | **`as_flex_table()` is the standard exit.** gtsummary → flextable → docx is the recommended pipeline. Pre-saved RDS cache pattern (`saveRDS(tbl, "output/tables/01_table.rds")` upstream, `readRDS()` in the qmd) is documented as a first-class pattern, not just a workaround. |
| 9 | Figure path | **Project-relative paths from a `fig()` helper**, with `knitr::opts_knit$set(root.dir = here::here())` in the setup chunk. The skill explains why Pandoc, knitr, and R chunks resolve paths from three different roots. |
| 10 | Trigger surface | **Keyword-rich.** Triggers include: word document, docx, .docx output, render to word, reference-doc, reference docx, flextable, save_as_docx, consulting report, client report, statistical report, page break, heading style, line spacing, justify, page numbers in word, figure not centered, table not centered. Explicit negative boundaries against `r-quarto` (HTML/PDF), `r-tables` (table styling without docx context), `r-clinical` (regulatory TLF), `r-shiny` (interactive). |
| 11 | Minimum styling guarantees | **Five locked-in invariants** (see "Minimalist style spec" below). Everything else is overridable via `make_reference_doc.R` args. |
| 12 | Existing skill edits | **Two one-line cross-references**: `r-quarto/SKILL.md` and `r-tables/SKILL.md` get a "for Word/.docx deliverables, see r-reporting" pointer. No content moved out. |

## Approach

**Approach B — new skill + new command + scaffold scripts.** The new content is purely additive; no existing skill content is removed. The skill carries the explanatory burden (so Claude can answer questions about the pipeline anywhere); the command carries the scaffolding burden (so a fresh project can be wired up in under a minute); the scripts are the load-bearing artifacts they both reference.

## Artifact inventory

```
skills/r-reporting/
  SKILL.md                              # ≤300 lines
  eval.md                               # routing eval (5+ trigger prompts)
  references/
    reference-docx-anatomy.md           # styles.xml internals; what to patch and why
    quarto-docx-pitfalls.md             # the lessons.md landmines, generalised
    word-figure-table-patterns.md       # as_flex_table, figure sizing, gt→docx
  scripts/
    make_reference_doc.R                # parameterised generator with minimalist defaults
    report_template.qmd                 # opinionated qmd starter with path helpers
    render_to_docx.R                    # system2() wrapper around quarto CLI
    quarto_yml_block.yml                # resources/execute-dir snippet to merge

commands/
  r-report.md                           # /r-report — the orchestrating command

tests/
  routing_matrix.json                   # add r-reporting trigger prompts (and 2 negatives)
```

Edits to existing content (one-line each):

- `skills/r-quarto/SKILL.md` — add a one-line pointer in the Boundary block: "For Word/.docx deliverables (reference docx, page breaks, footers, figure/table centering), see **r-reporting**."
- `skills/r-tables/SKILL.md` — same pointer in the Output Formats section, after the existing flextable example.
- `hooks/session-start` — surface `r-reporting` when the project contains a `*.qmd` with `format: docx` or a `reference.docx` file.

## SKILL.md outline (target ≤290 lines)

1. Frontmatter — `name: r-reporting`, `description:` 700-900 chars covering "Use when..." capability statement, ~12 trigger keywords, 4 negative boundaries.
2. One-paragraph intro — pipeline mental model: R analysis writes figures (PNG) and tables (RDS/CSV) to `output/`; the qmd reads those artifacts and assembles a report; Pandoc renders to docx using a custom `reference.docx` for styles.
3. Lazy reference index — 3 references, one line each.
4. Agent dispatch — `r-code-reviewer` for qmd/R quality; `r-statistician` for table content (when present).
5. MCP integration — `btw_tool_env_describe_data_frame` for inspecting cached objects in `output/`; `btw_tool_docs_help_page` for `flextable`, `quarto`, `xml2`.
6. **Project layout (~25 lines)** — package vs analysis layouts; where the qmd lives; `_quarto.yml` `resources:` glob and `execute-dir: project`; why `resource-path:` is needed when the qmd is nested under `inst/templates/`.
7. **Path helpers (~20 lines)** — `fig()` returns project-relative (Pandoc/Quarto resource resolver), `tbl()` and `mod()` return absolute (R chunks via readRDS/read_csv); `knitr::opts_knit$set(root.dir = here::here())` and why.
8. **Tables in Word (~30 lines)** — `as_flex_table()` as the standard exit; `flextable::set_table_properties(width = 1, layout = "autofit", align = "center")`; the RDS cache pattern; gt-vs-flextable decision.
9. **Figures in Word (~20 lines)** — `fig-width: 8`, `fig-height: 5`, `dpi: 150`; ggplot theming for print (no transparent backgrounds, contrast); `knitr::include_graphics()` vs live chunks; centering happens through the reference.docx Figure style, not the qmd.
10. **Reference.docx (~25 lines)** — what styles.xml looks like; which styles Pandoc uses (Normal, Heading 1-4, Caption, Image Caption, Compact); how to invoke `make_reference_doc.R`; arguments and defaults.
11. **Render workflow (~20 lines)** — `system2(quarto_bin, ...)` over `quarto::quarto_render()`; timestamped output for audit trail; why `--output` is broken with `embed-resources`.
12. **Verification (~10 lines)** — exit code 0; figures embedded (open the docx, scroll); tables centered; page breaks where expected.
13. **Gotchas table (~25 lines)** — the lessons.md landmines, generalized to a markdown table.
14. **Examples (3 prompts, ~30 lines total)** — happy path, edge case (Heading 1 not paginating), boundary case (when to fall back to gt → PNG).

## References (lazy-loaded)

### `references/reference-docx-anatomy.md` (~250 lines)

- Word measurement units: twentieths of a point, twips for margins, half-points for font size.
- styles.xml structure: `<w:styles>`, `<w:docDefaults>`, individual `<w:style>` elements keyed by `w:styleId`.
- Pandoc-relevant styles: `Normal`, `Heading1`-`Heading4`, `Caption`, `ImageCaption`, `Compact`, `Figure`, `Table`, `Author`, `Title`, `TOCHeading`, `TOC1`-`TOC4`.
- The two patch targets for body styling: `docDefaults/pPrDefault/pPr` (catches every paragraph that doesn't override) AND the `Normal` style (Pandoc routes body text through it).
- Concrete elements: `<w:spacing w:line="360" w:lineRule="auto"/>` (1.5x), `<w:jc w:val="both"/>` (full justify), `<w:pageBreakBefore/>` (forces a page break), `<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>`, `<w:sz w:val="22"/>` (11pt body, half-points).
- Footer patching for page numbers: `word/footer1.xml`, `<w:fldSimple w:instr=" PAGE \\* MERGEFORMAT "/>`, the `<w:p><w:pPr><w:jc w:val="center"/>...` wrapper.
- The docx-as-zip gotcha: `mode = "mirror"` when re-zipping with `zip::zip()`; `--no-recurse` and explicit relative entry paths if using the system `zip` binary; never flatten or re-zip from a parent directory.
- Sanity check after patching: re-read the styles.xml with `xml2::read_xml()` to confirm it parses as XML before re-zipping.

### `references/quarto-docx-pitfalls.md` (~180 lines)

The Robyn project lessons, generalized:

- Quarto YAML doesn't support `!r Sys.Date()` (R Markdown only). Use a plain string + inline R in `title:` / `date:` fields.
- `--output report_TS.html` breaks because the post-process still looks for sibling `report_files/` (not `report_TS_files/`). Don't use `--output` with `embed-resources`. Render with the default name, then `file.rename()` after exit code 0.
- `library(quarto)` eager load fails on machines without the R quarto package. The R quarto package is **not required** to render via the Quarto CLI. Wrap with `requireNamespace()` if you must reference it.
- `knitr::include_graphics()` resolves paths from the qmd's directory by default. With `embed-resources: true`, set `knitr::opts_knit$set(root.dir = here::here())` in setup. Don't mix `here::here()` absolute paths with `include_graphics()` unless `root.dir` is set.
- gtsummary 2.x: don't pass `include = NULL` or `by = NULL`; omit them. Build args list conditionally and call via `rlang::exec(!!!args)`, not `do.call` (lazy promises break gtsummary's argument checking).
- ggplot 4.0 deprecates `geom_errorbarh()`. Switch to `geom_errorbar(orientation = "y")` or `coord_flip()` on plain `geom_errorbar()`.
- `cache: true` keys on chunk code only; data changes don't invalidate. Use `cache.extra` keyed on a data hash, or `freeze: auto` in `_quarto.yml`.
- Reference.docx path is resolved relative to the qmd, not the project root. With qmds nested under `inst/templates/`, place `reference.docx` in the same directory.
- `embed-resources: true` is HTML-only. For docx, all images are embedded by Pandoc by default; don't add the option.
- TinyTeX is needed for PDF, NOT for docx. `quarto install tinytex` is unnecessary for Word-only deliverables.

### `references/word-figure-table-patterns.md` (~200 lines)

- gtsummary → flextable: `tbl |> as_flex_table()` is the canonical exit. Apply `flextable::set_table_properties(width = 1, layout = "autofit", align = "center")` before printing.
- gtsummary 2.x argument hygiene: build args list, drop NULL fields, `rlang::exec(!!!args)`.
- gt → docx: `gtsave("table.docx")` works for simple tables but loses styling fidelity in Word. Prefer `as_flex_table()` for any non-trivial styling.
- gt → PNG fallback: when gt has features flextable can't represent (sparklines via gtExtras, embedded plots), `gtsave("table.png", zoom = 2)` and `knitr::include_graphics()` it. Document this as a deliberate fallback, not a default.
- Conditional formatting in flextable: `bold(i = ~p < 0.05, j = "p_value")`; `color(i = ..., j = ..., color = "#B22222")`. Cleaner than gt's `tab_style(cells_body(...))` for Word output.
- The RDS cache pattern: build the table object in the analysis script, `saveRDS(tbl, "output/tables/01_table_one.rds")`, read it back in the qmd with `readRDS(tbl("01_table_one.rds")) |> as_flex_table()`. Avoids re-running the gtsummary call inside the qmd render context (where it's slower and can hit different package versions).
- Figure sizing for Word: 8" × 5" at 150 dpi is the safe default for letter/A4 single-column. For wide multipanel patchwork plots, use 8" × 7" or 8" × 9". Heights above 9" risk pagination glitches.
- ggplot theming for print: white backgrounds, opaque legends, contrast-safe colors (viridis, Color Brewer), font size ≥ 10pt for axis labels.
- Figure centering: handled by the `Figure` style in `reference.docx`, not by markup in the qmd. If figures aren't centering, the reference.docx is the place to fix it.

## Minimalist style spec — five locked invariants

These are the styling guarantees `make_reference_doc.R` must produce by default. Everything else is parameterized; these are not.

| # | Invariant | XML mechanism |
|---|---|---|
| 1 | Body text: 1.5 line spacing, full-justified, Calibri 11pt | `<w:spacing w:line="360" w:lineRule="auto"/>`, `<w:jc w:val="both"/>`, `<w:rFonts w:ascii="Calibri"/>`, `<w:sz w:val="22"/>` on both `docDefaults/pPrDefault` and the `Normal` style |
| 2 | Heading 1: starts a new page, bold, centered | `<w:pageBreakBefore/>`, `<w:b/>`, `<w:jc w:val="center"/>` on the `Heading1` style |
| 3 | Figures: centered horizontally on the page | `<w:jc w:val="center"/>` on the `Figure` style (Pandoc's image-paragraph wrapper) |
| 4 | Tables: centered horizontally | `align = "center"` in `flextable::set_table_properties()` (script-level) AND `<w:jc w:val="center"/>` on the `Table` style (defense in depth) |
| 5 | Page numbers: bottom-centered, nothing else | `word/footer1.xml` patched to a single centered paragraph with `<w:fldSimple w:instr=" PAGE "/>`. No header. No date. No other footer content. |

Overridable defaults (not invariants): font (Calibri), body size (11pt), heading sizes (18/14/12/11pt), margin (1 inch), paragraph spacing-after (8pt), `number-sections` (TRUE), TOC depth (3).

## `/r-report` command flow

`commands/r-report.md` (≤200 lines), runs the following on invocation:

1. **Detect project type** by inspecting `DESCRIPTION` (R package), `_targets.R` (targets pipeline), or fallback to "analysis project". Pick the qmd location accordingly:
   - Package → `inst/templates/report.qmd` (matches the Robyn project pattern)
   - Targets pipeline → `report/report.qmd` (sibling to `_targets.R`)
   - Analysis → `report/report.qmd`
2. **Refuse to clobber.** If `report.qmd` already exists at the target path, summarise its YAML and ask the user whether to overwrite or scaffold a sidecar (`report_v2.qmd`).
3. **Scaffold artifacts** by copying from `skills/r-reporting/scripts/`:
   - `report_template.qmd` → target qmd path
   - `render_to_docx.R` → `analysis/05_report.R` (analysis project) or `R/render_report.R` (package)
   - `make_reference_doc.R` → `analysis/make_reference_doc.R` or `inst/templates/make_reference_doc.R`
   - Merge `quarto_yml_block.yml` into existing `_quarto.yml` (or create one).
4. **Generate the reference docx** by sourcing `make_reference_doc.R` once. Confirm `reference.docx` is created adjacent to the qmd.
5. **Sanity render** by calling the render wrapper. Report the path of the timestamped output and the docx file size; flag any non-zero render warnings.
6. **Open the docx** on macOS via `system2("open", path)` (skip on Linux/CI; print path instead).

Abort conditions:

- No R project detected (no `DESCRIPTION`, no `*.Rproj`, no `.Rprofile`).
- Quarto CLI not on `PATH` (with install instructions).
- Working tree dirty — warn but proceed if the user confirms.

The command body explicitly references the skill (`**Skill:** r-reporting`) so Claude picks it up at scaffold time and again on follow-up edits.

## Testing

- **Routing tests** (`tests/routing_matrix.json`): 6 prompts that should route to `r-reporting`:
  - "render this report to Word"
  - "the figures aren't centered in my Word document"
  - "make the docx match journal style"
  - "build a Word reference template with 1.5 line spacing"
  - "convert this gtsummary table to flextable for docx"
  - "every section should start on a new page in the Word output"
  - 2 negative prompts that should NOT route there: "render this to HTML" → r-quarto; "format a regulatory TLF" → r-clinical.
- **Structural tests** (`tests/test_structural.py`): SKILL.md ≤300 lines, two-field frontmatter; command ≤200 lines with `description:`; references load.
- **Convention tests** (`tests/test_conventions.py`): no `%>%` outside `eval.md`; R code uses `<-`, `|>`, `snake_case`, `""`.
- **Smoke test** (new, optional `tests/smoke_r_report.sh`): scaffold into a temp dir, render, assert docx is non-empty and contains an expected string. Skipped if Quarto CLI not on PATH so CI without Quarto stays green.

## Migration / coexistence

`r-reporting` is purely additive. Existing users of `r-quarto` and `r-tables` are unaffected; they get a one-line "for docx, see r-reporting" pointer. No content moves between skills. Anyone with a custom report.qmd today can keep it; the `/r-report` command refuses to clobber.

## Risks and tradeoffs

- **Risk:** opinionated layout doesn't fit every project. **Mitigation:** scaffold is a starting point; users can move files. The skill content stands alone if no scaffold is used.
- **Risk:** `make_reference_doc.R` breaks when Pandoc's bundled reference.docx changes structure. **Mitigation:** the script reads, patches, writes — it doesn't assume specific structure beyond `Normal` style and `docDefaults/pPrDefault` existing. Sanity check (re-read patched XML) catches bad output before re-zipping. Breakage surfaces immediately at first run; a regenerated reference docx is one command away.
- **Risk:** footer1.xml patching is more fragile than styles.xml patching. **Mitigation:** gated behind `page_numbers = TRUE`; defaults to on but can be disabled in one arg. The patch is small (a single `<w:fldSimple>` field) and idempotent.
- **Risk:** users on Windows hit `system2("open", path)` failure. **Mitigation:** detect platform; use `shell.exec()` on Windows, `xdg-open` on Linux, no-op on CI.
- **Tradeoff:** scope. The compass artifact's editorial framework is interesting and arguably more valuable than the mechanics. By deferring it, the mechanics ship sooner and the editorial work gets the dedicated brainstorm it deserves.

## Forward links

- The editorial template (CONSORT/STROBE sections, estimand framework, prespecification, missing-data templates) is a separate brainstorm seeded by `docs/compass_artifact_wf-485b38b3-0576-4506-a6bf-efe7d5866ca2_text_markdown.md`. When that lands, `r-reporting` and the future `r-consulting-report` (or similar) skills will compose: `/r-report` will optionally scaffold an opinionated section structure if the editorial skill is installed.
- Posit Connect / `quarto publish` automation for client-facing report drops is out of scope here but would be a natural extension once the docx mechanics are stable.

---

**Approval:** Approach B with both layers ((iii)) confirmed. Five style invariants locked. Heading 1 page break confirmed. Footer simple (page-number-only) confirmed. Compass artifact deferred. Pending: implementation plan (next step — `superpowers:writing-plans`).
