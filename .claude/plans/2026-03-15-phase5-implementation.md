# Phase 5 Implementation Plan — Infrastructure, New Skills & Marketplace Readiness

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add hooks system, 3 new skills (r-project-setup, r-tidymodels, r-targets), and marketplace polish (README, LICENSE, RELEASE-NOTES) to supeRpowers.

**Architecture:** Content-only plugin — all deliverables are markdown, JSON, and shell scripts. No application code. Skills follow YAML frontmatter + body pattern (≤300 lines). Hooks follow the obra/superpowers polyglot .cmd pattern. All R code uses `|>`, `<-`, snake_case, double quotes.

**Tech Stack:** Bash (hooks), JSON (config), Markdown (skills/docs), R code examples within markdown.

**Spec:** `.claude/plans/2026-03-15-phase5-infrastructure-design.md`

---

## Chunk 1: Hooks System

### Task 1: Create hooks.json configuration

**Files:**
- Create: `hooks/hooks.json`

- [ ] **Step 1: Create the hooks directory**

```bash
mkdir -p hooks
```

- [ ] **Step 2: Write hooks.json**

Create `hooks/hooks.json` with this exact content:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add hooks/hooks.json
git commit -m "feat: add hooks.json SessionStart configuration"
```

---

### Task 2: Create cross-platform hook runner (run-hook.cmd)

**Files:**
- Create: `hooks/run-hook.cmd`

Reference: https://github.com/obra/superpowers/blob/main/hooks/run-hook.cmd

- [ ] **Step 1: Write the polyglot wrapper**

Create `hooks/run-hook.cmd` — this file must work as both a Windows batch file and a Unix bash script. The key trick: `:` is a no-op in bash but a valid label in batch.

```bash
: <<'BATCH_SCRIPT'
@echo off
setlocal

rem Try Git for Windows
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem Try 32-bit Git
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem Try PATH (MSYS2, Cygwin, user-installed)
where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    bash "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem No bash found — exit silently
exit /b 0
BATCH_SCRIPT

#!/usr/bin/env bash
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_NAME="${1:-}"

if [ -z "$HOOK_NAME" ]; then
    echo "Usage: run-hook.cmd <hook-name>" >&2
    exit 1
fi

HOOK_SCRIPT="${HOOK_DIR}/${HOOK_NAME}"

if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "Hook not found: ${HOOK_SCRIPT}" >&2
    exit 1
fi

