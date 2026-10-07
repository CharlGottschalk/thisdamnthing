---
name: tdt-remove-stack
description: Uninstall stacks; preserve user knowledge and work.
---

Read docs/stacks.md. Resolve the installed ID from the request and `tdt stack
list` (or MCP `tdt_stack_list`); ask only for an ambiguous target.
When available, use `tdt_stack_remove_preview` for the exact ID and read complete
before/after changes, including cache and derived catalog changes. Increase the
result budget if needed; an oversized/refused preview is not partial review. Its
hash identifies the preview only and is not a CLI approval token. Show its owned files and explain that
brain notes/candidates, workspace-created skills, linked projects and generated
user artifacts remain. An explicit uninstall/remove request authorizes this scope;
do not ask for a second confirmation. Inspection alone does not authorize removal.

Run `tdt stack uninstall ID` (the same operation as `stack remove ID`). On
missing/edited owned assets or untracked additions, report exact blockers. Preserve
edits/additions elsewhere and restore originals only within user authorization;
never discard them or force-delete the bundle. Retry after resolution. A pending
transaction requires `tdt stack recover`; preserve recovery conflicts for review.

Verify absence from `tdt stack list`, stack docs and the displayed owned paths.
No independent per-stack provider hook registrations exist: the core dispatcher
uses installed/trust records, removed in the same transaction. Shared core hooks
remain. Report already-uninstalled clearly; do not claim a new removal occurred.
Restart running hosts to clear previously loaded skill context. Removing user
knowledge or project artifacts is a separate operation outside this scope.
