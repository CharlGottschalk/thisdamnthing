"""Activate tracked hooks for this clone, preserving any existing hook setup."""
import os
from pathlib import Path
import subprocess
import sys

HOOKS = ('pre-commit', 'pre-merge-commit', 'commit-msg', 'pre-push')
ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)


def main():
    if sys.argv[1:] not in ([], ['--check']):
        raise ValueError('Usage: python3 .dev/git-hooks/setup.py [--check]')
    if git('rev-parse', '--show-toplevel').stdout.strip() != str(ROOT):
        raise ValueError('Run this setup from a Dryft source checkout.')
    current = git('config', '--get', 'core.hooksPath')
    if current.returncode not in (0, 1):
        raise ValueError('Unable to inspect Git hook configuration.')
    configured = current.stdout.strip()
    if configured and configured != '.dev/git-hooks':
        raise ValueError('Existing custom hooksPath preserved; integrate hooks explicitly before activation.')
    for name in HOOKS:
        path = ROOT / '.dev/git-hooks' / name
        if not path.is_file() or (os.name != 'nt' and not os.access(path, os.X_OK)):
            raise ValueError('Hook missing/not executable; restore tracked hook files.')
    if sys.argv[1:] == ['--check']:
        if configured != '.dev/git-hooks':
            raise ValueError('Tracked Git hooks are not active. Run this command without --check.')
        print('Tracked Git hooks are active for this clone.')
        return
    if not configured:
        raw = git('rev-parse', '--git-path', 'hooks').stdout.strip()
        directory = Path(raw) if Path(raw).is_absolute() else ROOT / raw
        if directory.exists() and any(p.is_file() and not p.name.endswith('.sample') for p in directory.iterdir()):
            raise ValueError('Existing Git hooks preserved; integrate them explicitly before activation.')
    result = git('config', '--local', 'core.hooksPath', '.dev/git-hooks')
    if result.returncode:
        raise ValueError('Cannot save repository-local hooksPath.')
    print('Activated tracked Git hooks for this clone only.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print('Dryft hook setup: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
