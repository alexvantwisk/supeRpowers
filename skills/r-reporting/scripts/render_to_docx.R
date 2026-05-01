## ============================================================================
## Script: render_to_docx.R
## Description: Render a Quarto report to docx via the Quarto CLI (system2).
##              Avoids the R `quarto` package — works on machines where it is
##              not installed. Produces a timestamped output for audit trail.
##
## Usage:       source(here::here("analysis", "render_to_docx.R"))
##              # or with overrides:
##              render_to_docx(
##                input_qmd  = "inst/templates/report.qmd",
##                output_dir = "output"
##              )
##
## R packages:  here
## ============================================================================

if (!requireNamespace("here", quietly = TRUE)) {
  stop("Package here is required. Install with: install.packages(\"here\")")
}

render_to_docx <- function(
  input_qmd  = here::here("inst", "templates", "report.qmd"),
  output_dir = here::here("output")
) {
  stopifnot(file.exists(input_qmd))

  quarto_bin <- Sys.which("quarto")
  if (nzchar(quarto_bin) == 0L) {
    stop("Quarto CLI not found on PATH. Install from https://quarto.org and rerun.")
  }
  message("Using Quarto CLI: ", quarto_bin)
  message("Rendering: ", input_qmd)

  result <- system2(
    quarto_bin,
    args = c(
      "render", shQuote(input_qmd),
      "--to", "docx",
      "--execute-dir", shQuote(here::here())
    ),
    stdout = "", stderr = "",
    wait = TRUE
  )
  if (result != 0L) {
    stop(sprintf("quarto render failed (exit %d).", result))
  }

  # Default output: same dir as the qmd, same basename, .docx extension.
  default_path <- sub("\\.qmd$", ".docx", input_qmd, ignore.case = TRUE)
  stopifnot(file.exists(default_path))

  # Timestamped audit trail name.
  ts <- format(Sys.time(), "%Y%m%d_%H%M%S")
  ts_basename <- sub("\\.docx$", paste0("_", ts, ".docx"), basename(default_path))

  in_template_dir <- file.path(dirname(default_path), ts_basename)
  file.rename(default_path, in_template_dir)

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  output_dest <- file.path(output_dir, ts_basename)
  file.copy(in_template_dir, output_dest, overwrite = TRUE)

  message(sprintf("DOCX written to: %s", output_dest))
  invisible(output_dest)
}

# When sourced as a script, invoke with defaults.
if (sys.nframe() == 0L) {
  render_to_docx()
}
