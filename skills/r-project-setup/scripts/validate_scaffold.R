#!/usr/bin/env Rscript
# validate_scaffold.R — Verify a project directory has required scaffold files
#
# Usage:  Rscript validate_scaffold.R path/to/project
#
# Checks for .gitignore, README.md, and an .Rproj file.
# Reports PASS/FAIL per file.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  cat("Usage: Rscript validate_scaffold.R path/to/project\n")
  quit(status = 1)
}

project_dir <- args[1]
if (!dir.exists(project_dir)) stop(sprintf("Directory not found: %s", project_dir))

cat(sprintf("Validating project scaffold: %s\n\n", normalizePath(project_dir)))

any_missing <- FALSE

for (fname in c(".gitignore", "README.md")) {
  present <- file.exists(file.path(project_dir, fname))
  status <- if (present) "PASS" else "FAIL"
  if (!present) any_missing <- TRUE
  cat(sprintf("  [%s] %s\n", status, fname))
}

# Check for any .Rproj file (name varies by project)
rproj_files <- list.files(project_dir, pattern = "\\.Rproj$")
has_rproj <- length(rproj_files) > 0
if (!has_rproj) any_missing <- TRUE
rproj_label <- if (has_rproj) sprintf("*.Rproj (%s)", rproj_files[1]) else "*.Rproj"
cat(sprintf("  [%s] %s\n", if (has_rproj) "PASS" else "FAIL", rproj_label))

cat("\n")
if (any_missing) {
  cat("Result: SCAFFOLD INCOMPLETE — missing files listed above.\n")
  quit(status = 1)
} else {
  cat("Result: ALL CHECKS PASSED — scaffold is complete.\n")
  quit(status = 0)
}
