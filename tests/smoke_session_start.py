#!/usr/bin/env python3
"""Smoke test: run the session-start hook in a temp dir with no R files,
via run-hook.cmd, asserting (1) stdout is valid JSON and (2) zero Rscript
spawns. A fake `Rscript` on PATH increments a counter file on each call."""

import json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        bindir = work / "bin"
        bindir.mkdir()
        counter = work / "rscript_calls.txt"
        # Fake Rscript shim (append a line on every invocation)
        if os.name == "nt":
            shim = bindir / "Rscript.cmd"
            shim.write_text(f'@echo x>>"{counter}"\n@exit /b 0\n')
        else:
            shim = bindir / "Rscript"
            shim.write_text(f'#!/usr/bin/env bash\necho x >> "{counter}"\n')
            shim.chmod(0o755)

        env = dict(os.environ)
        env["PATH"] = str(bindir) + os.pathsep + env["PATH"]
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)

        wrapper = ROOT / "hooks" / "run-hook.cmd"
        if os.name == "nt":
            cmd = [str(wrapper), "session-start"]
        else:
            cmd = ["bash", str(wrapper), "session-start"]

        proc = subprocess.run(cmd, cwd=work, env=env,
                              capture_output=True, text=True)
        out = proc.stdout.strip()
        try:
            json.loads(out or "{}")
        except json.JSONDecodeError as e:
            print(f"FAIL: invalid JSON: {e}\n{out!r}"); return 1
        spawns = counter.read_text().count("x") if counter.exists() else 0
        if spawns != 0:
            print(f"FAIL: session-start spawned Rscript {spawns}x in a non-R dir")
            return 1
        print(f"PASS: valid JSON, 0 Rscript spawns (stdout={out!r})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
