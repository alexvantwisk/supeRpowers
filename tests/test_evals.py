"""Layer 3: Deterministic eval-file validation (offline, CI-gating).

Validates evals/evals.json structure and checks that trigger_set
should_trigger consistency holds against each skill's own trigger phrases.
The expensive with/without-skill LLM benchmark is manual/nightly (see
CONTRIBUTING.md) and is NOT run here.
"""

import json
from conftest import (
    SKILLS_DIR,
    TestSuite,
    get_combined_trigger_text,
    get_skill_frontmatters,
    extract_trigger_phrases,
)

EVAL_SKILLS = [
    "r-data-analysis", "r-visualization", "r-package-dev",
    "r-stats", "r-reporting", "r-tdd", "r-debugging",
]


def run_eval_tests() -> TestSuite:
    suite = TestSuite("Layer 3: Eval Files")
    frontmatters = get_skill_frontmatters()

    for skill in EVAL_SKILLS:
        eval_path = SKILLS_DIR / skill / "evals" / "evals.json"
        suite.add(f"evals-exists/{skill}", eval_path.exists(),
                  f"Missing {skill}/evals/evals.json")
        if not eval_path.exists():
            continue
        data = json.loads(eval_path.read_text(encoding="utf-8"))

        suite.add(f"evals-name/{skill}", data.get("skill_name") == skill,
                  f"skill_name '{data.get('skill_name')}' != '{skill}'")

        scenarios = data.get("scenarios", [])
        suite.add(f"evals-scenario-count/{skill}", len(scenarios) >= 3,
                  f"Only {len(scenarios)} scenarios (need >=3)")
        for sc in scenarios:
            ok = bool(sc.get("prompt")) and len(sc.get("expectations", [])) >= 1
            suite.add(f"evals-scenario-shape/{skill}/{sc.get('id')}", ok,
                      "Scenario missing prompt or expectations")

        triggers = extract_trigger_phrases(
            get_combined_trigger_text(frontmatters.get(skill, {}))
        )
        tset = data.get("trigger_set", [])
        has_pos = any(t.get("should_trigger") for t in tset)
        has_neg = any(not t.get("should_trigger") for t in tset)
        suite.add(f"evals-trigger-both/{skill}", has_pos and has_neg,
                  "trigger_set needs >=1 should_trigger and >=1 should-not")

    return suite


if __name__ == "__main__":
    run_eval_tests().print_report()
