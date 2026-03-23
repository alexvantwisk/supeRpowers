---
name: r-performance
description: >
  Use when optimizing R code for speed or memory. Provides a profile-first
  methodology covering bench, profvis, data.table, vectorization, Rcpp,
  parallel processing, memory management, and proof-of-improvement benchmarks.
  Triggers: performance, optimization, profiling, benchmarking, data.table,
  vectorization, Rcpp, parallel, memory, speed, slow code, large dataset.
  Do NOT use for general data wrangling at normal scale — use r-data-analysis instead.
  Do NOT use for debugging errors — use r-debugging instead.
---

# R Performance Optimization

Profile first. Optimize the measured bottleneck. Prove the improvement.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/profiling-workflow.md` for systematic profiling and flame-graph interpretation
- Read `references/data-table-translation.md` for complete dplyr ↔ data.table side-by-side syntax

---

## Decision Tree: When to Optimize What

```
Code is slow / using too much memory?
  └─ Profile first with profvis/bench
       └─ Bottleneck is I/O?          → fread/fwrite, vroom, chunked reading
       └─ Bottleneck is computation?
            └─ Loops / vectorizable?  → vectorize, purrr, vapply
            └─ Data manipulation?     → data.table (>1M rows)
            └─ Numerical inner loop?  → Rcpp
            └─ Independent tasks?     → parallel (furrr)
```

Never parallelize before profiling — overhead often exceeds gains.

---

## Profiling & Benchmarking

```r
library(profvis)
library(bench)

# Visual flame graph (BEST for finding hot spots)
profvis::profvis({
  your_code_here()
})

# Microbenchmarking — always check = TRUE to validate equivalence
bench::mark(
  approach_a = dplyr_version(df),
  approach_b = dt_version(dt),
  check = TRUE,
  iterations = 100
)

# Parameter grid benchmarks
bench::press(
  rows = c(1e4, 1e5, 1e6),
  {
    dt <- data.table::as.data.table(generate_data(rows))
    bench::mark(dt[, .(mean_v = mean(value)), by = group])
  }
)

# Quick check (one-off)
system.time(slow_function(df))
```

Read `references/profiling-workflow.md` for the full 5-step workflow.

---

## data.table

Use when: dataset >1M rows, memory-constrained, or performance-critical loops.

```r
library(data.table)

dt <- data.table::fread("large.csv")        # fast I/O
data.table::fwrite(dt, "output.csv")        # fast write

# Syntax: dt[i, j, by]
dt[value > 0, .(mean_v = mean(value), n = .N), by = .(group, year)]

# Reference semantics — modify in place (no copy)
dt[, new_col := value * 2]                  # := adds/modifies column
dt[, c("a", "b") := NULL]                  # remove columns
data.table::setnames(dt, "old", "new")      # rename in place
data.table::setDT(existing_df)             # convert df to DT in place

# Keys for fast subsetting / joining
data.table::setkey(dt, id, date)
dt["id_001"]                               # fast key lookup

# Chaining
dt[value > 0][order(-value)][, head(.SD, 3), by = group]
```

Read `references/data-table-translation.md` for dplyr ↔ data.table translation.

---

## Vectorization

```r
# AVOID: growing vector in loop
result <- c()
for (x in items) result <- c(result, transform(x))  # O(n²) copies

# CORRECT: pre-allocate
result <- vector("numeric", length(items))
for (i in seq_along(items)) result[[i]] <- transform(items[[i]])

# BETTER: vectorized
result <- transform(items)          # if transform is vectorized
result <- vapply(items, f, numeric(1))  # vapply > sapply (type-safe)

# Tidyverse style
library(purrr)
results <- purrr::map_dbl(items, transform)    # returns numeric vector
results <- purrr::map_dfr(items, build_row)    # returns data frame

# Column-wise with across
df |> mutate(across(where(is.numeric), \(x) x / max(x, na.rm = TRUE)))

# Cumulative operations (no loop needed)
df |> mutate(running_total = cumsum(value), rolling_max = cummax(value))
```

---

## Memory Management

```r
library(lobstr)

lobstr::obj_size(large_df)           # actual memory footprint
tracemem(df)                         # track copies

# Avoid unnecessary copies — data.table reference semantics
data.table::setDT(df)                # in-place, no copy
dt[, col := value]                   # in-place column add

# Lazy / chunked reading for files larger than RAM
library(vroom)
df <- vroom::vroom("huge.csv",       # lazy column reads
  col_select = c(id, date, value))

library(readr)
readr::read_csv_chunked("huge.csv",
  callback = DataFrameCallback$new(\(chunk, pos) process(chunk)),
  chunk_size = 50000
)
```

R uses copy-on-modify: any modification of a shared object triggers a full copy.
Use `data.table::setDT()` and `:=` to work in-place and avoid copies.

---

## Rcpp

Use when: tight numerical loops, simulation inner loops, custom algorithms.

```r
# Inline (prototyping)
Rcpp::cppFunction("
  NumericVector cumsum_capped(NumericVector x, double cap) {
    int n = x.size();
    NumericVector out(n);
    double running = 0;
    for (int i = 0; i < n; i++) {
      running = std::min(running + x[i], cap);
      out[i] = running;
    }
    return out;
  }
")

# From file (production)
Rcpp::sourceCpp("src/my_algo.cpp")   # exports functions automatically

# Package integration
usethis::use_rcpp()                  # adds LinkingTo, creates src/
```

Rcpp sugar (`sum()`, `mean()`, `pow()`, `ifelse()`) lets you write C++-speed
code with R-like syntax. Use `NumericVector`, `IntegerVector`, `LogicalVector`.

---

## Parallel Processing

```r
library(furrr)
library(future)

# Tidyverse-aligned parallel (PREFERRED)
future::plan(future::multisession, workers = 4)

results <- furrr::future_map(items, slow_fn)
results_df <- furrr::future_map_dfr(items, build_row)
totals <- furrr::future_map_dbl(items, compute_total)

future::plan(future::sequential)    # restore sequential

# Classic approach
library(foreach); library(doParallel)
cl <- parallel::makeCluster(4)
doParallel::registerDoParallel(cl)
result <- foreach::foreach(x = items, .combine = rbind) %dopar% slow_fn(x)
parallel::stopCluster(cl)
```

**When NOT to parallelize:** task takes <100ms, data transfer overhead dominates,
or memory per worker exceeds available RAM.

---

## Common Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| `result <- c(result, x)` in loop | O(n²) copies | Pre-allocate or use `purrr::map` |
| `df <- rbind(df, row)` in loop | O(n²) copies | Collect list, then `bind_rows()` |
| `apply()` on data frame columns | Coerces to matrix | `dplyr::across()` or `vapply()` |
| `paste()` in tight loop | Slow for 1M+ items | `stringr::str_c()` vectorized |
| `df$col <- ...` on large shared df | Triggers full copy | `data.table::setDT()` + `:=` |
| `sapply()` over `vapply()` | Unpredictable return type | `vapply(x, f, FUN.VALUE = numeric(1))` |

---

## Example Prompts

1. "This dplyr pipeline is too slow on 5M rows — convert to data.table"
2. "Profile why my Shiny app takes 8 seconds to load"
3. "Benchmark three approaches to computing rolling averages"
4. "Parallelize this `purrr::map()` call that processes 500 files"
5. "Rewrite this simulation inner loop in Rcpp"
