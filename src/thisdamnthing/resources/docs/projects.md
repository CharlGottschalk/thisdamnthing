# Projects and working files

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

## Register a project

Use `/tdt-add-project` with the external project's path. The skill registers
its canonical directory and offers an explanation of its purpose and structure.
In Codex, use `$tdt-add-project` or the skill picker.

Terminal alternative: `tdt project add ../project` prints its stable ID and
bounded onboarding evidence. No project files are changed or copied into the
workspace. The project note records directory registration only; interpretations need approval.
Its filename combines the project directory name and a short ID suffix, such as
`brain/projects/sites-a31f29c8.md`. Inspection returns its actual `brain_link` for
use in proposals. Full project IDs remain stable and are still used in commands.

## Get oriented

Project-local stack artifacts use `.tdt-project/<stack-id>/`; `.tdt/` is reserved
for installed workspace harnesses and remains refused during registration.
Shared `.tdt-project/project.json` can hold a portable UUID and project name.
Inspection reads it as evidence without writing to the project. That UUID is
separate from the workspace registration ID and does not automatically reconnect
a moved project. There is no legacy project `.tdt/` lookup or migration.

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
path creates a new identity. Workspace/self/ancestor registration and internal locations outside work/ are refused.

## What TDT reads

Inspection reads only README.md, README.rst, README.txt, pyproject.toml,
package.json, Cargo.toml, go.mod, Makefile, docs/README.md and
.tdt-project/project.json, up to 4096 bytes
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
files private or review them before sharing. Existing registrations retain their
identity. Older hash filenames can be migrated using the [brain guide](brain.md).
A moved external directory remains missing
until explicitly registered at its new location.

## Internal work and conventions

`tdt project create studio/autumn-launch` creates and registers
`work/studio/autumn-launch/`. The argument is relative to work/; absolute paths,
dot components and symlinks are refused. Existing files are preserved. `tdt init`
creates a user-editable WORK.md, preserving it on refresh, but no work/ directory.
Edit WORK.md to place new projects under projects/ or studio/, or keep templates
directly in work/. These are agent-interpreted conventions, not executable rules;
the low-level CLI uses the explicit path passed to it.

`tdt project add <existing-path>` registers external directories or directories
below work/, excluding the core stores `work/notes/` and `work/reminders/`
and their descendants. Git is not required. Other workspace areas cannot be projects.
`tdt project inspect autumn-launch` resolves a unique basename; an ID, absolute
registered path or internal relative path disambiguates. IDs remain path-based;
moving directories is not an automatic identity migration.

`tdt work search "interview request"` returns current file paths under work/,
matching all query words in paths or supported text. Search is bounded to 2,000
entries, 50 matches and 32 KiB per text file; hidden paths, symlinks and detected
secrets are excluded. Read matches before using them. External project files are
not globally searched. This is discovery, not approved knowledge retrieval.

When resuming, read project instructions, current artifacts and available progress
records, then related brain notes. Ask what to continue if those are insufficient.
Normal capture still proposes durable knowledge; explicit saves use tdt-capture.
Use exact file sources and the registered project ID to relate decisions to work.
No automatic mirroring, project relocation or fixed progress-file layout occurs.
