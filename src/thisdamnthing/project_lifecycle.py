"""Explicit project relocation, archival and reviewed reference cleanup."""
import json
import os
from pathlib import Path
import stat

from . import brain, constitution, frontmatter, projects, stacks
from .workspace import WorkspaceError, managed_path

LIMIT = 262144
OUTCOME_LIMIT = 8 * 1024 * 1024


def text_file(root, relative):
    path = managed_path(root, relative)
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise WorkspaceError(f'Not a regular file: {relative}')
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT or b'\0' in raw:
        raise WorkspaceError(f'Not bounded text (maximum 256 KiB): {relative}')
    return raw.decode('utf-8')


def outcome_path(fingerprint):
    return '.tdt/state/project-operations/' + brain.identifier(fingerprint) + '.json'


def retained_outcome(root, fingerprint):
    path = managed_path(root, outcome_path(fingerprint))
    if not path.exists():
        return None
    record = json.loads(constitution.bounded(path, OUTCOME_LIMIT))
    if (not isinstance(record, dict)
            or set(record) != {'created', 'operation', 'user_instruction', 'proposal_sha256',
                               'request_sha256', 'before', 'after', 'status', 'details'}
            or record['proposal_sha256'] != fingerprint
            or record['operation'] not in ('remove', 'restore', 'relink', 'cleanup')
            or record['status'] not in ('prepared', 'completed')
            or not isinstance(record['before'], dict) or not isinstance(record['after'], dict)
            or not record['before'] or record['before'].keys() != record['after'].keys()
            or any(not isinstance(v, str) for v in record['before'].values())
            or any(not isinstance(v, str) and not (record['operation'] == 'cleanup' and v is None)
                   for v in record['after'].values())
            or brain.digest(json.dumps({'operation': record['operation'], 'before': record['before'],
                                        'after': record['after']}, sort_keys=True)) != fingerprint):
        raise WorkspaceError('Invalid retained project outcome')
    for relative in record['before']:
        stacks.safe_path(relative)
        if (not relative.startswith(('brain/', 'work/')) if record['operation'] == 'cleanup'
                else relative != projects.REGISTRY and not (relative.startswith('brain/') and relative.endswith('.md'))):
            raise WorkspaceError('Invalid retained project replacement path')
    brain.identifier(record['request_sha256'])
    brain.clean_text(record['user_instruction'], 'retained instruction', 500)
    details = record['details']
    if not isinstance(record['created'], str) or not isinstance(details, dict):
        raise WorkspaceError('Invalid retained project details')
    expected_keys = ({'previous', 'project', 'brain_link', 'notice'} if record['operation'] == 'relink'
                     else {'project', 'coverage'} if record['operation'] == 'cleanup'
                     else {'project', 'state', 'notice'})
    if set(details) != expected_keys or (record['operation'] != 'cleanup' and not isinstance(details['notice'], str)):
        raise WorkspaceError('Invalid retained project details')
    if record['operation'] == 'cleanup':
        project = details['project']
        if isinstance(project, dict) and set(project) == {'id', 'path'}:
            projects.validate_registry([{**project, 'created': record['created']}])
        else:
            projects.validate_registry([project])
        coverage = details['coverage']
        if (not isinstance(coverage, dict) or set(coverage) != {'truncated', 'skipped'}
                or not isinstance(coverage['truncated'], bool) or not isinstance(coverage['skipped'], list)
                or any(not isinstance(item, dict) or set(item) != {'path', 'reason'}
                       or any(not isinstance(v, str) for v in item.values()) for item in coverage['skipped'])):
            raise WorkspaceError('Invalid retained cleanup coverage')
        return record
    projects.validate_registry([details['project']])
    if record['operation'] == 'relink':
        projects.validate_registry([details['previous']])
        if not isinstance(details['brain_link'], str):
            raise WorkspaceError('Invalid retained project link')
    elif details['state'] not in ('active', 'archived', 'removed'):
        raise WorkspaceError('Invalid retained project state')
    return record


def operation_status(root, fingerprint):
    """Historical completion is meaningful only after shared journal recovery."""
    with brain.locked(root, shared=True):
        record = retained_outcome(root, fingerprint)
        from .skills import JOURNAL as SKILL_JOURNAL
        recovery = any(managed_path(root, p).exists() for p in (stacks.JOURNAL, SKILL_JOURNAL))
        return {'proposal_sha256': fingerprint,
                'status': 'recovery_required' if recovery else record['status'] if record else 'unknown',
                'backup': outcome_path(fingerprint) if record else None,
                'operation': record['operation'] if record else None,
                'project_id': record['details']['project']['id'] if record else None}


