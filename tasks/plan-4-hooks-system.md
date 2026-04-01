# Plan 4: Hooks System

## Summary

Implement the session-start hook that detects R project type in the current directory and surfaces relevant skills and agents. The hook fires on startup, resume, clear, and compact events.

**Deliverables:** 3 files in `hooks/` directory:
- `hooks/hooks.json` — hook configuration
- `hooks/session-start` — bash detection script
- `hooks/run-hook.cmd` — cross-platform Windows/Unix wrapper

## Reference Implementation

Based on the superpowers plugin's hooks system at `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/hooks/`:
- `hooks.json` uses `SessionStart` event with `startup|clear|compact` matcher
- Command uses `${CLAUDE_PLUGIN_ROOT}` variable for portable paths
- `run-hook.cmd` is a polyglot bash/cmd script that finds bash on Windows
- `session-start` outputs JSON with platform-aware context injection

## File Specifications

### Task 1: Create `hooks/hooks.json`

- [ ] Write hooks.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

Identical structure to superpowers — proven to work.

---

### Task 2: Create `hooks/run-hook.cmd`

- [ ] Write run-hook.cmd (polyglot bash/cmd wrapper)

Copy the superpowers run-hook.cmd structure exactly — it handles:
- Windows: tries Git for Windows bash in standard locations, then PATH bash
- Unix: runs the named script directly via `exec bash`
- No bash found: exits silently (plugin still works, just without context injection)

---

### Task 3: Create `hooks/session-start`

- [ ] Write session-start detection script (~80-100 lines)

**Detection logic (in priority order, all checks run — types can overlap):**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Detection flags
is_r_package=false
is_shiny=false
is_quarto=false
is_targets=false
is_clinical=false
is_r_project=false

# Detect R package (DESCRIPTION + R/ or NAMESPACE)
if [ -f "DESCRIPTION" ] && { [ -d "R" ] || [ -f "NAMESPACE" ]; }; then
  is_r_package=true
fi

# Detect Shiny app
if [ -f "app.R" ] || { [ -f "ui.R" ] && [ -f "server.R" ]; }; then
  is_shiny=true
fi
# golem detection (R package + inst/golem-config.yml)
if [ "$is_r_package" = true ] && [ -f "inst/golem-config.yml" ]; then
  is_shiny=true
fi
# rhino detection
if [ -f "rhino.yml" ]; then
  is_shiny=true
fi

# Detect Quarto project
if [ -f "_quarto.yml" ]; then
  is_quarto=true
fi

# Detect targets pipeline
if [ -f "_targets.R" ]; then
  is_targets=true
fi

# Detect clinical/pharma project
if [ "$is_r_package" = true ] && [ -f "DESCRIPTION" ]; then
  if grep -qE 'admiral|pharmaverse|sdtm|adam' "DESCRIPTION" 2>/dev/null; then
    is_clinical=true
  fi
fi
if [ -d "adam" ] || [ -d "sdtm" ] || [ -d "ADAM" ] || [ -d "SDTM" ]; then
  is_clinical=true
fi

# Detect general R project
if [ -f "*.Rproj" ] 2>/dev/null || ls *.R >/dev/null 2>&1 || [ -d "R" ]; then
  is_r_project=true
fi

# Build context message
skills=""
if [ "$is_r_package" = true ]; then
  skills="${skills}R package detected. Key skills: /r-package-dev, /r-tdd, /r-cmd-pkg-release, /r-cmd-tdd-cycle. Key agents: r-pkg-check, r-code-reviewer, r-dependency-manager.\n"
fi
if [ "$is_shiny" = true ]; then
  skills="${skills}Shiny app detected. Key skills: /r-shiny, /r-cmd-shiny-app. Key agents: r-shiny-architect.\n"
fi
if [ "$is_quarto" = true ]; then
  skills="${skills}Quarto project detected. Key skill: /r-quarto.\n"
fi
if [ "$is_targets" = true ]; then
  skills="${skills}Targets pipeline detected. Key skill: /r-targets.\n"