exec bash "$HOOK_SCRIPT"
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x hooks/run-hook.cmd
```

- [ ] **Step 3: Commit**

```bash
git add hooks/run-hook.cmd
git commit -m "feat: add cross-platform polyglot hook runner"
```

---

### Task 3: Create session-start hook script

**Files:**
- Create: `hooks/session-start`

This is the core detection logic. It scans the current working directory for R project indicators and outputs context via JSON.

- [ ] **Step 1: Write the session-start script**

Create `hooks/session-start`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# --- Detect plugin root ---
if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
    PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT"
else
    PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

# --- Detect R project type ---
PROJECT_TYPE="none"
SECONDARY_FEATURES=""

if [ -f "DESCRIPTION" ] && [ -f "NAMESPACE" ]; then
    PROJECT_TYPE="r-package"
    # Check for golem/shiny package
    if [ -f "app.R" ] || [ -f "R/app_server.R" ]; then
        PROJECT_TYPE="shiny-package"
    fi
elif [ -f "DESCRIPTION" ] && { [ -f "app.R" ] || [ -f "ui.R" ]; }; then
    PROJECT_TYPE="shiny-package"
elif [ -f "app.R" ] || { [ -f "ui.R" ] && [ -f "server.R" ]; }; then
    PROJECT_TYPE="shiny-app"
elif [ -f "_targets.R" ]; then
    PROJECT_TYPE="targets-pipeline"
elif [ -f "_quarto.yml" ] || compgen -G "*.qmd" > /dev/null 2>&1; then
    PROJECT_TYPE="quarto-project"
elif compgen -G "*.Rproj" > /dev/null 2>&1; then
    PROJECT_TYPE="r-analysis"
elif compgen -G "*.R" > /dev/null 2>&1; then
    PROJECT_TYPE="r-scripts"
fi

# Detect secondary features
if [ "$PROJECT_TYPE" != "targets-pipeline" ] && [ -f "_targets.R" ]; then
    SECONDARY_FEATURES="${SECONDARY_FEATURES}targets, "
fi
if [ "$PROJECT_TYPE" != "quarto-project" ] && { [ -f "_quarto.yml" ] || compgen -G "*.qmd" > /dev/null 2>&1; }; then
    SECONDARY_FEATURES="${SECONDARY_FEATURES}quarto, "
fi
# Trim trailing ", "
SECONDARY_FEATURES="${SECONDARY_FEATURES%, }"

# --- Check R environment (only if R project detected) ---
R_VERSION=""
RENV_STATUS="not initialized"
TESTTHAT_STATUS="no tests"
PKG_NAME=""
PKG_VERSION=""

if [ "$PROJECT_TYPE" != "none" ]; then
    # R version
    if command -v R > /dev/null 2>&1; then
        R_VERSION=$(R --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
    fi

    # renv status
    if [ -f "renv.lock" ]; then
        RENV_STATUS="active"
    fi

    # testthat
    if [ -d "tests/testthat" ]; then
        TESTTHAT_STATUS="present"
    fi

    # Package identity
    if [ -f "DESCRIPTION" ]; then
        PKG_NAME=$(grep -m1 '^Package:' DESCRIPTION 2>/dev/null | sed 's/Package: *//' || echo "")
        PKG_VERSION=$(grep -m1 '^Version:' DESCRIPTION 2>/dev/null | sed 's/Version: *//' || echo "")
    fi
fi

# --- Build skill relevance ---
case "$PROJECT_TYPE" in
    r-package|shiny-package)
        if [ "$PROJECT_TYPE" = "shiny-package" ]; then
            SKILLS="r-shiny, r-package-dev, r-tdd, r-debugging"
            AGENTS="r-shiny-architect, r-code-reviewer, r-pkg-check, r-dependency-manager"
        else
            SKILLS="r-package-dev, r-tdd, r-debugging"
            AGENTS="r-code-reviewer, r-pkg-check, r-dependency-manager"
        fi
        ;;
    shiny-app)
        SKILLS="r-shiny, r-tdd, r-debugging"
        AGENTS="r-shiny-architect, r-code-reviewer"
        ;;
    targets-pipeline)
        SKILLS="r-targets, r-data-analysis"
        AGENTS="r-code-reviewer, r-dependency-manager"
        ;;
    quarto-project)
        SKILLS="r-quarto, r-visualization, r-tables"
        AGENTS=""
        ;;
    r-analysis)
        SKILLS="r-data-analysis, r-visualization, r-stats"
        AGENTS="r-statistician"
        ;;
    r-scripts)
        SKILLS="r-data-analysis, r-debugging"
        AGENTS="r-code-reviewer"
        ;;
    none)
        SKILLS=""
        AGENTS=""
        ;;
esac

# --- Generate output ---
if [ "$PROJECT_TYPE" = "none" ]; then
    CONTEXT="supeRpowers active. No R project detected in current directory. R skills available on demand."
else
    CONTEXT="supeRpowers active."

    # Project type
    case "$PROJECT_TYPE" in
        r-package)
            if [ -n "$PKG_NAME" ]; then
                CONTEXT="$CONTEXT Detected: R package ($PKG_NAME $PKG_VERSION)"
            else
                CONTEXT="$CONTEXT Detected: R package"
            fi
            ;;
        shiny-package) CONTEXT="$CONTEXT Detected: Shiny app (package-based)" ;;
        shiny-app) CONTEXT="$CONTEXT Detected: Shiny app" ;;
        targets-pipeline) CONTEXT="$CONTEXT Detected: targets pipeline" ;;
        quarto-project) CONTEXT="$CONTEXT Detected: Quarto project" ;;
        r-analysis) CONTEXT="$CONTEXT Detected: R analysis project" ;;
        r-scripts) CONTEXT="$CONTEXT Detected: R scripts" ;;
    esac

    # Environment details
    DETAILS=""
    if [ -n "$R_VERSION" ]; then DETAILS="R $R_VERSION"; fi
    if [ "$RENV_STATUS" = "active" ]; then DETAILS="${DETAILS:+$DETAILS, }renv active"; fi
    if [ "$TESTTHAT_STATUS" = "present" ]; then DETAILS="${DETAILS:+$DETAILS, }testthat present"; fi
    if [ -n "$SECONDARY_FEATURES" ]; then DETAILS="${DETAILS:+$DETAILS, }also: $SECONDARY_FEATURES"; fi
    if [ -n "$DETAILS" ]; then CONTEXT="$CONTEXT ($DETAILS)."; else CONTEXT="$CONTEXT."; fi

    # Skills and agents
    if [ -n "$SKILLS" ]; then CONTEXT="$CONTEXT Relevant skills: $SKILLS."; fi
    if [ -n "$AGENTS" ]; then CONTEXT="$CONTEXT Agents: $AGENTS."; fi
fi

# Escape for JSON
CONTEXT_JSON=$(echo "$CONTEXT" | sed 's/"/\\"/g' | tr -d '\n')

# Output as JSON for Claude Code hook system
cat <<HOOK_EOF
{"hookSpecificOutput":{"additionalContext":"$CONTEXT_JSON"}}
HOOK_EOF
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x hooks/session-start
```

