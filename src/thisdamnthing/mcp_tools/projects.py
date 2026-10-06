"""Project registration, inspection and proposal adapters."""
import json
from pathlib import Path
from .. import brain, projects
from .common import Refused, bounded_text, inventory_page, serialized, workspace_key
from .models import (
    ProjectInspection,
    ProjectPage,
    ProjectProposed,
    ProjectRead,
    ProjectRegistered,
    ProjectSummary,
    Registration,
)


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
