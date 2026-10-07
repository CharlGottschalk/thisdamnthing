"""Explicit, recoverable migration of legacy hash filenames and current links."""
import json
from pathlib import Path
import re

from . import brain, constitution, frontmatter, stacks
from .workspace import WorkspaceError, managed_path


LIMIT = 8 * 1024 * 1024


def outcome_path(fingerprint):
    return '.tdt/state/brain-names/' + brain.identifier(fingerprint) + '.json'


def fingerprint_for(before, after, renames):
    return brain.digest(json.dumps({'before': before, 'after': after, 'renames': renames},
                                  sort_keys=True))


def valid_path(root, relative):
    stacks.safe_path(relative)
    if not (relative in ('brain/index.md', stacks.REGISTRY, '.tdt/stack-docs.md',
                         '.tdt/state/stack-docs.json') or
            (relative.startswith(('brain/candidates/', 'brain/knowledge/', 'brain/projects/',
                                  'brain/sessions/', 'work/notes/')) and relative.endswith('.md'))):
        raise WorkspaceError('Invalid migration outcome path')
    managed_path(root, relative)


def retained_outcome(root, fingerprint):
    path = managed_path(root, outcome_path(fingerprint))
    if not path.exists():
        return None
    record = json.loads(constitution.bounded(path, LIMIT))
    if (not isinstance(record, dict)
            or set(record) != {'created', 'user_instruction', 'proposal_sha256',
                               'before', 'after', 'renames', 'status'}
            or record['proposal_sha256'] != fingerprint
            or record['status'] not in ('prepared', 'completed')
            or not isinstance(record['before'], dict) or not isinstance(record['after'], dict)
            or record['before'].keys() != record['after'].keys()
            or not isinstance(record['renames'], dict)
            or any(v is not None and not isinstance(v, str)
                   for v in (*record['before'].values(), *record['after'].values()))
            or fingerprint_for(record['before'], record['after'], record['renames']) != fingerprint):
        raise WorkspaceError('Invalid retained migration outcome')
    for relative in record['before']:
        valid_path(root, relative)
    for old, new in record['renames'].items():
        if (not isinstance(new, str) or old not in record['after']
                or new not in record['after'] or record['after'][old] is not None
                or not isinstance(record['after'][new], str)):
            raise WorkspaceError('Invalid retained migration rename')
    brain.clean_text(record['user_instruction'], 'retained instruction', 500)
    if not isinstance(record['created'], str):
        raise WorkspaceError('Invalid retained migration timestamp')
    return record


def migration_status(root, fingerprint):
    with brain.locked(root, shared=True):
        record = retained_outcome(root, fingerprint)
        from .skills import JOURNAL as SKILL_JOURNAL
        recovery = any(managed_path(root, p).exists() for p in (stacks.JOURNAL, SKILL_JOURNAL))
        return {'proposal_sha256': fingerprint,
                'status': 'recovery_required' if recovery else record['status'] if record else 'unknown',
                'backup': outcome_path(fingerprint) if record else None}


