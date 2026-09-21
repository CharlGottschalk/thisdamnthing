"""Strict local stack bundles, owned projections and recoverable text transactions."""
import base64
import hashlib
import os
import tempfile
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import unicodedata

from .workspace import WorkspaceError, managed_path, read_json
from .bootstrap import existing_text, parse_settings, encode, SKILLS, LEGACY_SKILLS
from .brain import atomic, locked, now, note_text, clean_text

REGISTRY = '.tdt/state/stacks.json'
JOURNAL = '.tdt/state/stack-transaction.json'
ID = re.compile(r'(?=.{1,80}\Z)[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')
LEGACY_ID = re.compile(r'[a-z][a-z0-9-]{0,39}\.[a-z][a-z0-9-]{0,39}\Z')
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z')
EVENTS = ('session_start', 'turn_complete')


def sha(text):
    return hashlib.sha256(content_bytes(text)).hexdigest()


def file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def content_bytes(value):
    if isinstance(value, str):
        return value.encode('utf-8')
    if isinstance(value, dict) and set(value) == {'base64'} and isinstance(value['base64'], str):
        return base64.b64decode(value['base64'], validate=True)
    raise WorkspaceError('Invalid stack file content')


def content_value(raw):
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return {'base64': base64.b64encode(raw).decode('ascii')}


def existing_content(root, relative):
    path = managed_path(root, relative)
    return content_value(path.read_bytes()) if path.exists() else None


def write_content(root, relative, value):
    if isinstance(value, str):
        return atomic(root, relative, value)
    path = managed_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.tdt-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def safe_path(value):
    if (not isinstance(value, str) or not value or len(value) > 240
            or any(not p or p in ('.', '..')
                   or any(not (c.isalnum() or unicodedata.category(c).startswith('M') or c in ' _.-') for c in p)
                   for p in value.split('/'))):
        raise WorkspaceError(f'Invalid relative file path: {value!r}')
    return value


