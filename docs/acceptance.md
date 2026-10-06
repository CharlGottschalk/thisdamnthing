# Manual component verification

Use focused manual checks for the behavior being changed. Create disposable
workspaces and harmless fixtures outside source repositories and personal
workspaces. ThisDamnThing development does not use an automated test suite.

Choose relevant checks below. For a complete installed-product workflow, use the
[workspace runbook](e2e-runbook.md). This page defines checks; keep execution logs,
results and local paths in development records outside these guides.

| Area | Procedure and expected behavior |
| --- | --- |
| Packaging | Build and install a wheel. Check version/help and packaged resources; exclude development files and optional stack source. |
| Initialization | Create a path with spaces, inspect the brain and harness, run doctor and verify empty stack/project lists. |
| Preservation | Add unrelated files/settings and repeat setup. Compare hashes; edited owned resources must be preserved through refusal. |
| Agent selection | Exercise none, each host, both, enable, disable and re-enable. Check saved selection and ownership across core, stack and user skills. |
| Host adapters | In fresh sessions, check discovery, invocation and startup/request/Stop hook delivery separately. |
| Capture | Discuss harmless decisions, observe pending summaries, replay an event and recover an incomplete request without duplicate knowledge. |
| Review | Approve, edit and reject candidates. Check stale-content refusal and exclusion of pending/rejected content from every retrieval hop. |
| Retrieval | Query literal, linked, missing and conflicting evidence. Inspect citations and confirm unsupported answers acknowledge the gap. |
| Projects | Register and inspect scratch source. Confirm stable identity and unchanged external files; report missing paths without relinking. |
| UI | Submit grouped and custom browser answers, handle a follow-up, retry an event and check retained answers after restart. |
| User skills | Propose, refine, approve and decline. Check overlaps, stale versions, batch conflicts, recovery and fresh-session discovery. |
| History discovery | Use bounded native records with trustworthy completion evidence. Check workspace scope, duplicates and unavailable/partial coverage. |
| Workspace policy | Review and save rules, update by revision, check missing-policy failure and actual current-policy delivery. |
| Stack lifecycle | Validate, inspect, install, approve an update and uninstall. Confirm exact trust, ownership refusal, recovery and preserved brain/user files. |
| Stack docs | Check empty catalog, declared guides, version changes, escaped paths, refusal on edits and rebuild behavior. |
| Capabilities | Index/query an approved corpus; probe stale IDs, altered assets, incompatible runtimes, malformed output and interruption. |
| Registry | Check real TLS, digests, archive safety, prerequisites and withdrawn/absent selection refusal. Separate local and public transport. |
| Optional workflows | Generate/use a stack or run a small software workflow. Check generated artifacts and preservation after removal. |
| Privacy review | Review exact staged bytes and full message with synthetic findings, partial staging and incomplete binary coverage. |

## Inspect failure paths

Snapshot files before a mutating command, including unrelated configuration and
brain notes. For ownership conflicts or invalid input, compare the complete relevant
inventory after refusal. For interrupted operations, exercise the documented
recovery command and preserve unexpected edits instead of forcing cleanup.

Use explicit fixture approval only for harmless fixture content. Do not apply a
fixture decision to real user knowledge, executable content or project work.

## Report what the check establishes

Identify the source revision, artifact hash, interpreter/platform and host surface
in private verification records. Record the command, observed output and resulting
file state. Distinguish generated configuration, direct wrapper execution and
actual host delivery. Distinguish a local registry fixture from a public download.

An unavailable prerequisite leaves that check unverified. Report it plainly and
limit feature or platform claims to the behavior actually checked.

## Obsidian-style brain front matter (manual regression)

In a disposable workspace initialized with `tdt init <directory> --agent none`:

1. Create and register two directories below `work/`. Keep one project note's
   front matter as a JSON-shaped YAML flow mapping. Rewrite the other's YAML header,
   preserving its full ID, project ID, status and timestamps. Use `links` and
   `sources` block lists, a `provenance` map, and a `review` list of maps. Include
   a quoted value containing a colon and an unquoted numeric-looking string.
2. Run `tdt project inspect <name>` for both projects and `tdt brain search
   <title>`. Check that the YAML note retains its brain link and appears in search.
3. Add `brain/projects/broken.md` with an unterminated front-matter list. Repeat
   both inspections and search. Each command should succeed, print a warning
   naming `brain/projects/broken.md` on stderr, and retain valid results.
