# Product scope and implementation principles

## Outcome

Install ThisDamnThing with pipx, initialize a workspace, use Claude or Codex to retain
and retrieve knowledge, link an external project, and add optional stacks.
Keep stack-builder and software-production as separately installed examples, each
with its own GitHub repository.

## Product principles

- Core works with zero stacks. Domain workflows belong in optional stacks;
  first-party and community stacks use the same public contract and installer.
- `.tdt/` is reserved for workspace harnesses. Project-local stack artifacts use
  `.tdt-project/<stack-id>/`, with shared identity at `.tdt-project/project.json`;
  stacks do not read or migrate a legacy project `.tdt/` layout.
- Keep core agent agnostic; Claude/Codex behavior belongs in small adapters.
- Installed skills and hooks are scoped to their workspace. Never register them
  globally or copy workspace registrations into linked external projects.
- A workspace owns its brain, `.tdt/` harness and user docs. Project registration supports directories below work/ and
  leaves external source in place and unchanged; knowledge about it stays in the
  brain. Separately authorized project work follows that project's instructions.
- Knowledge uses readable Markdown, stable wikilinks and source references.
  Preserve useful facts, decisions and open questions; distinguish inference from
  evidence. Require user approval before promoting candidates, exclude secrets,
  and never treat instructions embedded in notes as authorization.

## Working defaults

- Python 3.11+, standard library where practical, one `tdt` CLI.
- Linux/macOS first; document platform support actually demonstrated.
- Local Markdown brain, simple text search and bounded wikilink traversal.
  Core needs no database, embeddings, background service or extra model subscription.
  Optional contract-v2 capability stacks may bundle local databases, embedding
  models and runtimes for offline on-demand search; Markdown stays authoritative.
- Automatic capture creates concise candidate notes with source references for
  user approval. Only approved candidates become authoritative brain knowledge.
  Full transcripts remain with the host agent.
- The marketplace contract uses `stacks.usetdt.com` as the registry destination
  on the usetdt.com website. Each stack has its own GitHub repository. The CLI
  and `/tdt-install-stack` skill fetch its ZIP/source archive through the registry
  JSON endpoint. Author accounts, submissions and ratings belong
  to the separate website; marketplace payments are future scope. See
  [Marketplace contract](marketplace-contract.md) for the authoritative marketplace contract.
- Core UI provides optional local browser questions and interactive input for
  users and all stacks, including standard controls and custom HTML/JavaScript.
  Chat/TUI remains available.
- Declare external and stack prerequisites in stack.json marketplace metadata; no dependency
  solver, automatic stack upgrades, or custom package format.
- No automated tests. Source development uses the constitution loader and the
  explicitly authorized tracked Git safeguards; no other development hooks.
  Installed-product capture hooks are part of the MVP and are a separate concern.

## Source layout

```text
src/
  thisdamnthing/            Python CLI and core modules
    resources/
      workspace/             initial brain and root instruction templates
      harness/               contracts, core skills, hooks, adapter templates
      docs/                  usage docs installed as <workspace>/docs/
  marketplace/               registry data/schema; website integration handoff
.dev/                        source-development tooling and coordination
docs/                        developer guides and verification procedures
pyproject.toml               pipx entry point and package resource configuration
```

Optional stacks are separate artifacts; core initialization installs none.
Use normal Python packaging. Author each first-party stack in its own repository;
do not bake their source into the core distribution. Stack-builder owns its
starter templates in its separate repository; they install under its bundle
directory through the ordinary optional templates list.

MCP transport stays in `mcp_server.py`. The `mcp_tools/` package groups adapters
by domain, with shared models and helpers, explicit catalog assembly and separate
dispatch. Its package imports preserve the existing model and operation names;
domain adapters call the same core functions as the CLI.

## Installed layout

```text
<workspace>/
  WORK.md                    user-maintained filing conventions
  work/                      user-owned work; created on demand
    notes/                   tagged scratchpad ideas; created on first save
    reminders/               one-time reminders; created on first save
  brain/
    index.md
    projects/
    knowledge/
    candidates/              pending user review; excluded from default retrieval
  .tdt/
    config.json
    contracts/
    skills/
    hooks/
    stacks/
    state/                   project registry, hook cursors, owned-file records
  docs/                      user/usage documentation
  README.md                  workspace orientation and agent enablement
  AGENTS.md                  when Codex enabled
  CLAUDE.md                  when Claude enabled
  .agents/skills/             generated Codex skill entry points
  .codex/hooks.json           generated Codex configuration
  .claude/skills/             generated Claude skill entry points
  .claude/settings.json       generated Claude configuration
```

