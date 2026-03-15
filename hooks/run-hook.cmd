: <<'BATCH_SCRIPT'
@echo off
setlocal

rem Try Git for Windows
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem Try 32-bit Git
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem Try PATH (MSYS2, Cygwin, user-installed)
where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    bash "%~dpn0" %*
    exit /b %ERRORLEVEL%
)

rem No bash found — exit silently
exit /b 0
BATCH_SCRIPT

#!/usr/bin/env bash
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_NAME="${1:-}"

if [ -z "$HOOK_NAME" ]; then
    echo "Usage: run-hook.cmd <hook-name>" >&2
    exit 1
fi

HOOK_SCRIPT="${HOOK_DIR}/${HOOK_NAME}"

if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "Hook not found: ${HOOK_SCRIPT}" >&2
    exit 1
fi

exec bash "$HOOK_SCRIPT"
