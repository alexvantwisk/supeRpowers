#!/usr/bin/env Rscript
# check_plot_conventions.R — Scan R files for ggplot2 convention violations
#
# Usage:
#   Rscript scripts/check_plot_conventions.R <file_or_directory>
#
# Checks: + at line start, xlim/ylim vs coord_cartesian, non-colorblind
#         palettes, ggsave without width/height

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) { message("Usage: Rscript check_plot_conventions.R <file_or_dir>"); quit(status = 1) }
target <- args[1]

if (dir.exists(target)) {
  r_files <- list.files(target, "\\.R$", recursive = TRUE, full.names = TRUE)
} else if (file.exists(target)) {
  r_files <- target
} else { message(sprintf("Error: path not found: %s", target)); quit(status = 1) }
if (length(r_files) == 0) { message("No .R files found."); quit(status = 0) }

issues <- list()
add_issue <- function(file, ln, type, detail) {
  issues[[length(issues) + 1]] <<- list(file = file, line = ln, type = type, detail = detail)
}
risky_pals <- c("rainbow", "heat\\.colors", "topo\\.colors", "cm\\.colors")

for (f in r_files) {
  lines <- tryCatch(readLines(f, warn = FALSE), error = function(e) character(0))
  for (i in seq_along(lines)) {
    line <- lines[i]
    if (grepl("^\\s*\\+\\s*(geom_|theme|scale_|labs|coord_|facet_|stat_|annotate)", line)) {
      add_issue(f, i, "PLUS_START_OF_LINE", "Place `+` at end of previous line")
    }
    if (grepl("\\b(xlim|ylim)\\s*\\(", line) && !grepl("coord_cartesian", line)) {
      add_issue(f, i, "XLIM_YLIM", "Use coord_cartesian() to avoid dropping data")
    }
    for (pal in risky_pals) {
      if (grepl(paste0("\\b", pal, "\\s*\\("), line)) {
        add_issue(f, i, "NON_CB_PALETTE", sprintf("Replace %s() with colorblind-safe palette", gsub("\\\\.", "", pal)))
      }
    }
    # ggsave without dimensions
    if (grepl("ggsave\\s*\\(", line)) {
      block <- paste(lines[i:min(i + 5, length(lines))], collapse = " ")
      if (!grepl("width\\s*=", block) || !grepl("height\\s*=", block)) {
        add_issue(f, i, "GGSAVE_NO_DIMS", "ggsave() missing explicit width/height")
      }
    }
  }
}

message(sprintf("Scanned %d R file(s)", length(r_files)))
if (length(issues) == 0) {
  message("No ggplot2 convention violations found.")
} else {
  message(sprintf("Found %d issue(s):\n", length(issues)))
  for (issue in issues) message(sprintf("  [%s] %s:%d — %s", issue$type, issue$file, issue$line, issue$detail))
  quit(status = 1)
}
