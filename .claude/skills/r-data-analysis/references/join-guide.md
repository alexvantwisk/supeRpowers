# Join Guide

Loaded lazily from the r-data-analysis skill. Covers join_by() syntax,
join type selection, filtering joins, and common join patterns.

---

## join_by() Syntax

All dplyr joins accept `join_by()` for specifying join conditions.

### Equality Joins

```r
# Single key (same column name in both tables)
left_join(orders, customers, join_by(customer_id))

# Different column names
left_join(orders, customers, join_by(cust_id == customer_id))

# Multiple keys
left_join(sales, targets, join_by(region, year, quarter))

# Mixed names
left_join(a, b, join_by(id == b_id, year))
```

### Inequality Joins

`join_by()` supports `>=`, `<=`, `>`, `<` for range-based matching.

```r
# Events within a time window
events |>
  left_join(
    sessions,
    join_by(user_id, event_time >= session_start, event_time <= session_end)
  )

# Price lookup by date range (effective pricing)
orders |>
  left_join(
    price_history,
    join_by(product_id, order_date >= effective_from, order_date < effective_to)
  )
```

### Helpers: closest(), between(), within(), overlaps()

```r
# Closest match (nearest preceding date)
events |>
  left_join(snapshots, join_by(id, closest(event_date >= snapshot_date)))

# Between (shorthand for >= lower, <= upper)
df |>
  left_join(ranges, join_by(id, between(value, lower, upper)))

# Overlaps (two intervals that share any time)
meetings_a |>
  inner_join(meetings_b, join_by(room, overlaps(start_a, end_a, start_b, end_b)))
```

---

## Join Type Decision Tree

```
Do you need ALL rows from the left table?
  YES -> left_join()
    Do you also need unmatched rows from the right?
      YES -> full_join()
      NO  -> left_join() (most common choice)
  NO  -> Do both sides MUST match?
    YES -> inner_join()
    NO  -> Do you just need to FILTER, not add columns?
      YES -> semi_join() (keep matches) or anti_join() (keep non-matches)
      NO  -> Do you need every combination?
        YES -> cross_join()
```

### Quick Reference

| Join Type | Left Unmatched | Right Unmatched | Columns Added | Use When |
|-----------|---------------|-----------------|---------------|----------|
| `left_join()` | Kept (NA-filled) | Dropped | Yes | Default — preserve all primary records |
| `inner_join()` | Dropped | Dropped | Yes | Only want complete matches |
| `right_join()` | Dropped | Kept (NA-filled) | Yes | Rare — usually rewrite as left_join() |
| `full_join()` | Kept (NA-filled) | Kept (NA-filled) | Yes | Merge two datasets, keep everything |
| `semi_join()` | Only matches kept | N/A | No | Filter left by existence in right |
| `anti_join()` | Only non-matches kept | N/A | No | Find orphans / missing records |
| `cross_join()` | All | All | Yes (cartesian) | Generate all combinations |

---

## Filtering Joins: semi_join() and anti_join()

Filtering joins never add columns — they only keep or remove rows from
the left table based on whether a match exists in the right table.

### semi_join — Keep Matches

```r
# Customers who have placed at least one order
active_customers <- customers |>
  semi_join(orders, join_by(customer_id))

# Products sold in Q4
q4_products <- products |>
  semi_join(
    sales |> filter(quarter == 4),
    join_by(product_id)
  )
```

### anti_join — Keep Non-Matches

```r
# Customers who never ordered
inactive_customers <- customers |>
  anti_join(orders, join_by(customer_id))

# Find orphaned records (orders referencing missing customers)
orphan_orders <- orders |>
  anti_join(customers, join_by(customer_id))

# Data quality check — which expected keys are missing?
expected_keys <- tibble(region = c("North", "South", "East", "West"))
missing_regions <- expected_keys |>
  anti_join(sales, join_by(region))
```

---

## cross_join() for Cartesian Products

Generates every combination. Use sparingly — output size = nrow(a) * nrow(b).

```r
# Generate all region-product combinations for a report scaffold
scaffold <- regions |>
  cross_join(products) |>
  left_join(actual_sales, join_by(region, product)) |>
  replace_na(list(total_sales = 0))

# All pairs for comparison
cross_join(items, items, suffix = c("_a", "_b")) |>
  filter(id_a < id_b)  # Remove self-pairs and duplicates
```

---

## Multiple Join Keys

```r
# Composite key
result <- sales |>
  left_join(budget, join_by(region, department, fiscal_year))
```

### Column Name Conflicts

When both tables have columns with the same name (besides the join key),
dplyr adds suffixes. Control this with the `suffix` argument.

```r
# Default: .x and .y
combined <- df_a |> left_join(df_b, join_by(id))
# Produces: name.x, name.y

# Custom suffixes
combined <- df_a |>
  left_join(df_b, join_by(id), suffix = c("_current", "_previous"))
# Produces: name_current, name_previous
```

### Handling Duplicates

Joins can multiply rows if the right table has multiple matches per key.
Guard against this:

```r
# Check for duplicate keys before joining
targets |> count(region, year) |> filter(n > 1)

# Use relationship argument to catch unexpected duplicates
orders |>
  left_join(customers, join_by(customer_id), relationship = "many-to-one")
# Errors if a customer_id appears multiple times in customers
```

`relationship` options: `"one-to-one"`, `"one-to-many"`, `"many-to-one"`,
`"many-to-many"`.

---

## Common Join Patterns

### Lookup Tables

```r
# Map codes to labels
sales |>
  left_join(region_names, join_by(region_code)) |>
  left_join(product_categories, join_by(product_id))
```

### Time-Stamped Data Merging

```r
# Merge daily metrics with monthly targets
daily_sales |>
  mutate(month = floor_date(date, "month")) |>
  left_join(monthly_targets, join_by(region, month))
```

### As-Of Join (Most Recent Lookup)

```r
# Find the most recent price for each order
orders |>
  left_join(
    price_history,
    join_by(product_id, closest(order_date >= price_date))
  )
```

### Self-Join for Comparisons

```r
# Compare each employee to their manager
employees |>
  left_join(
    employees |> select(emp_id, manager_name = name, manager_salary = salary),
    join_by(manager_id == emp_id)
  )
```

### Cascading Joins (Multiple Lookups)

```r
enriched_orders <- orders |>
  left_join(customers, join_by(customer_id)) |>
  left_join(products, join_by(product_id)) |>
  left_join(shipping_zones, join_by(zip_code)) |>
  select(order_id, customer_name, product_name, zone, total)
```

**Tip:** After cascading joins, check row counts — unexpected many-to-many
relationships silently multiply rows. Use `relationship = "many-to-one"`
on each join to catch this.

### Validating Join Results

```r
# Before/after row count check
nrow_before <- nrow(orders)
result <- orders |> left_join(customers, join_by(customer_id))
stopifnot(nrow(result) == nrow_before)  # left_join should not add rows

# Check for introduced NAs (unmatched keys)
result |>
  filter(is.na(customer_name)) |>
  distinct(customer_id)
```
