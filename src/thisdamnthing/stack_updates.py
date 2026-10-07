"""Inspect a replacement in memory; approval never survives changed inputs."""
from contextlib import contextmanager
import json
import sys

from . import marketplace, stacks
from .bootstrap import existing_text
from .workspace import WorkspaceError, managed_path


@contextmanager
def replacement(entry, source=None, registry_url=None, *, bounded=False):
    origin = entry['origin']
    if origin.get('kind') == 'local':
        if registry_url:
            raise WorkspaceError('Local updates cannot switch to a registry')
        path = source or origin.get('path')
        if not path:
            raise WorkspaceError('Local source unavailable; select --source PATH')
        manifest, files, provenance = stacks.validate(path, bounded=bounded)
        yield path, manifest, files, provenance, None
    elif origin.get('kind') == 'marketplace':
        if source:
            raise WorkspaceError('Registry updates cannot switch to local sources')
        saved = origin.get('registry_url')
        if saved and registry_url and saved != registry_url:
            raise WorkspaceError('Registry endpoint change refused')
        endpoint = saved or registry_url
        if not endpoint:
            raise WorkspaceError('Legacy origin lacks the endpoint; supply the original --registry HTTPS_URL after verification')
        if marketplace.origin(endpoint) != origin.get('registry_origin'):
            raise WorkspaceError('Registry origin change refused')
        listing, release = marketplace.select(marketplace.load(endpoint), entry['id'])
        if listing['repository'] != origin.get('repository'):
            raise WorkspaceError('Repository change refused')
        if listing['status']['state'] != 'active' or release['status']['state'] != 'active':
            raise WorkspaceError('Deprecated release/listing is ineligible for update')
        with marketplace.prepared(listing, release, endpoint) as prepared:
            yield *prepared, {'listing': listing, 'release': release}
    else:
        raise WorkspaceError('Unknown installed source type; preserve and inspect the ownership record')


def update(root, sid, *, source=None, registry_url=None, check=False,
           approve=None, trust=None, confirmed=()):
    entry = next((e for e in stacks.available(root) if e['id'] == sid), None)
    if entry is None:
        raise WorkspaceError('Stack is not installed')
    if check and approve:
        raise WorkspaceError('--check cannot be combined with --approve')
    with replacement(entry, source, registry_url) as (directory, manifest, files, origin, metadata):
        if manifest['id'] != sid:
            raise WorkspaceError('Replacement stack ID mismatch')
        stacks.check_owned(root, entry)
        current, target = entry['version'], manifest['version']
        if marketplace.version_key(target) <= marketplace.version_key(current):
            if target == current and origin['sha256'] == entry['origin'].get('sha256'):
                print(json.dumps({'status': 'current', 'id': sid, 'version': current}))
                return 'No newer version'
            raise WorkspaceError('Downgrade or same-version replacement refused; installed content preserved')
        projection_conflicts(root, sid, entry, manifest, files)
        base = f'.tdt/stacks/{sid}/'
        old = {p[len(base):]: digest for p, digest in entry['files'].items() if p.startswith(base)}
        from . import stack_docs
        projected = {base + p: text for p, text in files.items()}
        updated = {**entry, 'manifest': manifest, 'version': target,
                   'files': {p: stacks.sha(text) for p, text in projected.items()}}
        stack_docs.plan(root, [updated if e['id'] == sid else e for e in stacks.available(root)], projected)
        plan = {'id': sid, 'current_version': current, 'target_version': target,
                'current_origin': entry['origin'], 'target_origin': origin,
                'added': sorted(set(files) - set(old)), 'removed': sorted(set(old) - set(files)),
                'changed': sorted(p for p in files if p in old and stacks.sha(files[p]) != old[p]),
                'manifest': manifest, 'registry_metadata': metadata,
                'hooks': {h['path']: files[h['path']] for h in manifest['hooks']},
                'release_notes': 'No inline release notes available; registry links are references only.'}
        token = stacks.sha(json.dumps({'installed': entry, 'plan': plan}, sort_keys=True))
        print(json.dumps({**plan, 'approval_sha256': token}, indent=2))
        if check:
            return 'Update available; no changes made'
        if approve is None:
            if not sys.stdin.isatty():
                raise WorkspaceError('No approval; inspect with --check then pass --approve SHA256 after user approval')
            try:
                answer = input(f'Update {sid} from {current} to {target}? [y/N] ')
            except EOFError:
                answer = ''
            if answer.strip().lower() not in ('y', 'yes'):
                return 'Update declined; no changes made'
        elif approve != token:
            raise WorkspaceError('Update inspection changed; inspect and obtain renewed approval')
        stacks.install(root, directory, trust, provenance=origin, replacing=entry,
                       prerequisite_release=metadata['release'] if metadata else None,
                       confirmed=confirmed)
        installed = next(e for e in stacks.available(root) if e['id'] == sid)
        stacks.check_owned(root, installed)
        return f'Updated {sid} to {target}; restart hosts to refresh loaded skills'


