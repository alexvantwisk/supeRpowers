# Lever 2: Statistical Programmer Identity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reshape how Claude writes R code — prioritizing readable, linear, traceable analytical code over software engineering abstractions, and enforcing modern dplyr 1.2.0 function usage.

**Architecture:** Three changes: (1) new "Statistical Programming Style" section in r-conventions.md with principles and examples, (2) new reference file `rules/references/modern-r.md` for detailed function tables (keeping the rule file under 150 lines), (3) two new check categories in the r-code-reviewer agent.

**Tech Stack:** Markdown (rules/agents/references)

---

### Task 1: Create the Modern R Reference File

This must happen first because r-conventions.md will reference it.

**Files:**
- Create: `rules/references/modern-r.md`

- [ ] **Step 1: Create the references directory**

Run:
```bash
mkdir -p rules/references
```

- [ ] **Step 2: Write the modern-r.md reference file**

Create `rules/references/modern-r.md` with the following content:

```markdown
# Modern R Function Reference

Quick-reference tables for modern R function usage. Loaded on demand from `rules/r-conventions.md`.

## New Functions to Prefer (dplyr 1.2.0+)

| Function | Use for | Replaces |
|----------|---------|----------|
| `filter_out()` | Drop rows matching conditions (NA-safe: treats NA as FALSE, does not drop NA rows) | `filter(!(cond) \| is.na(...))` |
| `recode_values()` | Map values to new values via formula (`old ~ new`) or lookup table (`from`/`to` vectors). Use `.unmatched = "error"` for safety. | `case_match()`, `recode()` |
| `replace_values()` | Partially update a column by value match. Type-stable on input. Same formula/lookup interface as `recode_values()`. | `if_else(x == val, new, x)`, `recode()`, `tidyr::replace_na()` |
| `replace_when()` | Partially update a column by logical condition. Enhanced `base::replace()`. | `case_when(..., .default = x)` for partial-update cases |
| `when_any()` | Elementwise OR across logical vectors inside `filter()`. `filter(when_any(x, y, z))` = `filter(x \| y \| z)`. | Manual `\|` chains |
| `when_all()` | Elementwise AND across logical vectors inside `filter()`. | Manual `&` chains |

### Recoding/Replacing Decision Guide

|  | New column (recode) | Update existing (replace) |
|--|---------------------|--------------------------|
| **By condition** | `case_when()` | `replace_when()` |
| **By value** | `recode_values()` | `replace_values()` |

### Newly Stable (dplyr 1.2.0)

- **`.by` argument** — Stable. Prefer `.by` over `group_by() |> ... |> ungroup()` for single-operation grouping.
- **`reframe()`** — Stable. Use for summaries that return any number of rows per group.

### Performance Improvements (dplyr 1.2.0)

`if_else()`, `case_when()`, and `coalesce()` were rewritten in C via vctrs — up to 30x faster, 10x less memory. No API changes needed to benefit.

## Deprecated Function Blocklist

NEVER use these functions. Use the modern replacement.

| Deprecated | Use Instead | Since | Notes |
|-----------|-------------|-------|-------|
| `spread()` | `pivot_wider()` | tidyr 1.0 | |
| `gather()` | `pivot_longer()` | tidyr 1.0 | |
| `summarise_each()` | `across()` | dplyr 1.0 | Now defunct (errors) |
| `mutate_each()` | `across()` | dplyr 1.0 | Now defunct (errors) |
| `mutate_at()` | `across(.cols = )` | dplyr 1.0 | |
| `mutate_if()` | `across(where())` | dplyr 1.0 | |
| `mutate_all()` | `across(everything())` | dplyr 1.0 | |
| `funs()` | `list()` of lambdas | dplyr 0.8 | |
| `do()` | `reframe()` or `nest() \|> mutate(map(...))` | dplyr 1.1 | |
| `transmute()` | `mutate(.keep = "none")` | dplyr 1.1 | |
| `case_match()` | `recode_values()` / `replace_values()` | dplyr 1.2 | Soft-deprecated |
| `recode()` | `recode_values()` / `replace_values()` | dplyr 1.2 | Long-superseded |

## Defunct Functions (will error on dplyr 1.2.0)

All underscored SE verbs are now defunct: `mutate_()`, `filter_()`, `arrange_()`, `select_()`, `rename_()`, `slice_()`, `summarise_()`, `group_by_()`, `distinct_()`.

Also defunct: `combine()`, `tbl_df()`, `as.tbl()`, `add_rownames()`.
```

- [ ] **Step 3: Verify the file**

Run:
```bash
wc -l rules/references/modern-r.md
```
Expected: ~60 lines.

Run:
```bash
grep -n '%>%' rules/references/modern-r.md
```
Expected: No matches.

- [ ] **Step 4: Commit**

```bash
git add rules/references/modern-r.md
git commit -m "feat(rules): add modern R function reference with dplyr 1.2.0 tables"
```