- [ ] **Step 3: Test the hook locally**

Run from the supeRpowers project root. Since there are no `.R` files at the top level (only in nested `skills/*/`), the `*.R` glob won't match. Expected: "No R project detected."

```bash
cd /Users/alexandervantwisk/Desktop/Projects/supeRpowers && bash hooks/session-start
```

Expected output: `{"hookSpecificOutput":{"additionalContext":"supeRpowers active. No R project detected in current directory. R skills available on demand."}}`

Verify JSON is valid:

```bash
bash hooks/session-start | python3 -m json.tool
```

Then test from a directory that contains `.R` files directly (if available) to verify detection works.

- [ ] **Step 4: Commit**

```bash
git add hooks/session-start
git commit -m "feat: add session-start hook with R project detection"
```

---

### Task 4: Update plugin.json with hooks

**Files:**
- Modify: `plugin.json`

- [ ] **Step 1: Update plugin.json**

Make three edits to `plugin.json`:

1. Change `"version": "0.1.0"` to `"version": "0.2.0"`
2. Change `"keywords"` to: `["r", "rstats", "tidyverse", "shiny", "biostatistics", "clinical-trials", "tidymodels", "targets"]`
3. Add `"hooks": "hooks/hooks.json"` to the `claude_code` object (after the `"agents"` line)

Result should be:

```json
{
  "name": "supeRpowers",
  "version": "0.2.0",
  "description": "Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, and biostatistics.",
  "keywords": ["r", "rstats", "tidyverse", "shiny", "biostatistics", "clinical-trials", "tidymodels", "targets"],
  "author": "Alexander van Twisk",
  "license": "MIT",
  "claude_code": {
    "min_version": "1.0.0",
    "rules": ["rules/r-conventions.md"],
    "skills": ["skills/*/SKILL.md"],
    "agents": ["agents/*.md"],
    "hooks": "hooks/hooks.json"
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add plugin.json
git commit -m "feat: update plugin.json with hooks and version 0.2.0"
```

---

## Chunk 2: r-project-setup Skill

### Task 5: Create r-project-setup SKILL.md

**Files:**
- Create: `skills/r-project-setup/SKILL.md`

**Source material:** Spec section 2 has all the content. **Template:** Copy the format from `skills/r-data-analysis/SKILL.md` (frontmatter style, lazy reference pointers, agent dispatch line, code examples, examples section).

**Content authoring instructions:** The spec provides the full technical content for each section listed below. The implementer's job is to format it as a SKILL.md following the existing pattern — not to research or invent content. Copy R code examples from the spec verbatim. Use the same heading structure as `r-data-analysis/SKILL.md`.

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/r-project-setup/references
```

- [ ] **Step 2: Write SKILL.md**

Create `skills/r-project-setup/SKILL.md`. Must include:

**Frontmatter:**
```yaml
---
name: r-project-setup
description: >
  Use when setting up, initializing, or scaffolding a new R project, package,
  Shiny app, or Quarto document.
