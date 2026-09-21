# Making a change

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

## Choose a small outcome

Read the [development entry point](README.md) and the relevant runtime contract.
Describe what should behave differently and how you will check it. Keep the scope
small enough to review and verify without unrelated changes.

Create a branch from the agreed base. If that checkout has unrelated edits,
use a separate worktree from the base revision so they stay untouched:

```sh
git worktree add -b my-change .../tdt-my-change master
cd .../tdt-my-change
```

## Work and check

Keep product code and installed resources in `src/`; keep development helpers
in `.dev/`. Follow direct functions and plain files where practical. Change the
user guide alongside a behavior change, and update contracts when a shared
format changes. See [architecture](architecture.md) for where to look.

Run the CLI from source without an installation:

```sh
PYTHONPATH=src python3 -m thisdamnthing --help
PYTHONPATH=src python3 -m thisdamnthing init ../disposable-workspace --agent none
PYTHONPATH=src python3 -m thisdamnthing --workspace ../disposable-workspace doctor
```

Use a new directory outside the checkout and existing projects. Check the
specific behavior you changed, plus preservation and refusal paths when writes
are involved. Use harmless fixtures. For agent changes, run a real session in
an installed disposable workspace: generated files or direct hook output do
not prove discovery, invocation or live hook delivery. For docs-only changes,
check links, command syntax and readability. No automated tests are used.

## Finish and hand off

Record actual checks, results and gaps in the review description. Keep private
paths, logs and identity in ignored `.dev/local/`. Update user-facing feature
claims only when supported by verification. Development coordination belongs in
the repository's `.dev/` records, outside the how-to guides.

A request to edit files does not authorize staging, committing or pushing.
Before an authorized agent commit, run the repository's
[privacy skill](../.dev/skills/tdt-dev-pii/SKILL.md) against the exact staged
snapshot and complete message. Findings or incomplete review pause the commit.
See [setup](development.md) for Git safeguards and message format.

Give reviewers the problem, resulting behavior and focused verification. If
pausing, say what remains and how to resume; do not mark incomplete work done.
