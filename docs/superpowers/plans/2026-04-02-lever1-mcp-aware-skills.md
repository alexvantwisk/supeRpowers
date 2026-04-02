# Lever 1: MCP-Aware Skills — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make skills proactively use btw/mcptools MCP tools to inspect the R session before writing code — gracefully degrading when MCP is unavailable.

**Architecture:** Three integration points layered into existing infrastructure: (1) session-start hook captures R version, platform, and key package versions, (2) 9 skills get MCP dispatch lines following the r-clinical template, (3) r-conventions gets two new sections for environment-aware coding and verify-after-write.

**Tech Stack:** Bash (hooks), Markdown (skills/rules), btw/mcptools MCP tools

---

### Task 1: Add Environment-Aware Coding and Verify-After-Write Sections to r-conventions.md

**Files:**
- Modify: `rules/r-conventions.md:128-138` (after Anti-Patterns table, before Function Design section)

- [ ] **Step 1: Add the two new sections after the Anti-Patterns table**

Insert the following after line 128 (after the `| Modify input in place | Return new object — immutability preferred |` row) and before line 129 (`## Function Design`):

```markdown
## Environment-Aware Coding

When an R session is available via btw/mcptools:

- **Before writing code:** Inspect data frames (`btw_tool_env_describe_data_frame`), check installed packages, read function docs
- **When uncertain about a function:** Read the help page (`btw_tool_docs_help_page`) rather than guessing from training data
- **After writing non-trivial code:** Run it and verify the output (see Verify After Write below)
- **When recommending packages:** Check if they're installed first (`btw_tool_sessioninfo_is_package_installed`)

These are enhancement behaviors. All conventions work without MCP — MCP makes them more precise.

## Verify After Write

For non-trivial R code (data transformations, model fits, table generation), verify output when an R session is available:

1. Run the code via btw
2. Check for errors and warnings
3. Verify output dimensions and structure match expectations
4. Fix issues before presenting to the user

Skip verification for: simple one-liners, package scaffolding, configuration files, code that requires data not in the session.
```

- [ ] **Step 2: Verify the file is valid and within limits**

Run:
```bash
wc -l rules/r-conventions.md
```
Expected: ~157 lines. This is slightly over the 150-line soft limit for rules. Acceptable because Lever 2 will address this by moving content to a reference file.

- [ ] **Step 3: Verify no convention violations**

Run:
```bash
grep -n '%>%' rules/r-conventions.md
```
Expected: Only the existing WRONG example on line 16-18.

- [ ] **Step 4: Commit**

```bash
git add rules/r-conventions.md
git commit -m "feat(rules): add environment-aware coding and verify-after-write conventions"
```

---

### Task 2: Enhance Session-Start Hook with R Session Detection

**Files:**
- Modify: `hooks/session-start:49-68` (between detection flags and build context sections)

- [ ] **Step 1: Add R session info capture after detection flags**

Insert the following after line 48 (`fi` closing the general R project detection) and before line 50 (`# --- Build context ---`):

```bash
# --- R session info ---
# Capture R version, platform, and key package versions when Rscript is available.
# This gives skills concrete version info so they know the actual API surface.
r_session_info=""
r_platform=""
r_pkg_versions=""
if command -v Rscript >/dev/null 2>&1; then
  r_version=$(Rscript --vanilla -e 'cat(R.version$major, R.version$minor, sep=".")' 2>/dev/null || true)
  if [ -n "$r_version" ]; then
    r_platform=$(Rscript --vanilla -e 'cat(R.version$platform)' 2>/dev/null || true)
    r_session_info="R ${r_version} detected. Platform: ${r_platform:-unknown}."
    # Capture key tidyverse + infrastructure package versions
    r_pkg_versions=$(Rscript --vanilla -e '
      pkgs <- c("dplyr", "ggplot2", "tidyr", "purrr", "readr", "stringr",
                "forcats", "lubridate", "shiny", "testthat", "gt", "targets")
      installed <- pkgs[pkgs %in% rownames(installed.packages())]
      if (length(installed) > 0) {
        versions <- vapply(installed, \(p) as.character(packageVersion(p)), character(1))
        cat(paste(installed, versions, sep = " "), sep = ", ")
      }
    ' 2>/dev/null || true)
    if [ -n "$r_pkg_versions" ]; then
      r_session_info="${r_session_info}\\n  Key packages: ${r_pkg_versions}"
    fi
  fi
fi

# Check for renv.lock to surface package versions hint
if [ -f "renv.lock" ]; then
  r_session_info="${r_session_info}\\n  renv.lock found — package versions locked."
fi
```

