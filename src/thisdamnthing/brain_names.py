"""Explicit, recoverable migration of legacy hash filenames and current links."""
import json
from pathlib import Path
import re

from . import brain, stacks
from .workspace import WorkspaceError, managed_path


def migrate(root, apply=False):
    with brain.locked(root):
        entries = stacks.available(root)
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
        links = {old[6:-3]: new[6:-3] for old, new in renames.items()}

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
            header = json.dumps(updated, indent=2, ensure_ascii=False) if updated != meta else head
            content = '---\n' + header + '\n---\n' + wikilinks(body)
            if len(content.encode('utf-8')) > 32768:
                raise WorkspaceError(f'Migrated note exceeds 32 KiB: {path}')
            destination = renames.get(path, path)
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
        result = {'renames': renames, 'updated_files': [p for p in changes if p not in renames],
                  'applied': apply}
        if apply and changes:
            stacks.transaction(root, changes)
        return result
