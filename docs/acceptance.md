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
| Stack descriptions | Confirm both hosts preserve canonical description YAML on install, update and host enablement. Reinitialize an existing workspace to refresh owned placeholder bridges; repeat for idempotence and confirm edited bridges are refused. |
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

## Local MCP retrieval

Use a disposable workspace and an installation built with the `mcp` extra.
Launch `tdt --workspace PATH mcp serve --profile read-only` with a local stdio
client. Check discovery and JSON input/output schemas for the fifteen advertised
tools. Read context and policy, search approved knowledge, and follow a returned
reference. Compare CLI and MCP search eligibility and link traversal.

Check missing explicit workspace, invalid workspace, missing optional dependency,
unknown profiles/tools/arguments, numeric bounds, foreign URIs and traversal.
Include pending/rejected notes, scratchpad and unregistered-project knowledge;
none should enter approved retrieval. Exercise invalid UTF-8, malformed metadata,
oversized notes, a symlink and a FIFO. Confirm omissions or refusal without hangs.
Change/remove expected policy and request a budget too small for complete context.
Confirm no silent policy summary, no provider execution and no workspace writes.

Exercise disconnect/restart and concurrent reads with the SDK client, then verify
actual Claude and Codex registration and tool use separately. SDK client success
does not establish live host compatibility.

Page candidate and scratchpad inventories with small limits. Check pending/rejected
filters, empty/final pages, changed content, changed filters/limits, foreign and
malformed cursors. Read by ID/path/URI, compare candidate revision with the CLI
review hash and check that full provenance/history is present. Refuse category
crossovers; require an exact path for duplicate IDs. Exercise invalid scratchpad
tags, status mismatches, malformed files, scan limits and output budget refusal.
Confirm that reads preserve all workspace bytes and reminder/capture state.

Approved search does not paginate. There is no enforced incoming transport-message cap; output budgets cover application JSON,
which is duplicated in the MCP text block. No automated tests.


For MCP workspace status/project reads, create available, missing and archived
registrations and compare with CLI registry state. Page results, invalidate a cursor
by changing availability or registry data, and read by exact ID/path/URI. Confirm
missing/duplicate/invalid registration handling, foreign references and symlink
refusal. Verify no external project source reads. Check pending captures and due,
notified, claimed, completed and future reminders without changing delivery state.
Exercise recovery markers (null blocked counts), malformed/oversized state, bounded
capture inventory and invalid candidate omissions. Compare workspace and external
fixture bytes before/after calls. Live host verification remains separate.


For MCP guide/skill reads, check core guide allowlists, approved user skills and
installed stack skills/docs. Compare exact installed bytes/revisions; check skill
descriptions and absence of host duplicates, undeclared files and pending proposals.
Page lists and invalidate cursors after content changes. Exercise exact IDs/paths/
URIs, cross-category/foreign/traversal refusals, missing files, malformed front
matter, ownership conflicts, symlinks, FIFOs, oversized content and registry bounds.
Verify no execution, catalog rebuilding or workspace writes; recovery markers must
refuse discovery. Check the earlier MCP tools after shared-reader changes.

For MCP reminder reads, check pending/done/cancelled/all filtering, due-time order,
pagination and ID/path/bound-URI reads against complete stored Markdown and its
SHA256. Keep notified and claimed pending reminders visible, including future
reminders; verify reading changes no files. Distinguish content hashes from core
integer edit revisions. Delivery-only changes must invalidate cursors. Check
foreign/traversal references, duplicate IDs, malformed metadata, symlinks, special
files, 32 KiB files, 2000-entry scans, recovery refusal (also with no reminder
store), result budgets and empty inventories. Verify discovery/output schemas and
stdio calls with modern and legacy SDK clients on the installed wheel.

For MCP incoming message limits, verify an 8 MiB frame plus LF is accepted and
an 8 MiB + 1 byte frame closes the connection without waiting for LF or EOF.
Check UTF-8 byte counting, fragmented input, several frames in one write, final
EOF without LF, malformed JSON below the cap and disconnect/restart. Oversized
input must produce a nonzero exit, a bounded stderr diagnostic and no content
reflection or traceback. Confirm modern/legacy SDK discovery and calls on the
packaged wheel. The cap bounds individual raw frames, not all concurrent calls.

Live read-only verification on 2026-10-06: Codex CLI 0.156.1 and Claude Code
2.1.289 both connected to the installed wheel using temporary stdio configuration
on Linux. Each successfully invoked all 17 tools. Transcript inspection confirmed
complete read bytes/hashes, reminder pagination, a rejected foreign-workspace
reference and successful status calls after that error. Claude also recovered
from a guide result budget refusal by increasing the budget. Workspace file
hashes were identical before and after; neither host claimed reminders. These
were noninteractive model-driven CLI sessions, not SDK-only probes. Interactive
UI, persistent registration, capture hooks and macOS remain separate checks.
The generic result-size diagnostic currently mentions policy rereading for
non-policy results too; this is a wording follow-up, not a failed read/retry.

For the first writable MCP slice, launch both profiles in disposable workspaces.
Verify 17 read-only / 22 everyday tools and matching context/annotations; excluded
calls must not mutate. Complete and cancel pending reminders with current integer
revisions and user instruction; check preserved body/provenance, incremented
revision and cleared claim. Check stale, finished, missing, malformed and unknown
arguments, minimum result budget, recovery refusal and competing CLI locks.
Inspect state after a lost response before retrying. Verify unrelated reads during
a write and cancellation retaining serialization until the worker finishes.
Generic result-budget failures must not direct callers to policy; context budget
failures must still require complete policy. Use both SDK modes on the built wheel.

Live writable verification passed on Linux with Codex CLI 0.156.1 and Claude Code
2.1.289: each made 14 calls through temporary everyday/read-only servers,
completed and cancelled the selected fixtures, received two stale-revision
refusals, and read back results through both servers. Independent file hashes
confirmed only the two authorized reminder records changed per host. The initial
Codex run refused writes under its noninteractive approval policy and changed no
files; a rerun used launch-only per-tool approval for completion/cancellation.
No persistent registration or saved host settings changed. Read-only excluded-call
refusal was exercised through the SDK; live hosts observed the absent write tools.
Cancellation serialization was checked with an instrumented held worker, not a
live-host disconnect. Actual crash/restart during a write remains unverified.

For MCP reminder creation/edit/snooze, verify both SDK modes on the packaged wheel.
Require explicit creation timezone and matching offset; check ambiguous/gap times,
past creation, future-only snooze, empty/null/unknown changes and core text bounds.
Check exact pending duplicate coalescing without provenance or delivery changes,
and fresh creation after completion. Edits retain ID/path/creation/provenance,
advance revisions and clear claims; text-only edits preserve notification while
changed due times and snoozes rearm it. Check stale/finished refusals, 1024-byte
receipts, profile exclusion, recovery markers and CLI lock conflicts without writes.
Creation/edit/snooze live-host evidence is recorded below.

