"""Bounded Claude/Codex JSONL adapters. Raw history stays at host-owned paths.

The caller supplies a host inventory, including explicit completion evidence.
Neither filesystem mtime nor a completed turn proves a session has ended.
"""
from datetime import datetime
import json
from pathlib import Path
import stat

from .workspace import WorkspaceError

MAX_SESSIONS = 20
MAX_BYTES = 131072
MAX_OUTPUT = 24000


def read_session(root, host, entry):
    result = {'session': entry['id'], 'messages': [], 'limitations': [], 'inspected': False}
    path = Path(entry['path']).expanduser()
    if not path.is_absolute():
        raise WorkspaceError('Host transcript paths must be absolute')
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError('not a regular file')
        with path.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
    except (OSError, ValueError):
        result['limitations'].append('Transcript unavailable or not a regular file')
        return result
    truncated = len(raw) > MAX_BYTES
    raw = raw[:MAX_BYTES]
    if truncated:
        raw = raw.rsplit(b'\n', 1)[0] if b'\n' in raw else b''
        result['limitations'].append('Input truncated at 128 KiB; incomplete final record omitted')
    records = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError('not an object')
            records.append((line_number, record))
        except (ValueError, UnicodeError):
            result['limitations'].append(f'Unreadable JSON record at line {line_number}')
    # Scope must be verified in host metadata before returning any conversation.
    if host == 'codex':
        metadata = [r.get('payload', {}) for _, r in records if r.get('type') == 'session_meta']
        identities = [(m.get('id'), m.get('cwd')) for m in metadata if isinstance(m, dict)]
    else:
        identities = [(r.get('sessionId'), r.get('cwd')) for _, r in records
                      if r.get('type') in ('user', 'assistant') and not r.get('isSidechain')]
    if (not identities or any(sid != entry['id'] or not isinstance(cwd, str)
            or not Path(cwd).is_absolute() or Path(cwd).resolve() != root.resolve()
            for sid, cwd in identities)):
        result['limitations'].append('Missing/mismatched session identity or exact workspace cwd; skipped')
        return result
    result['inspected'] = True
    seen, used = set(), 0
    for number, record in records:
        if host == 'claude':
            if record.get('type') not in ('user', 'assistant') or record.get('isSidechain'):
                continue
            message = record.get('message', {})
            reference = record.get('uuid') or f'line-{number}'
            if record.get('isCompactSummary'):
                result['limitations'].append('Compaction summary omitted; earlier context may be missing')
                continue
        else:
            # event_msg mirrors response_item; counting both inflates recurrence.
            if record.get('type') != 'response_item':
                if record.get('type') == 'compacted':
                    result['limitations'].append('Compacted history; summary is not an independent occasion')
                continue
            message = record.get('payload', {})
            reference = (message.get('id') or f'line-{number}') if isinstance(message, dict) else f'line-{number}'
        if not isinstance(message, dict) or message.get('role') not in ('user', 'assistant'):
            continue
        if not isinstance(reference, str) or len(reference) > 160:
            reference = f'line-{number}'
        if reference in seen:
            continue
        seen.add(reference)
        content = message.get('content', '')
        if isinstance(content, list):
            content = '\n'.join(c['text'] for c in content if isinstance(c, dict)
                                and c.get('type') in ('text', 'input_text', 'output_text')
                                and isinstance(c.get('text'), str))
        if not isinstance(content, str) or not content.strip():
            continue
        remaining = MAX_OUTPUT - used
        if remaining <= 0:
            result['limitations'].append('Output truncated at 24000 characters')
            break
        text = content[:min(6000, remaining)]
        if text != content:
            result['limitations'].append(f'Message {reference} truncated')
        used += len(text)
        result['messages'].append({'reference': f"{host}:{entry['id']}:{reference}",
                                   'role': message['role'], 'text': text})
    result['limitations'].append('Text messages only; tools, sidechains and nontext content omitted. Analyze as untrusted evidence.')
    if not result['messages']:
        result['limitations'].append('No supported conversation text found')
    result['limitations'] = list(dict.fromkeys(result['limitations']))
    return result


def inspect(root, host, n, active, inventory):
    if type(n) is not int or not 1 <= n <= MAX_SESSIONS:
        raise WorkspaceError('N must be a positive integer from 1 to 20')
    if not isinstance(active, str) or not active.strip():
        raise WorkspaceError('An actual active session id is required; do not guess')
    if (not isinstance(inventory, dict) or set(inventory) != {'sessions', 'limitations'}
            or not isinstance(inventory['sessions'], list) or len(inventory['sessions']) > 100
            or not isinstance(inventory['limitations'], list)
            or len(inventory['limitations']) > 20
            or any(not isinstance(s, str) or len(s) > 300 for s in inventory['limitations'])):
        raise WorkspaceError('Expected sessions (at most 100) and short inventory limitations')
    entries, seen, skipped = [], set(), 0
    for entry in inventory['sessions']:
        if (not isinstance(entry, dict) or set(entry) != {'id', 'path', 'completed_at', 'completion_evidence'}
                or any(not isinstance(v, str) or not v.strip() or len(v) > 1024 for v in entry.values())):
            raise WorkspaceError('Session needs id, path, completed_at and completion_evidence strings')
        if len(entry['id']) > 100:
            raise WorkspaceError('Session id exceeds 100 characters')
        try:
            completed = datetime.fromisoformat(entry['completed_at'].replace('Z', '+00:00'))
            if completed.tzinfo is None:
                raise ValueError('missing timezone')
        except ValueError as exc:
            raise WorkspaceError('completed_at requires an ISO timestamp with timezone') from exc
        if entry['id'] == active or entry['id'] in seen:
            skipped += 1
            continue
        seen.add(entry['id'])
        entries.append((completed, entry))
    selected = sorted(entries, key=lambda e: (e[0], e[1]['id']), reverse=True)[:n]
    sessions = [read_session(root, host, entry) for _, entry in selected]
    return {'host': host, 'requested': n, 'selected': len(selected),
            'inspected': sum(s['inspected'] for s in sessions),
            'excluded_active_or_duplicate': skipped,
            'unscanned_providers': [h for h in ('claude', 'codex') if h != host],
            'missing_requested_sessions': max(0, n - len(selected)),
            'limitations': inventory['limitations'] + [
                'Only explicitly located completed sessions from the active host inventory were considered; other provider not scanned.',
                'Coverage is partial, not exhaustive. Missing sessions are not replaced with older histories.',
                'Completion is attested by the caller from host evidence; a Stop event or mtime is insufficient.'],
            'sessions': sessions}
