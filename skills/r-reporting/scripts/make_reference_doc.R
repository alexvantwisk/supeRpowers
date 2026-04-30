## ============================================================================
## Script: make_reference_doc.R
## Description: Generate a Pandoc reference.docx with minimalist defaults for
##              Word output from R Quarto reports. Patches styles.xml (Normal,
##              Heading 1, Figure, Table, ImageCaption) and word/footer1.xml.
##
## Usage:       source(here::here("analysis", "make_reference_doc.R"))
##              # or with overrides:
##              make_reference_doc(
##                ref_path           = "report/reference.docx",
##                font               = "Calibri",
##                body_size_pt       = 11,
##                body_line          = "1.5",   # one of "1", "1.5", "2"
##                heading1_pagebreak = TRUE,
##                heading1_centered  = TRUE,
##                page_numbers       = TRUE
##              )
##
## R packages:  here, xml2, zip
## ============================================================================

suppressPackageStartupMessages({
  library(here)
  library(xml2)
})

make_reference_doc <- function(
  ref_path           = here::here("inst", "templates", "reference.docx"),
  font               = "Calibri",
  body_size_pt       = 11L,
  body_line          = "1.5",
  heading1_pagebreak = TRUE,
  heading1_centered  = TRUE,
  page_numbers       = TRUE
) {
  stopifnot(
    is.character(ref_path), length(ref_path) == 1L,
    is.character(font), length(font) == 1L,
    is.numeric(body_size_pt), body_size_pt >= 8L, body_size_pt <= 16L,
    body_line %in% c("1", "1.5", "2"),
    is.logical(heading1_pagebreak), is.logical(heading1_centered),
    is.logical(page_numbers)
  )

  ## -------------------------------------------------------------------------
  ## 1. Resolve a pandoc binary (prefer the one bundled with Quarto)
  ## -------------------------------------------------------------------------
  pandoc_bin <- Sys.which("pandoc")
  if (nzchar(pandoc_bin) == 0L) {
    quarto_bin <- Sys.which("quarto")
    if (nzchar(quarto_bin) == 0L) {
      stop("Neither pandoc nor quarto is on PATH; cannot generate reference doc.")
    }
    candidate <- file.path(dirname(quarto_bin), "tools", "pandoc")
    if (file.exists(candidate)) {
      pandoc_bin <- candidate
    } else {
      candidates <- list.files(
        file.path(dirname(quarto_bin), "tools"),
        pattern = "^pandoc$",
        recursive = TRUE,
        full.names = TRUE
      )
      if (length(candidates) > 0L) pandoc_bin <- candidates[[1]]
      else stop("Cannot locate pandoc binary alongside quarto.")
    }
  }
  message("Using pandoc: ", pandoc_bin)

  ## -------------------------------------------------------------------------
  ## 2. Extract Pandoc's default reference docx
  ## -------------------------------------------------------------------------
  dir.create(dirname(ref_path), recursive = TRUE, showWarnings = FALSE)
  if (file.exists(ref_path)) file.remove(ref_path)
  status <- system2(
    pandoc_bin,
    args = c("-o", shQuote(ref_path), "--print-default-data-file", "reference.docx"),
    stdout = "", stderr = "",
    wait = TRUE
  )
  if (status != 0L || !file.exists(ref_path)) {
    stop("pandoc --print-default-data-file failed (exit ", status, ").")
  }
  message("Extracted default reference.docx to: ", ref_path)

  ## -------------------------------------------------------------------------
  ## 3. Unzip into a temp work dir
  ## -------------------------------------------------------------------------
  work_dir <- tempfile("refdocx_")
  dir.create(work_dir)
  on.exit(unlink(work_dir, recursive = TRUE), add = TRUE)
  utils::unzip(ref_path, exdir = work_dir)

  ## -------------------------------------------------------------------------
  ## 4. Patch styles.xml
  ## -------------------------------------------------------------------------
  styles_path <- file.path(work_dir, "word", "styles.xml")
  stopifnot(file.exists(styles_path))

  ns <- c(w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
  styles <- xml2::read_xml(styles_path)

  line_value <- switch(body_line, `1` = "240", `1.5` = "360", `2` = "480")
  font_size_halfpt <- as.character(as.integer(body_size_pt) * 2L)

  patch_body_styling <- function(ppr) {
    for (existing in xml2::xml_find_all(ppr, "w:spacing", ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(ppr, "w:jc",      ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(ppr, "w:spacing", `w:line` = line_value, `w:lineRule` = "auto")
    xml2::xml_add_child(ppr, "w:jc",      `w:val`  = "both")
  }

  ensure_pPr <- function(parent) {
    pPr <- xml2::xml_find_first(parent, "w:pPr", ns)
    if (inherits(pPr, "xml_missing")) {
      pPr <- xml2::xml_add_child(parent, "w:pPr", .where = 0L)
    }
    pPr
  }

  ensure_rPr <- function(parent) {
    rPr <- xml2::xml_find_first(parent, "w:rPr", ns)
    if (inherits(rPr, "xml_missing")) {
      rPr <- xml2::xml_add_child(parent, "w:rPr")
    }
    rPr
  }

  # 4a. Body — patch BOTH docDefaults and Normal style
  doc_default_ppr <- xml2::xml_find_first(
    styles, "//w:docDefaults/w:pPrDefault/w:pPr", ns
  )
  if (!inherits(doc_default_ppr, "xml_missing")) patch_body_styling(doc_default_ppr)

  doc_default_rpr <- xml2::xml_find_first(
    styles, "//w:docDefaults/w:rPrDefault/w:rPr", ns
  )
  if (!inherits(doc_default_rpr, "xml_missing")) {
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:rFonts", ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:sz",      ns)) xml2::xml_remove(existing)
    for (existing in xml2::xml_find_all(doc_default_rpr, "w:szCs",    ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(doc_default_rpr, "w:rFonts",
                        `w:ascii` = font, `w:hAnsi` = font, `w:cs` = font)
    xml2::xml_add_child(doc_default_rpr, "w:sz",   `w:val` = font_size_halfpt)
    xml2::xml_add_child(doc_default_rpr, "w:szCs", `w:val` = font_size_halfpt)
  }

  normal <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Normal']", ns)
  if (inherits(normal, "xml_missing")) {
    stop("Normal style not found in reference.docx styles.xml.")
  }
  patch_body_styling(ensure_pPr(normal))

  # 4b. Heading 1 — page break + center
  heading1 <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Heading1']", ns)
  if (!inherits(heading1, "xml_missing")) {
    h1_ppr <- ensure_pPr(heading1)
    if (heading1_pagebreak) {
      for (existing in xml2::xml_find_all(h1_ppr, "w:pageBreakBefore", ns)) xml2::xml_remove(existing)
      xml2::xml_add_child(h1_ppr, "w:pageBreakBefore")
    }
    if (heading1_centered) {
      for (existing in xml2::xml_find_all(h1_ppr, "w:jc", ns)) xml2::xml_remove(existing)
      xml2::xml_add_child(h1_ppr, "w:jc", `w:val` = "center")
    }
  }

  # 4c. Figure — center
  figure <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Figure']", ns)
  if (!inherits(figure, "xml_missing")) {
    fig_ppr <- ensure_pPr(figure)
    for (existing in xml2::xml_find_all(fig_ppr, "w:jc", ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(fig_ppr, "w:jc", `w:val` = "center")
  }

  # 4d. Table — center (paragraph style on Pandoc-emitted Table style if present)
  tbl <- xml2::xml_find_first(styles, "//w:style[@w:styleId='Table']", ns)
  if (!inherits(tbl, "xml_missing")) {
    tbl_ppr <- ensure_pPr(tbl)
    for (existing in xml2::xml_find_all(tbl_ppr, "w:jc", ns)) xml2::xml_remove(existing)
    xml2::xml_add_child(tbl_ppr, "w:jc", `w:val` = "center")
  }

  xml2::write_xml(styles, styles_path)

  # 4e. Sanity check — re-read and confirm parses
  invisible(xml2::read_xml(styles_path))
  message("Patched styles.xml.")

  ## -------------------------------------------------------------------------
  ## 5. Patch footer1.xml — minimalist centered page number
  ## -------------------------------------------------------------------------
  if (page_numbers) {
    footer_path <- file.path(work_dir, "word", "footer1.xml")
    if (file.exists(footer_path)) {
      footer_xml <- sprintf(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="Footer"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:fldSimple w:instr=" PAGE \\* MERGEFORMAT ">
      <w:r><w:t>1</w:t></w:r>
    </w:fldSimple>
  </w:p>
</w:ftr>'
      )
      writeLines(footer_xml, footer_path, useBytes = TRUE)
      invisible(xml2::read_xml(footer_path))   # sanity check parses
      message("Patched footer1.xml (centered page number).")
    } else {
      message("No footer1.xml in template; skipping page number patch.")
    }
  }

  ## -------------------------------------------------------------------------
  ## 6. Re-zip into the final reference.docx
  ## -------------------------------------------------------------------------
  unlink(ref_path)

  if (requireNamespace("zip", quietly = TRUE)) {
    entries <- list.files(work_dir, recursive = TRUE, all.files = TRUE,
                          include.dirs = FALSE, no.. = TRUE)
    zip::zip(zipfile = ref_path, files = entries, root = work_dir, mode = "mirror")
  } else {
    if (!nzchar(Sys.which("zip"))) {
      stop("Need either the `zip` R package or a system `zip` binary on PATH.")
    }
    old_wd <- setwd(work_dir)
    on.exit(setwd(old_wd), add = TRUE, after = FALSE)
    status <- system2("zip", c("-rq", shQuote(ref_path), "."))
    if (status != 0L) stop("system zip failed (exit ", status, ").")
  }

  message("Wrote: ", ref_path)
  invisible(ref_path)
}

# When sourced (not loaded as a function), invoke with defaults.
if (!exists(".reporting_test_skip_run", inherits = FALSE)) {
  if (sys.nframe() == 0L || identical(sys.function(1L), make_reference_doc)) {
    # script-mode invocation
    make_reference_doc()
  }
}
