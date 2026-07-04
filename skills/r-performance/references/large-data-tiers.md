# Large-data and parallel tiers

Pick the tier by where the data lives and where the compute goes.

## Tier A — fits in RAM

dplyr for clarity; `data.table` or `collapse` for raw speed.

```r
library(collapse)
df |> fgroup_by(group) |> fsummarise(mean_v = fmean(value))   # fast in-RAM
```

## Tier B — larger than RAM, single machine

Query on disk; never read the whole file into memory.

```r
library(arrow)
ds <- open_dataset("data/parquet_dir/")   # multi-file Parquet, lazy, out-of-core
ds |>
  dplyr::filter(year == 2025) |>
  dplyr::group_by(region) |>
  dplyr::summarise(total = sum(value)) |>
  dplyr::collect()                          # only the result lands in RAM

# duckplyr: dplyr syntax on the DuckDB engine (out-of-core, zero-copy)
library(duckplyr)
big <- duckplyr::as_duckplyr_df(large_df)
big |> dplyr::summarise(.by = carrier, n = dplyr::n())

# Or raw DuckDB SQL over a Parquet glob without loading it
con <- DBI::dbConnect(duckdb::duckdb())
DBI::dbGetQuery(con, "SELECT region, SUM(value) FROM 'data/*.parquet' GROUP BY region")
```

## Tier C — parallel compute

`mirai` is the modern backend; purrr integrates through `in_parallel()`
(purrr >= 1.1).

```r
library(mirai)
library(purrr)
daemons(4)                                       # start 4 parallel daemons
results <- map(items, in_parallel(\(x) slow_fn(x)))
daemons(0)                                       # stop daemons

# crew (mirai-powered) for pipeline-scale; crew.cluster for HPC (SLURM/SGE/PBS)
library(crew)
controller <- crew_controller_local(workers = 4)
```

### Compatibility note (furrr / future)

Existing code using furrr/future still works:

```r
library(furrr); library(future)
plan(multisession, workers = 4)
future_map(items, slow_fn)
plan(sequential)
```

Prefer `mirai` + `purrr::in_parallel()` for new code; keep furrr only for
existing pipelines.
