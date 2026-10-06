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
| Ask your agent to make older brain filenames readable | `tdt brain migrate-names` / `tdt brain migrate-names --apply` | Preview or apply legacy note renames and current brain link updates. |
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

The default `read-only` catalog has eighteen tools:

- `tdt_workspace_context`: current complete constitution, WORK.md and tool names.
- `tdt_workspace_status`: bounded operational counts and recovery markers.
- `tdt_reminder_settings`: timezone, chat preference and external scheduler reference.
- `tdt_reminder_list` / `tdt_reminder_read`: reminder summaries and complete Markdown.
- `tdt_project_list`: paginated registered projects, including archived/missing state.
- `tdt_project_read`: registry details and complete retained registration Markdown.
- `tdt_guides_list` / `tdt_guide_read`: installed core and declared stack guides.
- `tdt_skill_list` / `tdt_skill_read`: canonical core, user and stack skills.
- `tdt_constitution_read`: complete constitution and its revision.
- `tdt_brain_search`: literal search of approved knowledge with bounded links.
- `tdt_brain_read`: read an eligible note using a path or URI returned by search.
- `tdt_candidate_list`: paginated summaries; `status` is `pending` (default), `rejected` or `all`.
- `tdt_candidate_read`: complete candidate Markdown and its core review hash.
- `tdt_note_list`: paginated scratchpad summaries with subject tags.
- `tdt_note_read`: complete scratchpad Markdown, explicitly labeled unapproved.

All tools accept `budget_bytes`, defaulting to 32768 and capped at 131072 bytes
for the application JSON. MCP also carries a text copy, so wire responses are
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
existing CLI; a list summary is insufficient. Reading never approves content.
Duplicate IDs require an exact path. Neither category enters approved retrieval.

The opt-in `--profile everyday` adds eight reminder tools (26 tools total):

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

Profiles are fixed at startup, and excluded calls are refused. `read-only` remains
the default. Mutations use the same nonblocking cross-process lock as the CLI;
in-process mutations are serialized, and cancellation waits for an active worker
before releasing serialization. A lock conflict may return `operation_refused`;
inspect state before retrying. Reads remain available during a mutation.
Other everyday writes, provider execution and external source
reads are not exposed. Retrieved notes are
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