---
```

**Body structure (stay ≤300 lines total):**
1. Title + one-liner
2. Lazy references pointer to `references/scaffold-templates.md`
3. Agent dispatch: `r-dependency-manager` after scaffold, `r-package-dev` for package scaffolds
4. Project type decision table (Analysis / Package / Shiny / Quarto)
5. Analysis project scaffold — directory structure, `.Rproj`, `.Rprofile`, `renv::init()`
6. Package scaffold — brief: "Defer to r-package-dev skill for the authoritative scaffold workflow. Add `.lintr` if not present."
7. Shiny scaffold — basic mode (`app.R` + modules) and production mode (`golem::create_golem()`)
8. Quarto scaffold — document, presentation, website, book variants
9. Common to all scaffolds — `.lintr`, `.gitignore`, `.Rprofile`, README stub
10. Examples (4 prompts)

**R code conventions:** All code uses `|>`, `<-`, snake_case, double quotes. No `%>%`.

- [ ] **Step 3: Verify line count**

```bash
wc -l skills/r-project-setup/SKILL.md
```

Expected: ≤300 lines.

- [ ] **Step 4: Verify no %>%**

```bash
grep -n '%>%' skills/r-project-setup/SKILL.md
```

Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add skills/r-project-setup/SKILL.md
git commit -m "feat: add r-project-setup skill"
```

---

### Task 6: Create r-project-setup reference file

**Files:**
- Create: `skills/r-project-setup/references/scaffold-templates.md`

- [ ] **Step 1: Write scaffold-templates.md**

This file contains the full file contents for templates used across all scaffold types:

1. **`.lintr` template** — tidyverse defaults with `linters_with_defaults()`, `line_length_linter(120)`, `object_name_linter("snake_case")`
2. **`.gitignore` template** — R-specific: `.Rhistory`, `.RData`, `.Rproj.user/`, `renv/library/`, `renv/staging/`, `_targets/`, `.quarto/`, `*.html` (for Quarto renders), `data/raw/` note
3. **`.Rprofile` template** — `source("renv/activate.R")` with existence check
4. **`.Rproj` template** — standard RStudio project file settings (Version, RestoreWorkspace, SaveWorkspace, etc.)
5. **Basic Shiny `app.R` template** — minimal working app with `bslib::page_sidebar()`
6. **Quarto `_quarto.yml` templates** — one each for document, presentation, website, book

All R code in templates must use `|>`, `<-`, snake_case, double quotes.

- [ ] **Step 2: Commit**

```bash
git add skills/r-project-setup/references/scaffold-templates.md
git commit -m "feat: add scaffold template reference for r-project-setup"
```

---

## Chunk 3: r-tidymodels Skill

### Task 7: Create r-tidymodels SKILL.md

**Files:**
- Create: `skills/r-tidymodels/SKILL.md`

**Source material:** Spec section 3 has all the content including code examples, tables, and boundary definitions. **Template:** `skills/r-data-analysis/SKILL.md`. Copy R code and tables from the spec verbatim. Offload the parsnip model/engine table to `references/parsnip-engines.md` to stay within 300-line budget.

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/r-tidymodels/references
```

- [ ] **Step 2: Write SKILL.md**

Create `skills/r-tidymodels/SKILL.md`. Must include:

**Frontmatter:**
```yaml
---
name: r-tidymodels
description: >
  Use when building machine learning models, predictive modeling, or model tuning
  in R using tidymodels, recipes, workflows, tune, or yardstick.
