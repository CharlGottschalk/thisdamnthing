"""Bounded skill inspection and shared-core proposal/review operations."""
import json
from typing import Annotated, Literal

from pydantic import Field

from .. import brain, skills
from ..workspace import managed_path
from .common import Refused, bounded_text, inventory_page, serialized
from .models import ListInput, Model, ReadInput


class SkillProposalListInput(ListInput):
    status: Literal['pending', 'approved', 'declined', 'all'] = 'pending'


class SkillProposalInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')


class SkillProposeInput(ReadInput):
    name: str = Field(max_length=64, pattern=r'^tdt-[a-z0-9]+(?:-[a-z0-9]+)*$')
    description: str = Field(min_length=1, max_length=1024)
    instructions: str = Field(min_length=1, max_length=10000)
    sources: list[Annotated[str, Field(max_length=160, pattern=r'^[^\n]*$')]] = Field(default_factory=list, max_length=40)
    update: bool = False


class SkillReviewInput(SkillProposalInput):
    decision: Literal['approve', 'decline']
    user_instruction: str = Field(min_length=1, max_length=300)


class SkillSaved(Model):
    id: str
    status: Literal['pending', 'approved', 'declined']


def skill_propose(root, args):
    proposal = skills.propose(root, args.model_dump(
        include={'name', 'description', 'instructions', 'sources'}), update=args.update)
    # A fixed-size receipt fits even the minimum budget after a successful write.
    return SkillSaved(id=proposal['id'], status=proposal['status']), []


def skill_review(root, args):
    skills.review(root, [args.id], args.decision, args.user_instruction)
    return SkillSaved(id=args.id, status='approved' if args.decision == 'approve' else 'declined'), []


class SkillProposalSummary(Model):
    id: str
    name: str
    description: str
    status: Literal['pending', 'approved', 'declined']
    revision: str


class SkillProposalRead(SkillProposalSummary):
    instructions: str
    sources: list[Annotated[str, Field(max_length=160, pattern=r'^[^\n]*$')]] = Field(max_length=40)
    before: dict[str, str] | None
    decision_reference: str | None = Field(default=None, max_length=300)
    current_ownership: dict[str, str] | None


class SkillProposalPage(Model):
    items: list[SkillProposalSummary]
    next_cursor: str | None
    inventory_revision: str


class SkillInventoryItem(Model):
    name: str
    path: str
    owner: str
    content: str
    truncated: bool


class SkillInventoryPage(Model):
    items: list[SkillInventoryItem]
    next_cursor: str | None
    inventory_revision: str


def skill_inventory(root, args):
    with brain.locked(root, shared=True):
        rows = skills.inventory(root)['skills']
        revision = brain.digest(serialized(rows))
        items = [SkillInventoryItem(**row) for row in rows]
        page, cursor = inventory_page(root, args, 'skill-inventory', 'all', revision, items)
        omissions = [f'{item.path}: content limited to 16384 characters'
                     for item in page if item.truncated]
        return SkillInventoryPage(items=page, next_cursor=cursor,
                                  inventory_revision=revision), omissions


def proposal_records(root):
    skills.ready(root)
    path = managed_path(root, skills.STATE)
    state = (skills.validate_state(json.loads(bounded_text(root, skills.STATE, 2097152)))
             if path.exists() else {'skills': {}, 'proposals': {}})
    records = []
    for key, proposal in sorted(state['proposals'].items()):
        if set(proposal) - {'name', 'description', 'instructions', 'status', 'sources',
                            'before', 'decision_reference'}:
            raise Refused('operation_refused', 'Invalid retained skill proposal fields')
        owned = state['skills'].get(proposal['name'])
        records.append(SkillProposalRead(id=key,
            revision=brain.digest(serialized([proposal, owned])),
            current_ownership=owned, **proposal))
    return records


def skill_proposals(root, args):
    with brain.locked(root, shared=True):
        records = proposal_records(root)
        revision = brain.digest(serialized([record.model_dump() for record in records]))
        items = [SkillProposalSummary(**{field: getattr(record, field)
                 for field in SkillProposalSummary.model_fields}) for record in records
                 if args.status == 'all' or record.status == args.status]
        page, cursor = inventory_page(root, args, 'skill-proposals', args.status, revision, items)
        return SkillProposalPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def skill_proposal_read(root, args):
    with brain.locked(root, shared=True):
        for record in proposal_records(root):
            if record.id == args.id:
                return record, []
    raise Refused('not_found', 'No retained skill proposal matches this ID')