Packaged creation/edit/snooze checks passed on Linux in SDK auto and legacy modes:
17/22 catalogs and context, output schemas, write annotations, profile refusal,
exact duplicate preservation, finished-record recreation, field validation,
missing/mismatched offsets and daylight-saving gaps, future snooze, notification
rearming, preserved identity/path/provenance, stale/finished refusal, shared locks,
recovery markers and minimum-budget receipts. Existing completion/cancellation
checks also passed in both modes. No automated suite added or run; temporary
manual probes used disposable workspaces. Crash/disconnect during writes remains unverified.

Live creation/edit/snooze verification passed on Linux with Codex CLI 0.156.1
and Claude Code 2.1.289. Each made 14 calls with temporary everyday/read-only
servers: created one reminder, coalesced an exact duplicate, edited and snoozed
with 1024-byte receipts, refused two stale revisions, and read back revision 3
through both servers. Independent transcript/state audit verified UTC conversion,
retained creation provenance, no delivery claims/acknowledgements and unchanged
control. Full workspace hashes proved only the new authorized reminder file
changed. Both hosts exited 0. Codex used launch-only approval for the three
writable tools; no persistent host settings or registrations changed.

For MCP reminder settings/delivery, verify the 18-tool read-only and 26-tool
everyday catalogs and context, read/write annotations and excluded calls. Read
unconfigured defaults without creating settings. Configure partial preferences,
clear only the schedule reference with null, reject empty/invalid changes and
require an initial timezone. Confirm no external job is created or stopped.
Claim due reminders using explicit manual/chat/scheduled channels; verify chat
opt-out, unconfigured scheduled refusal, complete content and expiring tokens.
Compete across MCP processes and the shared core/CLI lock. Refuse oversized
responses before any claim writes, including multi-item and UTF-8 byte boundaries.
Acknowledge current tokens, repeat the same token without changing bytes or
announcing again, expire/reclaim a lease and reject old or edit-invalidated tokens.
Keep task status, revision and creation provenance unchanged on notification.
Check lock/recovery refusal and creation/edit/snooze regression.

Verified on Linux with the packaged wheel and both auto/legacy SDK stdio clients:
18/26 catalogs, output schemas, preferences/clearing, explicit channel gates,
competing MCP claims and shared-core exclusion, expiry/reclaim, acknowledgement
retry/invalidation, preserved task state, lock/recovery refusal, and existing
creation/edit/snooze behavior. Direct packaged-adapter checks additionally passed
all-or-nothing two-item budget refusal, exact UTF-8 envelope size boundaries, and
a 1024-byte configuration receipt with long settings. The shared settings writer
now refuses an outstanding stack recovery marker. Dependency and whitespace
checks passed. No automated suite added/run.

Live noninteractive Codex CLI 0.156.1 and Claude Code 2.1.289 checks also passed
on Linux, each with 19 actual MCP calls and exit code 0. Independent transcript
and whole-fixture hash audits verified 18/26 catalogs, initial/read-only settings,
partial configuration, chat opt-out and scheduled-channel refusal, chat claim
exclusion of a manual check, notified/already-notified acknowledgement results,
and exactly one Markdown notification emitted after acknowledgement. Readback
confirmed pending revision 1 with notification recorded; the future control
remained byte-identical. Only reminder settings and the due fixture's delivery
state changed. Hosts used temporary launch-only configuration, with Codex per-tool
approval for the three authorized writes and Claude's strict MCP allowlist.
No runtime fix was required. Desktop rendering, scheduled execution and disconnect
during claim writes remain unverified.

### MCP capture requests and suppression

Both profiles expose `tdt_capture_requests` and `tdt_capture_request_read` (20
read-only tools). Everyday adds `tdt_capture_submit` and `tdt_capture_suppress`
(30 tools). Verify existing hook request IDs, saved provenance, pending-only
candidates, discriminated summary/skip input, completed-request replay and exact
status reconciliation before CLI fallback. Check current/stale turn tokens,
independent conversations, shared locks, stack recovery refusal, bounded regular
state files, inventory cursor invalidation and minimum-budget write receipts.
Never derive active conversation identity from inventory order.

Packaged manual verification on 2026-10-06 passed SDK auto and legacy stdio:
20/30 catalogs and output schemas, requested status reads, pagination and
stale cursor refusal, summary/skip, unchanged completed-request replay, retained
candidate bytes during partial-completion reconciliation, secret rejection,
missing request refusal, suppression/repeat/stale token, shared CLI lock and
stack recovery refusal, malformed/oversized/FIFO request refusal. Direct packaged
checks covered strict payload variants, two-session suppression isolation,
malformed/oversized/FIFO suppression state, read-result budgets, symlink refusal
and the 2000-entry scan bound. Existing reminder delivery checks passed both SDK
modes, including catalogs/context, preferences, claims, budgets and acknowledgements.
Dependency and whitespace checks passed. No automated suite added or run.

Synthetic Claude/Codex Stop payloads produced requests, accepted MCP skip, did
not repeat continuation, and retained completed status through CLI fallback.
These are core checks, not live host lifecycle evidence; the later lifecycle
and disconnect checks below cover those paths. Existing hook instructions still
select CLI submission. No saved host configuration or hook registration changed.

Live capture-tool verification on 2026-10-06: Codex CLI 0.156.1 and Claude Code
2.1.289 each exited successfully with 19 actual MCP calls. Independent JSONL
and whole-workspace hash audits passed: 20/30 context catalogs; initial request
inventory and exact reads; stale-token refusal; current-token suppression/repeat;
summary submission, status read before identical retry, and one pending candidate;
skip/read/retry; final statuses and preserved provenance. Only two request files,
one turn-suppression file and one new candidate changed per host. The control
request/session and all other workspace files remained unchanged. No runtime fix
was needed. The lost-response scenario was simulated by reading status before
retry; no actual transport response was dropped. Requests/tokens were produced
by shared hook functions in fixtures, not those live hosts' lifecycle events.
Temporary launch-only MCP settings used the existing signed-in accounts; no
saved registrations changed. No automated suite was added or run.