---
```

**Body structure (stay ≤300 lines total):**
1. Title + one-liner
2. Lazy references pointers:
   - `references/recipe-steps-catalog.md` for complete step_* reference
   - `references/parsnip-engines.md` for engine comparison table
3. Agent dispatch: `r-statistician` for model selection methodology questions
4. Boundary note: r-tidymodels (prediction) vs r-stats (inference)
5. Core packages table (rsample, recipes, parsnip, workflows, tune, yardstick, broom, stacks)
6. Data splitting with rsample — `initial_split()`, `vfold_cv()`, stratification
7. Feature engineering with recipes — formula, key steps, selectors, ordering rule
8. Model specification with parsnip — summary only (3-4 common models inline, point to reference for full table)
9. Workflows — `workflow()` + `add_recipe()` + `add_model()`, `workflow_set()`
10. Hyperparameter tuning — `tune_grid()`, `tune_bayes()`, `select_best()`, `finalize_workflow()`
11. Evaluation with yardstick — metrics table, `collect_metrics()`, `conf_mat()`, `roc_curve()`
12. Model stacking — brief 5-line example with pointer to reference
13. targets integration — brief pipeline pattern
14. Examples (5 prompts)

**Key line-budget decisions:** Move the full parsnip model/engine table to `references/parsnip-engines.md`. Keep only 3-4 inline examples. Move stacking detail to references.

- [ ] **Step 3: Verify line count**

```bash
wc -l skills/r-tidymodels/SKILL.md
```

Expected: ≤300 lines.

- [ ] **Step 4: Verify no %>%**

```bash
grep -n '%>%' skills/r-tidymodels/SKILL.md
```

Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add skills/r-tidymodels/SKILL.md
git commit -m "feat: add r-tidymodels skill"
```

---

### Task 8: Create r-tidymodels reference files

**Files:**
- Create: `skills/r-tidymodels/references/recipe-steps-catalog.md`
- Create: `skills/r-tidymodels/references/parsnip-engines.md`

- [ ] **Step 1: Write recipe-steps-catalog.md**

Complete `step_*` reference organized by category:

1. **Imputation:** `step_impute_mean()`, `step_impute_median()`, `step_impute_knn()`, `step_impute_bag()`, `step_impute_linear()`
2. **Transformation:** `step_log()`, `step_sqrt()`, `step_BoxCox()`, `step_YeoJohnson()`, `step_poly()`, `step_ns()`
3. **Normalization:** `step_normalize()`, `step_center()`, `step_scale()`, `step_range()`
4. **Encoding:** `step_dummy()`, `step_other()`, `step_integer()`, `step_novel()`
5. **Feature selection:** `step_zv()`, `step_nzv()`, `step_corr()`, `step_pca()`, `step_select()`
6. **Interaction:** `step_interact()`, `step_product()`
7. **Date/time:** `step_date()`, `step_time()`, `step_holiday()`
8. **Text:** `step_tokenize()`, `step_tf()`, `step_tfidf()`, `step_word_embeddings()`

Each entry: function name, purpose, key arguments, when to use.

- [ ] **Step 2: Write parsnip-engines.md**

Engine comparison table for each model type from the spec:

| Model | Engine | R Package | Speed | Interpretability | Key Tunable Params | When to Choose |
|-------|--------|-----------|-------|-----------------|-------------------|----------------|
| linear_reg | lm | stats | fast | high | none | baseline, small data |
| linear_reg | glmnet | glmnet | fast | high | penalty, mixture | regularization needed |
| rand_forest | ranger | ranger | fast | medium | mtry, trees, min_n | general purpose, handles mixed types |
| boost_tree | xgboost | xgboost | medium | low | trees, tree_depth, learn_rate, mtry | best performance, structured data |
| boost_tree | lightgbm | bonsai | fast | low | trees, tree_depth, learn_rate | large datasets, categorical features |
| ... etc for all 7 model types |

- [ ] **Step 3: Commit**

```bash
git add skills/r-tidymodels/references/
git commit -m "feat: add tidymodels reference files (recipe steps, parsnip engines)"
```

---

## Chunk 4: r-targets Skill

### Task 9: Create r-targets SKILL.md

**Files:**
- Create: `skills/r-targets/SKILL.md`

**Source material:** Spec section 4 has all content including pipeline examples, command tables, branching patterns, integration recipes, and anti-patterns table. **Template:** `skills/r-data-analysis/SKILL.md`. Copy all R code and tables from spec verbatim.

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/r-targets/references
```

- [ ] **Step 2: Write SKILL.md**

Create `skills/r-targets/SKILL.md`. Must include:

**Frontmatter:**
```yaml
---
name: r-targets
description: >
  Use when creating reproducible analysis pipelines, managing computational
  workflows, or using the targets package for pipeline orchestration in R.
