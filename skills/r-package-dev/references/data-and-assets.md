# Data and Assets in R Packages

Where to put data, how to access it, and how to keep CRAN happy.

**Sources:**
- R Packages 2e ch. 7 "Data" — <https://r-pkgs.org/data.html>
- Writing R Extensions §1.1.6 "Data in packages" — <https://cran.r-project.org/doc/manuals/r-release/R-exts.html#Data-in-packages>
- usethis::use_data — <https://usethis.r-lib.org/reference/use_data.html>

---

## The Three Data Locations

| Location | Use for | Access via |
|---|---|---|
| `data/*.rda` | R objects users can load with `data()` | `data(name)` |
| `R/sysdata.rda` | R objects internal to your package | direct symbol |
| `inst/extdata/` | Raw files (CSV, JSON, images, parquet, etc.) | `system.file()` |

Plus `data-raw/`: scripts that produce the artifacts above. Not shipped.

---

## `data/` — Exported R Datasets

Lazy-loaded R objects available via `data()`. Each `.rda` file holds one
named object with the same name as the file.

Create with `usethis::use_data()`:

```r
my_dataset <- tibble::tibble(x = 1:10, y = letters[1:10])
usethis::use_data(my_dataset)
# writes data/my_dataset.rda
```

Document in `R/data.R`:

```r
#' Sample dataset for demonstrating x and y
#'
#' @format A tibble with 10 rows and 2 columns:
#' \describe{
#'   \item{x}{Integer values 1-10.}
#'   \item{y}{Lowercase letters a-j.}
#' }
#' @source Generated with `data-raw/my_dataset.R` from `mtcars`.
"my_dataset"
```

Access (user-facing):

```r
data(my_dataset, package = "mypkg")
mypkg::my_dataset       # also works thanks to LazyData: true
```

DESCRIPTION must include:

```dcf
LazyData: true
```

## `R/sysdata.rda` — Internal Data

Use for lookup tables, pre-computed constants, etc. that your package code
needs but should not expose to users.

```r
internal_lookup <- c("a" = 1L, "b" = 2L, "c" = 3L)
usethis::use_data(internal_lookup, internal = TRUE)
# writes R/sysdata.rda
```

Access from package code with the bare symbol:

```r
my_function <- function(key) {
  internal_lookup[[key]]
}
```

## `inst/extdata/` — Raw Files

Use for non-R files: CSV, JSON, parquet, images, fixtures, schemas.
Files in `inst/<x>/` end up at `system.file("<x>/", package = "mypkg")`
in the installed package.

```bash
mkdir -p inst/extdata
cp config_schema.json inst/extdata/
```

Access:

```r
schema_path <- system.file("extdata", "config_schema.json", package = "mypkg")
fs::path_package("mypkg", "extdata", "config_schema.json")  # equivalent
```

For test fixtures, prefer `tests/testthat/fixtures/` (loaded via
`testthat::test_path()`) — those don't ship in the installed package.

---

## `data-raw/` — Reproducible Data Prep

Scripts that produce `data/*.rda` and `R/sysdata.rda`. Not shipped to users.

```r
usethis::use_data_raw("my_dataset")
# creates data-raw/my_dataset.R + .Rbuildignore entry
```

Each script ends with `usethis::use_data(name, overwrite = TRUE)`. Re-run
when the source changes; commit both the script and the regenerated `.rda`.

`.Rbuildignore` must contain `^data-raw$` (added by `use_data_raw()`).

---

## CRAN Size Limits

| Limit | Source |
|---|---|
| Total package size | 5 MB (CRAN policy) |
| Single file in `inst/extdata` | unbounded but counts toward 5 MB |
| `data/*.rda` lazy-load | counts toward 5 MB |

Diagnose:

```r
tools::checkRdaFiles("data/")
```

Output shows compression and size for each `.rda`. Fix oversized files:

```r
usethis::use_data(big_dataset, overwrite = TRUE, compress = "xz")
# Try compress = "xz", "bzip2", "gzip" and pick the smallest.
```

If still too large, host data in a separate "data package" (e.g.,
`mypkgdata`) on a drat repo or use `pins`/`piggyback` for >5 MB files.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Editing `.rda` directly in `data/` | Edit `data-raw/*.R` and rerun `use_data()` |
| Using `read.csv()` on `inst/extdata` at package load | Use `system.file()` lazily inside functions |
| Committing intermediate files in `data-raw/` | Add to `.gitignore` and `.Rbuildignore` |
| Missing `LazyData: true` for `data/` | `usethis::use_lazy_data()` |
| Hard-coded path like `data/file.csv` | `system.file("extdata", "file.csv", package = "mypkg")` |
| Object name in `data/foo.rda` differs from file name | Rename — they must match |
| Documenting datasets via `@docType data` | Use the `"name"` literal pattern shown above |
