#!/usr/bin/env python3
"""supeRpowers Plugin Test Suite — Main Runner.

Runs all test layers and prints a consolidated scorecard.

Usage:
    python tests/run_all.py                  # Run all layers
    python tests/run_all.py --layer 1        # Run only Layer 1 (structural)
    python tests/run_all.py --layer 1b       # Run only Layer 1b (conventions)
    python tests/run_all.py --layer 2        # Run only Layer 2 (routing)
    python tests/run_all.py --verbose        # Show passing tests too
"""

import argparse
import os
import sys

# Ensure tests/ is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_structural import run_structural_tests
from test_conventions import run_convention_tests
from test_routing import run_routing_tests
from conftest import TestSuite


def print_banner():
    print()
    print("=" * 60)
    print("  supeRpowers Plugin Test Suite v1.0")
    print("=" * 60)


def print_summary(suites: list[TestSuite]):
    total_passed = sum(s.passed for s in suites)
    total_failed = sum(s.failed for s in suites)
    total_warned = sum(s.warned for s in suites)
    total_tests = sum(s.total for s in suites)

    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    for s in suites:
        icon = "\u2713" if s.failed == 0 else "\u2717"
        warn_str = f", {s.warned} warnings" if s.warned else ""
        fail_str = f", {s.failed} failed" if s.failed else ""
        print(f"  {icon} {s.name}: {s.passed}/{s.total} passed{fail_str}{warn_str}")

    print()
    print(f"  TOTAL: {total_passed}/{total_tests} passed", end="")
    if total_failed:
        print(f", {total_failed} FAILED", end="")
    if total_warned:
        print(f", {total_warned} warnings", end="")
    print()

    if total_failed == 0:
        print("\n  \u2713 All critical checks passed!")
    else:
        print(f"\n  \u2717 {total_failed} critical failure(s) require attention.")

    print()
    return total_failed


def main():
    parser = argparse.ArgumentParser(description="supeRpowers Plugin Test Suite")
    parser.add_argument("--layer", type=str, help="Run specific layer: 1, 1b, 2, or all")
    parser.add_argument("--verbose", action="store_true", help="Show passing tests")
    args = parser.parse_args()

    print_banner()

    suites: list[TestSuite] = []
    layer = (args.layer or "all").lower()

    if layer in ("all", "1"):
        suite = run_structural_tests()
        suites.append(suite)
        suite.print_report()

    if layer in ("all", "1b"):
        suite = run_convention_tests()
        suites.append(suite)
        suite.print_report()

    if layer in ("all", "2"):
        suite = run_routing_tests()
        suites.append(suite)
        suite.print_report()

    failures = print_summary(suites)
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
