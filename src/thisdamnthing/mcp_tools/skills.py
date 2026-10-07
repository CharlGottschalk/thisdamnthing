"""Bounded retained skill proposal reads; never installs or executes skills."""
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
