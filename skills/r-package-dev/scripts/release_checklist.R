#!/usr/bin/env Rscript
# release_checklist.R — Run the full pre-release gauntlet for an R package.
#
# Usage:  Rscript release_checklist.R [path/to/package]
#
# Runs, in order, the checks that must pass before a CRAN release:
#   1. devtools::check(cran = TRUE)   — 0 errors, 0 warnings
#   2. urlchecker::url_check()         — all URLs reachable
#   3. spelling::spell_check_package() — spelling clean
#   4. DESCRIPTION field validation    — required fields present
#   5. NEWS.md presence and current version match
#   6. Examples runnable               — confirmed by R CMD check above
#
# Exits 0 on success, 1 on any failure. Prints a coloured-ish summary.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

pkg_path <- normalizePath(pkg_path, mustWork = FALSE)
if (!dir.exists(pkg_path)) stop(sprintf("Directory not found: %s", pkg_path))

desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) {
  stop(sprintf("No DESCRIPTION file in %s — not an R package.", pkg_path))
}

need <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf(
      "Package '%s' required. Install with install.packages(\"%s\").",
      pkg, pkg
    ))
  }
}

need("devtools")
need("desc")

results <- list()
record <- function(name, ok, details = "") {
  results[[name]] <<- list(ok = ok, details = details)
  status <- if (ok) "PASS" else "FAIL"
  cat(sprintf("[%s] %s%s\n", status, name,
              if (nzchar(details)) paste0(" — ", details) else ""))
}

cat(sprintf("\n=== Release checklist: %s ===\n\n", pkg_path))

# ---- 1. devtools::check(cran = TRUE) ----
cat(">> Running R CMD check (cran = TRUE). This may take several minutes.\n")
check_result <- tryCatch(
  devtools::check(pkg_path, cran = TRUE, quiet = TRUE),
  error = function(e) e
)
if (inherits(check_result, "error")) {
  record("R CMD check", FALSE, conditionMessage(check_result))
} else {
  n_err <- length(check_result$errors)
  n_warn <- length(check_result$warnings)
  n_note <- length(check_result$notes)
  detail <- sprintf("%d errors, %d warnings, %d notes",
                    n_err, n_warn, n_note)
  record("R CMD check",
         n_err == 0L && n_warn == 0L,
         detail)
}

# ---- 2. urlchecker::url_check() ----
if (requireNamespace("urlchecker", quietly = TRUE)) {
  cat("\n>> Checking URLs...\n")
  url_result <- tryCatch(
    urlchecker::url_check(pkg_path),
    error = function(e) e
  )
  if (inherits(url_result, "error")) {
    record("URL check", FALSE, conditionMessage(url_result))
  } else {
    n_bad <- nrow(url_result)
    record("URL check", is.null(n_bad) || n_bad == 0L,
           if (!is.null(n_bad) && n_bad > 0L)
             sprintf("%d problematic URLs", n_bad) else "")
  }
} else {
  record("URL check", FALSE, "urlchecker not installed")
}

# ---- 3. spelling::spell_check_package() ----
if (requireNamespace("spelling", quietly = TRUE)) {
  cat("\n>> Checking spelling...\n")
  spell_result <- tryCatch(
    spelling::spell_check_package(pkg_path),
    error = function(e) e
  )
  if (inherits(spell_result, "error")) {
    record("Spelling", FALSE, conditionMessage(spell_result))
  } else {
    n_typos <- nrow(spell_result)
    record("Spelling", is.null(n_typos) || n_typos == 0L,
           if (!is.null(n_typos) && n_typos > 0L)
             sprintf("%d potential typos (review inst/WORDLIST)", n_typos)
           else "")
  }
} else {
  record("Spelling", FALSE, "spelling not installed")
}

# ---- 4. DESCRIPTION fields ----
cat("\n>> Validating DESCRIPTION fields...\n")
desc_obj <- desc::desc(file = desc_file)
required_fields <- c("Package", "Title", "Version", "Description",
                     "License", "Authors@R")
missing_fields <- character()
for (field in required_fields) {
  if (!desc_obj$has_fields(field)) {
    missing_fields <- c(missing_fields, field)
  }
}
recommended <- c("URL", "BugReports", "Encoding")
missing_recommended <- character()
for (field in recommended) {
  if (!desc_obj$has_fields(field)) {
    missing_recommended <- c(missing_recommended, field)
  }
}
record("Required DESCRIPTION fields",
       length(missing_fields) == 0L,
       if (length(missing_fields) > 0L)
         paste("missing:", paste(missing_fields, collapse = ", "))
       else "")
if (length(missing_recommended) > 0L) {
  cat(sprintf("[WARN] Missing recommended fields: %s\n",
              paste(missing_recommended, collapse = ", ")))
}

# Check version is not a dev version (no .9000 suffix)
ver <- as.character(desc_obj$get_version())
is_dev <- grepl("9000$", ver) || grepl("\\.9\\d+$", ver)
record("Release version (no .9000)",
       !is_dev,
       if (is_dev) sprintf("Version %s looks like a dev version", ver)
       else sprintf("Version %s", ver))

# ---- 5. NEWS.md ----
news_file <- file.path(pkg_path, "NEWS.md")
if (!file.exists(news_file)) {
  record("NEWS.md present", FALSE, "NEWS.md not found")
} else {
  news <- readLines(news_file, n = 20L, warn = FALSE)
  pkg_name <- desc_obj$get("Package")
  first_header <- grep("^# ", news, value = TRUE)[1]
  version_in_news <- grepl(
    paste0("^# ", pkg_name, " ", gsub("\\.", "\\\\.", ver), "\\s*$"),
    first_header %||% ""
  )
  record("NEWS.md present", TRUE)
  record("NEWS.md current version",
         isTRUE(version_in_news),
         if (!isTRUE(version_in_news))
           sprintf("Top entry '%s' does not match version %s",
                   first_header %||% "(none)", ver)
         else "")
}

# ---- 6. cran-comments.md ----
cran_comments <- file.path(pkg_path, "cran-comments.md")
record("cran-comments.md present", file.exists(cran_comments),
       if (!file.exists(cran_comments))
         "Missing — create before submission" else "")

# ---- Summary ----
cat("\n=== Summary ===\n")
n_pass <- sum(vapply(results, function(r) isTRUE(r$ok), logical(1)))
n_fail <- length(results) - n_pass
cat(sprintf("%d passed, %d failed of %d checks.\n",
            n_pass, n_fail, length(results)))

if (n_fail > 0L) {
  cat("\nBlockers:\n")
  for (name in names(results)) {
    if (!isTRUE(results[[name]]$ok)) {
      cat(sprintf("  * %s: %s\n", name, results[[name]]$details))
    }
  }
  cat("\nResult: NOT READY for CRAN.\n")
  quit(status = 1L)
}

cat("\nResult: READY for CRAN submission.\n")
cat("Next: update cran-comments.md, then run devtools::submit_cran().\n")
quit(status = 0L)
