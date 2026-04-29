---
name: r-data-analysis
description: >
  Use when working with data wrangling, cleaning, transformation, reshaping,
  or import in R using dplyr, tidyr, readr, lubridate, stringr, forcats, or
  purrr. Provides expert guidance on tidy data principles, column
  manipulation, joins, type conversion, string and date processing, factor
  reordering, list-columns, missing-data EDA, and data validation in
  pipelines.
  Triggers: data wrangling, data cleaning, data transformation, dplyr, tidyr,
  readr, mutate, filter, pivot, join, reshape, stringr, forcats, lubridate,
  purrr, pipe, regex, time zone, nested data, list-columns, factor reorder,
  clean names, data validation, missing data EDA, data manipulation, tidy
  data, clean data.
  Do NOT use for statistical modeling or hypothesis testing — use r-stats instead.
  Do NOT use for performance optimization of large datasets — use r-performance instead.
  Do NOT use for pipeline orchestration — use r-targets instead.
  For a guided analysis pipeline, invoke /r-analysis instead.
---

# R Data Analysis

Tidyverse-first data wrangling, cleaning, and transformation in R.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/dplyr-patterns.md` for advanced across()/pick()/window/nest recipes
- Read `references/join-guide.md` for complex join strategies and decision trees
- Read `references/tidyr-reshape.md` for pivots, unnesting, separating, completing
- Read `references/stringr-recipes.md` for regex, extraction, replacement, splitting
- Read `references/lubridate-recipes.md` for parsers, time zones, periods vs durations
- Read `references/forcats-recipes.md` for factor reorder/lump/recode/collapse
- Read `references/purrr-patterns.md` for typed map_*, list-columns, error handling
- Read `references/data-cleaning-toolkit.md` for janitor + naniar missing-data EDA
- Read `references/data-validation.md` for pointblank/validate pipelines

**Agent dispatch:** When analysis crosses into statistical modeling (regression,
hypothesis testing, mixed models), hand off to the **r-statistician** agent.
If the r-statistician agent is not yet available, provide basic modeling
guidance inline.

**MCP integration (when R session available):**
- Before joins or transformations: `btw_tool_env_describe_data_frame` to inspect column names, types, and dimensions of input data frames
- Before referencing specific columns: verify they exist in the actual data, not just assumed from context
- When uncertain about a function's arguments: `btw_tool_docs_help_page` to read installed docs

---

## Tidy-Data Principles

Every analysis starts by reshaping data into tidy form:

1. Each **variable** is a column.
2. Each **observation** is a row.
3. Each **value** is a cell.

If a column name encodes a value (e.g. `revenue_2024`, `q1_sales`), the
data is wide — pivot longer first. If multiple variables share a column,
split them. If one observation spans multiple rows, pivot wider.

Read `references/tidyr-reshape.md` for `pivot_longer`/`pivot_wider`,
`unnest_*`, `separate_wider_*`, `complete`, and `fill`.

---

## Data Import with readr

```r
# Always specify col_types in production — silent guessing causes subtle bugs
df <- read_csv("data/sales.csv", col_types = cols(
  id = col_integer(), date = col_date(format = "%Y-%m-%d"),
  amount = col_double(), category = col_character()
))

# Messy files: custom NA strings, skip rows, encoding
df <- read_csv("data/messy.csv",
  na = c("", "NA", "N/A", "null", "-"), skip = 2,
  locale = locale(encoding = "latin1")
)
```

---

## dplyr & tidyr Conventions

Use `.by` argument (not `group_by()`) for per-operation grouping. Use `across()` with `where()` or tidyselect for column-wise operations. Use `reframe()` when a summary returns multiple rows per group.

```r
# .by replaces group_by() + ungroup() — avoids forgotten ungroup() bugs
df |> summarise(total = sum(revenue), .by = c(region, product))
df |> summarise(across(where(is.numeric), list(mean = mean, sd = sd), na.rm = TRUE), .by = group)
```

Use `pivot_longer()` / `pivot_wider()` exclusively — `gather()`/`spread()` are deprecated. Use `separate_wider_delim()` not `separate()`. Use `nest(.by =)` + `map()` for group-level modeling.

---

## Joins

Use `join_by()` for all joins — supports equality and inequality conditions.

```r
orders |> left_join(customers, join_by(customer_id))
sales |> inner_join(targets, join_by(region, year))

