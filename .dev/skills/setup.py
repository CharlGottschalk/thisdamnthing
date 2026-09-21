"""Expose the source-only privacy skill in this repository; never globally."""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
bridge = '''---
name: tdt-dev-pii
description: Review staged source and the complete message before authorized ThisDamnThing development commits.
---

Read and follow .dev/skills/tdt-dev-pii/SKILL.md from this repository root.
'''
pending = False
for host in ('.agents', '.claude'):
    target = root / host / 'skills' / 'tdt-dev-pii' / 'SKILL.md'
    if any(p.is_symlink() for p in (target, *target.parents) if p != root.parent):
        raise SystemExit('Refusing symlinked discovery path.')
    if target.exists() and target.read_text() != bridge:
        raise SystemExit('Existing discovery entry differs; preserved.')
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open('x') as stream:
                stream.write(bridge)
        print(host + ': source-only skill bridge ready')
    except OSError:
        pending = True
        print(host + ': unable to write discovery entry; activation pending')

raise SystemExit(1 if pending else 0)
