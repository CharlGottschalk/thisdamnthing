"""Personal to-do items: project-independent, operational data, never knowledge."""
import re
import secrets

from . import brain, constitution, frontmatter
from .workspace import WorkspaceError, managed_path

STATUSES = ("open", "done")


class StaleRevision(WorkspaceError):
    """The to-do changed since the caller read it."""


def inventory(root):
    result, identities = [], set()
    for path in brain.note_files(root, ("todos",)):
        text = constitution.bounded(managed_path(root, path), 32768)
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise WorkspaceError("Expected to-do YAML front matter: " + path)
        head, body = text[4:].split("\n---\n", 1)
        try:
            meta = frontmatter.loads(head)
        except (ValueError, RecursionError) as exc:
            raise WorkspaceError(f"Invalid to-do front matter {path}: {exc}") from exc
        if (not isinstance(meta, dict) or meta.get("format_version") != 1 or meta.get("kind") != "todo"
                or meta.get("status") not in STATUSES or type(meta.get("revision")) is not int
                or meta["revision"] < 1 or not isinstance(meta.get("provenance"), dict)
                or not isinstance(meta.get("title"), str)
                or not isinstance(meta.get("id"), str) or not re.fullmatch("[a-f0-9]{64}", meta["id"])
                or (meta.get("completed") is not None and not isinstance(meta["completed"], str))):
            raise WorkspaceError("Invalid to-do metadata: " + path)
        if meta["id"] in identities:
            raise WorkspaceError("Duplicate to-do identity")
        identities.add(meta["id"])
        result.append({**meta, "path": path, "body": body.strip()})
    return sorted(result, key=lambda row: (row["created"], row["id"]))


def write(root, row):
    meta = {key: value for key, value in row.items() if key not in ("path", "body")}
    brain.atomic(root, row["path"], brain.note_text(meta, row["body"]))


def create(root, title, instruction, body=None):
    instruction = brain.clean_text(instruction, "user instruction/reference", 500)
    title = brain.clean_text(title, "to-do title", 160)
    if "\n" in title:
        raise WorkspaceError("Use a one-line to-do title")
    body = brain.clean_text(body, "to-do text", 8000) if body else ""
    with brain.locked(root):
        for row in inventory(root):
            # A retried add returns the open item instead of duplicating it.
            if row["status"] == "open" and (row["title"], row["body"]) == (title, body):
                return {"result": "existing", **row}
        key = secrets.token_hex(32)
        timestamp = brain.now()
        row = {"path": brain.named_path(root, "todos", key, title), "format_version": 1, "id": key,
               "kind": "todo", "title": title, "status": "open", "revision": 1, "created": timestamp,
               "updated": timestamp, "completed": None,
               "provenance": {"operation": "todo add", "user_instruction": instruction}, "body": body}
        write(root, row)
    return {"result": "saved", **row}


def select(root, key):
    """Full id, or a unique prefix of at least 8 characters."""
    if not isinstance(key, str) or not re.fullmatch("[a-f0-9]{8,64}", key):
        raise WorkspaceError("Expected a to-do id (at least 8 hex characters)")
    rows = [row for row in inventory(root) if row["id"].startswith(key)]
    if len(rows) != 1:
        raise WorkspaceError("Unknown to-do id" if not rows else "Ambiguous to-do id; use more characters")
    return rows[0]


def change(root, key, action, revision, instruction):
    """done, reopen or remove; remove deletes the record."""
    instruction = brain.clean_text(instruction, "user instruction/reference", 500)
    with brain.locked(root):
        row = select(root, key)
        if row["revision"] != revision:
            raise StaleRevision("To-do changed; reread before changing it")
        if action == "remove":
            managed_path(root, row["path"]).unlink()
            return {**row, "result": "removed"}
        wanted = "done" if action == "done" else "open"
        if row["status"] == wanted:
            raise WorkspaceError(f"To-do is already {wanted}")
        timestamp = brain.now()
        row.update(status=wanted, completed=timestamp if wanted == "done" else None,
                   revision=row["revision"] + 1, updated=timestamp, last_instruction=instruction)
        write(root, row)
    return {**row, "result": "changed"}


def listing(root, status="open"):
    return [row for row in inventory(root) if status == "all" or row["status"] == status]


def add_parser(commands):
    parser = commands.add_parser("todo", help="personal to-do list, separate from knowledge")
    actions = parser.add_subparsers(dest="action", required=True)
    adding = actions.add_parser("add", help="save a to-do")
    adding.add_argument("title")
    adding.add_argument("--detail", help="optional detail text")
    adding.add_argument("--user-instruction", required=True)
    actions.add_parser("list").add_argument("--status", choices=(*STATUSES, "all"), default="open")
    actions.add_parser("show").add_argument("id")
    for action in ("done", "reopen", "remove"):
        command = actions.add_parser(action)
        command.add_argument("id")
        command.add_argument("--revision", type=int, required=True)
        command.add_argument("--user-instruction", required=True)


def cli(root, args):
    if args.action == "add":
        return create(root, args.title, args.user_instruction, args.detail)
    if args.action == "list":
        return listing(root, args.status)
    if args.action == "show":
        return select(root, args.id)
    return change(root, args.id, args.action, args.revision, args.user_instruction)
