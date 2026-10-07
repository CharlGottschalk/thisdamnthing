"""Installed guide and skill discovery and read adapters."""
import json
from pathlib import Path
from .. import bootstrap, brain, frontmatter, skills, stack_docs, ui_resources
from ..workspace import managed_path
from .common import Refused, bounded_text, inventory_page, serialized, workspace_key
from .models import DocumentPage, DocumentRead, DocumentSummary
from .providers import installed_stacks


def stack_documents(root, args):
    return document_list(root, args, 'stack-docs')


def document_targets(root, category):
    installed = installed_stacks(root)
    targets = {}

    def add(path, identifier, owner):
        if path in targets:
            raise Refused('ownership_conflict', 'Document has multiple registered owners')
        targets[path] = (identifier, owner)
        if len(targets) > 2000:
            raise Refused('operation_refused', 'Document catalog exceeds 2000 entries')

    if category in ('guides', 'stack-docs'):
        for path in {**bootstrap.RESOURCES, **ui_resources.RESOURCES}:
            if category == 'guides' and path.startswith('docs/') and path.endswith('.md'):
                add(path, 'core/' + Path(path).stem, 'core')
            elif category == 'guides' and path == '.tdt/contracts/ui.md':
                add(path, 'core/contracts/ui', 'core')
        for stack_id, _, paths in stack_docs.documents(root, installed):
            for path in paths:
                add(f'.tdt/stacks/{stack_id}/{path}', f'{stack_id}/{path}', stack_id)
    else:
        for name in bootstrap.SKILLS:
            add(f'.tdt/skills/{name}/SKILL.md', name, 'core')
        state_path = managed_path(root, skills.STATE)
        state = (skills.validate_state(json.loads(bounded_text(root, skills.STATE, 2097152)))
                 if state_path.exists() else {'skills': {}})
        for name in state['skills']:
            add(f'.tdt/skills/{name}/SKILL.md', name, 'user')
        for entry in installed:
            for path in entry['files']:
                if path.startswith('.tdt/skills/') and path.endswith('/SKILL.md'):
                    add(path, Path(path).parent.name, entry['id'])
    return targets


def document_summary(root, category, path, identifier, owner):
    markdown = bounded_text(root, path, 65536)
    description = None
    if category == 'skills':
        if not markdown.startswith('---\n') or '\n---\n' not in markdown[4:]:
            raise Refused('operation_refused', 'Invalid canonical skill front matter')
        meta = frontmatter.loads(markdown[4:].split('\n---\n', 1)[0])
        if (not isinstance(meta, dict) or meta.get('name') != identifier
                or not isinstance(meta.get('description'), str)
                or not 1 <= len(meta['description'].strip()) <= 1024):
            raise Refused('operation_refused', 'Invalid canonical skill metadata')
        description = meta['description']
    item = DocumentSummary(id=identifier, path=path, owner=owner,
        uri=f'tdt://{workspace_key(root)}/{path}', revision=brain.digest(markdown),
        description=description)
    return item, markdown


def document_list(root, args, category):
    items, omissions = [], []
    for path, (identifier, owner) in sorted(document_targets(root, category).items()):
        if not managed_path(root, path).exists():
            omissions.append(path)
            continue
        item, _ = document_summary(root, category, path, identifier, owner)
        items.append(item)
    revision = brain.digest(serialized([[item.model_dump() for item in items], omissions]))
    page, cursor = inventory_page(root, args, category, 'all', revision, items)
    return DocumentPage(items=page, next_cursor=cursor, inventory_revision=revision), omissions


def document_read(root, args, category):
    for path, (identifier, owner) in document_targets(root, category).items():
        if args.reference in (identifier, path, f'tdt://{workspace_key(root)}/{path}'):
            if not managed_path(root, path).exists():
                raise Refused('not_found', 'Installed document is missing')
            item, markdown = document_summary(root, category, path, identifier, owner)
            return DocumentRead(**item.model_dump(), markdown=markdown), []
    raise Refused('not_found', 'No installed document matches this workspace reference')


def guides_list(root, args):
    return document_list(root, args, 'guides')


def guide_read(root, args):
    return document_read(root, args, 'guides')


def skill_list(root, args):
    return document_list(root, args, 'skills')


def skill_read(root, args):
    return document_read(root, args, 'skills')
