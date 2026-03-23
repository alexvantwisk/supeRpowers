# Debugging Tools Reference

Detailed command reference for R's interactive debugging tools, common gotcha
patterns, and performance debugging techniques.

---

## Interactive Breakpoints

### debug() / debugonce()

```r
# Debug every call to a function
debug(my_function)
my_function(data)
undebug(my_function)

# Debug only the next call
debugonce(my_function)
```

### trace() — Inject browser at a Specific Line

```r
# Insert browser at a specific line inside a function
trace(my_function, tracer = browser, at = 4)
untrace(my_function)
```

Use `as.list(body(my_function))` to find the line numbers for the `at` argument.

### Automatic Recovery on Error

```r
# Drop into browser on ANY error (great for interactive exploration)
options(error = recover)

# Reset to default behavior
options(error = NULL)
```

With `recover`, R presents a numbered list of frames after an error. Select a
frame number to inspect its environment. This is especially powerful for errors
deep inside nested function calls.

### Package Code Debugging

For debugging inside a package under development:

```r
devtools::load_all()
debugonce(pkg::internal_function)
# Or set options(error = recover) then trigger the bug
```

Key points for package debugging:
- `devtools::load_all()` loads the package into the session so breakpoints work
- Use `pkg::internal_function` (not `:::`) to access non-exported functions after `load_all()`
- `options(error = recover)` is often the fastest path when you don't know which function fails

### browser() Commands

| Command | Action |
|---------|--------|
| `n` | Execute next line (step over) |
| `s` | Step into the next function call |
| `c` | Continue execution (run to next breakpoint or end) |
| `Q` | Quit the browser and return to top-level |
| `f` | Finish execution of current loop or function |
| `ls()` | List objects in current environment |
| `str(obj)` | Inspect structure of an object |
| `where` | Print the call stack |

---

## Gotchas — Full Reference

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `as.numeric(factor_var)` | Returns internal codes (1, 2, 3), not actual values | Use `as.numeric(as.character(x))` or `readr::parse_number()` |
| NSE scoping: bare string var in `filter()` | `filter(col > 20)` looks for column named `col`, not the variable's value | Use `.data[[col]]` for strings, `{{ var }}` for function arguments |
| Silent vector recycling | R recycles shorter vectors with no error, producing wrong results | Guard with `stopifnot(length(x) == length(y))` |
| Copy-on-modify memory spikes | Modifying one column copies the entire data frame | Build data frames in one step, or use `data.table` for in-place mutation |
| `list$missing_element` returns `NULL` | No error on missing list element; `NULL` propagates silently | Use `[["key"]]` with explicit `is.null()` check |
| `0.1 + 0.2 == 0.3` is `FALSE` | Floating point representation; equality check fails | Use `dplyr::near()` or `all.equal()` with tolerance |
| Encoding issues on Windows | Garbled text, unexpected `nchar()` values | Diagnose with `Encoding(x)`; fix with `enc2utf8()` or explicit locale in `read_csv()` |
| Scope creep | Claude refactors surrounding code when asked to fix one bug | Fix only the identified bug; show minimal diff |

### Additional Gotcha Details

**Factor-to-numeric conversion** is the #1 silent-bug source in R. If your data
was read from CSV and a column was parsed as a factor, `as.numeric()` gives the
internal integer codes. Always use `as.numeric(as.character(x))` or, better yet,
ensure correct parsing at read time with `readr::read_csv(col_types = ...)`.

**NSE scoping** in tidyverse functions catches everyone. The rule:
- Column names inside `filter()`, `mutate()`, `select()` are bare (unquoted)
- Variables holding column names as strings: use `.data[[var]]`
- Function arguments forwarding column names: use `{{ var }}` (embrace)

**Vector recycling** is a feature, not a bug — but it silently produces wrong
results when you compare vectors of different lengths. The classic example:
`x == c("A", "B")` does element-wise recycling, not set membership. Always use
`%in%` for multi-value checks.

---

## Performance Debugging

When the bug is "it's too slow" or "it uses too much memory."

### Quick Timing

```r
system.time({ result <- slow_function(data) })
```

### Benchmarking Alternatives

```r
bench::mark(
  base = vapply(x, f, numeric(1)),
  purrr = map_dbl(x, f)
)
```

`bench::mark()` automatically checks that results are identical and reports
memory allocations alongside timing.

### Profiling with profvis

```r
profvis::profvis({ slow_function(data) })
```

Opens an interactive flame graph in the browser. Look for:
- Wide bars (functions consuming the most time)
- Repeated thin bars (functions called too many times)
- Memory allocation spikes (copy-on-modify issues)

### Memory Inspection

```r
lobstr::obj_size(large_object)
lobstr::obj_sizes(obj1, obj2, obj3)  # Compare multiple objects
```

### Common Performance Fixes

| Problem | Fix |
|---------|-----|
| Loop over rows | Vectorize with `dplyr::mutate()` or base `vapply()` |
| `sapply()` returns unexpected type | Use `vapply()` with explicit return type |
| Growing a vector in a loop | Pre-allocate: `result <- vector("numeric", n)` |
| Large data frame operations | Switch to `data.table` or `collapse` for >1M rows |
| Repeated subsetting of same data | Compute once, store in variable |
| String concatenation in loop | Collect in list, `paste0(collapse=)` once |
