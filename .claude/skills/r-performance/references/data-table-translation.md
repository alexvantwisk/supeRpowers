# dplyr ↔ data.table Translation

Complete side-by-side reference. Use data.table when: >1M rows, memory-constrained,
or performance-critical. Use dplyr for readability, NSE, and tidyverse integration.

---

## Setup

```r
# dplyr
library(dplyr)
df <- tibble::tibble(...)

# data.table
library(data.table)
dt <- data.table::as.data.table(df)   # copy
data.table::setDT(df)                 # in-place (no copy)
```

---

## Core Verb Translation

| Operation | dplyr | data.table |
|---|---|---|
| **filter rows** | `filter(df, x > 0)` | `dt[x > 0]` |
| **select columns** | `select(df, a, b, c)` | `dt[, .(a, b, c)]` |
| **drop columns** | `select(df, -a)` | `dt[, a := NULL]` |
| **rename** | `rename(df, new = old)` | `setnames(dt, "old", "new")` |
| **add column** | `mutate(df, z = x + y)` | `dt[, z := x + y]` |
| **add multiple** | `mutate(df, a=x+1, b=y*2)` | `dt[, ':='(a=x+1, b=y*2)]` |
| **sort** | `arrange(df, desc(x))` | `dt[order(-x)]` |
| **sort in place** | *(not supported)* | `setorder(dt, -x)` |
| **distinct rows** | `distinct(df)` | `unique(dt)` |
| **first N rows** | `slice_head(df, n=5)` | `dt[1:5]` |
| **sample N rows** | `slice_sample(df, n=100)` | `dt[sample(.N, 100)]` |
| **top N per group** | `slice_max(df, x, n=3, by=g)` | `dt[order(-x), head(.SD, 3), by=g]` |
| **count rows** | `count(df, group)` | `dt[, .N, by=group]` |
| **row count** | `nrow(df)` | `dt[, .N]` |

---

## Summarise / Aggregate

```r
# dplyr
df |>
  summarise(
    mean_val = mean(value, na.rm = TRUE),
    n = n(),
    .by = c(group, year)
  )

# data.table
dt[, .(mean_val = mean(value, na.rm = TRUE), n = .N), by = .(group, year)]

# keyby = by + auto-sort result
dt[, .(mean_val = mean(value, na.rm = TRUE)), keyby = .(group, year)]
```

---

## Multiple Columns (across equivalent)

```r
# dplyr
df |> summarise(across(where(is.numeric), mean, na.rm = TRUE), .by = group)

# data.table — .SD = Subset of Data, .SDcols filters columns
dt[, lapply(.SD, mean, na.rm = TRUE), by = group, .SDcols = is.numeric]

# Mutate across numeric columns
df |> mutate(across(c(a, b, c), \(x) x / max(x, na.rm = TRUE)))
dt[, (c("a","b","c")) := lapply(.SD, \(x) x / max(x, na.rm=TRUE)),
   .SDcols = c("a","b","c")]
```

---

## Joins

| Join type | dplyr | data.table |
|---|---|---|
| **left join** | `left_join(x, y, join_by(id))` | `y[x, on="id"]` |
| **inner join** | `inner_join(x, y, join_by(id))` | `x[y, on="id", nomatch=NULL]` |
| **right join** | `right_join(x, y, join_by(id))` | `x[y, on="id"]` |
| **anti join** | `anti_join(x, y, join_by(id))` | `x[!y, on="id"]` |
| **multi-key** | `inner_join(x, y, join_by(a, b))` | `x[y, on=.(a, b), nomatch=NULL]` |
| **non-equi** | `inner_join(x, y, join_by(a >= lo, a <= hi))` | `x[y, on=.(a>=lo, a<=hi)]` |

```r
# data.table join best practice: set key for repeated joins
setkey(orders, customer_id)
setkey(customers, customer_id)
orders[customers, nomatch = NULL]    # inner join, fast binary search
```

