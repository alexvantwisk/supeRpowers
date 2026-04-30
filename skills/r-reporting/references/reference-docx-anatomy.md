# Reference.docx Anatomy

Deep-dive reference for patching a Pandoc `reference.docx`. This file provides
the XML internals, unit conversions, and verbatim R code.

## Why a reference.docx?

Pandoc applies paragraph and character styles from a template Word file. Without
a `reference-doc:` key, Pandoc uses its built-in default — single spacing,
left-aligned figures, no page breaks before headings, blank footer. That default
is intentionally minimal. The only practical path to 1.5 line spacing, full
justification, Heading 1 page breaks, centered figures and tables, and a
page-number footer is to supply a patched `reference.docx`. Pandoc strips
`\centering` and alignment markup from `.qmd` files for docx output; patching
is the only lever.

## The docx Is a Zip Archive

A `.docx` file is a ZIP archive (Open Packaging Convention). Relevant internal
entries:

```
[Content_Types].xml       MIME type registry
_rels/.rels               package-level relationships
word/styles.xml           all named paragraph and character styles  ← patch here
word/footer1.xml          primary footer (page numbers)            ← patch here
word/header1.xml          primary header
word/document.xml         document body
docProps/core.xml         author, created date
```

The three files you patch are `word/styles.xml` and `word/footer1.xml` (and
`word/document.xml` for margin overrides). Everything else is off limits.

**Never flatten when re-zipping.** If you `unzip()` into a temp dir and re-zip
from R's working directory, entry paths will include the temp dir prefix and
Word will reject the file. Use `mode = "mirror"` when calling `zip::zip()` —
it mirrors the source tree so entries are stored without the prefix.

## Measurement Units Cheat Sheet

Word XML uses three distinct unit systems. Getting them wrong produces silently
wrong output.

| Property | Unit | Key values |
|---|---|---|
| Line spacing (`w:line`) | Twentieths of a point | 240 = single, 360 = 1.5×, 480 = double |
| Paragraph spacing-before/after | Twentieths of a point | 240 = 12 pt |
| Page margins, indents | Twips (1/1440 in = 1/20 pt) | 1440 = 1 inch |
| Font size (`w:sz`, `w:szCs`) | Half-points | 22 = 11 pt, 24 = 12 pt |

`w:lineRule="auto"` means "leading" (a multiple of 240 per line) — the standard
mode. `"exact"` fixes spacing regardless of content height; `"atLeast"` expands
when content is taller. Always use `"auto"` for body text.

## Pandoc-Relevant Styles

Pandoc maps each markdown element to a named Word style. Verified empirically
by rendering a sample `.qmd` and inspecting the output `.docx`.

| Markdown element | Word style (`w:styleId`) |
|---|---|
| Body paragraph | `Normal` |
| `# Heading 1` | `Heading1` |
| `> blockquote` | `BlockText` |
| Image paragraph | `Figure` |
| Image caption | `ImageCaption` |
| Table caption | `TableCaption` |
| Table cells | `Table` |
| Code block | `SourceCode` |
| List items | `Compact` / `BodyText` |
| TOC entries | `TOC1`–`TOC4` |

For the five style invariants, only `Normal`, `docDefaults`, `Heading1`,
`Figure`, `Table`, and `footer1.xml` need patching.

## The Two Body-Styling Patch Targets

Patching the `Normal` style alone is not sufficient. Many Pandoc-emitted
paragraphs — image paragraphs, blank separator paragraphs, some list items —
have empty `<w:pPr>` blocks with no `<w:pStyle>` element. Word resolves those
through `docDefaults/pPrDefault`, not `Normal`.

Patch **both** locations for guaranteed coverage:

1. `w:docDefaults/w:pPrDefault/w:pPr` — baseline for un-styled paragraphs.
2. `w:style[@w:styleId='Normal']/w:pPr` — the explicit Normal style.

## The Five Style Invariants and Their XML

### Body: 1.5× + Justify + Calibri 11pt

Apply to both `docDefaults/pPrDefault/pPr` and `Normal/pPr` (paragraph nodes),
and to `docDefaults/rPrDefault/rPr` and `Normal/rPr` (run nodes).

```xml
<!-- Paragraph properties -->
<w:spacing w:line="360" w:lineRule="auto"/>
<w:jc w:val="both"/>

<!-- Run (character) properties -->
<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
<w:sz w:val="22"/>
<w:szCs w:val="22"/>
```

`w:val="both"` is Word's "Justify". `w:szCs` sets font size for complex scripts
(Arabic, Hebrew, CJK); omit it and you get inconsistent sizing in mixed-script
documents.

### Heading 1: Page Break + Center + Bold

Apply to `w:style[@w:styleId='Heading1']/w:pPr` and `.../w:rPr`.

```xml
<!-- Paragraph properties -->
<w:pageBreakBefore/>
<w:jc w:val="center"/>

<!-- Run properties -->
<w:b/>
<w:bCs/>
```

`<w:pageBreakBefore/>` is a boolean element; its presence forces a new page.
`<w:bCs/>` applies bold to complex scripts.

### Figure: Center

Apply to `w:style[@w:styleId='Figure']/w:pPr`.

```xml
<w:jc w:val="center"/>
```

### Table: Center

Apply to `w:style[@w:styleId='Table']/w:pPr`.

