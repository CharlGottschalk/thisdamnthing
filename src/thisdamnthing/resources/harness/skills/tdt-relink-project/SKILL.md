---
name: tdt-relink-project
description: Reconnect a renamed or moved project and update its registration.
---

Use the installed workspace root and read docs/projects.md's lifecycle section.
Accept `<old-project> <new-project>` from the current request. The old project is
its registered ID, path or unambiguous name; the new project is an existing
folder path. If the old project is omitted, run `tdt project list` and ask which
project to relink, including missing and archived entries. If the new path is
omitted, ask for it. Reuse supplied arguments; ask only about missing or ambiguous
values. Never infer a relocation from similar names or a portable project UUID.

Use global `--workspace <root>` and safely quote paths. If request context supplies
a current `brain review-turn <token>` command, run it to suppress duplicate capture;
otherwise report that capture suppression is unavailable and continue authorized work.
Prefer workspace-bound `tdt_project_relink_preview` with the exact registered `id`
and absolute destination `path`; fall back to
`tdt project relink <old-project> <new-project>` to preview. This validates the
new location, refuses collisions, recalculates the path-based ID, updates project
associations and structured source paths, and updates the registration name/path.
Note filenames, wikilinks, other note IDs and historical provenance stay stable.
The source folder must already have moved; this command never moves source files
or rewrites project-local UUIDs, stack artifacts or arbitrary working files.

Inspect the preview. An explicit relink instruction with both unambiguous arguments
authorizes these mechanical updates; do not ask again. Apply the same command with
`--apply --expected-sha256 <proposal_sha256> --user-instruction <actual request or
message reference>`. If stale, preview again and check that the scope still matches
the request. For an interrupted transaction use `tdt stack recover`, then re-preview.

Run `project list`. Prefer workspace-bound `tdt_project_references` with the new
exact `id`, paging both `references` and `skipped`; fall back to
`tdt project references <new-id>` when MCP is unavailable. Read relevant matches to
identify stale prose or work references; historical provenance is expected to
retain old paths. Explain coverage gaps and do not claim all references were
rewritten. If the user wants additional reference edits, use the reviewed cleanup
format in docs/projects.md. Relinking an archived project preserves its archive
state; restore only when requested. Report the new ID/path, preserved brain link,
backup and any references still needing review.