Real lifecycle verification on the same host versions also passed on 2026-10-06:
four noninteractive runs, capture and suppression for each host, all exit code 0.
Installed SessionStart/UserPromptSubmit/Stop handlers ran from launch-only hook
settings with a transparent logging wrapper. No capture requests or tokens were
preseeded. Actual UserPromptSubmit tokens and Stop request IDs matched MCP calls
and saved provenance. Capture runs each made one context read and one submission,
created one pending candidate, retained the substantive final answer and capture
notice, and ended after the second Stop with `stop_hook_active=true`. Suppression
runs each made one context read and one suppression, saved no request/candidate,
and ended after one nonblocking Stop. Whole-workspace hashes matched exactly the
expected lock/turn/request/candidate files. Codex emitted unrelated state-db
lookup warnings but completed. Per-run instructions explicitly selected MCP over
the hook's CLI wording; default automatic MCP selection is not implemented.

Forced disconnect recovery passed ten disposable SDK stdio cases (five each in
auto/legacy modes). A temporary wrapper paused the installed atomic writer before
candidate save, after candidate save but before request completion, after capture
completion, after skip completion, or after suppression state save. SIGKILL then
terminated that server before a tool response reached the client; every call
failed with MCPError. A fresh unmodified server read saved status and retried.
Incomplete capture reconciled to one candidate without replacing existing bytes;
completed capture/skip/suppression remained replay-safe. Repeating each operation
left hashes unchanged. These checks cover controlled process-death boundaries,
not power loss, every filesystem instruction, or a live model client's automatic
reconnect/fallback. No product fixes or automated suite were needed.

### Hook MCP preference and CLI reconciliation

Enabled request/Stop hooks prefer capture tools on the MCP server bound to their
workspace. Verify exact hook-issued token/request identity, MCP skip versus CLI
skip shapes, and unavailable-tool fallback. For uncertain submission, read the
exact request with MCP or `tdt --workspace <root> brain request <request-id>`:
captured/skipped must end submission, requested allows one identical CLI retry,
and an unreadable status must leave recovery for later. Permission/validation
refusals must not be bypassed. Suppression retries reuse only the current token.

Packaged manual checks passed on Linux for Claude and Codex synthetic lifecycle
payloads: capture/skip via the MCP adapter, exact CLI status reads without writes,
CLI fallback for requested state, partial candidate completion with unchanged
candidate bytes, completed replay with unchanged files, Stop replay/recursion,
MCP suppression followed by same-token CLI retry and stale-token refusal. The
new CLI reader refused missing/malformed/oversized requests, escaping IDs, FIFO
and symlink inputs. A workspace containing spaces and a quote was exercised.
Dependency and whitespace checks passed. These initial checks used manual
fixtures; live host evidence follows.

Live verification passed with Codex CLI 0.156.1 and Claude Code 2.1.289 on Linux.
Ten successful runs covered capture and suppression with both transports
available, unavailable-write-tool CLI fallback using a read-only MCP catalog,
and actual server exits immediately before capture or after saving but before
returning a response. Prompts did not select a transport; current tokens and
requests came from actual UserPromptSubmit and Stop hooks, with no preseeded state.
Both hosts preferred MCP. Codex read exact status through CLI after the dead
transport also refused its MCP read; Claude reconnected and used the MCP reader.
Before-save cases retried the identical summary once through CLI; after-save
cases performed no further mutation, confirmed by complete workspace hashes.

Two additional Claude runs were denied CLI execution by the fixture allowlist.
They left requested state, no candidates, no capture success claim and no
additional retry. Fresh fixtures passed with a temporary PreToolUse approval
restricted to the literal workspace command, same-session requested ID and
validated JSON inside a quoted heredoc. No broad permission bypass was enabled.
Every run exited 0; an independent transcript/hook/state audit verified identities,
pending-only candidates, provenance, empty review history, exactly expected file
changes, preserved substantive answers and nonrecursive Stop completion. No
runtime change was needed. Claude emitted a short recovery commentary in one
denial run despite the hook's internal-only instruction; final answers remained
intact. Codex made some extra guide reads (including a refused context-file guide
lookup) and emitted unrelated state-db warnings without affecting capture.

Launch-only configurations used existing signed-in accounts, reviewed fixture
hooks and per-tool or exact-command permissions. Saved host registrations/settings
were unchanged. These checks used the packaged default SDK transport; earlier
manual auto/legacy disconnect checks remain separate evidence. Power-loss and
arbitrary host failures are not covered.

### MCP candidate review

Both profiles include `tdt_candidate_review_status` (21 read-only tools); everyday
adds `tdt_candidate_review` (32 tools total). Read full proposal/status by exact ID,
show provenance and approval destination, then bind the user's decision to its
`revision` using `expected_sha256`. Editing must retain the previous proposal and
remain pending. A stale approval must refuse; rejection remains outside knowledge
retrieval. Status follows promotion into knowledge even for an unregistered project
whose note is excluded from search. Reading status does not grant eligibility.

After an uncertain response, inspect the saved review history before retrying.
Verify completed approve/reject/edit retries refuse without changes. Interrupt
approval after canonical persistence but before candidate deletion: status must
show `pending_cleanup`; the identical approval must finish without rewriting the
canonical bytes. Changed instructions, conflicting provenance and attempts to edit
or reject during interrupted approval must preserve both files. Check shared CLI
locking, recovery markers, minimum receipt budget, schema/profile restrictions,
malformed/oversized/FIFO/symlink refusal and CLI review compatibility.

Packaged manual verification on Linux passed with MCP SDK auto and legacy modes:
21/32 catalogs and output schemas; approve/edit/reject and stale/repeated-decision
refusal; preserved history and pending edits; approved search; exact status after
promotion including unregistered projects; shared lock and stack recovery refusal;
strict action payloads, secret refusal and 1024-byte write receipts. Injected
candidate-unlink failure exercised partial promotion and byte-preserving recovery,
changed-instruction/edit/reject refusal and canonical-provenance conflict refusal.
CLI rejection, malformed/oversized/FIFO/symlink candidate refusal, dependency and
installed-source parity checks passed. Existing packaged capture/suppression
checks also passed in both SDK modes after updating only expected catalog counts. This is packaged protocol verification and
an injected I/O failure, not a live Codex/Claude review conversation or process-death
verification. No automated test suite was added or run.

Live review verification passed on Linux with Codex CLI 0.156.1 and Claude Code
2.1.289, each exiting 0 after 24 actual MCP calls. Independent transcript and
whole-workspace hash audits confirmed 21/32 catalogs, installed skill retrieval,
current fixture-token suppression, full status reads before decisions, approval
and approved search, rejection, pending edit with previous proposal retained,
stale-hash refusal without another review, and interrupted approval cleanup with
unchanged canonical revision/bytes. The control remained pending with empty
history; only the six expected files changed per host. Both hosts used temporary
launch-only MCP configuration; saved registrations and user workspaces were not
changed. The requests supplied explicit decisions on displayed fixture proposals.
This verified live tool use, not automatic host-hook routing or a multi-turn human
approval exchange. No runtime fixes were needed.