def completed_retry(root, expected, instruction, request):
    brain.identifier(expected)
    instruction = brain.clean_text(instruction, 'user instruction/reference', 500)
    record = retained_outcome(root, expected)
    if record:
        if (record['request_sha256'] != brain.digest(json.dumps(request, sort_keys=True))
                or record['user_instruction'] != instruction):
            raise WorkspaceError('Retained operation requires identical inputs and instruction')
        if record['status'] == 'completed':
            return {'operation': record['operation'], **record['details'],
                    'proposal_sha256': expected, 'replacements': record['after'],
                    'applied': True, 'backup': outcome_path(expected)}
    return None


def commit(root, changes, operation, apply, expected, instruction, details, request):
    for path in changes:
        stacks.safe_path(path)
    before = {path: text_file(root, path) for path in changes}
    fingerprint = brain.digest(json.dumps({'operation': operation, 'before': before,
                                           'after': changes}, sort_keys=True))
    result = {'operation': operation, **details, 'proposal_sha256': fingerprint,
              'replacements': changes, 'applied': False}
    if not apply:
        return result
    if expected != fingerprint:
        raise WorkspaceError('Project proposal changed; preview again before applying')
    instruction = brain.clean_text(instruction, 'user instruction/reference', 500)
    backup = outcome_path(fingerprint)
    record = retained_outcome(root, fingerprint) or {
        'created': brain.now(), 'operation': operation, 'user_instruction': instruction,
        'proposal_sha256': fingerprint, 'request_sha256': brain.digest(json.dumps(request, sort_keys=True)),
        'before': before, 'after': changes, 'status': 'prepared', 'details': details}
    completed = json.dumps({**record, 'status': 'completed'}, indent=2, ensure_ascii=False) + '\n'
    if len(completed.encode('utf-8')) > OUTCOME_LIMIT:
        raise WorkspaceError('Project operation backup exceeds 8 MiB; nothing applied')
    brain.save_json(root, backup, record)
    # Rollback restores prepared state along with the registry and note contents.
    stacks.transaction(root, {**changes, backup: completed})
    return {**result, 'applied': True, 'backup': backup}


def registration_note(root, entry):
    path = brain.find_note(root, 'projects', entry['id'])
    if not path:
        raise WorkspaceError('Project registration note missing; repair it before changing the project')
    return path


def moved_source(source, old, new):
    # Path boundaries matter: /app must not rewrite /application.
    if isinstance(source, str) and (source == old or source.startswith(old + '/')):
        return new + source[len(old):]
    return source


def relink(root, key, directory, *, apply=False, expected=None, instruction=None):
    with brain.locked(root, shared=not apply):
        stacks.available(root)
        request = {'operation': 'relink', 'key': key, 'directory': str(directory)}
        if apply:
            completed = completed_retry(root, expected, instruction, request)
            if completed:
                return completed
        entry = projects.resolve(root, key)  # Missing/archived projects can be relinked.
        path = projects.project_path(root, directory)
        new_id = brain.digest(str(path))
        records = projects.registry(root)
        if any(e['id'] == new_id and e['id'] != entry['id'] for e in records):
            raise WorkspaceError('Destination is already registered; projects cannot be merged by relinking')
        note = registration_note(root, entry)
        if new_id != entry['id'] and brain.find_note(root, 'projects', new_id):
            raise WorkspaceError('Destination has an existing project note; preserve and review the conflict')
        updated = {**entry, 'id': new_id, 'path': str(path)}
        changes = {}
        for relative in brain.note_files(root):
            meta, body = brain.read_note(root, relative)
            original = brain.note_text(meta, body)
            if relative == note:
                if new_id != entry['id']:
                    history = meta.setdefault('relocations', [])
                    if not isinstance(history, list):
                        raise WorkspaceError('Invalid project relocation history')
                    history.append({'id': entry['id'], 'path': entry['path'], 'title': meta['title']})
                meta['id'], meta['title'] = new_id, path.name
                meta['registration_path'] = str(path)
                for label in ('Registered internal directory: ', 'Registered external directory: '):
                    line = label + entry['path']
                    if body == line or body.startswith(line + '\n'):
                        prefix = 'Registered internal directory: ' if root in path.parents else 'Registered external directory: '
                        body = prefix + str(path) + body[len(line):]
                        break
            if meta.get('project') == entry['id']:
                meta['project'] = new_id
            sources = meta.get('sources')
            if isinstance(sources, list):
                meta['sources'] = [moved_source(s, entry['path'], str(path)) for s in sources]
            content = brain.note_text(meta, body)
            if content != original:
                changes[relative] = content
        changes[projects.REGISTRY] = stacks.encode([updated if e['id'] == entry['id'] else e for e in records])
        return commit(root, changes, 'relink', apply, expected, instruction,
                      {'previous': entry, 'project': updated, 'brain_link': brain.note_link(note),
                       'notice': 'Note filenames and historical provenance are preserved. Review prose and work references separately.'}, request)


