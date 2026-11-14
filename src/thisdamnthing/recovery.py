"""Bounded journal reads and preview binding for transaction recovery."""
import hashlib
import json

from . import safefs
from .workspace import WorkspaceError, managed_path


def journal_digest(record):
    return hashlib.sha256(json.dumps(record, ensure_ascii=False,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def check_preview(record, expected_sha256):
    if expected_sha256 is not None and (
            record is None or journal_digest(record) != expected_sha256):
        raise WorkspaceError('Recovery journal changed or absent; inspect again')


def read_journal(root, relative):
    raw = read_bytes(root, relative, 8 * 1024 * 1024)
    if raw is None:
        raise WorkspaceError('Recovery journal disappeared; inspect again')
    return json.loads(raw)


def read_bytes(root, relative, limit):
    try:
        value = safefs.read_file(managed_path(root, relative), limit + 1)
    except FileNotFoundError:
        return None
    except safefs.NotRegular as exc:
        raise WorkspaceError('Recovery requires regular files') from exc
    if len(value) > limit:
        raise WorkspaceError('Recovery inspection exceeds file limit or conflicts with journal')
    return value
