#!/usr/bin/env Rscript
# validate_description.R — Validate DESCRIPTION against CRAN expectations.
#
# Usage:  Rscript validate_description.R [path/to/package]
#
# Checks every common pre-submission issue in DESCRIPTION:
#   * Required fields present
#   * Title is title case, no "A Package for", no trailing period
#   * Description is non-trivial and ends with a period
#   * Authors@R uses person() and has exactly one cre
#   * URL and BugReports present
#   * Version is not a .9000 dev suffix (warning)
#   * License is a standard abbreviation
#   * Encoding is UTF-8
#
# Exits 0 if clean, 1 if any hard failure.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."
desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) {
  stop(sprintf("No DESCRIPTION in %s.", pkg_path))
}
if (!requireNamespace("desc", quietly = TRUE)) {
  stop("Package 'desc' required. install.packages(\"desc\").")
}

desc_obj <- desc::desc(file = desc_file)

errors <- character()
warnings <- character()

add_err <- function(msg) errors <<- c(errors, msg)
add_warn <- function(msg) warnings <<- c(warnings, msg)

# ---- Required fields ----
required <- c("Package", "Title", "Version", "Description",
              "License", "Authors@R")
for (field in required) {
  if (!desc_obj$has_fields(field)) {
    add_err(sprintf("Missing required field: %s", field))
  }
}

# ---- Package name ----
if (desc_obj$has_fields("Package")) {
  pkg_name <- desc_obj$get("Package")
  if (!grepl("^[A-Za-z][A-Za-z0-9.]+$", pkg_name)) {
    add_err(sprintf("Package name '%s' is invalid. Must match [A-Za-z][A-Za-z0-9.]+.",
                    pkg_name))
  }
  if (grepl("_", pkg_name)) {
    add_err(sprintf("Package name '%s' contains underscores (not allowed).",
                    pkg_name))
  }
}

# ---- Title ----
if (desc_obj$has_fields("Title")) {
  title <- trimws(desc_obj$get("Title"))
  if (grepl("\\.$", title)) {
    add_err(sprintf("Title must not end with a period: '%s'", title))
  }
  if (grepl("^(A|The) (Package|R Package) for", title, ignore.case = TRUE)) {
    add_err(sprintf("Title must not start with 'A/The Package for': '%s'",
                    title))
  }
  lower_exempt <- c("a", "an", "and", "as", "at", "but", "by", "for",
                    "in", "of", "on", "or", "the", "to", "via", "with")
  words <- strsplit(title, "\\s+")[[1]]
  # First and last word always capitalized; interior lowercase only for exempt
  for (i in seq_along(words)) {
    w <- words[i]
    if (nchar(w) <= 1L) next
    is_first_or_last <- (i == 1L || i == length(words))
    first_letter <- substr(w, 1, 1)
    if (is_first_or_last && grepl("^[a-z]", first_letter)) {
      add_warn(sprintf("Title may need title case: first/last word '%s' is lowercase",
                       w))
    }
    if (!is_first_or_last && grepl("^[a-z]", first_letter) &&
        !(tolower(w) %in% lower_exempt)) {
      add_warn(sprintf("Title: interior word '%s' may need capitalisation",
                       w))
    }
  }
}

# ---- Description ----
if (desc_obj$has_fields("Description")) {
  description <- trimws(desc_obj$get("Description"))
  description <- gsub("\\s+", " ", description)
  if (nchar(description) < 40L) {
    add_err(sprintf("Description too short (%d chars). Write at least one full sentence.",
                    nchar(description)))
  }
  if (!grepl("\\.\\s*$|\\.\\s*\\)\\s*$", description)) {
    add_err("Description must end with a period.")
  }
  # CRAN prefers packages referenced in Description to be single-quoted
  word_list <- regmatches(
    description,
    gregexpr("\\b([A-Z][a-zA-Z0-9]{2,})\\b", description)
  )[[1]]
  # Heuristic: words that look like package names but aren't quoted
  suspect <- word_list[nchar(word_list) > 3L]
  suspect <- setdiff(suspect, c("CRAN", "HTTP", "HTTPS", "JSON", "XML",
                                "HTML", "CSV", "URL", "API", "SQL",
                                "Tidy", "Bayesian"))
  if (length(suspect) > 0L) {
    unquoted <- suspect[!vapply(
      suspect,
      function(w) grepl(paste0("'", w, "'"), description, fixed = TRUE),
      logical(1)
    )]
    if (length(unquoted) > 0L) {
      add_warn(sprintf(
        "Description: consider single-quoting package names: %s",
        paste(unquoted, collapse = ", ")
      ))
    }
  }
}

