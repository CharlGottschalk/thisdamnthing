"""Explicit, bounded registry reads and immutable GitHub stack installation."""
from contextlib import contextmanager
from datetime import datetime
import hashlib
import io
import ipaddress
import http.client
import json
from pathlib import Path
import re
import stat
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request
from urllib.error import URLError
import zipfile
import unicodedata
import zlib

from . import stacks
from .bootstrap import parse_settings
from .workspace import WorkspaceError, resource_text

DEFAULT_REGISTRY = 'https://stacks.usedryft.com/registry/v1/index.json'
FEED_LIMIT = 5 * 1024 * 1024
ARCHIVE_LIMIT = 384 * 1024 * 1024
EXPANDED_LIMIT = 512 * 1024 * 1024


def origin(url):
    p = urlsplit(url)
    if (p.scheme != 'https' or not p.hostname or p.username or p.password
            or p.fragment):
        raise WorkspaceError('Expected a credential-free HTTPS URL')
    host = '[' + p.hostname + ']' if ':' in p.hostname else p.hostname
    return 'https://' + host + (':' + str(p.port) if p.port not in (None, 443) else '')


def local_archive_origin(value, registry_url):
    """Explicit test transport only; never permit arbitrary archive hosts."""
    if value is None:
        return None
    try:
        parsed = urlsplit(value)
        canonical = origin(value)
        if (value != canonical or parsed.path or parsed.query or parsed.fragment
                or parsed.username is not None or parsed.password is not None
                or not ipaddress.ip_address(parsed.hostname).is_loopback
                or canonical != origin(registry_url)):
            raise ValueError()
    except (ValueError, WorkspaceError):
        raise WorkspaceError('--local-archive-origin requires a literal-loopback HTTPS origin matching the registry origin, without credentials, path, query or fragment') from None
    return canonical


def fetch(url, limit, allowed_origin):
    """No cookies, credentials, cache, telemetry or cross-origin redirects."""
    class Redirects(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if origin(newurl) != allowed_origin:
                raise WorkspaceError('Cross-origin redirect refused')
            remaining = 30 - (time.monotonic() - started)
            if remaining <= 0:
                raise WorkspaceError('Download exceeded 30 seconds')
            req.timeout = remaining
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    if origin(url) != allowed_origin:
        raise WorkspaceError('Unexpected download origin')
    started = time.monotonic()
    try:
        with build_opener(Redirects()).open(Request(url, headers={
                'Accept': 'application/json' if limit == FEED_LIMIT else 'application/zip',
                'Accept-Encoding': 'identity', 'User-Agent': 'Dryft/0.1'}), timeout=30) as response:
            if response.status != 200 or response.headers.get('Content-Encoding', 'identity') != 'identity':
                raise WorkspaceError('Expected an unencoded HTTP 200 response')
            if limit == FEED_LIMIT and response.headers.get_content_type() != 'application/json':
                raise WorkspaceError('Registry must return application/json')
            chunks, size = [], 0
            while True:
                remaining = 30 - (time.monotonic() - started)
                if remaining <= 0:
                    raise WorkspaceError('Download exceeded 30 seconds')
                # A known-length final read closes fp before the next iteration.
                if response.fp is None:
                    break
                # Bound each underlying read by the remaining total deadline.
                response.fp.raw._sock.settimeout(remaining)
                chunk = response.read1(min(65536, limit + 1 - size))
                size += len(chunk)
                if size > limit:
                    raise WorkspaceError('Download exceeds size limit')
                if not chunk:
                    break
                chunks.append(chunk)
            if response.length not in (None, 0):
                raise WorkspaceError('Truncated download')
            return b''.join(chunks)
    except (URLError, OSError, ValueError, http.client.HTTPException) as exc:
        raise WorkspaceError(f'Download failed: {exc}') from exc


def validate_schema(value, rule, schema, path='$'):
    """Validate the keyword subset used by our bundled, fixed v1 schema."""
    if '$ref' in rule:
        return validate_schema(value, schema['$defs'][rule['$ref'].split('/')[-1]], schema, path)
    if 'anyOf' in rule:
        for choice in rule['anyOf']:
            try:
                validate_schema(value, choice, schema, path)
                return
            except WorkspaceError:
                pass
        raise WorkspaceError(f'Invalid registry value at {path}')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    if 'type' in rule and type(value) is not types[rule['type']]:
        raise WorkspaceError(f'Invalid registry type at {path}')
    if ('const' in rule and (type(value) is not type(rule['const']) or value != rule['const'])
            or 'enum' in rule and value not in rule['enum']):
        raise WorkspaceError(f'Unsupported registry value at {path}')
    if isinstance(value, dict):
        props = rule.get('properties', {})
        if not set(rule.get('required', [])) <= value.keys() or (rule.get('additionalProperties') is False and value.keys() - props.keys()):
            raise WorkspaceError(f'Invalid registry fields at {path}')
        for key, item in value.items():
            validate_schema(item, props[key], schema, path + '.' + key)
    if isinstance(value, list):
        if not rule.get('minItems', 0) <= len(value) <= rule.get('maxItems', 10000):
            raise WorkspaceError(f'Invalid registry list size at {path}')
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise WorkspaceError(f'Duplicate registry item at {path}')
        for item in value:
            validate_schema(item, rule['items'], schema, path + '[]')
    if isinstance(value, str):
        if (not rule.get('minLength', 0) <= len(value) <= rule.get('maxLength', 10000)
                or 'pattern' in rule and not re.search(rule['pattern'], value)
                or any(ord(c) < 32 and c not in '\n\t\r' for c in value)):
            raise WorkspaceError(f'Invalid registry text at {path}')
        if rule.get('format') == 'uri':
            origin(value)
        if rule.get('format') == 'date-time':
            try:
                if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)', value):
                    raise ValueError()
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise WorkspaceError(f'Invalid registry timestamp at {path}') from None
    if type(value) is int and value < rule.get('minimum', value):
        raise WorkspaceError(f'Invalid registry number at {path}')


