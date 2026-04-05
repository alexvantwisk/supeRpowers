# Join Strategy Guide

Decision trees, inequality joins, rolling joins, cross joins, and diagnostics.
All code uses `|>` and `<-`.

---

## Join Decision Tree

```
Need columns from both tables?
  YES → Which rows to keep?
    All left rows    → left_join()
    Only matches     → inner_join()
    All rows (both)  → full_join()
    All right rows   → right_join()
  NO → Filtering only?
    Keep matches     → semi_join()
    Keep non-matches → anti_join()
```

---

## join_by() — Modern Join Syntax

```r
# Equality join (standard)
orders |> left_join(customers, join_by(customer_id))

# Different column names
orders |> left_join(products, join_by(prod_code == product_id))

# Multiple keys
sales |> inner_join(targets, join_by(region, year, quarter))
```

Always use `join_by()` — it is clearer and supports inequality conditions.

---

## Inequality Joins

```r
# Events within a time window
events |>
  left_join(
    windows,
    join_by(user_id, between(event_time, window_start, window_end))
  )

# Comparison joins
employees |>
  inner_join(
    salary_bands,
    join_by(department, salary >= band_min, salary < band_max)
  )
```

**Helpers inside `join_by()`:**
- `between(x, lower, upper)` — equivalent to `x >= lower, x <= upper`
- `within(x_lower, x_upper, y_lower, y_upper)` — range containment
- `overlaps(x_lower, x_upper, y_lower, y_upper)` — range overlap

---

## Rolling Joins with closest()

```r
# Match each trade to the most recent quote (as-of join)
trades |>
  left_join(
    quotes,
    join_by(ticker, closest(trade_time >= quote_time))
  )

# Match events to the nearest prior reference point
events |>
  left_join(
    milestones,
    join_by(project_id, closest(event_date >= milestone_date))
  )
```

`closest()` finds the nearest match satisfying the inequality — essential
for time-series as-of joins.

---

## Cross Joins

```r
# All combinations of two tables
expand_grid(color = c("red", "blue"), size = c("S", "M", "L"))

# Cross join with dplyr
colors |> cross_join(sizes)
```

Use sparingly — output rows = `nrow(a) * nrow(b)`.

---

## Duplicate Protection with relationship

```r
# Enforce one-to-one join (error if duplicates exist)
orders |>
  left_join(shipments, join_by(order_id), relationship = "one-to-one")

# Enforce many-to-one (each left row matches at most one right row)
orders |>
  left_join(customers, join_by(customer_id), relationship = "many-to-one")

# Enforce one-to-many
customers |>
  left_join(orders, join_by(customer_id), relationship = "one-to-many")
```

**Values:** `"one-to-one"`, `"one-to-many"`, `"many-to-one"`, `"many-to-many"`.

Use `relationship` to catch unexpected duplicates at join time instead of
debugging silent row fan-out downstream.

---

## Join Diagnostics

```r
# BEFORE joining: check key uniqueness
customers |> count(customer_id) |> filter(n > 1)

# Row count audit
n_before <- nrow(orders)
result <- orders |> left_join(customers, join_by(customer_id))
n_after <- nrow(result)
stopifnot(n_after == n_before)  # left_join should preserve left row count

# Find orphans (unmatched keys)
orders |> anti_join(customers, join_by(customer_id))

# Find overlap (matching keys)
orders |> semi_join(customers, join_by(customer_id)) |> nrow()
```

**Rule:** Always compare row counts before and after a join. Use `anti_join()`
to investigate unmatched rows.

---

## Multi-key and Complex Strategies

```r
# Composite key join
transactions |>
  left_join(
    exchange_rates,
    join_by(currency, closest(txn_date >= rate_date))
  )

# Staged joins (build up context step by step)
orders |>
  left_join(customers, join_by(customer_id)) |>
  left_join(products, join_by(product_id)) |>
  left_join(regions, join_by(store_id == store_id))

# Coalesce after full join (merge columns from both sides)
full_join(source_a, source_b, join_by(id)) |>
  mutate(
    name = coalesce(name.x, name.y),
    value = coalesce(value.x, value.y)
  ) |>
  select(-ends_with(".x"), -ends_with(".y"))
```

---

## Gotchas

| Trap | Fix |
|------|-----|
| Silent row multiplication from duplicate keys | Check key uniqueness with `count()` before join, or use `relationship` argument |
| `left_join()` dropping columns with same name | Use `suffix` argument: `left_join(x, y, suffix = c("_order", "_customer"))` |
| Join on character vs factor column | Ensure matching types: `mutate(id = as.character(id))` before join |
| Inequality join producing Cartesian explosion | Add equality keys first to constrain the match space |
| Forgetting `unmatched = "error"` | Use `unmatched = "error"` to fail fast on unexpected orphan rows |
| `NA` keys match other `NA` keys | By default `NA == NA` is `TRUE` in joins; filter NAs from keys if unwanted |