# ---- Authors@R ----
if (desc_obj$has_fields("Authors@R")) {
  authors <- tryCatch(desc_obj$get_authors(), error = function(e) NULL)
  if (is.null(authors)) {
    add_err("Authors@R does not parse. Must use person() calls.")
  } else {
    roles <- unlist(lapply(authors, function(a) a$role))
    n_cre <- sum(roles == "cre")
    if (n_cre == 0L) {
      add_err("Authors@R must include exactly one person with role 'cre'.")
    } else if (n_cre > 1L) {
      add_err(sprintf("Authors@R has %d 'cre' roles; exactly one required.",
                      n_cre))
    }
    # Check cre has email
    cre_authors <- Filter(function(a) "cre" %in% a$role, authors)
    for (a in cre_authors) {
      if (is.null(a$email) || !nzchar(a$email)) {
        add_err(sprintf("cre '%s' must have an email address.",
                        paste(a$given, a$family)))
      }
    }
  }
}

# ---- URL / BugReports ----
if (!desc_obj$has_fields("URL")) {
  add_warn("Missing URL field (recommended).")
}
if (!desc_obj$has_fields("BugReports")) {
  add_warn("Missing BugReports field (recommended).")
}

# ---- Version ----
if (desc_obj$has_fields("Version")) {
  ver <- as.character(desc_obj$get_version())
  if (grepl("9000$", ver)) {
    add_warn(sprintf("Version %s has a .9000 dev suffix. Bump before release.",
                     ver))
  }
}

# ---- License ----
standard_licenses <- c(
  "MIT + file LICENSE", "GPL-2", "GPL-3", "GPL (>= 2)", "GPL (>= 3)",
  "LGPL-2", "LGPL-2.1", "LGPL-3", "LGPL (>= 2)", "LGPL (>= 2.1)",
  "LGPL (>= 3)", "Apache License (>= 2)", "Apache License 2.0",
  "BSD_2_clause + file LICENSE", "BSD_3_clause + file LICENSE",
  "CC0", "CC BY 4.0", "CC BY-SA 4.0", "AGPL-3", "AGPL (>= 3)"
)
if (desc_obj$has_fields("License")) {
  lic <- trimws(desc_obj$get("License"))
  if (!lic %in% standard_licenses) {
    add_warn(sprintf("License '%s' is non-standard. Verify against CRAN list.",
                     lic))
  }
}

# ---- Encoding ----
if (desc_obj$has_fields("Encoding")) {
  enc <- desc_obj$get("Encoding")
  if (enc != "UTF-8") {
    add_warn(sprintf("Encoding '%s'; prefer UTF-8.", enc))
  }
} else {
  add_warn("Missing Encoding field; add 'Encoding: UTF-8'.")
}

# ---- Output ----
cat(sprintf("=== DESCRIPTION validation: %s ===\n\n", pkg_path))
if (length(errors) > 0L) {
  cat("Errors:\n")
  for (e in errors) cat(sprintf("  * %s\n", e))
  cat("\n")
}
if (length(warnings) > 0L) {
  cat("Warnings:\n")
  for (w in warnings) cat(sprintf("  * %s\n", w))
  cat("\n")
}
if (length(errors) == 0L && length(warnings) == 0L) {
  cat("DESCRIPTION looks clean.\n")
}
cat(sprintf("Summary: %d errors, %d warnings.\n",
            length(errors), length(warnings)))
quit(status = if (length(errors) > 0L) 1L else 0L)
