#!/usr/bin/env Rscript
# create_reprex.R — Generate a minimal reprex template file
#
# Usage:
#   Rscript scripts/create_reprex.R [output_path]
#
# Arguments:
#   output_path  Path for the generated reprex file (default: "reprex.R")
#
# The template includes sections for library loading, data setup,
# expected vs actual behavior, and session info.

args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) args[1] else "reprex.R"

template <- c(
  "# Minimal Reproducible Example",
  "# Created: %s",
  "",
  "# --- Libraries ---",
  "# Load only what's needed to reproduce the issue",
  "# library(dplyr)",
  "",
  "# --- Data Setup ---",
  "# Create the smallest dataset that triggers the problem",
  "df <- data.frame(",
  "  x = 1:5,",
  "  y = c(\"a\", \"b\", \"c\", \"d\", \"e\")",
  ")",
  "",
  "# --- Expected Behavior ---",
  "# Describe what you expect to happen:",
  "# (e.g., \"df should have 3 rows after filtering\")",
  "",
  "# --- Actual Behavior ---",
  "# Code that demonstrates the problem:",
  "result <- df  # Replace with your problematic code",
  "print(result)",
  "",
  "# --- Error / Unexpected Output ---",
  "# Paste the error message or describe the unexpected output here:",
  "# Error in ...: ...",
  "",
  "# --- Session Info ---",
  "sessionInfo()"
)

template[2] <- sprintf(template[2], Sys.Date())
content <- paste(template, collapse = "\n")

tryCatch(
  {
    writeLines(content, output_path)
    message(sprintf("Reprex template created: %s", output_path))
  },
  error = function(e) {
    message(sprintf("Error creating reprex template: %s", conditionMessage(e)))
    quit(status = 1)
  }
)
