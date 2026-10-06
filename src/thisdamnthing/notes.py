"""Explicit user saves and tagged scratchpad retrieval."""
import json
import re
import sys

from . import brain
from .workspace import WorkspaceError


def tags(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 8:
        raise WorkspaceError("Include 1–8 specific subject tags")
    result = []
    for item in value:
        brain.clean_text(item, "tag", 64)
        if not isinstance(item, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", item):
            raise WorkspaceError("Tags must be lowercase words joined with hyphens, max 64 characters")
        if item not in result:
            result.append(item)
    return sorted(result)


def inventory(root):
    result = []
    for relative, meta, body in brain.scan_notes(root, ("notes",)):
        try:
            if meta["status"] != "scratchpad":
                raise WorkspaceError("expected scratchpad status")
            tags(meta.get("tags"))
        except WorkspaceError as exc:
            print(f"tdt: warning: skipping invalid note {relative}: {exc}", file=sys.stderr)
            continue
        result.append((relative, meta, body))
    return result


def related(root, key):
    brain.identifier(key)
    entries = inventory(root)
    selected = next((entry for entry in entries if entry[1]["id"] == key), None)
    if selected is None:
        raise WorkspaceError("Unknown scratchpad note id")
    selected_tags = set(selected[1]["tags"])
    matches = []
    for path, meta, body in entries:
        shared = sorted(selected_tags.intersection(meta["tags"]))
        if meta["id"] != key and shared:
            matches.append({"path": path, "title": meta["title"], "shared_tags": shared})
    return sorted(matches, key=lambda item: (-len(item["shared_tags"]), item["path"]))[:50]


def save(root, data, instruction, *, scratchpad=False):
    instruction = brain.clean_text(instruction, "user instruction/reference", 500)
    if not isinstance(data, dict):
        raise WorkspaceError("Expected a summary JSON object")
    payload = dict(data)
    note_tags = tags(payload.pop("tags", None)) if scratchpad else None
    value = brain.summary(payload)
    category = "notes" if scratchpad else "knowledge"
    # Identity excludes inferred links and audit references so retries do not
    # duplicate the user's content merely because related knowledge has changed.
    identity = {k: v for k, v in value.items() if k != "links"}
    if scratchpad:
        identity["tags"] = note_tags
    key = brain.digest("direct:" + category + ":" + json.dumps(identity, sort_keys=True))
    with brain.locked(root):
        if value["project"]:
            from .projects import registry
            if value["project"] not in {entry["id"] for entry in registry(root)}:
                raise WorkspaceError("Unknown registered project id")
        allowed = set(brain.eligible_notes(root)) | {"index"}
        if scratchpad:
            allowed.update(brain.note_link(path) for path, _, _ in inventory(root))
        if any(link not in allowed for link in value["links"] + re.findall(r"\[\[([^\]]+)\]\]", value["body"])):
            raise WorkspaceError("Links must reference existing eligible notes")
        # A malformed record may be an earlier save. Do not silently skip it and
        # allocate a duplicate during retry; require inspection of the store.
        matches = []
        for path in brain.note_files(root, (category,)):
            meta, _ = brain.read_note(root, path)
            if meta['id'] == key:
                if meta['status'] != ('scratchpad' if scratchpad else 'approved'):
                    raise WorkspaceError("Existing direct save has an unexpected status")
                matches.append(path)
        if len(matches) > 1:
            raise WorkspaceError("Duplicate direct save identity; inspect existing notes")
        existing = matches[0] if matches else None
        if existing:
            return {"status": "existing", "id": key, "path": existing}
        relative = brain.named_path(root, category, key, value["title"])
        body = value.pop("body") + "\n\nRelated: " + ", ".join(f"[[{link}]]" for link in value["links"])
        timestamp = brain.now()
        meta = {"format_version": 1, "id": key, "status": "scratchpad" if scratchpad else "approved",
                "created": timestamp, "updated": timestamp,
                "provenance": {"operation": "user note" if scratchpad else "user capture",
                               "user_instruction": instruction},
                "review": [] if scratchpad else [{"at": timestamp, "decision": "approve",
                    "user_instruction": instruction, "summary_sha256": brain.digest(json.dumps(data, sort_keys=True))}],
                **value}
        if scratchpad:
            meta["tags"] = note_tags
        else:
            meta["canonical"] = relative[6:-3]
        brain.atomic(root, relative, brain.note_text(meta, body))
    return {"status": "saved", "id": key, "path": relative}


def search(root, query, limit=10):
    query = brain.clean_text(query, "query", 300).casefold()
    if type(limit) is not int or not 1 <= limit <= 50:
        raise WorkspaceError("Search limit must be 1–50")
    return [(path, "[scratchpad] " + meta["title"], body + "\n\nTags: " + ", ".join(meta["tags"]) +
             "\nSources: " + json.dumps(meta["sources"], ensure_ascii=False))
            for path, meta, body in inventory(root)
            if query in (meta["title"] + "\n" + body + "\n" + " ".join(meta["tags"])).casefold()][:limit]