---

### Task 2: Add Statistical Programming Style Section to r-conventions.md

**Files:**
- Modify: `rules/r-conventions.md:128` (after Anti-Patterns table, before the new Environment-Aware Coding section added by Lever 1, or before Function Design if Lever 1 hasn't been applied yet)

Note: If Lever 1 has already been applied, this section goes between the Anti-Patterns table and the Environment-Aware Coding section. If not, it goes between Anti-Patterns and Function Design.

- [ ] **Step 1: Add the Statistical Programming Style section**

Insert the following after line 128 (the last row of the Anti-Patterns table):

```markdown

## Statistical Programming Style

Write R like a statistical programmer, not a software engineer:

- **Linear over abstract** — If logic runs once, keep it inline. Don't extract a helper function for a one-off transformation.
- **Readable over DRY** — Three similar pipelines are better than one parameterized function that's harder to trace. Extract only when repetition causes real maintenance risk.
- **Analytical intent comments** — Comment *why* (the analytical purpose), not *what* (code mechanics). One comment per logical block, not per line. No comments on self-explanatory code.
- **Flat over nested** — Break `map(map(map(...)))` into named intermediate steps with analytical names: `enrolled_patients`, `baseline_labs`, `efficacy_endpoints`.
- **Explicit over clever** — `if_else()` over `case_when()` for binary choices. Named intermediates over long chains.

```r
# WRONG: developer instinct — abstract a one-off operation
clean_data <- function(df, date_col, value_col) {
  df |>
    filter(!is.na(.data[[value_col]])) |>
    mutate(across(all_of(date_col), as.Date))
}
labs <- clean_data(labs_raw, "collection_date", "result_value")
vitals <- clean_data(vitals_raw, "measurement_date", "vital_value")

# RIGHT: statistical programmer — inline, traceable, obvious
# Remove records with missing lab results
labs <- labs_raw |>
  filter(!is.na(result_value)) |>
  mutate(collection_date = as.Date(collection_date))

# Remove records with missing vital signs
vitals <- vitals_raw |>
  filter(!is.na(vital_value)) |>
  mutate(measurement_date = as.Date(measurement_date))

# WRONG: over-commented — code is buried
# Filter the data to only include rows where age is greater than 18
data <- data |>
  # Use the filter function to keep rows matching the condition
  filter(age > 18) |>
  # Create a new column called bmi by dividing weight by height squared
  mutate(bmi = weight / height^2) |>
  # Arrange the data by descending bmi values
  arrange(desc(bmi))

# RIGHT: one comment explains the analytical intent
# Adults only, ranked by BMI for obesity screening
data <- data |>
  filter(age > 18) |>
  mutate(bmi = weight / height^2) |>
  arrange(desc(bmi))
```
```

- [ ] **Step 2: Verify line count**

Run:
```bash
wc -l rules/r-conventions.md
```
Expected: Approximately 158-177 lines depending on whether Lever 1 has been applied. Will exceed 150-line limit — this is expected and addressed in Task 3.

- [ ] **Step 3: Commit**

```bash
git add rules/r-conventions.md
git commit -m "feat(rules): add statistical programming style — linear, readable, analytical"
```

---

### Task 3: Add Modern R Section to r-conventions.md and Trim to Fit

This task adds a compact Modern R section that points to the reference file, and trims existing content to stay near the 150-line limit.

**Files:**
- Modify: `rules/r-conventions.md` (after Statistical Programming Style section)

- [ ] **Step 1: Add compact Modern R section**

Insert after the Statistical Programming Style section (after the RIGHT code example):

```markdown

## Modern R

Prefer modern tidyverse functions. See `rules/references/modern-r.md` for the full reference.

**Key dplyr 1.2.0 additions:** `filter_out()` (NA-safe row removal), `recode_values()` / `replace_values()` (value mapping), `replace_when()` (conditional update), `when_any()` / `when_all()` (logical combination in filter).

**Newly stable:** `.by` argument (prefer over `group_by() |> ... |> ungroup()` for single operations), `reframe()`.

**Never use deprecated functions:** `spread`/`gather` (use `pivot_wider`/`pivot_longer`), `mutate_at/if/all` (use `across()`), `case_match`/`recode` (use `recode_values`/`replace_values`), `do` (use `reframe`), `transmute` (use `mutate(.keep = "none")`). Full blocklist in `rules/references/modern-r.md`.

When uncertain about a function's current API, check docs via `btw_tool_docs_help_page` rather than guessing.
```

- [ ] **Step 2: Trim existing content to stay near 150 lines**

Compress the Package Development Toolchain section (lines 54-62) from 8 lines to 4:

Replace:
```markdown
The canonical modern stack:
- `usethis` — project setup, CI, licensing, boilerplate
- `devtools` — development workflow (`load_all()`, `test()`, `check()`, `document()`)
- `roxygen2` — documentation with markdown support enabled (`use_roxygen_md()`)
- `testthat` 3rd edition — testing (`use_testthat(3)`)
- `pkgdown` — documentation sites
- `styler` — code formatting
- `lintr` — static analysis
```

With:
```markdown
Canonical stack: `usethis` (setup), `devtools` (workflow), `roxygen2` (docs, enable markdown), `testthat` 3e (testing), `pkgdown` (sites), `styler` + `lintr` (formatting/linting).
```

Compress the Environment Management section (lines 44-48) from 4 lines to 2:

Replace:
```markdown
- **renv** for all projects. Check for `renv.lock` at project root.
- For new projects: suggest `renv::init()`.
- Before adding packages: `renv::install("pkg")` then `renv::snapshot()`.
- To restore: `renv::restore()`.
```

With:
```markdown
- **renv** for all projects. Check for `renv.lock`. New projects: `renv::init()`. Add packages: `renv::install("pkg")` then `renv::snapshot()`. Restore: `renv::restore()`.
```

- [ ] **Step 3: Verify final line count**

Run:
```bash
wc -l rules/r-conventions.md
```
Target: ≤160 lines. The 150-line limit is a soft guide; a rule file with high-value content (style principles + anti-patterns) can go slightly over.

- [ ] **Step 4: Verify no convention violations**

Run:
```bash
grep -n '%>%' rules/r-conventions.md
```
Expected: Only in the WRONG examples.

- [ ] **Step 5: Commit**

```bash
git add rules/r-conventions.md
git commit -m "feat(rules): add modern R conventions with dplyr 1.2.0, trim for line budget"
```

---

### Task 4: Add Deprecated Function and Analytical Style Checks to r-code-reviewer.md

**Files:**
- Modify: `agents/r-code-reviewer.md:64-75` (after Common bugs, before Check performance)

- [ ] **Step 1: Add deprecated function check to correctness section**

Insert after line 68 (the last `- `1:length(x)` when...` bullet in Common bugs) and before line 70 (`### 4. Check performance`):

```markdown
- **Deprecated functions:**
  - Any function from the blocklist in `rules/references/modern-r.md` — suggest modern replacement with example
  - `spread()`/`gather()`, `mutate_at/if/all()`, `case_match()`, `recode()`, `do()`, `transmute()` — all have modern equivalents
```

- [ ] **Step 2: Add new analytical style section between correctness and performance**

Insert after the deprecated functions bullet (just added above) and before `### 4. Check performance`. This becomes section 3b, keeping the existing numbering intact:

```markdown

### 3b. Check analytical style

- **Over-abstraction:** Helper functions called only once, parameterized functions where inline code would be clearer, unnecessary closures/factories. Suggest inlining with analytical intent comment. Severity: MEDIUM.
- **Over-commenting:** Mechanical comments that restate what the code does (e.g., "# filter rows where age > 18" before `filter(age > 18)`). Suggest removing or replacing with analytical intent. Severity: MEDIUM.
- **Under-commenting:** Complex multi-step pipelines (4+ operations) with no comment explaining analytical purpose. Suggest one-line intent comment above the pipeline. Severity: MEDIUM.
```

- [ ] **Step 3: Verify line count**

Run:
```bash
wc -l agents/r-code-reviewer.md
```
Expected: ~127 lines (was 112, added ~15). Well under 200-line limit.

- [ ] **Step 4: Verify no convention violations**

Run:
```bash
grep -n '%>%' agents/r-code-reviewer.md
```
Expected: Only in the existing example on line 100.

- [ ] **Step 5: Commit**

```bash
git add agents/r-code-reviewer.md
git commit -m "feat(r-code-reviewer): add deprecated function and analytical style checks"
```

---

### Task 5: Final Verification

- [ ] **Step 1: Check all modified files are within line limits**

Run:
```bash
echo "--- r-conventions.md ---" && wc -l rules/r-conventions.md
echo "--- r-code-reviewer.md ---" && wc -l agents/r-code-reviewer.md
echo "--- modern-r.md ---" && wc -l rules/references/modern-r.md
```
Expected:
- r-conventions.md: ≤160 lines
- r-code-reviewer.md: ≤130 lines
- modern-r.md: ~60 lines

- [ ] **Step 2: Verify no pipe violations across all content**

Run:
```bash
grep -rn '%>%' skills/ agents/ rules/ | grep -v 'WRONG\|Never\|flag any\|not.*%>%\|NEVER'
```
Expected: No matches.

- [ ] **Step 3: Verify all R code examples use correct conventions**

Run:
```bash
grep -rn ' = ' rules/r-conventions.md | grep -v 'never\|Never\|@param\|function\|#\|TRUE\|FALSE\|`.* =.*`'
```
Expected: No assignment with `=` outside of function arguments and documentation.