`nomatch = NULL` = inner join (keep only matching rows).
`nomatch = NA` (default) = left join (keep all left-side rows).

---

## Pivot / Reshape

| Operation | tidyr | data.table |
|---|---|---|
| **wide → long** | `pivot_longer(df, cols=a:c, names_to="k", values_to="v")` | `melt(dt, measure.vars=c("a","b","c"), variable.name="k", value.name="v")` |
| **long → wide** | `pivot_wider(df, names_from=k, values_from=v)` | `dcast(dt, ... ~ k, value.var="v")` |
| **long → wide + agg** | `pivot_wider(..., values_fn=sum)` | `dcast(dt, ... ~ k, value.var="v", fun.aggregate=sum)` |

```r
# data.table melt with multiple value columns
melt(dt,
  id.vars     = c("id", "date"),
  measure.vars = list(c("a_2022","a_2023"), c("b_2022","b_2023")),
  variable.name = "year",
  value.name    = c("a", "b")
)
```

---

## Window Functions

```r
# dplyr
df |>
  arrange(group, date) |>
  mutate(
    row_n    = row_number(),
    running  = cumsum(value),
    lag_v    = lag(value),
    rank_v   = rank(desc(value)),
    .by = group
  )

# data.table
dt[order(date),
   `:=`(
     row_n   = seq_len(.N),
     running = cumsum(value),
     lag_v   = shift(value, 1L),
     rank_v  = frank(-value)
   ),
   by = group]
```

`shift(x, n)` = lag; `shift(x, -n)` = lead. `frank()` is data.table's fast rank.

---

## Chaining

```r
# dplyr — native pipe works
df |>
  filter(value > 0) |>
  mutate(z = value * 2) |>
  summarise(mean_z = mean(z), .by = group)

# data.table — bracket chaining
dt[value > 0
   ][, z := value * 2
     ][, .(mean_z = mean(z)), by = group]
```

---

## Keys and Indices

```r
# Primary key — binary search, auto-sorts rows
setkey(dt, id)
dt["A001"]                      # instant O(log n) lookup

# Secondary index — no sort, stores index separately
setindex(dt, category)
dt[category == "electronics"]   # uses index automatically

# Composite key
setkey(dt, customer_id, date)
dt[.("C01", "2024-01-01")]
```

Keys give 10-100x speedup for repeated subsetting/joining on keyed columns.

---

## When Each Wins

### data.table wins when:
- Dataset >1M rows (lower memory, faster operations)
- File I/O (`fread`/`fwrite` are 3-10x faster than readr)
- Reference semantics needed (`:=` avoids copies)
- Repeated subsetting/joining (keys give binary search)
- Rolling joins and non-equi joins at scale

### dplyr wins when:
- Readability and maintainability are priorities
- Team is more familiar with tidyverse
- NSE (non-standard evaluation) needed in function interfaces (`{{ }}`)
- Integration with other tidyverse packages (ggplot2, tidyr, etc.)
- Datasets under 1M rows (performance difference is negligible)

---

## Hybrid Approach: dtplyr

`dtplyr` translates dplyr code to data.table automatically:

```r
library(dtplyr)
library(dplyr)
library(data.table)

# Wrap dt in lazy_dt() — all dplyr verbs work, data.table runs under the hood
result <- dt |>
  lazy_dt() |>
  filter(value > 0) |>
  mutate(z = value * 2) |>
  summarise(mean_z = mean(z), .by = group) |>
  as_tibble()   # materialise

# See the generated data.table code
show_query(
  lazy_dt(dt) |>
    filter(value > 0) |>
    summarise(n = n(), .by = group)
)
```

dtplyr is a good bridge when you want data.table speed but prefer writing dplyr
syntax. Not all dplyr operations are translatable — `show_query()` reveals what
actually runs, and untranslatable steps fall back to dplyr.
