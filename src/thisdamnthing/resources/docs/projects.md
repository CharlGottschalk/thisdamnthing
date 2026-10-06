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
use in proposals. Full project IDs are used in commands and remain stable until an explicit relink.

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
there is no automatic relocation or refresh of approved knowledge. Use
`/tdt-relink-project` to reconnect a moved directory. Workspace/self/ancestor registration and internal locations outside work/ are refused.

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
until explicitly relinked to its new location.

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
Use the lifecycle skills below for explicit registration changes.


## Project lifecycle

Use `/tdt-relink-project <old-project> <new-project>` after renaming or moving a
project directory. Supply its old registered name, path or ID, followed by its
new directory path. If either is missing, the skill asks for it; ambiguous names
also need a choice. Missing and archived projects can be selected. The new folder
must exist and must not belong to another registration.

Relinking updates the registered path and its hash-derived ID, the project note's
title, note metadata that refers to the old project ID, and structured source
paths below the old directory. Note filenames and wikilinks stay stable, including
any old hash suffix in a filename. Other note IDs, provenance and review history
stay intact. The registration note records its earlier path and ID. Relinking
does not move source files or change project-local UUIDs or stack artifacts.
Prose and working files may still contain old references; the skill reports
these for review. An archived project remains archived after relinking.

Use `/tdt-remove-project` to archive or permanently unregister a project. The
skill asks which mode when your request does not specify one. Archiving marks
the registration and its note, and blocks ordinary inspect/resume operations.
The project remains visible in `project list`; its knowledge remains searchable.
Ask the same skill to restore it when needed. Restoration also works when the
folder is missing, so it can be relinked afterward.

Permanent removal deletes the registry entry and marks the retained project note
as removed. It leaves project source, brain notes and working files in place.
Project-associated notes no longer appear in normal brain search once their
registration is gone. They remain on disk for a separate review and cleanup.
Reusing a permanently removed path through `project add` requires resolving the
retained registration note conflict first.

### Terminal workflow

These commands preview changes without writing:

```sh
tdt project relink OLD_PROJECT NEW_PATH
tdt project remove PROJECT
tdt project remove PROJECT --permanent
tdt project restore PROJECT
```

Inspect the returned replacements and repeat the selected command with
`--apply --expected-sha256 HASH --user-instruction "your instruction"`, using its
`proposal_sha256`. The supplied instruction records authorization; a hash does
not authorize an action by itself. An explicit relink with both arguments or a
removal with a chosen mode already authorizes those mechanical changes. If a
file has changed since preview, preview again. Backups under
`.tdt/state/project-operations/` record before/after content and the instruction.
Lifecycle outcomes are retained by proposal hash. After an uncertain response,
read `tdt project operation-status HASH` before retrying or switching transport.
`completed` records historical success, even if the project later changes;
identical completed retries return that result without writing. Keep the original
project argument, destination/mode and instruction for retries, including after
relink or unregister. Different inputs or instruction for a retained hash refuse.
`prepared` means a backup exists without committed completion; inspect before retry.
`unknown` means no indexed record, not proof the operation never ran. Legacy UUID
backups are not indexed. `recovery_required` overrides a
retained result while either shared transaction journal exists; use the indicated
`tdt stack recover` or `tdt skill recover`, then reread. Completion and lifecycle
changes share the journal, and rollback restores the prepared backup.

Both MCP profiles provide lifecycle previews and `tdt_project_operation_status`.
Everyday also offers `tdt_project_remove_apply`, `tdt_project_restore_apply` and
`tdt_project_relink_apply` with identical preview inputs, `expected_sha256` and
`user_instruction`. Receipts include the resulting `project_id`, operation, hash
and backup path. This is historical state; read current registration separately.
MCP project arguments are exact IDs and relink destinations are absolute paths.
Everyday also exposes hash-bound reference cleanup apply. Indexed lifecycle backups are bounded to
8 MiB; oversized operations refuse before writing.

### Review and clean references

When you request reference review, the skill runs `tdt project references ID`.
After permanent removal, use the full old ID while its registration note is
retained. After relinking, use the new ID; the scan also checks previous IDs and
paths recorded in relocation history.

The scan reports literal matches in supported text under brain/ and work/,
including candidates and scratchpad notes. It examines at most 5,000 entries and
256 KiB per file, skips hidden paths, symlinks, unsupported files and detected
secrets, and reports omissions. It does not scan external source directories.
Matches need interpretation: a shared name or a historical source is not a reason
to delete content. The scan cannot prove that every reference has been found.

Cleanup is separate from removing the registration. For specific approved edits,
pass this JSON shape to `tdt project cleanup ID` on stdin:

```json
{
  "changes": [
    {
      "path": "work/planning.md",
      "expected_sha256": "hash from the reference scan",
      "content": "Complete reviewed replacement text\n"
    }
  ]
}
```

Use `content: null` only for an explicitly approved whole-file deletion. Each
batch accepts 1–20 files from the current reference scan. Retained brain/core
notes must preserve metadata other than project, sources and links; remove only
the approved references from their bodies. Edit retained reminders through the
reminder commands so their delivery state stays consistent. Shared notes and project source files
need particular care because they may contain unrelated work. Preview the edits,
then apply the same JSON with the preview hash and instruction flags described
above. Cleanup does not recursively delete directories.

Keep the removed registration note until the final cleanup batch so later scans
can still resolve its ID. Before deleting a note, review and repair incoming links.
Operation backups retain old content and paths after cleanup; this is recoverable
editing, not secure erasure. Backup deletion is never implied by project removal.


Both MCP profiles expose `tdt_project_cleanup_preview` with an exact project ID
and 1–20 changes (`path`, current `expected_sha256`, complete `content`, or
explicit null for whole-file deletion). It uses the shared CLI cleanup validation
and returns complete replacements, proposal hash and scan coverage without writes
or backups. Preview reads share the workspace lock; applies remain exclusive.
Output budgets allow up to 1 MiB and refuse oversized results without partial
review content. Everyday exposes `tdt_project_cleanup_apply` with identical `id` and `changes`,
`expected_sha256` from the preview and the actual `user_instruction`; the CLI accepts
the same proposal and hash. Apply only separately authorized changes. Cleanup now
retains prepared/completed outcomes through the shared transaction, including
whole-file deletions. Read `tdt_project_operation_status` after uncertainty before
retry or CLI fallback. Identical completed retries return historical success even
after deleting the removed registration note, preserving later file edits.
Changed inputs/instruction refuse; old UUID backups remain unindexed. Backups are
bounded to 8 MiB before writes.
