"""Structural audits, reviewed repairs and retained outcomes through the shared core."""
from typing import Annotated, Literal

from pydantic import Field

from .. import brain, brain_maintenance
from .common import inventory_page, serialized
from .models import ListInput, Model, ReadInput


class BrainAuditInput(ListInput):
    section: Literal['findings', 'notes'] = 'findings'


class AuditNote(Model):
    path: str
    title: str
    status: str | None
    sha256: str


class AuditFinding(Model):
    kind: str
    path: str | None = None
    paths: list[str] | None = None
    link: str | None = None
    detail: str | None = None


class BrainAuditPage(Model):
    section: Literal['findings', 'notes']
    items: list[AuditFinding | AuditNote]
    next_cursor: str | None
    inventory_revision: str
    notes_total: int
    findings_total: int
    limitations: list[str]


def brain_audit(root, args):
    report = brain_maintenance.scan(root)
    revision = brain.digest(serialized(report))
    page, cursor = inventory_page(root, args, 'brain-audit', args.section,
                                  revision, report[args.section])
    item_type = AuditFinding if args.section == 'findings' else AuditNote
    omissions = [item['path'] for item in report['findings']
                 if item['kind'] == 'unreadable_note']
    return BrainAuditPage(section=args.section,
                         items=[item_type(**item) for item in page],
                         next_cursor=cursor, inventory_revision=revision,
                         notes_total=len(report['notes']),
                         findings_total=len(report['findings']),
                         limitations=report['limitations']), omissions


class RepairChange(Model):
    path: str = Field(min_length=1, max_length=512)
    expected_sha256: str = Field(pattern='^[a-f0-9]{64}$')
    body: str = Field(min_length=1, max_length=16000)
    links: list[Annotated[str, Field(max_length=512)]] = Field(max_length=100)


class BrainRepairPreviewInput(ReadInput):
    changes: list[RepairChange] = Field(min_length=1, max_length=20)
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)


class BrainRepairPreview(Model):
    proposal_sha256: str
    replacements: dict[str, str]
    applied: Literal[False] = False


def brain_repair_preview(root, args):
    proposal = {'changes': [change.model_dump() for change in args.changes]}
    result = brain_maintenance.repair(root, proposal)
    return BrainRepairPreview(**result), []


class BrainRepairStatusInput(ReadInput):
    proposal_sha256: str = Field(pattern='^[a-f0-9]{64}$')


class BrainRepairApplyInput(BrainRepairPreviewInput):
    expected_sha256: str = Field(pattern='^[a-f0-9]{64}$')
    user_instruction: str = Field(min_length=1, max_length=500)


class BrainRepairOutcome(Model):
    proposal_sha256: str
    status: Literal['unknown', 'prepared', 'completed', 'recovery_required']
    backup: str | None


def brain_repair_status(root, args):
    return BrainRepairOutcome(**brain_maintenance.repair_status(root, args.proposal_sha256)), []


def brain_repair_apply(root, args):
    proposal = {'changes': [change.model_dump() for change in args.changes]}
    result = brain_maintenance.repair(root, proposal, apply=True,
                                     expected=args.expected_sha256, instruction=args.user_instruction)
    return BrainRepairOutcome(proposal_sha256=result['proposal_sha256'],
                              status='completed', backup=result['backup']), []
