# Profiling Workflow

Systematic 5-step process for finding and fixing R performance bottlenecks.

---

## Step 1: Establish Baseline

Always measure before changing anything. Use `bench::mark()` with `check = TRUE`
to capture timing and memory together.

```r
library(bench)

baseline <- bench::mark(
  current_approach(df),
  check = FALSE,   # set TRUE when comparing equivalent implementations
  iterations = 10,
  memory = TRUE
)
print(baseline)
# Shows: min, median, max, mem_alloc, n_gc (garbage collections)
```

A high `n_gc` count indicates excessive memory allocation — a key signal.

---

## Step 2: Profile with profvis

`profvis::profvis()` produces an interactive flame graph in the RStudio Viewer
or browser. Run it around the code block you measured in Step 1.

```r
library(profvis)

profvis::profvis({
  result <- current_approach(df)
})
```

**Reading the flame graph:**

- **Width** = time spent (wider = slower)
- **Height** = call stack depth
- **Hot spots** = wide blocks near the bottom of the stack
- **Memory tab** = allocation timeline (spikes = many small allocs)

**What to look for:**
- `[gc]` blocks — garbage collection triggered by excessive allocation
- `Reduce` / `do.call` / `rbind` calls you didn't write directly
- Deep `tryCatch` or S4 dispatch overhead
- String operations (`paste`, `gsub`) inside loops

---

## Step 3: Identify Bottleneck Category

| Symptom | Category | Next action |
|---|---|---|
| Wide `fread`/`read_csv` block | **I/O** | Switch to `fread`, `vroom`, or chunked reads |
| Wide arithmetic / `for` block | **Computation** | Vectorize or Rcpp |
| Frequent `[gc]` blocks | **Allocation** | Pre-allocate, use `:=` in data.table |
| Wide `merge`/`join` block | **Join** | Set keys (`setkey`), use data.table join |
| Deep dispatch stack | **S4 / R5 overhead** | Consider S3 or plain functions |
| Wide `apply` on data frame | **Coercion** | Replace with `dplyr::across()` |

---

## Step 4: Apply Targeted Optimization

### I/O bottlenecks

```r
# Slow
df <- read.csv("data.csv")

# Fast
library(data.table)
dt <- data.table::fread("data.csv")   # often 5-10x faster

# Lazy column reads (only read columns you need)
library(vroom)
df <- vroom::vroom("data.csv", col_select = c(id, date, value))

# Larger-than-RAM: chunked
library(readr)
readr::read_csv_chunked(
  "huge.csv",
  callback = DataFrameCallback$new(\(chunk, pos) {
    chunk |>
      dplyr::filter(value > 0) |>
      dplyr::summarise(n = dplyr::n(), .by = group)
  }),
  chunk_size = 100000
)
```

### Computation bottlenecks (loops)

```r
# BEFORE: loop with rbind — O(n²)
result <- data.frame()
for (file in files) {
  result <- rbind(result, read_and_process(file))
}

# AFTER: collect then bind — O(n)
results_list <- vector("list", length(files))
for (i in seq_along(files)) {
  results_list[[i]] <- read_and_process(files[[i]])
}
result <- dplyr::bind_rows(results_list)

# BEST: purrr
result <- purrr::map(files, read_and_process) |> dplyr::bind_rows()
```

### Allocation bottlenecks

```r
# BEFORE: copy-on-modify triggers per column
df$col_a <- df$col_a * 2
df$col_b <- df$col_b + 1

# AFTER: data.table in-place
library(data.table)
data.table::setDT(df)
df[, `:=`(col_a = col_a * 2, col_b = col_b + 1)]
```

### Numerical inner loop → Rcpp

```r
# BEFORE: R loop (slow for n > 1e5)
rolling_capped <- function(x, cap) {
  out <- numeric(length(x))
  running <- 0
  for (i in seq_along(x)) {
    running <- min(running + x[[i]], cap)
    out[[i]] <- running
  }
  out
}

# AFTER: Rcpp
Rcpp::cppFunction("
  NumericVector rolling_capped(NumericVector x, double cap) {
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
```

---

## Step 5: Re-benchmark to Verify Improvement

Run `bench::mark()` comparing old and new, with `relative = TRUE` to see
the speedup ratio at a glance.

```r
bench::mark(
  old = rolling_capped_r(x, cap = 100),
  new = rolling_capped(x, cap = 100),   # Rcpp version
  check = TRUE,
  relative = TRUE
)
# relative = TRUE shows speedup factor in median column
```

Target: the new approach is the clear winner on both time and `mem_alloc`.

---

## Memory Profiling

```r
library(profmem)

# Detailed allocation log
mem_log <- profmem::profmem({
  result <- build_large_result(df)
})
print(mem_log)          # shows each allocation with size and call site
total_alloc <- sum(mem_log$bytes, na.rm = TRUE)

# Or via bench (simpler)
bench::mark(
  build_large_result(df),
  memory = TRUE
)

# Object sizes
library(lobstr)
lobstr::obj_size(df)              # actual size (shared refs counted once)
lobstr::obj_sizes(df, df2)        # sizes + shared memory between objects
tracemem(df)                      # print message every time df is copied
```

**Memory optimization checklist:**
- `lobstr::obj_size()` shows actual footprint (unlike `object.size()`)
- High `mem_alloc` in `bench::mark()` → look for `c()` / `rbind()` in loops
- Many `[gc]` → excessive small allocations; pre-allocate lists
- `tracemem()` reveals unexpected copies (stop with `untracemem()`)

---

## Profiling Shiny Apps

Wrap `server` logic or reactive expressions with `profvis`:

```r
library(shiny)
library(profvis)

# Option 1: profile a single reactive calculation
profvis::profvis({
  shiny::isolate({
    compute_heavy_reactive(input_val = "test")
  })
})

# Option 2: use profvis Shiny wrapper (captures full session)
profvis::profvis({
  shiny::runApp("myapp", test.mode = TRUE)
})
```

Common Shiny bottlenecks: `renderTable()` on large data (use `DT::renderDT()`),
re-running expensive queries on every input change (use `reactive()` caching or
`bindCache()`), and loading large datasets on every session start (load at global
scope or use `shiny::reactiveFileReader()`).
