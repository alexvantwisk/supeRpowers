#!/usr/bin/env python3
"""
Scan an R package repository and produce a structured inventory.

Usage:
    python3 scan_r_package.py /path/to/package [--output pkg-inventory.json]

Outputs a JSON file with package metadata, exported functions, file counts,
dependencies, class systems, and vignette information.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_description(pkg_path: Path) -> dict:
    """Parse the DESCRIPTION file into a dict of fields."""
    desc_file = pkg_path / "DESCRIPTION"
    if not desc_file.exists():
        print(f"ERROR: No DESCRIPTION file found in {pkg_path}", file=sys.stderr)
        sys.exit(1)

    fields = {}
    current_key = None
    current_value = []

    with open(desc_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # Continuation line (starts with whitespace)
            if line.startswith((" ", "\t")) and current_key:
                current_value.append(line.strip())
            else:
                # Save previous field
                if current_key:
                    fields[current_key] = " ".join(current_value)
                # Parse new field
                match = re.match(r"^([A-Za-z][A-Za-z0-9_.]*)\s*:\s*(.*)", line)
                if match:
                    current_key = match.group(1)
                    current_value = [match.group(2).strip()]
                else:
                    current_key = None
                    current_value = []

        # Save last field
        if current_key:
            fields[current_key] = " ".join(current_value)

    return fields


def parse_namespace(pkg_path: Path) -> dict:
    """Parse NAMESPACE for exports, S3/S4 methods, imports."""
    ns_file = pkg_path / "NAMESPACE"
    result = {
        "exports": [],
        "s3_methods": [],
        "s4_methods": [],
        "s4_classes": [],
        "imports": [],
        "import_from": {},
    }

    if not ns_file.exists():
        return result

    with open(ns_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Remove comments
    content = re.sub(r"#.*", "", content)

    # export(name) or export(name1, name2, name3)
    # Handle multi-line by collapsing: find all export(...) blocks
    raw_exports = re.findall(r"export\(([^)]+)\)", content)
    for block in raw_exports:
        # Split on commas to handle export(foo, bar, baz)
        items = [item.strip().strip('"').strip("'") for item in block.split(",")]
        result["exports"].extend(item for item in items if item)

    # exportPattern
    patterns = re.findall(r'exportPattern\("?([^)"]+)"?\)', content)

    # S3method(generic, class)
    s3 = re.findall(r"S3method\(([^,]+),\s*([^)]+)\)", content)
    result["s3_methods"] = [f"{g.strip()}.{c.strip()}" for g, c in s3]

    # S4 exports
    result["s4_methods"] = re.findall(r"exportMethods\(([^)]+)\)", content)
    result["s4_classes"] = re.findall(r"exportClasses\(([^)]+)\)", content)

    # import(pkg)
    result["imports"] = re.findall(r"(?<!\w)import\(([^)]+)\)", content)

    # importFrom(pkg, fn1, fn2)
    import_froms = re.findall(r"importFrom\(([^)]+)\)", content)
    for entry in import_froms:
        parts = [p.strip().strip('"').strip("'") for p in entry.split(",")]
        if len(parts) >= 2:
            pkg = parts[0]
            fns = parts[1:]
            result["import_from"].setdefault(pkg, []).extend(fns)

    # Handle exportPattern (e.g., "^[[:alpha:]]+" means export everything)
    if patterns:
        result["export_patterns"] = patterns

    return result


def scan_directory(pkg_path: Path, subdir: str) -> dict:
    """Count files and total lines in a subdirectory."""
    dir_path = pkg_path / subdir
    if not dir_path.exists():
        return {"exists": False, "file_count": 0, "total_lines": 0, "files": []}

    files = []
    total_lines = 0
    for f in sorted(dir_path.rglob("*")):
        if f.is_file():
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    line_count = sum(1 for _ in fh)
            except Exception:
                line_count = 0
            total_lines += line_count
            files.append({
                "path": str(f.relative_to(pkg_path)),
                "lines": line_count,
                "size_bytes": f.stat().st_size,
            })

    return {
        "exists": True,
        "file_count": len(files),
        "total_lines": total_lines,
        "files": files,
    }


def detect_class_systems(pkg_path: Path) -> dict:
    """Detect which OOP class systems are used."""
    r_dir = pkg_path / "R"
    systems = {"S3": False, "S4": False, "R6": False, "R7": False}

    if not r_dir.exists():
        return systems

    for f in r_dir.glob("*.R"):
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception:
            continue

        if re.search(r"UseMethod\(", content):
            systems["S3"] = True
        if re.search(r"setClass\(|setGeneric\(|setMethod\(", content):
            systems["S4"] = True
        if re.search(r"R6Class\(|R6::R6Class\(", content):
            systems["R6"] = True
        if re.search(r"new_class\(|S7::new_class\(", content):
            systems["R7"] = True

    return systems


def parse_dependencies(desc_fields: dict) -> dict:
    """Extract package dependencies from DESCRIPTION fields."""
    deps = {}
    for field in ["Depends", "Imports", "Suggests", "LinkingTo", "Enhances"]:
        raw = desc_fields.get(field, "")
        if not raw:
            deps[field.lower()] = []
            continue
        # Split on commas, handling version specs in parens
        items = re.split(r",\s*(?![^(]*\))", raw)
        cleaned = []
        for item in items:
            item = item.strip()
            if item:
                # Extract package name (before any version spec)
                pkg_match = re.match(r"([A-Za-z][A-Za-z0-9_.]*)", item)
                if pkg_match:
                    cleaned.append(item)
        deps[field.lower()] = cleaned

    return deps


def extract_vignette_titles(pkg_path: Path) -> list:
    """Extract vignette titles from vignette files."""
    vignettes = []
    vig_dir = pkg_path / "vignettes"
    if not vig_dir.exists():
        return vignettes

    for f in sorted(vig_dir.glob("*")):
        if f.suffix in (".Rmd", ".Rnw", ".qmd", ".md"):
            title = f.stem
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read(2000)
                # YAML frontmatter title
                yaml_match = re.search(r"title:\s*[\"']?(.+?)[\"']?\s*$", content, re.MULTILINE)
                if yaml_match:
                    title = yaml_match.group(1).strip()
                # Sweave VignetteTitle
                sweave_match = re.search(r"%\\VignetteIndexEntry\{(.+?)\}", content)
                if sweave_match:
                    title = sweave_match.group(1).strip()
            except Exception:
                pass
            vignettes.append({"file": f.name, "title": title})

    return vignettes


def extract_function_signatures(pkg_path: Path, exports: list) -> list:
    """Extract function signatures from R source files for exported functions."""
    r_dir = pkg_path / "R"
    signatures = {}

    if not r_dir.exists():
        return []

    for f in sorted(r_dir.glob("*.R")):
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except Exception:
            continue

        # Two-pass approach for multi-line function definitions:
        # First find "name <- function(" or "name = function(", then scan
        # forward from the opening paren to find the matching close paren.
        for match in re.finditer(
            r"^(\w[\w.]*)\s*(?:<-|=)\s*function\s*\(", content, re.MULTILINE
        ):
            name = match.group(1)
            if name not in exports:
                continue

            # Find the matching closing paren from the opening paren position
            open_pos = match.end() - 1  # position of '('
            depth = 1
            pos = open_pos + 1
            while pos < len(content) and depth > 0:
                if content[pos] == "(":
                    depth += 1
                elif content[pos] == ")":
                    depth -= 1
                pos += 1

            if depth == 0:
                args = content[open_pos + 1 : pos - 1].strip()
                # Normalise whitespace in multi-line args
                args = re.sub(r"\s+", " ", args)
            else:
                args = ""

            signatures[name] = {
                "name": name,
                "args": args[:500],  # Truncate very long arg lists
                "file": str(f.relative_to(pkg_path)),
            }

    # Return in export order, adding any we didn't find source for
    result = []
    for exp in exports:
        if exp in signatures:
            result.append(signatures[exp])
        else:
            result.append({"name": exp, "args": None, "file": None})

    return result


def main():
    parser = argparse.ArgumentParser(description="Scan an R package repository")
    parser.add_argument("pkg_path", help="Path to R package root")
    parser.add_argument("--output", default="pkg-inventory.json", help="Output JSON path")
    args = parser.parse_args()

    pkg_path = Path(args.pkg_path).resolve()

    if not (pkg_path / "DESCRIPTION").exists():
        print(f"ERROR: {pkg_path} does not appear to be an R package (no DESCRIPTION)", file=sys.stderr)
        sys.exit(1)

    # Parse core metadata
    desc = parse_description(pkg_path)
    namespace = parse_namespace(pkg_path)
    deps = parse_dependencies(desc)
    class_systems = detect_class_systems(pkg_path)
    vignettes = extract_vignette_titles(pkg_path)
    fn_signatures = extract_function_signatures(pkg_path, namespace["exports"])

    # Scan directories
    dirs = {}
    for d in ["R", "man", "tests", "vignettes", "src", "data", "inst", "data-raw"]:
        dirs[d] = scan_directory(pkg_path, d)

    # Build inventory
    inventory = {
        "package": {
            "name": desc.get("Package", "UNKNOWN"),
            "title": desc.get("Title", ""),
            "description": desc.get("Description", ""),
            "version": desc.get("Version", ""),
            "authors": desc.get("Authors@R", desc.get("Author", "")),
            "license": desc.get("License", ""),
            "url": desc.get("URL", ""),
            "bug_reports": desc.get("BugReports", ""),
        },
        "exports": {
            "functions": fn_signatures,
            "count": len(namespace["exports"]),
            "s3_methods": namespace["s3_methods"],
            "s4_methods": namespace["s4_methods"],
            "s4_classes": namespace["s4_classes"],
            "export_patterns": namespace.get("export_patterns", []),
        },
        "class_systems": class_systems,
        "dependencies": deps,
        "namespace_imports": {
            "packages": namespace["imports"],
            "selective": namespace["import_from"],
        },
        "directories": dirs,
        "vignettes": vignettes,
    }

    # Write output
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(inventory, f, indent=2)

    # Print summary to stdout
    print(f"Package: {inventory['package']['name']} v{inventory['package']['version']}")
    print(f"Title: {inventory['package']['title']}")
    print(f"Exported functions: {inventory['exports']['count']}")
    print(f"S3 methods: {len(namespace['s3_methods'])}")
    print(f"S4 methods: {len(namespace['s4_methods'])}")
    print(f"Class systems: {', '.join(k for k, v in class_systems.items() if v) or 'none detected'}")
    print(f"R files: {dirs['R']['file_count']} ({dirs['R']['total_lines']} lines)")
    print(f"Man pages: {dirs['man']['file_count']}")
    print(f"Tests: {dirs['tests']['file_count']} ({dirs['tests']['total_lines']} lines)")
    print(f"Vignettes: {len(vignettes)}")
    print(f"Has compiled code: {dirs['src']['exists']}")
    print(f"Dependencies: {len(deps.get('imports', []))} imports, {len(deps.get('suggests', []))} suggests")
    print(f"\nInventory written to: {output_path}")


if __name__ == "__main__":
    main()