fi
if [ "$is_clinical" = true ]; then
  skills="${skills}Clinical/pharma project detected. Key skill: /r-clinical. Key agent: r-statistician.\n"
fi
if [ "$is_r_project" = true ] && [ "$is_r_package" = false ]; then
  skills="${skills}R project detected. Key skills: /r-data-analysis, /r-visualization, /r-stats, /r-cmd-analysis. Key agent: r-statistician.\n"
fi

# If nothing detected, exit silently
if [ -z "$skills" ]; then
  echo '{}'
  exit 0
fi

# Escape and output JSON
# [escape_for_json function and platform-aware output, same pattern as superpowers]
```

**Output format:** Same platform-aware JSON as superpowers:
- Claude Code: `hookSpecificOutput.additionalContext`
- Cursor: `additional_context`
- Copilot CLI / default: `additionalContext`

---

## Project Type → Skills Mapping

| Project Type | Detected By | Skills Surfaced | Agents Surfaced |
|-------------|-------------|-----------------|-----------------|
| R Package | DESCRIPTION + (R/ or NAMESPACE) | r-package-dev, r-tdd, r-cmd-pkg-release, r-cmd-tdd-cycle | r-pkg-check, r-code-reviewer, r-dependency-manager |
| Shiny App | app.R, ui.R+server.R, golem config, rhino.yml | r-shiny, r-cmd-shiny-app | r-shiny-architect |
| Quarto | _quarto.yml | r-quarto | — |
| Targets | _targets.R | r-targets | — |
| Clinical | DESCRIPTION with admiral/pharmaverse, adam/sdtm dirs | r-clinical | r-statistician |
| General R | .Rproj, .R files, R/ dir (not a package) | r-data-analysis, r-visualization, r-stats, r-cmd-analysis | r-statistician |
| Not R | None of the above | (nothing — hook stays silent) | — |

**Overlap handling:** All checks run independently. An R package that is also a Shiny app gets both sets of skills surfaced.

## Implementation Tasks

- [ ] **Task 1:** Write `hooks/hooks.json`
- [ ] **Task 2:** Write `hooks/run-hook.cmd` (copy superpowers polyglot pattern)
- [ ] **Task 3:** Write `hooks/session-start` with detection logic
- [ ] **Task 4:** Make `hooks/session-start` executable (`chmod +x`)
- [ ] **Task 5:** Test with an R package directory
- [ ] **Task 6:** Test with a Shiny app directory
- [ ] **Task 7:** Test with a non-R directory (should output `{}`)

## Testing Plan

Create temporary test directories to verify each detection path:

```bash
# Test R package detection
mkdir -p /tmp/test-pkg/R && touch /tmp/test-pkg/DESCRIPTION
cd /tmp/test-pkg && bash /path/to/hooks/session-start

# Test Shiny detection
mkdir -p /tmp/test-shiny && touch /tmp/test-shiny/app.R
cd /tmp/test-shiny && bash /path/to/hooks/session-start

# Test golem overlap (package + shiny)
mkdir -p /tmp/test-golem/R /tmp/test-golem/inst
touch /tmp/test-golem/DESCRIPTION /tmp/test-golem/inst/golem-config.yml
cd /tmp/test-golem && bash /path/to/hooks/session-start

# Test non-R project
mkdir -p /tmp/test-nope
cd /tmp/test-nope && bash /path/to/hooks/session-start
# Should output: {}
```

## Verification Checklist

- [ ] `hooks/hooks.json` is valid JSON
- [ ] `hooks/session-start` is executable
- [ ] `hooks/run-hook.cmd` finds bash on Windows (Git Bash)
- [ ] R package correctly detected in a package directory
- [ ] Shiny app correctly detected (app.R, golem, rhino patterns)
- [ ] Quarto project correctly detected
- [ ] Targets pipeline correctly detected
- [ ] Clinical project correctly detected
- [ ] Non-R directory produces empty JSON `{}`
- [ ] Overlapping types produce combined output
- [ ] Output JSON is valid (no unescaped characters)
- [ ] `plugin.json` already references `"hooks": "hooks/hooks.json"` — no change needed
