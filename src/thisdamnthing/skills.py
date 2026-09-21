"""User-owned workspace skills; approval records are separate from bootstrap/stacks."""
import json
import re
from pathlib import Path

from .bootstrap import SKILLS, PROVIDERS, digest, encode, existing_text
from .brain import atomic, locked
from .workspace import WorkspaceError, managed_path, read_json

STATE = '.tdt/state/user-skills.json'
JOURNAL = '.tdt/state/user-skill-transaction.json'
MAX_PROPOSALS = 100


def name_checked(name):
    if (not isinstance(name, str) or len(name) > 64
            or not re.fullmatch(r'tdt-[a-z0-9]+(?:-[a-z0-9]+)*', name)
            or name in SKILLS):
        raise WorkspaceError('Expected an unreserved tdt-name, at most 64 characters')
    return name


def paths(name, root=None):
    name_checked(name)
    from .agents import folders
    selected = folders(root) if root is not None else ('.tdt/skills', '.claude/skills', '.agents/skills')
    return [f'{folder}/{name}/SKILL.md' for folder in selected]


def text_checked(value, label, maximum):
    if (not isinstance(value, str) or not value.strip() or len(value) > maximum
            or any(ord(c) < 32 and c not in '\n\t' for c in value)):
        raise WorkspaceError(f'{label} must be nonempty text <= {maximum} characters')
    return value.strip()


def render(proposal, bridge=False):
    # JSON quoted strings are YAML scalars; colon/hash/newline cannot inject fields.
    head = (f"---\nname: {proposal['name']}\ndescription: "
            + json.dumps(proposal['description'], ensure_ascii=False) + '\n---\n\n')
    body = (f"Read and follow .tdt/skills/{proposal['name']}/SKILL.md from the workspace root."
            if bridge else proposal['instructions'])
    return head + body + '\n'


def valid_record(record, name):
    return (f'.tdt/skills/{name}/SKILL.md' in record
            and set(record).issubset(paths(name)))


def state(root):
    if not managed_path(root, STATE).exists():
        return {'version': 1, 'skills': {}, 'proposals': {}}
    value = read_json(root, STATE)
    if (not isinstance(value, dict) or value.get('version') != 1
            or not isinstance(value.get('skills'), dict)
            or not isinstance(value.get('proposals'), dict)):
        raise WorkspaceError('Invalid user skill registry')
    if len(value['proposals']) > MAX_PROPOSALS:
        raise WorkspaceError('User proposal registry exceeds 100 entries')
    for key, proposal in value['proposals'].items():
        if not isinstance(proposal, dict):
            raise WorkspaceError('Invalid skill proposal')
        behavior = {field: proposal.get(field) for field in ('name', 'description', 'instructions')}
        name_checked(behavior['name'])
        text_checked(behavior['description'], 'description', 1024)
        text_checked(behavior['instructions'], 'instructions', 10000)
        if (key != digest(json.dumps(behavior, sort_keys=True))
                or proposal.get('status') not in ('pending', 'approved', 'declined')):
            raise WorkspaceError('Changed proposal content or invalid decision; preserve and inspect registry')
        before = proposal.get('before')
        if before is not None and (not isinstance(before, dict)
                or not valid_record(before, behavior['name'])
                or any(not isinstance(h, str) or not re.fullmatch('[a-f0-9]{64}', h)
                       for h in before.values())):
            raise WorkspaceError('Invalid proposal ownership snapshot')
    for name, record in value['skills'].items():
        if (not isinstance(record, dict) or not valid_record(record, name)
                or any(not isinstance(h, str) or not re.fullmatch('[a-f0-9]{64}', h)
                       for h in record.values())):
            raise WorkspaceError('Invalid user skill ownership')
    return value


def ready(root):
    from .stacks import JOURNAL as STACK_JOURNAL
    if managed_path(root, STACK_JOURNAL).exists():
        raise WorkspaceError('Interrupted stack or agent operation; run tdt stack recover')
    if managed_path(root, JOURNAL).exists():
        raise WorkspaceError('Interrupted skill save; run tdt skill recover')


