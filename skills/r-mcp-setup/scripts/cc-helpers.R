# cc-helpers.R — IDE-awareness helpers for Claude Code
# Source from .Rprofile to make these available in interactive R sessions.
# Pairs with mcp_session() from the mcptools package to close the gap with
# Positron Assistant.

`%||%` <- function(a, b) if (is.null(a)) b else a

cc_plot <- function(name = NULL, width = 8, height = 5, dpi = 120) {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("Package ggplot2 is required. Install with: install.packages(\"ggplot2\")")
  }
  dir <- ".claude/scratch/plots"
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  name <- name %||% format(Sys.time(), "%Y%m%d-%H%M%S")
  path <- file.path(dir, paste0(name, ".png"))
  ggplot2::ggsave(path, width = width, height = height, dpi = dpi)
  message("Plot saved: ", path)
  invisible(path)
}

cc_env <- function() {
  if (!requireNamespace("purrr", quietly = TRUE) ||
      !requireNamespace("tibble", quietly = TRUE)) {
    stop("Packages purrr and tibble are required. ",
         "Install with: install.packages(c(\"purrr\", \"tibble\"))")
  }
  objs <- ls(envir = .GlobalEnv)
  if (!length(objs)) {
    cat("(empty)\n")
    return(invisible(NULL))
  }
  out <- purrr::map_dfr(objs, function(x) {
    o <- get(x, envir = .GlobalEnv)
    tibble::tibble(
      name  = x,
      class = paste(class(o), collapse = "/"),
      dim   = if (!is.null(dim(o))) paste(dim(o), collapse = "x") else as.character(length(o)),
      mem   = format(utils::object.size(o), units = "auto")
    )
  })
  print(out, n = Inf)
  invisible(out)
}

cc_view <- function(x, n = 50) {
  nm <- deparse(substitute(x))
  dir <- ".claude/scratch"
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  path <- file.path(dir, paste0(nm, ".csv"))
  utils::write.csv(utils::head(x, n), path, row.names = FALSE)
  message("Preview saved: ", path, " (", nrow(x), " rows total)")
  invisible(path)
}