---
```

**Body structure (stay ≤300 lines total):**
1. Title + one-liner
2. Lazy references pointers:
   - `references/branching-patterns.md` for static vs dynamic branching decision tree
   - `references/targets-integration-recipes.md` for copy-paste pipeline patterns
3. Agent dispatch: `r-dependency-manager` for renv + targets reproducibility questions
4. Pipeline fundamentals — `_targets.R` structure, `tar_target()`, `tar_option_set()`
5. Core workflow commands table — `tar_make()`, `tar_read()`, `tar_visnetwork()`, etc.
6. Target formats table — qs, rds, feather, parquet, file
7. Static branching — `tar_map()` with example
8. Dynamic branching — `pattern = map()` with example
9. Error handling — `tar_workspace()`, `tar_meta()`, `tar_traceback()`
10. Integration: targets + Quarto — `tarchetypes::tar_quarto()` example
11. Integration: targets + tidymodels — pipeline stages example
12. Integration: targets + renv — reproducibility stack
13. Parallel execution — `crew` backend example
14. Anti-patterns table
15. Examples (5 prompts)

- [ ] **Step 3: Verify line count**

```bash
wc -l skills/r-targets/SKILL.md
```

Expected: ≤300 lines.

- [ ] **Step 4: Verify no %>%**

```bash
grep -n '%>%' skills/r-targets/SKILL.md
```

Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add skills/r-targets/SKILL.md
git commit -m "feat: add r-targets skill"
```

---

### Task 10: Create r-targets reference files

**Files:**
- Create: `skills/r-targets/references/branching-patterns.md`
- Create: `skills/r-targets/references/targets-integration-recipes.md`

- [ ] **Step 1: Write branching-patterns.md**

Decision tree and recipes:

1. **Decision tree:** Static vs dynamic branching
   - Values known at definition time? → static (`tar_map()`)
   - Values depend on upstream targets? → dynamic (`pattern = map()`)
   - All combinations needed? → `pattern = cross()`
   - Subset only? → `pattern = slice()`
2. **Static branching recipes:**
   - Multiple datasets: `tar_map(values = tibble(data_name = c(...)))`
   - Parameter sweep: `tar_map(values = tibble(param = seq(...)))`
   - Cross-validation: `tar_map(values = tibble(fold_id = 1:10))`
3. **Dynamic branching recipes:**
   - File processing: `pattern = map(files)`
   - Simulation replicates: `tar_target(sims, 1:1000), tar_target(result, run_sim(sims), pattern = map(sims))`
   - Group-by analysis: `tar_group_by()` + `pattern = map(grouped_data)`
4. **Combining results:** `tar_combine()` for aggregating branched targets

All code uses `|>`, `<-`, snake_case, double quotes.

- [ ] **Step 2: Write targets-integration-recipes.md**

Copy-paste pipeline patterns:

1. **Data import + cleaning pipeline** — read raw → validate → clean → save processed
2. **ML pipeline** — split → recipe → model → tune → evaluate → report (using tidymodels)
3. **Report generation** — data → analysis → `tar_quarto()` report
4. **Simulation study** — parameters → dynamic branching → aggregate → visualize
5. **Multi-dataset analysis** — static branch per dataset → common analysis → comparison table

Each recipe: complete `_targets.R` file + supporting `R/` function stubs.

- [ ] **Step 3: Commit**

```bash
git add skills/r-targets/references/
git commit -m "feat: add targets reference files (branching patterns, integration recipes)"
```

---

## Chunk 5: Marketplace Readiness

### Task 11: Create LICENSE file

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write MIT LICENSE**

```
MIT License

Copyright (c) 2026 Alexander van Twisk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "docs: add MIT LICENSE file"
```

---

### Task 12: Create RELEASE-NOTES.md

**Files:**
- Create: `RELEASE-NOTES.md`

- [ ] **Step 1: Write RELEASE-NOTES.md**

