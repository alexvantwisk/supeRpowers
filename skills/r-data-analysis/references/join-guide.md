# Join Strategy Guide

All seven dplyr join verbs, inequality and rolling joins, cross/nest joins,
and the dplyr 1.1 safety arguments (`relationship`, `multiple`, `unmatched`).
All code uses `|>` and `<-`.

---

## Join Decision Tree

```
Need columns from both tables?
  YES → Want one row per x-row, with y rows nested?
    YES → nest_join()                       (list-column of matches)
    NO  → Which rows to keep?
      All left rows    → left_join()
      Only matches     → inner_join()
      All rows (both)  → full_join()
      All right rows   → right_join()
  NO → Filtering only?
    Keep matches     → semi_join()
    Keep non-matches → anti_join()
  Just need every combination?
    cross_join()                              (Cartesian product)
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

## nest_join() — Joins Without Fan-out

```r
# Each x row keeps a list-column of its matching y rows
customers |> nest_join(orders, join_by(customer_id))
#> # A tibble: 3 x 3
#>   customer_id name      orders
#>         <int> <chr>     <list>
#> 1           1 Alice     <tibble [2 x 2]>
#> 2           2 Bob       <tibble [0 x 2]>
#> 3           3 Charlie   <tibble [5 x 2]>

# Pair with map() / unnest() for downstream work — see references/purrr-patterns.md
customers |>
  nest_join(orders, join_by(customer_id), name = "order_data") |>
  mutate(n_orders = map_int(order_data, nrow),
         total = map_dbl(order_data, \(o) sum(o$amount)))
```

**Identity:** `inner_join()` ≡ `nest_join() |> unnest()`;
`left_join()` ≡ `nest_join() |> unnest(keep_empty = TRUE)`.

Reach for `nest_join()` when you need to operate on the matched rows
*per-x-row* (count, summarise, fit a model) without first fanning out to
a wide table — preserves row count and is faster than `left_join() |>
nest()` for large `y`.

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

## multiple = — Pick Which Match to Keep

```r
# When one x row has many y matches, control what comes back:
trades |> left_join(quotes, join_by(ticker), multiple = "all")    # default-ish
trades |> left_join(quotes, join_by(ticker), multiple = "first")  # earliest
trades |> left_join(quotes, join_by(ticker), multiple = "last")   # latest
trades |> left_join(quotes, join_by(ticker), multiple = "any")    # any one match
```

**Values:** `"all"`, `"first"`, `"last"`, `"any"`. As of dplyr 1.1.1, only
true many-to-many joins warn — one-to-many is silent. Set `multiple = "all"`
explicitly when you *expect* fan-out: it documents intent and silences any
remaining warnings. For "first/last by a key", combine with sorted `y`.

---

## unmatched = — Fail on Orphans

```r
# Default drops y rows that didn't match — silent
orders |> inner_join(customers, join_by(customer_id))

# Error if any x row has no match in y
orders |> inner_join(customers, join_by(customer_id), unmatched = "error")

# inner_join can take a length-2 vector for x and y independently
orders |> inner_join(
  customers,
  join_by(customer_id),
  unmatched = c("error", "drop")    # error on x orphans, drop y orphans
)
```

**Values:** `"drop"` (default), `"error"`. Use with `inner_join()` and
`right_join()` when an unmatched key is a data quality bug, not just a
filter — fails loudly at join time.

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
| Renamed key column collapses into one | Pass `keep = TRUE` to retain both join columns in the output |
| Legacy `by = "id"` syntax mixed with `join_by()` | Pick one: `join_by()` is the modern form and supports inequality + helpers |
| `nest_join()` vs `left_join() |> nest()` | Prefer `nest_join()` — preserves x row count and skips an unnecessary fan-out |
| `closest()` doesn't translate to SQL via dbplyr | Pre-aggregate in the database, then `collect()` into R for the rolling join |
