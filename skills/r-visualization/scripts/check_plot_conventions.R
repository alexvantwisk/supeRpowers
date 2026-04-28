#!/usr/bin/env Rscript
# check_plot_conventions.R — Scan R files for ggplot2 convention violations
#
# Usage:
#   Rscript scripts/check_plot_conventions.R <file_or_directory>
#
# Checks: + at line start, xlim/ylim vs coord_cartesian, non-colorblind
#         palettes, ggsave without width/height, legacy survminer,
#         geom_bar(stat="identity"), default theme + ggsave

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
    # Legacy survminer for new KM code
    if (grepl("library\\(survminer\\)", line)) {
      add_issue(f, i, "LEGACY_SURVMINER",
                "Prefer ggsurvfit (modern, ggplot2-native) over survminer for new KM code")
    }
    # geom_bar(stat = "identity") instead of geom_col
    if (grepl("geom_bar\\s*\\(\\s*stat\\s*=\\s*[\"']identity[\"']", line)) {
      add_issue(f, i, "USE_GEOM_COL",
                "Prefer geom_col() over geom_bar(stat = \"identity\")")
    }
  }
  # File-level: theme_grey/theme_gray combined with ggsave (publication context)
  joined <- paste(lines, collapse = "\n")
  uses_default_theme <- grepl("theme_gr[ae]y\\s*\\(", joined)
  uses_ggsave        <- grepl("ggsave\\s*\\(", joined)
  if (uses_default_theme && uses_ggsave) {
    add_issue(f, NA_integer_, "DEFAULT_THEME_ON_SAVE",
              "theme_grey/theme_gray combined with ggsave — default theme is not publication-ready; use theme_minimal/theme_bw/custom")
  }
}

message(sprintf("Scanned %d R file(s)", length(r_files)))
if (length(issues) == 0) {
  message("No ggplot2 convention violations found.")
} else {
  message(sprintf("Found %d issue(s):\n", length(issues)))
  for (issue in issues) {
    ln <- if (is.na(issue$line)) "-" else as.character(issue$line)
    message(sprintf("  [%s] %s:%s — %s", issue$type, issue$file, ln, issue$detail))
  }
  quit(status = 1)
}