def projection_conflicts(root, sid, entry, manifest, files, *, bounded=False):
    """Check CLI update collisions, including disabled host projections."""
    for relative in files:
        target_path = f'.tdt/stacks/{sid}/{relative}'
        if bounded and target_path not in entry['files']:
            from .recovery import read_bytes
            read_bytes(root, target_path, 1048576)
        if target_path not in entry['files'] and stacks.existing_content(root, target_path) is not None:
            raise WorkspaceError('New bundle path conflict: ' + target_path)
    for relative in manifest['skills']:
        name = relative.split('/')[1]
        for folder in ('.tdt/skills', '.agents/skills', '.claude/skills'):
            directory_path = f'{folder}/{name}'
            if managed_path(root, directory_path).exists() and directory_path + '/SKILL.md' not in entry['files']:
                raise WorkspaceError('New skill directory conflict: ' + directory_path)
        if managed_path(root, f'.claude/commands/{name}.md').exists():
            raise WorkspaceError('Claude command conflict: ' + name)


def local_preview(root, sid, directory, *, candidate_timestamp=None):
    """Complete local update snapshot; caller holds a shared workspace lock."""
    from .recovery import read_bytes
    from datetime import datetime
    candidate_timestamp = candidate_timestamp or stacks.now()
    if (datetime.fromisoformat(candidate_timestamp).isoformat() != candidate_timestamp
            or not candidate_timestamp.endswith('+00:00')):
        raise WorkspaceError('Expected canonical UTC candidate timestamp')
    read_bytes(root, stacks.REGISTRY, 1048576)
    entries = stacks.available(root)
    if len(entries) > 2000 or any(not isinstance(e.get('version'), str) or
                                not stacks.VERSION.fullmatch(e['version']) for e in entries):
        raise WorkspaceError('Invalid or oversized installed stack catalog')
    entry = next((e for e in entries if e['id'] == sid), None)
    if entry is None:
        raise WorkspaceError('Stack is not installed')
    if entry['origin'].get('kind') != 'local':
        raise WorkspaceError('Local preview requires a locally installed stack; source switching refused')
    with replacement(entry, source=directory, bounded=True) as (_, manifest, files, origin, _):
        if manifest['id'] != sid:
            raise WorkspaceError('Replacement stack ID mismatch')
        projection_conflicts(root, sid, entry, manifest, files, bounded=True)
        changes = stacks.installation_plan(root, manifest, files, origin,
                                           replacing=entry, bounded=True,
                                           candidate_timestamp=candidate_timestamp)
    before = {}
    remaining = 8 * 1048576
    for relative in changes:
        raw = read_bytes(root, relative, remaining)
        before[relative] = None if raw is None else stacks.content_value(raw)
        remaining -= len(raw) if raw is not None else 0
    proposal = {'id': sid, 'candidate_timestamp': candidate_timestamp,
            'current_version': entry['version'],
            'target_version': manifest['version'], 'current_origin': entry['origin'],
            'target_origin': origin,
            'requires_executable_trust': bool(manifest['hooks'] or manifest.get('capabilities')),
            'before': before, 'after': changes}

    return {**proposal, 'proposal_sha256': stacks.sha(json.dumps(
        proposal, ensure_ascii=False, sort_keys=True, separators=(',', ':')))}


def local_apply(root, sid, directory, *, candidate_timestamp, expected_sha256, trust=None):
    """Apply the complete reviewed local update under exclusive locking."""
    from .recovery import read_bytes
    read_bytes(root, '.tdt/config.json', 1048576)
    with stacks.locked(root):
        preview = local_preview(root, sid, directory, candidate_timestamp=candidate_timestamp)
        if preview['proposal_sha256'] != expected_sha256:
            raise WorkspaceError('Stack update preview changed; inspect again')
        digest = preview['target_origin']['sha256']
        if preview['requires_executable_trust'] and trust != digest:
            raise WorkspaceError('Executable stack content requires explicit source digest trust')
        if trust is not None and trust != digest:
            raise WorkspaceError('Executable trust digest does not match source')
        entry = next(e for e in stacks.available(root) if e['id'] == sid)
        stacks.transaction(root, preview['after'], bounded=True)
        stacks.prune(root, entry['files'])
    return sid