def validate(directory, *, legacy_skills=False, legacy_id=False, metadata_only=False):
    source = Path(directory).expanduser().absolute()
    for parent in (source, *source.parents):
        if parent.is_symlink():
            raise WorkspaceError(f'Stack source symlink: {parent}')
    if not source.is_dir():
        raise WorkspaceError('Stack source must be a local directory')
    def read(relative, maximum=262144):
        path = managed_path(source, safe_path(relative))
        if not path.is_file() or path.stat().st_size > maximum:
            raise WorkspaceError(f'Expected regular UTF-8 file <=256 KiB: {relative}')
        return path.read_bytes().decode('utf-8')
    manifest_text = read('stack.json', 2 * 1024 * 1024)
    data = parse_settings(manifest_text)
    required = {'contract_version', 'id', 'version', 'description', 'author', 'license', 'skills', 'hooks', 'knowledge'}
    if not isinstance(data, dict) or not required <= set(data) or set(data) - required - ({'templates', 'docs', 'capabilities', 'assets', 'compatibility'} if data.get('contract_version') == 2 else {'templates', 'docs'}):
        raise WorkspaceError('Invalid stack fields; see .tdt/contracts/stack.md')
    if type(data['contract_version']) is not int or data['contract_version'] not in (1, 2):
        raise WorkspaceError('Expected contract_version integer 1 or 2')
    if data['contract_version'] == 1 and len(manifest_text.encode()) > 262144:
        raise WorkspaceError('v1 manifest exceeds 256 KiB')
    if not isinstance(data['id'], str) or not (ID.fullmatch(data['id']) or legacy_id and LEGACY_ID.fullmatch(data['id'])):
        raise WorkspaceError('Stack id must be 1-80 lowercase letters, digits and single separating hyphens, starting with a letter')
    if not isinstance(data['version'], str) or not VERSION.fullmatch(data['version']):
        raise WorkspaceError('Version must be numeric MAJOR.MINOR.PATCH without leading zeroes')
    for field in ('description', 'author', 'license'):
        clean_text(data[field], field, 500)
        if '\n' in data[field]:
            raise WorkspaceError(f'{field} must be one line')
    files = {'stack.json': manifest_text}
    names = set()
    for category in ('skills', 'hooks', 'knowledge', 'templates', 'docs'):
        entries = data.get(category, [])
        if not isinstance(entries, list) or len(entries) > 50:
            raise WorkspaceError(f'{category} must be a list of at most 50 entries')
        for entry in entries:
            if category == 'hooks':
                if (not isinstance(entry, dict) or set(entry) != {'event', 'path'}
                        or entry['event'] not in EVENTS):
                    raise WorkspaceError('Hook requires event (session_start or turn_complete) and path')
                relative = safe_path(entry['path'])
                if not relative.startswith('hooks/') or not relative.endswith('.py'):
                    raise WorkspaceError('Hooks must be explicitly listed hooks/*.py Python files')
            else:
                relative = safe_path(entry)
                if not relative.startswith(category + '/'):
                    raise WorkspaceError(f'{category} files must be under {category}/')
            if relative in files:
                raise WorkspaceError(f'Duplicate listed path: {relative}')
            files[relative] = read(relative)
            if category == 'skills':
                parts = relative.split('/')
                name = parts[1]
                if (len(parts) != 3 or parts[2] != 'SKILL.md'
                        or not ((len(name) <= 64 and re.fullmatch(r'tdt-[a-z0-9]+(?:-[a-z0-9]+)*', name))
                                or (legacy_skills and re.fullmatch(r'tdt\.[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)*', name)))
                        or name in (*SKILLS, *LEGACY_SKILLS) or name in names):
                    raise WorkspaceError(f'Invalid or reserved skill: {relative}')
                if not files[relative].startswith(f'---\nname: {name}\n'):
                    raise WorkspaceError(f'Skill must start with front matter name: {name}')
                text = files[relative]
                if '\n---\n' not in text[4:]:
                    raise WorkspaceError(f'Missing skill front matter delimiter: {relative}')
                head = text[4:].split('\n---\n', 1)[0]
                description = re.search(r'^description: ([^\n]+)$', head, re.M)
                if not description or (not legacy_skills and not 1 <= len(description[1].strip()) <= 1024):
                    raise WorkspaceError(f'Skill requires a one-line description: {relative}')
                names.add(name)
            if category == 'knowledge':
                if not relative.endswith('.md'):
                    raise WorkspaceError('Knowledge files must be Markdown')
                clean_text(files[relative], 'knowledge', 3000)
    if sum(len(t.encode()) for t in files.values()) > 2 * 1024 * 1024:
        raise WorkspaceError('Stack exceeds 2 MiB')
    asset_hashes = {}
    if data['contract_version'] == 2:
        from .capabilities import validate_manifest
        asset_hashes = validate_manifest(data, source, files, metadata_only)
    digest = sha(json.dumps(files if data['contract_version'] == 1 else {**{p: sha(v) for p, v in files.items()}, **asset_hashes}, sort_keys=True, ensure_ascii=False))
    return data, files, {'kind': 'local', 'path': str(source.resolve()), 'sha256': digest}


def registry(root):
    entries = read_json(root, REGISTRY)
    if not isinstance(entries, list):
        raise WorkspaceError('Invalid stack registry')
    seen = set()
    for entry in entries:
        if (not isinstance(entry, dict) or not isinstance(entry.get('id'), str)
                or not (ID.fullmatch(entry['id']) or LEGACY_ID.fullmatch(entry['id'])) or entry['id'] in seen
                or not isinstance(entry.get('files'), dict)
                or not isinstance(entry.get('manifest'), dict)
                or not isinstance(entry.get('origin'), dict)):
            raise WorkspaceError('Invalid stack ownership record')
        seen.add(entry['id'])
        for relative, digest in entry['files'].items():
            safe_path(relative)
            prefix = f".tdt/stacks/{entry['id']}/"
            if not (relative.startswith(prefix) or re.fullmatch(r'(?:\.tdt|\.agents|\.claude)/skills/tdt[.-][a-z0-9.-]+/SKILL.md', relative)):
                raise WorkspaceError('Unexpected stack ownership path')
            if relative.split('/')[-2] in (*SKILLS, *LEGACY_SKILLS) or not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
                raise WorkspaceError('Invalid stack ownership digest or reserved skill')
    return entries