def inventory(root):
    ready(root)
    data = state(root)
    from .stacks import available
    stacks = available(root)
    results = []
    for folder in ('.tdt/skills', '.claude/skills', '.agents/skills'):
        directory = managed_path(root, folder)
        for child in sorted(directory.iterdir()) if directory.exists() else []:
            relative = f'{folder}/{child.name}/SKILL.md'
            path = managed_path(root, relative)
            if not path.is_file():
                continue
            with path.open(encoding='utf-8') as stream:
                content = stream.read(16385)
            owner = ('user' if child.name in data['skills'] else
                     'core' if child.name in SKILLS else
                     next((s['id'] for s in stacks if relative in s['files']), 'unmanaged'))
            results.append({'name': child.name, 'path': relative, 'owner': owner,
                            'content': content[:16384], 'truncated': len(content) > 16384})
    return {'skills': results, 'proposals': data['proposals']}


def propose(root, value):
    if not isinstance(value, dict) or set(value) - {'name', 'description', 'instructions', 'sources'}:
        raise WorkspaceError('Proposal requires name, description, instructions and optional sources')
    proposal = {'name': name_checked(value.get('name')),
                'description': text_checked(value.get('description'), 'description', 1024),
                'instructions': text_checked(value.get('instructions'), 'instructions', 10000)}
    sources = value.get('sources', [])
    if (not isinstance(sources, list) or len(sources) > 40
            or any(not isinstance(s, str) or len(s) > 160 or '\n' in s for s in sources)):
        raise WorkspaceError('sources must contain at most 40 short session/turn references')
    key = digest(json.dumps(proposal, sort_keys=True))
    with locked(root):
        ready(root)
        data = state(root)
        previous = data['proposals'].get(key)
        if previous is not None:
            if previous['status'] != 'approved' and previous.get('before') == data['skills'].get(proposal['name']):
                return {'id': key, **previous}
            owned = data['skills'].get(proposal['name'])
            check_targets(root, proposal['name'], owned)
            if owned == rendered_hashes(proposal, root):
                return {'id': key, **previous}
            # Historical approval is not approval to replace the current version.
            # Reopen the proposal against today's ownership snapshot.
        if previous is None and len(data['proposals']) >= MAX_PROPOSALS:
            raise WorkspaceError('100 retained proposals reached; review/archive the registry before adding more')
        owned = data['skills'].get(proposal['name'])
        check_targets(root, proposal['name'], owned)
        proposal.update(status='pending', sources=sources, before=owned)
        data['proposals'][key] = proposal
        atomic(root, STATE, encode(data))
    return {'id': key, **proposal}


def rendered_hashes(proposal, root):
    return {p: digest(render(proposal, bridge=i > 0))
            for i, p in enumerate(paths(proposal['name'], root))}


def check_targets(root, name, owned):
    from .stacks import available
    if owned is not None and set(owned) != set(paths(name, root)):
        raise WorkspaceError("Skill integrations changed; propose again before approval")
    if any(set(paths(name)) & set(entry['files']) for entry in available(root)):
        raise WorkspaceError(f'Stack owns skill name: {name}')
    for relative in (owned if owned is not None else paths(name, root)):
        current = existing_text(root, relative)
        if owned is None:
            if managed_path(root, str(Path(relative).parent)).exists():
                raise WorkspaceError(f'Skill directory collision: {relative}')
        elif current is None or digest(current) != owned[relative]:
            raise WorkspaceError(f'User skill edited or missing; preserve and reconcile: {relative}')
    if any(p.startswith('.claude/') for p in paths(name, root)) and managed_path(root, f'.claude/commands/{name}.md').exists():
        raise WorkspaceError(f'Claude command collision: {name}')


