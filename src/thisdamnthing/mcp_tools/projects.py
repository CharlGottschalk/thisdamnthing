"""Project registration, inspection and proposal adapters."""
import json
from pathlib import Path
from typing import Literal
from pydantic import Field
from .. import brain, projects, project_lifecycle
from .common import Refused, bounded_text, inventory_page, serialized, workspace_key
from .models import (
    ListInput, Model, ReadInput,
    ProjectInspection,
    ProjectPage,
    ProjectProposed,
    ProjectRead,
    ProjectRegistered,
    ProjectSummary,
    Registration,
)


class ProjectReferencesInput(ListInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    section: Literal['references', 'skipped'] = 'references'


class ReferenceProject(Model):
    id: str
    path: str
    created: str | None = None
    status: Literal['active', 'archived'] | None = None


class ProjectReference(Model):
    path: str
    sha256: str
    matched: list[str]


class SkippedReference(Model):
    path: str
    reason: str


class ProjectReferencesPage(Model):
    project: ReferenceProject
    section: Literal['references', 'skipped']
    items: list[ProjectReference | SkippedReference]
    next_cursor: str | None
    inventory_revision: str
    references_total: int
    skipped_total: int
    scan_truncated: bool
    limitations: list[str]


def project_references(root, args):
    report = project_lifecycle.references(root, args.id)
    revision = brain.digest(serialized(report))
    page, cursor = inventory_page(root, args, 'project-references',
                                  [args.id, args.section], revision, report[args.section])
    item_type = ProjectReference if args.section == 'references' else SkippedReference
    omissions = ([f"{len(report['skipped'])} entries skipped; read the skipped section for details"]
                 if report['skipped'] else [])
    return ProjectReferencesPage(
        project=ReferenceProject(**report['project']), section=args.section,
        items=[item_type(**item) for item in page], next_cursor=cursor,
        inventory_revision=revision, references_total=len(report['references']),
        skipped_total=len(report['skipped']), scan_truncated=report['truncated'],
        limitations=report['limitations']), omissions


def project_add(root, args):
    # MCP paths must not depend on the server launch directory or host home.
    if not Path(args.path).is_absolute() or '..' in Path(args.path).parts:
        raise Refused('invalid_input', 'Use an absolute existing project directory without traversal')
    entry, created = projects.add(root, args.path)
    return ProjectRegistered(id=entry['id'], result='registered' if created else 'existing'), []


def project_create(root, args):
    entry, created = projects.create(root, args.relative_folder)
    return ProjectRegistered(id=entry['id'], result='registered' if created else 'existing'), []


def project_inspect(root, args):
    value = projects.inspect(root, args.id)
    omissions = [f"{doc['source']}: {doc['omitted']}" for doc in value['documents']
                 if doc.get('omitted')]
    omissions.extend(f"{doc['source']}: content truncated" for doc in value['documents']
                     if doc.get('truncated'))
    if value['inventory_truncated']:
        omissions.append('Project top-level inventory truncated at 100 names')
    return ProjectInspection(**value), omissions


def project_propose(root, args):
    return ProjectProposed(**projects.propose_record(root, args.id,
                                                    args.summary.model_dump())), []


def project_inventory(root):
    records = projects.validate_registry(json.loads(bounded_text(root, projects.REGISTRY, 262144)))
    if len(records) > 2000:
        raise Refused('operation_refused', 'Project inventory exceeds 2000 entries')
    items = []
    for entry in sorted(records, key=lambda entry: entry['id']):
        value = dict(id=entry['id'], uri=f"tdt://{workspace_key(root)}/projects/{entry['id']}",
                     path=entry['path'], created=entry['created'],
                     status=entry.get('status', 'active'), availability=projects.status(entry))
        items.append(ProjectSummary(**value, revision=brain.digest(serialized(value))))
    return items, brain.digest(serialized([item.model_dump() for item in items]))


def project_list(root, args):
    items, revision = project_inventory(root)
    page, cursor = inventory_page(root, args, 'project_registry', 'all', revision, items)
    return ProjectPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def project_read(root, args):
    items, _ = project_inventory(root)
    # Exact registered references only; project paths are never opened for content.
    selected = next((item for item in items if args.reference in
                     (item.id, item.uri, item.path)), None)
    if selected is None:
        raise Refused('not_found', 'No registered project matches this workspace reference')
    omissions, matches = [], []
    for path in brain.note_files(root, ('projects',)):
        try:
            meta, _, markdown = brain.read_note(root, path, include_text=True)
        except brain.NoteError:
            omissions.append(path)
            continue
        if meta['id'] == selected.id:
            if meta['status'] != 'approved' or meta.get('project') != selected.id:
                raise Refused('operation_refused', 'Invalid project registration note')
            matches.append(Registration(path=path, uri=f'tdt://{workspace_key(root)}/{path}',
                                        revision=brain.digest(markdown), markdown=markdown))
    if len(matches) > 1:
        raise Refused('operation_refused', 'Duplicate project registration notes')
    return ProjectRead(project=selected, registration=matches[0] if matches else None,
                       registration_status='available' if matches else 'missing'), omissions


class ProjectLifecycleInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)


