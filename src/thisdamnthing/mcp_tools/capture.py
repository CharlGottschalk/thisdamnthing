"""Hook capture request and turn-suppression adapters."""
import os
from pathlib import Path
from .. import brain, capture
from ..workspace import managed_path
from .common import Refused, inventory_page, serialized
from .models import CapturePage, CaptureRequest, CaptureSubmitted, CaptureSuppressed


def capture_request_value(root, key):
    request = brain.read_request(root, key)
    return CaptureRequest(id=key, status=request['status'], created=request['created'],
        completed=request.get('completed'), provenance=request['provenance'],
        revision=brain.digest(serialized(request)))


def capture_request_read(root, args):
    return capture_request_value(root, args.request_id), []


def capture_requests(root, args):
    directory = managed_path(root, '.tdt/state/captures')
    items = []
    if directory.exists():
        with os.scandir(directory) as entries:
            for count, entry in enumerate(entries, 1):
                if count > 2000:
                    raise Refused('operation_refused', 'Capture inventory exceeds 2000 entries')
                managed_path(root, str(Path(entry.path).relative_to(root)))
                if entry.name.endswith('.json'):
                    items.append(capture_request_value(root, brain.identifier(entry.name[:-5])))
    items.sort(key=lambda item: item.id)
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    selected = [item for item in items if args.status == 'all' or item.status == args.status]
    page, cursor = inventory_page(root, args, 'captures', args.status, revision, selected)
    return CapturePage(items=page, next_cursor=cursor, inventory_revision=revision), []


def capture_submit(root, args):
    data = ({'skip': True} if args.payload.action == 'skip'
            else args.payload.summary.model_dump())
    status = brain.capture(root, args.request_id, data).split(':', 1)[0]
    return CaptureSubmitted(id=args.request_id, status=status), []


def capture_suppress(root, args):
    capture.suppress_review_turn(root, args.token)
    return CaptureSuppressed(), []
