"""Small Markdown candidate store. All mutations share a workspace lock."""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .workspace import WorkspaceError, managed_path, read_config, read_json

IDENTIFIER = re.compile(r"[a-f0-9]{64}\Z")
LINK = re.compile(r"(?:index|(?:knowledge|projects|sessions)/[a-z0-9][a-z0-9/_-]*)\Z")
SECRET = re.compile(r"-----BEGIN .*PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,})|(?:password|api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*\S+", re.I)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise WorkspaceError("Expected a full 64-character capture/candidate id")
    return value


@contextmanager
def locked(root):
    read_config(root)
    path = managed_path(root, ".tdt/state/brain.lock")
    with path.open("a", encoding="utf-8") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise WorkspaceError("Brain is busy; retry this operation") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def atomic(root, relative, content):
    path = managed_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".tdt-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_json(root, relative, value):
    atomic(root, relative, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def note_text(meta, body):
    # JSON is a YAML subset; no YAML parser/dependency is needed.
    text = "---\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n---\n\n" + body.rstrip() + "\n"
    if len(text.encode("utf-8")) > 32768:
        raise WorkspaceError("Note and review history exceed 32 KiB; existing note preserved")
    return text


def read_note(root, relative):
    path = managed_path(root, relative)
    if path.stat().st_size > 32768:
        raise WorkspaceError(f"Note too large: {relative}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise WorkspaceError(f"Expected ThisDamnThing JSON front matter: {relative}")
    head, body = text[4:].split("\n---\n", 1)
    meta = json.loads(head)
    if (not isinstance(meta, dict) or meta.get("format_version") != 1
            or not isinstance(meta.get("id"), str) or not IDENTIFIER.fullmatch(meta["id"])
            or meta.get("status") not in ("pending", "approved", "rejected")
            or not isinstance(meta.get("title"), str)
            or not isinstance(meta.get("review"), list)
            or any(not isinstance(item, dict) for item in meta["review"])
            or not isinstance(meta.get("provenance"), dict)):
        raise WorkspaceError(f"Invalid note metadata: {relative}")
    return meta, body.strip()


def clean_text(value, field, maximum):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(c) < 32 and c not in "\n\t" for c in value)):
        raise WorkspaceError(f"Invalid {field} (nonempty text, maximum {maximum} characters)")
    if SECRET.search(value):
        raise WorkspaceError(f"Possible secret in {field}; remove it before capture")
    return value.strip()


