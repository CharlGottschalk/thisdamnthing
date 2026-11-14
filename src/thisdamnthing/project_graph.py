"""File-level view of a graphify graph built in a registered project.

Reads <project>/graphify-out/graph.json; never runs graphify or returns file contents.
"""
import json
from datetime import datetime, timezone
from pathlib import PurePosixPath

from . import brain, projects, safefs
from .workspace import WorkspaceError

GRAPH = ('graphify-out', 'graph.json')
BUILD = ('graphify-out', '.graphify_build.json')
HOOK = ('.git', 'hooks', 'post-commit')
HOOK_MARKER = b'# graphify-hook-start'
SCHEMA_VERSIONS = (1,)
MAX_GRAPH = 64 * 1024 * 1024
MAX_SYMBOLS = 50
INSTRUCTIONS = {'CLAUDE.md', 'AGENTS.md', 'GEMINI.md'}
DOCS = {'.md', '.mdx', '.markdown', '.rst', '.txt', '.adoc'}
CONFIDENCE = {'EXTRACTED': 2, 'INFERRED': 1}


class UnsupportedSchema(WorkspaceError):
    pass


def read_file(directory, parts, limit):
    """Read a regular file below an open directory without following symlinks."""
    try:
        raw, info = directory.read(parts, limit + 1)
    except (FileNotFoundError, NotADirectoryError):
        return None, None
    except safefs.NotRegular as exc:
        raise WorkspaceError('Graph file is not a regular file or is too large') from exc
    if info.st_size > limit:
        raise WorkspaceError('Graph file is not a regular file or is too large')
    return raw, info.st_mtime


def safe_path(value):
    if not isinstance(value, str) or not value or len(value) > 512 or '\\' in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or path.parts[:1] == ('graphify-out',):
        return None
    return str(path)


def kind(path):
    name = PurePosixPath(path).name
    if name in INSTRUCTIONS:
        return 'instruction'
    return 'doc' if PurePosixPath(path).suffix.lower() in DOCS else 'code'


def fold(data):
    """Fold graphify's symbol nodes to one node per file and dedupe cross-file edges."""
    owner, files = {}, {}
    for node in data.get('nodes', []):
        if not isinstance(node, dict) or node.get('type') in ('external', 'module'):
            continue
        path = safe_path(node.get('source_file'))
        if path is None or not isinstance(node.get('id'), str):
            continue
        owner[node['id']] = path
        symbols = files.setdefault(path, set())
        label = node.get('label')
        if (isinstance(label, str) and node.get('file_type') == 'code' and node.get('source_location')
                and not path.endswith(label) and len(label) <= 200):
            symbols.add(label)
    edges = {}
    for link in data.get('links', data.get('edges', [])):
        if not isinstance(link, dict):
            continue
        source, target = owner.get(link.get('source')), owner.get(link.get('target'))
        relation = link.get('relation')
        if not source or not target or source == target or not isinstance(relation, str):
            continue
        confidence = link.get('confidence') if link.get('confidence') in CONFIDENCE else 'INFERRED'
        key = (source, target, relation)
        if CONFIDENCE[confidence] > CONFIDENCE.get(edges.get(key), 0):
            edges[key] = confidence
    nodes = [{'id': path, 'kind': kind(path), 'symbols': sorted(symbols)[:MAX_SYMBOLS],
              'symbols_total': len(symbols)} for path, symbols in sorted(files.items())]
    links = [{'source': s, 'target': t, 'relation': r, 'confidence': c}
             for (s, t, r), c in sorted(edges.items())]
    return nodes, links


def graph(root, key):
    entry = projects.find(root, key)
    with projects.directory_handle(entry['path']) as directory:
        raw, mtime = read_file(directory, GRAPH, MAX_GRAPH)
        hook, _ = read_file(directory, HOOK, 1024 * 1024)
        build, _ = read_file(directory, BUILD, 4096)
    result = {'project': entry['id'], 'status': 'no_graph', 'hook_installed': bool(hook and HOOK_MARKER in hook),
              'schema_version': None, 'graphify_version': None, 'built_at': None,
              'built_at_commit': None, 'code_only': None, 'nodes': [], 'links': []}
    if raw is None:
        return result
    try:
        data = json.loads(raw)
        meta = data['graph']
    except (ValueError, KeyError, TypeError):
        raise WorkspaceError('graph.json is not a graphify graph') from None
    version = meta.get('schema_version') if isinstance(meta, dict) else None
    if version not in SCHEMA_VERSIONS:
        raise UnsupportedSchema(f'Unsupported graphify schema_version {version!r}')
    try:
        code_only = json.loads(build).get('code_only') if build else None
    except (ValueError, AttributeError):
        code_only = None
    nodes, links = fold(data)
    commit = data.get('built_at_commit')
    result.update(status='graph', schema_version=version,
                  graphify_version=str(meta.get('graphify_version') or '') or None,
                  built_at=datetime.fromtimestamp(mtime, timezone.utc).isoformat(timespec='seconds'),
                  built_at_commit=commit if isinstance(commit, str) and len(commit) <= 64 else None,
                  code_only=code_only if isinstance(code_only, bool) else None,
                  nodes=nodes, links=links)
    return result


def revision(result):
    return brain.digest(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    # ponytail: self-check of the fold rules; run with `python -m thisdamnthing.project_graph`.
    sample = {'graph': {'schema_version': 1}, 'nodes': [
        {'id': 'a', 'label': 'a.ts', 'file_type': 'code', 'source_file': 'src/a.ts', 'source_location': 'L1'},
        {'id': 'a_f', 'label': 'run', 'file_type': 'code', 'source_file': 'src/a.ts', 'source_location': 'L2'},
        {'id': 'b', 'label': 'b.ts', 'file_type': 'code', 'source_file': 'src/b.ts'},
        {'id': 'm', 'label': 'esbuild', 'type': 'module', 'source_file': 'esbuild'},
        {'id': 'x', 'label': 'x', 'file_type': 'code', 'source_file': '../escape.ts'},
        {'id': 'c', 'label': 'CLAUDE.md', 'file_type': 'document', 'source_file': 'CLAUDE.md'}],
        'links': [
        {'source': 'a_f', 'target': 'b', 'relation': 'imports', 'confidence': 'INFERRED'},
        {'source': 'a', 'target': 'b', 'relation': 'imports', 'confidence': 'EXTRACTED'},
        {'source': 'a', 'target': 'a_f', 'relation': 'contains', 'confidence': 'EXTRACTED'},
        {'source': 'a', 'target': 'm', 'relation': 'imports', 'confidence': 'EXTRACTED'},
        {'source': 'c', 'target': 'a', 'relation': 'references', 'confidence': 'INFERRED'}]}
    n, l = fold(sample)
    assert [x['id'] for x in n] == ['CLAUDE.md', 'src/a.ts', 'src/b.ts'], n
    assert [x['kind'] for x in n] == ['instruction', 'code', 'code']
    assert n[1]['symbols'] == ['run'] and n[2]['symbols'] == []
    assert l == [{'source': 'CLAUDE.md', 'target': 'src/a.ts', 'relation': 'references', 'confidence': 'INFERRED'},
                 {'source': 'src/a.ts', 'target': 'src/b.ts', 'relation': 'imports', 'confidence': 'EXTRACTED'}], l
    print('ok')
