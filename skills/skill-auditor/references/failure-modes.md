# Five Skill Failure Modes

Every skill failure falls into one of five categories. Diagnose the category and the fix becomes obvious.

Source: hooeem (Full Skills Course), Ole Lehmann (Skills 2.0).

## 1. The Silent Skill (Never Fires)

**Symptoms:** You type a request that should trigger the skill. Claude responds normally without using it. No indication it was considered.

**Root cause:** Description is too weak. Claude's activation threshold requires a strong match between the request and the description. Vague, generic, or missing trigger phrases never cross the threshold.

**Diagnosis:**
- Does the description explicitly list the words/phrases the user typed?
- Are there fewer than 5 trigger phrases?
- Is the description under 100 chars (too thin)?

**Fix:**
- Make the description "pushy" — embarrassingly explicit about when to activate
- Add 5-7 quoted trigger phrases: "Use when the user says 'X', 'Y', 'Z'..."
- Add context clues: "Also activate when the user uploads [type] and asks for [action]"

**Rubric checks:** D2, D5

## 2. The Hijacker (Fires on Wrong Requests)

**Symptoms:** You ask something unrelated and the skill activates. You wanted skill A but skill B fired instead.

**Root cause:** Description is too broad, or negative boundaries are missing. The description matches too many types of requests.

**Diagnosis:**
- Which words in the request matched the skill's description?
- Should those words have been excluded?
- Does the description contain generic terms ("data", "help", "process")?

**Fix:**
- Add negative boundaries: "Do NOT use for [list every similar-but-different task]"
- Tighten trigger phrases to be specific to this skill's actual function
- Reference sibling skills by name: "For X, use [other-skill] instead"

**Rubric checks:** D3, D4, O1, O4

## 3. The Drifter (Fires But Wrong Output)

**Symptoms:** The skill activates correctly but the output doesn't match expectations. Formatting is off, tone is wrong, or it skips steps.

**Root cause:** Instructions are ambiguous. Multiple interpretations exist, and Claude chose a different one than intended.

**Diagnosis:**
- Read instructions as if you've never seen them before
- Find sentences that could mean two different things
- Look for vague language: "handle appropriately", "format nicely", "as needed"

**Fix:**
- Replace ambiguous language with specific, testable instructions
- "Format nicely" → "Use H2 headings for each section, bold the first sentence, keep paragraphs to 3 lines max"
- Add concrete examples showing expected output format

**Rubric checks:** G5, E1, E2

## 4. The Fragile Skill (Works Sometimes, Breaks on Edge Cases)

**Symptoms:** Works perfectly on clean, well-formed inputs. Breaks on anything slightly unusual: incomplete data, unexpected format, missing fields.

**Root cause:** Edge case handling is incomplete. The skill assumes clean inputs.

**Diagnosis:**
- Feed the skill worst-case inputs: missing fields, wrong types, mixed formats
- Identify which scenarios cause failures
- Check whether the skill has explicit edge case instructions

**Fix:**
- Add explicit edge case instructions: "If [condition], then [specific action]"
- Include an edge case example showing unusual input handling
- Consider a validation step before processing

**Rubric checks:** G3, E3

## 5. The Overachiever (Adds Unrequested Content)

**Symptoms:** The skill produces the requested output but also adds unsolicited commentary, extra sections, or creative embellishments.

**Root cause:** Instructions say what TO do but not what NOT to do. Without constraints, Claude defaults to being maximally helpful.

**Diagnosis:**
- Check the output for anything not explicitly requested
- Look at instructions for scope constraints
- Are output boundaries defined?

**Fix:**
- Add explicit scope constraints: "Output ONLY [specified format] and nothing else"
- "Do NOT add explanatory text, commentary, or suggestions unless the user asks"
- Define exact output sections and format

**Rubric checks:** G6

## Diagnostic Quick Reference

| Symptom | Failure Mode | First Check |
|---------|-------------|-------------|
| Skill never activates | Silent Skill | Description trigger phrases (D2, D5) |
| Wrong skill fires | Hijacker | Negative boundaries (D3, D4, O1) |
| Right skill, wrong output | Drifter | Ambiguous instructions (G5) |
| Works on clean input, breaks on messy | Fragile | Edge case handling (G3, E3) |
| Output has extra unrequested content | Overachiever | Scope constraints (G6) |
