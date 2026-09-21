"""Read-only, bounded staged/message evidence. No approvals or commit execution.

"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

LIMIT = 1024 * 1024
TOTAL = 8 * LIMIT
PATTERNS = {
    'private-key': r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
    'token': r'\b(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}|sk-[A-Za-z0-9_-]{20,})',
    'credential': r'''(?i)\b(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[=:]\s*["']?[^\s"'<>${}]{8,}''',
    'personal-path': r'''(?i)(?:/(?:home|Users|media)/[^/\s"'<>]+|[A-Z]:[\\/]Users[\\/][^\\/\s"'<>]+|\\\\[^\\\s]+\\[^\\\s]+)''',
    'absolute-path-heuristic': r'''(?<![\w:/])/(?!/)[A-Za-z0-9_.-]+/(?:[^\s"'<>]+)|\b[A-Za-z]:[\\/][^\s"'<>]+''',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'phone-heuristic': r'(?<!\w)(?:\+\d[\d ()-]{7,}\d|\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4})\b',
    'identity-heuristic': r'(?i)\b(?:full[_ -]?name|first[_ -]?name|last[_ -]?name|user[_ -]?id|account[_ -]?id|employee[_ -]?id|customer[_ -]?id|organization|company|address)\s*[:=]\s*\S+',
    'address-heuristic': r'(?i)\b\d{1,6}\s+(?:[A-Za-z]+\s+){1,4}(?:street|road|avenue|lane|drive|boulevard|st|rd|ave)\b',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args, limit=4 * LIMIT, optional=False):
    # Spool output privately, never forward Git stderr (paths may be private).
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(['git', '-C', str(repo), *args], stdout=output,
                                stderr=subprocess.DEVNULL, timeout=20)
        if result.returncode:
            if optional:
                return b''
            raise ValueError('Git inspection failed')
        output.seek(0)
        data = output.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Git metadata/read limit exceeded')
        return data


def decode(data):
    if b'\0' in data or data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        return None
    try:
        return data.decode('utf-8')
    except UnicodeError:
        return None


def scan(data, ref, location, existing, binding):
    findings = []
    for number, line in enumerate(data.splitlines(), 1):
        for category, pattern in PATTERNS.items():
            if re.search(pattern, line):
                # Entire excerpt is masked; surrounding text may hold another secret.
                item = {'ref': ref, 'location': location, 'line': number,
                        'category': category, 'exposure': 'existing-context' if line in existing else 'new',
                        'excerpt': '[redacted]'}
                item['id'] = sha(binding + json.dumps(item, sort_keys=True).encode())
                findings.append(item)
    return findings


def review(repo, message):
    root = git(repo, 'rev-parse', '--show-toplevel').rstrip(b'\n')
    index_path = git(repo, 'rev-parse', '--git-path', 'index').rstrip(b'\n')
    before = git(repo, 'ls-files', '--stage', '-z')
    head = git(repo, 'rev-parse', '--verify', 'HEAD', optional=True)
    changes = git(repo, 'diff', '--cached', '--raw', '--no-abbrev', '-z', '-M', '-C',
                  '--no-ext-diff', '--no-textconv').split(b'\0')
    gaps, findings, coverage = [], [], []
    if any(record.split(b'\t', 1)[0].split()[-1:] != [b'0'] for record in before.split(b'\0') if record):
        gaps.append('unmerged index')
    message_data = None
    if message is None:
        gaps.append('complete proposed message pending')
    else:
        with Path(message).open('rb') as stream:
            message_data = stream.read(LIMIT + 1)
        if len(message_data) > LIMIT:
            gaps.append('message exceeds 1 MiB')
            message_data = None
    binding = root + b'\0' + index_path + b'\0' + head + before
    snapshot = sha(binding + b'\0message\0' + (message_data if message_data is not None else b'PENDING'))
    budget = TOTAL

    def blob(oid, mode):
        nonlocal budget
        if mode not in (b'100644', b'100755', b'120000'):
            return None
        size = int(git(repo, 'cat-file', '-s', oid.decode()))
        if size > LIMIT or size > budget:
            return None
        budget -= size
        return decode(git(repo, 'cat-file', 'blob', oid.decode(), limit=LIMIT))

    pos = 0
    while pos < len(changes) and changes[pos]:
        header = changes[pos].split(); pos += 1
        old_mode, mode, old_oid, oid, status = header
        old_mode = old_mode.lstrip(b':')
        path = changes[pos]; pos += 1
        old_path = path
        if status[:1] in (b'R', b'C'):
            path = changes[pos]; pos += 1
        ref = sha(path)[:12]
        file_binding = path + b'\0' + oid
        findings.extend(scan(os.fsdecode(path), ref, 'path', {os.fsdecode(old_path)} if old_mode != b'000000' else set(), file_binding))
        if status == b'D':
            coverage.append({'ref': ref, 'content': 'deleted; path only'})
            continue
        previous = ''
        if old_mode != b'000000':
            previous = blob(old_oid, old_mode)
            if previous is None:
                gaps.append(ref + ': prior version uninspected; exposure uncertain')
        content = blob(oid, mode)
        if content is None:
            gaps.append(ref + ': binary/non-UTF-8/large/LFS/submodule or total budget exceeded')
            coverage.append({'ref': ref, 'content': 'uninspected'})
            continue
        coverage.append({'ref': ref, 'content': 'full staged UTF-8', 'lines': len(content.splitlines())})
        findings.extend(scan(content, ref, 'file', set((previous or '').splitlines()), file_binding))
    if message_data is not None:
        content = decode(message_data)
        if content is None:
            gaps.append('message is binary/non-UTF-8/LFS')
        elif not content.strip():
            gaps.append('proposed message is empty')
        else:
            findings.extend(scan(content, 'message', 'message', set(), message_data))
            coverage.append({'ref': 'message', 'content': 'complete subject/body/trailers', 'lines': len(content.splitlines())})
    if before != git(repo, 'ls-files', '--stage', '-z') or head != git(repo, 'rev-parse', '--verify', 'HEAD', optional=True):
        gaps.append('index or HEAD changed during review')
    if message_data is not None:
        with Path(message).open('rb') as stream:
            if stream.read(LIMIT + 1) != message_data:
                gaps.append('message changed during review')
    return {'status': 'incomplete' if gaps else 'findings' if findings else 'pass',
            'scope': 'bounded pattern evidence; semantic review still required',
            'snapshot': snapshot, 'coverage': coverage, 'findings': findings, 'gaps': gaps,
            'limits': '1 MiB/blob/message; 8 MiB combined old/new blobs; 4 MiB metadata; 20s/Git command. No history/release review. Patterns cannot prove absence of PII.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--message-file')
    args = parser.parse_args()
    try:
        report = review(args.repo, args.message_file)
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        report = {'status': 'incomplete', 'gaps': ['Unable to inspect Git state or message within bounds; no raw diagnostics emitted.']}
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return {'pass': 0, 'findings': 1, 'incomplete': 2}[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
