"""Workspace policy, context and operational status adapters."""
import json
import os
from pathlib import Path
from pydantic import Field
from .. import brain, constitution, reminders
from ..workspace import managed_path
from .common import Refused, bounded_text, workspace_key
from .knowledge import stored_inventory
from .models import Context, Model, Policy, ReadInput, WorkspaceStatus
from .projects import project_inventory


class PolicySaveInput(ReadInput):
    markdown: str = Field(min_length=1, max_length=6000)
    expected_sha256: str = Field(pattern=r'^(missing|[a-f0-9]{64})$')
    user_instruction: str = Field(min_length=1, max_length=240)


class PolicySaved(Model):
    sha256: str


def policy_save(root, args):
    saved = constitution.save(root, args.markdown, args.expected_sha256,
                              args.user_instruction)
    # Complete policy can exceed the minimum budget; return only its revision
    # so successful writes never become output-budget errors.
    return PolicySaved(sha256=saved['sha256']), []


def policy_read(root, args):
    return Policy(**constitution.load(root)), []


def context_read(root, args):
    from .catalog import CATALOG

    policy = Policy(**constitution.load(root))
    work = managed_path(root, 'WORK.md')
    filing = bounded_text(root, 'WORK.md', 32768) if work.exists() else None
    return Context(workspace_key=workspace_key(root), policy=policy,
                   filing_conventions=filing, tools=list(CATALOG)), []


def workspace_status(root, args):
    observed = brain.now()
    markers = [path for path in ('.tdt/state/stack-transaction.json',
               '.tdt/state/user-skill-transaction.json') if managed_path(root, path).exists()]
    items, _ = project_inventory(root)
    incomplete = 0
    captures = managed_path(root, '.tdt/state/captures')
    if captures.exists():
        with os.scandir(captures) as entries:
            for count, entry in enumerate(entries, 1):
                if count > 2000:
                    raise Refused('operation_refused', 'Capture inventory exceeds 2000 entries')
                relative = str(Path(entry.path).relative_to(root))
                managed_path(root, relative)
                if not entry.name.endswith('.json'):
                    continue
                key = brain.identifier(entry.name[:-5])
                request = brain.validate_request(json.loads(bounded_text(root, relative, 32768)), key)
                incomplete += request['status'] == 'requested'
    omissions = []
    pending = due = None
    if '.tdt/state/stack-transaction.json' in markers:
        # Core inventories refuse interrupted transactions; do not hide the marker
        # behind that refusal or present unobserved counts as zero.
        omissions.extend(['brain/candidates', 'work/reminders'])
    else:
        candidates, omissions, _ = stored_inventory(root, 'candidates')
        pending = sum(item.status == 'pending' for item in candidates)
        current = reminders.instant(observed)
        due = sum(row['status'] == 'pending' and reminders.instant(row['due_at']) <= current
                  for row in reminders.inventory(root))
    return WorkspaceStatus(workspace_key=workspace_key(root), observed_at=observed,
        pending_candidates=pending, incomplete_captures=incomplete,
        projects_total=len(items), projects_available=sum(x.availability == 'available' for x in items),
        projects_missing=sum(x.availability == 'missing or moved' for x in items),
        projects_archived=sum(x.status == 'archived' for x in items), due_reminders=due,
        recovery_markers=markers), omissions
