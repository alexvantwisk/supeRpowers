# Data Cleaning Toolkit

`janitor` for cleaning column names, frequencies, and dupes; `naniar` for
missing-data exploration. All code uses `|>` and `<-`.

---

## janitor::clean_names() — Tidy Column Names

```r
df <- read_csv("messy.csv")
names(df)
#> [1] "First Name" "Last Name!" "Email Address" "DOB (YYYY-MM-DD)"

df <- df |> janitor::clean_names()
names(df)
#> [1] "first_name" "last_name" "email_address" "dob_yyyy_mm_dd"

# Other case styles
df |> janitor::clean_names(case = "small_camel")  # firstName, lastName
df |> janitor::clean_names(case = "screaming_snake")  # FIRST_NAME
```

**Rule:** Run `clean_names()` immediately after import. It is idempotent and
removes a class of bugs caused by spaces, parentheses, and unicode in
column names. Never paper over messy names with backticks.

---

## janitor::tabyl() — Frequency Tables

```r
# 1-way tabulation with counts and percentages
df |> janitor::tabyl(category)

# 2-way crosstab
df |> janitor::tabyl(category, region)

# Polish for display
df |>
  janitor::tabyl(category, region) |>
  janitor::adorn_totals("row") |>
  janitor::adorn_percentages("col") |>
  janitor::adorn_pct_formatting(digits = 1) |>
  janitor::adorn_ns()
```

`tabyl()` is the cleanest tidyverse-friendly answer to base `table()`.
Output is a tibble — pipe directly into ggplot or gt.

---

## janitor::remove_empty() and get_dupes()

```r
# Drop empty columns and rows in one call
df |> janitor::remove_empty(c("rows", "cols"))

# Drop columns where everything is constant (no information)
df |> janitor::remove_constant()

# Find rows that are exact duplicates on a key
df |> janitor::get_dupes(customer_id)

# Inspect duplicate counts before deciding to dedupe
df |> janitor::get_dupes(customer_id, order_date) |> count(customer_id)
```

`get_dupes()` returns the duplicates with a `dupe_count` column — much
clearer than `count() |> filter(n > 1)` then re-joining back.

---

## naniar::miss_var_summary() — Per-Column Missingness

```r
# What fraction is missing in each column?
df |> naniar::miss_var_summary()
#> # A tibble: 6 x 3
#>   variable   n_miss pct_miss
#>   <chr>       <int>    <num>
#> 1 income        523     34.9
#> 2 occupation    302     20.1
#> ...

# Per-row missingness summary
df |> naniar::miss_case_summary()

# Missingness by group
df |>
  group_by(region) |>
  naniar::miss_var_summary()
```

---

## naniar Visualisation: vis_miss() and gg_miss_*()

```r
# Heatmap of missingness across the full data frame
naniar::vis_miss(df, sort_miss = TRUE)

# Variable-level missing counts as a bar chart
naniar::gg_miss_var(df, facet = treatment_arm)

# Co-occurrence: which variables tend to be missing together?
naniar::gg_miss_upset(df)
```

These are the fastest way to spot **MCAR/MAR/MNAR patterns** before
deciding to drop, impute, or model the missingness.

---

## Missing-Data Decision Tree

| Pattern | Risk | Default action |
|---------|------|----------------|
| Random scattered NAs (<5%, MCAR-ish) | Low | `drop_na()` on the affected variables only |
| Block of related NAs (e.g. all "income_*") | Moderate | `naniar::vis_miss()` to confirm; investigate before dropping |
| NAs concentrated in one group | High — selection bias | DO NOT `drop_na()` blindly; report missingness per group first |
| MNAR (missingness depends on the value itself) | High — biased estimates | Multiple imputation (mice/Amelia) or model jointly — defer to r-stats |

```r
# Safer than drop_na() on the whole frame: drop only on key analysis cols
df |>
  drop_na(treatment, outcome) |>
  naniar::miss_var_summary()      # confirm what remains
```

**Rule:** Always run `naniar::miss_var_summary()` and `vis_miss()` BEFORE
calling `drop_na()` or `na.omit()`. Quantify missingness, characterise its
pattern, and only then choose a strategy.

---

## When to Defer Imputation

Simple imputation (`replace_na(x, median(x, na.rm = TRUE))`) belongs here.
But **anything model-based — multiple imputation, MICE, predictive mean
matching, group-conditional imputation** — is statistical modeling. Defer
to:

- `r-stats` for inference-focused multiple imputation (`mice`, `Amelia`)
- `r-tidymodels` for predictive imputation as a recipe step
  (`step_impute_*`)

A skill that performs imputation must report:
1. The fraction missing per variable
2. The chosen method and why
3. Whether the analysis was run on multiple imputed datasets and pooled

---

## Gotchas

| Trap | Fix |
|------|-----|
| Backticks all over a script (`` `Customer Name` ``) | Run `janitor::clean_names()` once at import |
| `names(df) <- tolower(gsub(...))` reinventing wheel | Use `janitor::clean_names()` |
| `count() |> filter(n > 1)` to find dupes | Use `janitor::get_dupes()` — returns the offending rows directly |
| `drop_na()` on the whole frame silently drops 60% | Always quantify missingness first with `naniar::miss_var_summary()` |
| `na.omit()` — base — drops rows with ANY NA | Prefer `drop_na(specific_cols)` to scope the drop |
| Imputing without diagnostics | Report `miss_var_summary()` before/after; document method choice |
| Treating "" or "NA" string as data | Pass `na = c("", "NA", "N/A")` to `read_csv()` |
