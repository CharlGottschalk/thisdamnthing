"""Explicit UI lifecycle adapters; answers remain untrusted session data."""
from pydantic import Field, JsonValue
from .. import ui
from .models import Model, ReadInput


class UIInput(ReadInput):
    # A complete page and event can exceed the ordinary retrieval budget.
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)
    session_id: str = Field(pattern='^[a-f0-9]{32}$')


class UIStartInput(ReadInput):
    session_id: str | None = Field(default=None, pattern='^[a-f0-9]{32}$')
    idle: int = Field(default=1800, ge=30, le=3600)
    open_browser: bool = False


class UIPresentInput(UIInput):
    page: dict[str, JsonValue]


class UIReadInput(UIInput):
    after: int = Field(default=0, ge=0, le=1000)
    limit: int = Field(default=1, ge=1, le=20)


class UIWaitInput(UIReadInput):
    timeout: int = Field(default=20, ge=0, le=30)


class UIAckInput(UIInput):
    event_id: int = Field(ge=0, le=1000)


class UIStarted(Model):
    session_id: str
    url: str
    browser_opened: bool
    status: str


class UIPresented(Model):
    round_id: str
    status: str


class UIStatus(Model):
    session_id: str
    status: str
    connected: bool
    round_id: str | None
    ack: int


class UIEvents(Model):
    events: list[dict[str, JsonValue]]
    prompts: dict[str, JsonValue]
    ack: int
    status: str
    timed_out: bool
    next_after: int
    has_more: bool


class UIAcknowledged(Model):
    ack: int


class UIClosed(Model):
    status: str


class UICleaned(Model):
    deleted: str


def ui_start(root, args):
    return UIStarted(**ui.start(root, args.session_id, args.idle, not args.open_browser)), []


def ui_present(root, args):
    return UIPresented(**ui.present(root, args.session_id, args.page)), []


def ui_status(root, args):
    value = ui.status(root, args.session_id)
    return UIStatus(**{key: value[key] for key in UIStatus.model_fields}), []


def ui_read(root, args):
    value = ui.read_events(root, args.session_id, args.after, getattr(args, 'timeout', 0))
    events = value['events'][:args.limit]
    value.update(events=events, prompts={e['round_id']: value['prompts'][e['round_id']] for e in events},
                 next_after=events[-1]['event_id'] if events else args.after,
                 has_more=len(value['events']) > len(events))
    return UIEvents(**value), []


def ui_ack(root, args):
    return UIAcknowledged(**ui.change_session(root, args.session_id, 'ack', args.event_id)), []


def ui_close(root, args):
    return UIClosed(**ui.change_session(root, args.session_id, 'close')), []


def ui_cleanup(root, args):
    return UICleaned(**ui.cleanup(root, args.session_id)), []
