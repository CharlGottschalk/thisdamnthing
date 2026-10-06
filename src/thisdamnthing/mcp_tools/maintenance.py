"""Read-only, paginated structural brain audits through the shared core."""
from typing import Literal

from .. import brain, brain_maintenance
from .common import inventory_page, serialized
from .models import ListInput, Model


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
