"""Bounded brain audit and reviewed, recoverable edits to existing notes."""
from collections import defaultdict
import json
import re
import uuid

from . import brain, stacks
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
    if file.stat().st_size > 32768:
        raise WorkspaceError(f'File exceeds 32 KiB: {path}')
    return file.read_text(encoding='utf-8')


def scan(root):
    with brain.locked(root):
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


def repair(root, proposal, apply=False, expected=None, instruction=None):
    """Preview exact replacements; apply only a hash-bound batch with a backup."""
    if not isinstance(proposal, dict) or set(proposal) != {'changes'}:
        raise WorkspaceError('Expected changes array')
    items = proposal['changes']
    if not isinstance(items, list) or not 1 <= len(items) <= 20:
        raise WorkspaceError('Provide 1–20 note changes per batch')
    with brain.locked(root):
        stacks.available(root)  # Refuse to overwrite an interrupted transaction.
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
        instruction = brain.clean_text(instruction, 'user instruction/reference', 500)
        backup = '.tdt/state/brain-maintenance/' + uuid.uuid4().hex + '.json'
        brain.save_json(root, backup, {'created': brain.now(), 'user_instruction': instruction,
                                     'proposal_sha256': fingerprint, 'before': before, 'after': changes})
        stacks.transaction(root, changes)
        result.update(applied=True, backup=backup)
        return result
