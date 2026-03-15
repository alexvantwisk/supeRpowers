#!/usr/bin/env python3
"""
Set up the working environment for R package skill generation.

Usage:
    python3 setup_workspace.py <github-url> [--workdir /path/to/dir]

This script:
1. Validates the GitHub URL
2. Creates a temp working directory (or uses --workdir)
3. Clones the repo (shallow)
4. Verifies it's an R package
5. Creates the reports/ directory
6. Runs the scanner
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def validate_github_url(url: str) -> tuple:
    """Validate and parse GitHub URL. Returns (owner, repo)."""
    patterns = [
        r"https?://github\.com/([^/]+)/([^/\s.]+?)(?:\.git)?/?$",
        r"git@github\.com:([^/]+)/([^/\s.]+?)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, url.strip())
        if match:
            return match.group(1), match.group(2)
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Set up R package skill generation workspace")
    parser.add_argument("github_url", help="GitHub URL of the R package")
    parser.add_argument(
        "--workdir",
        default=None,
        help="Working directory (default: creates a temp directory under OS temp dir)",
    )
    args = parser.parse_args()

    # Determine working directory
    if args.workdir:
        workdir = Path(args.workdir)
        workdir.mkdir(parents=True, exist_ok=True)
    else:
        workdir = Path(tempfile.mkdtemp(prefix="rpkg-skill-"))
        print(f"Created working directory: {workdir}")

    pkg_dir = workdir / "pkg-source"
    reports_dir = workdir / "reports"

    # Validate URL
    owner, repo = validate_github_url(args.github_url)
    if not owner:
        print(f"ERROR: Invalid GitHub URL: {args.github_url}", file=sys.stderr)
        print("Expected: https://github.com/owner/repo", file=sys.stderr)
        sys.exit(1)

    print(f"Repository: {owner}/{repo}")

    # Clean previous clone if present
    if pkg_dir.exists():
        if not pkg_dir.is_dir():
            print(f"ERROR: {pkg_dir} exists but is not a directory", file=sys.stderr)
            sys.exit(1)
        # Safety: only remove if it looks like a previous clone (contains .git)
        if (pkg_dir / ".git").exists() or not any(pkg_dir.iterdir()):
            shutil.rmtree(pkg_dir)
        else:
            print(
                f"ERROR: {pkg_dir} exists and doesn't look like a git clone. "
                "Remove it manually if safe.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Clone
    print(f"\nCloning {args.github_url}...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", args.github_url, str(pkg_dir)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Clone failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("Clone successful.")

    # Verify it's an R package
    desc = pkg_dir / "DESCRIPTION"
    if not desc.exists():
        print("ERROR: No DESCRIPTION file found. This may not be an R package.", file=sys.stderr)
        sys.exit(1)

    # Check for Package field
    with open(desc, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    if not re.search(r"^Package:", content, re.MULTILINE):
        print("ERROR: DESCRIPTION exists but has no Package: field.", file=sys.stderr)
        sys.exit(1)

    # Create reports directory
    reports_dir.mkdir(exist_ok=True)
    print(f"Reports directory: {reports_dir}")

    # Run scanner
    scanner = Path(__file__).parent / "scan_r_package.py"
    inventory_path = workdir / "pkg-inventory.json"
    print("\nScanning package...")
    result = subprocess.run(
        [sys.executable, str(scanner), str(pkg_dir), "--output", str(inventory_path)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Scanner warnings:\n{result.stderr}", file=sys.stderr)

    # Summary
    print("\n" + "=" * 60)
    print(f"WORKDIR={workdir}")
    print("Workspace ready. Next steps:")
    print(f"1. Read {inventory_path} for package overview")
    print("2. Dispatch exploration agents (see agents/ directory)")
    print(f"3. Collect reports from {reports_dir}")
    print("4. Synthesise into skill (see references/synthesis-guide.md)")
    print("=" * 60)


if __name__ == "__main__":
    main()