def remove(root, key, *, permanent=False, restore=False, apply=False, expected=None, instruction=None):
    with brain.locked(root, shared=not apply):
        stacks.available(root)
        if permanent and restore:
            raise WorkspaceError('Restore and permanent removal are mutually exclusive')
        request = {'operation': 'restore' if restore else 'unregister' if permanent else 'archive', 'key': key}
        if apply:
            completed = completed_retry(root, expected, instruction, request)
            if completed:
                return completed
        entry = projects.resolve(root, key)
        records = projects.registry(root)
        state = 'active' if restore else 'removed' if permanent else 'archived'
        note = registration_note(root, entry)
        meta, body = brain.read_note(root, note)
        meta['project_state'] = state
        meta['registration_path'] = entry['path']
        if permanent:
            records = [e for e in records if e['id'] != entry['id']]
        else:
            records = [{**e, 'status': state} if e['id'] == entry['id'] else e for e in records]
        changes = {projects.REGISTRY: stacks.encode(records), note: brain.note_text(meta, body)}
        return commit(root, changes, 'restore' if restore else 'remove', apply, expected, instruction,
                      {'project': entry, 'state': state,
                       'notice': 'Project files and brain/work references retained. Cleanup requires a separate explicit request.'}, request)


def reference_entry(root, key):
    # Removed projects remain reviewable through their retained registration note.
    try:
        return projects.resolve(root, key)
    except WorkspaceError:
        if not brain.IDENTIFIER.fullmatch(key):
            raise
        note = brain.find_note(root, 'projects', key)
        if not note:
            raise
        meta, _ = brain.read_note(root, note)
        if meta.get('project_state') != 'removed' or not isinstance(meta.get('registration_path'), str):
            raise
        return {'id': key, 'path': meta['registration_path']}


def references_unlocked(root, key):
    entry = reference_entry(root, key)
    note = registration_note(root, entry)
    meta, _ = brain.read_note(root, note)
    terms = {entry['id'], entry['path'], Path(entry['path']).name, meta['title'], brain.note_link(note)}
    history = meta.get('relocations', [])
    if not isinstance(history, list):
        raise WorkspaceError('Invalid project relocation history')
    for prior in history:
        if isinstance(prior, dict):
            terms.update(v for k, v in prior.items() if k in ('id', 'path', 'title') and isinstance(v, str))
    terms.discard('')
    matches, skipped = [], []
    count, truncated = 0, False
    for base in ('brain', 'work'):
        folder = managed_path(root, base)
        if not folder.exists():
            continue
        def failed(error):
            skipped.append({'path': str(error.filename), 'reason': 'unreadable directory'})
        for current, directories, filenames in os.walk(folder, followlinks=False, onerror=failed):
            count += len(directories) + len(filenames)
            if count > 5000:
                truncated = True
                break
            for name in list(directories):
                child = Path(current) / name
                if name.startswith('.') or child.is_symlink():
                    skipped.append({'path': str(child.relative_to(root)), 'reason': 'hidden directory or symlink'})
                    directories.remove(name)
            directories.sort()
            for name in sorted(filenames):
                relative = str((Path(current) / name).relative_to(root))
                if name.startswith('.') or Path(relative).suffix.lower() not in ('.md', '.txt', '.json', '.csv', '.yaml', '.yml', '.toml', '.rst'):
                    skipped.append({'path': relative, 'reason': 'hidden or unsupported file'})
                    continue
                try:
                    text = text_file(root, relative)
                    if brain.SECRET.search(text):
                        skipped.append({'path': relative, 'reason': 'possible secret'})
                        continue
                except (WorkspaceError, OSError, UnicodeError) as exc:
                    skipped.append({'path': relative, 'reason': str(exc)})
                    continue
                hits = sorted(t for t in terms if t in text or t in relative)
                if hits:
                    matches.append({'path': relative, 'sha256': brain.digest(text), 'matched': hits})
            if truncated:
                break
        if truncated:
            break
    return {'project': entry, 'references': matches, 'skipped': skipped, 'truncated': truncated,
            'limitations': ['Literal matches are review hints, not proof of ownership or a complete semantic review.',
                           'At most 5000 entries, supported text up to 256 KiB; no hidden paths, symlinks or external source scan.',
                           'Retained operation backups and provenance may contain historical references.']}


