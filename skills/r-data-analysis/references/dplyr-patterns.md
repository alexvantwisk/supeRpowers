# Advanced dplyr Patterns

Recipes for `across()`, `pick()`, window functions, `.by`, `reframe()`,
`consecutive_id()`, and `case_match()`. All code uses `|>` and `<-`.

---

## across() — Column-wise Operations

```r
# Apply multiple functions to multiple columns
df |>
  summarise(
    across(where(is.numeric), list(mean = mean, sd = sd), na.rm = TRUE),
    .by = group
  )

# Transform columns matching a pattern
df |>
  mutate(across(starts_with("score_"), \(x) (x - mean(x)) / sd(x)))

# Rename while transforming
df |>
  summarise(across(c(revenue, cost), mean, .names = "avg_{.col}"), .by = region)
```

**Key selectors:** `where(is.numeric)`, `starts_with()`, `ends_with()`,
`matches()`, `all_of()`, `any_of()`.

---

## pick() — Column Selection Inside Verbs

```r
# Use pick() inside mutate/summarise to grab columns as a tibble
df |>
  mutate(row_mean = rowMeans(pick(where(is.numeric)), na.rm = TRUE))

# pick() replaces deprecated across(.fns = NULL) pattern
df |>
  summarise(n_complete = sum(complete.cases(pick(everything()))), .by = group)
```

**Rule:** Use `across()` when applying functions to columns. Use `pick()`
when you need the selected columns as a data frame (e.g., for `rowMeans()`,
`complete.cases()`).

---

## .by — Per-operation Grouping

```r
# .by replaces group_by() |> ... |> ungroup()
df |> summarise(total = sum(revenue), .by = c(region, product))
df |> mutate(pct = revenue / sum(revenue), .by = region)
df |> filter(revenue == max(revenue), .by = region)
df |> slice_max(revenue, n = 3, by = region)
```

**Prefer `.by` over `group_by()`** — avoids forgotten `ungroup()` bugs
and makes grouping scope explicit per operation.

---

## filter() vs filter_out() (dplyr >= 1.2)

```r
# filter() keeps rows where the condition is TRUE — NAs are dropped silently
df |> filter(class != "suv")             # also drops rows with NA class

# filter_out() drops rows where the condition is TRUE — NAs are kept
df |> filter_out(class == "suv")         # keeps NA class rows
```

**Rule:** When the *intent* is "drop these rows", use `filter_out()` —
matches intuition with NAs and avoids the `!(... | is.na(...))` boolean
gymnastics that `filter()` forces. New in dplyr 1.2 (Feb 2026).

---

## reframe() — Multi-row Summaries

```r
# When summary returns multiple rows per group, use reframe() not summarise()
df |>
  reframe(
    quantile = c(0.25, 0.50, 0.75),
    value = quantile(revenue, c(0.25, 0.50, 0.75)),
    .by = region
  )

# Distribution summaries
df |>
  reframe(broom::tidy(t.test(score)), .by = treatment)
```

`summarise()` warns when results have >1 row per group. `reframe()` is the
explicit replacement for multi-row summaries.

---

## consecutive_id() — Run-length Grouping

```r
# Identify consecutive runs of the same value
df |>
  mutate(run_id = consecutive_id(status))

# Summarise consecutive sequences
events |>
  summarise(
    start = min(timestamp),
    end = max(timestamp),
    duration = difftime(max(timestamp), min(timestamp), units = "hours"),
    .by = c(user_id, consecutive_id(event_type))
  )
```

---

## recode_values() / replace_values() — Value Mapping (dplyr >= 1.2)

```r
# recode_values() — create a new vector by mapping old → new values
df |>
  mutate(region_name = recode_values(
    region_code,
    "NE" ~ "Northeast",
    "SE" ~ "Southeast",
    "MW" ~ "Midwest",
    "W"  ~ "West",
    default = "Unknown"
  ))

# Collapse multiple values into a bucket
df |>
  mutate(size = recode_values(
    n_employees,
    1:10 ~ "Small",
    11:100 ~ "Medium",
    default = "Large"
  ))

# replace_values() — partially update; unmatched values keep their original
df |> mutate(status = replace_values(status, "n/a" ~ NA, "" ~ NA))

# Lookup-table form with from/to vectors
codes  <- c("NE", "SE", "MW", "W")
names  <- c("Northeast", "Southeast", "Midwest", "West")
df |> mutate(region_name = recode_values(region_code, from = codes, to = names))
```

