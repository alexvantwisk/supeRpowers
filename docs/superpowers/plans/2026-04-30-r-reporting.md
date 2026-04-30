# r-reporting Skill + /r-report Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a new `r-reporting` skill (mechanics knowledge), a new `/r-report` slash command (orchestrating scaffold), and supporting reference + script artifacts so an R consulting project can go from zero to a clean, minimalist Word (.docx) deliverable in one command.

**Architecture:** Approach B from the spec — purely additive. New skill carries explanatory burden so Claude can answer questions anywhere; command carries scaffolding burden so a fresh project gets wired up fast; scripts are the load-bearing artifacts both reference. Implementation runs in a dedicated git worktree on `feature/r-reporting`.

**Tech Stack:** Markdown (skill content + command), Python 3 (test harness `tests/run_all.py`), Bash (verification + smoke test + session-start hook), R (`xml2`, `zip`, `flextable`, `here`, `quarto` CLI invoked via `system2()`). Conventions: `|>`, `<-`, snake_case, double quotes, R ≥ 4.1.0.

**Spec:** `docs/superpowers/specs/2026-04-30-r-reporting-design.md`

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `.claude/worktrees/r-reporting/` | Create (worktree) | Isolated working directory |
| `tests/routing_matrix.json` | Modify | Add 6 positive + 2 negative routing entries |
| `skills/r-reporting/SKILL.md` | Create | ≤300 lines; pipeline mental model + path/table/figure/render guidance |
| `skills/r-reporting/eval.md` | Create | Binary eval questions + happy/edge/adversarial/boundary prompts |
| `skills/r-reporting/references/reference-docx-anatomy.md` | Create | styles.xml internals; what to patch and why; ~250 lines |
| `skills/r-reporting/references/quarto-docx-pitfalls.md` | Create | Generalised lessons from the Robyn project; ~180 lines |
| `skills/r-reporting/references/word-figure-table-patterns.md` | Create | as_flex_table, RDS cache pattern, gt fallback, fig sizing; ~200 lines |
| `skills/r-reporting/scripts/make_reference_doc.R` | Create | Parameterised generator; minimalist defaults; the 5 style invariants |
| `skills/r-reporting/scripts/report_template.qmd` | Create | Opinionated qmd starter with path helpers, setup chunk, sample sections |
| `skills/r-reporting/scripts/render_to_docx.R` | Create | system2() wrapper around `quarto` CLI; timestamped output |
| `skills/r-reporting/scripts/quarto_yml_block.yml` | Create | resources/execute-dir snippet for merging into project `_quarto.yml` |
| `commands/r-report.md` | Create | Orchestrating slash command; ≤200 lines |
| `skills/r-quarto/SKILL.md` | Modify | Add one-line cross-reference to r-reporting in Boundary block |
| `skills/r-tables/SKILL.md` | Modify | Add one-line cross-reference to r-reporting in Output Formats |
| `hooks/session-start` | Modify | Surface r-reporting when project contains a `*.qmd` with `format: docx` |
| `tests/smoke_r_report.sh` | Create (optional) | End-to-end scaffold + render smoke test; skip if Quarto missing |

---

## Conventions Reminder (apply to ALL new content)

Every R code block, every R script, every example must use:
- `|>` (base pipe) — never `%>%` (magrittr).
- `<-` for assignment — never `=` (except inside function arguments).
- `snake_case` for all identifiers.
- Double quotes for strings — never single quotes.
- Tidyverse-first where applicable (dplyr, readr, etc.). `xml2`, `zip`, `flextable`, `here` are required for the docx mechanics.
- Target R ≥ 4.1.0.

After every file write, run a local convention check (commands embedded in each task).

---

## Task 1: Set up isolated worktree

**Files:**
- Create: `.claude/worktrees/r-reporting/` (worktree root)
- Branch: `feature/r-reporting` (created off `main`)

- [ ] **Step 1: Verify clean working tree on main**

Run from `/Users/alexandervantwisk/Desktop/Projects/supeRpowers`:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
```

Expected: empty output (or only untracked items unrelated to this work); current branch `main`. If the spec file (`docs/superpowers/specs/2026-04-30-r-reporting-design.md`) is still untracked, that's expected — pick it up in Task 18 commit.

- [ ] **Step 2: Create the worktree**

```bash
git worktree add -b feature/r-reporting .claude/worktrees/r-reporting main
```

Expected: `Preparing worktree (new branch 'feature/r-reporting')` then `HEAD is now at <sha> ...`.

- [ ] **Step 3: Verify worktree and copy the (untracked) spec into it**

```bash
git worktree list
ls .claude/worktrees/r-reporting/docs/superpowers/specs/
```

If the spec is untracked, copy it across so the worktree has the same starting state:

```bash
[ -f docs/superpowers/specs/2026-04-30-r-reporting-design.md ] && \
  cp docs/superpowers/specs/2026-04-30-r-reporting-design.md \
     .claude/worktrees/r-reporting/docs/superpowers/specs/
```

Expected: worktree contains the spec.

- [ ] **Step 4: Switch to the worktree directory**

All subsequent tasks run from `.claude/worktrees/r-reporting/`. Either `cd` there once or prefix every command with the absolute path. The plan assumes you're inside the worktree from this point forward.

```bash
cd .claude/worktrees/r-reporting
pwd
```

Expected: prints the absolute worktree path.

---

## Task 2: Add routing matrix entries (RED)

**Files:**
- Modify: `tests/routing_matrix.json`

The routing test fires before the skill exists. Adding entries first locks down the trigger surface and gives Task 3 a concrete target. With no skill, the routing tests for r-reporting must fail — that's the RED state.

- [ ] **Step 1: Inspect current matrix**

```bash
python3 -c "import json; m=json.load(open('tests/routing_matrix.json')); print(len(m))"
```

Expected: `64` entries today (next id will be `route-065`).

- [ ] **Step 2: Append 8 new entries (6 positive, 2 negative)**

Use the Edit tool to append, preserving the closing `]`. The 8 entries (insert before the final `]`):

```json
  ,
  {
    "id": "route-065",
    "prompt": "Render this analysis report to Word and make sure tables and figures come out right",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-quarto", "r-tables"],
    "discriminator": "Word/.docx output + tables and figures",
    "category": "report-mechanics"
  },
  {
    "id": "route-066",
    "prompt": "The figures in my Word document aren't centered — how do I fix the reference docx?",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-visualization", "r-quarto"],
    "discriminator": "reference docx + Word centering",
    "category": "report-mechanics"
  },
  {
    "id": "route-067",
    "prompt": "Build a Word reference template with 1.5 line spacing, full justify, and Heading 1 starting on a new page",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-quarto"],
    "discriminator": "reference.docx authoring",
    "category": "report-mechanics"
  },
  {
    "id": "route-068",
    "prompt": "Convert this gtsummary regression table to flextable so it renders correctly in docx",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-tables"],
    "discriminator": "gtsummary -> flextable -> docx pipeline (Word context)",
    "category": "report-mechanics"
  },
  {
    "id": "route-069",
    "prompt": "Every section in my consulting report should start on a new page in the Word output",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-quarto"],
    "discriminator": "Heading 1 page break in Word",
    "category": "report-mechanics"
  },
  {
    "id": "route-070",
    "prompt": "Set up a clean docx report pipeline for my client deliverable — tables from gtsummary, figures from ggplot, page numbers in the footer",
    "expected_skill": "r-reporting",
    "must_not_fire": ["r-quarto", "r-tables"],
    "discriminator": "end-to-end docx pipeline orchestration",
    "category": "report-mechanics"
  },
  {
    "id": "route-071",
    "prompt": "Render this Quarto book to HTML with a custom theme and embedded resources",
    "expected_skill": "r-quarto",
    "must_not_fire": ["r-reporting"],
    "discriminator": "HTML output (not Word) -> r-quarto, NOT r-reporting",
    "category": "report-mechanics"
  },
  {
    "id": "route-072",
    "prompt": "Generate a regulatory TLF package for FDA submission with admiral-derived ADaM data",
    "expected_skill": "r-clinical",
    "must_not_fire": ["r-reporting", "r-tables"],
    "discriminator": "regulatory TLF (FDA + admiral + ADaM) -> r-clinical, NOT r-reporting",
    "category": "report-mechanics"
  }
```

- [ ] **Step 3: Run routing tests to confirm RED**

```bash
python3 tests/run_all.py --layer 2 2>&1 | tail -40
```

Expected: routing tests for `route-065` through `route-070` fail because `r-reporting` skill doesn't exist; `route-071` and `route-072` should pass on existing skills. If routing test framework cannot resolve a skill name, the failure mode is "skill not found" rather than "routed wrong" — both are acceptable RED states.

- [ ] **Step 4: Commit**

```bash
git add tests/routing_matrix.json
git commit -m "test(routing): add r-reporting matrix entries (RED)

Adds 6 positive + 2 negative routing prompts for the new
r-reporting skill. Tests will fail until the skill ships in
subsequent tasks."
```

---

## Task 3: Create skill skeleton with frontmatter

**Files:**
- Create: `skills/r-reporting/SKILL.md`

The skeleton just needs frontmatter + minimal body to pass structural tests. The full body lands in Task 5.

- [ ] **Step 1: Create the directory**

```bash
mkdir -p skills/r-reporting/references skills/r-reporting/scripts
```

- [ ] **Step 2: Write the SKILL.md skeleton**

Create `skills/r-reporting/SKILL.md` with this content:

```markdown
---
name: r-reporting
description: >
  Use when producing Word (.docx) deliverables from R analyses — consulting
  reports, manuscript drafts, client handoffs — where tables, figures, page
  layout, and a custom reference.docx need to compose cleanly through the
  Quarto -> Pandoc -> Word pipeline.
  Provides expert guidance on reference.docx authoring (line spacing, justify,
  Heading 1 page breaks, centered figures and tables, simple page-number
  footer), the gtsummary -> flextable -> docx exit ramp, the RDS cache pattern
  for tables built upstream, project layout for a Word-output qmd
  (resources, execute-dir, resource-path, path helpers), and the
  system2(quarto, ...) render workflow.
  Triggers: word document, docx, .docx output, render to word, reference-doc,
  reference docx, flextable, save_as_docx, consulting report, client report,
  statistical report, page break, heading style, line spacing, justify, page
  numbers in word, figure not centered, table not centered.
  Do NOT use for HTML/PDF output — use r-quarto.
  Do NOT use for table styling without a Word context — use r-tables.
  Do NOT use for regulatory TLFs — use r-clinical.
  Do NOT use for interactive HTML reports or Shiny dashboards — use r-shiny.