def summary(data):
    if not isinstance(data, dict) or set(data) - {"title", "kind", "body", "sources", "links", "project"}:
        raise WorkspaceError("Summary requires title, kind, body, sources, links and optional project")
    title = clean_text(data.get("title"), "title", 160)
    if "\n" in title:
        raise WorkspaceError("Title must be one line")
    kind = data.get("kind")
    if kind not in ("fact", "decision", "question", "inference"):
        raise WorkspaceError("Kind must be fact, decision, question or inference")
    body = clean_text(data.get("body"), "body", 3000)
    if "```" in body or len(body.splitlines()) > 40:
        raise WorkspaceError("Use concise prose, not transcripts or tool/code dumps")
    sources = data.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 8:
        raise WorkspaceError("Include 1–8 source references")
    sources = [clean_text(s, "source", 400) for s in sources]
    links = data.get("links", ["index"])
    if not isinstance(links, list) or not 1 <= len(links) <= 8:
        raise WorkspaceError("Include 1–8 brain-relative links (use index if no related note exists)")
    for link in links + re.findall(r"\[\[([^\]]+)\]\]", body):
        if not isinstance(link, str) or not LINK.fullmatch(link) or ".." in link or "//" in link:
            raise WorkspaceError("Invalid wikilink; use brain-relative paths without .md")
    project = data.get("project")
    if project is not None and (not isinstance(project, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", project)):
        raise WorkspaceError("Invalid project id")
    return {"title": title, "kind": kind, "body": body, "sources": sources,
            "links": links, "project": project}


def request_path(key):
    return f".tdt/state/captures/{identifier(key)}.json"


def read_request(root, key):
    request = read_json(root, request_path(key))
    if (not isinstance(request, dict) or request.get("format_version") != 1
            or request.get("id") != key
            or request.get("status") not in ("requested", "captured", "skipped")
            or not isinstance(request.get("created"), str)
            or not isinstance(request.get("provenance"), dict)
            or request["provenance"].get("host") not in ("claude", "codex")
            or not isinstance(request["provenance"].get("session_id"), str)):
        raise WorkspaceError("Invalid capture request state")
    return request


def capture(root, key, data):
    """Accept only agent summaries tied to a previously delivered host request."""
    with locked(root):
        request = read_request(root, key)
        if request.get("status") in ("captured", "skipped"):
            return request["status"] + ": " + key
        existing = managed_path(root, f"brain/candidates/{key}.md")
        if existing.exists():
            previous, _ = read_note(root, f"brain/candidates/{key}.md")
            if previous.get("id") != key or previous.get("provenance") != request["provenance"]:
                raise WorkspaceError("Candidate ownership conflict")
            request.update(status="captured", completed=now())
            save_json(root, request_path(key), request)
            return "captured: " + key
        if data == {"skip": True}:
            request.update(status="skipped", completed=now())
        else:
            value = summary(data)
            relative = f"brain/candidates/{key}.md"
            body = value.pop("body")
            meta = {"format_version": 1, "id": key, "status": "pending",
                    "created": request["created"], "updated": now(),
                    "provenance": request["provenance"], "review": [], **value}
            body += "\n\nRelated: " + ", ".join(f"[[{link}]]" for link in meta["links"])
            atomic(root, relative, note_text(meta, body))
            request.update(status="captured", completed=now())
        save_json(root, request_path(key), request)
        return request["status"] + ": " + key


def candidates(root, status="pending"):
    directory = managed_path(root, "brain/candidates")
    result = []
    for path in sorted(directory.glob("*.md")):
        meta, body = read_note(root, str(path.relative_to(root)))
        if status == "all" or meta.get("status") == status:
            result.append((meta, body))
    return result


def review(root, key, decision, instruction, expected, edited=None):
    """Explicit review only. A hash binds approval to the exact displayed proposal."""
    identifier(key)
    instruction = clean_text(instruction, "user instruction/reference", 500)
    if decision not in ("approve", "reject", "edit"):
        raise WorkspaceError("Expected approve, reject or edit")
    with locked(root):
        relative = f"brain/candidates/{key}.md"
        path = managed_path(root, relative)
        original = path.read_text(encoding="utf-8")
        if digest(original) != expected:
            raise WorkspaceError("Candidate changed; show it again before review")
        meta, body = read_note(root, relative)
        if meta.get("id") != key or meta.get("status") != "pending":
            raise WorkspaceError("Only pending candidates can be reviewed")
        record = {"at": now(), "decision": decision, "user_instruction": instruction,
                  "proposal_sha256": expected}
        if decision == "edit":
            value = summary(edited)
            record["previous"] = {k: meta.get(k) for k in value if k != "body"}
            record["previous"]["body"] = body
            body = value.pop("body") + "\n\nRelated: " + ", ".join(f"[[{link}]]" for link in value["links"])
            meta.update(value)
        else:
            meta["status"] = "approved" if decision == "approve" else "rejected"
        meta["updated"] = record["at"]
        meta["review"].append(record)
        if decision == "approve":
            # Always create a distinct canonical note: conflicting evidence survives.
            target = f"brain/knowledge/{key}.md"
            meta["canonical"] = f"knowledge/{key}"
            content = note_text(meta, body)
            destination = managed_path(root, target)
            if destination.exists() and destination.read_text(encoding="utf-8") != content:
                # Recovery after canonical write uses the stored approval, not a new timestamp.
                prior, prior_body = read_note(root, target)
                if (prior.get("id") != key or prior.get("status") != "approved"
                        or prior_body != body or not prior.get("review")
                        or prior["review"][-1].get("proposal_sha256") != expected
                        or prior["review"][-1].get("user_instruction") != instruction):
                    raise WorkspaceError("Canonical note conflict; existing evidence preserved")
                meta = prior
            else:
                atomic(root, target, content)
        atomic(root, relative, note_text(meta, body))
        return meta["status"] + ": " + key


def eligible_notes(root):
    """Current canonical approvals, restricted to registered project identities."""
    from .projects import registry
    project_ids = {p['id'] for p in registry(root)}
    notes = {}
    # Bound both filesystem work and output. Never traverse symlink directories.
    def scan_error(error):
        raise WorkspaceError(f"Cannot scan brain: {error}")
    count = 0
    for category in ("knowledge", "projects", "sessions"):
        directory = managed_path(root, f"brain/{category}")
        for current, directories, filenames in os.walk(directory, followlinks=False, onerror=scan_error):
            count += len(directories)
            if count > 2000:
                raise WorkspaceError("Brain scan exceeds 2000 entries")
            directories.sort()
            for name in directories:
                managed_path(root, str((Path(current) / name).relative_to(root)))
            for name in sorted(filenames):
                count += 1
                if count > 2000:
                    raise WorkspaceError("Brain scan exceeds 2000 files; narrow the stored corpus")
                if not name.endswith(".md"):
                    continue
                path = Path(current) / name
                relative = str(path.relative_to(root))
                meta, body = read_note(root, relative)
                if meta.get("project") is not None and not isinstance(meta["project"], str):
                    raise WorkspaceError(f"Invalid project identity in note: {relative}")
                if (meta["status"] == "approved"
                        and (not meta.get("project") or meta["project"] in project_ids)
                        and (category != "projects" or meta["id"] in project_ids)):
                    notes[relative[6:-3]] = (relative, meta["title"], body + "\n\nSources: " + json.dumps(meta.get("sources", []), ensure_ascii=False))
    return notes


def search(root, query, limit=10, depth=1, providers=()):
    """Literal text seeds plus bounded outgoing links, always approved-only."""
    query = clean_text(query, "query", 300).casefold()
    if type(limit) is not int or not 1 <= limit <= 50 or type(depth) is not int or not 0 <= depth <= 3:
        raise WorkspaceError("Search limit must be 1–50 and depth 0–3")
    notes = eligible_notes(root)
    seeds = [key for key, (_, title, body) in notes.items()
             if query in (title + "\n" + body).casefold()][:limit]
    if providers:
        from .capabilities import rank
        seeds = rank(root, query, notes, providers)[:limit]
    queue = [(key, 0) for key in seeds]
    seen, result = set(), []
    while queue and len(result) < limit:
        key, level = queue.pop(0)
        if key in seen or key not in notes:
            continue
        seen.add(key)
        note = notes[key]
        result.append(note)
        if level < depth:
            for link in re.findall(r"\[\[([^\]]+)\]\]", note[2]):
                if LINK.fullmatch(link) and ".." not in link and "//" not in link:
                    queue.append((link, level + 1))
    return result
