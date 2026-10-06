"""Bounded brain audit and reviewed, recoverable edits to existing notes."""
from collections import defaultdict
import json
import re
import stat

from . import brain, constitution, stacks
from .workspace import WorkspaceError, managed_path

CATEGORIES = ('knowledge', 'projects', 'sessions')
WIKI = re.compile(r'\[\[([^\]]+)\]\]')


def body_links(body):
    # Examples in fenced blocks and inline code are not navigable relations.
    prose = []
    fence = None
    for line in body.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
        elif match:
            fence = match[1]
        else:
            prose.append(line)
    text = re.sub(r"(`+).*?\1", "", "\n".join(prose), flags=re.S)
    return WIKI.findall(text)


def target(value):
    return value.split('|', 1)[0].split('#', 1)[0]


def inventory(root):
    files = brain.note_files(root, CATEGORIES)
    return ['brain/index.md', *files]


def read_text(root, path):
    file = managed_path(root, path)
    if not stat.S_ISREG(file.lstat().st_mode):
        raise WorkspaceError(f'Expected a regular note file: {path}')
    if file.stat().st_size > 32768:
        raise WorkspaceError(f'File exceeds 32 KiB: {path}')
    with file.open('rb') as stream:
        raw = stream.read(32769)
    if len(raw) > 32768:
        raise WorkspaceError(f'File exceeds 32 KiB: {path}')
    return raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')


def scan(root):
    with brain.locked(root, shared=True):
        files = inventory(root)
        findings, notes = [], []
        bodies, metadata = {}, {}
        identities, titles = defaultdict(list), defaultdict(list)
        for path in files:
            try:
                text = read_text(root, path)
                if path == 'brain/index.md':
                    meta, body = {}, text
                else:
                    meta, body = brain.read_note(root, path)
                    if meta['status'] != 'approved':
                        findings.append({'kind': 'unapproved_canonical_note', 'path': path})
                    identities[meta['id']].append(path)
                    titles[meta['title'].strip().casefold()].append(path)
                    if (not isinstance(meta.get('sources'), list) or not meta['sources']
                            or any(not isinstance(x, str) or not x.strip() for x in meta['sources'])):
                        findings.append({'kind': 'missing_sources', 'path': path})
                bodies[path], metadata[path] = body, meta
                notes.append({'path': path, 'title': meta.get('title', 'Brain index'),
                              'status': meta.get('status'), 'sha256': brain.digest(text)})
            except (WorkspaceError, UnicodeError) as exc:
                findings.append({'kind': 'unreadable_note', 'path': path, 'detail': str(exc)})
        paths = {brain.note_link(p): p for p in files}
        # Scratchpad links are valid targets but do not connect approved brain notes.
        scratch = {brain.note_link(p) for p in brain.note_files(root, ('notes',))}
        incoming, outgoing = defaultdict(set), defaultdict(set)
        for path, body in bodies.items():
            links = metadata[path].get('links', [])
            if not isinstance(links, list) or any(not isinstance(x, str) for x in links):
                findings.append({'kind': 'invalid_links_metadata', 'path': path})
                links = []
            if path != 'brain/index.md' and set(links) - set(body_links(body)):
                findings.append({'kind': 'metadata_links_missing_from_body', 'path': path})
            for raw in sorted(set(links + body_links(body))):
                link = target(raw)
                if not brain.LINK.fullmatch(link) or '..' in link or '//' in link:
                    kind = 'invalid_link'
                elif link not in paths and link not in scratch:
                    kind = 'broken_link'
                elif link in paths and paths[link] not in bodies:
                    kind = 'unreadable_target'
                else:
                    if link in paths and paths[link] != path:
                        outgoing[path].add(paths[link])
                        incoming[paths[link]].add(path)
                    continue
                findings.append({'kind': kind, 'path': path, 'link': raw})
        for path in bodies:
            if path != 'brain/index.md' and not incoming[path]:
                findings.append({'kind': 'no_incoming_links', 'path': path})
        reached, queue = set(), ['brain/index.md']
        while queue:
            path = queue.pop()
            if path not in reached:
                reached.add(path)
                queue.extend(outgoing[path] - reached)
        for path in sorted(bodies.keys() - reached):
            findings.append({'kind': 'unreachable_from_index', 'path': path})
        for kind, groups in (('duplicate_id', identities), ('same_title_review', titles)):
            for paths_group in groups.values():
                if len(paths_group) > 1:
                    findings.append({'kind': kind, 'paths': paths_group})
        return {'notes': notes, 'findings': findings,
                'limitations': ['Canonical brain folders and index only; candidates are reviewed separately.',
                                'Link targets checked, not headings, external URLs or source availability.',
                                'Same titles and disconnected notes are review hints, not deletion instructions.',
                                'An agent must inspect note contents for duplicates, conflicts and stale relationships.']}


def outcome_path(fingerprint):
    return '.tdt/state/brain-maintenance/' + brain.identifier(fingerprint) + '.json'


