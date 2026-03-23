#!/usr/bin/env Rscript
# check_leakage.R — Scan R scripts for potential data leakage patterns
#
# Usage:
#   Rscript scripts/check_leakage.R <script_path>
#
# Checks: preprocessing before split, feature selection on full data,
#         missing set.seed() before resampling, step_*() without recipe()

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) { message("Usage: Rscript check_leakage.R <script_path>"); quit(status = 1) }
script_path <- args[1]
if (!file.exists(script_path)) { message(sprintf("Error: file not found: %s", script_path)); quit(status = 1) }

lines <- readLines(script_path, warn = FALSE)
issues <- list()
add_issue <- function(ln, type, detail) {
  issues[[length(issues) + 1]] <<- list(line = ln, type = type, detail = detail)
}

split_line <- NA_integer_; recipe_line <- NA_integer_
for (i in seq_along(lines)) {
  line <- lines[i]
  if (grepl("initial_split\\s*\\(", line)) split_line <- i
  if (grepl("\\brecipe\\s*\\(", line)) recipe_line <- i

  # Transforms before split
  if (is.na(split_line)) {
    for (pat in c("\\bscale\\s*\\(", "\\bnormalize\\s*\\(", "\\bcenter\\s*\\(")) {
      if (grepl(pat, line)) add_issue(i, "PRE_SPLIT_TRANSFORM", trimws(line))
    }
  }
  # Feature selection before split
  if (is.na(split_line) && grepl("(cor\\(|select_if|step_corr|boruta|varImp)", line)) {
    add_issue(i, "FEATURE_SELECT_FULL_DATA", trimws(line))
  }
  # Resampling without set.seed
  for (fn in c("vfold_cv", "bootstraps", "mc_cv", "initial_split", "group_vfold_cv")) {
    if (grepl(paste0("\\b", fn, "\\s*\\("), line)) {
      preceding <- paste(lines[max(1, i - 5):(i - 1)], collapse = " ")
      if (!grepl("set\\.seed\\s*\\(", preceding)) {
        add_issue(i, "MISSING_SEED", sprintf("No set.seed() before %s()", fn))
      }
    }
  }
  # step_*() without recipe
  if (grepl("\\bstep_\\w+\\s*\\(", line) && is.na(recipe_line)) {
    add_issue(i, "STEP_WITHOUT_RECIPE", sprintf("step_*() before recipe() at line %d", i))
  }
}

message(sprintf("Scanned %s (%d lines)", script_path, length(lines)))
if (length(issues) == 0) {
  message("No data leakage patterns detected.")
} else {
  message(sprintf("Found %d potential issue(s):\n", length(issues)))
  for (issue in issues) message(sprintf("  [%s] Line %d: %s", issue$type, issue$line, issue$detail))
  quit(status = 1)
}
