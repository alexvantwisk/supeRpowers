# Creating Quarto Templates & Extensions

How to *author* reusable templates in Quarto, as opposed to *using* installed
ones. Anchored to Quarto 1.5+. Confirm feature availability with `quarto check`.

Quarto has two distinct customization mechanisms, chosen by output format:

| Format family | Mechanism | Key |
|---|---|---|
| `docx`, `pptx`, `odt` | A **reference document** (a real Office file whose styles Pandoc copies) | `reference-doc:` |
| `html`, `pdf` (LaTeX), `typst`, `revealjs` | **Pandoc templates & partials** (text templates with `$variable$` slots) | `template:`, `template-partials:` |

You cannot use `template-partials:` for docx/pptx — those formats have no text
template, only a reference doc. This is the single most common point of confusion.

---

## 1. Reference documents (docx / pptx / odt)

Word, PowerPoint, and OpenDocument outputs are styled by copying named styles
out of a reference file. The workflow is always: **generate a starting file →
edit its styles in the Office app → wire it in via YAML**.

### Generate a starting reference file

```bash
# Word
quarto pandoc -o custom-reference.docx --print-default-data-file reference.docx

# PowerPoint
quarto pandoc -o custom-reference.pptx --print-default-data-file reference.pptx
```

`quarto pandoc` forwards to the Pandoc bundled with Quarto, so the reference
file matches the Pandoc version that will render your document. `--print-default-data-file`
emits Pandoc's built-in neutral template. (Pandoc also supports `reference.odt`
for OpenDocument the same way, but Quarto's own docs don't document that path —
treat it as Pandoc-level pass-through.)

**PowerPoint differs from Word.** For `.pptx` it is **slide layouts** by name,
not paragraph styles, that Pandoc matches against. The reference deck must keep
layouts named `Title Slide`, `Title and Content`, `Section Header`, `Two
Content`, `Comparison`, `Content with Caption`, and `Blank`. Rename or delete
one and Pandoc warns and falls back to the default deck's layout of that name.
Edit these via View → Slide Master in PowerPoint.

### Edit the styles that matter

Open the generated file in Word/PowerPoint and modify the **named styles** (not
ad-hoc formatting on a paragraph — Pandoc only copies style *definitions*). The
styles Pandoc maps markdown onto:

| Markdown element | Word style |
|---|---|
| Body paragraph | `Body Text` / `Normal` |
| `# … ###### Heading` | `Heading 1`–`Heading 6` |
| `> blockquote` | `Block Text` |
| Image | `Figure` |
| Image caption | `Image Caption` |
| Table caption | `Table Caption` |
| Table body | `Table` (a table style) |
| Code block | `Source Code` |
| Fenced div `.foo` (custom) | a paragraph style named `foo`, if it exists |

Page margins, headers, footers, and page size come from the reference file's
**section properties** — set them in Word (Layout → Margins; Insert → Page
Number) and they carry through. Save when done.

### Wire it in

```yaml
format:
  docx:
    reference-doc: custom-reference.docx   # resolved relative to the qmd
  pptx:
    reference-doc: custom-slides.pptx
```

In a project, put it under `format:` in `_quarto.yml` so every document
inherits it. Commit the reference file.

### Two paths for Word — pick by reproducibility need

- **Edit-in-Word (this section).** Fastest for a one-off or a template a
  non-programmer will maintain. The reference file is a binary artifact; changes
  are made by hand in Word.
- **Programmatic XML patching.** When the styling must be reproducible,
  diff-able, parameterised, or regenerated in CI, patch `word/styles.xml` inside
  the docx zip with `xml2` instead of editing in Word. See
  `reference-docx-anatomy.md` for the OOXML unit systems, which styles to patch
  (Normal, docDefaults, Heading 1, Figure, Table, footer), the xml2 idiom, and
  the `zip::zip(mode = "mirror")` re-zip requirement. For the *content* and
  *project pipeline* of a consulting/clinical Word deliverable (report sections,
  estimands, the RDS-cache orchestration, the `/r-report` scaffold), use
  **r-reporting**.

---

## 2. Custom format extensions (`quarto create extension`)

A **format extension** bundles a reference doc (or template/partials), default
metadata, filters, and styling into a reusable, distributable unit under
`_extensions/`. This is how you turn "our house Word style" or "our slide
theme" into something teammates install with one command.

### Scaffold

```bash
quarto create extension format:docx      # Word format extension
quarto create extension format:html      # HTML
quarto create extension format:pdf       # LaTeX PDF
quarto create extension format:revealjs  # slides
```

Those four are the documented `format:<x>` shorthands. For a **Typst** format
extension, run `quarto create extension format` (no `:type`) and pick `typst`
from the interactive base-format list. There is no `journal` create type —
journal formats are ordinary format extensions, authored the same way and shared
via `quarto use template` / `quarto add`. The scaffold creates:

```
my-report/
  _extensions/
    my-report/
      _extension.yml     # extension manifest
      <style assets>     # e.g. reference-doc, .scss, .tex partials
  template.qmd           # example document that USES the extension
  README.md
```

### The `_extension.yml` manifest

```yaml
title: My Report
author: Data Science Team
version: 1.0.0
quarto-required: ">=1.5.0"
contributes:
  formats:
    docx:
      reference-doc: my-report-reference.docx
      toc: true
      number-sections: true
```

