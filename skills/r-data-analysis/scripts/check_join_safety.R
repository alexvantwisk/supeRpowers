#!/usr/bin/env Rscript
# check_join_safety.R — Check for duplicate keys before a join
#
# Usage:  Rscript check_join_safety.R path/to/data.csv key_column
#
# Reads a CSV and checks whether the specified column has unique values.
# Reports duplicate counts if duplicates are found.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  cat("Usage: Rscript check_join_safety.R path/to/data.csv key_column\n")
  quit(status = 1)
}

csv_path <- args[1]
key_col <- args[2]

if (!file.exists(csv_path)) stop(sprintf("File not found: %s", csv_path))

df <- tryCatch(
  read.csv(csv_path, check.names = FALSE),
  error = function(e) stop(sprintf("Could not read CSV: %s", e$message))
)

if (!key_col %in% colnames(df)) {
  stop(sprintf("Column '%s' not found. Available: %s", key_col, paste(colnames(df), collapse = ", ")))
}

key_values <- df[[key_col]]
total_rows <- length(key_values)
unique_count <- length(unique(key_values))
dup_count <- total_rows - unique_count

cat(sprintf("Join safety check: %s (column: %s)\n", csv_path, key_col))
cat(sprintf("  Total rows:  %d\n  Unique keys: %d\n", total_rows, unique_count))

if (dup_count == 0) {
  cat("\n  [SAFE] Key is unique — safe for 1:1 join.\n")
  quit(status = 0)
}

freq_table <- sort(table(key_values), decreasing = TRUE)
dups <- freq_table[freq_table > 1]
top_n <- min(10, length(dups))
cat(sprintf("  Duplicates:  %d\n\n", dup_count))
cat("  [WARNING] Key is NOT unique — join will produce extra rows.\n")
cat(sprintf("  Top %d duplicated values:\n", top_n))
for (i in seq_len(top_n)) {
  cat(sprintf("    %s  (n = %d)\n", names(dups)[i], dups[i]))
}
quit(status = 1)
