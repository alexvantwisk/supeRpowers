#!/usr/bin/env Rscript
# check_modules.R — Scan a Shiny app for common module issues
#
# Usage:
#   Rscript scripts/check_modules.R [app_directory]
#
# Checks: missing ns() in module UI, reactiveVal inside observe, renderUI without ns()

args <- commandArgs(trailingOnly = TRUE)
app_dir <- if (length(args) >= 1) args[1] else "."
if (!dir.exists(app_dir)) { message(sprintf("Error: directory not found: %s", app_dir)); quit(status = 1) }

r_files <- list.files(app_dir, pattern = "\\.R$", recursive = TRUE, full.names = TRUE)
if (length(r_files) == 0) { message("No .R files found."); quit(status = 0) }

issues <- list()
add_issue <- function(file, line_num, type, detail) {
  issues[[length(issues) + 1]] <<- list(file = file, line = line_num, type = type, detail = detail)
}

for (f in r_files) {
  lines <- tryCatch(readLines(f, warn = FALSE), error = function(e) character(0))
  if (length(lines) == 0) next
  in_module_ui <- FALSE
  for (i in seq_along(lines)) {
    line <- lines[i]
    if (grepl("(_ui|UI)\\s*<-\\s*function", line)) in_module_ui <- TRUE
    if (in_module_ui) {
      if (grepl("(inputId|outputId)\\s*=\\s*\"", line) && !grepl("ns\\(", line)) {
        add_issue(f, i, "MISSING_NS", trimws(line))
      }
      if (grepl("^\\s*\\}", line)) in_module_ui <- FALSE
    }
    if (grepl("observe", line) && grepl("reactiveVal", line)) {
      add_issue(f, i, "REACTIVE_IN_OBSERVE", trimws(line))
    }
    if (grepl("renderUI\\s*\\(", line)) {
      block <- paste(lines[i:min(i + 15, length(lines))], collapse = "\n")
      if (grepl("(inputId|outputId)\\s*=", block) && !grepl("(session\\$ns|ns\\()", block)) {
        add_issue(f, i, "RENDERUI_NO_NS", "renderUI block may be missing ns()")
      }
    }
  }
}

message(sprintf("Scanned %d R file(s) in %s", length(r_files), app_dir))
if (length(issues) == 0) {
  message("No module issues found.")
} else {
  message(sprintf("Found %d issue(s):\n", length(issues)))
  for (issue in issues) {
    message(sprintf("  [%s] %s:%d — %s", issue$type, issue$file, issue$line, issue$detail))
  }
  quit(status = 1)
}
