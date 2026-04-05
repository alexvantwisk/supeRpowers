# Eval: r-performance

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to "clean and reshape" a normal-sized dataset (under 1M rows) with no mention of performance issues, does the skill defer to r-data-analysis?
2. When the user reports an error in optimized code (e.g., a data.table syntax mistake), does the skill defer the error diagnosis to r-debugging rather than debugging it inline?
3. Does the skill require profiling results (or recommend profiling) before suggesting any optimization, rather than jumping to a solution?
4. When suggesting data.table as an optimization, does the skill include or require a benchmark comparison against the original tidyverse code?
5. When asked about speeding up tidymodels training, does the skill defer to r-tidymodels for model-level tuning rather than applying general optimization techniques?
6. When recommending parallel processing, does the skill address overhead costs and minimum problem size thresholds rather than unconditionally suggesting parallelism?
7. Does all generated code use `|>` and `<-` exclusively (no `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "My dplyr pipeline on a 50M-row data frame takes 4 minutes. Here's the code: [group_by |> summarise with multiple window functions]. Profile it and suggest optimizations."
- "I need to process 200 Parquet files (total 80GB) in R. What's the most memory-efficient approach?"

### Edge Cases

- "I have a hot loop calling an R function 100,000 times. It's too slow. I'm considering Rcpp but I've never used it. Walk me through converting just the bottleneck to C++."
- "I want to parallelize a `map()` call across 8 cores using the future framework, but some iterations fail. How do I handle errors without losing completed results?"
- "My dataset is 40GB and won't fit in memory. I've heard about arrow and memory-mapped files. How do I query it without loading everything?"

### Adversarial Cases

- "I have a data frame with 50,000 rows. Clean the column names, parse dates, and remove duplicates." (boundary: normal-scale wrangling should defer to r-data-analysis)
- "My data.table code throws 'Column not found' errors when I use `:=` inside a function. What's wrong?" (boundary: error diagnosis should defer to r-debugging)
- "My xgboost model training is slow. How do I speed up hyperparameter tuning in tidymodels?" (boundary: model training optimization should defer to r-tidymodels)

### Boundary Tests

- "Read a CSV, fix column types, and pivot to long format. The file is about 10,000 rows." boundary -> r-data-analysis
- "I'm getting a segfault when I call my Rcpp function. Help me figure out why." boundary -> r-debugging
- "How do I use parallel backend with tune_grid() in tidymodels?" boundary -> r-tidymodels

## Success Criteria

- Happy path profiling response MUST start with profiling (using `profvis`, `bench::mark`, or `system.time`) BEFORE suggesting any code changes.
- Happy path 80GB response MUST recommend `arrow::open_dataset()` with lazy evaluation and MUST NOT suggest `read.csv()` or `readr::read_csv()` on the full dataset.
- Rcpp edge case MUST include a minimal working `.cpp` file with `// [[Rcpp::export]]`, proper type mapping, and a benchmark comparing R vs. Rcpp versions.
- Parallel processing response MUST mention `future::plan()`, discuss worker overhead, and show error handling with `safely()` or `future.apply` error collection -- not just `mclapply`.
- Arrow/memory-mapped response MUST demonstrate `dplyr` verbs on an Arrow dataset with `collect()` only at the end, not eager loading.
- Normal-scale wrangling prompt MUST be deferred to r-data-analysis; response must NOT profile or optimize a 50K-row dataset.
- Error diagnosis prompt MUST be deferred to r-debugging; response must NOT apply the reproduce-isolate-diagnose workflow.
- Model training prompt MUST be deferred to r-tidymodels; response must NOT produce `tune_grid()` or `fit_resamples()` code.
- Response must NOT suggest switching to data.table without showing benchmark evidence that it actually improves the specific bottleneck.
- Response must NOT recommend parallelism for tasks under 10 seconds without discussing overhead tradeoffs.
- Response must NOT suggest optimization without profiling first; phrases like "try data.table, it's faster" without measurement are a failure.
- Response must NOT use `%>%`, `=` for assignment, or single quotes for strings.
