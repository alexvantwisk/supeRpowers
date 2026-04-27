# tidyr Reshape and Rectangling

Pivots, unnesting, splitting, completing, filling. Core principle: each
variable a column, each observation a row, each value a cell. All code
uses `|>` and `<-`.

---

## pivot_longer() — Wide to Long

```r
# Basic — every non-id column becomes a row
sales_wide |>
  pivot_longer(cols = jan:dec, names_to = "month", values_to = "sales")

# Drop NA values in the resulting value column
df |> pivot_longer(starts_with("q_"), values_drop_na = TRUE)

# names_pattern — split a column name into multiple parts
df |>
  pivot_longer(
    cols = matches("^(rev|cost)_\\d{4}$"),
    names_to = c("metric", "year"),
    names_pattern = "(rev|cost)_(\\d{4})",
    names_transform = list(year = as.integer)
  )

# names_sep — simpler alternative for delimited names
df |>
  pivot_longer(
    cols = -id,
    names_to = c("metric", "year"),
    names_sep = "_"
  )
```

**Rule:** `names_sep` for fixed delimiters (`q_2024`); `names_pattern` for
regex (`rev_2024Q3`). When a single column encodes multiple variables, the
data is wide — pivot longer first.

---

## pivot_wider() — Long to Wide

```r
# Basic — names from one column, values from another
long |>
  pivot_wider(names_from = metric, values_from = value)

# Multiple value columns — names get a prefix
long |>
  pivot_wider(
    names_from = period,
    values_from = c(revenue, cost),
    names_glue = "{period}_{.value}"
  )

# Aggregate duplicates with values_fn
long |>
  pivot_wider(
    names_from = metric,
    values_from = value,
    values_fn = mean,            # collapse duplicates
    values_fill = 0              # fill missing combinations
  )
```

If `pivot_wider()` warns about list-columns, you have duplicated
`names_from` × id combinations — pass `values_fn` to aggregate them.

---

## Unnest: longer vs wider

```r
# Decision: list-column of vectors → longer; list-column of named records → wider

# unnest_longer() — one row per element
df <- tibble(id = 1:2, vals = list(c(10, 20), c(30, 40, 50)))
df |> unnest_longer(vals)

# unnest_wider() — one column per name in each element
df <- tibble(id = 1:2, info = list(list(name = "A", n = 10), list(name = "B", n = 20)))
df |> unnest_wider(info)

# unnest() — for tibble list-columns (e.g. nest() output)
df |> nest(.by = group) |> unnest(data)
```

---

## hoist() — Pull Specific Fields

```r
# Pull named fields out of a list-column (often JSON) into top-level columns
api_data |>
  hoist(payload,
    user_id  = "user_id",
    score    = c("metrics", "score"),     # nested key
    first_tag = list("tags", 1L)          # first element of "tags" list
  )
```

`hoist()` is the surgical alternative to `unnest_wider()` — pull only the
fields you want and leave the rest as a list-column for later.

---

## separate_wider_*() — Split a Column

```r
# Split by a delimiter
df |> separate_wider_delim(name, delim = " ",
                           names = c("first", "last"))

# Split by a regex with capture groups
df |> separate_wider_regex(
  code,
  patterns = c(year = "\\d{4}", "-", region = "[A-Z]{2}", "-", id = ".*")
)

# Split by fixed widths
df |> separate_wider_position(code, widths = c(year = 4, region = 2, id = 6))

# Handle parse failures gracefully
df |> separate_wider_delim(name, delim = " ",
                           names = c("first", "last"),
                           too_few = "align_start",
                           too_many = "merge")
```

`separate()` is deprecated. Use `separate_wider_*()` (one row → multiple
columns) or `separate_longer_*()` (one row → multiple rows).

---

## complete() and fill()

```r
# complete() — make implicit missing combinations explicit
sales |>
  complete(region, year, fill = list(revenue = 0))

# fill() — propagate the last non-NA value down (or up) within groups
df |>
  arrange(id, date) |>
  fill(category, .direction = "down", .by = id)

# expand() — get all combinations of a set of columns (useful before joining)
df |> expand(region, year)

# expand_grid() — Cartesian product of vectors
expand_grid(a = 1:3, b = c("x", "y"))
```

`complete()` for time-series with gaps; `fill()` for forward/backward NA
propagation; `expand_grid()` for setting up parameter grids.

---

## nest(.by =) and List-columns

```r
# nest() collapses each group into a tibble in a list-column
nested <- df |> nest(.by = group)

# Pair with map() for per-group operations (see references/purrr-patterns.md)
nested |>
  mutate(fit = map(data, \(d) lm(y ~ x, data = d)),
         tidied = map(fit, broom::tidy)) |>
  unnest(tidied)
```

Prefer `nest(.by =)` over the older `group_by() |> nest()` — clearer scope.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `gather()` / `spread()` (deprecated) | Use `pivot_longer()` / `pivot_wider()` |
| `pivot_wider()` produces list-columns | Pass `values_fn =` to aggregate duplicate combinations |
| Lost type info after `pivot_longer()` (numeric → character) | Use `names_transform` / `values_transform` to coerce |
| `separate()` (deprecated) silently drops/extends rows | Use `separate_wider_*()` with explicit `too_few`/`too_many` |
| `complete()` produces NAs you forgot to fill | Pass `fill = list(col = 0)` |
| Nested data frames are slow to print | `print(n = 10)` or `select()` away the list-column for inspection |
| `unnest()` collapses a list-column to scalar atomic | Use `unnest_longer()` for vectors, `unnest_wider()` for named records |
| `hoist()` mixed with `unnest_wider()` confusion | `hoist()` for surgical extraction, `unnest_wider()` for the full payload |