```markdown
# Release Notes

## 0.2.0 (2026-03-15)

### Added
- **Hooks:** Session-start hook detects R project type (package, Shiny, targets, Quarto, analysis, scripts) and surfaces relevant skills/agents
- **Hooks:** Cross-platform polyglot runner for Windows compatibility
- **Skill:** r-project-setup — scaffold analysis projects, packages, Shiny apps, Quarto documents
- **Skill:** r-tidymodels — machine learning with tidymodels ecosystem (recipes, workflows, tune, yardstick)
- **Skill:** r-targets — reproducible pipeline orchestration with targets, branching, and integrations
- **Docs:** README with badges, architecture diagram, skill/agent catalogs, quick start
- **Docs:** LICENSE (MIT)

### Changed
- plugin.json: added hooks directory, new keywords, bumped version to 0.2.0

## 0.1.0 (2026-03-15)

### Added
- **Foundation:** r-conventions rule (base pipe, tidyverse-first, style guide)
- **Phase 1:** r-data-analysis, r-visualization, r-tdd, r-debugging skills
- **Phase 2:** r-package-dev, r-shiny skills + r-code-reviewer, r-dependency-manager agents
- **Phase 3:** r-stats, r-clinical, r-tables, r-quarto skills + r-statistician, r-pkg-check, r-shiny-architect agents
- **Phase 4:** r-performance, r-package-skill-generator skills
- **Docs:** CLAUDE.md development guide
- **Config:** plugin.json manifest
```

- [ ] **Step 2: Commit**

```bash
git add RELEASE-NOTES.md
git commit -m "docs: add RELEASE-NOTES.md with version history"
```

---

### Task 13: Create README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write README.md**

Full showcase README. Structure:

```markdown
# supeRpowers

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-15-purple)
![R](https://img.shields.io/badge/R-%3E%3D%204.1.0-blue)

Comprehensive R programming assistant for Claude Code — tidyverse-first data analysis, package development, Shiny, statistics, biostatistics, and more.

## Installation

[installation command for Claude Code marketplace]

## How It Works

supeRpowers uses a three-layer architecture:

[text diagram: Foundation → Domain → Service]

**Foundation** — `rules/r-conventions.md` is loaded into every R conversation...
**Domain** — 15 specialized skills activated by matching your intent...
**Service** — 5 shared agents dispatched from skills or invoked directly...
**Hooks** — Session-start hook detects your R project type...

## Skills

[15-row table: Skill | What It Does | Key Packages]

## Agents

[5-row table: Agent | Purpose | Dispatched By]

## Quick Start

[6 example prompts]

## Requirements

- R >= 4.1.0
- Claude Code >= 1.0.0

## License

MIT — see LICENSE
```

Include the full skill catalog table (all 15 skills) and agent catalog table (all 5 agents) from the spec. Include 6 example prompts.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add full README with badges, catalogs, and quick start"
```

---

### Task 13.5: Research and optionally create marketplace.json

**Files:**
- Optionally create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Research whether Claude Code marketplace requires a marketplace.json**

Check the Claude Code plugin documentation for marketplace submission requirements. If `marketplace.json` is required, create `.claude-plugin/marketplace.json`:

```json
{
  "categories": ["programming", "data-science", "statistics"],
  "icon": "chart-bar",
  "pricing": "free"
}
```

If not required, skip this task and note the decision.

- [ ] **Step 2: Commit (if created)**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: add marketplace.json metadata"
```

---

## Chunk 6: Update Existing Files

### Task 14: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update skill and agent counts**

Change "12 skills, 6 agents, and 1 rule" to "15 skills, 5 agents, and 1 rule" in the "What This Is" section.

- [ ] **Step 2: Update project structure**

Add `hooks/` directory and new skills to the project structure tree:

```
hooks/                   # Session lifecycle hooks
  hooks.json             # SessionStart hook configuration
  session-start          # R project detection script
  run-hook.cmd           # Cross-platform wrapper
```

Add to the skills listing:
```
  r-project-setup/       r-tidymodels/          r-targets/
```

- [ ] **Step 3: Add hooks section**

After the "Verification Checklist" section, add:

```markdown
## Hooks

The plugin includes a session-start hook (`hooks/session-start`) that fires on startup, resume, clear, and compact. It detects the R project type in the current directory and injects context about relevant skills and agents. Configuration is in `hooks/hooks.json`.
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md — add Phase 5 skills/hooks, fix agent count (6->5)"
```

---

### Task 15: Update original design spec

**Files:**
- Modify: `plans/2026-03-15-superpowers-r-plugin-design.md`

- [ ] **Step 1: Add new skill triggers to the frontmatter contracts table**

