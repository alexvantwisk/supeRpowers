@echo off
REM Cross-platform wrapper for supeRpowers hooks on Windows.
REM Usage: run-hook.cmd <hook-name>
REM Delegates to the bash script via WSL or Git Bash.

setlocal

set "HOOK_NAME=%~1"
if "%HOOK_NAME%"=="" (
    echo Usage: run-hook.cmd ^<hook-name^>
    exit /b 1
)

set "HOOK_DIR=%~dp0"
set "HOOK_PATH=%HOOK_DIR%%HOOK_NAME%"

REM Try WSL first, then Git Bash
where wsl >nul 2>&1
if %errorlevel% equ 0 (
    wsl bash "%HOOK_PATH%"
    exit /b %errorlevel%
)

where bash >nul 2>&1
if %errorlevel% equ 0 (
    bash "%HOOK_PATH%"
    exit /b %errorlevel%
)

echo Error: No bash interpreter found. Install WSL or Git Bash.
exit /b 1