Everything under `contributes.formats.<base-format>` is merged into any document
that selects the extension. (Current Quarto docs use both `contributes: formats:`
plural and `contributes: format:` singular across pages — both are accepted;
don't "fix" one to the other.)

Bundling a reference doc: the documented pages don't spell out a docx-extension
recipe, but the extension mechanics make it straightforward — drop the `.docx`
inside `_extensions/<name>/` beside `_extension.yml` and point `reference-doc:`
at it by name (paths resolve relative to the extension directory).

### Use the extension

Within the scaffold, `template.qmd` already selects it. In any project that has
installed the extension, select it as `<extension-name>-<base-format>`:

```yaml
format:
  my-report-docx: default
```

The `-docx` suffix tells Quarto which base format the extension refines.

---

## 3. Starting from a template: `quarto use` vs `quarto add`

| Command | What it does | When |
|---|---|---|
| `quarto add <gh-org>/<repo>` | Installs the extension into `_extensions/` of the **current** project. No example files. | You already have a document and just want the format available. |
| `quarto use template <gh-org>/<repo>` | Creates a **new directory** seeded with the extension *and* its example `.qmd`, ready to render. | Starting a fresh document from someone's template. |

```bash
quarto use template quarto-journals/jss     # new project from the JSS template
quarto add quarto-journals/jss              # add JSS format to an existing project
```

Both write to `_extensions/` — commit that directory so collaborators and CI
get the same template without a network fetch.

`quarto use template` copies the repo but skips hidden dot-files, GitHub
metadata (`README.md`, `LICENSE`), and AI config files (`CLAUDE.md`,
`AGENTS.md`), then auto-renames the repo's `template.qmd` to match the new
directory. List extra exclusions in a `.quartoignore` (gitignore-style globs) at
the template repo root.

---

## 4. Template partials & full templates (html / pdf / typst / revealjs)

For text-template formats you can override *parts* of Pandoc's template
(partials) or replace it entirely.

```yaml
format:
  html:
    template-partials:
      - title-block.html      # override just the title block
      - toc.html
  pdf:
    template-partials:
      - before-body.tex
    include-in-header: preamble.tex   # inject without replacing the template
  typst:
    template-partials:
      - typst-template.typ    # layout / styling
      - typst-show.typ        # how the doc body is placed into the template
```

- **`template-partials:`** — override named sub-templates while keeping
  Quarto's overall structure. Preferred: you inherit future Quarto improvements.
- **`template:`** — replace Pandoc's entire template. Maximum control, but you
  own all of Quarto's scaffolding (dependencies, TOC, code highlighting) and
  must maintain it across Quarto upgrades. Avoid unless a journal demands it.
- **`include-in-header` / `include-before-body` / `include-after-body`** — the
  lightest touch: splice a fragment in without touching the template at all.

Get the current default partials to edit from as a starting point:

```bash
quarto pandoc --print-default-template=html   # or latex, typst
```

### Typst specifics

Typst extensions center on two partials: `typst-template.typ` (defines a `#show`
rule / page layout / fonts) and `typst-show.typ` (calls the template function
with the document's metadata and body). A Typst format extension bundles these
under `contributes.formats.typst`. Typst also honors `_brand.yml` for shared
colours, fonts, and logo across html/typst/revealjs/dashboard — reach for
brand.yml first if all you need is consistent branding, and only build a Typst
template when you need custom page structure.

---

## 5. Distributing a template

An extension is just a directory. Distribution options:

1. **GitHub (most common).** Push the repo with `_extensions/<name>/` at its
   root (or under a subdirectory named in the repo). Users run
   `quarto add <org>/<repo>` or `quarto use template <org>/<repo>`. Tag releases
   so `quarto add <org>/<repo>@v1.2.0` can pin a version.
2. **Within an R package.** Ship the `_extensions/` tree under `inst/` and copy
   it into a user's project from your package's setup helper.
3. **Committed in a monorepo.** Teams keep house templates in `_extensions/`
   checked into every analysis repo, or in a shared repo added as a git submodule.

Manifest hygiene for shared extensions: set a real `version`, an honest
`quarto-required` floor (test it), and keep `contributes.formats` minimal —
only the keys you genuinely want to force. Anything you set there overrides the
user's document, so default-on options can surprise people.

---

## Gotchas

| Trap | Why | Fix |
|---|---|---|
| `template-partials:` under `format: docx` | docx has no text template | Use `reference-doc:`; partials are html/pdf/typst/revealjs only |
| Editing a paragraph directly in Word instead of the style | Pandoc copies *style definitions*, not local formatting | Modify the named style (Heading 1, Body Text, Figure…) |
| Reference doc from `install.packages()` or a random Word file | Style set won't match Pandoc's expected style names | Generate with `quarto pandoc --print-default-data-file reference.docx` |
| Extension selected as `format: docx` when it's an extension | Quarto loads the base format, ignores the extension | Select `format: <extension-name>-docx` |
| `_extensions/` in `.gitignore` | Collaborators/CI lose the template | Commit `_extensions/` |
| Full `template:` replacement then Quarto upgrade breaks output | You own the whole template now | Prefer `template-partials:` or `include-in-header:` |
