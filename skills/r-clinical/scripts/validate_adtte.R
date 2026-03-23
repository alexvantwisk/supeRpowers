#!/usr/bin/env Rscript
# validate_adtte.R — Validate an ADTTE dataset for required CDISC variables
#
# Usage:
#   Rscript validate_adtte.R path/to/adtte.csv
#
# Checks that the CSV contains the required CDISC ADTTE variables:
#   USUBJID, AVAL, CNSR, PARAMCD, TRT01P
# Prints PASS/FAIL per variable and exits with code 1 if any are missing.

required_vars <- c("USUBJID", "AVAL", "CNSR", "PARAMCD", "TRT01P")

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  cat("Error: No CSV path provided.\n")
  cat("Usage: Rscript validate_adtte.R path/to/adtte.csv\n")
  quit(status = 1)
}

csv_path <- args[1]

if (!file.exists(csv_path)) {
  cat(sprintf("Error: File not found: %s\n", csv_path))
  quit(status = 1)
}

adtte <- tryCatch(
  read.csv(csv_path, nrows = 0, check.names = FALSE),
  error = function(e) {
    cat(sprintf("Error: Could not read CSV: %s\n", e$message))
    quit(status = 1)
  }
)

actual_vars <- colnames(adtte)
cat(sprintf("Validating ADTTE dataset: %s\n", csv_path))
cat(sprintf("Found %d columns\n\n", length(actual_vars)))

any_fail <- FALSE

for (var in required_vars) {
  present <- var %in% actual_vars
  status <- if (present) "PASS" else "FAIL"
  if (!present) any_fail <- TRUE
  cat(sprintf("  [%s] %s\n", status, var))
}

cat("\n")

if (any_fail) {
  cat("Result: VALIDATION FAILED — missing required variables.\n")
  quit(status = 1)
} else {
  cat("Result: ALL CHECKS PASSED — ADTTE structure is valid.\n")
  quit(status = 0)
}
