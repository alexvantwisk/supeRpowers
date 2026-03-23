#!/usr/bin/env Rscript
# check_render.R — Render a .qmd file and check for common issues
#
# Usage:
#   Rscript scripts/check_render.R <path_to_qmd>
#
# Checks: render errors, unresolved cross-refs, output file size (> 10 MB).
# Requires: quarto CLI on PATH

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) { message("Usage: Rscript check_render.R <path_to_qmd>"); quit(status = 1) }
qmd_path <- args[1]
if (!file.exists(qmd_path)) { message(sprintf("Error: file not found: %s", qmd_path)); quit(status = 1) }

issues <- character(0)

message(sprintf("Rendering %s ...", qmd_path))
render_result <- tryCatch(
  {
    out <- system2("quarto", c("render", shQuote(qmd_path)), stdout = TRUE, stderr = TRUE)
    attr(out, "status")
  },
  error = function(e) { issues <<- c(issues, sprintf("RENDER ERROR: %s", conditionMessage(e))); 1L }
)
if (!is.null(render_result) && render_result != 0) {
  issues <- c(issues, "RENDER FAILED: quarto render returned non-zero exit code")
}

output_path <- sub("\\.qmd$", ".html", qmd_path, ignore.case = TRUE)
if (file.exists(output_path)) {
  content <- readLines(output_path, warn = FALSE)
  xref_hits <- grep("\\?(fig|tbl|sec|eq)-", content, value = TRUE)
  if (length(xref_hits) > 0) {
    issues <- c(issues, sprintf("UNRESOLVED XREF: %d cross-reference(s)", length(xref_hits)))
  }
  size_mb <- file.info(output_path)$size / 1e6
  if (size_mb > 10) {
    issues <- c(issues, sprintf("LARGE OUTPUT: %.1f MB", size_mb))
  }
  message(sprintf("Output: %s (%.2f MB)", output_path, size_mb))
}

message("")
if (length(issues) == 0) {
  message("All checks passed.")
} else {
  message(sprintf("Found %d issue(s):", length(issues)))
  for (issue in issues) message(sprintf("  - %s", issue))
  quit(status = 1)
}