# Filtering joins — no columns added
orders |> semi_join(active_customers, join_by(customer_id))   # keep matches
orders |> anti_join(active_customers, join_by(customer_id))   # keep orphans
```

Use `left_join()` to preserve all left-side rows (most common),
`inner_join()` when both sides must match, `anti_join()` to find orphans.
Read `references/join-guide.md` for inequality joins and complex strategies.

---

## stringr — Strings and Regex

Always prefer stringr over base `grep`/`sub`/`gsub` — consistent
`string`-first argument order, vectorised, locale-aware. Reach for
`str_detect()` to filter, `str_extract()` to capture, `str_replace_all()`
to substitute. Use `fixed()` for literal substrings, `regex()` for
patterns, `coll()` for accent-insensitive matching.

Read `references/stringr-recipes.md` for the regex cheatsheet, splitting,
padding, case conversion, and `glue` interop.

---

## lubridate — Dates and Times

Always use lubridate parsers (`ymd()`, `mdy()`, `ymd_hms()`) over
`as.Date()` — `as.Date()` silently returns NA on unrecognised formats. For
mixed input, use `parse_date_time()` with multiple `orders`. Use `%m+%`
when adding months to month-end dates. Distinguish `with_tz()` (convert
instant to another zone) from `force_tz()` (relabel a wall-clock time).

Read `references/lubridate-recipes.md` for parsers, components, periods
vs durations, time zones, and `floor_date()` for time-series binning.

---

## forcats — Factors

Use `fct_reorder()` (by a summary stat) for self-sorting boxplots and bar
charts; never reach for `factor(..., levels = ...)` manual gymnastics. Use
`fct_lump_n()` to collapse rare levels into "Other", `fct_collapse()` /
`fct_recode()` for renaming, and `fct_na_value_to_level()` to make NAs an
explicit, visible level.

Read `references/forcats-recipes.md` for the full reorder, lump, modify,
and missing-NA family.

---

## purrr — Functional Patterns

Use typed `map_*` variants (`map_dbl`, `map_chr`, `map_lgl`) over
`sapply()` — type-safe and fail-fast. For per-group modeling, replace `for`
loops with `nest(.by =) |> mutate(fit = map(data, ...))`. Wrap fragile
operations in `safely()` / `possibly()`.

Read `references/purrr-patterns.md` for `map2`/`pmap`, list-columns with
broom, list rectangling (`hoist`), and `across()` vs `map()` boundaries.

---

## Data Cleaning: janitor + naniar

Run `janitor::clean_names()` immediately after import — it is idempotent
and removes a class of name-related bugs. Use `janitor::get_dupes()` to
inspect duplicate rows on a key, and `tabyl()` for tidyverse-friendly
frequency tables. Before calling `drop_na()` on the whole frame, run
`naniar::miss_var_summary()` and `naniar::vis_miss()` to characterise the
missingness pattern — dropping blindly bakes in selection bias.

Read `references/data-cleaning-toolkit.md` for the missing-data decision
tree and when to defer imputation modeling to r-stats / r-tidymodels.

---

## Data Validation: pointblank / validate

For pipelines that fan out into reports or models, validate on ingest
with `pointblank::create_agent()` + rule functions + `interrogate()` —
not scattered `stopifnot()` chains. Catches schema drift, type drift,
out-of-range values, and duplicate keys with one report.

Read `references/data-validation.md` for rule functions, action levels,
YAML round-trip, and the boundary against r-package-skill-generator (a
*"build a skill from the pointblank repo"* request still routes there).

---

## Missing Data — Quick Reference

```r
df |> summarise(across(everything(), \(x) sum(is.na(x))))  # diagnose
df |> drop_na(revenue, date)                                # scoped drop
df |> mutate(score = replace_na(score, 0),                  # replace
             label = coalesce(label, backup_label, "unknown"))