def references(root, key):
    with brain.locked(root, shared=True):
        stacks.available(root)
        return references_unlocked(root, key)


def cleanup(root, key, proposal, *, apply=False, expected=None, instruction=None):
    if not isinstance(proposal, dict) or set(proposal) != {'changes'}:
        raise WorkspaceError('Expected changes array')
    items = proposal['changes']
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise WorkspaceError('Provide 1–20 reference edits per batch')
    with brain.locked(root, shared=not apply):
        stacks.available(root)
        request = {'operation': 'cleanup', 'key': key, 'proposal': proposal}
        if apply:
            completed = completed_retry(root, expected, instruction, request)
            if completed:
                return completed
        entry = reference_entry(root, key)
        registered_ids = {e['id'] for e in projects.registry(root)}
        registered = entry['id'] in registered_ids
        note = registration_note(root, entry)
        report = references_unlocked(root, key)
        allowed = {item['path'] for item in report['references']}
        changes = {}
        for item in items:
            if not isinstance(item, dict) or set(item) != {'path', 'expected_sha256', 'content'}:
                raise WorkspaceError('Each edit needs path, expected_sha256 and content (text or null for deletion)')
            relative, content = item['path'], item['content']
            if not isinstance(relative, str) or relative not in allowed or relative in changes:
                raise WorkspaceError('Choose unique paths from the reference scan')
            stacks.safe_path(relative)  # Shared recovery must be able to restore every edited path.
            if relative == note and (registered or content is not None):
                raise WorkspaceError('Registration notes use lifecycle commands; only removed registrations may be deleted')
            if content is None and relative == 'brain/index.md':
                raise WorkspaceError('Preserve brain/index.md; edit its references instead')
            if relative.startswith('brain/projects/') and relative.endswith('.md'):
                project_meta, _ = brain.read_note(root, relative)
                if project_meta['id'] in registered_ids:
                    raise WorkspaceError('Registered project notes use lifecycle commands')
            original = text_file(root, relative)
            if brain.digest(original) != item['expected_sha256']:
                raise WorkspaceError(f'Reference changed; review again: {relative}')
            if content is not None:
                if relative.startswith('work/reminders/'):
                    raise WorkspaceError('Edit retained reminders through reminder commands to preserve delivery state')
                if not isinstance(content, str) or len(content.encode('utf-8')) > LIMIT or '\0' in content:
                    raise WorkspaceError('Replacement must be bounded text or null')
                if brain.SECRET.search(content):
                    raise WorkspaceError('Possible secret in replacement')
            if content is not None and relative != 'brain/index.md' and relative.startswith(
                    ('brain/knowledge/', 'brain/projects/', 'brain/sessions/', 'brain/candidates/', 'work/notes/')) and relative.endswith('.md'):
                # Retained notes keep their identity and historical evidence. Whole-file
                # deletion is separately visible in the reviewed proposal.
                try:
                    old_head = original.split('\n---\n', 1)[0][4:]
                    new_head, new_body = content[4:].split('\n---\n', 1)
                    old_meta, new_meta = frontmatter.loads(old_head), frontmatter.loads(new_head)
                    if not content.startswith('---\n') or not isinstance(new_meta, dict):
                        raise ValueError('expected note metadata')
                    editable = {'project', 'sources', 'links'}
                    if ({k: v for k, v in old_meta.items() if k not in editable}
                            != {k: v for k, v in new_meta.items() if k not in editable}):
                        raise ValueError('preserve identity, status, provenance and review history')
                    for field in ('sources', 'links'):
                        if not isinstance(new_meta.get(field), list) or any(not isinstance(v, str) for v in new_meta[field]):
                            raise ValueError('sources and links must remain lists of strings')
                    if new_meta.get('project') is not None and not isinstance(new_meta['project'], str):
                        raise ValueError('invalid project reference')
                    brain.note_text(new_meta, new_body)
                except (ValueError, TypeError, AttributeError, RecursionError) as exc:
                    raise WorkspaceError(f'Invalid retained note: {relative}: {exc}') from exc
            changes[relative] = content
        return commit(root, changes, 'cleanup', apply, expected, instruction,
                      {'project': entry, 'coverage': {'truncated': report['truncated'], 'skipped': report['skipped']}}, request)