def available(root):
    from .skills import JOURNAL as SKILL_JOURNAL
    if managed_path(root, SKILL_JOURNAL).exists():
        raise WorkspaceError('Interrupted skill save; run tdt skill recover')
    if managed_path(root, JOURNAL).exists():
        raise WorkspaceError('Interrupted stack operation; run tdt stack recover')
    return registry(root)


def transaction(root, changes):
    # All registry mutations (including future updates) refresh the same view.
    from . import stack_docs
    if REGISTRY in changes:
        changes = {**changes, **stack_docs.plan(root, json.loads(changes[REGISTRY]), changes)}
    before = {p: existing_content(root, p) for p in changes}
    directories = set()
    for p in changes:
        parent = managed_path(root, p).parent
        while parent != root and not parent.exists():
            directories.add(str(parent.relative_to(root)))
            parent = parent.parent
    record = {'before': before, 'after': changes, 'directories': sorted(directories)}
    atomic(root, JOURNAL, encode(record))
    try:
        for relative, text in changes.items():
            if text is None:
                managed_path(root, relative).unlink()
            else:
                write_content(root, relative, text)
        managed_path(root, JOURNAL).unlink()
    except (OSError, ValueError):
        recover(root)
        raise


def recover(root):
    path = managed_path(root, JOURNAL)
    if not path.exists():
        return 'No stack transaction to recover.'
    record = read_json(root, JOURNAL)
    if (not isinstance(record, dict) or set(record) != {'before', 'after', 'directories'}
            or not isinstance(record['before'], dict) or not isinstance(record['after'], dict)
            or record['before'].keys() != record['after'].keys()
            or not isinstance(record['directories'], list)):
        raise WorkspaceError('Invalid stack recovery journal')
    from .bootstrap import RESOURCES, MANIFEST, PROVIDERS
    from .ui_resources import RESOURCES as UI_RESOURCES, MANIFEST as UI_MANIFEST
    bootstrap_paths = {*RESOURCES, *UI_RESOURCES, MANIFEST, UI_MANIFEST,
                       '.tdt/config.json', '.tdt/state/owned-files.json',
                       '.tdt/state/user-skills.json', '.tdt/state/capability-state.json', 'README.md',
                       *(p for provider in PROVIDERS.values() for p in (provider[0], provider[2]))}
    for relative, before in record['before'].items():
        safe_path(relative)
        if not (relative in bootstrap_paths or relative in (REGISTRY, '.tdt/stack-docs.md', '.tdt/state/stack-docs.json') or relative.startswith(('.tdt/stacks/', '.tdt/skills/', '.agents/skills/', '.claude/skills/', 'brain/candidates/', '.tdt/state/capabilities/'))):
            raise WorkspaceError('Unexpected recovery path')
        after = record['after'][relative]
        for value in (before, after):
            if value is not None:
                content_bytes(value)
        if existing_content(root, relative) not in (before, after):
            raise WorkspaceError(f'Recovery conflict; preserve and inspect {relative}')
    for relative in record['directories']:
        safe_path(relative)
        if not any(p.startswith(relative + '/') for p in record['before']):
            raise WorkspaceError('Invalid recovery directory')
        managed_path(root, relative)
    for relative, before in record['before'].items():
        if before is None:
            managed_path(root, relative).unlink(missing_ok=True)
        else:
            write_content(root, relative, before)
    for relative in sorted(record['directories'], key=len, reverse=True):
        try:
            managed_path(root, relative).rmdir()
        except OSError:
            pass  # Preserve directories that acquired unrelated user files.
    path.unlink()
    return 'Rolled back interrupted stack operation.'


def bridge(name):
    return (f'---\nname: {name}\ndescription: Use the installed {name} stack workflow.\n---\n\n'
            f'Read and follow .tdt/skills/{name}/SKILL.md from the workspace root.\n')


