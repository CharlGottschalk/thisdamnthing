"""Shared MCP bounds, serialization, workspace identity and pagination."""
import base64
import hashlib
import json
from .. import brain, constitution
from ..workspace import managed_path


class Refused(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message


def serialized(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def bounded_text(root, relative, limit):
    path = managed_path(root, relative)
    return constitution.bounded(path, limit)


def workspace_key(root):
    return hashlib.sha256(str(root).encode()).hexdigest()[:24]


def check_registry(root):
    # The existing core registry reader is unbounded; cap it before retrieval.
    bounded_text(root, '.tdt/state/projects.json', 262144)


def inventory_page(root, args, category, selection, revision, selected):
    binding = brain.digest(serialized([workspace_key(root), category, selection, args.limit, revision]))
    offset = 0
    if args.cursor is not None:
        try:
            value = json.loads(base64.b64decode(args.cursor, altchars=b'-_', validate=True))
            if (not isinstance(value, list) or len(value) != 2
                    or type(value[1]) is not int or value[1] < 0):
                raise ValueError('Invalid cursor')
            token, offset = value
        except (ValueError, TypeError):
            raise Refused('invalid_input', 'Invalid inventory cursor') from None
        if token != binding:
            raise Refused('stale_revision', 'Inventory or query changed; restart without a cursor')
    if offset > len(selected):
        raise Refused('invalid_input', 'Invalid inventory cursor offset')
    end = offset + args.limit
    cursor = (base64.urlsafe_b64encode(serialized([binding, end]).encode()).decode()
              if end < len(selected) else None)
    return selected[offset:end], cursor