def version_key(value):
    return tuple(map(int, value.split('.')))


def parse_feed(raw, registry_url=DEFAULT_REGISTRY):
    if len(raw) > FEED_LIMIT:
        raise WorkspaceError('Registry exceeds 5 MiB')
    data = parse_settings(raw.decode('utf-8'))
    schema = json.loads(resource_text('marketplace/registry.schema.json'))
    validate_schema(data, schema, schema)
    seen = set()
    for listing in data['stacks']:
        sid = listing['id']
        if sid in seen:
            raise WorkspaceError('Duplicate stack ID')
        seen.add(sid)
        repo = listing['repository'].removeprefix('https://github.com/').split('/')
        if repo[-1] in ('.', '..') or repo[-1].endswith('.git'):
            raise WorkspaceError('Expected canonical GitHub repository URL')
        if listing['listing_url'] != origin(registry_url) + '/' + sid:
            raise WorkspaceError('Invalid listing URL')
        if listing['github_stars'] is not None and listing['github_stars_fetched_at'] is None:
            raise WorkspaceError('GitHub stars require a fetch timestamp')
        versions = set()
        active = []
        for release in listing['versions']:
            v = release['version']
            if v in versions or release['tag'].removeprefix('v') != v:
                raise WorkspaceError('Duplicate version or release tag mismatch')
            versions.add(v)
            identity = release['manifest_identity']
            if identity['id'] != sid or identity['version'] != v:
                raise WorkspaceError('Release manifest identity mismatch')
            if release['status']['state'] == 'active':
                active.append(v)
            deps = set()
            for dep in release['dependencies']:
                key = (dep['type'], dep['ref'])
                if key in deps or dep['type'] == 'stack' and not stacks.ID.fullmatch(dep['ref']):
                    raise WorkspaceError('Invalid or duplicate prerequisite')
                deps.add(key)
            hook_paths = set()
            for hook in release['hooks']:
                p = stacks.safe_path(hook['path'])
                if p in hook_paths:
                    raise WorkspaceError('Duplicate hook path')
                hook_paths.add(p)
        for status in [listing['status'], *(r['status'] for r in listing['versions'])]:
            if status['state'] != 'active' and not (status['reason'] or '').strip():
                raise WorkspaceError('Non-active status requires a reason')
        latest = max(active, key=version_key) if active and listing['status']['state'] != 'withdrawn' else None
        if listing['latest_version'] != latest:
            raise WorkspaceError('Incorrect latest_version')
        if latest:
            identity = next(r for r in listing['versions'] if r['version'] == latest)['manifest_identity']
            if (listing['summary'], listing['author']['name'], listing['license']) != (identity['description'], identity['author'], identity['license']):
                raise WorkspaceError('Latest listing metadata mismatch')
    return data


