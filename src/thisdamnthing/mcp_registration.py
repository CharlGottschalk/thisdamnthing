"""Explicit workspace-local MCP registration with entry ownership."""
import json
from pathlib import Path
import sys
import tomllib

from .bootstrap import encode, parse_settings
from .brain import locked
from .recovery import read_bytes
from .workspace import WorkspaceError

STATE = '.tdt/state/mcp.json'
PATHS = {'claude': '.mcp.json', 'codex': '.codex/config.toml'}
NAME = 'thisdamnthing'
BEGIN = '# tdt:mcp:begin\n'
END = '# tdt:mcp:end\n'
LIMIT = 1048576


def text(root, path):
    raw = read_bytes(root, path, LIMIT)
    return None if raw is None else raw.decode('utf-8')


def state(root):
    raw = text(root, STATE)
    data = {'format_version': 1, 'hosts': {}} if raw is None else parse_settings(raw)
    if (not isinstance(data, dict) or set(data) != {'format_version', 'hosts'}
            or type(data['format_version']) is not int or data['format_version'] != 1
            or not isinstance(data['hosts'], dict) or set(data['hosts']) - PATHS.keys()):
        raise WorkspaceError('Invalid MCP ownership record')
    for entry in data['hosts'].values():
        if (not isinstance(entry, dict) or set(entry) != {'command', 'args'}
                or not isinstance(entry['command'], str) or not Path(entry['command']).is_absolute()
                or '\x00' in entry['command']
                or not isinstance(entry['args'], list) or len(entry['args']) != 8
                or entry['args'][:3] != ['-m', 'thisdamnthing', '--workspace']
                or not isinstance(entry['args'][3], str) or not Path(entry['args'][3]).is_absolute()
                or '\x00' in entry['args'][3]
                or entry['args'][4:7] != ['mcp', 'serve', '--profile']
                or entry['args'][7] not in ('read-only', 'everyday')):
            raise WorkspaceError('Invalid owned MCP launch configuration')
    return data


def block(entry):
    # JSON string/array encodings are also valid TOML basic values here.
    return (BEGIN + f'[mcp_servers.{NAME}]\ncommand = ' + json.dumps(entry['command'], ensure_ascii=False)
            + '\nargs = ' + json.dumps(entry['args'], ensure_ascii=False) + '\n' + END)


def parse(host, raw):
    data = (parse_settings(raw) if host == 'claude' else tomllib.loads(raw)) if raw else {}
    key = 'mcpServers' if host == 'claude' else 'mcp_servers'
    if not isinstance(data, dict) or not isinstance(data.get(key, {}), dict):
        raise WorkspaceError('Invalid host MCP configuration')
    return data, key


def merge(host, raw, previous, desired):
    """Reject unowned names and edited entries; preserve all unrelated settings."""
    raw = raw or ''
    data, key = parse(host, raw)
    servers = data.get(key, {})
    if previous is None:
        if NAME in servers:
            raise WorkspaceError('MCP server name already exists without TDT ownership')
    elif NAME not in servers or servers[NAME] != previous:
        raise WorkspaceError('Owned MCP entry changed or missing; preserve and reconcile it manually')
    if host == 'claude':
        if desired is None:
            servers.pop(NAME, None)
        else:
            servers[NAME] = desired
        if servers or key in data:
            data[key] = servers
        return encode(data)
    # Exact marked block ownership avoids reserializing arbitrary user TOML.
    if previous is None:
        if BEGIN.strip() in raw or END.strip() in raw:
            raise WorkspaceError('Unowned MCP markers in Codex configuration')
        remaining = raw
    else:
        owned = block(previous)
        if (raw.count(BEGIN.strip()) != 1 or raw.count(END.strip()) != 1
                or raw.count(owned) != 1):
            raise WorkspaceError('Owned Codex MCP block changed or missing')
        remaining = raw.replace(owned, '', 1)
    replacement = remaining
    if desired is not None:
        replacement += ('\n' if remaining and not remaining.endswith('\n') else '') + block(desired)
    # Detect table-scope changes, multiline-string markers, dotted/inline tables,
    # or user keys accidentally attached to the managed table.
    expected = dict(data)
    expected[key] = dict(servers)
    expected[key].pop(NAME, None)
    if desired is not None:
        expected[key][NAME] = desired
    actual, _ = parse(host, replacement)
    if not expected[key]:
        expected.pop(key)
    if actual.get(key) == {}:
        actual.pop(key)
    if actual != expected:
        raise WorkspaceError('Codex MCP edit would change unrelated settings')
    return replacement


def configure(root, host, action, profile='read-only'):
    from .skills import ready
    from .stacks import transaction
    if host not in PATHS or action not in ('register', 'unregister', 'status'):
        raise WorkspaceError('Unknown MCP host or registration action')
    if profile not in ('read-only', 'everyday'):
        raise WorkspaceError('Unknown MCP profile')
    # Bound config before the shared lock's ordinary config read.
    text(root, '.tdt/config.json')
    with locked(root, shared=action == 'status'):
        ready(root)
        data = state(root)
        previous = data['hosts'].get(host)
        raw = text(root, PATHS[host])
        if action == 'status':
            current, key = parse(host, raw)
            present = NAME in current.get(key, {})
            if previous is not None:
                merge(host, raw, previous, previous)
            return {'host': host, 'path': PATHS[host],
                    'status': 'owned' if previous else ('unowned' if present else 'absent'),
                    'entry': previous}
        if action == 'unregister' and previous is None:
            current, key = parse(host, raw)
            if NAME in current.get(key, {}):
                raise WorkspaceError('Refusing to remove an unowned MCP entry')
            return {'host': host, 'status': 'absent'}
        desired = None if action == 'unregister' else {
            # Keep the venv interpreter path: resolving its symlink loses the venv.
            'command': str(Path(sys.executable).absolute()),
            'args': ['-m', 'thisdamnthing', '--workspace', str(root),
                     'mcp', 'serve', '--profile', profile]}
        replacement = merge(host, raw, previous, desired)
        if desired is None:
            data['hosts'].pop(host)
        else:
            data['hosts'][host] = desired
        changes = {PATHS[host]: replacement, STATE: encode(data)}
        if any(len(value.encode('utf-8')) > LIMIT for value in changes.values()):
            raise WorkspaceError('MCP configuration exceeds 1 MiB')
        changes = {path: value for path, value in changes.items() if text(root, path) != value}
        if changes:
            transaction(root, changes, bounded=True)
        return {'host': host, 'status': 'registered' if desired else 'unregistered',
                'path': PATHS[host], 'entry': desired,
                'next_step': 'Restart the host and review project trust/MCP approval. Registration does not grant permissions or enable capture.'}
