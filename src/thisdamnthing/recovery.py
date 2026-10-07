"""Bounded journal reads and preview binding for transaction recovery."""
import hashlib
import json
import os
import stat

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
    path = managed_path(root, relative)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise WorkspaceError('Recovery requires regular files')
        value = stream.read(limit + 1)
    if len(value) > limit:
        raise WorkspaceError('Recovery inspection exceeds file limit or conflicts with journal')
    return value
