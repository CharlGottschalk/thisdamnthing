"""Cross-project relay adapters over the shared core."""
from typing import Literal

from pydantic import Field

from .. import brain, relays
from .common import Refused, inventory_page, serialized
from .models import ListInput, Model, ReadInput

Status = Literal['open', 'done', 'cancelled']


class RelayListInput(ListInput):
    project: str | None = Field(default=None, min_length=1, max_length=400)
    status: Literal['open', 'done', 'cancelled', 'all'] = 'open'


class RelayReadInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{8,64}$')


class RelaySummary(Model):
    id: str
    path: str
    title: str
    status: Status
    from_project: str
    to_project: str
    from_label: str
    to_label: str
    origin: str | None
    resolution: str | None
    relay_revision: int
    created: str
    updated: str


class RelayRead(RelaySummary):
    body: str


class RelayPage(Model):
    items: list[RelaySummary]
    next_cursor: str | None = None
    inventory_revision: str


class RelayCreateInput(ReadInput):
    from_project: str = Field(min_length=1, max_length=400)
    to_project: str = Field(min_length=1, max_length=400)
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=16000)
    origin: str | None = Field(default=None, min_length=1, max_length=500)
    user_instruction: str = Field(min_length=1, max_length=500)


class RelayCloseInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    relay_revision: int = Field(ge=1, le=9223372036854775806)
    resolution: str | None = Field(default=None, min_length=1, max_length=500)
    user_instruction: str = Field(min_length=1, max_length=500)


class RelayChanged(Model):
    id: str
    relay_revision: int
    status: Status
    result: Literal['saved', 'existing', 'closed'] = 'closed'


def summary(row, names, model=RelaySummary, **extra):
    return model(id=row['id'], path=row['path'], title=row['title'], status=row['status'],
                 from_project=row['from'], to_project=row['to'],
                 from_label=names.get(row['from'], 'unknown project'),
                 to_label=names.get(row['to'], 'unknown project'),
                 origin=row['origin'], resolution=row['resolution'], relay_revision=row['revision'],
                 created=row['created'], updated=row['updated'], **extra)


def relay_list(root, args):
    names = relays.labels(root)
    items = [summary(row, names) for row in relays.listing(root, args.project, args.status)]
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    selection = serialized([args.project, args.status])
    page, cursor = inventory_page(root, args, 'relays', selection, revision, items)
    return RelayPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def relay_read(root, args):
    try:
        row = relays.select(root, args.id)
    except relays.WorkspaceError:
        raise Refused('not_found', 'No single relay matches this id') from None
    return summary(row, relays.labels(root), RelayRead, body=row['body']), []


def relay_create(root, args):
    row = relays.create(root, args.from_project, args.to_project, args.title, args.body,
                        args.user_instruction, args.origin)
    return RelayChanged(id=row['id'], relay_revision=row['revision'], status=row['status'],
                        result=row['result']), []


def relay_close(root, args, action):
    row = relays.close(root, args.id, action, args.relay_revision, args.user_instruction, args.resolution)
    return RelayChanged(id=row['id'], relay_revision=row['revision'], status=row['status']), []


def relay_done(root, args):
    return relay_close(root, args, 'done')


def relay_cancel(root, args):
    return relay_close(root, args, 'cancel')
