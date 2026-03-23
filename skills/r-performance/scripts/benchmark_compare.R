#!/usr/bin/env Rscript
# benchmark_compare.R — Compare two R expressions with bench::mark
#
# Usage:
#   Rscript scripts/benchmark_compare.R <expr1> <expr2> [iterations]
#
# Example:
#   Rscript scripts/benchmark_compare.R "mean(1:1e6)" "sum(1:1e6)/1e6" 50

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  message("Usage: Rscript benchmark_compare.R <expr1> <expr2> [iterations]")
  quit(status = 1)
}

expr1_str <- args[1]
expr2_str <- args[2]
iterations <- if (length(args) >= 3) as.integer(args[3]) else 100L

if (is.na(iterations) || iterations < 1) {
  message("Error: iterations must be a positive integer")
  quit(status = 1)
}

tryCatch(
  {
    if (!requireNamespace("bench", quietly = TRUE)) {
      stop("Package 'bench' is required. Install with: install.packages(\"bench\")")
    }
    expr1 <- parse(text = expr1_str)
    expr2 <- parse(text = expr2_str)
    message(sprintf("Benchmarking %d iterations...\n  expr1: %s\n  expr2: %s\n",
                    iterations, expr1_str, expr2_str))
    results <- bench::mark(
      expr1 = eval(expr1), expr2 = eval(expr2),
      iterations = iterations, check = FALSE
    )
    results$expression <- c(expr1_str, expr2_str)
    print(results[, c("expression", "min", "median", "mem_alloc", "n_itr")])
    faster <- if (results$median[1] < results$median[2]) expr1_str else expr2_str
    ratio <- max(results$median) / min(results$median)
    message(sprintf("\nFaster: %s (%.1fx)", faster, ratio))
  },
  error = function(e) {
    message(sprintf("Benchmark error: %s", conditionMessage(e)))
    quit(status = 1)
  }
)
