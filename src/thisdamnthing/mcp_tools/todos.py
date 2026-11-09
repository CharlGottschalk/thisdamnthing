"""Personal to-do adapters over the shared core."""
from typing import Literal

from pydantic import Field

from .. import brain, todos
from .common import Refused, inventory_page, serialized
from .models import ListInput, Model, ReadInput

Status = Literal['open', 'done']


class TodoListInput(ListInput):
    status: Literal['open', 'done', 'all'] = 'open'


class TodoReadInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{8,64}$')


class TodoSummary(Model):
    id: str
    path: str
    title: str
    status: Status
    todo_revision: int
    created: str
    updated: str
    completed: str | None


class TodoRead(TodoSummary):
    body: str


class TodoPage(Model):
    items: list[TodoSummary]
    next_cursor: str | None = None
    inventory_revision: str


class TodoCreateInput(ReadInput):
    title: str = Field(min_length=1, max_length=160)
    body: str | None = Field(default=None, min_length=1, max_length=8000)
    user_instruction: str = Field(min_length=1, max_length=500)


class TodoChangeInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    todo_revision: int = Field(ge=1, le=9223372036854775806)
    user_instruction: str = Field(min_length=1, max_length=500)


class TodoChanged(Model):
    id: str
    todo_revision: int
    status: Status
    result: Literal['saved', 'existing', 'changed', 'removed']


def summary(row, model=TodoSummary, **extra):
    return model(id=row['id'], path=row['path'], title=row['title'], status=row['status'],
                 todo_revision=row['revision'], created=row['created'], updated=row['updated'],
                 completed=row.get('completed'), **extra)


def todo_list(root, args):
    items = [summary(row) for row in todos.listing(root, args.status)]
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    page, cursor = inventory_page(root, args, 'todos', args.status, revision, items)
    return TodoPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def todo_read(root, args):
    try:
        row = todos.select(root, args.id)
    except todos.WorkspaceError:
        raise Refused('not_found', 'No single to-do matches this id') from None
    return summary(row, TodoRead, body=row['body']), []


def changed(row):
    return TodoChanged(id=row['id'], todo_revision=row['revision'], status=row['status'], result=row['result'])


def todo_add(root, args):
    return changed(todos.create(root, args.title, args.user_instruction, args.body)), []


def todo_done(root, args):
    return changed(todos.change(root, args.id, 'done', args.todo_revision, args.user_instruction)), []


def todo_reopen(root, args):
    return changed(todos.change(root, args.id, 'reopen', args.todo_revision, args.user_instruction)), []


def todo_remove(root, args):
    return changed(todos.change(root, args.id, 'remove', args.todo_revision, args.user_instruction)), []
