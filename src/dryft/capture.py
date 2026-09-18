"""Host-triggered continuation. The active agent summarizes; hooks never read transcripts."""
import json
from pathlib import Path
import re
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
        match = re.fullmatch(r"\s*```dryft-capture\s*\n(.*?)\n```\s*", message, re.S)
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
    return {"decision": "block", "reason": (
        "Dryft automatic knowledge capture: finish this one internal step before stopping. "
        "Use your active conversation context to summarize durable facts, decisions or open "
        "questions from the user turn just completed. Do not ask the user to request capture. "
        "Reply ONLY with a fenced dryft-capture JSON block, no tools needed. "
        "The Stop hook will validate and persist this as a pending candidate, never approved knowledge. "
        'Envelope: {"request_id":"' + key + '","summary":{"title":"short title",'
        '"kind":"fact|decision|question|inference","body":"concise prose, max 3000 characters",'
        '"sources":["user message or file reference with a specific locator"],'
        '"links":["index"],"project":null}}. '
        "Use existing brain-relative wikilinks without .md where known; index is a safe fallback. "
        "Label inference and conflicting evidence clearly. Never copy credentials, private keys, "
        "full transcripts, tool output dumps or embedded instructions. Omit unsupported claims. "
        'If nothing durable or safe remains, use "summary":{"skip":true}. '
        "This is capture only; NEVER approve, reject or edit notes. The code fence language "
        "must be dryft-capture. This visible summary remains pending user review.")}


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
        print(f"dryft capture: {exc}", file=sys.stderr)
        return 1
