"""Local Git safeguards. No dependencies, network calls, or index mutations."""
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
LIMIT = 1024 * 1024


def git(*args, check=True):
    return subprocess.run(['git', *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=check)


def text(*args):
    return git(*args).stdout.decode('utf-8').strip()


def branch_guard(policy):
    result = git('symbolic-ref', '--quiet', '--short', 'HEAD', check=False)
    if result.returncode or any(fnmatch.fnmatchcase(result.stdout.decode().strip(), p)
                                for p in policy['protected_branches']):
        raise ValueError('Create/switch to a working branch before committing: git switch -c <branch>')


def approval_file():
    return Path(text('rev-parse', '--show-toplevel')) / '.dev/local/git-privacy-approvals.json'


def approved(kind, name, data):
    path = approval_file()
    records = json.loads(path.read_text()) if path.exists() else []
    return {'kind': kind, 'name': name, 'sha256': hashlib.sha256(data).hexdigest()} in records


PATTERNS = {
    'private-key': r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
    'token': r'\b(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}|sk-[A-Za-z0-9_-]{20,})',
    'credential': r'''(?i)\b(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[=:]\s*["']?[^\s"'<>${}]{8,}''',
    'personal-path': r'''(?i)(?:/(?:home|Users|media)/[^/\s"'<>]+|[A-Z]:[\\/]Users[\\/][^\\/\s"'<>]+|\\\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_$.-]+)''',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'phone': r'(?<!\w)\+\d[\d ()-]{7,}\d\b',
}
PLACEHOLDERS = {'user', 'username', 'name', 'you', 'example', 'example-user'}


def scan(kind, name, data, mode=None):
    if approved(kind, name, data):
        print('Privacy: using a local approval for unchanged content.', file=sys.stderr)
        return []
    location = kind + ' ' + hashlib.sha256(name.encode()).hexdigest()[:12]
    if mode == '160000' or len(data) > LIMIT or b'\0' in data or data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        return [f'{location}: incomplete privacy coverage (binary, large file, LFS or submodule); review explicitly']
    try:
        content = data.decode('utf-8')
    except UnicodeError:
        return [f'{location}: incomplete privacy coverage (non-UTF-8 content); review explicitly']
    findings = []
    # Scan staged names as well, but never echo a potentially sensitive filename.
    lines = content.splitlines()
    if kind == 'file':
        lines = [name, *lines]
    for number, line in enumerate(lines, 0 if kind == 'file' else 1):
        for category, pattern in PATTERNS.items():
            for match in re.finditer(pattern, line):
                value = match.group()
                if category == 'email':
                    domain = value.rsplit('@', 1)[1].lower()
                    if domain in {'example.com', 'example.org', 'example.net', 'users.noreply.github.com'}:
                        continue
                if category == 'personal-path' and re.split(r'[\\/]', value)[-1].lower() in PLACEHOLDERS:
                    continue
                # Identify the file by a path digest, not by leaking personal filenames.
                ref = hashlib.sha256(name.encode()).hexdigest()[:12]
                findings.append(f'{kind} {ref}, line {number}: {category} [redacted]')
                break
    return findings


def staged():
    paths = git('diff', '--cached', '--name-only', '--diff-filter=ACMRT', '-z', '--no-ext-diff', '--no-textconv').stdout.split(b'\0')
    entries = {}
    for record in git('ls-files', '--stage', '-z').stdout.split(b'\0'):
        if record:
            header, path = record.split(b'\t', 1)
            mode, oid, stage = header.split()
            if stage == b'0':
                entries[path] = (mode.decode(), oid.decode())
    for raw in paths:
        if not raw:
            continue
        name = os.fsdecode(raw)
        mode, oid = entries[raw]
        size = int(text('cat-file', '-s', oid)) if mode != '160000' else LIMIT + 1
        data = git('cat-file', 'blob', oid).stdout if size <= LIMIT else oid.encode()
        yield name, mode, data, size


def staged_guard():
    findings = []
    for name, mode, data, size in staged():
        # Sensitive private files must never be staged accidentally.
        if name == '.dev/developer.json' or name.startswith('.dev/local/') or name == '.env':
            findings.append('Private configuration/log file is staged; unstage it before committing.')
        elif size > LIMIT:
            if not approved('file', name, data):
                findings.append('Incomplete privacy coverage for large blob/submodule; review explicitly.')
        else:
            findings.extend(scan('file', name, data, mode))
    reject(findings)


def reject(findings):
    if findings:
        print('\n'.join(dict.fromkeys(findings)), file=sys.stderr)
        raise ValueError('Privacy review required. Values are redacted; see docs/development.md for scoped approvals.')


def message_guard(path, policy):
    data = Path(path).read_bytes()
    reject(scan('message', 'commit-message', data))
    content = data.decode('utf-8')
    comment = git('config', '--get', 'core.commentChar', check=False).stdout.decode().strip() or '#'
    # Git's final cleanup may differ; checking raw content above is conservative.
    lines = [line.rstrip() for line in content.splitlines() if not line.startswith(comment)]
    while lines and not lines[0].strip():
        lines.pop(0)
    subject = lines[0] if lines else ''
    types = '|'.join(re.escape(t) for t in policy['commit_types'])
    if not re.fullmatch(r'(?:' + types + r')(?:\([^()\r\n]+\))?!?: \S.*', subject):
        raise ValueError('Use a Conventional Commit: type(scope): description (e.g. feat(cli): add workspace setup)')
    if len(lines) > 1 and lines[1]:
        raise ValueError('Separate the commit subject and body with a blank line.')


def push_guard(policy):
    for line in sys.stdin:
        fields = line.split()
        if len(fields) != 4:
            raise ValueError('Cannot inspect malformed push ref input.')
        destination = fields[2]
        if destination.startswith('refs/heads/') and any(fnmatch.fnmatchcase(destination[11:], p)
                                                       for p in policy['protected_branches']):
            raise ValueError('Push to a protected destination branch refused. Push a working branch and open a pull request.')


def approve(kind, target):
    if kind == 'file':
        matches = [(data, size) for name, mode, data, size in staged() if name == target]
        if not matches:
            raise ValueError('Path is not a staged added/changed file.')
        data = matches[0][0]
        name = target
    else:
        data, name = Path(target).read_bytes(), 'commit-message'
    if not sys.stdin.isatty():
        raise ValueError('A scoped privacy exception requires interactive review.')
    print('Only approve after reviewing this exact staged content/message. Type APPROVE: ', end='', flush=True)
    if input() != 'APPROVE':
        raise ValueError('Approval cancelled.')
    path = approval_file()
    records = json.loads(path.read_text()) if path.exists() else []
    record = {'kind': kind, 'name': name, 'sha256': hashlib.sha256(data).hexdigest()}
    if record not in records:
        records.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + '\n')
    print('Local approval recorded for exact content; edits require a new review.')


def main():
    try:
        policy = json.loads((BASE / 'policy.json').read_text())
        action = sys.argv[1]
        if action in ('pre-commit', 'pre-merge-commit'):
            branch_guard(policy)
            staged_guard()
        elif action == 'commit-msg':
            branch_guard(policy)
            staged_guard()  # Recheck in case another hook changed the index.
            message_guard(sys.argv[2], policy)
        elif action == 'pre-push':
            push_guard(policy)
        elif action == 'scan':
            staged_guard()
        elif action in ('approve-file', 'approve-message'):
            approve('file' if action == 'approve-file' else 'message', sys.argv[2])
        else:
            raise ValueError('Unknown hook action.')
        return 0
    except (ValueError, OSError, KeyError, IndexError, subprocess.CalledProcessError) as exc:
        # Never print Git stderr or raw exception values that may contain secrets.
        message = str(exc) if type(exc) is ValueError else 'Unable to complete Git safeguards; check configuration and Git state.'
        print('Dryft Git: ' + message, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
