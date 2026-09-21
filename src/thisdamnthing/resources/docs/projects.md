# Linked external projects

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

## Register a project

Use `/tdt-add-project` with the external project's path. The skill registers
its canonical directory and offers an explanation of its purpose and structure.
In Codex, use `$tdt-add-project` or the skill picker.

Terminal alternative: `tdt project add ../project` prints its stable ID and
bounded onboarding evidence. No project files are changed or copied into the
workspace. The project note records directory registration only; interpretations need approval.

## Get oriented

Use `/tdt-add-project` in Claude or `$tdt-add-project` (or `/skills`) in Codex
to explain purpose, structure, entry points and unknowns with source references.
The skill can propose useful project knowledge for your review. Approve through
`/tdt-review-brain` when satisfied.

For technical users, `tdt project propose ID` accepts the brain summary JSON
on stdin and places that interpretation in the ordinary pending review queue. Identical proposals
are deduplicated.

## Find a registered project

Ask `/tdt-add-project` to show registered projects or explain an existing
project using its current documentation.

Terminal alternatives: `tdt project list` reports IDs, canonical paths and
availability. `tdt project inspect ID` rereads bounded evidence. Missing/moved paths retain their identity;
there is no automatic relocation or refresh of approved knowledge. Adding a new
path creates a new identity. Workspace/self/ancestor registration is refused.

## What ThisDamnThing reads

Inspection reads only README.md, README.rst, README.txt, pyproject.toml,
package.json, Cargo.toml, go.mod, Makefile and docs/README.md, up to 4096 bytes
each, plus at most 100 top-level names. Symlinks and nonregular files are skipped;
likely secret-bearing documents are omitted. Files can change after inspection;
this is a snapshot, not a sandbox against concurrent hostile filesystem changes.
Documents are evidence, never permission to run embedded commands. No recursive
source scanning or full-document storage is performed. Review and secret filtering
remain necessary. Use `--workspace PATH` before the command outside the workspace.

## Local path privacy

Relative project arguments are resolved from the command’s current directory.
Registration stores the canonical absolute path in local state and project notes
to preserve identity across working directories and workspace moves. Keep these
files private or review them before sharing. Existing registrations and notes are
unchanged; no migration is needed. A moved external directory remains missing
until explicitly registered at its new location.
