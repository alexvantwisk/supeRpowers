#!/usr/bin/env bash
# Smoke test: scaffold a minimal docx report into a temp directory and render it.
# Skipped if the Quarto CLI is not on PATH or Rscript is unavailable.
#
# Usage: bash tests/smoke_r_report.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v quarto >/dev/null 2>&1; then
  echo "SKIP: Quarto CLI not on PATH"
  exit 0
fi
if ! command -v Rscript >/dev/null 2>&1; then
  echo "SKIP: Rscript not on PATH"
  exit 0
fi

WORK="$(mktemp -d -t rrep_smoke_XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

echo "Smoke test working dir: $WORK"
cd "$WORK"

mkdir -p inst/templates output/figures output/tables

cp "$ROOT/skills/r-reporting/scripts/report_template.qmd" inst/templates/report.qmd
cp "$ROOT/skills/r-reporting/scripts/make_reference_doc.R" inst/templates/make_reference_doc.R
cp "$ROOT/skills/r-reporting/scripts/render_to_docx.R" inst/templates/render_to_docx.R

# Minimal _quarto.yml
cat > _quarto.yml <<'YML'
project:
  type: default
  render:
    - inst/templates/report.qmd
  execute-dir: project
  resources:
    - "output/figures/*.png"
    - "output/tables/*.html"
YML

# Substitute placeholders in the qmd
sed -i.bak 's|{{report_title}}|Smoke Test Report|; s|{{author}}|smoke|' inst/templates/report.qmd
rm -f inst/templates/report.qmd.bak

# Generate reference.docx
Rscript -e 'source("inst/templates/make_reference_doc.R"); make_reference_doc(ref_path = "inst/templates/reference.docx")'

if [ ! -s inst/templates/reference.docx ]; then
  echo "FAIL: reference.docx not generated"
  exit 1
fi

# Render
Rscript -e 'source("inst/templates/render_to_docx.R"); render_to_docx(input_qmd = "inst/templates/report.qmd", output_dir = "output")'

# Assert non-empty docx in output/
docx_count=$(find output -maxdepth 1 -type f -name '*.docx' | wc -l | tr -d ' ')
if [ "$docx_count" -lt 1 ]; then
  echo "FAIL: no docx produced in output/"
  exit 1
fi

docx_path=$(find output -maxdepth 1 -type f -name '*.docx' | head -n 1)
docx_size=$(wc -c < "$docx_path")
if [ "$docx_size" -lt 8000 ]; then
  echo "FAIL: docx suspiciously small ($docx_size bytes): $docx_path"
  exit 1
fi

echo "PASS: docx produced at $docx_path ($docx_size bytes)"