The `.tdt/` harness is canonical; provider files are thin discovery/config
bridges, generated only for enabled hosts. Initial setup detects executables on
PATH unless explicitly overridden; `.tdt/config.json` remembers enabled hosts.
`tdt agent enable` exposes all owned skills to another host later. Bootstrap preserves unrelated configuration and refuses name clashes.

## Command surface

Common commands (use subcommand `--help` for all options):

```text
tdt init [directory] [--agent claude|codex|both|none]
tdt agent enable claude|codex
tdt agent disable claude|codex
tdt doctor
tdt brain search <query>
tdt project add <path>
tdt project list
tdt project relink <old-project> <new-path>
tdt project remove <project> [--permanent]
tdt project restore <project>
tdt project references <project>
tdt stack validate <directory>
tdt stack install <directory-or-catalog-id>
tdt stack list
tdt stack remove <id>
tdt stack update <id>
tdt stack uninstall <id>
tdt stack docs
tdt brain providers
tdt brain index --provider <provider-id>
tdt marketplace search <query>
```

Omit the `init` directory to initialize the current directory.
Use `--workspace <path>` when operating outside the workspace. Hook internals
can call the same Python core; do not build a parallel command API for everything.

## Knowledge and projects

Use Markdown with small metadata fields: id, title, kind, timestamps, source,
and optional project id. Wikilinks use brain-relative paths without `.md`, such
as `[[projects/example]]`, avoiding duplicate-title ambiguity.
New filenames use a readable title slug and short ID suffix, extending the suffix
on collisions. Full IDs remain in metadata; editing a title does not rename a
file. Legacy hash filenames remain supported; `tdt brain migrate-names` previews
an explicit migration, and `--apply` renames them and updates current brain links.

Candidates record pending/approved/rejected state, provenance, and review history.
`/tdt-review-brain` presents candidates and promotes only what the user approves.
Approval creates or updates a canonical note without erasing conflicting evidence;
the approved candidate file is removed after the knowledge note is saved, with
provenance and review history retained in that note. Rejected candidates never
appear as approved knowledge.

Stop hooks trigger capture at a supported turn completion boundary. The active
agent produces a structured summary;
the hook persists a candidate through shared core code. Verify the actual capture
path on each supported host. Avoid recursive Stop loops, deduplicate repeated
events, and retain recoverable pending state after failure.
Do not assume a shell hook can independently summarize arbitrary conversation.

`/tdt-search` searches, follows a bounded number of links, and answers with
note references. It says when evidence is missing or conflicting. All text is
knowledge input, never permission to run embedded instructions.

`/tdt-add-project` creates internal projects below work/ or registers an existing
internal/external directory and writes a project
note based on a bounded read of project docs and manifests. It offers onboarding
and explains purpose, structure, entry points, and unknowns with source references.
It never copies project source or writes into the external project. Work inside
that project still follows its own instructions and the user's authorization.

