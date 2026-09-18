"""Versioned on-demand local search providers; core alone returns evidence."""
import hashlib
import json
import os
from pathlib import Path
import platform
import selectors
import signal
import subprocess
import sys
import tempfile
import time

from .workspace import WorkspaceError, managed_path, read_json
from . import brain, stacks

MAX_ASSET = 128 * 1024 * 1024
MAX_BUNDLE = 384 * 1024 * 1024
MAX_INPUT = 16 * 1024 * 1024
MAX_OUTPUT = 256 * 1024
STATE = '.dryft/state/capability-state.json'


def validate_manifest(data, source, files, metadata_only=False):
    if not {'assets', 'capabilities', 'compatibility'} <= data.keys():
        raise WorkspaceError('v2 requires assets, capabilities and compatibility')
    compat = data['compatibility']
    if (not isinstance(compat, dict) or set(compat) != {'dryft', 'platforms', 'python'}
            or compat['dryft'] != '0.1' or not isinstance(compat['platforms'], list)
            or not compat['platforms'] or any(p not in ('linux-x86_64', 'linux-aarch64', 'darwin-arm64', 'darwin-x86_64') for p in compat['platforms'])
            or not isinstance(compat['python'], list) or not compat['python']
            or any(p not in ('3.11', '3.12', '3.13') for p in compat['python'])):
        raise WorkspaceError('Invalid v2 compatibility (Dryft 0.1, explicit platform and Python minor lists)')
    assets = data['assets']
    if not isinstance(assets, list) or len(assets) > 10000:
        raise WorkspaceError('Expected at most 10000 explicit assets')
    total = sum(len(stacks.content_bytes(v)) for v in files.values())
    import unicodedata
    spellings = {unicodedata.normalize('NFC', p).casefold() for p in files}
    asset_hashes = {}
    for asset in assets:
        if (not isinstance(asset, dict) or set(asset) != {'path', 'sha256', 'size'}
                or type(asset['size']) is not int or not 0 <= asset['size'] <= MAX_ASSET
                or not isinstance(asset['sha256'], str) or not brain.IDENTIFIER.fullmatch(asset['sha256'])):
            raise WorkspaceError('Asset requires path, SHA256 and size <=128 MiB')
        relative = stacks.safe_path(asset['path'])
        if not relative.startswith('assets/') or unicodedata.normalize('NFC', relative).casefold() in spellings:
            raise WorkspaceError('Asset path must be unique under assets/')
        spellings.add(unicodedata.normalize('NFC', relative).casefold())
        path = managed_path(source, relative)
        total += asset['size']
        if total > MAX_BUNDLE or not path.is_file() or path.stat().st_size != asset['size']:
            raise WorkspaceError('Asset missing, size mismatch or bundle exceeds 384 MiB')
        if metadata_only:
            digest = stacks.file_sha(path)
        else:
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            files[relative] = stacks.content_value(raw)
        if digest != asset['sha256']:
            raise WorkspaceError('Asset hash mismatch: ' + relative)
        asset_hashes[relative] = digest
    prefixes = {}
    for relative in {*files, *asset_hashes}:
        for parent in (*Path(relative).parents, Path(relative)):
            key = unicodedata.normalize('NFC', str(parent)).casefold()
            if prefixes.setdefault(key, str(parent)) != str(parent):
                raise WorkspaceError('Normalized asset directory collision')
    caps = data['capabilities']
    if not isinstance(caps, list) or len(caps) != 1:
        raise WorkspaceError('v2 currently requires exactly one brain.search capability')
    cap = caps[0]
    if (not isinstance(cap, dict) or set(cap) != {'name', 'interface_version', 'entrypoint'}
            or cap['name'] != 'brain.search' or type(cap['interface_version']) is not int
            or cap['interface_version'] != 1 or not isinstance(cap['entrypoint'], str)
            or cap['entrypoint'] not in asset_hashes or not cap['entrypoint'].startswith('assets/')
            or not cap['entrypoint'].endswith('.py')):
        raise WorkspaceError('Expected brain.search interface 1 and an explicitly hashed assets/*.py entrypoint')
    return asset_hashes


def discover(root):
    return [{'id': e['id'], 'version': e['version'], 'capabilities': e['manifest']['capabilities'],
             'compatibility': e['manifest']['compatibility'],
             'trusted': e.get('trusted_capabilities') == e['origin'].get('sha256')}
            for e in stacks.available(root) if e['manifest'].get('capabilities')]


