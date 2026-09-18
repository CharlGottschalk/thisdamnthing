"""Load the development constitution for both hosts."""

import json
from pathlib import Path
import sys


root = Path(__file__).resolve().parents[2]
# Hook payload cwd is the session location; the process may run elsewhere.
# Empty input also supports invoking this loader manually within the repo.
try:
    raw = sys.stdin.read(65537)
    if len(raw) > 65536:
        raise ValueError("Hook input exceeds 64 KiB")
    payload = json.loads(raw) if raw.strip() else {"cwd": str(Path.cwd())}
    cwd = payload.get("cwd") if isinstance(payload, dict) else None
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError("Expected absolute session cwd")
    if not Path(cwd).resolve().is_relative_to(root):
        raise ValueError("Session is outside this repository")
except (OSError, ValueError):
    raise SystemExit(0)

constitution = root / ".dev/CONSTITUTION.md"
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": constitution.read_text(encoding="utf-8"),
    }
}))