def recover(root):
    path = managed_path(root, JOURNAL)
    if not path.exists():
        return 'No user skill transaction to recover.'
    record = read_json(root, JOURNAL)
    if (not isinstance(record, dict) or set(record) != {'before', 'after'}
            or not isinstance(record['before'], dict) or not isinstance(record['after'], dict)
            or record['before'].keys() != record['after'].keys()):
        raise WorkspaceError('Invalid user skill journal')
    for relative, before in record['before'].items():
        if relative != STATE:
            match = re.fullmatch(r'(?:\.tdt|\.claude|\.agents)/skills/(tdt-[a-z0-9-]+)/SKILL.md', relative)
            if not match or relative not in paths(match[1]):
                raise WorkspaceError('Invalid user skill recovery path')
        after = record['after'][relative]
        if any(v is not None and not isinstance(v, str) for v in (before, after)):
            raise WorkspaceError('Invalid user skill recovery content')
        if existing_text(root, relative) not in (before, after):
            raise WorkspaceError(f'Recovery conflict; preserve and inspect {relative}')
    for relative, before in record['before'].items():
        if before is None:
            target = managed_path(root, relative)
            target.unlink(missing_ok=True)
            if relative != STATE:
                try:
                    target.parent.rmdir()
                except OSError:
                    pass
        else:
            atomic(root, relative, before)
    path.unlink()
    return 'Rolled back interrupted user skill save; proposal remains reviewable.'


def review(root, keys, decision, instruction):
    text_checked(instruction, 'user instruction reference', 300)
    if not keys or len(keys) > 20 or len(set(keys)) != len(keys):
        raise WorkspaceError('Select 1–20 distinct proposal ids')
    with locked(root):
        ready(root)
        data = state(root)
        changes, names = {}, set()
        for key in keys:
            proposal = data['proposals'].get(key)
            if proposal is None:
                raise WorkspaceError('Unknown proposal id')
            if proposal['name'] in names:
                raise WorkspaceError('Select only one version of each skill')
            names.add(proposal['name'])
            if proposal['status'] == ('approved' if decision == 'approve' else 'declined'):
                if decision == 'approve':
                    owned = data['skills'].get(proposal['name'])
                    check_targets(root, proposal['name'], owned)
                    if owned != rendered_hashes(proposal, root):
                        raise WorkspaceError('Approved version is no longer installed; propose it again before review')
                continue
            if proposal['status'] != 'pending' and not (proposal['status'] == 'declined' and decision == 'approve'):
                raise WorkspaceError('Proposal already approved; decline does not uninstall a skill')
            if decision == 'approve':
                check_targets(root, proposal['name'], proposal['before'])
                if data['skills'].get(proposal['name']) != proposal['before']:
                    raise WorkspaceError('Skill ownership changed since proposal')
                targets = paths(proposal['name'], root)
                for i, target in enumerate(targets):
                    changes[target] = render(proposal, bridge=i > 0)
                data['skills'][proposal['name']] = {p: digest(changes[p]) for p in targets}
            proposal['status'] = 'approved' if decision == 'approve' else 'declined'
            proposal['decision_reference'] = instruction
        changes[STATE] = encode(data)
        before = {p: existing_text(root, p) for p in changes}
        atomic(root, JOURNAL, encode({'before': before, 'after': changes}))
        try:
            for relative, content in changes.items():
                atomic(root, relative, content)
            managed_path(root, JOURNAL).unlink()
        except (OSError, ValueError):
            recover(root)
            raise
    return 'Saved decision. Approved skills may require a new host session to appear.'


def add_parser(commands):
    parser = commands.add_parser('skill', help='review and save workspace-local user skills')
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('list', 'propose', 'recover'):
        actions.add_parser(name)
    review_parser = actions.add_parser('review')
    review_parser.add_argument('ids', nargs='+')
    review_parser.add_argument('--decision', choices=('approve', 'decline'), required=True)
    review_parser.add_argument('--user-instruction', required=True, help='actual user message reference')
    history = actions.add_parser('history', help='read bounded, explicitly located host histories')
    history.add_argument('n', type=int)
    history.add_argument('--host', choices=tuple(PROVIDERS), required=True)
    history.add_argument('--active-session', required=True)


def cli(root, args, value=None):
    if args.action == 'list':
        return inventory(root)
    if args.action == 'propose':
        return propose(root, value)
    if args.action == 'review':
        return review(root, args.ids, args.decision, args.user_instruction)
    if args.action == 'recover':
        with locked(root):
            return recover(root)
    from .history import inspect
    return inspect(root, args.host, args.n, args.active_session, value)