class ProjectRemovePreviewInput(ProjectLifecycleInput):
    mode: Literal['archive', 'unregister']


class ProjectRelinkPreviewInput(ProjectLifecycleInput):
    path: str = Field(min_length=1, max_length=400)


class ProjectStatePreview(Model):
    operation: Literal['remove', 'restore']
    project: ReferenceProject
    state: Literal['active', 'archived', 'removed']
    notice: str
    proposal_sha256: str
    replacements: dict[str, str]
    applied: Literal[False] = False


class ProjectRelinkPreview(Model):
    operation: Literal['relink']
    previous: ReferenceProject
    project: ReferenceProject
    brain_link: str
    notice: str
    proposal_sha256: str
    replacements: dict[str, str]
    applied: Literal[False] = False


def project_remove_preview(root, args):
    return ProjectStatePreview(**project_lifecycle.remove(
        root, args.id, permanent=args.mode == 'unregister')), []


def project_restore_preview(root, args):
    return ProjectStatePreview(**project_lifecycle.remove(root, args.id, restore=True)), []


def project_relink_preview(root, args):
    if not Path(args.path).is_absolute() or '..' in Path(args.path).parts:
        raise Refused('invalid_input', 'Use an absolute existing project directory without traversal')
    return ProjectRelinkPreview(**project_lifecycle.relink(root, args.id, args.path)), []


class ProjectOperationStatusInput(ReadInput):
    proposal_sha256: str = Field(pattern='^[a-f0-9]{64}$')


class ProjectApplyInput(ProjectLifecycleInput):
    expected_sha256: str = Field(pattern='^[a-f0-9]{64}$')
    user_instruction: str = Field(min_length=1, max_length=500)


class ProjectRemoveApplyInput(ProjectApplyInput):
    mode: Literal['archive', 'unregister']


class ProjectRelinkApplyInput(ProjectApplyInput):
    path: str = Field(min_length=1, max_length=400)


class ProjectOperationOutcome(Model):
    proposal_sha256: str
    status: Literal['unknown', 'prepared', 'completed', 'recovery_required']
    backup: str | None
    operation: Literal['remove', 'restore', 'relink'] | None
    project_id: str | None


def project_operation_status(root, args):
    return ProjectOperationOutcome(**project_lifecycle.operation_status(root, args.proposal_sha256)), []


def lifecycle_receipt(result):
    return ProjectOperationOutcome(proposal_sha256=result['proposal_sha256'], status='completed',
                                   backup=result['backup'], operation=result['operation'],
                                   project_id=result['project']['id']), []


def project_remove_apply(root, args):
    return lifecycle_receipt(project_lifecycle.remove(
        root, args.id, permanent=args.mode == 'unregister', apply=True,
        expected=args.expected_sha256, instruction=args.user_instruction))


def project_restore_apply(root, args):
    return lifecycle_receipt(project_lifecycle.remove(
        root, args.id, restore=True, apply=True,
        expected=args.expected_sha256, instruction=args.user_instruction))


def project_relink_apply(root, args):
    if not Path(args.path).is_absolute() or '..' in Path(args.path).parts:
        raise Refused('invalid_input', 'Use an absolute existing project directory without traversal')
    return lifecycle_receipt(project_lifecycle.relink(
        root, args.id, args.path, apply=True,
        expected=args.expected_sha256, instruction=args.user_instruction))
