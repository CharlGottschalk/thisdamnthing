---
name: dryft-dev-pii
description: Review exact staged Dryft source and proposed commit messages for private information before an authorized agent commit, or on direct request.
---

This skill belongs only to this source repository. Resolve the source root from
this canonical `.dev/skills/dryft-dev-pii/SKILL.md`, not the host bridge or shell
cwd. Follow [review.md](review.md) for every invocation. Run its companion
`scripts/review.py` with `--repo` pointing to the intended Git worktree and
`--message-file` pointing to the complete literal proposed message when available.
Use Python 3.11+ and Git. Do not use an installed Dryft workspace as the source.
The repository Git hooks remain separate safeguards; do not bypass them or assume
hook approval supplies the semantic review described here.