- [ ] **Step 2: Add R session info to the context output**

Modify the context string (currently at line 76). Replace:

```bash
context="supeRpowers R plugin active.\\n${skills}Use /r-cmd-* workflow skills to start guided workflows, or /r-* knowledge skills for reference."
```

With:

```bash
r_info=""
if [ -n "$r_session_info" ]; then
  r_info="${r_session_info}\\n"
fi
context="supeRpowers R plugin active.\\n${r_info}${skills}Use /r-cmd-* workflow skills to start guided workflows, or /r-* knowledge skills for reference.\\nTip: btw/mcptools MCP enhances all skills with live R session awareness."
```

- [ ] **Step 3: Test the hook locally**

Run:
```bash
cd "C:/BS/_Projects/supeRpowers" && bash hooks/session-start
```
Expected: JSON output with `additionalContext` that includes R version info (if R is installed) and the btw tip.

- [ ] **Step 4: Commit**

```bash
git add hooks/session-start
git commit -m "feat(hooks): add R version detection and btw MCP hint to session-start"
```

---

### Task 3: Add MCP Dispatch Lines to r-data-analysis Skill

**Files:**
- Modify: `skills/r-data-analysis/SKILL.md` (after the agent dispatch section, around line 26)

- [ ] **Step 1: Add MCP Integration section**

Insert the following after the existing agent dispatch line (line 26) and before the next content section:

```markdown

**MCP integration (when R session available):**
- Before joins or transformations: `btw_tool_env_describe_data_frame` to inspect column names, types, and dimensions of input data frames
- Before referencing specific columns: verify they exist in the actual data, not just assumed from context
- When uncertain about a function's arguments: `btw_tool_docs_help_page` to read installed docs
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-data-analysis/SKILL.md
```
Expected: ~195 lines (was 190, added 5). Well under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-data-analysis/SKILL.md
git commit -m "feat(r-data-analysis): add MCP dispatch lines for data inspection"
```

---

### Task 4: Add MCP Dispatch Lines to r-stats Skill

**Files:**
- Modify: `skills/r-stats/SKILL.md` (after the agent dispatch section, around line 25)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before recommending a model from a specific package: `btw_tool_sessioninfo_is_package_installed` to verify availability
- When choosing between model families: `btw_tool_docs_help_page` to read the actual function signatures and arguments
- Before fitting a model: `btw_tool_env_describe_data_frame` to check outcome variable type and sample size
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-stats/SKILL.md
```
Expected: ~241 lines (was 236, added 5). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-stats/SKILL.md
git commit -m "feat(r-stats): add MCP dispatch lines for package and model verification"
```

---

### Task 5: Add MCP Dispatch Lines to r-visualization Skill

**Files:**
- Modify: `skills/r-visualization/SKILL.md` (after the agent dispatch section, around line 21)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before writing ggplot code: `btw_tool_env_describe_data_frame` to check variable types and choose appropriate geoms (continuous vs discrete vs date)
- When uncertain about a geom or scale function: `btw_tool_docs_help_page` to read current argument signatures
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-visualization/SKILL.md
```
Expected: ~260 lines (was 256, added 4). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-visualization/SKILL.md
git commit -m "feat(r-visualization): add MCP dispatch lines for data-aware geom selection"
```

---

### Task 6: Add MCP Dispatch Lines to r-package-dev Skill

**Files:**
- Modify: `skills/r-package-dev/SKILL.md` (after the agent dispatch section, around line 28)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before writing or updating roxygen2 docs: `btw_tool_docs_help_page` to read existing documentation for the function
- When working on exports or NAMESPACE: `btw_tool_docs_package_help_topics` to see the full list of exported functions
- Before adding a dependency: `btw_tool_sessioninfo_is_package_installed` to check if it's already available
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-package-dev/SKILL.md
```
Expected: ~306 lines (was 301, added 5). If over 300 lines, trim 6+ lines from the existing CRAN submission checklist or class systems overview (the most compressible sections) to stay within limits.

- [ ] **Step 3: Commit**

```bash
git add skills/r-package-dev/SKILL.md
git commit -m "feat(r-package-dev): add MCP dispatch lines for docs and dependency checks"
```

---

### Task 7: Add MCP Dispatch Lines to r-shiny Skill

**Files:**
- Modify: `skills/r-shiny/SKILL.md` (after the agent dispatch section, around line 27)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before building UI for data display: `btw_tool_env_describe_data_frame` to inspect the data that will be rendered
- When uncertain about Shiny or bslib functions: `btw_tool_docs_help_page` to check current API
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-shiny/SKILL.md
```
Expected: ~257 lines (was 253, added 4). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-shiny/SKILL.md
git commit -m "feat(r-shiny): add MCP dispatch lines for data inspection and API checks"
```