```

For pattern characterisation and the bias decision tree, read
`references/data-cleaning-toolkit.md`.

---

## data.table Boundary

> For performance optimization of large datasets, use r-performance instead.

Consider `data.table` when: dataset >1M rows, memory-constrained, or
performance-critical inner loops; `fread()`/`fwrite()` are significantly
faster for file I/O. For most analysis under 1M rows, dplyr is clearer
and preferred.

---

## Verification

After joins: compare row counts before/after. After type conversion: verify with `glimpse()`. After reshaping: check dimensions match expectation.

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `%>%` instead of `\|>` | Convention violation; base pipe is project standard | Always use `\|>` — never `%>%` |
| Omitting `col_types` in `read_csv()` | Silent type guessing causes subtle downstream bugs | Always specify `col_types` explicitly in production code |
| `=` for assignment | Convention violation; `<-` is project standard | Use `<-` for assignment, `=` only in function arguments |
| Joining without checking duplicates | Silent row multiplication when join keys are not unique | Run `count()` on join keys first; assert no duplicates |
| `.` placeholder with `\|>` | Base pipe does not support `.` placeholder like magrittr | Use anonymous function: `x \|> (\(d) lm(y ~ x, data = d))()` |
| Forgetting `ungroup()` | Grouped data frame silently changes downstream `mutate()`/`summarise()` behavior | Use `.by` argument instead, or call `ungroup()` explicitly |
| `gather()`/`spread()` | Deprecated; superseded by `pivot_longer()`/`pivot_wider()` | Use `pivot_longer()` and `pivot_wider()` exclusively |
| Scope creep | Claude rewrites entire pipeline when asked to fix one step | Fix only the identified issue; show minimal diff |

---

## Examples

### Happy Path: Reshape wide-to-long, clean, and summarise

**Prompt:** "Monthly columns (jan-dec) need to be long, clean missing values, then summarise by region."

```r
# Input
wide_sales <- tribble(
  ~region,  ~jan, ~feb, ~mar,
  "North",  100,  NA,   130,
  "South",  200,  210,  220
)

# Output
wide_sales |>
  pivot_longer(cols = jan:mar, names_to = "month", values_to = "sales") |>
  mutate(month = fct_relevel(month, "jan", "feb", "mar")) |>
  drop_na(sales) |>
  summarise(avg_sales = mean(sales), n_months = n(), .by = region)
#> # A tibble: 2 x 3
#>   region avg_sales n_months
#>   <chr>      <dbl>    <int>
#> 1 North       115.        2
#> 2 South       210.        3
```

### Edge Case: Join with duplicates causing silent row fan-out

**Prompt:** "Left join orders to customers, but some customers have multiple addresses."

```r
# Input — addresses has duplicates on customer_id
orders <- tibble(order_id = 1:3, customer_id = c(10, 20, 10))
addresses <- tibble(customer_id = c(10, 10, 20), city = c("NYC", "LA", "CHI"))

# BAD: silent fan-out — 3 orders become 4 rows
orders |> left_join(addresses, join_by(customer_id))
#> # A tibble: 4 x 3   <-- unexpected extra row!

# GOOD: detect duplicates first, then deduplicate before joining
addresses |> count(customer_id) |> filter(n > 1)  # find duplicates
primary <- addresses |> slice_head(n = 1, by = customer_id)
orders |> left_join(primary, join_by(customer_id))
#> # A tibble: 3 x 3   <-- correct row count
```

**More example prompts:**
- "Compute average satisfaction by department, excluding incomplete surveys"
- "Z-score all numeric columns within each group"
- "Last 90 days, clean names, weekly totals by region"
- "Which customers have zero orders?"