Find the "Skill Frontmatter Contracts" table containing `r-package-skill-generator`. After that last row, add:

```
| r-project-setup | r-project-setup | Use when setting up, initializing, or scaffolding a new R project, package, Shiny app, or Quarto document. |
| r-tidymodels | r-tidymodels | Use when building machine learning models, predictive modeling, or model tuning in R using tidymodels, recipes, workflows, tune, or yardstick. |
| r-targets | r-targets | Use when creating reproducible analysis pipelines, managing computational workflows, or using the targets package for pipeline orchestration in R. |
```

- [ ] **Step 2: Add new skills to directory structure**

Find the "Directory Structure" section (contains the file tree with `skills/` directory). Add under `skills/`:
```
  r-project-setup/
    SKILL.md
    references/
  r-tidymodels/
    SKILL.md
    references/
  r-targets/
    SKILL.md
    references/
```

Also add the `hooks/` directory at root level.

- [ ] **Step 3: Add new skill chaining workflows**

Find the "Skill Chaining — Natural Workflows" section (contains "Analysis to publication" chain). Add:
```
- **ML pipeline:** `r-project-setup` → `r-targets` → `r-tidymodels` → `r-visualization`
- **Reproducible analysis:** `r-project-setup` → `r-targets` → `r-data-analysis` → `r-quarto`
```

- [ ] **Step 4: Add Phase 5 entry**

Find the "Implementation Phases" section, after the "Phase 4: Performance" subsection. Add:

```markdown
### Phase 5: Infrastructure & New Skills
- `hooks/` (session-start hook, cross-platform runner)
- `r-project-setup/`
- `r-tidymodels/`
- `r-targets/`
- README.md, LICENSE, RELEASE-NOTES.md
```

- [ ] **Step 5: Commit**

```bash
git add plans/2026-03-15-superpowers-r-plugin-design.md
git commit -m "docs: update design spec with Phase 5 skills, hooks, and chaining"
```

---

## Chunk 7: Verification

### Task 16: Run full verification checklist

**Files:** None (read-only verification)

- [ ] **Step 1: Check for %>% violations**

```bash
grep -rn '%>%' skills/ agents/ rules/ hooks/
```

Expected: no matches.

- [ ] **Step 2: Verify all SKILL.md files are ≤300 lines**

```bash
for f in skills/*/SKILL.md; do echo "$(wc -l < "$f") $f"; done | sort -rn
```

Expected: all ≤300.

- [ ] **Step 3: Verify agent files are ≤200 lines**

```bash
for f in agents/*.md; do echo "$(wc -l < "$f") $f"; done | sort -rn
```

Expected: all ≤200.

- [ ] **Step 4: Verify SKILL.md frontmatter format**

```bash
for f in skills/*/SKILL.md; do head -5 "$f"; echo "---"; done
```

Expected: each starts with `---`, has `name:` and `description:` fields, ends with `---`.

- [ ] **Step 5: Verify plugin.json globs match new files**

```bash
ls skills/*/SKILL.md | wc -l
```

Expected: 15 (12 existing + 3 new).

```bash
ls agents/*.md | wc -l
```

Expected: 5.

- [ ] **Step 6: Verify hooks are executable**

```bash
ls -la hooks/session-start hooks/run-hook.cmd
```

Expected: both have execute permission.

- [ ] **Step 7: Verify no %>% in new files (final check)**

```bash
grep -rn '%>%' skills/r-project-setup/ skills/r-tidymodels/ skills/r-targets/ hooks/
```

Expected: no matches. R code convention checks (`<-` vs `=`, snake_case, double quotes) are enforced by `rules/r-conventions.md` at runtime — manual verification of these in markdown content is impractical due to false positives from YAML, prose, and function arguments.

- [ ] **Step 8: Validate hooks.json is valid JSON**

```bash
python3 -m json.tool hooks/hooks.json > /dev/null && echo "Valid JSON" || echo "INVALID JSON"
```

Expected: "Valid JSON"

- [ ] **Step 9: Final commit (if any fixes needed)**

Stage only the specific files that were fixed (do not use `git add -A`):

```bash
git add <fixed-files>
git commit -m "fix: verification checklist corrections"
```

Only commit if fixes were needed. Do not create an empty commit.