---

### Task 8: Add MCP Dispatch Lines to r-clinical Skill

**Files:**
- Modify: `skills/r-clinical/SKILL.md` (the existing MCP Integration section at ~line 193)

Note: r-clinical already has an MCP Integration section for Clinical Trials MCP and bioRxiv MCP. Add btw-specific lines to complement the existing content.

- [ ] **Step 1: Add btw MCP lines to existing MCP Integration section**

Insert the following at the beginning of the existing `## MCP Integration (Optional)` section (after the "All MCP features below are **optional**" line), before the Clinical Trials MCP subsection:

```markdown

### btw/mcptools (R session awareness)

- Before recommending admiral/pharmaverse functions: `btw_tool_sessioninfo_is_package_installed` to verify the package is available
- Before writing CDISC transformations: `btw_tool_env_describe_data_frame` to inspect actual dataset structure (variable names, types, expected CDISC domains)
- When uncertain about admiral function arguments: `btw_tool_docs_help_page` to read installed docs
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-clinical/SKILL.md
```
Expected: ~300 lines (was 293, added ~7). At the 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-clinical/SKILL.md
git commit -m "feat(r-clinical): add btw MCP dispatch lines for CDISC package and data verification"
```

---

### Task 9: Add MCP Dispatch Lines to r-tidymodels Skill

**Files:**
- Modify: `skills/r-tidymodels/SKILL.md` (after the agent dispatch section, around line 28)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before specifying a parsnip model engine: `btw_tool_sessioninfo_is_package_installed` to verify the engine package is installed
- Before writing recipe steps: `btw_tool_env_describe_data_frame` to inspect predictor types and choose appropriate preprocessing
- When uncertain about recipe step or tune function arguments: `btw_tool_docs_help_page` to read installed docs
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-tidymodels/SKILL.md
```
Expected: ~275 lines (was 270, added 5). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-tidymodels/SKILL.md
git commit -m "feat(r-tidymodels): add MCP dispatch lines for engine and data verification"
```

---

### Task 10: Add MCP Dispatch Lines to r-tables Skill

**Files:**
- Modify: `skills/r-tables/SKILL.md` (after the agent dispatch section, around line 25)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- Before designing a table: `btw_tool_env_describe_data_frame` to inspect column names, types, and cardinality for grouping/stratification decisions
- When uncertain about gt or gtsummary functions: `btw_tool_docs_help_page` to check current API and arguments
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-tables/SKILL.md
```
Expected: ~227 lines (was 223, added 4). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-tables/SKILL.md
git commit -m "feat(r-tables): add MCP dispatch lines for data inspection before table design"
```

---

### Task 11: Add MCP Dispatch Lines to r-targets Skill

**Files:**
- Modify: `skills/r-targets/SKILL.md` (after the agent dispatch section, around line 28)

- [ ] **Step 1: Add MCP Integration section**

Insert after the existing agent dispatch lines:

```markdown

**MCP integration (when R session available):**
- When uncertain about targets API (tar_target options, branching syntax): `btw_tool_docs_help_page` to read installed docs
- Before writing targets that process data: `btw_tool_env_describe_data_frame` to verify input structure
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l skills/r-targets/SKILL.md
```
Expected: ~288 lines (was 284, added 4). Under 300-line limit.

- [ ] **Step 3: Commit**

```bash
git add skills/r-targets/SKILL.md
git commit -m "feat(r-targets): add MCP dispatch lines for API doc lookups"
```

---

### Task 12: Final Verification

- [ ] **Step 1: Verify no convention violations across all modified files**

Run:
```bash
grep -rn '%>%' skills/ agents/ rules/ | grep -v 'WRONG\|Never\|flag any'
```
Expected: No matches (all `%>%` references are in "don't do this" examples).

- [ ] **Step 2: Verify all SKILL.md files are under 300 lines**

Run:
```bash
wc -l skills/*/SKILL.md | sort -n
```
Expected: All files ≤300 lines (r-package-dev may be ~306, flag if so).

- [ ] **Step 3: Verify r-conventions.md line count**

Run:
```bash
wc -l rules/r-conventions.md
```
Expected: ~157 lines. Over 150 but Lever 2 will fix this by extracting content to a reference file.

- [ ] **Step 4: Test session-start hook**

Run:
```bash
bash hooks/session-start
```
Expected: Valid JSON output with R version info and btw tip in the context string.