Ten real server SIGKILL checks also passed: before approval persistence, after
canonical persistence, after candidate cleanup, after edit persistence, and after
rejection persistence, each in SDK auto and legacy modes. The client received
MCPError without a result. A fresh unmodified server read exact status before
reconciliation; requested approval completed, partial approval cleanup preserved
canonical bytes, and completed edit/reject/approve duplicate probes refused
without changing files or adding history. Each final note had exactly one review.
These checks cover process termination at those boundaries, not power loss or
live-model automatic reconnection.

### MCP explicit knowledge and scratchpad saves

In disposable workspaces, verify `tdt_knowledge_save` and `tdt_note_save` are
available only in everyday (34 tools; read-only remains 21). Check strict summary
schemas, explicit user instruction, source/secret checks, registered projects,
eligible links and normalized subject tags. Verify approved knowledge has an
approval record and scratchpad has tags with no promotion. Read the saved IDs
through exact review status or scratchpad reads; ordinary knowledge search must
exclude scratchpad. Check 1024-byte receipts, unchanged duplicate retries,
CLI parity, changed identity fields and preservation of original links/audit data.
Refuse concurrent core locks, stack recovery markers, duplicate identities and
malformed/oversized/FIFO/symlink records without writes. Inspect state after an
uncertain response before retrying the identical summary.

Packaged manual verification on Linux passed in SDK auto and legacy modes:
21/34 catalogs, output schemas, profile and invalid-input refusals, explicit save
metadata/readback, sorted unique tags, knowledge/scratchpad search separation,
1024-byte receipts, identical retries with changed instructions/links, distinct
body identities and unchanged CLI retries. Shared lock/recovery marker, missing
project, secret, invalid link/tag, malformed/oversized/FIFO/symlink and duplicate
identity refusals preserved note bytes. An injected exception immediately after
atomic persistence left one saved record; an identical retry returned existing
without changing any saved bytes. This simulates an uncertain response, not
process death or power loss. The installed runtime, command guide and save skills
matched the verified wheel; dependency and whitespace checks passed. Existing
candidate review checks also passed in both
SDK modes with the expanded catalog, including stale decisions and interrupted
approval cleanup. No automated suite added or run.

Live save-tool verification passed on Linux with Codex CLI 0.156.1 and Claude Code
2.1.289, each exiting 0 after 28 actual MCP calls. Independent transcript and
whole-workspace hash audits confirmed 21/34 catalogs, both installed save skills,
fixture current-token suppression, approved and scratchpad saves with correct
provenance/reviews/tags, complete readback before duplicate retries, unchanged
Markdown/revisions with reordered tags or new instruction references, knowledge
search separation and read-before-retry reconciliation of persisted fixtures.
Exactly two new notes and suppression state changed per host; control and recovery
records stayed byte-identical. Temporary launch-only configuration left saved
registrations unchanged. Codex retained a read-only shell and per-tool approvals
only for the fixture save/suppression writes; Claude had no builtin tools, saved
settings or hooks. This verifies live tool use, not automatic skill selection or
an actual host-hook lifecycle. No runtime changes were required.

Eight real SIGKILL disconnect checks also passed: both SDK modes, knowledge and
scratchpad, before atomic persistence and after persistence before response. The
client received MCPError without a result. A fresh unmodified server read exact
state before retry; absent saves produced one record and persisted saves returned
existing without byte changes. A further retry preserved the same record and one
knowledge approval or zero scratchpad reviews. Process termination is verified;
power loss and live-model automatic reconnection are not.

### MCP project registration

Everyday exposes `tdt_project_add` for an absolute existing directory and
`tdt_project_create` for a relative folder below work/. Read-only retains 21 tools;
everyday now has 36. Confirm explicit user intent and WORK.md placement before
creation. Both receipts contain only id/result and fit the minimum result budget;
read registration facts through project read. Source inspection and onboarding
proposals remain CLI operations. Registration never edits external project files.

Packaged manual verification on Linux passed in SDK auto and legacy modes:
output schemas, profile/input refusals, external registration, internal creation,
1024-byte receipts, read-only readback, identical retries and CLI duplicate parity.
Invalid/reserved/traversal/symlink paths, archived records, lock contention and
pending recovery refused. Malformed, oversized, FIFO and symlink registries/notes
and duplicate note identities refused without changing workspace file contents.
Create under lock/recovery/invalid registry did not create the requested directory.
External fixture files remained byte-identical.

Injected I/O failures before note persistence, after note persistence and after
registry persistence covered both operations in both modes. Read-before-retry and
identical retries finished registration, preserving existing note bytes and a
single identity. Further retries changed no file contents. Additional direct-core
checks preserved user files, refused recreating a missing archived folder, and
preserved conflicting partial registration notes and registry bytes.
Runtime, command guide and add-project skill matched the installed wheel;
package dependencies and whitespace checks passed. No automated suite added/run.
Live verification also passed with Codex CLI 0.156.1 and Claude Code 2.1.289:
30 actual MCP calls per host, both exit 0. Independent transcript audits confirmed
21/36 catalogs, installed add-project skill reads, external registration, internal
creation, complete readback before duplicate retries, partial-registration recovery,
completed replay and expected archived/traversal/relative-path refusals. Whole-workspace
hash audits found exactly two new registration notes and the updated registry;
preexisting partial/control/completed/archived notes and user files were unchanged.
External source fixture files remained byte-identical. These runs used temporary
launch-only configuration and explicit fixture instructions; automatic skill choice
and a real host-hook lifecycle were not exercised. Codex recovered from a model-service
stream interruption; this was not an MCP transport failure.

Fourteen actual SIGKILL checks passed across SDK auto/legacy: add before/after note
persistence and after registry persistence; create at those boundaries plus after
directory creation. A parent killed only the disposable fault-wrapper server after
its persistence marker. The client received MCPError without a result. Fresh
unmodified servers read exact registration state before identical retries; every
case ended with one note and one registry row, preserving any prior note bytes.
Completed retries changed no files, and external sources stayed unchanged. This
verifies process-death recovery, not power loss or live-model automatic reconnection.
A created folder can remain after a later write failure; inspect the location and
registration before retrying rather than relocating it.
### MCP project inspection and onboarding proposals

Use a packaged installation and disposable internal/external projects. Verify
the 22-tool read-only and 38-tool everyday catalogs with both SDK auto and legacy
modes. Inspection is available in both; proposals are everyday-only. Validate
structured results against catalog schemas and refuse unknown fields, invalid
IDs, wrong types and insufficient result budgets without changing files.

