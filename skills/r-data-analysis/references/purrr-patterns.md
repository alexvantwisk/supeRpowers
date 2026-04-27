# purrr Patterns

Functional programming for data wrangling: typed `map_*` variants, parallel
mapping, list-columns, error handling, and rectangling. All code uses `|>`
and `<-`.

---

## Typed `map_*` Variants

```r
# map_*() returns a typed atomic vector — fails fast on type mismatch
files <- list.files("data", pattern = "\\.csv$", full.names = TRUE)
sizes <- map_dbl(files, file.size)        # numeric vector
exists <- map_lgl(files, file.exists)     # logical vector
heads  <- map_chr(files, \(f) readLines(f, n = 1))

# map() returns a list — use when output type is heterogeneous
fits <- map(split(mtcars, mtcars$cyl), \(d) lm(mpg ~ wt, data = d))

# map_vec() — for typed output beyond the four atomic types (Date, factor, ...)
dates <- map_vec(strs, \(s) lubridate::ymd(s))
```

**Rule:** Prefer `map_*()` typed variants over `sapply()`. `sapply()` silently
returns a list on type mismatch; `map_dbl()` errors loudly. `map_vec()`
(purrr >= 1.0) extends the type-safety guarantee to dates, factors,
date-times, and other vctrs vector types.

---

## map2(), pmap() — Parallel Mapping

```r
# map2() — two parallel inputs, recycled to common length
weights <- c(0.1, 0.5, 0.4)
values  <- c(10, 20, 30)
map2_dbl(weights, values, \(w, v) w * v)

# pmap() — N parallel inputs from a list or data frame
params <- tibble(mean = c(0, 5, 10), sd = c(1, 2, 3), n = c(10, 20, 30))
samples <- pmap(params, \(mean, sd, n) rnorm(n, mean, sd))

# pmap with a tibble row-wise — each column becomes a named arg
pmap_dbl(params, \(mean, sd, n) mean + sd * sqrt(n))
```

---

## walk() — Side Effects Only

```r
# walk() returns input invisibly — for side effects (writing files, plotting)
plots <- map(unique(df$group), \(g) df |> filter(group == g) |> ggplot(...))
walk2(plots, unique(df$group), \(p, g) ggsave(paste0(g, ".png"), p))

# Common pattern: write a list of data frames to disk
results |> iwalk(\(d, name) write_csv(d, paste0(name, ".csv")))
```

`iwalk()` / `imap()` pass the list element AND its name (or index).

---

## list_rbind() / list_cbind() / list_c() — Combining Results

```r
# Stack many data frames — preferred over reduce(bind_rows)
files |> map(read_csv) |> list_rbind()
files |> map(read_csv) |> list_rbind(names_to = "file")  # tag each by source

# Bind a list of vectors into one
splits |> map(\(x) tibble(group = x, n = length(x))) |> list_rbind()

# Concatenate atomic vectors
1:3 |> map(\(i) i + 0:1) |> list_c()                    # 1 2 2 3 3 4
```

**Rule (purrr >= 1.0):** `map_dfr()` and `map_dfc()` are *superseded* —
the `_dfr`/`_dfc` suffixes implied a 1-to-1 type contract that the
functions never enforced. Replace with `map() |> list_rbind()` (uses
`vctrs::vec_rbind()` under the hood, no dplyr dependency).

---

## reduce() and accumulate()

```r
# reduce() — fold a list to a single value
filters |> reduce(\(d, f) f(d), .init = df)             # apply filter pipeline

# accumulate() — keep all intermediate steps
1:5 |> accumulate(`+`)                                  # 1 3 6 10 15
df_list |> accumulate(left_join, by = "id")            # progressive joins
```

Reach for `reduce()` when each step depends on the previous one; reach
for `list_rbind()` / `list_c()` when you just need to concatenate.

---

## List-columns: nest() + map() + broom

```r
# Per-group modeling without a for loop — returns one row per group
mtcars |>
  nest(.by = cyl) |>
  mutate(
    fit = map(data, \(d) lm(mpg ~ wt, data = d)),
    tidied = map(fit, broom::tidy),
    glanced = map(fit, broom::glance)
  ) |>
  unnest(tidied)
```

The list-column pattern keeps grouped models, predictions, and diagnostics
in one tidy frame. Hand off to `r-stats` for inference details.

---

## Error Handling: safely(), possibly(), quietly()

```r
# safely() — wrap a function; returns list(result, error)
safe_read <- safely(read_csv)
results <- map(files, safe_read)
oks <- results |> map("result") |> compact()
errs <- results |> map("error") |> compact()

# possibly() — return a default on error
read_or_null <- possibly(read_csv, otherwise = NULL)
files |> map(read_or_null) |> compact()

# quietly() — capture warnings/messages alongside the result
noisy <- quietly(\(x) { warning("whoops"); x * 2 })
out <- noisy(10)
out$result    # 20
out$warnings  # "whoops"
```

Wrap fragile operations (file I/O, network, parsers) with `safely()` or
`possibly()`; never let one bad input abort the whole pipeline.

---

## List Rectangling: hoist(), unnest_*()

```r
# Pull named fields out of a list-column (e.g. JSON) into top-level columns
api_data |>
  hoist(payload,
    user_id  = "user_id",
    score    = c("metrics", "score"),       # nested key
    tags     = list("tags", 1L)             # first element of tags list
  )

# Convert a list-column of vectors to long format
df |> unnest_longer(values)

# Convert a list-column of named lists/vectors to wide format
df |> unnest_wider(payload)
```

Read `references/tidyr-reshape.md` for the full rectangling decision tree.

---

## When to Prefer across() Over map()

```r
# across() — apply functions to columns within a single data frame
df |> mutate(across(where(is.numeric), \(x) (x - mean(x)) / sd(x)))

# map() — apply a function to elements of a list (or rows via list-columns)
list_of_dfs |> map(\(d) d |> filter(score > 0))
```

**Rule:** Inside one data frame, use `across()`. Across a list of objects
(data frames, models, files), use `map()`.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `sapply()` returns inconsistent types | Use `map_dbl()`/`map_chr()`/`map_lgl()` or `vapply()` |
| Anonymous function with `function(x)` is verbose | Use the lambda shortcut `\(x) ...` (R >= 4.1) |
| `map(df, fn)` iterates over columns, not rows | For row-wise, use `pmap()` or `nest() + map()` |
| Long `for` loop fitting models per group | Replace with `nest(.by =) |> mutate(fit = map(data, ...))` |
| `safely()` output is `list(result, error)` not flat | Use `transpose()` then `compact()` to split successes from errors |
| `reduce(.init =)` omitted on empty input | Always pass `.init` when input may be empty |
| Mixing `purrr::map` and `base::Map` | Stick with purrr — naming, NSE, and type guarantees are consistent |
| `map_dfr()` / `map_dfc()` superseded (purrr >= 1.0) | Use `map() |> list_rbind()` or `map() |> list_cbind()` |
| `imap()` over an unnamed list passes index, not name | Add names with `set_names()` first if you want named callbacks |