def install(root, directory, trust=None, *, provenance=None, replacing=None,
            prerequisite_release=None, confirmed=()):
    data, files, origin = validate(directory)
    if provenance is not None:
        if provenance.get('sha256') != origin['sha256']:
            raise WorkspaceError('Installation provenance content mismatch')
        origin = dict(provenance)
    if (data['hooks'] or data.get('capabilities')) and trust != origin['sha256']:
        raise WorkspaceError('Executable stack content requires --trust-executable (alias --trust-hooks) ' + origin['sha256'] + ' after reviewing stack validate output and source')
    with locked(root):
        entries = available(root)
        if prerequisite_release is not None:
            from .marketplace import prerequisites
            prerequisites(entries, prerequisite_release, confirmed)
        current = next((e for e in entries if e['id'] == data['id']), None)
        if replacing is not None:
            if current != replacing:
                raise WorkspaceError('Installed state changed; inspect and approve again')
            check_owned(root, current)
            if tuple(map(int, data['version'].split('.'))) <= tuple(map(int, current['version'].split('.'))):
                raise WorkspaceError('Update requires a strictly newer version')
        elif current is not None:
            raise WorkspaceError('Stack already installed; use stack update')
        base = f".tdt/stacks/{data['id']}"
        if replacing is None and managed_path(root, base).exists():
            raise WorkspaceError(f'Stack directory conflict: {base}')
        changes = {f'{base}/{p}': t for p, t in files.items()}
        from .agents import folders
        skill_folders = folders(root)
        for relative in data['skills']:
            name = relative.split('/')[1]
            for folder in skill_folders:
                if (managed_path(root, f'{folder}/{name}').exists()
                        and (replacing is None or f'{folder}/{name}/SKILL.md' not in replacing['files'])):
                    raise WorkspaceError(f'Skill directory conflict: {folder}/{name}')
                changes[f'{folder}/{name}/SKILL.md'] = files[relative] if folder == '.tdt/skills' else bridge(name)
            if '.claude/skills' in skill_folders and managed_path(root, f'.claude/commands/{name}.md').exists():
                raise WorkspaceError(f'Claude command conflict: {name}')
        owned = {p: sha(t) for p, t in changes.items()}
        candidates = list(replacing.get('candidates', [])) if replacing else []
        for relative in data['knowledge']:
            if replacing and existing_content(root, f'{base}/{relative}') == files[relative]:
                continue
            key = sha(data['id'] + ':' + origin['sha256'] + ':' + relative)
            target = f'brain/candidates/{key}.md'
            candidates.append(target)
            # Prior candidates/approved notes survive removal and reinstall.
            if managed_path(root, target).exists():
                from .brain import read_note
                meta, body = read_note(root, target)
                if meta.get('provenance') != {'stack': data['id'], **origin, 'file': relative}:
                    raise WorkspaceError(f'Stack candidate conflict: {target}')
                continue
            meta = {'format_version': 1, 'id': key, 'status': 'pending', 'title': Path(relative).stem,
                    'kind': 'fact', 'created': now(), 'updated': now(), 'review': [],
                    'provenance': {'stack': data['id'], **origin, 'file': relative},
                    'sources': [f"stack:{data['id']}@{data['version']}/{relative} sha256:{origin['sha256']}"],
                    'links': ['index']}
            changes[target] = note_text(meta, files[relative])
        for relative in changes:
            if existing_content(root, relative) is not None and (replacing is None or relative not in replacing['files']):
                raise WorkspaceError(f'Install file conflict: {relative}')
        if replacing:
            changes.update({p: None for p in replacing['files'] if p not in owned})
            entries = [e for e in entries if e['id'] != data['id']]
        entries.append({'id': data['id'], 'version': data['version'], 'manifest': data,
                        'origin': origin, 'files': owned, 'candidates': candidates,
                        'trusted_hooks': origin['sha256'] if data['hooks'] else None,
                        'trusted_capabilities': origin['sha256'] if data.get('capabilities') else None})
        if replacing:
            from .capabilities import cache_changes
            changes.update(cache_changes(root, data['id']))
        changes[REGISTRY] = encode(entries)
        transaction(root, changes)
        if replacing:
            prune(root, replacing['files'])
    return data['id']