---

# R Reporting

Quarto-to-Word (.docx) pipeline for R consulting deliverables. Pairs with the
`/r-report` command, which scaffolds an opinionated working pipeline into an
existing R project. All R code uses `|>`, `<-`, snake_case, and double quotes.

> **Boundary:** Word/.docx output. For HTML/PDF, use r-quarto. For regulatory
> TLFs, use r-clinical.

(Body content fills in during Task 5.)
```

- [ ] **Step 3: Run structural tests**

```bash
python3 tests/run_all.py --layer 1 2>&1 | tail -20
```

Expected: skill is discovered, frontmatter parses (`name` + `description`), line count under limit, plugin.json (if it lists skills) is consistent. New failures specific to r-reporting should be zero.

- [ ] **Step 4: Run routing tests again — partial GREEN**

```bash
python3 tests/run_all.py --layer 2 2>&1 | tail -30
```

Expected: with the description live, several `route-065`–`route-070` entries should now route to `r-reporting`. Some may still fail until the body content (Task 5) provides discriminating context. That's fine — the skill is provisionally wired up.

- [ ] **Step 5: Commit**

```bash
git add skills/r-reporting/SKILL.md
git commit -m "feat(r-reporting): add skill skeleton with frontmatter

Frontmatter establishes the trigger surface and negative
boundaries. Body content lands in a follow-up commit."
```

---

## Task 4: Create eval.md

**Files:**
- Create: `skills/r-reporting/eval.md`

The eval file is dev-only (not loaded by the plugin) but is the canonical record of expected skill behavior. Mirror the structure of `skills/r-quarto/eval.md`.

- [ ] **Step 1: Write the eval file**

Create `skills/r-reporting/eval.md`:

```markdown
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
```

- [ ] **Step 2: Convention check (eval.md is exempt from %>% scan but still scanned for structure)**

```bash
wc -l skills/r-reporting/eval.md
```

Expected: between 70 and 110 lines.

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/eval.md
git commit -m "test(r-reporting): add binary eval questions and routing prompts

Mirrors r-quarto/eval.md structure. Covers happy path, edge
cases, adversarial deferrals, and boundary tests."
```

---

## Task 5: Write SKILL.md body

**Files:**
- Modify: `skills/r-reporting/SKILL.md`

Replace the placeholder body. Target ≤290 lines including frontmatter.

- [ ] **Step 1: Replace SKILL.md body in place**

Use the Edit tool to replace the line `(Body content fills in during Task 5.)` with the full body below. Keep the frontmatter and the existing intro/boundary block from Task 3.

The body, in order:

1. **Lazy reference index (5 lines):**

```markdown
**Lazy references:**
- Read `references/reference-docx-anatomy.md` for styles.xml structure, twentieths-of-a-point units, which Pandoc styles to patch (Normal, docDefaults, Heading 1, Figure, Table, ImageCaption), and the docx-zip "mirror mode" requirement.
- Read `references/quarto-docx-pitfalls.md` for the Quarto/Pandoc/knitr landmines: `!r` not in YAML, `--output` breaking `_files/`, `library(quarto)` eager load, `include_graphics` path resolution, `gtsummary` 2.x argument hygiene.
- Read `references/word-figure-table-patterns.md` for `as_flex_table()`, the RDS cache pattern, `gt -> PNG` fallback, conditional formatting in flextable, figure sizing and ggplot theming for print.
```

2. **Agent dispatch:**

```markdown
**Agent dispatch:** For R/qmd code quality, dispatch to **r-code-reviewer**. For statistical content of inline tables, dispatch to **r-statistician**.
```

3. **MCP integration (when an R session is available):**

```markdown
**MCP integration (when R session available):**
- Before writing a table-loading chunk: `btw_tool_env_describe_data_frame` on the cached object to confirm shape and column types.
- When uncertain about a flextable function: `btw_tool_docs_help_page` to check the current API.
- When patching `reference.docx`: `btw_tool_docs_help_page` for `xml2` namespace handling.
```

4. **Pipeline mental model (~12 lines):** one paragraph describing the pipeline:

> The R analysis writes figures (PNG) and tables (RDS or CSV) to `output/`. The qmd reads those artifacts and assembles the report. Pandoc renders the qmd to docx using a custom `reference.docx` for styles. Path resolution differs by tool: R chunks resolve from the project root via `here::here()`; Pandoc resolves images relative to the qmd; knitr's `include_graphics()` resolves from the qmd unless `opts_knit$set(root.dir = ...)` overrides. Reconciling these three roots is most of the work.

5. **Project layout (~25 lines):** show two layouts side by side:

```markdown
## Project Layout

| Project type | qmd location | Reference docx | Render script |
|---|---|---|---|
| R package | `inst/templates/report.qmd` | `inst/templates/reference.docx` | `R/render_report.R` or `analysis/05_report.R` |
| Analysis project | `report/report.qmd` | `report/reference.docx` | `analysis/05_report.R` |
| targets pipeline | `report/report.qmd` | `report/reference.docx` | a `tar_target` calling `system2(quarto, ...)` |

Wherever the qmd lives, three things must align:

1. **`_quarto.yml`** at the project root specifies `execute-dir: project` and a `resources:` glob covering `output/figures/*.png` and `output/tables/*.html`. Without `execute-dir`, `here::here()` fails inside chunks.
2. **The qmd's YAML** specifies `resource-path: [".", "../.."]` (or appropriate relative path back to the project root) so Pandoc can find figures referenced as `output/figures/foo.png`.
3. **The setup chunk** sets `knitr::opts_knit$set(root.dir = here::here())` so `knitr::include_graphics()` resolves correctly.
```

6. **Path helpers (~20 lines):** show `fig()` / `tbl()` / `mod()` and explain the project-relative-vs-absolute split.

```markdown
## Path Helpers in the qmd

```r
fig <- function(file) file.path("output", "figures", file)   # project-relative for Pandoc
tbl <- function(file) here::here("output", "tables",  file)  # absolute for R chunks
mod <- function(file) here::here("output", "models",  file)  # absolute for R chunks
```

`fig()` returns project-relative paths so Pandoc / Quarto's resource resolver can find figures under both `quarto render` and `quarto preview --output-dir <tmp>`. `tbl()` and `mod()` return absolute paths because they are read by R chunks (`readRDS`, `read_csv`) which run from the project root.
```

7. **Tables in Word (~30 lines):**

```markdown
## Tables in Word

`as_flex_table()` is the canonical exit from gtsummary. Apply set_table_properties for autofit + centered alignment:

```r
library(flextable)

readRDS(tbl("01_table_one.rds")) |>
  as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
  flextable::fontsize(size = 10, part = "all")
```

**The RDS cache pattern.** Build the table object in the analysis script, save it to `output/tables/`, read it back in the qmd:

```r
# In 04_model.R — runs once, cached
tbl_one <- trial |>
  gtsummary::tbl_summary(by = trt) |>
  gtsummary::add_p() |>
  gtsummary::bold_labels()
saveRDS(tbl_one, here::here("output", "tables", "01_table_one.rds"))
```

```r
# In report.qmd — fast, deterministic
readRDS(tbl("01_table_one.rds")) |>
  as_flex_table() |>
  flextable::set_table_properties(width = 1, layout = "autofit", align = "center")
```

This avoids re-running gtsummary inside the qmd render context (slower, can hit different package versions).

For gt-only features (gtExtras sparklines, embedded plots) that flextable can't represent, fall back to `gtsave("table.png", zoom = 2)` and `knitr::include_graphics()` — labelled as a deliberate fallback, not a default.
```

8. **Figures in Word (~20 lines):**

```markdown
## Figures in Word

YAML defaults: `fig-width: 8`, `fig-height: 5`, `dpi: 150`. For wide multipanel patchwork plots, use 8" × 7" or 8" × 9". Heights above 9" risk pagination glitches.

ggplot theming for print: white backgrounds (`theme_minimal(base_size = 11) + theme(plot.background = element_rect(fill = "white", colour = NA))`), opaque legends, contrast-safe palettes (viridis, Color Brewer), font size ≥ 10pt.

**Figure centering happens in the reference.docx Figure style, not in the qmd.** If figures aren't centering, regenerate `reference.docx` — don't add `\centering` or alignment markup to the qmd (Pandoc strips it for docx output).

For pre-built figures from upstream scripts:

```r
knitr::include_graphics(fig("01_attrition_flow.png"))
```

Requires `knitr::opts_knit$set(root.dir = here::here())` in the setup chunk.
```

9. **Reference.docx (~25 lines):**

```markdown
## Reference.docx

Pandoc applies styles from a `reference.docx` you supply via YAML:

```yaml
format:
  docx:
    reference-doc: reference.docx   # resolved relative to the qmd's directory
```

Pandoc's default reference docx ships with neutral defaults. To get the five style invariants (1.5 line spacing + full justify + Calibri 11pt body, Heading 1 starts a new page bold centered, figures centered, tables centered, simple page-number footer), patch the styles.xml inside the docx zip.

**Generate via the bundled script:**

```r
source(here::here("analysis", "make_reference_doc.R"))
```

The script extracts Pandoc's default `reference.docx`, patches `styles.xml` (Normal, docDefaults, Heading 1, Figure, Table, ImageCaption) and `word/footer1.xml` (centered PAGE field), and re-zips with `mode = "mirror"`. Read `references/reference-docx-anatomy.md` for the XML internals and parameterisation arguments.
```

10. **Render workflow (~20 lines):**

```markdown
## Render Workflow

Use `system2()` against the Quarto CLI, not the R `quarto` package. The R package is not required for rendering:

```r
quarto_bin <- Sys.which("quarto")
if (nzchar(quarto_bin) == 0L) stop("Quarto CLI not on PATH.")

result <- system2(
  quarto_bin,
  args = c(
    "render", shQuote(input_qmd),
    "--to", "docx",
    "--execute-dir", shQuote(here::here())
  ),
  stdout = "", stderr = "",
  wait = TRUE
)
if (result != 0L) stop("quarto render failed.")
```

**Timestamped output for audit trail.** After a successful render, rename the default output file to `report_YYYYMMDD_HHMMSS.docx` and copy to `output/` so each render is preserved.

**Don't use `--output`.** With `embed-resources` HTML it breaks `_files/` resolution. With docx it works but the bundled wrapper takes the safer post-render rename path.
```

11. **Verification (~10 lines):**

```markdown
## Verification

After render: exit code 0; the docx file exists and is non-empty (>20 KB typically); opening the docx shows figures embedded, tables centered, Heading 1 sections starting on new pages, page numbers in footer. Run `file output/report_*.docx` — should report `Microsoft Word 2007+`.
```

12. **Gotchas (~25 lines):** a markdown table summarising the landmines:

```markdown
## Gotchas

| Trap | Why It Fails | Fix |
|---|---|---|
| `date: !r Sys.Date()` in YAML | `!r` is R Markdown only; Quarto doesn't honor it | Use a plain string in `params` and resolve via inline R in the title field |
| `--output report_TS.html` with `embed-resources: true` | Post-process still looks for `report_files/`, not `report_TS_files/` | Render with default name; `file.rename()` after exit code 0 |
| `library(quarto)` in `00_setup.R` | Fails on machines without the R quarto package; not required for CLI render | `if (requireNamespace("quarto", quietly = TRUE)) library(quarto)` |
| `knitr::include_graphics(fig("foo.png"))` resolves from qmd dir | knitr defaults to qmd's directory, not project root | Set `knitr::opts_knit$set(root.dir = here::here())` in setup chunk |
| `tbl_summary(by = NULL)` in gtsummary 2.x | gtsummary 2.x errors on NULL passed to `by`/`include` | Build args list conditionally; `rlang::exec(!!!args)` (NOT `do.call`) |
| `geom_errorbarh()` in ggplot 4.0 | Deprecated; loud warnings | `geom_errorbar(orientation = "y")` or `coord_flip()` |
| Re-zipping reference.docx with flat directory | Word rejects the file | `zip::zip(..., mode = "mirror")` preserves the directory tree |
| `cache: true` not invalidating on data change | `cache: true` keys on chunk code only | Use `cache.extra = digest::digest(data_path)` or `freeze: auto` in `_quarto.yml` |
| `embed-resources: true` in docx YAML | HTML-only; ignored or warned for docx | Drop it. Pandoc embeds images in docx by default |
| Figure centering markup in qmd (`\centering`, ::: divs) | Pandoc strips for docx | Center via the Figure style in `reference.docx` |
```

13. **Examples (~30 lines):** three example prompts:

```markdown
## Examples

### Happy Path: scaffold a docx pipeline

**Prompt:** "Set up a Quarto-to-Word pipeline for my consulting project."

Invoke `/r-report`. The command detects project type, scaffolds `report.qmd`, `make_reference_doc.R`, and a render script, generates the reference docx with minimalist defaults, and runs the first render.

### Edge Case: figures rendered but not centered

**Prompt:** "My figures show up in the Word output but they're left-aligned."

Diagnose: Pandoc routes images through the `Figure` paragraph style. Centering is a styles.xml fix, not a qmd fix. Regenerate `reference.docx` (the bundled `make_reference_doc.R` patches the Figure style by default) and re-render.

### Boundary: complex table with gtExtras sparklines

**Prompt:** "I have a gt table with `gt_sparkline()` and `gt_plt_bar()` columns — how do I get it into Word?"

flextable cannot represent gtExtras inline graphics. Use the PNG fallback:

```r
gt::gtsave(my_gt_tbl, here::here("output", "tables", "10_summary.png"), zoom = 2)
# In qmd:
knitr::include_graphics(fig("10_summary.png"))
```

Document this as a deliberate fallback. For ordinary gtsummary tables, prefer `as_flex_table()`.
```

- [ ] **Step 2: Run structural tests**

```bash
python3 tests/run_all.py --layer 1 2>&1 | tail -20
wc -l skills/r-reporting/SKILL.md
```

Expected: structural tests pass; line count between 240 and 290.

- [ ] **Step 3: Run convention tests**

```bash
python3 tests/run_all.py --layer 1b 2>&1 | tail -20
```

Expected: zero `%>%` violations in r-reporting; zero `=`-as-assignment violations in R code blocks.

- [ ] **Step 4: Run routing tests**

```bash
python3 tests/run_all.py --layer 2 2>&1 | tail -30
```

Expected: all 6 positive r-reporting routing entries (`route-065`–`route-070`) pass; the 2 negatives (`route-071`, `route-072`) still pass.

- [ ] **Step 5: Commit**

```bash
git add skills/r-reporting/SKILL.md
git commit -m "feat(r-reporting): write full SKILL.md body

Adds pipeline mental model, project layout matrix, path helpers,
tables/figures/reference.docx/render workflow sections, gotchas
table, and three examples. Routing for 6 positive prompts now
resolves to r-reporting."
```

---

## Task 6: Write `references/reference-docx-anatomy.md`

**Files:**
- Create: `skills/r-reporting/references/reference-docx-anatomy.md`
- Target: ~250 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Reference.docx Anatomy`

Required sections (in order):

1. **Why a reference.docx?** — Pandoc applies styles from a template; without it, Pandoc uses a built-in default. Patching is the only practical way to get pagination + centering + footer behaviour.
2. **The docx is a zip archive** — internal structure (`[Content_Types].xml`, `_rels/`, `word/styles.xml`, `word/footer1.xml`, `word/header1.xml`, `docProps/`); never flatten when re-zipping; `mode = "mirror"` requirement.
3. **Measurement units cheat sheet** — twentieths of a point (line spacing, paragraph spacing-before/after); twips (margins, indents); half-points (font size); Word's quirky line-rule (`line=240` single, `line=360` 1.5x, `line=480` double; `lineRule="auto"` means leading).
4. **Pandoc-relevant styles** — table mapping markdown elements to Word styles: paragraph -> `Normal`, `# Heading 1` -> `Heading1`, `> blockquote` -> `BlockText`, image paragraph -> `Figure`, image caption -> `ImageCaption`, table caption -> `TableCaption`, table cells -> `Table`, code blocks -> `SourceCode`, list items -> `Compact` or `BodyText`, TOC entries -> `TOC1`-`TOC4`. (Verified empirically by rendering a sample qmd and inspecting the output docx.)
5. **The two body-styling patch targets** — patching `Normal` alone is not enough; many Pandoc-emitted paragraphs have empty `<w:pPr>` blocks that fall through to `docDefaults/pPrDefault`. Patch both for guaranteed coverage.
6. **The five style invariants and their XML** — show the exact XML for each invariant: body 1.5x + justify + Calibri 11pt; Heading 1 page break + center + bold; Figure center; Table center; footer page-number-only.
   - Body styling: `<w:spacing w:line="360" w:lineRule="auto"/>`, `<w:jc w:val="both"/>`, `<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>`, `<w:sz w:val="22"/>`, `<w:szCs w:val="22"/>` — all on `docDefaults/pPrDefault/pPr` and `Normal/pPr`.
   - Heading 1: `<w:pageBreakBefore/>`, `<w:jc w:val="center"/>`, `<w:b/>` (and `<w:bCs/>` for complex scripts) on `Heading1/pPr` and `Heading1/rPr`.
   - Figure: `<w:jc w:val="center"/>` on `Figure/pPr`.
   - Table: `<w:jc w:val="center"/>` on `Table/pPr` (defense in depth alongside flextable's `align = "center"`).
   - Footer: in `word/footer1.xml`, replace the body paragraph with a single centered paragraph containing `<w:fldSimple w:instr=" PAGE \\* MERGEFORMAT "/>`.
7. **The `xml2` patching idiom** — `xml_find_first()`, `xml_find_all()`, `xml_remove()` for stripping existing values, `xml_add_child()` with named arguments using namespace prefixes (`` `w:line` = "360" ``).
8. **The namespace map** — `c(w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main")`. Without the `w` namespace bound, all XPaths return missing.
9. **Sanity check after patching** — re-read the patched XML with `xml2::read_xml()` to confirm it still parses; reject and abort if not.
10. **Re-zipping** — three options: (a) `zip::zip(zipfile, files = entries, root = work_dir, mode = "mirror")` — recommended; (b) system `zip` binary with `cd work_dir && zip -rq target.docx .` — works on macOS/Linux but fails on Windows by default; (c) `utils::zip()` — has its own gotchas with directory entries. Go with (a) when the `zip` R package is available.
11. **What NOT to patch** — `_rels/.rels`, `[Content_Types].xml`, `docProps/core.xml`. Touching these can corrupt the docx silently.

Required code samples: at least three working R snippets — one for body styling, one for Heading 1 page break, one for footer patching.

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-reporting/references/reference-docx-anatomy.md
wc -l skills/r-reporting/references/reference-docx-anatomy.md
```

Expected: zero `%>%` hits; line count between 200 and 280.

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/references/reference-docx-anatomy.md
git commit -m "docs(r-reporting): add reference-docx-anatomy reference

styles.xml internals, twentieths-of-a-point unit cheat sheet,
the two body-styling patch targets, the five style invariants
with exact XML, xml2 patching idiom, sanity check, and re-zip
guidance."
```

---

## Task 7: Write `references/quarto-docx-pitfalls.md`

**Files:**
- Create: `skills/r-reporting/references/quarto-docx-pitfalls.md`
- Target: ~180 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Quarto-to-Docx Pitfalls`

Required sections (each titled by the pitfall, in this order):

1. `## Quarto YAML doesn't support !r` — describe the trap (`date: !r Sys.Date()` is R Markdown only); show wrong vs right; right is `date: ""` in `params` plus inline R `\`r if (nzchar(params$date)) params$date else format(Sys.Date())\`` in the title YAML.
2. `## --output breaks _files/ for embed-resources HTML` — describe (post-process looks for sibling `report_files/` directory keyed off the original filename); fix is render with default name + `file.rename()` after exit 0; note this only applies to HTML; with docx `--output` is fine but the bundled wrapper does the rename anyway for consistency.
3. `## library(quarto) eager load` — the R quarto package is NOT required to render via the CLI; eager-loading it breaks pipelines on machines without it; show `if (requireNamespace("quarto", quietly = TRUE)) library(quarto)` or just skip and use `system2()`.
4. `## knitr::include_graphics path resolution` — knitr resolves paths from the qmd's directory by default; with project-relative figure paths, set `knitr::opts_knit$set(root.dir = here::here())` in setup; show right vs wrong examples.
5. `## gtsummary 2.x argument hygiene` — `tbl_summary(include = NULL, by = NULL)` errors in 2.x; build args list conditionally with `purrr::compact()` or manual `if (!is.null(...))`; call via `rlang::exec(!!!args)`, not `do.call` (lazy promises break gtsummary's argument checking).
6. `## ggplot 4.0 deprecations` — `geom_errorbarh()` deprecated; switch to `geom_errorbar(orientation = "y")` or `coord_flip()` on plain `geom_errorbar()`.
7. `## cache: true does not invalidate on data change` — `cache: true` keys on chunk code only; show `cache.extra = digest::digest(file.info(data_path)$mtime)` or move to `freeze: auto` in `_quarto.yml` for project-wide caching tied to source-file mtimes.
8. `## reference.docx path resolution` — Pandoc resolves `reference-doc:` relative to the qmd, not the project root; with the qmd in `inst/templates/`, place `reference.docx` in the same directory; show wrong vs right.
9. `## embed-resources is HTML-only` — `embed-resources: true` is silently ignored for docx (or warns); for docx, Pandoc embeds images by default; remove the option from your docx format block.
10. `## TinyTeX is not needed for docx` — `quarto install tinytex` is for PDF output only; docx-only pipelines don't need a LaTeX install; document this so users don't waste time on a 250 MB install.
11. `## Stale R library state between Rscript invocations` — symptom: one render works, the next reports "no package called 'dplyr'"; usually a parallel install or broken DESCRIPTION; report and retry, don't try to fix from inside the analysis pipeline.
12. `## "Not applicable" as structural NA` — survey skip patterns produce string "Not applicable"; replace with NA but document explicitly via a missingness summary; do NOT impute.

Each section: 3-5 sentences + (where applicable) a short ```r``` code block showing wrong vs right.

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-reporting/references/quarto-docx-pitfalls.md
wc -l skills/r-reporting/references/quarto-docx-pitfalls.md
```

Expected: zero `%>%` hits; line count between 140 and 200.

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/references/quarto-docx-pitfalls.md
git commit -m "docs(r-reporting): add quarto-docx-pitfalls reference

Generalises the Robyn project lessons: !r in YAML, --output and
embed-resources, library(quarto) eager load, include_graphics
paths, gtsummary 2.x, ggplot 4.0 deprecations, cache invalidation,
reference.docx resolution, embed-resources for docx, TinyTeX
unneeded for docx, stale library state, structural NA."
```

---

## Task 8: Write `references/word-figure-table-patterns.md`

**Files:**
- Create: `skills/r-reporting/references/word-figure-table-patterns.md`
- Target: ~200 lines

- [ ] **Step 1: Create the file with required outline**

Required H1: `# Figure & Table Patterns for Word`

Required sections (in order):

1. **The gtsummary -> flextable -> docx pipeline** — `as_flex_table()` is canonical; show full example with `set_table_properties(width = 1, layout = "autofit", align = "center")`, `fontsize(size = 10, part = "all")`, `bold(part = "header")`.
2. **gtsummary 2.x argument hygiene** — same as in `quarto-docx-pitfalls.md` but with the focus on table-build callers.
3. **gt -> docx native (`gtsave("table.docx")`)** — works for simple tables; loses styling fidelity for non-trivial cases; not recommended for production reports; OK for quick previews.
4. **gt -> PNG fallback** — when flextable can't represent the table (gtExtras `gt_sparkline`, `gt_plt_bar`, embedded plots, conditional images): `gtsave("table.png", zoom = 2)` then `knitr::include_graphics()`. Cite this as a deliberate fallback; document the tradeoff (loss of accessibility, no copy-paste of values) so future maintainers don't think it's the default.
5. **Conditional formatting in flextable** — `bold(i = ~p_value < 0.05, j = "p_value")`; `color(i = ~estimate < 0, j = "estimate", color = "#B22222")`; `bg(i = ..., j = ..., bg = "lightgray")`. Cleaner than gt's `tab_style(cells_body(...))` for Word output.
6. **The RDS cache pattern** — full `04_model.R` build + `report.qmd` consumer side-by-side; rationale (avoid re-running gtsummary inside render context; consistent package versions; faster iteration).
7. **Multi-table merging** — `flextable::compose()` for headers; `flextable::merge_h()` and `merge_v()` for cell merges; for side-by-side tables, prefer `tbl_merge()` BEFORE `as_flex_table()` (gtsummary handles column dedup natively).
8. **Figure sizing for letter/A4** — recommended defaults: 8" × 5" at 150 dpi for single-panel; 8" × 7" for 2-row patchwork; 8" × 9" for 3-row; heights >9" risk pagination glitches. Show the YAML execute defaults and per-chunk overrides via `#| fig-width:` / `#| fig-height:`.
9. **ggplot theming for print** — opaque white backgrounds (`theme(plot.background = element_rect(fill = "white", colour = NA))`); base size ≥ 11; viridis or Color Brewer palettes; opaque legend backgrounds; explicit axis titles with units.
10. **Including pre-built figures** — `knitr::include_graphics(fig("foo.png"))` with `knitr::opts_knit$set(root.dir = here::here())`; never use `here::here()` absolute paths inside `include_graphics()` if `root.dir` is set (path is interpreted as already-rooted and breaks).
11. **Centering in Word** — figure centering is a reference.docx Figure-style fix; table centering happens at TWO layers (flextable's `align = "center"` AND the Table style in styles.xml — defense in depth). Don't add `\centering` or alignment markup to the qmd.
12. **Figure captions and cross-references** — Quarto supports `#| label: fig-foo` + `#| fig-cap: "..."` plus `@fig-foo` in body; in docx output, captions appear below the figure with `ImageCaption` styling. To restyle captions, edit the `ImageCaption` style in reference.docx.

Each section: 4-8 sentences + at least one R code block.

- [ ] **Step 2: Convention check**

```bash
grep -n '%>%' skills/r-reporting/references/word-figure-table-patterns.md
wc -l skills/r-reporting/references/word-figure-table-patterns.md
```

Expected: zero `%>%` hits; line count between 160 and 220.

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/references/word-figure-table-patterns.md
git commit -m "docs(r-reporting): add word-figure-table-patterns reference

Covers as_flex_table, RDS cache pattern, gt -> PNG fallback,
conditional formatting, multi-table merging, figure sizing,
ggplot print theming, include_graphics path resolution, and
two-layer table centering."
```

---

## Task 9: Write `scripts/make_reference_doc.R`

**Files:**
- Create: `skills/r-reporting/scripts/make_reference_doc.R`
- Target: ~210 lines

This is the load-bearing artifact for the five style invariants. Adapted from the working version in the Robyn project, parameterised, with Heading 1 page break + Figure/Table centering + footer patching added.

- [ ] **Step 1: Write the script**

Create `skills/r-reporting/scripts/make_reference_doc.R`:

```r
## ============================================================================
## Script: make_reference_doc.R
## Description: Generate a Pandoc reference.docx with minimalist defaults for
##              Word output from R Quarto reports. Patches styles.xml (Normal,
##              Heading 1, Figure, Table, ImageCaption) and word/footer1.xml.
##
## Usage:       source(here::here("analysis", "make_reference_doc.R"))
##              # or with overrides:
##              make_reference_doc(
##                ref_path           = "report/reference.docx",
##                font               = "Calibri",
##                body_size_pt       = 11,
##                body_line          = "1.5",   # one of "1", "1.5", "2"
##                heading1_pagebreak = TRUE,
##                heading1_centered  = TRUE,
##                page_numbers       = TRUE
##              )
##
## R packages:  here, xml2, zip
## ============================================================================

suppressPackageStartupMessages({
  library(here)
  library(xml2)
})

make_reference_doc <- function(
  ref_path           = here::here("inst", "templates", "reference.docx"),
  font               = "Calibri",
  body_size_pt       = 11L,
  body_line          = "1.5",
  heading1_pagebreak = TRUE,
  heading1_centered  = TRUE,
  page_numbers       = TRUE
) {
  stopifnot(
    is.character(ref_path), length(ref_path) == 1L,
    is.character(font), length(font) == 1L,
    is.numeric(body_size_pt), body_size_pt >= 8L, body_size_pt <= 16L,
    body_line %in% c("1", "1.5", "2"),
    is.logical(heading1_pagebreak), is.logical(heading1_centered),
    is.logical(page_numbers)
  )

  ## -------------------------------------------------------------------------
  ## 1. Resolve a pandoc binary (prefer the one bundled with Quarto)
  ## -------------------------------------------------------------------------
  pandoc_bin <- Sys.which("pandoc")
  if (nzchar(pandoc_bin) == 0L) {
    quarto_bin <- Sys.which("quarto")
    if (nzchar(quarto_bin) == 0L) {
      stop("Neither pandoc nor quarto is on PATH; cannot generate reference doc.")
    }
    candidate <- file.path(dirname(quarto_bin), "tools", "pandoc")
    if (file.exists(candidate)) {
      pandoc_bin <- candidate
    } else {
      candidates <- list.files(
        file.path(dirname(quarto_bin), "tools"),
        pattern = "^pandoc$",
        recursive = TRUE,
        full.names = TRUE
      )
      if (length(candidates) > 0L) pandoc_bin <- candidates[[1]]
      else stop("Cannot locate pandoc binary alongside quarto.")
    }
  }
  message("Using pandoc: ", pandoc_bin)

  ## -------------------------------------------------------------------------
  ## 2. Extract Pandoc's default reference docx
  ## -------------------------------------------------------------------------
  dir.create(dirname(ref_path), recursive = TRUE, showWarnings = FALSE)
  if (file.exists(ref_path)) file.remove(ref_path)
  status <- system2(
    pandoc_bin,
    args = c("-o", shQuote(ref_path), "--print-default-data-file", "reference.docx"),
    stdout = "", stderr = "",
    wait = TRUE
  )
  if (status != 0L || !file.exists(ref_path)) {
    stop("pandoc --print-default-data-file failed (exit ", status, ").")
  }
  message("Extracted default reference.docx to: ", ref_path)

  ## -------------------------------------------------------------------------
  ## 3. Unzip into a temp work dir
  ## -------------------------------------------------------------------------
  work_dir <- tempfile("refdocx_")
  dir.create(work_dir)
  on.exit(unlink(work_dir, recursive = TRUE), add = TRUE)
  utils::unzip(ref_path, exdir = work_dir)

  ## -------------------------------------------------------------------------
  ## 4. Patch styles.xml
  ## -------------------------------------------------------------------------
  styles_path <- file.path(work_dir, "word", "styles.xml")
  stopifnot(file.exists(styles_path))

  ns <- c(w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
  styles <- xml2::read_xml(styles_path)

  line_value <- switch(body_line, `1` = "240", `1.5` = "360", `2` = "480")
  font_size_halfpt <- as.character(as.integer(body_size_pt) * 2L)

  patch_body_styling <- function(ppr) {
    for (existing in xml2::xml_find_all(ppr, "w:spacing", ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(ppr, "w:jc",      ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(ppr, "w:spacing", `w:line` = line_value, `w:lineRule` = "auto")
    xml2::xml_add_child(ppr, "w:jc",      `w:val`  = "both")
  }

  ensure_pPr <- function(parent) {
    pPr <- xml2::xml_find_first(parent, "w:pPr", ns)
    if (inherits(pPr, "xml_missing")) {
      pPr <- xml2::xml_add_child(parent, "w:pPr", .where = 0L)
    }
    pPr
  }

  ensure_rPr <- function(parent) {
    rPr <- xml2::xml_find_first(parent, "w:rPr", ns)
    if (inherits(rPr, "xml_missing")) {
      rPr <- xml2::xml_add_child(parent, "w:rPr")
    }
    rPr
  }

  # 4a. Body — patch BOTH docDefaults and Normal style
  doc_default_ppr <- xml2::xml_find_first(
    styles, "//w:docDefaults/w:pPrDefault/w:pPr", ns
  )
  if (!inherits(doc_default_ppr, "xml_missing")) patch_body_styling(doc_default_ppr)

  doc_default_rpr <- xml2::xml_find_first(
    styles, "//w:docDefaults/w:rPrDefault/w:rPr", ns
  )
  if (!inherits(doc_default_rpr, "xml_missing")) {
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:rFonts", ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:sz",      ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:szCs",    ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(doc_default_rpr, "w:rFonts",
                        `w:ascii` = font, `w:hAnsi` = font, `w:cs` = font)
    xml2::xml_add_child(doc_default_rpr, "w:sz",   `w:val` = font_size_halfpt)
    xml2::xml_add_child(doc_default_rpr, "w:szCs", `w:val` = font_size_halfpt)
  }

  normal <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Normal']", ns)
  if (inherits(normal, "xml_missing")) {
    stop("Normal style not found in reference.docx styles.xml.")
  }
  patch_body_styling(ensure_pPr(normal))

  # 4b. Heading 1 — page break + center
  heading1 <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Heading1']", ns)
  if (!inherits(heading1, "xml_missing")) {
    h1_ppr <- ensure_pPr(heading1)
    if (heading1_pagebreak) {
      for (existing in xml2::xml_find_all(h1_ppr, "w:pageBreakBefore", ns)) xml2::xml_remove(existing)
      xml2::xml_add_child(h1_ppr, "w:pageBreakBefore")
    }
    if (heading1_centered) {
      for (existing in xml2::xml_find_all(h1_ppr, "w:jc", ns)) xml2::xml_remove(existing)
      xml2::xml_add_child(h1_ppr, "w:jc", `w:val` = "center")
    }
  }

  # 4c. Figure — center
  figure <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Figure']", ns)
  if (!inherits(figure, "xml_missing")) {
    fig_ppr <- ensure_pPr(figure)
    for (existing in xml2::xml_find_all(fig_ppr, "w:jc", ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(fig_ppr, "w:jc", `w:val` = "center")
  }

  # 4d. Table — center (paragraph style on Pandoc-emitted Table style if present)
  tbl <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Table']", ns)
  if (!inherits(tbl, "xml_missing")) {
    tbl_ppr <- ensure_pPr(tbl)
    for (existing in xml2::xml_find_all(tbl_ppr, "w:jc", ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(tbl_ppr, "w:jc", `w:val` = "center")
  }

  xml2::write_xml(styles, styles_path)

  # 4e. Sanity check — re-read and confirm parses
  invisible(xml2::read_xml(styles_path))
  message("Patched styles.xml.")

  ## -------------------------------------------------------------------------
  ## 5. Patch footer1.xml — minimalist centered page number
  ## -------------------------------------------------------------------------
  if (page_numbers) {
    footer_path <- file.path(work_dir, "word", "footer1.xml")
    if (file.exists(footer_path)) {
      footer_xml <- sprintf(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="Footer"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:fldSimple w:instr=" PAGE \\* MERGEFORMAT ">
      <w:r><w:t>1</w:t></w:r>
    </w:fldSimple>
  </w:p>
</w:ftr>'
      )
      writeLines(footer_xml, footer_path, useBytes = TRUE)
      invisible(xml2::read_xml(footer_path))   # sanity check parses
      message("Patched footer1.xml (centered page number).")
    } else {
      message("No footer1.xml in template; skipping page number patch.")
    }
  }

  ## -------------------------------------------------------------------------
  ## 6. Re-zip into the final reference.docx
  ## -------------------------------------------------------------------------
  unlink(ref_path)

  if (requireNamespace("zip", quietly = TRUE)) {
    entries <- list.files(work_dir, recursive = TRUE, all.files = TRUE,
                          include.dirs = FALSE, no.. = TRUE)
    zip::zip(zipfile = ref_path, files = entries, root = work_dir, mode = "mirror")
  } else {
    if (!nzchar(Sys.which("zip"))) {
      stop("Need either the `zip` R package or a system `zip` binary on PATH.")
    }
    old_wd <- setwd(work_dir)
    on.exit(setwd(old_wd), add = TRUE, after = FALSE)
    status <- system2("zip", c("-rq", shQuote(ref_path), "."))
    if (status != 0L) stop("system zip failed (exit ", status, ").")
  }

  message("Wrote: ", ref_path)
  invisible(ref_path)
}

# When sourced (not loaded as a function), invoke with defaults.
if (!exists(".reporting_test_skip_run", inherits = FALSE)) {
  if (sys.nframe() == 0L || identical(sys.function(1L), make_reference_doc)) {
    # script-mode invocation
    make_reference_doc()
  }
}
```

- [ ] **Step 2: Syntax check via Rscript -e (no rendering, just parse)**

```bash
Rscript -e 'parse("skills/r-reporting/scripts/make_reference_doc.R")'
```

Expected: silent success (no error). If `Rscript` is unavailable, skip — convention tests will still flag obvious issues.

- [ ] **Step 3: Convention check**

```bash
grep -n '%>%' skills/r-reporting/scripts/make_reference_doc.R
grep -nE '^[^#]*[A-Za-z_][A-Za-z0-9_]+\s*=\s*[^=,)]' skills/r-reporting/scripts/make_reference_doc.R | grep -vE '\b(function|switch|stop|message|writeLines|c|sprintf|file\.|list\.|dir\.|on\.exit|setwd|system2|args|stdout|stderr|wait|exist|requireNamespace|zip::zip|w:line|w:lineRule|w:val|w:ascii|w:hAnsi|w:cs|w:line|where|recursive|all\.files|include\.dirs|no\.\.|inherits|skip)' || true
wc -l skills/r-reporting/scripts/make_reference_doc.R
```

Expected: zero `%>%` hits; the `=`-grep should show no matches outside function-arg context (the second grep filters known false positives — manual review any remaining hits).

- [ ] **Step 4: Commit**

```bash
git add skills/r-reporting/scripts/make_reference_doc.R
git commit -m "feat(r-reporting): add make_reference_doc.R generator

Parameterised generator producing a reference.docx with the five
style invariants: 1.5x line + full justify + Calibri body, Heading 1
page break + center + bold, Figure center, Table center, simple
centered page number footer. Sanity-checks XML before re-zipping
with mode = mirror."
```

---

## Task 10: Write `scripts/report_template.qmd`

**Files:**
- Create: `skills/r-reporting/scripts/report_template.qmd`
- Target: ~110 lines

The qmd starter that `/r-report` copies into a fresh project. Includes the path helpers, setup chunk, and three sample sections so the first render produces visible output.

- [ ] **Step 1: Write the qmd template**

Create `skills/r-reporting/scripts/report_template.qmd`:

```markdown
---
title: "{{report_title}}"
author: "{{author}}"
date: "`r if (nzchar(params$date)) params$date else format(Sys.Date())`"
format:
  docx:
    toc: true
    toc-depth: 3
    number-sections: true
    fig-width: 8
    fig-height: 5
    reference-doc: reference.docx
resource-path:
  - "."
  - ".."
  - "../.."
params:
  date: ""
---

```{r setup, include = FALSE}
knitr::opts_chunk$set(
  echo = FALSE, warning = FALSE, message = FALSE,
  fig.width = 8, fig.height = 5, dpi = 150
)
knitr::opts_knit$set(root.dir = here::here())

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(flextable)
  library(here)
  library(readr)
})

fig <- function(file) file.path("output", "figures", file)
tbl <- function(file) here::here("output", "tables",  file)
mod <- function(file) here::here("output", "models",  file)

read_csv_safe <- function(p) suppressMessages(readr::read_csv(p, show_col_types = FALSE))
```

# Executive Summary

(One-page synthesis. Replace this with bottom-line findings, key effect estimates with uncertainty, and recommendations.)

# Background and Objectives

(Scientific background, research questions, scope.)

# Data and Methods

## Data sources

(Source documentation; provenance; data quality.)

## Statistical methods

(Methods with citations for non-standard approaches; software versions; assumption checking; missing data handling.)

# Results

## Demographics

```{r tbl-demographics}
#| tbl-cap: "Participant characteristics by group."
table_one_path <- tbl("01_table_one.rds")
if (file.exists(table_one_path)) {
  readRDS(table_one_path) |>
    as_flex_table() |>
    flextable::set_table_properties(width = 1, layout = "autofit", align = "center") |>
    flextable::fontsize(size = 10, part = "all")
} else {
  flextable::flextable(data.frame(Note = "Build the table upstream and saveRDS to output/tables/01_table_one.rds."))
}
```

## Primary outcome

```{r fig-primary}
#| fig-cap: "Primary outcome trajectory by group."
primary_fig_path <- fig("01_primary.png")
if (file.exists(here::here(primary_fig_path))) {
  knitr::include_graphics(primary_fig_path)
} else {
  cat("Build the figure upstream and write to output/figures/01_primary.png.")
}
```

# Sensitivity Analyses

(Document robustness under alternative assumptions.)

# Limitations

(Honest acknowledgment of biases, precision constraints, generalisability.)

# Recommendations

(Actionable, prioritised, tied to findings; respect consultant-client boundary.)

# Reproducibility

```{r reproducibility}
sessionInfo()
```

# References

(Citations for non-standard methods, guidelines followed, background literature.)
```

The `{{report_title}}` and `{{author}}` placeholders are filled in by the `/r-report` command using simple string replacement at scaffold time.

- [ ] **Step 2: Sanity check (no rendering)**

```bash
wc -l skills/r-reporting/scripts/report_template.qmd
grep -c '%>%' skills/r-reporting/scripts/report_template.qmd
grep -c '<- ' skills/r-reporting/scripts/report_template.qmd
```

Expected: line count between 80 and 130; zero `%>%`; multiple `<-` (assignment usage).

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/scripts/report_template.qmd
git commit -m "feat(r-reporting): add report_template.qmd starter

Opinionated qmd with format: docx + reference-doc, resource-path
for nested layouts, knitr::opts_knit root.dir, the fig/tbl/mod
helpers, and section stubs (Exec Summary, Background, Methods,
Results, Sensitivity, Limitations, Recommendations, Reproducibility,
References) with safe fallbacks when output artifacts do not yet
exist."
```

---

## Task 11: Write `scripts/render_to_docx.R`

**Files:**
- Create: `skills/r-reporting/scripts/render_to_docx.R`
- Target: ~80 lines

- [ ] **Step 1: Write the render wrapper**

Create `skills/r-reporting/scripts/render_to_docx.R`:

```r
## ============================================================================
## Script: render_to_docx.R
## Description: Render a Quarto report to docx via the Quarto CLI (system2).
##              Avoids the R `quarto` package — works on machines where it is
##              not installed. Produces a timestamped output for audit trail.
##
## Usage:       source(here::here("analysis", "render_to_docx.R"))
##              # or with overrides:
##              render_to_docx(
##                input_qmd  = "inst/templates/report.qmd",
##                output_dir = "output"
##              )
##
## R packages:  here
## ============================================================================

suppressPackageStartupMessages(library(here))

render_to_docx <- function(
  input_qmd  = here::here("inst", "templates", "report.qmd"),
  output_dir = here::here("output")
) {
  stopifnot(file.exists(input_qmd))

  quarto_bin <- Sys.which("quarto")
  if (nzchar(quarto_bin) == 0L) {
    stop("Quarto CLI not found on PATH. Install from https://quarto.org and rerun.")
  }
  message("Using Quarto CLI: ", quarto_bin)
  message("Rendering: ", input_qmd)

  result <- system2(
    quarto_bin,
    args = c(
      "render", shQuote(input_qmd),
      "--to", "docx",
      "--execute-dir", shQuote(here::here())
    ),
    stdout = "", stderr = "",
    wait = TRUE
  )
  if (result != 0L) {
    stop(sprintf("quarto render failed (exit %d).", result))
  }

  # Default output: same dir as the qmd, same basename, .docx extension.
  default_path <- sub("\\.qmd$", ".docx", input_qmd, ignore.case = TRUE)
  stopifnot(file.exists(default_path))

  # Timestamped audit trail name.
  ts <- format(Sys.time(), "%Y%m%d_%H%M%S")
  ts_basename <- sub("\\.docx$", paste0("_", ts, ".docx"), basename(default_path))

  in_template_dir <- file.path(dirname(default_path), ts_basename)
  file.rename(default_path, in_template_dir)

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  output_dest <- file.path(output_dir, ts_basename)
  file.copy(in_template_dir, output_dest, overwrite = TRUE)

  message(sprintf("DOCX written to: %s", output_dest))
  invisible(output_dest)
}

# When sourced as a script, invoke with defaults.
if (sys.nframe() == 0L) {
  render_to_docx()
}
```

- [ ] **Step 2: Syntax check**

```bash
Rscript -e 'parse("skills/r-reporting/scripts/render_to_docx.R")'
```

Expected: silent success.

- [ ] **Step 3: Convention check**

```bash
grep -n '%>%' skills/r-reporting/scripts/render_to_docx.R
wc -l skills/r-reporting/scripts/render_to_docx.R
```

Expected: zero `%>%`; line count between 60 and 90.

- [ ] **Step 4: Commit**

```bash
git add skills/r-reporting/scripts/render_to_docx.R
git commit -m "feat(r-reporting): add render_to_docx.R wrapper

system2() against the Quarto CLI; --execute-dir set to project
root; timestamped audit trail copy to output/. Avoids the R quarto
package so the workflow runs on machines without it."
```

---

## Task 12: Write `scripts/quarto_yml_block.yml`

**Files:**
- Create: `skills/r-reporting/scripts/quarto_yml_block.yml`
- Target: ~25 lines

The snippet `/r-report` merges into an existing `_quarto.yml` (or creates a fresh one with).

- [ ] **Step 1: Write the snippet**

Create `skills/r-reporting/scripts/quarto_yml_block.yml`:

```yaml
project:
  type: default

  # Render only the report by default; other .qmd files in the repo are not
  # treated as project documents unless explicitly listed.
  render:
    - {{report_qmd_path}}

  # Run R chunks from the project root so here::here() and project-relative
  # paths (output/figures/*.png, output/tables/*.html) resolve correctly.
  execute-dir: project

  # Make generated figures and tables visible to Quarto's resource resolver
  # so quarto render and quarto preview can find them.
  resources:
    - "output/figures/*.png"
    - "output/tables/*.html"
    - "output/tables/*.csv"
```

The `{{report_qmd_path}}` placeholder is filled in by `/r-report` (e.g. `inst/templates/report.qmd` for packages, `report/report.qmd` otherwise).

- [ ] **Step 2: Sanity check**

```bash
wc -l skills/r-reporting/scripts/quarto_yml_block.yml
grep -c '%>%' skills/r-reporting/scripts/quarto_yml_block.yml
```

Expected: line count between 15 and 30; zero `%>%`.

- [ ] **Step 3: Commit**

```bash
git add skills/r-reporting/scripts/quarto_yml_block.yml
git commit -m "feat(r-reporting): add quarto_yml_block.yml snippet

Project-level Quarto config block for /r-report to merge: render
target list, execute-dir: project, and a resources glob covering
output/figures and output/tables."
```

---

## Task 13: Write `commands/r-report.md`

**Files:**
- Create: `commands/r-report.md`
- Target: ~150 lines

- [ ] **Step 1: Write the command**

Create `commands/r-report.md`:

```markdown
---
description: Scaffold and render a clean, minimalist Word (.docx) report from an R analysis
---


# Report Pipeline (Quarto -> Word)

Guided workflow: detect project type, scaffold the qmd + reference docx + render wrapper, generate the reference docx with the five style invariants, run the first render. Pairs with the `r-reporting` skill for mechanics and troubleshooting.

## Prerequisites

- Existing R project (R package, analysis project, or targets pipeline).
- Quarto CLI on PATH (`quarto --version` succeeds).
- R packages: `here`, `xml2`, `zip`, `flextable`, `readr`, `dplyr`, `ggplot2`. Install if missing.

## Progress Tracking

Use TaskCreate at the start of this workflow — one task per phase below.

- "Phase 1: Detect project type and target paths"
- "Phase 2: Scaffold artifacts (qmd, render wrapper, reference docx generator, _quarto.yml block)"
- "Phase 3: Generate reference.docx"
- "Phase 4: First render"
- "Phase 5: Verification"

## Steps

### Step 1: Detect project type

**Skill:** `r-reporting`

Inspect the working directory:

- `DESCRIPTION` + `R/` -> **R package**. Target paths: `inst/templates/report.qmd`, `inst/templates/reference.docx`, `R/render_report.R`, `inst/templates/make_reference_doc.R`.
- `_targets.R` -> **targets pipeline**. Target paths: `report/report.qmd`, `report/reference.docx`, `R/render_report.R` or `analysis/05_report.R`, `analysis/make_reference_doc.R`.
- Otherwise (`.Rproj` and/or `.R` files) -> **analysis project**. Target paths: `report/report.qmd`, `report/reference.docx`, `analysis/05_report.R`, `analysis/make_reference_doc.R`.

If none of the above detect, **abort** with: "No R project detected. Run from the project root, or initialise with /r-project-setup."

**Gate:** target paths printed; user has had a chance to override before scaffold begins.

### Step 2: Refuse to clobber

**Skill:** `r-reporting`

If `report.qmd` already exists at the target path:

- Read its YAML frontmatter and summarise (title, format list, reference-doc path).
- Ask: "A report.qmd already exists. Overwrite, scaffold a sidecar (`report_v2.qmd`), or abort?"
- Default to abort if the user is silent.

**Gate:** safe-to-write decision recorded.

### Step 3: Scaffold artifacts

**Skill:** `r-reporting`

Copy the four scripts from the skill into the project, performing the listed substitutions:

| Source | Destination | Substitutions |
|---|---|---|
| `skills/r-reporting/scripts/report_template.qmd` | target qmd path | `{{report_title}}` -> ask user (default to project basename); `{{author}}` -> ask user (default to git config user.name) |
| `skills/r-reporting/scripts/render_to_docx.R` | render-script path (Step 1) | none |
| `skills/r-reporting/scripts/make_reference_doc.R` | adjacent to target qmd (or `analysis/`) | none |
| `skills/r-reporting/scripts/quarto_yml_block.yml` | merge into project `_quarto.yml` (create if missing) | `{{report_qmd_path}}` -> target qmd path |

If `_quarto.yml` already exists, merge by appending (or splice into) the `project:`, `execute-dir:`, and `resources:` keys without overwriting unrelated keys (e.g. `website:` or `book:` configs).

**Gate:** all four artifacts in place; project `_quarto.yml` valid YAML (`quarto check` passes).

### Step 4: Generate reference.docx

**Skill:** `r-reporting`

Run the bundled generator with defaults:

```r
source("path/to/make_reference_doc.R")
```

Confirms `reference.docx` exists adjacent to the target qmd. Inspect file size (should be 30-50 KB).

**Gate:** reference.docx exists and is non-empty.

### Step 5: First render

**Skill:** `r-reporting`

Run the render wrapper:

```r
source("path/to/render_to_docx.R")
```

Confirms exit code 0 and a timestamped docx in `output/`.

**Gate:** docx exists, file size > 20 KB, no render errors.

### Step 6: Verification

**Skill:** `r-reporting`

- macOS: `system2("open", path)` to preview.
- Linux: `system2("xdg-open", path)` if available; otherwise print the path.
- Windows: `shell.exec(path)`.
- CI / headless: print path only.

If the user reports issues (figures not centered, page breaks missing, footer wrong), dispatch back to the `r-reporting` skill — most fixes are reference.docx regeneration with a different `make_reference_doc()` argument.

**Gate:** user has visually verified the output OR explicitly skipped verification.

## Abort Conditions

- No R project detected (see Step 1).
- Quarto CLI not on PATH (see Prerequisites).
- Working tree dirty (warn but allow with explicit user confirmation).
- `_quarto.yml` exists with conflicting top-level keys (`project: type: website` or `book`) — do not auto-merge; ask the user.

## Examples

```text
# Inside a fresh R consulting project
/r-report

# Output (paraphrased):
# Detected: analysis project
# Target qmd: report/report.qmd
# Target render script: analysis/05_report.R
# ...
```

```text
# Inside a package project where report.qmd already exists
/r-report

# Output:
# Detected: R package
# inst/templates/report.qmd exists.
# Title: "Q3 2026 client report"
# Overwrite | Sidecar (report_v2.qmd) | Abort?
```
```

- [ ] **Step 2: Run structural tests**

```bash
python3 tests/run_all.py --layer 1 2>&1 | tail -10
wc -l commands/r-report.md
```

Expected: structural tests pass (frontmatter has `description`; line count ≤200).

- [ ] **Step 3: Commit**

```bash
git add commands/r-report.md
git commit -m "feat(commands): add /r-report orchestrating command

Detect project type, scaffold qmd/render-wrapper/reference-doc
generator, merge _quarto.yml block, generate reference.docx,
first render, verification. References the r-reporting skill at
each step."
```

---

## Task 14: Add cross-reference in `r-quarto/SKILL.md`

**Files:**
- Modify: `skills/r-quarto/SKILL.md`

- [ ] **Step 1: Read the current Boundary block**

```bash
grep -n "Boundary" skills/r-quarto/SKILL.md
```

Expected: there is a `> **Boundary:**` line near the top of the body.

- [ ] **Step 2: Append the cross-reference**

Use the Edit tool to extend the Boundary block. Find:

```markdown
> **Boundary:** Quarto documents, sites, and presentations. For R package vignettes, use r-package-dev instead.
```

Replace with:

```markdown
> **Boundary:** Quarto documents, sites, and presentations. For R package vignettes, use r-package-dev instead. For Word/.docx deliverables (reference docx, page breaks, footers, figure/table centering), use **r-reporting**.
```

- [ ] **Step 3: Run structural and convention tests**

```bash
python3 tests/run_all.py --layer 1 --layer 1b 2>&1 | tail -10
```

Expected: still passing; no length regression.

- [ ] **Step 4: Commit**

```bash
git add skills/r-quarto/SKILL.md
git commit -m "docs(r-quarto): cross-reference r-reporting in boundary

One-line pointer to r-reporting for Word/.docx deliverables. No
content moved out of r-quarto."
```

---

## Task 15: Add cross-reference in `r-tables/SKILL.md`

**Files:**
- Modify: `skills/r-tables/SKILL.md`

- [ ] **Step 1: Identify the Output Formats section**

```bash
grep -n "Output Formats\|Word — gtsummary -> flextable" skills/r-tables/SKILL.md
```

Expected: line with `## Output Formats` heading and a comment mentioning the gtsummary -> flextable pipeline.

- [ ] **Step 2: Append a cross-reference after the Word example block**

Use the Edit tool to find the closing of the Word example block in `## Output Formats` (the line that ends the docx code fence with ``` followed by a blank line). Add a one-line reference immediately after:

```markdown
For an end-to-end Word report scaffold (reference.docx + path helpers + render wrapper), see **r-reporting**.
```

- [ ] **Step 3: Run structural and convention tests**

```bash
python3 tests/run_all.py --layer 1 --layer 1b 2>&1 | tail -10
```

Expected: still passing.

- [ ] **Step 4: Commit**

```bash
git add skills/r-tables/SKILL.md
git commit -m "docs(r-tables): cross-reference r-reporting after Word example

One-line pointer to r-reporting for end-to-end Word report
scaffolding. No content moved out of r-tables."
```

---

## Task 16: Update `hooks/session-start` to surface r-reporting

**Files:**
- Modify: `hooks/session-start`

The hook needs to surface r-reporting when a project's qmd produces docx, OR when a `reference.docx` is present.

- [ ] **Step 1: Add detection logic**

Use the Edit tool. Locate the detection-flag block at the top (where `is_quarto`, `is_targets`, etc. are set). Add a new flag right after the `is_quarto` block:

```bash
# Word report pipeline: any *.qmd with format: docx, OR a reference.docx file
is_word_report=false
if grep -lE '^\s*(format:\s*docx|reference-doc:)' --include='*.qmd' -r . 2>/dev/null | head -n 1 | read -r; then
  is_word_report=true
fi
if [ -f "reference.docx" ] || [ -f "inst/templates/reference.docx" ] || [ -f "report/reference.docx" ]; then
  is_word_report=true
fi
```

- [ ] **Step 2: Add the skills line**

Locate the `# --- Build context ---` block and the cascade of `if [ "$is_quarto" = true ] ...` lines. Add this line right after the `is_quarto` block:

```bash
if [ "$is_word_report" = true ]; then
  skills="${skills}Word .docx report pipeline detected. Key skill: /r-reporting. Command: /r-report.\\n"
fi
```

- [ ] **Step 3: Test the hook locally**

```bash
bash hooks/session-start
```

Expected: from a fresh repo state (no qmd with format: docx), output is roughly the same as before. From a directory containing a sample qmd with `format: docx`, the new line appears.

To test the positive case:

```bash
mkdir -p /tmp/rrep_hook_test && cd /tmp/rrep_hook_test
echo "---" > test.qmd
echo "format:" >> test.qmd
echo "  docx:" >> test.qmd
echo "---" >> test.qmd
bash /Users/alexandervantwisk/Desktop/Projects/supeRpowers/.claude/worktrees/r-reporting/hooks/session-start | head -5
cd - && rm -rf /tmp/rrep_hook_test
```

Expected: the hook output mentions `/r-reporting`.

- [ ] **Step 4: Commit**

```bash
git add hooks/session-start
git commit -m "feat(hooks): surface /r-reporting on docx project detection

Detection fires on any *.qmd with format: docx or reference-doc:,
or on the presence of a reference.docx in canonical locations
(., inst/templates/, report/)."
```

---

## Task 17: Add optional smoke test

**Files:**
- Create: `tests/smoke_r_report.sh`

- [ ] **Step 1: Write the smoke test**

Create `tests/smoke_r_report.sh`:

```bash
#!/usr/bin/env bash
# Smoke test: scaffold a minimal docx report into a temp directory and render it.
# Skipped if the Quarto CLI is not on PATH or Rscript is unavailable.
#
# Usage: bash tests/smoke_r_report.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v quarto >/dev/null 2>&1; then
  echo "SKIP: Quarto CLI not on PATH"
  exit 0
fi
if ! command -v Rscript >/dev/null 2>&1; then
  echo "SKIP: Rscript not on PATH"
  exit 0
fi

WORK="$(mktemp -d -t rrep_smoke_XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

echo "Smoke test working dir: $WORK"
cd "$WORK"

mkdir -p inst/templates output/figures output/tables

cp "$ROOT/skills/r-reporting/scripts/report_template.qmd" inst/templates/report.qmd
cp "$ROOT/skills/r-reporting/scripts/make_reference_doc.R" inst/templates/make_reference_doc.R
cp "$ROOT/skills/r-reporting/scripts/render_to_docx.R" inst/templates/render_to_docx.R

# Minimal _quarto.yml
cat > _quarto.yml <<'YML'
project:
  type: default
  render:
    - inst/templates/report.qmd
  execute-dir: project
  resources:
    - "output/figures/*.png"
    - "output/tables/*.html"
YML

# Substitute placeholders in the qmd
sed -i.bak 's|{{report_title}}|Smoke Test Report|; s|{{author}}|smoke|' inst/templates/report.qmd
rm -f inst/templates/report.qmd.bak

# Generate reference.docx
Rscript -e 'source("inst/templates/make_reference_doc.R"); make_reference_doc(ref_path = "inst/templates/reference.docx")'

if [ ! -s inst/templates/reference.docx ]; then
  echo "FAIL: reference.docx not generated"
  exit 1
fi

# Render
Rscript -e 'source("inst/templates/render_to_docx.R"); render_to_docx(input_qmd = "inst/templates/report.qmd", output_dir = "output")'

# Assert non-empty docx in output/
docx_count=$(find output -maxdepth 1 -type f -name '*.docx' | wc -l | tr -d ' ')
if [ "$docx_count" -lt 1 ]; then
  echo "FAIL: no docx produced in output/"
  exit 1
fi

docx_path=$(find output -maxdepth 1 -type f -name '*.docx' | head -n 1)
docx_size=$(wc -c < "$docx_path")
if [ "$docx_size" -lt 8000 ]; then
  echo "FAIL: docx suspiciously small ($docx_size bytes): $docx_path"
  exit 1
fi

echo "PASS: docx produced at $docx_path ($docx_size bytes)"
```

- [ ] **Step 2: Make executable and run**

```bash
chmod +x tests/smoke_r_report.sh
bash tests/smoke_r_report.sh 2>&1 | tail -20
```

Expected: either `SKIP: ...` (if Quarto/Rscript missing) or `PASS: docx produced at ... (NNNNN bytes)`. A `FAIL: ...` line means a real bug — diagnose against the most recent task touching the failing component.

- [ ] **Step 3: Commit**

```bash
git add tests/smoke_r_report.sh
git commit -m "test(smoke): add r-reporting end-to-end scaffold-and-render test

Creates a temp project, copies the four scripts, generates a
reference.docx, runs the render wrapper, and asserts a non-empty
docx (>=8 KB) lands in output/. Skips silently when Quarto or
Rscript is unavailable so CI without these tools stays green."
```

---

## Task 18: Final verification, plan-back-to-main, and PR prep

**Files:**
- Verify: all of the above.
- (Optional) merge feature/r-reporting back to main.

- [ ] **Step 1: Run the full test suite**

```bash
python3 tests/run_all.py 2>&1 | tail -40
```

Expected: all layers pass. Specifically:
- Layer 1 (structural): no new failures; r-reporting skill discovered with valid frontmatter; commands/r-report.md valid.
- Layer 1b (conventions): zero `%>%` in the new content; zero `=`-as-assignment.
- Layer 2 (routing): all 8 new entries (`route-065`–`route-072`) pass.

- [ ] **Step 2: Validate the plugin manifest**

```bash
claude plugin validate . 2>&1 | tail -20
```

Expected: validation passes (warnings tolerable). If `claude plugin validate` reports an error specific to r-reporting (e.g., glob coverage), inspect `.claude-plugin/plugin.json` — the manifest is glob-driven so new files under `skills/`, `commands/`, etc. are picked up automatically.

- [ ] **Step 3: Optional smoke render**

```bash
bash tests/smoke_r_report.sh 2>&1 | tail -10
```

Expected: `PASS: docx produced at ...` (or `SKIP` if Quarto absent).

- [ ] **Step 4: Final convention sweep**

```bash
grep -rn '%>%' skills/r-reporting/ commands/r-report.md --exclude=eval.md
grep -rn '%>%' tests/smoke_r_report.sh
```

Expected: zero hits in both.

- [ ] **Step 5: Verify line counts**

```bash
wc -l skills/r-reporting/SKILL.md commands/r-report.md \
      skills/r-reporting/references/*.md \
      skills/r-reporting/scripts/*.R \
      skills/r-reporting/scripts/*.qmd \
      skills/r-reporting/scripts/*.yml
```

Expected:
- `SKILL.md` ≤ 290
- `r-report.md` ≤ 200
- `reference-docx-anatomy.md` 200–280
- `quarto-docx-pitfalls.md` 140–200
- `word-figure-table-patterns.md` 160–220
- `make_reference_doc.R` 180–230
- `render_to_docx.R` 60–90
- `report_template.qmd` 80–130
- `quarto_yml_block.yml` 15–30

- [ ] **Step 6: Review the worktree commit log**

```bash
git log --oneline main..HEAD
```

Expected: 17 commits (one per Task 2-17 plus optionally a spec-pickup commit), each with a conventional-commits prefix and a clear single-purpose message.

- [ ] **Step 7: Decide on integration approach**

Options:
- **Direct merge to main:** if working solo, `git checkout main && git merge --no-ff feature/r-reporting` from the main worktree at `/Users/alexandervantwisk/Desktop/Projects/supeRpowers`. Push.
- **Pull request:** `gh pr create --base main --head feature/r-reporting --title "feat(r-reporting): skill + /r-report command" --body-file -` with a body summarising the spec, the artifacts shipped, and the test results.

Pause here for user confirmation before merging or pushing.

- [ ] **Step 8: Clean up the worktree (only after merge)**

```bash
cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers
git worktree remove .claude/worktrees/r-reporting
git branch -d feature/r-reporting    # if merged
```

Expected: worktree removed cleanly; branch deleted (or kept for reference).

---

## Self-Review Checklist (run after writing the plan, before kicking off implementation)

1. **Spec coverage.** Walk each section of `docs/superpowers/specs/2026-04-30-r-reporting-design.md` and find the corresponding task:
   - Goal / Non-goals / Scope decisions — Task 5 (skill body) + Task 13 (command). ✓
   - 12 scope decisions — all reflected in respective tasks. ✓
   - Artifact inventory — Tasks 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13. ✓
   - SKILL.md outline (14 sections) — Task 5 step 1 enumerates all. ✓
   - References (3 with deep outlines) — Tasks 6, 7, 8. ✓
   - Five style invariants — Task 9 implements all five. ✓
   - `/r-report` command flow (6 steps) — Task 13 enumerates all. ✓
   - Testing (routing, structural, convention, smoke) — Tasks 2 (routing), 17 (smoke); existing test infra covers structural + convention. ✓
   - Migration / coexistence — Tasks 14, 15. ✓
   - Risks — addressed in Task 9 (sanity check XML), Task 16 (platform-aware open), Task 17 (skip on missing tooling). ✓

2. **Placeholder scan.** No `TBD`, `TODO`, `fill in details`, or `similar to Task N` references in the plan. Each step has either (a) the actual content to write, (b) the actual command to run, or (c) the required outline + cross-link list for narrative content. Convention checks are real grep commands with expected outcomes.

3. **Type/name consistency.**
   - `make_reference_doc()` function signature: same args (`ref_path`, `font`, `body_size_pt`, `body_line`, `heading1_pagebreak`, `heading1_centered`, `page_numbers`) referenced consistently across Task 9 (script), Task 13 (command Step 4), Task 17 (smoke test).
   - `render_to_docx()` function signature: same args (`input_qmd`, `output_dir`) referenced consistently across Task 11 and Task 17.
   - Script paths: `skills/r-reporting/scripts/<name>` consistent across Tasks 9-12, 13, 17.
   - Project layout target paths: `inst/templates/report.qmd` (package), `report/report.qmd` (analysis/targets) consistent across spec, Task 13, Task 17.

If something drifts, fix it inline before kicking off implementation.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-30-r-reporting.md`. Two execution options:

1. **Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration. REQUIRED SUB-SKILL: `superpowers:subagent-driven-development`.
2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints. REQUIRED SUB-SKILL: `superpowers:executing-plans`.

Which approach?
