# Lever 2: Statistical Programmer Identity

## Problem

Claude writes R like a software engineer — extracting helpers, chasing DRY, building abstractions, using clever functional patterns. Statistical programmers want the opposite: linear, traceable pipelines where you can follow the analytical logic top-to-bottom.

Additionally, Claude's training data is stale. It reaches for deprecated functions (`spread`, `gather`, `case_match`), old API surfaces, and doesn't know about recent package releases like dplyr 1.2.0.

Comments are also problematic in both directions: either absent (no analytical intent) or overdone (code gets lost between comments).

## Goal

Reshape how Claude thinks about R code — prioritizing readability and analytical traceability over software engineering abstractions, and enforcing modern function usage.

## Three Changes

### 1. Statistical Programming Style (r-conventions.md)

New section (~25 lines) establishing the coding identity.

**Core principles:**

- **Linear over abstract** — Prefer a clear sequential pipeline over extracting a helper function. If the logic runs once, it stays inline.
- **Readable over DRY** — Three similar pipelines are better than one parameterized function that's harder to trace. Only extract when repetition genuinely causes maintenance risk (5+ occurrences or bug-prone logic).
- **Analytical intent comments** — Comment WHY you're filtering, joining, or transforming, not what the code does mechanically. One comment per logical block, not per line. No comments on obvious code.
- **Flat over nested** — Avoid deeply nested `map(map(map(...)))`. Break into named intermediate steps with meaningful names that describe the analytical state (e.g., `enrolled_patients`, `baseline_labs`).
- **Explicit over clever** — `if_else()` over `case_when()` for binary choices. Named intermediate variables over long chains. No anonymous functions where a named step would be clearer.

**Anti-pattern example:**

```r
# WRONG: developer instinct — abstract into a helper
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
```

**Comment anti-pattern:**

```r
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

### 2. Modern R Section (r-conventions.md)

New section (~30 lines) addressing stale training data with two components.

**A) New functions to prefer (dplyr 1.2.0+):**

| Function | Use for | Replaces |
|----------|---------|----------|
| `filter_out()` | Drop rows matching conditions (NA-safe) | `filter(!(cond) \| is.na(...))` |
| `recode_values()` | Map values to new values (formula or lookup) | `case_match()`, `recode()` |
| `replace_values()` | Partially update column by value match | `if_else(x == val, new, x)`, `recode()`, `tidyr::replace_na()` |
| `replace_when()` | Partially update column by condition | `case_when(..., .default = x)` |
| `when_any()` / `when_all()` | Combine logicals in filter | Manual `\|` / `&` chains across columns |

**Recoding/replacing decision guide (2x2 family):**

|  | New column (recode) | Update existing (replace) |
|--|---------------------|--------------------------|
| **By condition** | `case_when()` | `replace_when()` |
| **By value** | `recode_values()` | `replace_values()` |

**Newly stable:** `.by` argument and `reframe()` are stable as of dplyr 1.2.0. Prefer `.by` over `group_by() |> ... |> ungroup()` for single-operation grouping.

**B) Deprecated function blocklist:**

| Deprecated | Use instead | Since |
|-----------|-------------|-------|
| `spread()` | `pivot_wider()` | tidyr 1.0 |
| `gather()` | `pivot_longer()` | tidyr 1.0 |
| `summarise_each()` / `mutate_each()` | `across()` | dplyr 1.0 |
| `mutate_at()` / `mutate_if()` / `mutate_all()` | `across()` | dplyr 1.0 |
| `funs()` | `list()` of lambdas | dplyr 0.8 |
| `do()` | `reframe()` or `nest() \|> mutate(map(...))` | dplyr 1.1 |
| `transmute()` | `mutate(.keep = "none")` | dplyr 1.1 |
| `case_match()` | `recode_values()` / `replace_values()` | dplyr 1.2 |
| `recode()` | `recode_values()` / `replace_values()` | dplyr 1.2 |

**Uncertainty protocol:** When unsure about a function's current API, say so and check docs via `btw_tool_docs_help_page` (ties into Lever 1). Better to be explicit about uncertainty than to confidently use a deprecated signature.

### 3. Code Reviewer Agent Updates (r-code-reviewer.md)

Two new check categories added to existing procedure:

**In Section 3 (Check correctness), add:**

- **Deprecated functions:** Flag any function from the blocklist. Suggest modern replacement with example. Severity: HIGH.

**New Section (between correctness and performance), add:**

### Check analytical style

- **Over-abstraction:** Flag helper functions called only once, parameterized functions where inline would be clearer, unnecessary closures/factories. Suggest inlining with analytical intent comment. Severity: MEDIUM.
- **Over-commenting:** Flag mechanical comments that restate what the code does. Suggest replacing with analytical intent or removing. Severity: MEDIUM.
- **Under-commenting:** Flag complex multi-step pipelines (4+ steps) with no comment explaining the analytical purpose. Suggest one-line intent comment. Severity: MEDIUM.

## Files Changed

| File | Change | Lines Added |
|------|--------|-------------|
| `rules/r-conventions.md` | Add "Statistical Programming Style" section | ~25 |
| `rules/r-conventions.md` | Add "Modern R" section (new functions + deprecated blocklist) | ~30 |
| `agents/r-code-reviewer.md` | Add deprecated function check to correctness section | ~5 |
| `agents/r-code-reviewer.md` | Add new "Check analytical style" section | ~10 |

## Files NOT Changed

- No new skills or agents created
- Existing anti-patterns table preserved and extended
- Skill SKILL.md files not modified — conventions rule propagates automatically

## Verification

- [ ] r-conventions.md stays under 150 lines (current: 138, adding ~55 = ~193 — may need to tighten existing content or split into a reference)
- [ ] r-code-reviewer.md stays under 200 lines (current: 112, adding ~15 = ~127)
- [ ] No `%>%` in any examples
- [ ] All example code uses `<-`, snake_case, double quotes
- [ ] Anti-pattern examples show WRONG and RIGHT clearly
- [ ] Deprecated blocklist matches actual lifecycle status in dplyr 1.2.0, tidyr 1.0+

## Note on Line Limits

r-conventions.md is a rule file (150-line limit per CLAUDE.md). Adding ~55 lines puts it at ~193. Two options:

1. **Tighten existing content** — compress some sections (e.g., combine environment management, shorten tidy eval section)
2. **Move detailed tables to a reference** — create `rules/references/modern-r.md` for the blocklist/new function tables, keep only the principles inline

Recommendation: Option 2. Keep the principles and anti-pattern examples in the rule (high-signal, always loaded). Move the detailed lookup tables to a reference (loaded on demand).