def load(registry_url=DEFAULT_REGISTRY):
    return parse_feed(fetch(registry_url, FEED_LIMIT, origin(registry_url)), registry_url)


def search(data, query='', *, category=None, tag=None, author=None, agent=None, browse='new'):
    results = []
    for item in data['stacks']:
        text = ' '.join([item['name'], item['summary'], item['description'], item['author']['name'], *item['tags']])
        latest = next((r for r in item['versions'] if r['version'] == item['latest_version']), None)
        if (query.casefold() not in text.casefold() or category and category not in item['categories']
                or tag and tag not in item['tags'] or author and author != item['author']['id']
                or agent and (not latest or agent not in latest['supported_agents'])
                or browse == 'featured' and item['featured_rank'] is None):
            continue
        results.append(item)
    results.sort(key=lambda i: i['id'])
    if browse == 'new':
        results.sort(key=lambda i: datetime.fromisoformat(i['first_approved_at'].replace('Z', '+00:00')), reverse=True)
    elif browse == 'featured':
        results.sort(key=lambda i: i['featured_rank'])
    else:
        results.sort(key=lambda i: (i['github_stars'] is None, -(i['github_stars'] or 0)))
    return results


def select(data, sid, version=None):
    listing = next((i for i in data['stacks'] if i['id'] == sid), None)
    if listing is None:
        raise WorkspaceError('Unknown marketplace stack ID')
    if listing['status']['state'] == 'withdrawn':
        raise WorkspaceError('Stack withdrawn: ' + listing['status']['reason'])
    version = version or listing['latest_version']
    if version is None:
        raise WorkspaceError('No active release; select a deprecated version explicitly')
    release = next((r for r in listing['versions'] if r['version'] == version), None)
    if release is None:
        raise WorkspaceError('Unknown marketplace version')
    if release['status']['state'] == 'withdrawn':
        raise WorkspaceError('Version withdrawn: ' + release['status']['reason'])
    return listing, release


def unpack(raw, destination):
    """Preflight all entries; extract only after the entire archive is safe."""
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > 12000:
                raise WorkspaceError('Archive entry limit exceeded')
            paths, roots, size = {}, set(), 0
            spellings = {}
            for info in infos:
                name = info.filename[:-1] if info.is_dir() else info.filename
                parts = name.split('/')
                mode = info.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if (info.orig_filename != info.filename or '\\' in name or len(parts) > 20
                        or any(p in ('', '.', '..') or ':' in p for p in parts)
                        or any(ord(c) < 32 for c in name) or info.flag_bits & 1
                        or kind not in (0, stat.S_IFDIR if info.is_dir() else stat.S_IFREG)):
                    raise WorkspaceError('Unsafe archive entry')
                for i in range(1, len(parts) + 1):
                    prefix = '/'.join(parts[:i])
                    normalized = unicodedata.normalize('NFC', prefix).casefold()
                    if spellings.setdefault(normalized, prefix) != prefix:
                        raise WorkspaceError('Normalized archive path collision')
                key = unicodedata.normalize('NFC', name).casefold()
                if key in paths:
                    raise WorkspaceError('Duplicate or normalized archive collision')
                paths[key] = info.is_dir()
                roots.add(parts[0])
                size += info.file_size
                if size > EXPANDED_LIMIT:
                    raise WorkspaceError('Archive expansion exceeds 512 MiB')
            for key in paths:
                parts = key.split('/')
                if any(paths.get('/'.join(parts[:i])) is False for i in range(1, len(parts))):
                    raise WorkspaceError('Archive file/directory collision')
            if len(roots) != 1 or paths.get(next(iter(roots)).casefold() + '/stack.json') is not False:
                raise WorkspaceError('Archive needs one root directory with stack.json')
            total = 0
            for info in infos:
                target = destination / info.filename
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open('xb') as output:
                    while chunk := source.read(65536):
                        total += len(chunk)
                        if total > EXPANDED_LIMIT:
                            raise WorkspaceError('Archive expansion exceeds 512 MiB')
                        output.write(chunk)
            return destination / next(iter(roots))
    except (zipfile.BadZipFile, NotImplementedError, RuntimeError, EOFError, zlib.error) as exc:
        raise WorkspaceError(f'Invalid ZIP archive: {exc}') from exc