def retained_outcome(root, fingerprint):
    path = managed_path(root, outcome_path(fingerprint))
    if not path.exists():
        return None
    record = json.loads(constitution.bounded(path, 8 * 1024 * 1024))
    if (not isinstance(record, dict)
            or set(record) != {'created', 'user_instruction', 'proposal_sha256',
                               'request_sha256', 'before', 'after', 'status'}
            or record['proposal_sha256'] != fingerprint
            or record['status'] not in ('prepared', 'completed')
            or not isinstance(record['before'], dict) or not isinstance(record['after'], dict)
            or record['before'].keys() != record['after'].keys()
            or not 1 <= len(record['before']) <= 20
            or any(not isinstance(v, str) for v in (*record['before'].values(), *record['after'].values()))
            or brain.digest(json.dumps({'before': record['before'], 'after': record['after']},
                                       sort_keys=True)) != fingerprint):
        raise WorkspaceError('Invalid retained repair outcome')
    brain.identifier(record['request_sha256'])
    brain.clean_text(record['user_instruction'], 'retained instruction', 500)
    if not isinstance(record['created'], str):
        raise WorkspaceError('Invalid retained repair timestamp')
    return record


def repair_status(root, fingerprint):
    """Read historical outcome; an outstanding journal prevents a final verdict."""
    with brain.locked(root, shared=True):
        record = retained_outcome(root, fingerprint)
        from .skills import JOURNAL as SKILL_JOURNAL
        recovery = any(managed_path(root, p).exists() for p in (stacks.JOURNAL, SKILL_JOURNAL))
        return {'proposal_sha256': fingerprint,
                'status': 'recovery_required' if recovery else record['status'] if record else 'unknown',
                'backup': outcome_path(fingerprint) if record else None}


def repair(root, proposal, apply=False, expected=None, instruction=None):
    """Preview exact replacements; apply only a hash-bound batch with a backup."""
    if not isinstance(proposal, dict) or set(proposal) != {'changes'}:
        raise WorkspaceError('Expected changes array')
    items = proposal['changes']
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise WorkspaceError('Provide 1–20 note changes per batch')
    with brain.locked(root, shared=not apply):
        stacks.available(root)  # Refuse to overwrite an interrupted transaction.
        retained = None
        if apply:
            brain.identifier(expected)
            instruction = brain.clean_text(instruction, 'user instruction/reference', 500)
            request_hash = brain.digest(json.dumps(proposal, sort_keys=True))
            retained = retained_outcome(root, expected)
            if retained:
                if (retained['request_sha256'] != request_hash
                        or retained['user_instruction'] != instruction):
                    raise WorkspaceError('Retained repair requires the identical proposal and instruction')
                if retained['status'] == 'completed':
                    return {'proposal_sha256': expected, 'replacements': retained['after'],
                            'applied': True, 'backup': outcome_path(expected)}
        allowed = set(inventory(root))
        changes, before = {}, {}
        for item in items:
            if not isinstance(item, dict) or set(item) != {'path', 'expected_sha256', 'body', 'links'}:
                raise WorkspaceError('Each change needs path, expected_sha256, body and links')
            path = item['path']
            if not isinstance(path, str) or path not in allowed or path in changes:
                raise WorkspaceError('Repair requires unique existing canonical note paths or brain/index.md')
            original = read_text(root, path)
            if brain.digest(original) != item['expected_sha256']:
                raise WorkspaceError(f'Note changed; rescan and review again: {path}')
            body = brain.clean_text(item['body'], 'replacement body', 16000)
            links = item['links']
            if not isinstance(links, list) or len(links) > 100 or any(not isinstance(x, str) for x in links):
                raise WorkspaceError('Expected at most 100 link strings')
            if path != 'brain/index.md' and set(links) - set(body_links(body)):
                raise WorkspaceError('Include metadata links in the body so search can follow them')
            for raw in links + body_links(body):
                link = target(raw)
                if not brain.LINK.fullmatch(link) or '..' in link or '//' in link:
                    raise WorkspaceError(f'Invalid replacement link: {raw}')
                relative = link + '.md' if link.startswith('work/') else 'brain/' + link + '.md'
                if not managed_path(root, relative).is_file():
                    raise WorkspaceError(f'Replacement link target missing: {raw}')
            if path == 'brain/index.md':
                if links:
                    raise WorkspaceError('Index links belong in body; supply links: []')
                content = body + '\n'
            else:
                meta, _ = brain.read_note(root, path)
                if meta['status'] != 'approved':
                    raise WorkspaceError('Only approved notes can be repaired')
                # Identity, sources, provenance and approval history cannot be replaced.
                meta['links'] = links
                content = brain.note_text(meta, body)
            if len(content.encode('utf-8')) > 32768:
                raise WorkspaceError('Replacement exceeds 32 KiB')
            before[path], changes[path] = original, content
        fingerprint = brain.digest(json.dumps({'before': before, 'after': changes}, sort_keys=True))
        result = {'proposal_sha256': fingerprint, 'replacements': changes, 'applied': False}
        if not apply:
            return result
        if expected != fingerprint:
            raise WorkspaceError('Proposal changed; preview and approve the exact replacements again')
        backup = outcome_path(fingerprint)
        record = retained or {'created': brain.now(), 'user_instruction': instruction,
                              'proposal_sha256': fingerprint, 'request_sha256': request_hash,
                              'before': before, 'after': changes, 'status': 'prepared'}
        if not retained:
            brain.save_json(root, backup, record)
        # Completion and note writes share one journal. Rollback restores prepared;
        # a crash with a journal cannot be mistaken for a completed operation.
        stacks.transaction(root, {**changes, backup: json.dumps(
            {**record, 'status': 'completed'}, indent=2, ensure_ascii=False) + '\n'})
        result.update(applied=True, backup=backup)
        return result
