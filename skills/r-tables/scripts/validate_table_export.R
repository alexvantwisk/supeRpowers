#!/usr/bin/env Rscript
# validate_table_export.R — Verify a gt/gtsummary table can export to HTML
#
# Usage:  Rscript validate_table_export.R path/to/table.rds
#
# Reads a gt or gtsummary table from .rds, exports to a temp HTML file,
# and verifies the output exists and is non-empty.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  cat("Usage: Rscript validate_table_export.R path/to/table.rds\n")
  quit(status = 1)
}

table_path <- args[1]
if (!file.exists(table_path)) stop(sprintf("File not found: %s", table_path))

tbl_obj <- tryCatch(readRDS(table_path),
  error = function(e) stop(sprintf("Could not read RDS: %s", e$message)))

# Convert gtsummary to gt if needed
if (inherits(tbl_obj, "gtsummary")) {
  if (!requireNamespace("gtsummary", quietly = TRUE)) stop("gtsummary not installed.")
  cat("Detected gtsummary object — converting to gt...\n")
  tbl_obj <- gtsummary::as_gt(tbl_obj)
}

if (!inherits(tbl_obj, "gt_tbl")) stop("Object is not a gt or gtsummary table.")
if (!requireNamespace("gt", quietly = TRUE)) stop("gt package not installed.")

out_file <- tempfile(fileext = ".html")
cat(sprintf("Exporting table to: %s\n", out_file))

export_ok <- tryCatch(
  { gt::gtsave(tbl_obj, filename = out_file); TRUE },
  error = function(e) { cat(sprintf("  [FAIL] Export error: %s\n", e$message)); FALSE }
)

if (!export_ok) quit(status = 1)
if (!file.exists(out_file)) { cat("  [FAIL] HTML file was not created.\n"); quit(status = 1) }

file_size <- file.info(out_file)$size
if (is.na(file_size) || file_size == 0) {
  cat("  [FAIL] HTML file is empty.\n")
  quit(status = 1)
}

cat(sprintf("  [PASS] HTML exported successfully (%s bytes).\n", format(file_size, big.mark = ",")))
unlink(out_file)
cat("\nResult: TABLE EXPORT VALIDATED.\n")