**dplyr 1.2 (Feb 2026):** `case_match()` is soft-deprecated and `recode()`
is superseded — use `recode_values()` (new vector) or `replace_values()`
(partial update). Older code using `case_match()` still works but warns.
Use `case_when()` for conditional logic with expressions.

---

## Window Functions

```r
# Ranking
df |> mutate(rank = row_number(desc(score)), .by = group)
df |> mutate(dense_rank = dense_rank(desc(score)), .by = group)
df |> mutate(pct_rank = percent_rank(score), .by = group)
df |> mutate(ntile = ntile(score, 4), .by = group)

# Lead/lag
df |> mutate(
  prev_value = lag(value),
  next_value = lead(value),
  change = value - lag(value),
  .by = group
)

# Cumulative
df |> mutate(
  running_total = cumsum(revenue),
  running_mean = cummean(revenue),
  running_max = cummax(revenue),
  .by = group
)
```

---

## rowwise() — Row-level Operations

```r
# When vectorized operations are not available
df |>
  rowwise() |>
  mutate(best = max(c_across(starts_with("score_")))) |>
  ungroup()

# Prefer pick() + rowMeans/rowSums when possible (faster)
df |> mutate(avg = rowMeans(pick(starts_with("score_")), na.rm = TRUE))
```

**Rule:** Prefer vectorized alternatives (`rowMeans()`, `rowSums()`,
`pmin()`, `pmax()`) over `rowwise()` — they are much faster.

---

## nest() + unnest() — List-columns

```r
# Collapse each group into a tibble in a list-column
by_cyl <- mtcars |> nest(.by = cyl)
by_cyl
#> # A tibble: 3 x 2
#>     cyl data
#>   <dbl> <list>
#> 1     6 <tibble [7 x 10]>
#> 2     4 <tibble [11 x 10]>
#> 3     8 <tibble [14 x 10]>

# Pair with map() for per-group modeling — see references/purrr-patterns.md
by_cyl |>
  mutate(fit = map(data, \(d) lm(mpg ~ wt, data = d)),
         tidied = map(fit, broom::tidy)) |>
  unnest(tidied)
```

Use `nest(.by =)` instead of `group_by() |> nest()` — explicit and less
verbose. Read `references/purrr-patterns.md` for `map()`-on-nested patterns.

---

## Patterns with .env and .data Pronouns

```r
# .data refers to the data frame column (avoids ambiguity)
filter_by <- function(df, col, val) {
  df |> filter(.data[[col]] == val)
}

# .env refers to the calling environment
threshold <- 100
df |> filter(.data[["revenue"]] > .env[["threshold"]])

# Preferred: use embracing {{ }} for tidy eval
filter_col <- function(df, col, val) {
  df |> filter({{ col }} == val)
}
```

---

## Gotchas

| Trap | Fix |
|------|-----|
| `across()` inside `filter()` silently dropped | Use `if_any()` or `if_all()` for filtering across columns |
| `rowwise()` is slow on large data | Use `rowMeans(pick(...))` or `pmap()` instead |
| `pick()` in `filter()` context | `pick()` works in `mutate()`/`summarise()`, use `if_any()`/`if_all()` in `filter()` |
| `.by` not available in older dplyr | Requires dplyr >= 1.1.0; fall back to `group_by()` |
| `case_match()` soft-deprecated (dplyr 1.2) | Use `recode_values()` (new vector) or `replace_values()` (partial update) |
| Underscored verbs `mutate_()`/`arrange_()` | Defunct in dplyr 1.2 — use the unsuffixed verbs with `across()` / tidyselect |
| `summarise()` returning >1 row per group | Defunct in dplyr 1.2 — use `reframe()` |
| Recoding type mismatch | Ensure match values are the same type as the input column (`recode_values()` errors loudly on mismatch) |
