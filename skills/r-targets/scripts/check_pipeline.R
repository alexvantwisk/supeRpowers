#!/usr/bin/env Rscript
# check_pipeline.R — Validate a targets pipeline for common issues
#
# Usage:
#   Rscript scripts/check_pipeline.R [project_path]
#
# Checks: functions in _targets.R, tar_load() in target fns, missing tar_source()

args <- commandArgs(trailingOnly = TRUE)
project_path <- if (length(args) >= 1) args[1] else "."
targets_file <- file.path(project_path, "_targets.R")
r_dir <- file.path(project_path, "R")
if (!file.exists(targets_file)) { message(sprintf("Error: _targets.R not found in %s", project_path)); quit(status = 1) }

issues <- character(0)
targets_lines <- readLines(targets_file, warn = FALSE)

# Functions defined in _targets.R (should live in R/)
func_defs <- grep("^[a-zA-Z_][a-zA-Z0-9_.]*\\s*<-\\s*function\\s*\\(", targets_lines)
for (ln in func_defs) {
  line_text <- trimws(targets_lines[ln])
  if (!grepl("^(tar_|list\\()", line_text)) {
    issues <- c(issues, sprintf("FUNC_IN_TARGETS: line %d (move to R/): %s", ln, substring(line_text, 1, 80)))
  }
}

# Missing tar_source()
has_source <- any(grepl("(tar_source|\\bsource)\\s*\\(", targets_lines))
if (dir.exists(r_dir) && !has_source) {
  issues <- c(issues, "MISSING_SOURCE: R/ exists but _targets.R has no tar_source() or source()")
}

# tar_load/tar_read inside functions in R/
r_files <- if (dir.exists(r_dir)) list.files(r_dir, "\\.R$", full.names = TRUE, recursive = TRUE) else character(0)
for (f in r_files) {
  lines <- tryCatch(readLines(f, warn = FALSE), error = function(e) character(0))
  in_func <- FALSE; depth <- 0
  for (i in seq_along(lines)) {
    line <- lines[i]
    if (grepl("<-\\s*function\\s*\\(", line)) { in_func <- TRUE; depth <- 0 }
    if (in_func) {
      depth <- depth + nchar(gsub("[^{]", "", line)) - nchar(gsub("[^}]", "", line))
      if (grepl("\\b(tar_load|tar_read)\\s*\\(", line)) {
        issues <- c(issues, sprintf("TAR_LOAD_IN_FUNC: %s:%d — use target dependencies instead", basename(f), i))
      }
      if (depth <= 0) in_func <- FALSE
    }
  }
}

message(sprintf("Checked pipeline in %s", normalizePath(project_path, mustWork = FALSE)))
if (length(issues) == 0) {
  message("No pipeline issues found.")
} else {
  message(sprintf("Found %d issue(s):\n", length(issues)))
  for (issue in issues) message(sprintf("  - %s", issue))
  quit(status = 1)
}
