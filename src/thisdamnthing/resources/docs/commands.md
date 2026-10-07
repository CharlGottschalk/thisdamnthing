# CLI command reference

Use the related skill below for guided work in chat. Names use Claude's `/`
syntax; in Codex use `$` or the skill picker. The CLI column is a secondary
reference for technical users. “Ask your agent” means there is no dedicated skill
for that operation. Skills run the same commands and preserve their review and
trust requirements.

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Run commands from your workspace or a subdirectory. From elsewhere, put
`tdt --workspace "."` before the command. Use `tdt --help`
and `tdt COMMAND --help` for options; nested commands also accept `--help`.
Paths with spaces need shell quotes. Replace example IDs and hashes with actual
values returned by inspection; a placeholder is never approval.

| Skill or chat request | CLI command | Purpose |
| --- | --- | --- |
| Ask your agent to initialize or refresh setup | `tdt init [PATH] --agent both` | Initialize or refresh unchanged owned core files; omit PATH for the current directory. Select `claude`, `codex`, `both` or `none`. |
| `/tdt-workspace` | `tdt doctor` | Check local layout, ownership and recovery state. |
| Ask your agent to enable or disable an integration | `tdt agent enable codex` / `tdt agent disable codex` | Add or remove that workspace-local host integration; also supports `claude`. |
| `/tdt-constitution` | `tdt constitution show` | Read the current workspace policy and revision hash. |
| `/tdt-review-brain` | `tdt brain candidates --status all` | Inspect pending, approved and rejected proposals. Default is pending. |
| Ask your agent to inspect incomplete capture requests | `tdt brain requests` | List incomplete capture requests. |
| Ask your agent to make older brain filenames readable | `tdt brain migrate-names` / `tdt brain migrate-names --apply --expected-sha256 HASH --user-instruction REF` | Preview or apply legacy note renames and current brain link updates. |
| `/tdt-search` | `tdt brain search "query" --limit 10 --depth 1` | Retrieve current eligible notes with bounded links. |
| `/tdt-search` with a provider request | `tdt brain providers` | List installed search providers without executing them. |
| `/tdt-search` with an explicit indexing request | `tdt brain index --provider ID --rebuild` | Explicitly rebuild a selected provider index; omit rebuild to reconcile. |
| `/tdt-search` with the selected provider | `tdt brain search "query" --provider ID` | Select a provider for this query; repeat the option to combine rankings. |
| `/tdt-add-project` | `tdt project add PATH` / `tdt project list` | Register an external directory unchanged, or list registrations. |
| `/tdt-add-project` | `tdt project inspect ID` | Reread bounded onboarding evidence. |
| `/tdt-relink-project` | `tdt project relink OLD NEW_PATH` | Preview a moved project's registration and reference updates. |
| `/tdt-remove-project` | `tdt project remove ID [--permanent]` / `tdt project restore ID` | Preview archive, unregister or restore. |
| Project lifecycle skills | `tdt project references ID` / `tdt project cleanup ID` | Scan references or preview exact cleanup JSON from stdin. |
| Ask your agent to validate only; also used by `/tdt-install-stack` and optional `/tdt-stack-builder-create` | `tdt stack validate PATH` | Validate a local bundle and inspect disclosures. |
| `/tdt-install-stack` | `tdt stack install PATH` | Install a local bundle; catalog IDs also work when the registry is available. |
| `/tdt-install-stack` with an inspection-only request | `tdt stack install ID --inspect` | Download and verify a catalog release without installing. |
| `/tdt-workspace` | `tdt stack list` / `tdt stack docs ID` | Inspect installed provenance or find a stack's local guides. Omit ID to list all guides. |
| `/tdt-update-stack` | `tdt stack update ID --check` | Inspect a newer replacement without changing workspace state. |
| `/tdt-update-stack` after review | `tdt stack update ID --approve HASH` | Apply the exact inspected and user-approved replacement. |
| `/tdt-remove-stack` | `tdt stack remove ID` | Uninstall owned stack runtime files, preserving brain knowledge; `uninstall` is an alias. |
| Ask your agent to recover an interrupted operation | `tdt stack recover` | Recover an interrupted lifecycle, refresh, brain filename migration or host-integration transaction. |
| `/tdt-install-stack` | `tdt marketplace search "query"` | Search the selected HTTPS registry; requires network access. |
| `/tdt-add-skill` to author a workflow | `tdt skill propose` / `tdt skill propose --update` | Propose a named skill or intentionally update a user-owned skill; review before saving. |
| `/tdt-find-skills` for inventory; ask your agent for recovery | `tdt skill list` / `tdt skill recover` | Inspect skills/proposals or recover an interrupted user-skill save. |
| `/tdt-ui` | `tdt ui read SESSION --after 0` | Read retained interview responses. |
| `/tdt-ui` | `tdt ui close SESSION` / `tdt ui cleanup SESSION` | Stop the service, or delete retained session data. |

Review and policy writes require an actual decision on displayed contents. Use
[brain](brain.md), [constitution](constitution.md) and [skills](skills.md) for
proposal, hash and JSON-input details. Executable stack trust is separate from
update approval: see [stacks](stacks.md). For browser start, present, wait and
acknowledgement commands, see [UI](ui.md).

Explicit saves and scratchpad commands:

| Skill | CLI | Purpose |
| --- | --- | --- |
| `/tdt-capture` | `tdt brain save --user-instruction TEXT` | Save supplied knowledge; summary JSON on stdin. |
| `/tdt-note` | `tdt brain note --user-instruction TEXT` | Save scratchpad summary JSON with tags on stdin. |
| `/tdt-search-notes` | `tdt brain search QUERY --scope notes` | Search scratchpad content and tags. |
| | `tdt brain notes [--tag TAG]` | List scratchpad notes, metadata and IDs. |
| | `tdt brain related ID` | Find scratchpad notes sharing subject tags. |

## Reminders

`tdt reminder configure` reads preferences; `--timezone IANA --chat on|off`
updates them. `--schedule REFERENCE` records an externally configured job;
`--clear-schedule` clears the reference. These commands do not create/delete jobs.
`tdt reminder add --user-instruction TEXT` accepts reminder JSON on stdin.
`list [--status pending|done|cancelled|all]` shows records. `edit`, `snooze`, `done`
and `cancel` require an ID, current `--revision` and `--user-instruction`; edit and
snooze accept JSON on stdin. `check --channel manual|chat|scheduled [--limit N]`
claims due items; `ack ID --token TOKEN` records notification, not completion.
See [reminders](reminders.md) for the schema, setup and delivery recovery.

## Working files

- `tdt project create <relative-folder>` creates below work/ and registers the project.
- `tdt project inspect <name-or-id>` resolves a unique project name or registered path.
- `tdt work search <query>` discovers internal working files separately from knowledge.

Read WORK.md before choosing new locations; CLI paths are explicit and do not parse conventions.