```xml
<w:jc w:val="center"/>
```

Defense in depth alongside flextable's `align = "center"`.

### Footer: Page Number Only

In `word/footer1.xml`, replace the body paragraph with:

```xml
<w:p>
  <w:pPr><w:jc w:val="center"/></w:pPr>
  <w:fldSimple w:instr=" PAGE \* MERGEFORMAT ">
    <w:r><w:t>1</w:t></w:r>
  </w:fldSimple>
</w:p>
```

`w:fldSimple` is a paragraph-level element that wraps `w:r` children — it cannot
nest inside `w:r`. The leading and trailing spaces inside `w:instr` are required.
For "Page X of Y", append a second `fldSimple` with
`instr=" NUMPAGES \* MERGEFORMAT "` after a literal ` of ` run.

## The xml2 Patching Idiom

The pattern: read XML, locate the target node, strip conflicting children, add
new children, write back.

```r
ns <- c(w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
styles <- xml2::read_xml(styles_path)
normal_ppr <- xml2::xml_find_first(
  styles, "//w:style[@w:styleId='Normal']/w:pPr", ns
)
xml2::xml_remove(xml2::xml_find_all(normal_ppr, "w:spacing", ns))
xml2::xml_remove(xml2::xml_find_all(normal_ppr, "w:jc", ns))
xml2::xml_add_child(normal_ppr, "w:spacing", `w:line` = "360", `w:lineRule` = "auto")
xml2::xml_add_child(normal_ppr, "w:jc", `w:val` = "both")
xml2::write_xml(styles, styles_path)
```

Note the backtick quoting — `` `w:line` = "360" `` — because colons make
attribute names non-syntactic in R. Omitting the backticks causes
`formal argument "w" matched by multiple actual arguments`.

Heading 1 page break:

```r
h1_ppr <- xml2::xml_find_first(
  styles, "//w:style[@w:styleId='Heading1']/w:pPr", ns
)
xml2::xml_remove(xml2::xml_find_all(h1_ppr, "w:pageBreakBefore", ns))
xml2::xml_add_child(h1_ppr, "w:pageBreakBefore")
xml2::xml_add_child(h1_ppr, "w:jc", `w:val` = "center")
```

Footer patching:

```r
footer <- xml2::read_xml(footer_path)
purrr::walk(xml2::xml_find_all(footer, "//w:p", ns), xml2::xml_remove)
body <- xml2::xml_find_first(footer, "//w:body", ns)
p_node <- xml2::xml_add_child(body, "w:p")
ppr_node <- xml2::xml_add_child(p_node, "w:pPr")
xml2::xml_add_child(ppr_node, "w:jc", `w:val` = "center")
fld_node <- xml2::xml_add_child(p_node, "w:fldSimple", `w:instr` = " PAGE \\* MERGEFORMAT ")
r_node <- xml2::xml_add_child(fld_node, "w:r")
xml2::xml_add_child(r_node, "w:t", "1")
xml2::write_xml(footer, footer_path)
```

## The Namespace Map

```r
ns <- c(w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
```

Without this binding, every `xml_find_first()` / `xml_find_all()` call returns
`NULL` or an empty node set — silently, with no error. This is the most common
source of "my patches aren't doing anything" bugs. The `w` namespace URI is
fixed for Word 2007+ (OOXML); hard-code it, do not inspect the document.

Always pass `ns` as the third argument to every xpath call.

## Sanity Check After Patching

After every `xml2::write_xml()`, immediately re-read the file to confirm it
still parses. A truncation or encoding error can corrupt the patch silently.

```r
tryCatch(
  xml2::read_xml(styles_path),
  error = function(e) stop(paste("Patched XML is invalid:", conditionMessage(e)))
)
```

Abort and surface the error rather than re-zipping a corrupt archive. Word opens
corrupt docx files with a "repaired content" dialog that silently drops your
style changes.

## Re-Zipping

Three options, in preference order:

**(a) `zip::zip()` with `mode = "mirror"` — recommended.**

```r
entries <- list.files(work_dir, recursive = TRUE, full.names = FALSE)
zip::zip(zipfile = output_path, files = entries, root = work_dir, mode = "mirror")
```

`mode = "mirror"` stores entries relative to `root`, preserving the directory
tree. `zip` is a hard dependency of `officer` so it is almost always available.

**(b) System `zip` binary — macOS/Linux only.**

```r
system2("zip", args = c("-rq", shQuote(output_path), "."),
        stdout = FALSE, stderr = FALSE, wd = work_dir)
```

Fails silently on Windows without Info-ZIP. Not safe for cross-platform scripts.

**(c) `utils::zip()` — avoid.** Does not expose `mode`; directory-entry
handling varies by platform and R version.

## What NOT to Patch

Do not modify these files — touching them can corrupt the docx silently:

- `_rels/.rels` — package-level relationships. Altering targets or IDs breaks
  the package structure.
- `[Content_Types].xml` — MIME type registry. Removing a content type causes
  Word to discard the corresponding part.
- `docProps/core.xml` — author and revision metadata. Word rewrites this on
  every save; patching it achieves nothing and can introduce encoding conflicts.

Patch only `word/styles.xml`, `word/footer1.xml`, and (for margin overrides)
`word/document.xml`.
