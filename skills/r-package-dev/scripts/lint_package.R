#!/usr/bin/env Rscript
# lint_package.R — Run lintr on a package with tidyverse-friendly defaults.
#
# Usage:  Rscript lint_package.R [path/to/package]
#
# Runs lintr::lint_package() with a configured set of linters that match
# the conventions in this project (base pipe, <-, snake_case, double
# quotes). Prints a grouped summary and exits non-zero if any lints found.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

if (!dir.exists(pkg_path)) stop(sprintf("Directory not found: %s", pkg_path))
if (!file.exists(file.path(pkg_path, "DESCRIPTION"))) {
  stop("Not an R package (no DESCRIPTION).")
}
if (!requireNamespace("lintr", quietly = TRUE)) {
  stop("Package 'lintr' required. install.packages(\"lintr\").")
}

`%||%` <- function(a, b) if (is.null(a)) b else a

# Linter configuration. Projects may override by adding .lintr.
linters <- lintr::linters_with_defaults(
  assignment_linter = lintr::assignment_linter(
    operator = "<-", allow_right_assign = FALSE
  ),
  object_name_linter = lintr::object_name_linter(
    styles = c("snake_case", "symbols")
  ),
  line_length_linter = lintr::line_length_linter(length = 80L),
  quotes_linter = lintr::quotes_linter(delimiter = "\""),
  pipe_continuation_linter = lintr::pipe_continuation_linter(),
  pipe_consistency_linter = lintr::pipe_consistency_linter(pipe = "|>"),
  object_usage_linter = NULL,  # Noisy for package code with NSE
  cyclocomp_linter = lintr::cyclocomp_linter(complexity_limit = 20L),
  commented_code_linter = NULL  # Too many false positives on roxygen2
)

cat(sprintf("Linting %s...\n\n", normalizePath(pkg_path)))

lints <- tryCatch(
  lintr::lint_package(pkg_path, linters = linters),
  error = function(e) {
    cat("ERROR: lint failed.\n")
    cat("Details:", conditionMessage(e), "\n")
    quit(status = 1L)
  }
)

if (length(lints) == 0L) {
  cat("No lints found.\n")
  quit(status = 0L)
}

# Group by file
by_file <- split(lints, vapply(lints, `[[`, character(1), "filename"))

cat(sprintf("Found %d lints across %d files.\n\n",
            length(lints), length(by_file)))

for (file in names(by_file)) {
  file_lints <- by_file[[file]]
  cat(sprintf("--- %s (%d) ---\n", file, length(file_lints)))
  for (l in file_lints) {
    cat(sprintf("  L%d:%d [%s] %s\n",
                l$line_number %||% 0L,
                l$column_number %||% 0L,
                l$linter %||% "lint",
                l$message %||% ""))
  }
  cat("\n")
}

# Count by linter
linter_counts <- sort(
  table(vapply(lints, function(l) l$linter %||% "unknown", character(1))),
  decreasing = TRUE
)
cat("Summary by linter:\n")
for (name in names(linter_counts)) {
  cat(sprintf("  %-40s %d\n", name, linter_counts[[name]]))
}

quit(status = 1L)