Project lifecycle mutations require `--apply`, the preview `--expected-sha256`,
and `--user-instruction`. See [project lifecycle](projects.md#project-lifecycle).

## Local MCP reads

Install the optional dependency with `pipx inject thisdamnthing 'mcp>=2.3,<3'`
for an existing pipx installation, or install `thisdamnthing[mcp]` in a Python
virtual environment. Configure your local MCP host to launch `tdt` with:

```json
{
  "command": "tdt",
  "args": ["--workspace", "/path/to/workspace", "mcp", "serve", "--profile", "read-only"]
}
```

Replace the workspace path with an initialized workspace. The process stays bound
to that directory and uses stdin/stdout for MCP. Registration is manual; TDT does
not edit host configuration. Connecting MCP does not enable automatic capture.

The default `read-only` catalog has 43 tools; `everyday` has 76 in total.
The following list covers reads and selected everyday counterparts:

- `tdt_brain_names_preview`: complete legacy filename migration preview in both profiles, including renames and replacement contents (null removes an old path). Up to 1 MiB output budget; oversized output refuses without partial content. Shared read lock, no note or registry writes. Returns `proposal_sha256` binding renames and complete before/after contents, including derived catalog writes.
- `tdt_brain_names_apply` (everyday): apply with the preview `expected_sha256` and actual `user_instruction`. Stale plans refuse; identical completed retries preserve later edits. Prepared/completed backups are limited to 8 MiB, including no-op outcomes.
- `tdt_brain_names_status`: read retained outcome by `proposal_sha256` before retry or CLI fallback. CLI equivalent: `tdt brain names-status HASH`. Journals require CLI recovery and reread; unknown does not prove the operation never ran.
- `tdt_brain_repair_status`: read the retained outcome by exact `proposal_sha256` in either profile. After an uncertain apply, read this before retry or CLI fallback. CLI equivalent: `tdt brain repair-status <hash>`.
- `tdt_brain_repair_apply` (everyday): supply identical `changes`, preview `expected_sha256` and actual `user_instruction`. Returns a small completion receipt and backup path. Identical completed retries preserve later edits.
- `tdt_brain_repair_preview`: validate 1–20 changes against current audit hashes and return complete replacements plus a proposal hash, without writing notes or backups. Increase the result budget (up to 1 MiB) or reduce the batch if needed. Apply explicitly authorized changes through `tdt_brain_repair_apply` (everyday) or `tdt brain repair` with identical changes and the returned hash.
- `tdt_brain_audit`: paginated structural findings and canonical note hashes, with scan limitations and unreadable-note omissions.
- `tdt_capture_requests` / `tdt_capture_request_read`: bounded hook request inventory and exact status/provenance, without transcript reads.
- `tdt_workspace_context`: current complete constitution, WORK.md and tool names.
- `tdt_workspace_status`: bounded operational counts and recovery markers.
- `tdt_reminder_settings`: timezone, chat preference and external scheduler reference.
- `tdt_reminder_list` / `tdt_reminder_read`: reminder summaries and complete Markdown.
- `tdt_project_list`: paginated registered projects, including archived/missing state.
- `tdt_project_read`: registry details and complete retained registration Markdown.
- `tdt_project_operation_status`: exact proposal hash; historical outcome reconciliation before retry or CLI fallback.
- `tdt_project_remove_preview`: exact registered `id` and explicit `mode` (`archive` or `unregister`); complete replacements and the CLI proposal hash, without writes or source deletion.
- `tdt_project_restore_preview`: exact registered `id`; preview restoring active status, even with a missing source directory. Unregistered entries cannot be restored this way.
- `tdt_project_cleanup_preview`: exact project `id` and 1–20 `changes` with `path`, current `expected_sha256`, and complete `content` (explicit null deletes the whole file). Returns full replacements, scan coverage and CLI proposal hash; up to 1 MiB output budget, shared read lock, no writes. Use everyday `tdt_project_cleanup_apply` with identical changes, hash and actual user instruction. Cleanup outcomes are retained by proposal hash.
- `tdt_project_relink_preview`: exact registered `id` and absolute existing destination `path`; complete mechanical updates, new identity and preserved brain link. Source files and historical provenance remain intact. All lifecycle previews allow up to 1 MiB `budget_bytes`; oversized results refuse without partial output. Everyday apply tools use identical inputs, preview hash and the actual user instruction; reference cleanup is separate.
- `tdt_project_references`: paginated literal references and skipped entries for an exact project ID.
- `tdt_project_inspect`: bounded source evidence from an explicitly selected registered project.
- `tdt_guides_list` / `tdt_guide_read`: installed core and declared stack guides.
- `tdt_skill_list` / `tdt_skill_read`: canonical core, user and stack skills.
- `tdt_skill_inventory`: paginated live skill content prefixes across canonical and
  host folders for overlap review, including unmanaged skills. Ownership labels
  do not verify assets; truncated content is incomplete evidence. Also inspect
  retained proposals with status all. No execution or host history access.
- `tdt_skill_proposals` / `tdt_skill_proposal_read`: paginated retained user skill
  proposals and complete behavior, sources, decisions and recorded ownership.
  Defaults to pending; select approved, declined or all explicitly. Historical
  approval does not prove the version is installed. These reads never execute
  skill instructions, inspect host histories, propose or approve skills.
- `tdt_constitution_read`: complete constitution and its revision.
- `tdt_constitution_save` (everyday): complete approved `markdown`, current
  `expected_sha256` (or `missing`) and actual `user_instruction` approval reference
  (1–240 characters, one line). Uses the CLI policy lock and revision checks;
  appends an audit reference. The final policy must fit 6000 UTF-8 bytes. Returns
  only the saved SHA256 so the receipt fits the minimum budget. Read the complete
  policy back. After uncertainty reread before retry or CLI fallback; no retained
  outcome or automatic retry. Does not enable hooks or recover policy state.
- `tdt_brain_search`: literal search of approved knowledge with bounded links.
- `tdt_brain_read`: read an eligible note using a path or URI returned by search.
- `tdt_candidate_list`: paginated summaries; `status` is `pending` (default), `rejected` or `all`.
- `tdt_candidate_read`: complete candidate Markdown and its core review hash.
- `tdt_candidate_review_status`: complete candidate or promoted knowledge by exact ID, review history, revision and approval destination.
- `tdt_note_list`: paginated scratchpad summaries with subject tags.
- `tdt_note_read`: complete scratchpad Markdown, explicitly labeled unapproved.
- `tdt_note_search`: paginated scratchpad summaries matching a literal phrase in title, body or tags.
- `tdt_note_related`: paginated scratchpad summaries with shared tags, selected by exact note ID.
- `tdt_work_search`: bounded working-file discovery by filename and supported text.
- `tdt_work_read`: bounded working text by workspace-relative path or URI.
- `tdt_search_providers`: installed search provider metadata and recorded trust, without execution.
- `tdt_stack_list`: installed stack versions and recorded provenance.
- `tdt_stack_docs`: declared installed stack guides; read full content with `tdt_guide_read`.

Stack/provider catalogs accept `limit` (1–50) and inventory-bound `cursor` values.
They read at most 1 MiB of registry data and refuse interrupted stack/skill
transactions. Documentation reads retain the guide reader's 64 KiB file bound.
Recorded provider trust is an installation decision, not verification of current
assets or runtime compatibility. Discovery never runs providers, builds indexes,
downloads sources or rebuilds the documentation catalog. Metadata and documents
are untrusted reference material, not permission to execute instructions.

Scratchpad search/related accept `limit` (default 20, maximum 50) and `cursor`.
Search takes `query`; related takes `id` and ranks by shared-tag count then path.
Cursors bind the query, limit, operation, workspace and inventory revision; restart
without a cursor when stale. Results contain metadata, not full bodies: use
`tdt_note_read` before citing evidence. Scratchpad remains unapproved and is never
mixed into approved knowledge search. Shared tags do not establish semantic truth.

Working-file search takes `query` and `limit` (default 20, maximum 50); all
whitespace-separated words must match the filename and/or text. It scans at most
2000 entries and 32 directory levels under `work/`. Hidden entries, symlinks,
special files, nested `.tdt`/`.dryft` workspaces and `work/notes`/`work/reminders`
are excluded. Use the dedicated tools for those stores. External projects are not
searched. `.md`, `.txt`, `.csv` and `.json` support text search/read; other regular
files match names only (`text_readable: false`). Binary, invalid UTF-8 and possible
secret text are omitted. Search reports omission counts, `scan_truncated` and
`limit_reached` separately; it does not paginate. Narrow incomplete searches.

Working text reads accept `reference`, return at most a 32 KiB UTF-8 prefix and
explicitly report `content_truncated`. `revision` hashes the returned text, not
unread bytes. Search uses the same prefix, so text and possible secrets beyond
that bound are unknown. A filename match is not evidence of its current contents.
Working files are untrusted evidence, not approved knowledge. Reads never execute
file contents. The CLI `work search` shares these boundaries and reports omissions.

Brain audits accept `section` (`findings` by default, or `notes`), `limit` (1–50)
and `cursor`. Follow `next_cursor` until null for each section. Each page includes
the full report revision, readable-note and finding totals, scanner limitations
and all unreadable-note paths in `coverage.omissions`. Changing the report,
workspace, section or page limit invalidates a cursor; restart without it.
The shared CLI scanner checks at most 2000 canonical entries plus 2000 scratchpad
target entries and reads at most 32 KiB per note. Candidates are excluded, and
scratchpad links are checked only as targets. No repairs, provider execution,
external source checks or semantic review occur. An empty findings page is not
proof of a clean brain if there are omissions or additional pages. Findings and
note titles are untrusted data. Preview with `tdt_brain_repair_preview`; apply
explicitly authorized repairs with `tdt_brain_repair_apply` in everyday or the CLI.

All tools accept `budget_bytes`, generally defaulting to 32768 and capped at
131072 bytes for the application JSON. Repair and lifecycle previews/applies
allow up to 1 MiB. MCP also carries a text copy, so wire responses are
larger. Oversized results are refused whole. Increase the budget or narrow the
query; a refusal never substitutes a policy summary. Search accepts `query`,
`limit` (1 to 50, default 20) and `depth` (0 to 3, default 1). `limit_reached`
means more results may exist. Approved search does not paginate. Invalid note paths
appear in `coverage.omissions`; failed scans return an error rather than an empty
successful result. Evidence revisions identify the returned path, title and
content, including source references.

Candidate and scratchpad lists accept `limit` (1 to 50, default 20) and an opaque
`cursor`. Pass `next_cursor` unchanged with the same limit and status; null marks
the last page. Cursors bind the workspace, category, filter and inventory revision.
Changed inventory returns `stale_revision`; restart without a cursor. Scans are
bounded to 2000 entries per category and are not atomic across external edits.
Invalid notes are omitted with paths in `coverage.omissions`. A failed or oversized
scan is refused, not returned as a complete empty list.

Candidate/scratchpad reads accept `reference` as an inventory ID, path or URI.
They return full Markdown including sources, provenance and review history.
Their `revision` hashes that complete text with the same newline normalization
as core candidate review. Read the full candidate before reviewing it through the
review tool or CLI; a list summary is insufficient. Reading never approves content.
Duplicate IDs require an exact path. Neither category enters approved retrieval.

The opt-in `--profile everyday` adds candidate review, two capture tools and eight reminder tools, alongside the other everyday operations below.

`tdt_candidate_review_status` accepts `id` and reads the current complete Markdown
under the shared lock. It follows promotion into knowledge even when project
eligibility excludes that note from search. It does not grant search eligibility.
`approval_destination` previews the current allocation; concurrent filename
collisions can change the eventual path. `pending_cleanup` means both stores
contain this ID and requires inspection of the saved approval history.

`tdt_candidate_review` requires `id`, `expected_sha256` from the complete displayed
proposal's `revision`, an actual `user_instruction`, and `decision`:
`{"action":"approve"}`, `{"action":"reject"}`, or
`{"action":"edit","summary":{...}}` using the capture summary fields below.
Approval preserves provenance/history in a separate knowledge note before removing
the candidate. Rejection remains outside knowledge search. Editing retains the
previous proposal in history and stays pending until a new explicit approval.
The small receipt fits the minimum 1024-byte budget. Stale hashes, nonpending
candidates, secrets, lock conflicts and stack recovery markers refuse writes.

After an uncertain response, read exact review status and compare saved history
with the original instruction, decision and proposal hash. Do not repeat completed
edits or rejections with a fresh hash. An interrupted approval may leave
`pending_cleanup`; only the identical original approval can finish deletion after
the shared core verifies the saved canonical content. If state is unreadable,
leave recovery for later. Candidate reads/saves do not authenticate user consent.
Use the current hook token to suppress automatic capture for review turns.

Live candidate review passed with Codex CLI 0.156.1 and Claude Code 2.1.289
using temporary configurations: explicit approval/rejection/edit, stale-hash
refusal, pending edit exclusion from search, and interrupted approval cleanup
without changing canonical content. Independent file audits confirmed unchanged
control records. Separate process-termination checks passed before/after approval
persistence, after cleanup, and after edit/reject persistence in both SDK modes.
The live runs used displayed fixture proposals and preauthorized decisions; they
did not verify automatic review-skill routing or a multi-turn human approval flow.

`tdt_capture_requests` accepts `status` (`requested` by default, `captured`,
`skipped` or `all`), `limit` and `cursor`. Scans refuse malformed state and exceedances
of 2000 entries or 32768 bytes per request. Cursors expire when inventory changes.
`tdt_capture_request_read` accepts an exact `request_id`; neither reader reads the
transcript path stored in provenance. Inventory order never identifies the active
conversation.

`tdt_capture_submit` requires the existing `request_id` delivered by the current
host hook and a discriminated `payload`: `{"action":"skip"}` or
`{"action":"summary","summary":{"title":"...","kind":"fact","body":"...",
"sources":["user message with locator"],"links":["index"],"project":null}}`.
Kinds are fact, decision, question or inference; shared core summary limits and
secret checks apply. Provenance comes from the saved request. Capture creates a
pending candidate only. Replays return the saved captured/skipped status without
accepting replacement content. After a lost response, read request status before
retrying or using CLI fallback; a partial candidate write can be reconciled by
resubmitting the original request.

`tdt_capture_suppress` requires the exact current request-hook `token`. Use it for
user saving restrictions or explicit save/review/reminder work. Repeats are safe
within that turn; stale tokens fail. Tokens and request IDs are explicit context,
not authenticated host identity. MCP does not create hook requests or turn tokens,
register hooks, or enable automatic capture. Enabled hooks prefer these tools on
the server bound to their workspace, with CLI fallback when unavailable. After an
uncertain capture response, read the exact request through MCP or
`tdt --workspace <root> brain request <request-id>` (bounded JSON, no transcript
read). Captured/skipped is final; requested permits one identical CLI retry.
If status cannot be read, leave recovery for later. Same-token suppression may be
repeated safely through CLI. Neither fallback bypasses permission or validation
refusals. Refresh existing owned workspace resources to receive updated hooks.
Both writes share core
locking, refuse stack recovery state, and return receipts within the minimum
1024-byte budget. Live Codex CLI and Claude Code checks verified submission,
skip, status-before-retry, token suppression and preserved pending provenance
using disposable hook-generated fixtures. Real lifecycle capture and suppression
also passed on both hosts. Updated hooks selected MCP without a transport override
in the user prompt; capture and suppression both passed with CLI available.
Read-only MCP catalogs exercised unavailable-tool CLI fallback. Server exits before
and after capture writes exercised real lost responses: Codex used the exact CLI
status reader after MCP transport closure; Claude reconnected for the MCP status
read. Requested state led to one identical CLI retry; captured state led to no
resubmission. CLI fallback requires host permission. Two initially denied Claude
runs preserved pending state without claiming success; fresh runs with narrowly
scoped approval passed. Forced server termination before/after
candidate writes and after capture/skip/suppression state saves recovered through
fresh-server status reads and retries in both SDK modes. Live routing checks used
the default SDK mode; power-loss recovery remains unverified. Hosts may display
recovery commentary despite the hook's request to keep capture internal.

The reminder tools are:

- `tdt_reminder_create` requires `title`, `body`, `due_at`, an explicit IANA
  `timezone`, and `user_instruction`. Resolve the intended date/time with the user;
  `due_at` must include an offset matching that timezone. Title/body limits are
  160/1500 characters, with one title line and at most 20 body lines.
- `tdt_reminder_edit` accepts a nonempty `changes` object containing any of
  `title`, `body`, `due_at` and `timezone`. Omitted fields remain unchanged;
  null values are refused. Changing timezone requires a matching `due_at`.
- `tdt_reminder_snooze` requires `changes.due_at` in the future and optionally
  `changes.timezone`; otherwise it uses the reminder's existing timezone.
- `tdt_reminder_complete` and `tdt_reminder_cancel` retain the record and change
  its task status. Completion is separate from notification.

Every edit, snooze or task-status change requires its exact `id`, the integer
`reminder_revision` from a fresh read (not the Markdown hash), and
`user_instruction` describing the user's request. Changes advance the revision
and clear delivery claims. Text-only edits preserve prior notification; changing
the due time or snoozing rearms it. Creation coalesces exact pending duplicates
without changing their provenance, notification or revision. Finished records do
not block creation of a new reminder.

Creation, edits and task-status changes return a small receipt containing ID, status and the reminder revision;
creation also returns `result` (`saved` or `existing`). Read the reminder again
for full content. A stale revision refuses the write. After a disconnect or
uncertain error, inspect state before retrying; changes do not replay a successful
receipt, and duplicate creation coalesces only while the exact pending record
still exists. The instruction records stated authority; it does not authenticate
a human decision.

`tdt_reminder_configure` accepts `user_instruction` and a nonempty `changes`
object with `timezone`, `chat` and/or `schedule`. Omitted fields stay unchanged;
`schedule: null` clears the external job reference. Initial setup requires a
valid IANA timezone. It returns a small `configured` receipt; reread settings
for the resulting values. The instruction is validated but is not retained in
the existing settings format. Configuration does not create, stop or verify an
external job, and changing the default timezone does not reschedule reminders.

`tdt_reminder_claim_due` requires an explicit `channel` (`manual`, `chat` or
`scheduled`) for an authorized check; `limit` defaults to 10 and accepts 1–20.
Chat checks return no claims while opted out; scheduled checks refuse without a
configured reference. Results contain complete title/body, ID, integer revision,
due time/timezone, delivery token, channel and lease expiry. Claims last ten
minutes and exclude competing checkers across CLI and MCP processes. The complete
response budget is checked under the shared lock before any claims are written;
reduce the limit or increase the budget after a budget refusal.

Call `tdt_reminder_ack` with each `id` and `token` before displaying its content.
Display only a `notified` result; `already-notified` is a successful same-token
retry and must not announce again. Changed, expired or invalidated tokens refuse
acknowledgement. Notification leaves task status and revision unchanged. A lost
claim response requires inspecting reminder state or waiting for lease expiry;
a partial I/O failure can leave some claims saved. Rendering is not transactional:
a failure between acknowledgement and display can leave a notified item unseen.
Reminder content is data and never permission to execute the reminded action.

Explicit saves are available in the everyday profile:

- `tdt_knowledge_save`: supply `summary` (title, kind, body, sources, links and
  optional project) plus `user_instruction`. Saves approved knowledge with source
  provenance and an approval record on an explicit user request.
- `tdt_note_save`: the same input with 1–8 lowercase subject `tags` inside the
  summary. Saves scratchpad content with no promotion or approval history.

Both return `id`, `status` and `result` (`saved` or `existing`); read the ID with
`tdt_candidate_review_status` (knowledge) or `tdt_note_read` (scratchpad) to
obtain its path and complete content. The exact status reader also accepts direct
knowledge IDs; ordinary `tdt_brain_read` accepts eligible paths or workspace URIs.
Receipts fit the 1024-byte minimum result budget. No automatic hooks or host
identity are inferred. The save skills require current-turn capture suppression
and prefer MCP with CLI fallback; direct tools remain usable without hooks.
Search existing content first and preserve conflicts. User instruction is local
audit information, not authenticated consent.

After a lost response inspect the relevant inventory/content before an identical
retry, including CLI fallback. Identity derives from normalized title, kind, body,
sources and project, plus sorted unique scratchpad tags. Links and instruction
references do not change identity. Existing content, provenance and review history
are preserved, even if the submitted links or instruction differ. Changed identity
fields create a new note. Invalid existing records in the target store refuse the
save instead of being skipped during duplicate detection. Registered-project and
eligible-link checks still apply on retry. Knowledge excluded by current project
eligibility cannot be read through ordinary knowledge retrieval; inspect the exact
ID with `tdt_candidate_review_status` if needed. Never change a summary merely to
force a retry, or claim an unread record was verified.

Explicit save tools also passed live Codex CLI 0.156.1 and Claude Code 2.1.289
checks on Linux: 28 MCP calls per host, approved/scratchpad readback, duplicate
preservation, search separation and read-before-retry recovery of persisted
fixtures. Independent file hashes confirmed only the two requested new notes and
suppression state changed. Eight real server-kill checks covered both SDK modes
and both save types before and after persistence; fresh-server reads and identical
retries retained one record without rewriting completed saves. Automatic skill
selection, actual host-hook lifecycle for these saves, power loss and live-model
reconnection were not verified by these checks.

Project registration is available in the everyday profile:

- `tdt_project_add`: supply an absolute `path` to an existing directory, internal
  below work/ or external. Relative paths, home shorthand and traversal are refused.
- `tdt_project_create`: supply `relative_folder` below work/, without the work/
  prefix. Read WORK.md first. Existing directories and files are preserved;
  reserved stores, hidden components and unsafe paths are refused.

Both require the user's instruction and return only `id` and `result`
(`registered` or `existing`), within the minimum 1024-byte budget. Read registration
facts with `tdt_project_read`. These tools do not inspect external source or save
onboarding interpretations. `/tdt-add-project` prefers them with CLI fallback.

Project onboarding adds two tools:

- `tdt_project_inspect` (both profiles): pass the exact registered `id`. Reads up
  to 100 top-level names and ten allowlisted docs/manifests, at most 4 KiB each,
  from an active available project. This explicitly reads internal or external
  source. It returns registration facts, `brain_link`, names, documents and an
  evidence notice. Documents carry exact `source`, `text` and `truncated`, or an
  `omitted` reason. Missing/unsafe/unreadable files and possible secrets are
  reported as omissions; inventory/content truncation also sets coverage flags.
  Directory components and documents cannot be symlinks. No recursive scan,
  command execution or project writes occur. Increase `budget_bytes` up to
  131072 if the result does not fit; budget refusal returns no partial evidence.
- `tdt_project_propose` (everyday): pass `id` and `summary` with title, kind,
  concise body, 1–8 source references and links (prefer inspection's `brain_link`).
  Optional summary `project` must be null/absent or match `id`. Interpretations
  should use kind `inference` and cite the inspected evidence. Returns candidate
  `id`, `status` and `result` (`saved` or `existing`) within 1024 bytes. New
  proposals are pending, with project provenance and no approval. Read full
  saved content with `tdt_candidate_review_status`; promotion requires the
  ordinary explicit candidate review.

`/tdt-add-project` prefers these tools with CLI inspect/propose fallback. Identical
proposal retries preserve existing bytes, including edited or reviewed content;
they may return pending, approved or rejected. After an uncertain write, inspect
candidate inventory and exact review status (or saved Markdown) before retrying
the identical summary. Malformed records, duplicate identities, interrupted
promotion, mismatched provenance, archived/missing projects, lock conflicts and
pending stack recovery refuse proposal writes. Resolve the existing state rather
than changing the summary to force a new identity. Project source stays unchanged.

Onboarding passed live Codex CLI 0.156.1 and Claude Code 2.1.289 verification on
Linux, with 36 MCP calls per host. Independent transcript and file-hash audits
confirmed bounded internal/external inspection, two pending proposals, exact reads
before identical retries, retained reviewed proposals, expected refusals and
unchanged external source/control records. Ten actual server-kill checks covered
both SDK modes before/after proposal persistence and after approval's canonical
write. Fresh-server reads and recovery retained one proposal, preserved completed
bytes and required exact approval recovery before replaying an interrupted
promotion. Automatic skill routing, actual host-hook lifecycle, power loss and
live-model automatic reconnection were not verified by these checks.

After an uncertain response, inspect project list/read before an identical retry.
Creation can leave a directory before registration completes. Registration writes
its note before its registry entry; retry preserves an exact interrupted note and
completes the registry. Existing registrations retain their note and identity.
Malformed or duplicate registration notes, invalid or oversized registries, lock
conflicts and pending workspace recovery refuse writes. Archived projects require
restore; moved projects require explicit relinking. Never register a replacement
identity to bypass those workflows. Internal creation is covered by the same lock
as registration. It does not scaffold source or write into external projects.

Project registration also passed live Codex CLI 0.156.1 and Claude Code 2.1.289
checks on Linux: 30 MCP calls per host, exact readback, duplicate preservation,
partial-registration recovery and expected refusals. Independent file hashes
confirmed only the two requested new notes and registry changed; existing user
files, registration notes and external source fixtures were preserved. Fourteen
real server-kill checks covered add/create in both SDK modes at directory, note
and registry persistence boundaries. Fresh-server reads and identical retries
retained one registration and preserved existing note bytes. Automatic skill
selection, power loss and live-model automatic reconnection remain unverified.

Profiles are fixed at startup, and excluded calls are refused. `read-only` remains
the default. Mutations use the same nonblocking cross-process lock as the CLI;
in-process mutations are serialized, and cancellation waits for an active worker
before releasing serialization. A lock conflict may return `operation_refused`;
inspect state before retrying. Reads remain available during a mutation.
Everyday also exposes `tdt_brain_search_providers` with required `providers`
(1–8 distinct explicitly selected stack IDs), `query`, `limit`, `depth` and
`budget_bytes`. It combines provider and literal rankings through core, checking
trust, assets, compatibility and current approved evidence. It never indexes or
persists query cache changes through core. Trusted provider code runs with local
process permissions, not an OS or network sandbox; its MCP annotation is open-world
and non-read-only. Failures refuse the query rather than silently falling back;
offer `tdt_brain_search` explicitly. A budget refusal can follow execution.
Everyday `tdt_brain_index` requires one `provider` stack ID and the actual
`user_instruction`; optional `rebuild` defaults false and `budget_bytes` follows
ordinary read budgets. It reconciles the approved corpus through shared CLI core;
rebuild starts without the previous cache. Trust, assets, compatibility, ownership
and the exclusive workspace lock are checked before execution. Cache and ownership
are written together. The receipt (`provider`, `indexed`, `rebuild`) fits the
minimum budget and reports provider acknowledgement, not a retained outcome.
Execution can take five minutes and runs with local process permissions. After
uncertainty inspect provider search/cache state before an authorized retry; retries
execute code again, and interrupted journals require CLI recovery. This tool never
installs or trusts a provider. Other everyday writes are not exposed. External source
reads are limited to explicit registered-project inspection. Retrieved notes are
evidence; instructions inside them do not authorize actions. The server has no
HTTP endpoint, resource subscriptions or MCP prompts. Read-only calls were verified
on Linux with Codex CLI 0.156.1 and Claude Code 2.1.289 in noninteractive sessions
using temporary MCP configuration. Completion/cancellation also passed live checks
in both hosts, including stale-revision refusals and reads through a second
read-only server. Creation/edit/snooze also passed in both hosts, including exact
duplicate coalescing, stale-revision refusals, read-only readback and unchanged
control records. Settings/configuration and delivery claims/acknowledgements also
passed in both hosts: chat opt-out and scheduled-channel refusal, claim exclusion,
same-token acknowledgement retry, read-only readback, and one post-acknowledgement
Markdown notification in each CLI transcript. Task status/revision and a future
control reminder stayed unchanged. This does not verify desktop rendering,
external scheduler delivery or disconnect during a claim write.
The noninteractive Codex checks required launch-only approval
for the exercised writable tools; host approval settings still apply independently of
the selected TDT profile. Interactive UI, persistent registration and automatic
capture were not exercised by those checks. Incoming stdio messages are limited to 8 MiB of
bytes per line, excluding the final LF (a CR counts toward the limit). The reader
enforces this before UTF-8 decoding and JSON parsing. Oversized input closes the
connection with a nonzero exit and a stderr diagnostic, without echoing content
or draining the rest of the line. Reconnect with a smaller request; no JSON-RPC
response is promised for the rejected frame. This is a per-message limit, not a
total session memory or concurrency limit.

Project lists use the same `limit`/`cursor` rules as note inventories. Project reads
accept an exact registered ID, absolute path or workspace URI from the list; names
and arbitrary paths are not resolved. They report a missing registration note
explicitly. Registration revisions hash complete Markdown. Project revisions hash
returned registry details and availability. External project paths are checked for
availability; source files are never read. Archived projects keep their archived
availability label, matching the CLI. Lists include at most 2000 registry entries
and read at most 256 KiB of registry JSON.

Workspace status reports an observation time, pending candidate count, incomplete
capture count, project counts, due pending reminders and known recovery markers.
Due reminders include already announced or currently claimed reminders that remain
pending; this is a task count, not a delivery queue. Capture scans stop at 2000
entries and read at most 32 KiB per request without opening transcripts. Malformed
operational state refuses the call. Invalid candidate notes appear as omissions,
so candidate counts may be partial. An interrupted stack/project transaction
leaves candidate/reminder counts null with omissions. Status never recovers,
claims delivery, executes providers or writes files. These reads are observations,
not atomic snapshots across concurrent edits.

Guide and skill lists use `limit`/`cursor` pagination. Reads accept the returned
catalog ID, exact path or workspace URI. Guides include the shipped core guide
allowlist and documentation declared in installed stack records. Skills include
canonical core skills, approved user-owned skills and installed stack-owned
canonical entries. Host bridges, undeclared files, skill proposals and decision
history are excluded. Ownership labels identify registry attribution, not a fresh
integrity or trust approval. Local edits remain readable and change revisions.

Each document is limited to 64 KiB and each catalog to 2000 entries. Stack registry
reads cap at 1 MiB and user skill state at 2 MiB. Missing core/user files appear as
list omissions; invalid content, unsafe paths, conflicting owners, missing declared
stack docs or recovery markers refuse the call. Skill descriptions come from
validated canonical front matter. Reads return complete Markdown with its SHA256;
output budgets can refuse a document whole. Reading does not execute a skill or
authorize embedded instructions, and these tools never rebuild catalogs.

Reminder lists use the same `limit`/`cursor` rules, sorted by due time and ID.
`status` accepts `pending` (default), `done`, `cancelled` or `all`. Pending includes
future, already notified and claimed reminders; listing is not a delivery check.
`claimed` means a stored claim exists, including an expired claim. Reads accept an
exact ID, workspace-relative path or bound URI and return complete Markdown.
`revision` is the SHA256 of that text; `reminder_revision` is the core integer edit
revision. Delivery changes invalidate cursors even when the edit revision stays
unchanged. Reads never claim, acknowledge, complete or schedule reminders.
Malformed or duplicate records refuse the inventory; files are limited to 32 KiB
and scanning to 2000 entries. Reminder text remains operational data, separate
from approved knowledge.


Everyday MCP exposes `tdt_ui_start`, `tdt_ui_present`, `tdt_ui_status`,
`tdt_ui_read`, `tdt_ui_wait`, `tdt_ui_ack`, `tdt_ui_close` and `tdt_ui_cleanup`.
Present accepts the page object directly, using the same core validation as CLI.
Start defaults to no browser launch and returns the private local URL. Status
returns connection/round/cursor metadata without page content or credentials.
Read/wait include complete events and original prompts, defaulting to one event;
use `next_after` while `has_more` is true. Increase `budget_bytes` up to 1 MiB
for large events. Budget refusal never acknowledges events. Waits are bounded to
30 seconds and do not hold the MCP mutation lock. A cancelled MCP call does not
cancel the interview. After uncertain start/present responses inspect retained
state/current round before retrying; present always creates a new round.
Close retains answers; cleanup deletes them and requires explicit user instruction.
These tools do not submit answers on the user's behalf or promote them to knowledge.

### MCP project reference review

`tdt_project_references` is available in both profiles. Supply an exact project
`id`, optional `section` (`references` by default, or `skipped`), `limit` and
`cursor`. Removed projects remain addressable while their registration note is
retained. Every page includes project identity, reference/skipped totals, scan
truncation and limitations. Cursors bind the entire report, project, section and
page size; restart after changes. Skipped details have their own paginated section
so omissions cannot silently disappear behind the reference page.

The shared CLI scan checks at most 5000 entries in brain/work and supported text
files up to 256 KiB; it skips hidden paths, symlinks, unsupported/unreadable files
and possible secrets. It does not scan external project source. Literal matches
are review hints, not ownership or permission to delete. Everyday supports separately authorized reference cleanup writes. A result-budget refusal returns no partial page.


### MCP project lifecycle apply and outcomes

Both profiles expose `tdt_project_operation_status` with an exact
`proposal_sha256`. Everyday adds `tdt_project_remove_apply` (exact `id`, explicit
`mode`: `archive` or `unregister`), `tdt_project_restore_apply` (`id`) and
`tdt_project_relink_apply` (`id`, absolute `path`). Each apply requires the same
preview inputs, `expected_sha256` and actual `user_instruction`/reference.
Review complete previews before applying within the user's authorized scope.
Source directories remain untouched; reference cleanup requires separate review.

Apply returns a small receipt with `status`, `operation`, `project_id`, hash and
backup path. The project ID is the resulting identity, including after relink or
unregister. After uncertainty, read status before retry or CLI fallback:
`tdt project operation-status HASH`. `completed` is historical success, not proof
current files match; identical retries return it without changing later edits.
Use original arguments and instruction even after the old registration disappears.
Changed arguments or instruction for the same retained hash refuse.

`prepared` means backup/intent retained without committed completion; inspect
before identical retry. `unknown` means no retained record, not proof it never ran
and not permission to apply. Legacy UUID backups are not indexed.
`recovery_required` means a shared transaction journal exists; use the indicated
CLI recovery and reread. Completion and registry/note writes share the journal;
rollback restores prepared state. Status reads share the read lock; applies use
the exclusive workspace lock. Indexed backups refuse above 8 MiB before writes.


### MCP reference cleanup apply

Everyday exposes `tdt_project_cleanup_apply` with identical `id` and `changes`
from `tdt_project_cleanup_preview`, `expected_sha256` and actual `user_instruction`.
Review complete replacements and scan coverage; null content deletes the entire
file. Archive/unregister permission alone does not authorize reference cleanup.
CLI cleanup shares the same hashes, validation, backups and retained outcomes.
Use `tdt_project_operation_status` after uncertainty before retry or CLI fallback.
Identical completed retries preserve later changes even after the removed
registration note was deleted. Keep that note until the final batch so additional
reference scans can resolve the project. Cleanup completion and file changes share
the recoverable transaction; legacy UUID cleanup backups remain unindexed.