4. Check candidate and scratchpad listings with valid YAML and malformed neighbors.
   Direct reads of malformed notes must raise an error naming the relative file.
5. Confirm a YAML write/read round trip preserves nested review history and the
   body. Confirm unsafe symlinks still stop scans, and filename migration refuses
   malformed notes. No command should rewrite the skipped file.

Also check multiline values, inline maps, duplicate-key refusal and alias refusal.
This verifies YAML parsing, not a live Obsidian/plugin session.

### YAML writes and reminder lifecycle

- Save a note containing numeric-looking IDs, date/boolean-looking strings,
  Unicode, empty strings, nulls, multiline text and nested review history. Confirm
  strings are quoted, field order is stable and a write/read/write cycle is identical.
- Edit and approve a candidate; confirm the saved YAML retains previous review
  history. Check project registration and scratchpad save/search too.
- Create a due reminder, claim it, acknowledge it, edit it with the current
  revision and mark it done. Check that both revision fields are integers and
  acknowledged reminders are not delivered again. Repeat an edit from a YAML flow-mapping
  header and confirm it saves as YAML. Settings and CLI payloads stay JSON.
- Migrate a hash-named YAML note: preview writes nothing; apply writes YAML for
  changed notes, preserves unrelated files and body/history, and is idempotent.

- Verify block and JSON-shaped flow mappings use identical scalar typing and
  duplicate-key checks; no JSON-specific parsing path remains.

## Notes and reminders under work

In a disposable workspace initialized with both hosts, confirm `work/` is absent
until needed and doctor succeeds. Save a scratchpad and reminder; confirm their
paths are under `work/notes/` and `work/reminders/`, with no corresponding brain
folders. Check scratchpad search, shared tags, duplicate saves and links using
`work/notes/<filename>`; default knowledge search must exclude both stores.
Exercise reminder claim/acknowledgement and confirm no repeat delivery. Refresh
the workspace and compare store bytes. Preview/apply a scratchpad hash-filename
rename and check current links and repeat idempotence. Refuse symlink/file store
conflicts and project creation/registration in either reserved store.


## Brain maintenance

In a disposable workspace, run `tdt brain audit` on an empty brain; code examples
in the default index must not become broken-link findings. Add notes with a broken
link, duplicate ID, matching titles, missing sources, malformed metadata and a
cluster unreachable from the index. Confirm separate findings and visible scan
limits. Candidate and scratchpad contents remain outside semantic brain review.

Preview a small `tdt brain repair` batch and verify no note bytes change. Apply
with the displayed proposal hash and explicit approval reference, then inspect the
backup and confirm identity, sources, provenance and prior review history survive.
Rescan to confirm repaired links and index reachability. Refuse stale source or
proposal hashes, missing targets, path escapes, symlinks and non-approved notes.
Simulate an interrupted shared transaction and run `tdt stack recover`; confirm
original bytes are restored. Install and refresh both host skill bridges and
check brain-router discovery. Semantic review quality and live host execution
require a separate real conversation; structural checks do not establish them.


## Project lifecycle (manual)

Use disposable workspaces and external directories; never a personal workspace.

1. Initialize both hosts; confirm both new skills, their explicit entry points,
   workspace router and docs install. Refresh and run doctor.
2. Register a project, add associated candidate/knowledge/scratchpad notes and a
   working file mentioning it. Move/rename its directory. Preview and apply relink;
   confirm the new path hash, title, metadata associations and source prefixes,
   stable filenames/wikilinks, preserved provenance/review and unchanged source.
3. Refuse destination collisions, invalid destinations, ambiguous old names,
   changed preview hashes and symlinks in managed note paths without partial writes.
4. Archive a project; confirm list marks it archived, inspect/resume refuses it,
   knowledge remains available and files survive. Relink an archived project and
   restore it, including while its directory is missing.
5. Permanently unregister; confirm registry absence, retained removed project note,
   preserved files and reference scan by full ID. Preview selected cleanup edits
   and explicit deletions; confirm stale file hashes refuse changes, unrelated
   content survives and retained note provenance cannot be rewritten.
6. Check reference scan omissions for unsupported/oversized/hidden files, symlinks
   and possible secrets. Check project source is never deleted by removal.
7. Interrupt a multi-file lifecycle write and run shared recovery. Confirm exact
   rollback and backups; confirm recovery refuses intervening edits.
8. Exercise skill conversations with neither relink argument, only one argument,
   both unambiguous arguments, ambiguous names and removal with no chosen mode.
   Ask only for missing choices; never infer relocation or cleanup authority.
