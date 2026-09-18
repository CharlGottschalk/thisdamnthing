"""Workspace-local host selection and owner-preserving skill enablement."""
import shutil
from pathlib import Path

from .workspace import WorkspaceError, read_config, managed_path
from .bootstrap import PROVIDERS, digest, encode, existing_text, load_manifest


def detected():
    """Only executable discovery; never launch a host or inspect global settings."""
    return [host for host in PROVIDERS if shutil.which(host)]


def enabled(root, config=None):
    config = read_config(root) if config is None else config
    selected = config.get('enabled_agents')
    if selected is not None:
        if (not isinstance(selected, list) or any(not isinstance(h, str) or h not in PROVIDERS for h in selected)
                or len(set(selected)) != len(selected)):
            raise WorkspaceError('Invalid enabled_agents in workspace config')
        return selected
    # Legacy consent comes only from ownership records, never from host folders.
    from . import stacks, skills
    manifest = load_manifest(root)
    records = [manifest['files'], *(e['files'] for e in stacks.registry(root)),
               *skills.state(root)['skills'].values()]
    return [host for host, (instruction, folder, settings) in PROVIDERS.items()
            if host in config['adapters'] or instruction in manifest['instructions']
            or settings in manifest['hooks']
            or any(any(p.startswith(folder + '/') for p in record) for record in records)]


def folders(root):
    return ['.dryft/skills', *(PROVIDERS[h][1] for h in enabled(root))]


def plan_skills(root, hosts):
    """Add bridges to each original owner's record; preflight before any write."""
    from . import stacks, skills
    skills.ready(root)
    entries = stacks.available(root)
    users = skills.state(root)
    changes = {}

    def add(name, record, content):
        for host in hosts:
            target = f'{PROVIDERS[host][1]}/{name}/SKILL.md'
            if host == 'claude' and managed_path(root, f'.claude/commands/{name}.md').exists():
                raise WorkspaceError(f'Claude command collision: {name}')
            if target in record:
                continue
            if managed_path(root, str(Path(target).parent)).exists():
                raise WorkspaceError(f'Skill directory collision: {target}')
            if target in changes:
                raise WorkspaceError(f'Duplicate skill ownership: {name}')
            changes[target] = content
            record[target] = digest(content)

    for entry in entries:
        stacks.check_owned(root, entry)
        for relative in entry['manifest']['skills']:
            name = relative.split('/')[1]
            add(name, entry['files'], stacks.bridge(name))
    for name, record in users['skills'].items():
        for path, expected in record.items():
            current = existing_text(root, path)
            if current is None or digest(current) != expected:
                raise WorkspaceError(f'Owned skill file edited or missing: {path}')
        # Preserve the approved description exactly, including older serialized YAML.
        canonical = existing_text(root, f'.dryft/skills/{name}/SKILL.md')
        if canonical is None or '\n---\n' not in canonical[4:]:
            raise WorkspaceError(f'Missing user skill front matter: {name}')
        head = canonical[:canonical.index('\n---\n', 4) + 5]
        add(name, record, head + '\n' +
            f'Read and follow .dryft/skills/{name}/SKILL.md from the workspace root.\n')
    if entries:
        changes[stacks.REGISTRY] = encode(entries)
    if users['skills']:
        changes[skills.STATE] = encode(users)
    return changes


def enable(root, host):
    from .workspace import initialize
    initialize(root, host)
    return f'Enabled {host} for all owned workspace skills. Start a new host session and review project trust and /hooks.'


def disable(root, host):
    """Remove only recorded host integrations, preserving canonical resources."""
    from . import stacks, skills
    from .brain import locked
    from .bootstrap import BEGIN, END, MANIFEST, parse_settings
    from .workspace import read_json
    if host not in PROVIDERS:
        raise WorkspaceError('Unknown agent selection')
    with locked(root):
        skills.ready(root)
        entries = stacks.available(root)
        users = skills.state(root)
        config = read_config(root)
        selected = enabled(root, config)
        if host not in selected:
            return f'{host.capitalize()} integration already disabled.'
        state = load_manifest(root)
        instruction, folder, settings = PROVIDERS[host]
        changes = {}
        records = [state['files'], *(e['files'] for e in entries), *users['skills'].values()]
        for record in records:
            for path, expected in list(record.items()):
                if not path.startswith(folder + '/'):
                    continue
                current = existing_text(root, path)
                if current is None or digest(current) != expected:
                    raise WorkspaceError(f'Owned agent bridge edited or missing: {path}')
                if path in changes:
                    raise WorkspaceError(f'Duplicate agent bridge ownership: {path}')
                changes[path] = None
                del record[path]
        previous = state['instructions'].get(instruction)
        if previous is not None:
            current = existing_text(root, instruction)
            if (not isinstance(previous, str) or current is None
                    or current.count(BEGIN) != 1 or current.count(END) != 1
                    or previous not in current):
                raise WorkspaceError(f'Owned instruction block changed or missing: {instruction}')
            remaining = current.replace(previous, '', 1)
            changes[instruction] = remaining if remaining.strip() else None
            del state['instructions'][instruction]
        hook_records = (('SessionStart', 'hooks'), ('Stop', 'capture_hooks'),
                        ('UserPromptSubmit', 'policy_hooks'))
        if any(settings in state[key] for _, key in hook_records):
            raw = existing_text(root, settings)
            data = parse_settings(raw) if raw is not None else None
            if not isinstance(data, dict) or not isinstance(data.get('hooks'), dict):
                raise WorkspaceError(f'Owned hook settings missing or invalid: {settings}')
            for event, key in hook_records:
                previous = state[key].get(settings)
                if previous is None:
                    continue
                values = data['hooks'].get(event)
                if not isinstance(values, list) or values.count(previous) != 1:
                    raise WorkspaceError(f'Owned {event} hook changed, duplicated or missing: {settings}')
                values.remove(previous)
                if not values:
                    del data['hooks'][event]
                del state[key][settings]
            if not data['hooks']:
                del data['hooks']
            # Settings have entry ownership, never whole-file ownership.
            changes[settings] = encode(data)
        config['enabled_agents'] = [h for h in selected if h != host]
        config['adapters'].pop(host, None)
        owned = read_json(root, '.dryft/state/owned-files.json')
        if not isinstance(owned, list) or any(not isinstance(p, str) for p in owned):
            raise WorkspaceError('Invalid owned-files list')
        changes[MANIFEST] = encode(state)
        changes['.dryft/config.json'] = encode(config)
        changes['.dryft/state/owned-files.json'] = encode(sorted(set(owned) -
            {p for p, value in changes.items() if value is None}))
        if entries:
            changes[stacks.REGISTRY] = encode(entries)
        if users['skills']:
            changes[skills.STATE] = encode(users)
        stacks.transaction(root, changes)
        stacks.prune(root, [p for p, value in changes.items() if value is None])
    return f'Disabled {host} workspace integration. Start a new host session; canonical skills and brain are preserved.'
