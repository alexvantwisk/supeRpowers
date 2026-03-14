# Advanced dplyr Patterns

Loaded lazily from the r-data-analysis skill. These are recipes for
across(), pick(), window functions, rowwise operations, and the .by argument.

---

## across() with Multiple Functions

```r
# Apply multiple summary functions
df |>
  summarise(
    across(
      c(revenue, cost, quantity),
      list(mean = \(x) mean(x, na.rm = TRUE),
           sd = \(x) sd(x, na.rm = TRUE),
           median = \(x) median(x, na.rm = TRUE)),
      .names = "{.col}_{.fn}"
    ),
    .by = region
  )
# Produces: revenue_mean, revenue_sd, revenue_median, cost_mean, ...
```

### .names Glue Syntax

The `.names` argument uses glue syntax with two placeholders:
- `{.col}` — the column name
- `{.fn}` — the function name (from the named list)

```r
# Custom naming patterns
df |> mutate(across(c(x, y), \(col) col * 100, .names = "pct_{.col}"))
# Produces: pct_x, pct_y

df |> summarise(across(where(is.numeric), list(
  lo = \(x) quantile(x, 0.25, na.rm = TRUE),
  hi = \(x) quantile(x, 0.75, na.rm = TRUE)
), .names = "{.fn}_{.col}"))
# Produces: lo_revenue, hi_revenue, lo_cost, hi_cost, ...
```

### across() with Conditional Logic

```r
# Different transformations by column type
df |>
  mutate(
    across(where(is.character), str_to_lower),
    across(where(is.numeric), \(x) round(x, 2)),
    across(where(is.Date), \(x) format(x, "%Y-%m"))
  )
```

---

## pick() for Column Selection Inside Verbs

`pick()` selects columns and returns a tibble — useful inside `mutate()`,
`summarise()`, and other verbs where you need the selected data as a tibble.

```r
# Row-level operations across selected columns
df |>
  mutate(
    row_mean = rowMeans(pick(where(is.numeric)), na.rm = TRUE),
    row_any_na = rowSums(is.na(pick(everything()))) > 0
  )

# Pass picked columns to a function expecting a data frame
df |>
  mutate(
    score = pmap_dbl(pick(q1, q2, q3, q4), \(...) mean(c(...), na.rm = TRUE))
  )
```

---

## reframe() for Multi-Row Summaries

`reframe()` replaces `summarise()` when the result has multiple rows per
group. Unlike `summarise()`, it never warns about multiple-row output.

```r
# Quantile distribution per group
df |>
  reframe(
    probs = c(0.1, 0.25, 0.5, 0.75, 0.9),
    value = quantile(score, c(0.1, 0.25, 0.5, 0.75, 0.9), na.rm = TRUE),
    .by = department
  )

# Top N per group with reframe
df |>
  reframe(
    slice_max(pick(everything()), order_by = revenue, n = 3),
    .by = region
  )
```

---

## Window Functions

Window functions operate within groups without collapsing rows.

### lag() and lead()

```r
# Period-over-period change
df |>
  arrange(date) |>
  mutate(
    prev_value = lag(value),
    next_value = lead(value),
    pct_change = (value - lag(value)) / lag(value) * 100,
    .by = product
  )

# Lag with default fill
df |> mutate(prev = lag(value, default = 0), .by = group)
```

### Cumulative Functions

```r
df |>
  arrange(date) |>
  mutate(
    running_total = cumsum(amount),
    running_max = cummax(amount),
    running_mean = cummean(amount),
    .by = account
  )
```

### Ranking Functions

```r
df |>
  mutate(
    rank = row_number(desc(score)),          # No ties — arbitrary tiebreak
    dense = dense_rank(desc(score)),         # Ties share rank, no gaps
    pct_rank = percent_rank(score),          # 0-1 percentile
    ntile_q = ntile(score, 4),              # Quartile bins
    .by = department
  )
```

---

## rowwise() + c_across()

For row-level computations across many columns. Slower than vectorized
alternatives — prefer `rowMeans()`, `rowSums()`, or `pmap()` when possible.

```r
# Row-level summary across selected columns
df |>
  rowwise() |>
  mutate(
    max_score = max(c_across(starts_with("score"))),
    any_fail = any(c_across(starts_with("score")) < 50)
  ) |>
  ungroup()
```

**Performance note:** `rowwise()` is essentially a loop. For large data:
```r
# Faster alternative using pick() + rowMeans()
df |> mutate(avg = rowMeans(pick(starts_with("score")), na.rm = TRUE))
```

---

## .by Argument (Inline Grouping)

The `.by` argument (dplyr >= 1.1.0) replaces the `group_by() |> ... |>
ungroup()` pattern. The result is always ungrouped.

```r
# PREFERRED: .by for simple grouped operations
df |> summarise(mean_val = mean(x), .by = c(group_a, group_b))
df |> mutate(group_mean = mean(x), .by = group)
df |> filter(x == max(x), .by = group)
df |> slice_max(x, n = 1, by = group)

# USE group_by() WHEN: you need persistent grouping across multiple operations
df |>
  group_by(region) |>
  arrange(date) |>
  mutate(
    cumulative = cumsum(revenue),
    rank = row_number()
  ) |>
  filter(rank <= 5) |>
  ungroup()
```

**Rule of thumb:** Use `.by` for single-verb grouping. Use `group_by()` when
grouping must persist across a chain of verbs.

---

## Common Recipes

### Running Totals

```r
daily_totals <- transactions |>
  summarise(daily_sum = sum(amount), .by = c(account, date)) |>
  arrange(account, date) |>
  mutate(running_balance = cumsum(daily_sum), .by = account)
```

### Group-Level Deduplication

```r
# Keep first occurrence per group (by date)
deduped <- df |>
  arrange(group_id, date) |>
  slice_head(n = 1, by = group_id)

# Keep row with max value per group
best_per_group <- df |>
  slice_max(score, n = 1, by = group_id, with_ties = FALSE)
```

### Rolling Calculations (with slider)

For true rolling windows, use the `slider` package:

```r
library(slider)

df |>
  arrange(date) |>
  mutate(
    rolling_mean_7d = slide_dbl(value, mean, .before = 6, .complete = TRUE),
    rolling_sum_30d = slide_dbl(value, sum, .before = 29, .complete = TRUE),
    .by = group
  )
```

### Conditional Aggregation

```r
df |>
  summarise(
    total = sum(amount),
    total_positive = sum(amount[amount > 0]),
    count_missing = sum(is.na(value)),
    pct_complete = mean(!is.na(value)) * 100,
    .by = category
  )
```

### Pivoting Summary Statistics

```r
# Compute multiple stats then pivot for a report-friendly layout
df |>
  summarise(
    across(c(revenue, cost),
      list(mean = \(x) mean(x, na.rm = TRUE),
           total = \(x) sum(x, na.rm = TRUE)),
      .names = "{.col}__{.fn}"
    ),
    .by = region
  ) |>
  pivot_longer(
    cols = -region,
    names_to = c("metric", "stat"),
    names_sep = "__",
    values_to = "value"
  )
```