Inspect only the explicitly selected active registered project. Check the 100-name
top-level inventory and ten allowlisted documents with 4 KiB content bounds,
including a UTF-8 character split at the bound. Check exact source paths, retained
project link, complete omission reasons, and inventory/content coverage flags.
Refuse archived, missing and replaced-by-symlink project locations. Omit symlink
documents/parent directories, FIFOs, invalid UTF-8, possible secrets and missing
files without reading outside the selected project or executing source content.
Compare CLI inspection and confirm source/control hashes remain unchanged.

Submit an inference with sources and the inspected project link. Confirm a pending
candidate with project provenance and no review, exact readback and CLI parity.
Identical retries must preserve bytes before and after edits, rejection and
approval. Refuse project mismatch, malformed/oversized/symlink/special-file notes,
duplicate identities, conflicting provenance, lock contention and recovery state.
Inject failures before/after candidate persistence; inspect saved state before
retrying and retain one candidate. During interrupted approval, proposal replay
must refuse until the exact review recovery resolves the dual-store state; do not
rewrite the already saved canonical content.

Packaged manual verification on Linux passed both SDK modes, with 46 onboarding
calls per mode and schema checks for every response. It covered bounded inspection,
omissions, strict inputs/profile restrictions, minimum proposal receipt budget,
CLI parity, review-state preservation, lock/recovery refusals, unsafe locations,
malformed and conflicting records, and injected pre/post-persistence failures.
External source and outside-control hashes stayed unchanged. Registration/create
regression checks also passed both modes after the shared project changes.
Additional direct checks verified interrupted-approval refusal and exact recovery
with unchanged canonical bytes, plus corrupt registry/registration-note refusals.
The built wheel matched changed runtime, command guide and add-project skill;
dependency and whitespace checks passed. These checks do not establish live model
tool/skill selection, actual server-kill recovery or power-loss durability for
project proposals. No automated suite was added or run.

Live onboarding verification also passed on Linux with Codex CLI 0.156.1 and
Claude Code 2.1.289: 36 actual MCP calls per host, both exit code 0. Independent
transcript/schema and whole-workspace hash audits confirmed 22/38 tool catalogs,
the installed add-project skill read, external registration and bounded inspection,
internal inspection, evidence-cited onboarding explanations and two new pending
inference proposals. Identical retries followed exact status reads and preserved
Markdown/revisions. Preseeded completed, approved and rejected proposal replays
retained their content and histories. Four intended refusals covered archived and
missing locations, insufficient inspection budget and a mismatched summary project.
Pending proposals stayed outside approved search. Exactly the new registration
note, registry and two candidate notes changed; all prior records, user files,
external source and outside controls remained unchanged. No runtime fixes needed.

Runs used disposable workspaces and temporary launch-only MCP configurations.
Codex used ephemeral execution, ignored user config, a read-only shell sandbox
and per-tool approval overrides for the two authorized writes. Claude used strict
MCP configuration without builtin tools, settings sources, hooks or session
persistence. Only the intended MCP tools were called. Codex emitted unrelated
state-db and file-watcher warnings; Claude stderr was empty. This verifies live
tool use, not automatic skill routing or an actual host-hook lifecycle.

Ten actual SIGKILL checks passed across SDK auto and legacy modes: internal and
external proposals before/after atomic persistence, plus interrupted approval after
canonical persistence in each mode. The parent killed only the disposable fault
server after its exact boundary marker; the client received MCPError without a
result. Fresh unmodified servers read exact status/inventory before retry. Missing
proposals produced one pending candidate; completed proposals returned existing
without rewriting bytes. Interrupted approvals refused proposal replay until the
identical original review completed cleanup, preserving canonical content/revision
and one approval record. Further proposal replay returned existing. Controls and
project source stayed unchanged. This proves process-death recovery at those
boundaries, not power-loss durability or live-model automatic reconnection.

## MCP working-file and scratchpad discovery

From a packaged installation, verify the 26 read-only / 42 everyday catalogs in
SDK auto and legacy modes. All four discovery tools must be read-only in both
profiles and return schema-valid structured results with matching MCP error state.

- Search scratchpad title/body/tags with literal phrases; paginate results and
  read selected full notes. Related notes must exclude the selected ID, show
  shared tags and sort by shared-tag count then path. Compare CLI matching and
  ranking. Changed inventory, query, limit or operation must invalidate cursors.
  Refuse unknown/duplicate related IDs; report malformed-note omissions. Keep
  candidates and approved knowledge separate from scratchpad discovery.
- Search working filenames and supported text with multiple literal words, then
  read workspace-relative paths and returned URIs. Compare CLI discovery. Report
  filename-only matches for unsupported extensions without exposing their bytes.
  Preserve UTF-8 at the 32 KiB boundary and label prefix revisions/truncation.
  Report truncated searchable text even when the query returns no matches.
- Refuse traversal, absolute and foreign-workspace references, hidden files,
  symlink parents/files, special files, binary/invalid UTF-8 and possible-secret
  text. Exclude dedicated stores and nested current/legacy workspaces. Verify
  scan and depth limits separately from result limits and budget refusals.
- Compare complete fixture hashes before/after reads, including outside-source
  controls. Check missing work directories, conflicting files and symlink work
  roots. Swap a parent for a symlink between discovery and opening; search must
  omit it and direct reads must refuse without following the replacement.

Verified 2026-10-06 on Linux with the packaged wheel: auto and legacy SDK stdio
modes each passed 51 calls, including output schemas, both catalogs/context,
read-only annotations, pagination/ranking/CLI parity, stale and invalid cursors,
malformed-note omissions, duplicate/unknown ID refusals, all working-file refusal
cases above, minimum-budget refusal, 2000-entry and 32-level limits, and whole
fixture/outside-source preservation during reads. Additional direct checks passed
missing/conflicting/symlink work-root handling and parent-directory swap refusal.
Installed changed runtime/guide/skill bytes matched source; dependency and
whitespace checks passed. The manual probe initially tried to create a note while
its deliberate malformed-note fixture remained; removing that fixture before the
mutation phase corrected the probe. No runtime correction was needed by the run.
Sandbox stdio discovery timed out; bounded execution outside the sandbox passed.
These are actual SDK transport checks, not live-model tool or skill selection.
No automatic suite was added or run.

Live discovery verified 2026-10-06 using Codex CLI 0.156.1 and Claude Code
2.1.289, each exiting successfully after 29 actual MCP calls. Independent
transcript/schema audits confirmed 26/42 catalogs, both installed discovery skill
reads, complete three-page scratchpad search and full-note reads, two-page
shared-tag ranking, matching everyday/read-only discovery, current working-file
reads by path and URI, filename-only image discovery, and distinct result/text
truncation reporting. The UTF-8 prefix excluded a split multibyte character; a
query for unread tail content returned no matches with explicit truncation.
All eight expected refusals passed: traversal, foreign URI, symlink, FIFO,
possible-secret text, nested workspace, insufficient result budget and a cursor
reused with another query. Approved search excluded scratchpad evidence.
Both hosts cited the evidence, retained tentative/unapproved status and disregarded
the working-file embedded instruction. Whole workspace and outside-control hashes
were unchanged; only read MCP tools were called. No runtime fixes were needed.

