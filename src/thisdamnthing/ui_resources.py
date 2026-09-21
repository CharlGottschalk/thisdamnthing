"""Preflight core UI resources independently of optional host adapters."""
from .bootstrap import digest, encode, existing_text
from .workspace import read_json, resource_text, WorkspaceError, managed_path

MANIFEST = '.tdt/state/ui-resources.json'
RESOURCES = {
    '.tdt/contracts/ui.md': 'harness/contracts/ui.md',
    '.tdt/skills/tdt-ui/SKILL.md': 'harness/skills/tdt-ui/SKILL.md',
    'docs/ui.md': 'docs/ui.md',
}


def plan(root):
    raw = existing_text(root, MANIFEST)
    previous = read_json(root, MANIFEST) if raw is not None else {}
    legacy = '.tdt/skills/tdt.ui/SKILL.md'
    if not isinstance(previous, dict) or set(previous) - (RESOURCES.keys() | {legacy}):
        raise WorkspaceError('Invalid core UI ownership manifest')
    pending = {}
    if legacy in previous:
        current = existing_text(root, legacy)
        if current is None or digest(current) != previous[legacy]:
            raise WorkspaceError(f'Core UI resource edited or missing: {legacy}')
        pending[legacy] = None
    hashes = {}
    for target, source in RESOURCES.items():
        content = resource_text(source)
        current = existing_text(root, target)
        if target in previous:
            if current is None or digest(current) != previous[target]:
                raise WorkspaceError(f'Core UI resource edited or missing: {target}')
        elif target.endswith('/SKILL.md') and managed_path(root, target.rsplit('/', 1)[0]).exists():
            raise WorkspaceError(f'Core UI skill directory conflict: {target}')
        elif current is not None:
            raise WorkspaceError(f'Core UI resource conflict: {target}')
        hashes[target] = digest(content)
        if current != content:
            pending[target] = content
    pending[MANIFEST] = encode(hashes)
    return pending
