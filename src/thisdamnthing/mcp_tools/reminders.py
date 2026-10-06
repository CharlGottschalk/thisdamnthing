"""Reminder lifecycle, settings and delivery adapters."""
from .. import brain, reminders
from .common import Refused, inventory_page, serialized, workspace_key
from .models import (
    ReminderAcknowledged,
    ReminderChanged,
    ReminderClaims,
    ReminderConfigured,
    ReminderCreated,
    ReminderDelivery,
    ReminderPage,
    ReminderRead,
    ReminderSettings,
    ReminderSummary,
    Result,
)


def reminder_inventory(root):
    items, texts = [], {}
    for row in reminders.inventory(root, include_text=True):
        markdown = row['markdown']
        item = ReminderSummary(**{key: row[key] for key in
            ('id', 'path', 'status', 'title', 'due_at', 'timezone', 'notified_at')},
            uri=f"tdt://{workspace_key(root)}/{row['path']}",
            revision=brain.digest(markdown), reminder_revision=row['revision'],
            claimed=row['claim'] is not None)
        items.append(item)
        texts[item.id] = markdown
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    return items, texts, revision


def reminder_list(root, args):
    items, _, revision = reminder_inventory(root)
    selected = [item for item in items if args.status == 'all' or item.status == args.status]
    page, cursor = inventory_page(root, args, 'reminders', args.status, revision, selected)
    return ReminderPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def reminder_read(root, args):
    items, texts, _ = reminder_inventory(root)
    for item in items:
        if args.reference in (item.id, item.path, item.uri):
            return ReminderRead(**item.model_dump(), markdown=texts[item.id]), []
    raise Refused('not_found', 'No reminder matches this workspace reference')


def reminder_complete(root, args):
    return reminder_change(root, args, 'done')


def reminder_cancel(root, args):
    return reminder_change(root, args, 'cancel')


def reminder_create(root, args):
    data = args.model_dump(include={'title', 'body', 'due_at', 'timezone'})
    row = reminders.create(root, data, args.user_instruction)
    return ReminderCreated(id=row['id'], reminder_revision=row['revision'],
                           status=row['status'], result=row['result']), []


def reminder_edit(root, args):
    return reminder_change(root, args, 'edit')


def reminder_snooze(root, args):
    return reminder_change(root, args, 'snooze')


def reminder_change(root, args, action):
    data = args.changes.model_dump(exclude_unset=True) if action in ('edit', 'snooze') else None
    row = reminders.change(root, args.id, action, args.reminder_revision, args.user_instruction, data)
    # A fixed, small receipt fits even the minimum budget. No post-write reread.
    return ReminderChanged(id=row['id'], reminder_revision=row['revision'],
                           status=row['status']), []


def reminder_settings(root, args):
    value = reminders.settings(root)
    return ReminderSettings(**{key: value[key] for key in ('timezone', 'chat', 'schedule')}), []


def reminder_configure(root, args):
    brain.clean_text(args.user_instruction, 'user instruction/reference', 500)
    changes = args.changes.model_dump(exclude_unset=True)
    reminders.configure(root, tz=changes.get('timezone'), chat=changes.get('chat'),
                        schedule=changes.get('schedule'),
                        clear_schedule='schedule' in changes and changes['schedule'] is None)
    # Do not return potentially large settings after committing the write.
    return ReminderConfigured(), []


def reminder_claim_due(root, args):
    def receipt(rows):
        return ReminderClaims(items=[ReminderDelivery(
            id=row['id'], reminder_revision=row['revision'], title=row['title'],
            body=row['body'], due_at=row['due_at'], timezone=row['timezone'],
            token=row['claim']['token'], channel=row['claim']['channel'],
            expires_at=row['claim']['expires_at']) for row in rows])

    def before_write(rows):
        value = Result[ReminderClaims](data=receipt(rows)).model_dump()
        if len(serialized(value).encode('utf-8')) > args.budget_bytes:
            raise Refused('result_too_large',
                          'Claims exceed budget; increase budget_bytes or reduce limit. No claims written.')

    rows = reminders.check(root, args.channel, args.limit, before_write=before_write)
    return receipt(rows), []


def reminder_ack(root, args):
    return ReminderAcknowledged(**reminders.acknowledge(root, args.id, args.token)), []
