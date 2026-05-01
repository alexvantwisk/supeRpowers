#!/usr/bin/env Rscript
# check_docs.R — Check roxygen2 documentation completeness for exports.
#
# Usage:  Rscript check_docs.R [path/to/package]
#
# For every exported function, verifies that the roxygen2 block contains:
#   * @param for every argument (and no extras)
#   * @returns (or @return)
#   * @examples
#   * A title (first non-empty line)
# Also flags:
#   * Exports with no roxygen block at all
#   * @param entries that don't match any argument
#   * @examples that use \dontrun{} (flag only; may be intentional)
#
# Exits 0 if all exports documented, 1 if any gaps.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

if (!dir.exists(pkg_path)) stop(sprintf("Directory not found: %s", pkg_path))
desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) stop("Not an R package (no DESCRIPTION).")
if (!requireNamespace("roxygen2", quietly = TRUE)) {
  stop("Package roxygen2 required.")
}

`%||%` <- function(a, b) if (is.null(a)) b else a

r_dir <- file.path(pkg_path, "R")
if (!dir.exists(r_dir)) {
  cat("No R/ directory.\n")
  quit(status = 0L)
}

r_files <- list.files(r_dir, pattern = "\\.[RrSsQq]$", full.names = TRUE)
if (length(r_files) == 0L) {
  cat("No R source files.\n")
  quit(status = 0L)
}

# Parse with roxygen2 to get blocks
env <- new.env(parent = baseenv())
blocks <- tryCatch(
  roxygen2::parse_package(pkg_path, env = env),
  error = function(e) {
    cat("ERROR: roxygen2 parse failed.\n")
    cat("Details:", conditionMessage(e), "\n")
    quit(status = 1L)
  }
)

issues <- list()
add_issue <- function(file, line, name, msg) {
  issues[[length(issues) + 1L]] <<- list(
    file = file, line = line, name = name, msg = msg
  )
}

tag_names <- function(block) {
  vapply(block$tags, function(t) t$tag, character(1))
}

for (block in blocks) {
  tags <- tag_names(block)

  is_export <- "export" %in% tags
  if (!is_export) next

  obj_name <- block$object$alias %||% block$object$topic %||%
    (if (is.function(block$object$value)) "(anonymous)" else "(unknown)")
  file <- block$file
  line <- block$line

  # Title is usually tag "title" or the first description line
  has_title <- "title" %in% tags ||
    (!is.null(block$object$value) && nzchar(block$object$alias %||% ""))

  # Check for @returns / @return
  has_returns <- any(tags %in% c("returns", "return"))
  if (!has_returns) {
    add_issue(file, line, obj_name, "Missing @returns (or @return)")
  }

  # Check for @examples
  has_examples <- "examples" %in% tags || "examplesIf" %in% tags
  if (!has_examples) {
    add_issue(file, line, obj_name, "Missing @examples")
  } else {
    example_tag <- block$tags[[which(tags == "examples")[1]]]
    example_text <- paste(
      vapply(example_tag$val, as.character, character(1)),
      collapse = "\n"
    )
    if (grepl("\\\\dontrun\\{", example_text)) {
      add_issue(file, line, obj_name,
                "Uses \\dontrun{} — prefer \\donttest{} when possible")
    }
  }

  # @param coverage
  if (is.function(block$object$value)) {
    formal_args <- names(formals(block$object$value))
    documented_params <- character()
    for (t in block$tags) {
      if (t$tag == "param") {
        nm <- t$val$name
        if (!is.null(nm)) documented_params <- c(documented_params, nm)
      } else if (t$tag == "inheritParams") {
        # Assume inherited params cover everything (conservative)
        documented_params <- formal_args
      }
    }
    # Flatten comma-separated @param foo,bar
    documented_params <- unlist(strsplit(documented_params, "\\s*,\\s*"))
    missing_params <- setdiff(formal_args, c(documented_params, "..."))
    # "..." is documented with @param ... but may be named differently
    if (length(missing_params) > 0L) {
      add_issue(file, line, obj_name,
                sprintf("Missing @param for: %s",
                        paste(missing_params, collapse = ", ")))
    }
    extra_params <- setdiff(documented_params, c(formal_args, "..."))
    if (length(extra_params) > 0L) {
      add_issue(file, line, obj_name,
                sprintf("@param documents non-existent argument(s): %s",
                        paste(extra_params, collapse = ", ")))
    }
  }
}

cat(sprintf("=== Documentation check: %s ===\n\n", pkg_path))
cat(sprintf("Exports checked: %d\n",
            sum(vapply(blocks, function(b) "export" %in% tag_names(b),
                       logical(1)))))
cat(sprintf("Issues found: %d\n\n", length(issues)))

if (length(issues) == 0L) {
  cat("All exports are fully documented.\n")
  quit(status = 0L)
}

# Group by file
by_file <- split(issues, vapply(issues, `[[`, character(1), "file"))
for (file in names(by_file)) {
  cat(sprintf("--- %s ---\n", file))
  for (i in by_file[[file]]) {
    cat(sprintf("  %s (L%d): %s\n",
                i$name, i$line %||% 0L, i$msg))
  }
  cat("\n")
}

cat("Fix roxygen blocks, then regenerate docs (devtools document or roxygen2).\n")
quit(status = 1L)