def selected(root, ids):
    if not ids or len(ids) > 8 or len(set(ids)) != len(ids):
        raise WorkspaceError('Select 1–8 distinct provider stack IDs')
    entries = {e['id']: e for e in stacks.available(root)}
    result = []
    for sid in sorted(ids):
        entry = entries.get(sid)
        if not entry or not entry['manifest'].get('capabilities'):
            raise WorkspaceError(f'Provider unavailable: {sid}; omit --provider for literal search')
        stacks.check_owned(root, entry)
        manifest, _, origin = stacks.validate(managed_path(root, f'.dryft/stacks/{sid}'), metadata_only=True, legacy_id=True)
        if origin['sha256'] != entry.get('trusted_capabilities') or manifest != entry['manifest']:
            raise WorkspaceError('Provider snapshot changed or lacks trust: ' + sid)
        compat = manifest['compatibility']
        host = sys.platform + '-' + platform.machine().lower()
        if host not in compat['platforms'] or f'{sys.version_info.major}.{sys.version_info.minor}' not in compat['python']:
            raise WorkspaceError(f'Provider {sid} incompatible with {host}/Python {sys.version_info.major}.{sys.version_info.minor}; use literal search')
        result.append(entry)
    return result


def run(argv, request, cwd, timeout):
    """Bound all three pipes and kill the process group on every exit path."""
    raw = json.dumps(request, ensure_ascii=False).encode()
    if len(raw) > MAX_INPUT:
        raise WorkspaceError('Provider request exceeds 16 MiB; reduce corpus size')
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME')}
    env.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=cwd, env=env, start_new_session=True)
    output, errors, offset = bytearray(), bytearray(), 0
    deadline = time.monotonic() + timeout
    try:
        with selectors.DefaultSelector() as poll:
            for pipe, event in ((process.stdin, selectors.EVENT_WRITE), (process.stdout, selectors.EVENT_READ), (process.stderr, selectors.EVENT_READ)):
                os.set_blocking(pipe.fileno(), False)
                poll.register(pipe, event)
            while poll.get_map():
                if time.monotonic() >= deadline:
                    raise WorkspaceError('Provider timed out; process group cancelled')
                for key, event in poll.select(min(.1, max(0, deadline - time.monotonic()))):
                    pipe = key.fileobj
                    if event == selectors.EVENT_WRITE:
                        try:
                            offset += os.write(pipe.fileno(), raw[offset:offset + 65536])
                        except BrokenPipeError:
                            offset = len(raw)
                        if offset == len(raw):
                            poll.unregister(pipe)
                            pipe.close()
                    else:
                        chunk = os.read(pipe.fileno(), 65536)
                        target = output if pipe is process.stdout else errors
                        target.extend(chunk)
                        if len(target) > MAX_OUTPUT:
                            raise WorkspaceError('Provider output exceeds 256 KiB')
                        if not chunk:
                            poll.unregister(pipe)
                            pipe.close()
            try:
                code = process.wait(timeout=max(.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired as exc:
                raise WorkspaceError('Provider timed out') from exc
            if code:
                raise WorkspaceError('Provider failed: ' + errors.decode('utf-8', errors='replace')[:2000])
            try:
                value = stacks.parse_settings(output.decode('utf-8'))
            except (ValueError, UnicodeError) as exc:
                raise WorkspaceError('Provider returned malformed JSON') from exc
            if not isinstance(value, dict) or type(value.get('protocol_version')) is not int or value['protocol_version'] != 1:
                raise WorkspaceError('Provider response requires protocol_version 1')
            return value
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        for pipe in (process.stdin, process.stdout, process.stderr):
            pipe.close()


def corpus(root):
    notes = brain.eligible_notes(root)
    return notes, [{'id': key, 'title': note[1], 'text': note[2],
                    'sha256': stacks.sha(json.dumps(note, ensure_ascii=False))}
                   for key, note in notes.items()]


def state(root):
    value = read_json(root, STATE) if managed_path(root, STATE).exists() else {}
    if not isinstance(value, dict):
        raise WorkspaceError('Invalid capability state registry')
    for sid, record in value.items():
        if (not (stacks.ID.fullmatch(sid) or stacks.LEGACY_ID.fullmatch(sid)) or not isinstance(record, dict)
                or set(record) != {'sha256', 'snapshot'}
                or any(not isinstance(v, str) or not brain.IDENTIFIER.fullmatch(v) for v in record.values())):
            raise WorkspaceError('Invalid capability cache ownership')
    return value


def cache_path(sid):
    return f'.dryft/state/capabilities/{sid}/index'


def cache_changes(root, sid):
    records = state(root)
    path = cache_path(sid)
    target = managed_path(root, path)
    if target.exists() and (not target.is_file() or target.stat().st_size > MAX_ASSET):
        raise WorkspaceError('Capability cache must be a regular file <=128 MiB; preserve/move before retry: ' + path)
    current = stacks.existing_content(root, path)
    record = records.get(sid)
    if current is not None and (record is None or stacks.sha(current) != record['sha256']):
        raise WorkspaceError('Capability cache modified; preserve/move before retry: ' + path)
    records.pop(sid, None)
    changes = {STATE: stacks.encode(records)} if record else {}
    if current is not None:
        changes[path] = None
    return changes


def invoke(root, entry, documents, operation, query='', rebuild=False):
    sid = entry['id']
    records = state(root)
    cache_changes(root, sid)  # Verify ownership before reading or replacing cache.
    with tempfile.TemporaryDirectory(prefix='dryft-provider-') as folder:
        index_path = Path(folder) / 'index'
        previous = managed_path(root, cache_path(sid))
        if not rebuild and previous.exists() and records.get(sid, {}).get('snapshot') == entry['origin']['sha256']:
            index_path.write_bytes(previous.read_bytes())
        request = {'protocol_version': 1, 'operation': operation, 'query': query,
                   'notes': documents, 'limit': 50, 'rebuild': rebuild, 'state_path': str(index_path)}
        base = managed_path(root, f'.dryft/stacks/{sid}')
        result = run([sys.executable, '-I', '-B', str(base / entry['manifest']['capabilities'][0]['entrypoint'])],
                     request, folder, 300 if operation == 'index' else 20)
        if operation == 'index':
            if set(result) != {'protocol_version', 'indexed'} or type(result['indexed']) is not int or result['indexed'] != len(documents):
                raise WorkspaceError('Invalid provider index acknowledgement')
            if not index_path.is_file() or index_path.is_symlink() or index_path.stat().st_size > MAX_ASSET:
                raise WorkspaceError('Provider cache missing or exceeds 128 MiB')
            content = stacks.content_value(index_path.read_bytes())
            records[sid] = {'sha256': stacks.sha(content), 'snapshot': entry['origin']['sha256']}
            stacks.transaction(root, {cache_path(sid): content, STATE: stacks.encode(records)})
        elif set(result) != {'protocol_version', 'results'} or not isinstance(result['results'], list) or len(result['results']) > 50:
            raise WorkspaceError('Invalid provider search response')
        return result


def index(root, ids, rebuild=False):
    with brain.locked(root):
        entries = selected(root, ids)
        _, documents = corpus(root)
        return {entry['id']: invoke(root, entry, documents, 'index', rebuild=rebuild)['indexed'] for entry in entries}


def rank(root, query, notes, ids):
    with brain.locked(root):
        entries = selected(root, ids)
        current, documents = corpus(root)
        hashes = {d['id']: d['sha256'] for d in documents}
        rankings = []
        for entry in entries:
            result = invoke(root, entry, documents, 'search', query)
            ranking = []
            for item in result['results']:
                if (not isinstance(item, dict) or set(item) != {'id', 'sha256'}
                        or not isinstance(item['id'], str) or item['id'] in ranking
                        or item['id'] not in hashes or item['sha256'] != hashes[item['id']]):
                    raise WorkspaceError('Provider returned duplicate, stale or ineligible note IDs')
                ranking.append(item['id'])
            rankings.append(ranking)
        # Rank fusion avoids comparing incomparable FTS/cosine scores. Literal
        # matches participate; exact title/ID matches remain first.
        rankings.append([k for k, (_, title, body) in current.items() if query == k.casefold() or query in (title + '\n' + body).casefold()])
        scores = {}
        for ranking in rankings:
            for position, key in enumerate(ranking, 1):
                scores[key] = scores.get(key, 0) + 1 / (60 + position)
        fresh = brain.eligible_notes(root)
        # Recheck every item after subprocesses; never display cached provider text.
        notes.clear()
        notes.update({k: v for k, v in fresh.items() if current.get(k) == v})
        return sorted((k for k in scores if k in notes),
                      key=lambda k: (not (query == notes[k][1].casefold() or query == k.casefold()), -scores[k], k))