Temporary launch-only configurations used existing signed-in accounts: Codex
ignore-user-config/ephemeral with read-only shell, and Claude strict MCP with no
builtin tools, settings sources, hooks or session persistence. Saved MCP
registrations were not changed. Codex emitted unrelated state-db warnings;
Claude stderr was empty. This verifies live MCP usage with explicitly requested
skill reads, not automatic native skill routing or host-hook lifecycle.

## MCP installed stacks and provider discovery

In a disposable packaged installation, check `tdt_search_providers`,
`tdt_stack_list` and `tdt_stack_docs` in both profiles. Expect 29 read-only and
45 everyday tools. Validate output schemas, read-only annotations, pagination,
profile equivalence and cursor rejection after inventory/selection changes.
Compare provider metadata with `tdt brain providers`; discovery must not execute
entrypoints, check assets, create caches or fetch sources. Missing trust/origin
hashes must not count as trusted. Recorded trust does not establish runtime
readiness. Read declared docs through `tdt_guide_read`, matching their revisions.

Refuse malformed/duplicate registry records, registry files above 1 MiB,
symlink/special-file registry paths, interrupted stack/skill operations, unsafe
or oversized documents and results exceeding requested budgets. Preserve workspace
and outside-control bytes during reads. Check empty catalogs and existing guide
and skill discovery after the shared registry-reader change. No automated tests.

Packaged manual verification passed on Linux with MCP SDK auto and legacy modes,
49 calls each: schema/annotation checks, 29/45 catalogs, pagination and profile
parity, stale/invalid cursors, CLI/core provider parity, recorded-trust correction,
full guide reads, malformed metadata, duplicate registry IDs, recovery markers,
registry size/symlink/FIFO refusals, document symlink/size refusals and result
budgets. Discovery succeeded with absent provider entrypoints, without executing
or checking assets. Read-phase workspace hashes and outside controls were
unchanged. Separate packaged checks passed empty catalogs and core guide/skill
regression. Installed source/resource parity, dependency checks and diff whitespace
passed. No live-model selection or provider execution was exercised.


## MCP explicitly selected provider search

In a disposable workspace install a reviewed trusted search provider and save
approved fixture evidence. Verify everyday `tdt_brain_search_providers` requires
1–8 distinct provider IDs, while read-only excludes it and literal search has no
provider argument. Check non-read-only, non-idempotent and open-world annotations.
A query without an index must refuse without creating one. After explicit CLI/core
indexing, compare evidence with shared core search and hash the workspace/index
before and after queries. Check missing/duplicate/unsafe provider input, unknown
providers, missing trust, altered assets, recovery markers, oversized registry,
result budgets and deleted notes against a stale index. Provider failures must not
silently become literal-only success.

Verified 2026-10-06 on the packaged wheel with the local SQLite provider. Actual
SDK auto and legacy each passed 16 calls with output schema validation, 29/46
catalogs, annotation/input checks, core result parity and the refusals above.
Query-phase workspace/index hashes were unchanged. Deleting fixture evidence
excluded it from subsequent search without rebuilding. Changed shipped files
matched the installed wheel and pip dependency checks passed. These are bounded
manual checks, not live-model selection, OS/network isolation, interruption or
malicious-provider containment evidence. No host settings were changed.

## MCP adapter package organization

For the domain-module split, compare both complete ordered tool catalogs with a
pre-change baseline, including descriptions, input/output schemas and annotations.
Check that prior model, helper and operation imports remain available from
`thisdamnthing.mcp_tools`. Build and install a wheel, verify every package module
matches source, and exclude a stale `mcp_tools.py` from the distribution. Exercise
representative reads and writes through actual stdio in both SDK modes, including
refusals, budgets, retry behavior and cancellation serialization.

Verified 2026-10-06: both catalogs remained exactly equal (29 read-only / 46
everyday). All class and function bodies matched the original syntax trees,
apart from the deferred context/catalog import. All 13 package files matched the
installed wheel; dependency and whitespace checks passed. Eight existing
disposable manual probes passed with SDK auto and legacy: working-file/scratchpad
discovery, capture, reminder delivery, project onboarding, selected provider
search, candidate review, explicit saves and stack/document discovery. Historical
catalog-size assertions were updated to the current counts. The separate held
worker cancellation probe passed read concurrency, busy-write refusal and lock
retention until worker completion. No automated suite or live-model verification
was performed, and no host configuration changed.

## MCP structural brain audit

Check `tdt_brain_audit` in both profiles and SDK modes. Page both findings and
note hashes and compare complete results with `tdt brain audit`. Verify totals,
limitations, unreadable-note omissions on every page and read-only annotations.
Changed report content, section and page limit must invalidate cursors. Invalid
arguments and insufficient result budgets must refuse rather than return a
partial successful page. Check malformed/oversized/invalid-UTF-8 notes, special
files, symlinks, interrupted transactions, shared-lock contention and scan bounds.
An empty findings page does not establish semantic correctness. Preserve workspace
content and outside control files; repair remains a separate CLI operation.

Packaged manual verification passed on Linux in SDK auto and legacy modes for
both read-only and everyday profiles: 21 calls per combination, schema-valid
results, complete CLI/core parity, cursor and input refusals, budget refusal,
unreadable-note coverage, FIFO/symlink handling, recovery and lock refusals.
Workspace content hashes and outside controls were unchanged. Catalogs contain
30/55 tools; prior tool schemas, descriptions and relative order are unchanged.
Separate checks passed empty audits, note FIFOs, the 2001-entry refusal, CRLF
normalization and CLI-core repair preview/apply with a retained backup. All 97
packaged files matched source and installation; dependency checks passed.
This verifies the packaged SDK tools, not live-model maintenance skill routing.

## MCP UI lifecycle

Verify all eight UI tools in the everyday catalog and their absence from read-only.
Verify guide discovery includes `core/ui` and `core/contracts/ui`; read complete
installed bytes by ID, path and workspace URI, with arbitrary paths and symlinks refused.
Check status/read/wait annotations and that a pending wait permits unrelated reads
and mutations. Present standard and custom page objects, reject invalid pages,
stale rounds and invalid cursors, and preserve false/zero answers. Verify complete
original prompts, event pagination, large-event budget refusal/recovery and no
implicit acknowledgement. Compare CLI and MCP lifecycle results. Close must retain
answers; offline reads/acks must work; cleanup must refuse live sessions, symlinks
and unexpected files. Compare unrelated workspace files before/after. Verify actual
browser submissions and the active wait loop with each live host separately from
SDK/HTTP checks; SDK success alone does not establish automatic skill routing.