def check_owned(root, entry):
    """Refuse edits, missing assets and additions before any lifecycle mutation."""
    for relative, digest in entry['files'].items():
        path = managed_path(root, relative)
        if not path.is_file() or file_sha(path) != digest:
            raise WorkspaceError(f'Owned stack file changed or missing; preserve edits elsewhere and restore the original: {relative}')
    directories = {f".tdt/stacks/{entry['id']}"}
    directories.update(str(Path(p).parent) for p in entry['files']
                       if not p.startswith('.tdt/stacks/'))
    allowed_dirs = {str(parent) for p in entry['files'] for parent in Path(p).parents}
    def inspect(directory):
        for path in managed_path(root, directory).iterdir():
            relative = str(path.relative_to(root))
            if path.is_symlink():
                raise WorkspaceError(f'Untracked stack symlink; preserve/move before retry: {relative}')
            if path.is_dir() and relative in allowed_dirs:
                inspect(relative)
            elif relative not in entry['files']:
                raise WorkspaceError(f'Untracked stack addition; preserve/move before retry: {relative}')
    for directory in directories:
        inspect(directory)


def prune(root, files):
    boundaries = [root / p for p in ('.tdt/stacks', '.tdt/skills', '.agents/skills', '.claude/skills')]
    for relative in sorted(files, key=len, reverse=True):
        parent = managed_path(root, relative).parent
        while parent != root and parent not in boundaries:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent


def remove(root, stack_id):
    with locked(root):
        entries = available(root)
        entry = next((e for e in entries if e['id'] == stack_id), None)
        if entry is None:
            raise WorkspaceError('Stack is not installed; nothing removed')
        check_owned(root, entry)
        changes = {p: None for p in entry['files']}
        from .capabilities import cache_changes
        changes.update(cache_changes(root, stack_id))
        changes[REGISTRY] = encode([e for e in entries if e['id'] != stack_id])
        transaction(root, changes)
        prune(root, entry['files'])
    return stack_id


def dispatch(root, event):
    """Notification-only hooks: no provider output, permission changes or Stop blocks."""
    if event['event'] not in EVENTS or event.get('stop_hook_active'):
        return
    if not Path(event['cwd']).resolve().is_relative_to(root.resolve()):
        raise WorkspaceError('Stack hook cwd is outside workspace')
    deadline = time.monotonic() + 4
    for entry in available(root):
        hooks = entry['manifest'].get('hooks', [])
        if not hooks:
            continue
        if entry.get('trusted_hooks') != entry['origin'].get('sha256'):
            raise WorkspaceError('Stack hooks lack recorded trust')
        base = f".tdt/stacks/{entry['id']}"
        # Validate installed bytes against the trust digest, including unexecuted files.
        # Previously trusted bundles retain their exact bytes until the user
        # removes/reinstalls them; new installations require compliant names.
        manifest, _, origin = validate(managed_path(root, base), legacy_skills=True, legacy_id=True)
        if origin['sha256'] != entry['trusted_hooks']:
            raise WorkspaceError(f"Trusted stack changed: {entry['id']}")
        for hook in manifest['hooks']:
            if hook['event'] != event['event']:
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                print('tdt stack hook budget exhausted; remaining notifications skipped', file=sys.stderr)
                return
            payload = {**event, 'workspace': str(root), 'stack_id': entry['id']}
            try:
                subprocess.run([sys.executable, str(managed_path(root, base + '/' + hook['path']))],
                               input=encode(payload), text=True, cwd=root, timeout=min(2, remaining),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (OSError, subprocess.SubprocessError) as exc:
                print(f"tdt stack hook failed: {entry['id']} {hook['path']}: {exc}", file=sys.stderr)


def notify_hooks(root, event):
    try:
        dispatch(root, event)
    except (WorkspaceError, OSError, ValueError) as exc:
        print(f"tdt stack hooks unavailable: {exc}", file=sys.stderr)
