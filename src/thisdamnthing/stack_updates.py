"""Inspect a replacement in memory; approval never survives changed inputs."""
from contextlib import contextmanager
import json
import sys

from . import marketplace, stacks
from .bootstrap import existing_text
from .workspace import WorkspaceError, managed_path


@contextmanager
def replacement(entry, source=None, registry_url=None):
    origin = entry['origin']
    if origin.get('kind') == 'local':
        if registry_url:
            raise WorkspaceError('Local updates cannot switch to a registry')
        path = source or origin.get('path')
        if not path:
            raise WorkspaceError('Local source unavailable; select --source PATH')
        manifest, files, provenance = stacks.validate(path)
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
        # Inspect new projection collisions before asking for approval.
        for relative in files:
            target_path = f'.tdt/stacks/{sid}/{relative}'
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
