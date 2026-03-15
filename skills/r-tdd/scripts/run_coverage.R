#!/usr/bin/env Rscript
# Run package test coverage and print function-level summary
# Usage: Rscript scripts/run_coverage.R [package_path]

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) > 0) args[1] else "."

if (!requireNamespace("covr", quietly = TRUE)) {
  cli::cli_abort("Package {.pkg covr} is required. Install with {.code install.packages('covr')}")
}

cov <- covr::package_coverage(path = pkg_path)

# Overall summary
cat("\n=== Coverage Summary ===\n")
pct <- covr::percent_coverage(cov)
cat(sprintf("Overall coverage: %.1f%%\n", pct))

if (pct < 80) {
  cat("WARNING: Coverage below 80% threshold!\n")
}

# Function-level breakdown
cat("\n=== Function-Level Coverage ===\n")
func_cov <- covr::tally_coverage(cov, by = "function")
func_cov <- func_cov[order(func_cov$value), ]
print(func_cov[, c("filename", "functions", "value")], row.names = FALSE)

cat(sprintf("\nTotal: %.1f%% | Threshold: 80%%\n", pct))
