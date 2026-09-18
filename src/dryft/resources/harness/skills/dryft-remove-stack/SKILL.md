---
name: dryft-remove-stack
description: Uninstall an explicitly selected stack and its owned runtime assets while preserving user knowledge and work.
---

Read docs/stacks.md. Resolve the installed ID from the request and `dryft stack
list`; ask only for an ambiguous target. Show its owned files and explain that
brain notes/candidates, workspace-created skills, linked projects and generated
user artifacts remain. An explicit uninstall/remove request authorizes this scope;
do not ask for a second confirmation. Inspection alone does not authorize removal.

Run `dryft stack uninstall ID` (the same operation as `stack remove ID`). On
missing/edited owned assets or untracked additions, report exact blockers. Preserve
edits/additions elsewhere and restore originals only within user authorization;
never discard them or force-delete the bundle. Retry after resolution. A pending
transaction requires `dryft stack recover`; preserve recovery conflicts for review.

Verify absence from `dryft stack list`, stack docs and the displayed owned paths.
No independent per-stack provider hook registrations exist: the core dispatcher
uses installed/trust records, removed in the same transaction. Shared core hooks
remain. Report already-uninstalled clearly; do not claim a new removal occurred.
Restart running hosts to clear previously loaded skill context. Removing user
knowledge or project artifacts is a separate operation outside this scope.
