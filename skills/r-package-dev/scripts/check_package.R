#!/usr/bin/env Rscript
# check_package.R — Run devtools::check() and summarize results
#
# Usage:  Rscript check_package.R [path/to/package]
#
# Runs devtools::check() on the given package directory (defaults to ".")
# and prints a clean summary of errors, warnings, and notes.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

if (!dir.exists(pkg_path)) stop(sprintf("Directory not found: %s", pkg_path))
if (!file.exists(file.path(pkg_path, "DESCRIPTION"))) {
  stop(sprintf("No DESCRIPTION file in %s — not an R package.", pkg_path))
}
if (!requireNamespace("devtools", quietly = TRUE)) {
  stop("devtools is not installed. Run: install.packages(\"devtools\")")
}

cat(sprintf("Running R CMD check on: %s\n\n", normalizePath(pkg_path)))

result <- tryCatch(
  devtools::check(pkg_path, quiet = TRUE),
  error = function(e) stop(sprintf("Check failed: %s", e$message))
)

n_err <- length(result$errors)
n_warn <- length(result$warnings)
n_note <- length(result$notes)

cat(sprintf("  Errors: %d | Warnings: %d | Notes: %d\n\n", n_err, n_warn, n_note))

print_issues <- function(label, items) {
  if (length(items) > 0) {
    cat(sprintf("--- %s ---\n", label))
    for (item in items) cat(sprintf("  * %s\n", trimws(item)))
    cat("\n")
  }
}

print_issues("ERRORS", result$errors)
print_issues("WARNINGS", result$warnings)
print_issues("NOTES", result$notes)

if (n_err > 0) {
  cat("Result: FAILED — fix errors before submitting.\n")
  quit(status = 1)
} else {
  cat("Result: PASSED.\n")
  quit(status = 0)
}
