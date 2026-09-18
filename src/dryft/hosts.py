"""Small host payload boundary; never parse host transcripts in core code."""

import json
from pathlib import Path
import sys

from .workspace import WorkspaceError, managed_path

EVENTS = {"UserPromptSubmit": "user_request", "SessionStart": "session_start", "Stop": "turn_complete",
          "PreCompact": "pre_compact"}


def normalize_event(host, payload):
    if host not in ("claude", "codex") or not isinstance(payload, dict):
        raise ValueError("Expected a Claude or Codex hook JSON object")
    event = payload.get("hook_event_name")
    if not isinstance(event, str) or event not in EVENTS:
        raise ValueError("Unsupported hook_event_name")
    for field in ("session_id", "cwd"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise ValueError(f"Hook requires nonempty {field}")
    for field in ("transcript_path", "turn_id", "source"):
        value = payload.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"Hook {field} must be a nonempty string or null")
    for field in ("cwd", "transcript_path"):
        value = payload.get(field)
        if value is not None and ("\x00" in value or not Path(value).is_absolute()):
            raise ValueError(f"Hook {field} must be an absolute path")
    active = payload.get("stop_hook_active", False)
    if type(active) is not bool:
        raise ValueError("Hook stop_hook_active must be a boolean")
    return {"format_version": 1, "host": host, "event": EVENTS[event],
            "session_id": payload["session_id"], "cwd": payload["cwd"],
            "transcript_path": payload.get("transcript_path"),
            "turn_id": payload.get("turn_id"), "source": payload.get("source"),
            "stop_hook_active": active}


def session_start(root):
    try:
        if len(sys.argv) != 2:
            raise ValueError("Expected host argument: claude or codex")
        raw = sys.stdin.read(65537)
        if len(raw) > 65536:
            raise ValueError("Hook input exceeds 64 KiB")
        event = normalize_event(sys.argv[1], json.loads(raw))
        if event["event"] != "session_start":
            raise ValueError("This entry point only handles SessionStart")
        cwd = Path(event["cwd"]).resolve()
        from .constitution import context as policy_context, in_scope
        if not in_scope(root, cwd):
            return 0
        current_policy = policy_context(root)
        path = managed_path(root, ".dryft/context.md")
        with path.open(encoding="utf-8") as stream:
            context = stream.read(12001)
        if len(context) > 12000:
            raise ValueError("Workspace context exceeds 12000 characters")
        context += "\n\n" + current_policy
        if len(context) > 10000:
            raise ValueError("Combined workspace context exceeds 10000 characters; nothing loaded")
        from .stacks import notify_hooks
        notify_hooks(root, event)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": context}}))
        return 0
    except (OSError, ValueError, WorkspaceError) as exc:
        print(f"dryft startup: {exc}", file=sys.stderr)
        print(json.dumps({"continue": False, "stopReason": f"Dryft startup policy/context load failed: {exc}"}))
        return 0