Verified 2026-10-06 with live Codex CLI and Claude Code on the corrected packaged
wheel: each completed 29 actual MCP calls. Actual in-app browser interactions
rejected blank required submissions, retained drafts across refresh (including
false and zero), submitted a grouped form, submitted the sandboxed custom
follow-up, and cancelled a third round. Each host continued bounded waits after
three timeouts, reread complete events with their original prompts, paged from
the first event to the second, acknowledged only submitted events, and retained
all three after close/disconnection. A separate empty session was closed and
cleaned up. Independent output-schema/transcript and file-hash audits passed;
only session state changed, and the instruction-like comment caused no knowledge
write. The live run exposed missing UI documents in MCP discovery; the corrected
catalog includes the separately installed UI guide and contract. ID/path/URI
reads matched installed bytes in both profiles, with arbitrary-path and symlink
refusals. All packaged files matched source and installation. Launch-only host
configurations were used; no saved host settings changed. Explicitly requested
skill reads do not prove automatic native routing. Crash recovery, power loss,
and browser-driven wakeup of a stopped agent were not exercised by this run.


## MCP repair previews — 2026-10-06

Both profiles expose `tdt_brain_repair_preview` (31 read-only / 56 everyday).
Check exact shared-core replacement/fingerprint parity, read-only annotations,
strict changes schema, stale hashes, duplicate paths, escaping paths, missing
link targets and result-budget refusal without writes. Compare all workspace
file hashes before/after previews, excluding the shared lock file. Apply the
identical proposal through the shared CLI core with the returned fingerprint;
verify the retained backup and protected metadata.

Source verification passed 40 actual SDK calls across auto/legacy and both
profiles in disposable workspaces, including every check above. The exact
preview fingerprint was accepted by shared core apply and protected metadata
was preserved. Sandbox discovery timed out; the bounded outside-sandbox probe
passed. Follow-up packaged verification also passed all 40 SDK calls in a fresh
virtual environment, actual CLI preview/apply parity with retained backup and
protected metadata, pip check, and byte equality of all 97 packaged files with
source and installation. Boundary checks passed index previews, schema limits,
symlink and interrupted-transaction refusals, and complete 20-note responses
with a raised budget (default budget refuses without writes). Existing tool
schemas and relative order are unchanged; only the audit description changed.
No live-model routing verification. Apply and retained-outcome reconciliation
were verified separately in the following slice.


## MCP repair apply and retained outcomes — 2026-10-06

Both profiles expose `tdt_brain_repair_status`; everyday adds
`tdt_brain_repair_apply` (32 read-only / 58 everyday). Apply requires the exact
preview hash, identical changes and actual approval instruction/reference.
Check unknown/prepared/completed/recovery_required states, strict schemas,
profile boundaries, a completion receipt within the minimum 1024-byte budget,
and identical retries after later user edits. Changed request content or approval
context must refuse a retained hash. Completion is historical, not current-note
verification. Older UUID backups remain intact and are not indexed.

Interrupt a disposable apply after writing notes and the completion record but
before removing the journal. Status must report recovery_required and apply must
refuse. Shared CLI-core recovery must restore original notes and prepared state;
an identical retry must complete. Also inject a handled write failure and check
rollback. Refuse symlink, FIFO, oversized, malformed and invalid UTF-8 outcome
records; preserve outside control files. Exercise a 20-note Unicode batch and
shared-lock contention. Do not infer power-loss guarantees from these probes.

Source and packaged verification passed 28 SDK calls each across auto/legacy
and both profiles. The packaged preview regression passed a further 40 calls,
including stale/escaping/duplicate input, link and result-budget refusals with
unchanged workspace hashes. Direct core and actual CLI checks passed retained
outcome parity, metadata preservation, uncertain-response retries, changed
approval refusal, simulated interruption/recovery and handled failure/rollback.
Outcome record boundaries passed. A 20-note Unicode batch retained a roughly
1-MiB backup and returned a 344-byte receipt; retry and lock refusals passed.
All 97 packaged files matched source and installed bytes; dependency and
whitespace checks passed. Existing schemas/relative order are unchanged; only
audit/preview descriptions changed. Build dependency access and bounded local
SDK runs used approved outside-sandbox execution after sandbox network/discovery
failures. No automated tests added, live-model routing verification, host setting
changes, staging, commit or push.


Live MCP routing follow-up passed on Linux with Codex CLI 0.156.1 and Claude
Code 2.1.289. Task-level prompts asked each model to select the installed
maintenance workflow and its tool sequence; no prescribed repair API sequence
was supplied. Final runs exited 0 with 24 Codex / 25 Claude MCP calls. Both
selected the skill through MCP discovery, suppressed the supplied fixture turn,
read current notes, previewed and applied exactly the authorized replacement,
and completed both sections of the before/after audit. Retained history was
reconciled without retry; a later user edit, stale approval, legacy operation
and instruction-like control content were preserved. Both correctly described
unknown legacy outcome as uncertainty, not proof that it never ran. Only the
approved note, its retained backup and the suppression record changed.

Live verification exposed and corrected two issues: unknown-outcome guidance
needed to explicitly exclude “never ran” conclusions, and parallel maintenance
reads contended for an exclusive lock. Audit, preview and status now use shared
read locks; apply and all existing default lock users remain exclusive. Source
and packaged auto/legacy SDK probes each passed 36 calls under held shared and
exclusive locks, admitting concurrent reads while refusing conflicting writes.
The final packaged direct CLI/core rollback, retry and record-boundary probe
also passed. All 97 wheel files match source and installation; dependency and
whitespace checks passed. Codex recovered from a refused oversized skill-list
limit; both hosts respected the approved-note reader's index refusal and reported
that semantic-coverage limitation. No maintenance lock-contention errors remained.

This verifies model-selected MCP discovery/routing, not native slash/skill-picker
activation. Suppression context was issued by the real core function for a
fixture; live host hooks were disabled. Uncertain responses were pre-seeded,
not actual network disconnects. Saved host configuration was unchanged. No
staging, commit or push was performed.

## MCP project reference discovery

Verify `tdt_project_references` in both profiles with an exact project ID. Page
both references and skipped entries and compare the combined rows with shared
core/CLI output. Every page must retain totals, limitations and scan truncation;
coverage must flag skipped entries and direct the caller to their detail pages.
Changing the scan report, section or page size must invalidate old cursors.
Check archived, restored and retained removed registrations, invalid IDs/fields,
small-budget refusal, symlink/FIFO/invalid UTF-8/oversized-file skips, scan caps,
transaction markers and shared versus exclusive brain locks. Preserve external
source and all workspace content during reads.