@contextmanager
def prepared(listing, release, registry_url, *, local_origin=None):
    print(json.dumps({'listing': listing, 'selected_release': release}, indent=2))
    for status in (listing['status'], release['status']):
        if status['state'] == 'deprecated':
            print('WARNING: deprecated: ' + status['reason'] + '; replacement: ' + str(status['replacement_id']))
    repo = listing['repository'].removeprefix('https://github.com/')
    local_origin = local_archive_origin(local_origin, registry_url)
    archive_url = (f"{local_origin}/registry/local/archives/{listing['id']}/{release['commit']}"
                   if local_origin else f"https://codeload.github.com/{repo}/zip/{release['commit']}")
    raw = fetch(archive_url, ARCHIVE_LIMIT, local_origin or 'https://codeload.github.com')
    if hashlib.sha256(raw).hexdigest() != release['archive_sha256']:
        raise WorkspaceError('Archive SHA256 mismatch')
    with tempfile.TemporaryDirectory(prefix='dryft-stack-') as temp:
        directory = unpack(raw, Path(temp))
        manifest, files, local = stacks.validate(directory)
        if (any(manifest[k] != v for k, v in release['manifest_identity'].items())
                or manifest['hooks'] != release['hooks'] or local['sha256'] != release['content_sha256']):
            raise WorkspaceError('Approved manifest, hooks or content SHA256 mismatch')
        for hook in manifest['hooks']:
            print(f"Executable Python hook: {hook['event']} {hook['path']}\n{files[hook['path']]}")
        provenance = {'kind': 'marketplace', 'registry_origin': origin(registry_url), 'registry_url': registry_url,
                      'repository': listing['repository'], 'release_tag': release['tag'],
                      'commit': release['commit'], 'archive_sha256': release['archive_sha256'],
                      'sha256': local['sha256']}
        if local_origin:
            provenance.update(archive_transport='local-loopback', archive_url=archive_url)
        print(json.dumps({'origin': provenance}, indent=2))
        yield directory, manifest, files, provenance


def prerequisites(entries, release, confirmed):
    installed = {e['id'] for e in entries}
    for dep in release['dependencies']:
        if not dep['required']:
            continue
        key = dep['type'] + ':' + dep['ref']
        if dep['type'] == 'stack' and dep['ref'] not in installed:
            raise WorkspaceError('Missing required stack prerequisite: ' + dep['ref'])
        if (dep['type'] != 'stack' or dep['version_constraint']) and key not in confirmed:
            raise WorkspaceError('Prerequisite availability/version unknown; verify then pass --confirm-prerequisite ' + key)


def install(root, sid, *, version=None, registry_url=DEFAULT_REGISTRY, trust=None, inspect_only=False, confirmed=(), local_origin=None):
    local_origin = local_archive_origin(local_origin, registry_url)
    listing, release = select(load(registry_url), sid, version)
    with prepared(listing, release, registry_url, local_origin=local_origin) as (directory, manifest, files, provenance):
        if inspect_only:
            return sid
        return stacks.install(root, directory, trust, provenance=provenance,
                              prerequisite_release=release, confirmed=confirmed)
