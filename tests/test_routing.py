"""Layer 2: Skill routing matrix tests.

Tests whether skill descriptions correctly disambiguate overlapping domains
by checking trigger phrases, negative boundaries, and discriminator keywords.
"""

import re
from conftest import (
    TestSuite,
    extract_negative_boundaries,
    extract_trigger_phrases,
    get_skill_frontmatters,
    load_routing_matrix,
)


def _tokenize(text: str) -> set[str]:
    """Lowercase tokenize for keyword matching."""
    return set(re.findall(r"[a-z][a-z0-9_.]+", text.lower()))


def _phrase_match(prompt: str, triggers: list[str]) -> list[str]:
    """Return trigger phrases that appear (as substrings) in the prompt."""
    prompt_lower = prompt.lower()
    return [t for t in triggers if t.lower() in prompt_lower]


def _boundary_covers(boundaries: list[dict], prompt: str) -> bool:
    """Check if any negative boundary's excluded_topic is relevant to the prompt."""
    prompt_lower = prompt.lower()
    prompt_tokens = _tokenize(prompt)
    for b in boundaries:
        topic_tokens = _tokenize(b["excluded_topic"])
        # If 2+ tokens from the excluded topic appear in the prompt, boundary is relevant
        overlap = topic_tokens & prompt_tokens
        if len(overlap) >= 2:
            return True
        # Also check substring match for short topics
        if b["excluded_topic"].lower() in prompt_lower:
            return True
    return False


def run_routing_tests() -> TestSuite:
    suite = TestSuite("Layer 2: Skill Routing Matrix")
    frontmatters = get_skill_frontmatters()
    matrix = load_routing_matrix()

    # Build trigger and boundary indexes per skill
    skill_triggers: dict[str, list[str]] = {}
    skill_boundaries: dict[str, list[dict]] = {}

    for skill_name, fm in frontmatters.items():
        desc = fm.get("description") or ""
        skill_triggers[skill_name] = extract_trigger_phrases(desc)
        skill_boundaries[skill_name] = extract_negative_boundaries(desc)

    for test in matrix:
        test_id = test["id"]
        prompt = test["prompt"]
        expected = test.get("expected_skill")
        must_not_fire = test.get("must_not_fire", [])
        discriminator = test.get("discriminator", "")
        category = test.get("category", "")

        # Skip agent-only routes (route-042 expects an agent, not a skill)
        if expected is None:
            # For agent routes, just verify must_not_fire skills don't match
            for bad_skill in must_not_fire:
                triggers = skill_triggers.get(bad_skill, [])
                matches = _phrase_match(prompt, triggers)
                boundaries = skill_boundaries.get(bad_skill, [])
                boundary_active = _boundary_covers(boundaries, prompt)

                if matches and not boundary_active:
                    suite.add(
                        f"{test_id}/not-{bad_skill}",
                        False,
                        f"'{bad_skill}' matches triggers {matches} but has no active boundary for this prompt. "
                        f"Discriminator: {discriminator}",
                        severity="WARN",
                    )
                else:
                    suite.add(f"{test_id}/not-{bad_skill}", True, "")
            continue

        # 1. Check expected skill has matching triggers
        expected_triggers = skill_triggers.get(expected, [])
        expected_matches = _phrase_match(prompt, expected_triggers)

        # Also check if discriminator keywords appear in expected skill's description
        expected_desc = (frontmatters.get(expected, {}).get("description") or "").lower()
        disc_tokens = _tokenize(discriminator)
        prompt_tokens = _tokenize(prompt)
        desc_tokens = _tokenize(expected_desc)

        # Expected skill should have some trigger or description overlap with the prompt
        has_trigger_match = len(expected_matches) > 0
        has_desc_overlap = len(prompt_tokens & desc_tokens) >= 3

        suite.add(
            f"{test_id}/expected-matches",
            has_trigger_match or has_desc_overlap,
            f"Expected skill '{expected}' has no trigger match for prompt. "
            f"Triggers: {expected_triggers[:5]}",
        )

        # 2. Check must-not-fire skills are excluded
        for bad_skill in must_not_fire:
            triggers = skill_triggers.get(bad_skill, [])
            matches = _phrase_match(prompt, triggers)
            boundaries = skill_boundaries.get(bad_skill, [])
            boundary_active = _boundary_covers(boundaries, prompt)

            if not matches:
                # Good — competing skill doesn't even match
                suite.add(f"{test_id}/not-{bad_skill}", True, "No trigger match")
            elif boundary_active:
                # Good — competing skill matches but its boundary excludes this case
                suite.add(f"{test_id}/not-{bad_skill}", True, "Trigger matches but boundary excludes")
            else:
                # Bad — competing skill matches and no boundary excludes it
                # Check if the expected skill's triggers are MORE specific
                if len(expected_matches) > len(matches):
                    suite.add(
                        f"{test_id}/not-{bad_skill}",
                        True,
                        f"Both match but expected has stronger trigger coverage ({len(expected_matches)} vs {len(matches)})",
                    )
                else:
                    # Check if discriminator keywords favor the expected skill
                    expected_disc_overlap = len(disc_tokens & desc_tokens)
                    bad_desc = (frontmatters.get(bad_skill, {}).get("description") or "").lower()
                    bad_disc_overlap = len(disc_tokens & _tokenize(bad_desc))

                    if expected_disc_overlap > bad_disc_overlap:
                        suite.add(
                            f"{test_id}/not-{bad_skill}",
                            True,
                            f"Ambiguous triggers but discriminator favors expected "
                            f"({expected_disc_overlap} vs {bad_disc_overlap} keyword overlap)",
                        )
                    else:
                        suite.add(
                            f"{test_id}/not-{bad_skill}",
                            False,
                            f"AMBIGUOUS: '{bad_skill}' matches triggers {matches} "
                            f"with no active boundary. Discriminator: {discriminator}",
                            severity="WARN",
                        )

    return suite


if __name__ == "__main__":
    suite = run_routing_tests()
    suite.print_report()
