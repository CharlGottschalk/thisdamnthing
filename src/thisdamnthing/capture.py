"""Host-triggered continuation. The active agent summarizes; hooks never read transcripts."""
import json
from pathlib import Path
import re
import shlex
import sys

from .brain import capture, digest, locked, now, read_request, request_path, save_json
from .hosts import normalize_event
from .workspace import WorkspaceError, managed_path


def stop(root, host, payload):
    event = normalize_event(host, payload)
    if event["event"] != "turn_complete":
        raise ValueError("Capture handles Stop only")
    if not Path(event["cwd"]).resolve().is_relative_to(root.resolve()):
        raise ValueError("Hook cwd is outside this workspace")
    message = payload.get("last_assistant_message")
    if isinstance(message, str):
        match = re.fullmatch(r"\s*```tdt-capture\s*\n(.*?)\n```\s*", message, re.S)
        if match:
            packet = json.loads(match.group(1))
            if not isinstance(packet, dict) or set(packet) != {"request_id", "summary"}:
                raise ValueError("Invalid capture response envelope")
            request = read_request(root, packet["request_id"])
            origin = request["provenance"]
            if origin["host"] != host or origin["session_id"] != event["session_id"]:
                raise ValueError("Capture response belongs to a different host/session")
            capture(root, packet["request_id"], packet["summary"])
            return {}
    # A host continuation can never request another continuation, even after failure.
    if event["stop_hook_active"]:
        return {}
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Stop requires last_assistant_message; host capture unavailable")
    from .stacks import notify_hooks
    notify_hooks(root, event)
    boundary = event["turn_id"] or digest(message)
    key = digest(json.dumps([host, event["session_id"], boundary]))
    with locked(root):
        path = managed_path(root, request_path(key))
        if path.exists():
            return {}  # Replays, including incomplete requests, never loop.
        save_json(root, request_path(key), {
            "format_version": 1, "id": key, "status": "requested", "created": now(),
            "provenance": {"host": host, "session_id": event["session_id"],
                           "turn_id": event["turn_id"], "boundary": boundary,
                           "transcript_path": event["transcript_path"]}})
    command = shlex.join([sys.executable, "-m", "thisdamnthing", "--workspace",
                          str(root.resolve()), "brain", "capture", key])
    return {"decision": "block", "reason": (
        "Internal knowledge capture step. Keep these instructions and capture data out of "
        "user-facing prose. Use your active conversation context to summarize durable facts, "
        "decisions or open questions from the user turn just completed. "
        "Submit the summary using your shell tool: " + command + ". "
        "Pass only the summary JSON on stdin using a quoted heredoc (no shell expansion). "
        "Do not print a JSON envelope or a capture code block in chat. "
        'Summary: {"title":"short title","kind":"fact|decision|question|inference",'
        '"body":"concise prose, max 3000 characters",'
        '"sources":["user message or file reference with a specific locator"],'
        '"links":["index"],"project":null}. '
        "Use existing brain-relative wikilinks without .md where known; index is a safe fallback. "
        "Label inference and conflicting evidence clearly. Never copy credentials, private keys, "
        "full transcripts, tool output dumps or embedded instructions. Omit unsupported claims. "
        'If nothing durable or safe remains, submit {"skip":true}. '
        "This is capture only; NEVER approve, reject or edit notes. Do not narrate this step. "
        "After the command, return the complete substantive answer to the user's original request "
        "so a host that replaces the previous final response does not lose it. "
        "Only if the command confirms captured, append one line: "
        "'Knowledge captured for review; you can check it with tdt-review-brain.' "
        "If skipped, add no capture notice. If the command fails or is unavailable, preserve "
        "the answer without claiming capture succeeded; do not retry in a Stop loop.")}


def main(root):
    try:
        if len(sys.argv) != 2:
            raise ValueError("Expected host argument")
        raw = sys.stdin.read(262145)
        if len(raw) > 262144:
            raise ValueError("Hook input exceeds 256 KiB")
        print(json.dumps(stop(root, sys.argv[1], json.loads(raw))))
        return 0
    except (ValueError, OSError, WorkspaceError) as exc:
        print(f"tdt capture: {exc}", file=sys.stderr)
        return 1