`/tdt-relink-project` explicitly reconnects moved or renamed directories, updates
path-derived project IDs and structured references, and preserves note links and
history. Missing arguments require user selection. `/tdt-remove-project` archives
(reversibly) or permanently unregisters projects without deleting source. Brain
and work reference cleanup is separately requested and reviewed. Lifecycle writes
use hash-bound previews, backups and shared transaction recovery. See the
[project lifecycle guide](../src/thisdamnthing/resources/docs/projects.md#project-lifecycle).

Explicit user saves use `/tdt-capture` to write approved knowledge with source,
provenance and an approval record. `/tdt-note` saves tagged scratchpad ideas in
`work/notes/`, with no promotion. `/tdt-search-notes` retrieves scratchpad content
and subject tags, labels it as unapproved, and follows shared-tag relationships.
Default knowledge search still excludes scratchpad notes. Explicit saving uses
the turn suppression guard to avoid duplicate automatic candidates.

Brain maintenance uses `/tdt-maintain-brain` and `tdt brain audit` to inspect
canonical note links and structure, followed by agent review of meaning. Reviewed
repairs use `tdt brain repair`: hash-bound previews, preserved identities and
provenance, local backups and recoverable writes. Consolidation retains original
notes; candidate approval remains a separate operation. See the installed
[brain guide](../src/thisdamnthing/resources/docs/brain.md#maintain-the-brain).

## Reminders

`/tdt-remind` saves explicit one-time reminders directly to `work/reminders/`,
without candidates or knowledge promotion. `/tdt-check-reminders` claims due and
overdue records and announces them once; notification and task completion are
separate. List, edit, snooze, done and cancel use the same small CLI/store.
Workspace timezone and opt-in request-hook checks are configured during
`/tdt-workspace` onboarding. Scheduled checks require a separately configured,
verified external scheduler; core has no daemon. Shared expiring delivery claims
coordinate channels/hosts. Rendering is host-dependent and not transactional
with acknowledgement. See the [reminder guide](../src/thisdamnthing/resources/docs/reminders.md).

## Stack contracts

Both v1 workflow and v2 capability bundles are supported. The packaged
[stack contract](../src/thisdamnthing/resources/harness/contracts/stack.md) defines the
exact current fields, limits and trust rules; [capability guide](stack-capabilities.md)
explains provider integration and verification. The following describes the v1 baseline.

Define one `stack.json` with `contract_version`, normalized `id`, `version`,
`description`, `author`, `license`, and explicit `skills`, `hooks`, `knowledge`
file lists. Optional templates/docs can be explicitly listed too. No dependencies
in v1. Use the packaged contract for exact field types and event payloads.

All skills follow the [Agent Skills specification](https://agentskills.io/specification):
names and directories match, begin with `tdt-`, use lowercase letters/digits/
hyphens, and are documented as `/tdt-*`. Stack IDs and repository folders use the same
lowercase hyphen-separated name (`namespace-name`). Suggested stack skill
names: `/tdt-stack-builder-create` and `/tdt-software-production-brief`.
Adapter work must verify host naming and invocation support; surface any mismatch.

Stacks install under `.tdt/stacks/<id>/`; core exposes owned skills/hooks and
imports stack knowledge as pending candidates. Removal deletes only owned assets and
entry points, preserving user brain notes. Core and community use the same path.
Reject traversal, escaping symlinks, invalid names, and conflicts before writing.
Show executable hooks and provenance before activating community content; require
explicit trust for executable hooks without changing agent permission settings.

Registry entries include stack id, description, version, GitHub repository, and
release reference resolved to a commit, with archive and selected-content digests. Fetch
the ZIP/source archive, validate it, and record its origin and resolved revision.
CLI and `/tdt-install-stack` share the same installer. Community authors submit
their repository metadata for registry review. Use [the marketplace contract](marketplace-contract.md) for the JSON
endpoint contract. The separate Sites project
owns the listing page and endpoint for `stacks.usetdt.com`; verify deployment
before documenting a public registry as available.

## Verify the installed product

Use the [component checklist](acceptance.md) and [workspace runbook](e2e-runbook.md)
to check a packaged build in disposable workspaces. Verify public package and
registry destinations separately from local installation. Limit platform and host
claims to the behavior exercised on the intended release artifact.

## ThisDamnThing's UI, core capability

Users can request “use ui”; agents can offer ThisDamnThing's UI or direct chat/TUI answers.
Core serves a local browser page, accepts structured submitted responses, and
returns them to the active agent through a bounded CLI wait/read loop. The agent
can act on an answer or update the same session with follow-up questions. This
works with zero stacks. Standard controls and custom HTML/JavaScript share a
versioned contract and the Satin Slate design system.

Stack-builder and software-production reuse core UI for
context, briefs, plans and tasks. UI session state stays local and separate from
approved brain knowledge. This is an on-demand local interaction service, not
a continuously running background daemon. Root `.design-system/` holds copied
development references; implementation extracts only needed runtime assets into
core resources. See [the UI implementation guide](ui.md) for session handling,
browser boundaries and verification procedures.

Internal work and project resolution follow the [project guide](../src/thisdamnthing/resources/docs/projects.md). WORK.md is user-owned; refresh preserves edits. Stack skills respect it when scaffolding requested work.

## Local MCP retrieval

The optional `mcp` dependency enables `tdt --workspace PATH mcp serve` over stdio.
The initial read-only catalog exposes current policy/context and built-in approved
knowledge search/read through the existing core, plus paginated candidate and
scratchpad inventories and complete reads with explicit status labels. Workspace
status and paginated project registry/registration reads are also available;
external project source is not read. Paginated guide and canonical skill catalogs
provide complete, bounded reads without executing instructions. Reminder lists and
complete reads expose task and delivery state without claiming or acknowledging
notifications. Workspace selection is explicit
and fixed for the process. Incoming stdio messages are bounded to 8 MiB before
decoding or parsing; oversized frames close the connection. The opt-in `everyday` profile adds reminder creation and revision-checked editing,
snoozing, completion and cancellation on explicit user instruction, using the shared
core lock. Settings are readable in both profiles; everyday also configures
preferences, claims due reminders with expiring leases, and acknowledges delivery
without completing tasks. Claim responses are budget-checked before writing.
Both profiles also provide bounded capture request inventories and exact status reads,
without reading transcripts. Everyday submits summary/skip to existing hook requests
and suppresses capture using current hook turn tokens through shared core locking;
candidates remain pending and completed submissions preserve their saved outcome.
Enabled hooks prefer workspace-bound MCP capture/suppression tools, with CLI
fallback. Uncertain capture responses require an exact status read before retry;
completed outcomes are retained. MCP does not establish host/session identity or
enable capture hooks.
Both profiles expose exact candidate review status across promotion, including full
review history. Everyday supports hash-bound approval, rejection and editing on an
explicit user decision; edits remain pending for fresh approval. Shared core checks
retain provenance and refuse conflicting interrupted promotions.
Everyday also saves explicitly requested approved knowledge and tagged scratchpad
notes through the shared core, preserving deterministic identities and existing
content on identical retries. Save skills prefer MCP with CLI fallback.
Everyday also registers existing directories and creates internal project folders,
returning small receipts through shared locked core operations. The add-project
skill prefers these tools with CLI fallback. Both profiles support explicit
registered-project inspection, including bounded external source evidence with
reported omissions. Everyday also submits onboarding interpretations as pending
candidates; identical retries preserve prior content and review status. Retries preserve exact interrupted registration
notes and existing identities. Read-only remains the default. Other writes, host registration, resources and prompts
are not implemented. See the installed [command reference](../src/thisdamnthing/resources/docs/commands.md#local-mcp-reads).

Both MCP profiles also expose paginated scratchpad literal search and shared-tag
related-note discovery, keeping results explicitly unapproved. Working-file
search/read stay below work/, exclude dedicated stores and nested workspaces,
and report scan limits, omitted entries and bounded text prefixes. They neither
read external projects nor execute working-file content.

Both profiles expose paginated installed stack provenance, declared stack guides
and search provider metadata through bounded registry reads. Provider trust is
the recorded installation decision; discovery does not verify assets or runtime
readiness, execute provider code, index content or fetch sources. Full stack guide
reads use the existing guide reader. Everyday also exposes `tdt_brain_search_providers` for 1–8 explicitly selected
providers through shared core search. It validates trust/assets/compatibility,
rechecks current approved evidence, and never implicitly indexes. Provider code
runs with local process permissions, outside any OS or network sandbox.

Everyday MCP also exposes the eight UI lifecycle tools through shared CLI core
functions. Structured pages, complete paginated events with original prompts,
bounded waits, explicit acknowledgements, retained close and authorized cleanup
follow the [UI guide](ui.md).

Both profiles expose `tdt_brain_audit` through the shared structural scanner.
Findings and note hashes are separately paginated, with report-bound cursors,
totals, limitations and unreadable-note omissions. Audits do not repair notes or
replace semantic review. Both profiles also expose `tdt_brain_repair_preview`
for complete, hash-bound replacements through shared core validation, without
writing notes or backups. Both profiles expose exact retained outcome reads;
everyday applies explicitly authorized replacements with the preview hash and actual approval reference.
Completion is recorded with note writes in the shared transaction. Identical
completed retries return historical success without overwriting later changes.
Interrupted transactions require CLI recovery and a fresh outcome read.
Audit, preview and outcome reads share a read lock so parallel model calls do
not contend with one another; apply retains the exclusive workspace lock.
Read-only has 44 tools; everyday has 80.

Both profiles expose `tdt_brain_names_preview` through the shared filename
migration core, returning all renames and complete replacements, including null
old-path deletions. Preview uses a shared lock and refuses output beyond its
up-to-1-MiB budget without partial content. The proposal hash binds renames and complete
before/after contents, including derived stack catalog writes. Everyday exposes
`tdt_brain_names_apply` with the preview hash and actual user instruction; both
profiles expose `tdt_brain_names_status`. CLI apply requires the same hash and
instruction. Prepared/completed backups are bounded to 8 MiB; completion shares
the file transaction. Identical completed retries preserve later edits. After an
uncertain result read status before retry or CLI fallback; journals require CLI
recovery and a fresh status read. Unknown is not proof an operation never ran.
A no-op apply retains a completion record without changing notes.

Both MCP profiles expose `tdt_project_references` for explicit project IDs through
the shared lifecycle scanner, including retained removed registrations. Reference
and skipped-entry pages bind the complete scan revision and report totals, scan
truncation and limitations. Matches do not establish ownership or authorize
cleanup. Reference cleanup requires separate explicit authorization.

Both profiles expose project archive/unregister, restore and relink previews with
complete replacements and shared CLI proposal hashes. Lifecycle previews use
shared read locks; applies keep exclusive locks. Preview result budgets support
up to 1 MiB and refuse oversized output without partial review content. Everyday
applies explicitly authorized lifecycle changes using identical preview inputs,
hash and actual approval reference. Both profiles read retained outcomes
by proposal hash. Completion shares the registry/note transaction; identical
completed retries return historical success without resolving the old registration
or overwriting later changes. Prepared outcomes require inspection; interrupted
journals require CLI recovery and a fresh status read. Unknown is not proof an
operation never ran; legacy UUID backups are not indexed. Indexed
backups are bounded to 8 MiB before writes. Everyday also exposes hash-bound reference cleanup apply.


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

Everyday also exposes `tdt_brain_index` for one explicitly selected installed
provider and actual user instruction. `rebuild` defaults false; true starts with
an empty cache. Shared CLI core validates trust/assets/compatibility and cache
ownership, indexes current approved evidence under its exclusive lock and writes
cache/ownership together. The small receipt fits the minimum budget. Provider
code runs with local process permissions. There is no retained operation outcome;
after uncertainty inspect search/cache state before an authorized retry. Retries
execute again; interrupted journals require CLI recovery. No batch indexing,
installation, trust changes or automatic query-time indexing is added.

Everyday exposes `tdt_constitution_save` for complete explicitly approved policy
Markdown, the current revision (or `missing`) and an actual approval reference.
It uses the existing CLI policy lock and stale-revision checks, appends the audit
reference and enforces the 6000-byte final UTF-8 limit. The receipt returns only
the saved SHA256; read complete policy back. After uncertainty reread before retry
or CLI fallback; no retained operation outcome or automatic retry. Policy saving
does not enable hooks, recover state or grant permissions beyond host boundaries.

Both MCP profiles expose retained user skill proposals with pending/approved/declined/all
filters, revision-bound pagination and complete exact-ID reads. Reads include
behavior, source references, decision reference, original ownership snapshot and
current recorded ownership. Historical approval and recorded ownership do not
verify live skill files. Shared read locks and a 2-MiB registry cap protect reads;
interrupted skill/stack journals refuse discovery. Output budgets refuse partial
review content. Everyday exposes `tdt_skill_propose` and single-ID `tdt_skill_review` through
shared CLI core, exclusive locking and ownership checks. Review requires the
actual user decision reference. Small receipts fit minimum budgets; full proposal
reads precede review. After uncertainty inspect retained decisions and live files
before retry; historical proposals can reopen, so retries are not automatic.
CLI recovery remains required for interrupted transactions. Shared registry reads
and proposed writes are capped at 2 MiB. Host history remains CLI-only.

Both profiles expose `tdt_skill_inventory` for overlap review across canonical and
host skill folders using the shared bounded CLI inventory. Paginated content
prefixes report truncation; owner labels do not verify assets. Retained proposals
remain a separate inventory. No skill execution or host history access is added.

Both profiles expose `tdt_recovery_preview` with an explicit `stack` or `skill`
journal selection. Shared CLI recovery validation checks every current file
against its journal versions under a shared read lock. Complete before/after
contents include null deletions and base64 binary values; output beyond the
up-to-1-MiB budget refuses without partial content. Journal input is capped at
8 MiB; special files, escaping paths and conflicting local edits refuse.
The semantic journal hash binds a snapshot for everyday `tdt_recovery_apply`,
which requires the selected kind, `expected_sha256` and actual user instruction.
Shared CLI rollback revalidates bounded current files and the journal hash under
an exclusive lock; absent/changed journals refuse. The fixed-size receipt is not
a durable outcome or approval audit. After uncertainty inspect preview, affected
files and original operation outcomes before any newly authorized retry; absence
does not prove success. Interrupted rollback retains its journal. CLI recovery
remains available without hash binding. Other CLI recovery references above may
use this reviewed tool for stack/skill journals; no policy-lock recovery is added. An absent selected journal is not a clean-workspace assessment.