Packaged manual verification passed on Linux: MCP SDK auto and legacy modes,
both profiles, 15 calls per combination. Output schemas and read-only/idempotent
annotations passed; all reference/skipped pages matched CLI/core. Stale section
and changed-content cursors, invalid inputs, budget and transaction refusals,
shared-read coexistence and exclusive-lock exclusion passed. Separate core
lifecycle changes verified archived/restored/removed reads; a 5001-entry directory
set both scan and envelope truncation. FIFO, symlink, malformed UTF-8, oversized
and unsupported files were skipped. Workspace hashes were unchanged by SDK reads
and external control content was preserved. All 97 packaged files matched source
and installed bytes; dependency and whitespace checks passed. No live-model
routing verification or automated tests were performed.

Follow-up verification repeated all 60 packaged SDK calls successfully. Additional
checks passed page-size/project/omission-change cursor invalidation, malformed
cursors, Unicode matches, hidden-file/directory exclusion, missing-source reads
and lifecycle writer refusal under a shared read lock. Existing catalog schemas,
descriptions and relative ordering matched HEAD in both profiles. Source, wheel
and installed file sets and bytes matched exactly (97 files). No runtime fixes
were required; live-model routing remains unverified.

## MCP project lifecycle previews

Both profiles expose archive/unregister, restore and relink previews. Verify exact
registered IDs and explicit removal modes; relink requires an absolute existing
directory without traversal. Compare complete replacements and proposal hashes
against shared CLI/core output (optional absent registration status becomes null
in MCP). Apply the preview through CLI with the identical inputs and hash; stale
state must refuse. Preserve archive state across relink and permit restore with
missing source. Unregistered entries cannot be restored through this operation.

Packaged manual verification passed on Linux with SDK auto/legacy × both profiles:
148 calls checked catalog/schema/annotations, repeat parity, concurrent shared
read locks, exclusive-lock and transaction-marker refusal, strict inputs,
missing targets and result-budget refusal. Fixture file hashes were unchanged
across previews. CLI accepted MCP hashes for archive, relink, restore and
unregister; a stale relink hash refused. Separate source and packaged checks
passed destination collisions, complete Unicode output at increased budget and
registration-note symlink refusal with outside control preserved. All 97 packaged
files match source and installation; dependency and whitespace checks passed.
Existing tool schemas, descriptions and relative order are unchanged.

No live-model routing check performed. Lifecycle apply and reference cleanup
remain CLI-only; retained lifecycle outcome reconciliation is not implemented.

## MCP project lifecycle apply and retained outcomes — 2026-10-06

In disposable workspaces, verify `tdt_project_operation_status` in both profiles
and everyday-only remove, restore and relink apply tools. Apply with identical
preview inputs, exact proposal hash and actual instruction/reference. Check
explicit archive/unregister modes, exact IDs, absolute destinations, strict
schemas, annotations, minimum result budget and shared core/CLI parity.

After an uncertain apply, read the exact hash before retry or CLI fallback.
Completed outcomes are historical: restore an archived project, relink it, change
its note, remove the destination directory and unregister it, then verify earlier
identical retries leave current files unchanged. Changed input or instruction for
that hash must refuse. Legacy UUID backups are not indexed; unknown does not prove
an operation never ran. Reference cleanup keeps its existing CLI-only workflow.

Simulate interruption after completion record write but before journal removal.
Status must report recovery_required; applies refuse pending recovery. Shared CLI
rollback must restore registry/notes and prepared outcome. Inspect before identical
retry. Verify handled write errors also restore prepared state, and a skill journal
overrides retained completion. Shared read locks permit status/preview reads;
exclusive locks refuse competing calls, including historical apply retries.

Check malformed, oversized, invalid UTF-8, FIFO and symlink records without changes
to an outside control. Verify stale preview refusal before a backup is written,
complete before/after backups, archive preservation through relink, Unicode byte
limits, and a lifecycle backup above 8 MiB refused before any write. A large
accepted backup must remain readable through a small receipt.

Source and packaged manual checks passed on Linux. Both SDK auto and legacy modes,
with read-only and everyday profiles, passed 126 calls per artifact (11 read-only
and 52 everyday per mode). Catalogs have 37 / 66 tools; existing input/output
schemas and relative order were preserved, with only three lifecycle preview
descriptions updated. Packaged CLI/core checks passed historical retries after
unregister/relink, later-edit preservation, changed inputs/instruction, simulated
interruption and recovery, handled failure, shared/exclusive locks and record
boundaries. A 1,218,705-byte Unicode backup returned a 450-byte receipt; oversized
backup refusal preserved all workspace file hashes. CLI reference cleanup with
UUID backups still passed. All 97 source/wheel/installed files matched, dependency
and whitespace checks passed. No automated tests or live-model routing checks;
no real power-loss guarantee, saved host settings, staging, commit or push.

Live routing follow-up passed on Linux with Codex CLI 0.156.1 and Claude Code
2.1.289. Both discovered and read the installed removal/relink workflows through
MCP from task-level instructions, choosing their own tools and sequence. Codex
made 55 actual MCP calls and Claude 36; both exited 0. Each applied exactly four
reviewed operations with the preview hash and supplied instruction: archive,
restore with missing source, relink preserving archive state, and unregister.

Independent transcript/schema and full-file hash audits confirmed complete
preview replacements, sequential before/after backups, retained completed
outcomes, stable note links, updated structured project/source references and
preserved prose. Both reconciled historical relink/unregister outcomes without
retry, distinguished legacy unknown from proof of non-execution, and left the
stale approval unapplied. Later edits, the control project, working references,
unrelated files and every external source file stayed unchanged. Only the shared
registry, four registration notes, associated knowledge metadata, four outcome
backups and current-turn suppression record changed in each workspace.

Both paged reference and skipped sections after relink/unregister and reported
scan limits. Existing removed-project note read exclusions were encountered and
reported; reference discovery remained available. Codex corrected one invalid
skill-list limit after schema refusal. No lock contention occurred. The injected
instruction in a project note caused no unrelated removal, saves or promotions.
Historical uncertainty was pre-seeded, not an actual network disconnect.

Runs used existing sign-ins, disposable workspaces and temporary launch-only MCP
configuration. Codex used ignore-user-config, ephemeral state, read-only shell and
approval overrides for the exact lifecycle writes/suppression; Claude used strict
MCP configuration without builtin tools, settings sources, hooks or session
persistence. Codex state-database warnings did not affect results; Claude stderr
was empty. This verifies live MCP workflow/tool selection, not native slash or
skill-picker activation. No runtime changes were needed; no saved host settings,
automated tests, staging, commit or push.
