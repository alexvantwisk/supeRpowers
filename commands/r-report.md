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