def migrate(root, apply=False, *, include_replacements=False, expected=None, instruction=None):
    with brain.locked(root, shared=not apply):
        entries = stacks.available(root)
        retained = None
        if apply:
            brain.identifier(expected)
            instruction = brain.clean_text(instruction, 'user instruction/reference', 500)
            retained = retained_outcome(root, expected)
            if retained:
                if retained['user_instruction'] != instruction:
                    raise WorkspaceError('Retained migration requires the identical instruction')
                if retained['status'] == 'completed':
                    return {'proposal_sha256': expected, 'applied': True,
                            'backup': outcome_path(expected)}
        files = brain.note_files(root)
        notes = {path: brain.read_note(root, path) for path in files}
        seen = set()
        renames = {}
        for path, (meta, _) in notes.items():
            category = path.split('/')[1]
            identity = (category, meta['id'])
            if identity in seen:
                raise WorkspaceError(f'Duplicate note identity in {category}: {meta["id"]}')
            seen.add(identity)
            if Path(path).stem == meta['id']:
                renames[path] = brain.named_path(root, category, meta['id'], meta['title'], renames.values())
        links = {brain.note_link(old): brain.note_link(new) for old, new in renames.items()}

        def wikilinks(text):
            # Preserve optional aliases, headings and embed markers verbatim.
            return re.sub(r'\[\[([^\]|#]+)([^\]]*)\]\]',
                          lambda m: '[[' + links.get(m[1], m[1]) + m[2] + ']]', text)

        changes = {}
        for path, (meta, _) in notes.items():
            original = managed_path(root, path).read_text(encoding='utf-8')
            head, body = original[4:].split('\n---\n', 1)
            updated = dict(meta)
            if isinstance(meta.get('links'), list):
                if any(not isinstance(link, str) for link in meta['links']):
                    raise WorkspaceError(f'Invalid note links: {path}')
                updated['links'] = [links.get(link, link) for link in meta['links']]
            if isinstance(meta.get('canonical'), str):
                updated['canonical'] = links.get(meta['canonical'], meta['canonical'])
            # Review snapshots and source/provenance references are historical evidence.
            destination = renames.get(path, path)
            rewritten_body = wikilinks(body)
            changed = updated != meta or rewritten_body != body or destination != path
            header = frontmatter.dumps(updated) if changed else head
            content = '---\n' + header + '\n---\n' + rewritten_body
            if len(content.encode('utf-8')) > 32768:
                raise WorkspaceError(f'Migrated note exceeds 32 KiB: {path}')
            if destination != path:
                changes[destination] = content
                changes[path] = None
            elif content != original:
                changes[path] = content

        index = managed_path(root, 'brain/index.md')
        if index.exists():
            if index.stat().st_size > 32768:
                raise WorkspaceError('Brain index exceeds 32 KiB')
            original = index.read_text(encoding='utf-8')
            content = wikilinks(original)
            if content != original:
                changes['brain/index.md'] = content
        registry_changed = False
        for entry in entries:
            old = entry.get('candidates', [])
            if not isinstance(old, list) or any(not isinstance(path, str) for path in old):
                raise WorkspaceError('Invalid stack candidate references')
            new = [renames.get(path, path) for path in old]
            if new != old:
                entry['candidates'] = new
                registry_changed = True
        if registry_changed:
            changes[stacks.REGISTRY] = json.dumps(entries, indent=2, ensure_ascii=False) + '\n'
        # Include all derived transaction writes in the reviewed hash and backup.
        if registry_changed:
            from . import stack_docs
            changes = {**changes, **stack_docs.plan(root, entries, changes)}
        before = {}
        for relative in changes:
            valid_path(root, relative)
            path = managed_path(root, relative)
            before[relative] = constitution.bounded(path, LIMIT) if path.exists() else None
        fingerprint = fingerprint_for(before, changes, renames)
        result = {'renames': renames, 'updated_files': [p for p in changes if p not in renames],
                  'proposal_sha256': fingerprint, 'applied': False}
        if include_replacements:
            result['replacements'] = changes
        if not apply:
            return result
        if expected != fingerprint:
            raise WorkspaceError('Migration changed; preview and approve again')
        backup = outcome_path(fingerprint)
        record = retained or {'created': brain.now(), 'user_instruction': instruction,
                              'proposal_sha256': fingerprint, 'before': before, 'after': changes,
                              'renames': renames, 'status': 'prepared'}
        completed = json.dumps({**record, 'status': 'completed'}, indent=2, ensure_ascii=False) + '\n'
        if len(completed.encode('utf-8')) > LIMIT:
            raise WorkspaceError('Migration backup exceeds 8 MiB; nothing written')
        if not retained:
            brain.save_json(root, backup, record)
        stacks.transaction(root, {**changes, backup: completed})
        return {'proposal_sha256': fingerprint, 'applied': True, 'backup': backup}
