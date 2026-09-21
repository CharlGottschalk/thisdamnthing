# Stack contract v1

First-party and community bundles use exactly the same local installer. Core
starts with zero stacks. No dependencies, install scripts, automatic upgrades,
network fetching or provider permission changes exist in this contract.

`stack.json` is a UTF-8 JSON object with unique keys. Required fields:

| Field | Type / rule |
| --- | --- |
| contract_version | Integer `1` (not a boolean). |
| id | String of 1–80 lowercase letters, digits and single separating hyphens, starting with a letter; no dots, consecutive or trailing hyphens. Use the same ID for the repository and source directory, e.g. `tdt-search-sqlite`. |
| version | String `MAJOR.MINOR.PATCH`; nonnegative decimal integers without leading zeros. No prerelease/build suffixes in v1. |
| description, author, license | Nonempty single-line strings, each at most 500 characters. License is an author-provided identifier or description, not legal verification. |
| skills | Array of explicit `skills/tdt-<name>/SKILL.md` paths. |
| hooks | Array of objects containing exactly `event` and `path` strings. |
| knowledge | Array of explicit `knowledge/*.md` paths; subdirectories allowed. |
| marketplace | Optional object for publication metadata; see the marketplace section below. |
| templates, docs | Optional arrays of explicit file paths under the corresponding directory. |

Unknown fields are rejected. Each array has at most 50 entries. Every selected
file is regular UTF-8, at most 256 KiB; the total is at most 2 MiB. Files not listed
are not copied or hashed. Paths use `/`, with Unicode letters/digits/combining marks, spaces, `_`, `-`
and `.` in components; no empty components, `.`/`..`, absolute paths, backslashes
or symlinks in selected paths or source ancestors. A path may be listed once only.
V1 bundles use self-contained Python hook files; no dependency installation.

Skills follow https://agentskills.io/specification. Names start with `tdt-`,
contain 1–64 lowercase ASCII letters/digits/hyphens, have no consecutive or
terminal hyphens, and match their directory. Core names are reserved. Document
invocation as `/tdt-<name>` (Codex can use `$tdt-<name>`). Stack IDs and source
repository folders use the same lowercase hyphen-separated name, for example `tdt-software-production`.

V1's simple frontmatter subset starts with the exact plain name line, followed
by a nonempty, single-line description of at most 1024 characters. Use valid YAML
and quote values with YAML-significant punctuation. Keep skill bodies concise;
load supporting bundle docs/templates when needed. Every shipped skill must
conform to Agent Skills, even though v1 validation is a bounded subset checker.

```markdown
---
name: tdt-example-hello
description: Say hello when the user asks for a greeting.
---
```

Existing installed dotted skills are preserved for removal and trusted hook
execution; new installs require compliant names. Approve a newer stack version with `stack update` to migrate its skills. Core `init` migrates only unchanged owned
core skills/resources, refusing edits and new-name collisions. Use `--agent`
when adding/configuring adapters. No provider permissions or user brain data are changed.

Example layout and manifest:

```text
stack.json
skills/tdt-example-hello/SKILL.md
hooks/start.py
knowledge/greeting.md
templates/brief.md
docs/usage.md
```

```json
{
  "contract_version": 1,
  "id": "example-hello",
  "version": "1.0.0",
  "description": "A small greeting workflow",
  "author": "Example author",
  "license": "MIT",
  "skills": ["skills/tdt-example-hello/SKILL.md"],
  "hooks": [{"event": "session_start", "path": "hooks/start.py"}],
  "knowledge": ["knowledge/greeting.md"],
  "templates": ["templates/brief.md"],
  "docs": ["docs/usage.md"]
}
```

## Hook events and capabilities

Supported neutral events are `session_start` (provider SessionStart) and
`turn_complete` (provider Stop). Both configured Claude and Codex adapters deliver
notifications through existing core hooks; no extra provider hook entries are
added. PreCompact and all other events are refused. Unconfigured adapters do not
run hooks. Workspace trust and host hook enablement still govern delivery.

Each `hooks` object selects a `hooks/*.py` file. Core runs it with its own Python,
workspace cwd, no shell, and one JSON object on stdin:

| Payload field | Type |
| --- | --- |
| format_version | Integer 1 |
| host | `claude` or `codex` |
| event | `session_start` or `turn_complete` |
| session_id | Nonempty string |
| cwd | Absolute string path inside workspace |
| transcript_path | Absolute string path or null; reference only, not transcript contents |
| turn_id, source | Nonempty string or null |
| stop_hook_active | Boolean; active Stop continuations are skipped |
| workspace | Absolute workspace path string |
| stack_id | Namespaced stack ID string |

Output is discarded: hooks cannot inject host context or block Stop through
stdout. Failure is reported on stderr without breaking core capture/startup.
Each invocation has a two-second timeout, with a shared four-second execution
budget; remaining hooks may be skipped. Hooks are best-effort notifications,
not an exactly-once queue; authors must handle replay and missed delivery.
They execute with the agent process's OS access and inherited environment; this
is explicit code trust, not a sandbox. Do not spawn background processes.

## Installation, knowledge and ownership

`tdt stack validate <directory>` displays manifest, canonical local origin,
selected-content SHA256 and executable hook source. Review the bundle before
installing. Hooks require `--trust-hooks <that SHA256>`, binding trust to the exact
selected files and manifest. Installed bytes are rechecked before execution.
Changes require remove/reinstall; an installed ID is never replaced in v1.

Canonical files live under `.tdt/stacks/<id>/`. Skills are copied to owned
`.tdt/skills/` paths with thin `.agents/skills/` and `.claude/skills/` bridges.
Both namespaces are reserved even before host bootstrap. Directory/name/legacy
command conflicts fail preflight. Host naming is the existing `tdt-*` convention;
new stack skill live invocation is not yet verified on either host.

Knowledge files contain concise plain Markdown (at most 3000 characters, with
common secret-pattern checks). Install indexes each as a pending brain candidate
with local bundle provenance and source digest. Only explicit ordinary brain
review makes it searchable. Candidate snapshots and approved notes survive
removal, and unchanged reinstall does not reset prior review decisions. Templates
and docs remain within the installed bundle, never overwrite user documents.

`.tdt/state/stacks.json` records manifest, origin, trust digest, candidate paths
and owned-file hashes. Removal refuses edited/missing owned files and untracked additions; it unregisters
hooks, deletes only matching owned files and prunes empty directories. Unrelated
additions block mutation until preserved/moved by the user.

Stack mutations use the shared brain lock, atomic file replacement and a write-ahead
journal. Preflight refusals leave content unchanged (the shared lock file may be
created). Ordinary write failures roll back; after interruption run
`tdt stack recover` to restore the prior state. Recovery refuses intervening
file edits. While a journal exists, stack hooks/list/install/update/remove are disabled.
Do not run hosts or edit bundle files during install/update/remove/recovery. This is a
local cooperative-filesystem design, not protection against hostile concurrent
filesystem replacement; power-loss durability is not guaranteed.

Declared `docs/` files stay in the bundle and appear in the core-managed
`.tdt/stack-docs.md` catalog. Names come from file paths, not executable metadata
or parsed document instructions. Supporting local links must resolve within the
installed bundle; declare their target files too. Projected skills should use
workspace-relative `.tdt/stacks/<id>/docs/...` references. Publishing readiness
checks must inspect links in the installed artifact, without a source checkout.

## Contract v2: local capabilities

V1 remains unchanged, including its text/file limits and digest algorithm. V2
retains the required workflow fields (empty lists are valid), adds required
`assets`, `capabilities`, `compatibility`, and uses `contract_version: 2`.

- `compatibility` has exactly `tdt: "0.1"`, `platforms` (nonempty explicit list
  drawn from linux-x86_64, linux-aarch64, darwin-x86_64, darwin-arm64), and `python`
  (nonempty explicit minor list drawn from 3.11, 3.12, 3.13). Declarations are
  author claims; only tested combinations should be listed. Execution rejects a
  mismatch. Windows execution is not implemented.
- `capabilities` contains exactly one object: `name: "brain.search"`, integer
  `interface_version: 1`, and `entrypoint: "assets/provider.py"` (or another
  explicitly selected `.py` path under assets). No shell or generic install scripts.
- `assets` lists up to 10,000 objects with exactly `path`, `size` (integer bytes),
  `sha256` (lowercase SHA256). Files under assets may be binary, each <=128 MiB;
  total bundle <=384 MiB. Manifest <=2 MiB; manifest plus workflow text <=2 MiB.
  Existing workflow files retain their 256 KiB bounds. Paths retain v1 rules;
  normalized name/directory collisions are refused. No globbing or symlinks.
- The v2 snapshot digest is SHA256 of UTF-8 Python JSON serialization of the
  path-to-file-SHA256 map (`sort_keys=True, ensure_ascii=False`, default separators),
  including stack.json. `stack validate` prints the manifest and digest. Install
  requires `--trust-executable SHA256` (old `--trust-hooks` is an alias).
  Discover/install never execute providers. Every call rechecks owned files,
  additions, compatibility and the exact trusted snapshot. Updates require fresh
  digest trust and separate exact update approval; no implicit carry-forward.

### brain.search interface 1

CLI: `brain providers` discovers without execution; `brain index --provider ID`
reconciles, `--rebuild` starts empty; `brain search QUERY --provider ID` queries.
Repeat --provider for up to eight distinct providers. Selection is per command,
explicit, and sorted by stack ID. Omit providers for zero-stack literal search.
Unavailable, incompatible or failed selected providers give actionable errors;
there is no silent semantic-to-keyword substitution.

Core launches `[sys.executable, "-I", "-B", absolute_entrypoint]`, with no shell,
from a disposable directory. One UTF-8 JSON request on stdin, then EOF:

```json
{"protocol_version":1,"operation":"search","query":"release risk","notes":[{"id":"knowledge/release","title":"Release safety","text":"Current Markdown body and source references","sha256":"64 lowercase hex characters"}],"limit":50,"rebuild":false,"state_path":"absolute disposable index path"}
```

Index requests use operation `index`, empty query and an explicit rebuild boolean.
The input is capped at 16 MiB; the approved corpus scan at 2,000 entries, each note
at 32 KiB. Index gets 300 seconds, queries 20 seconds per provider. stdout and stderr
are each capped at 256 KiB through bounded pipes. Timeout, cancellation, failure
and completion kill the process group and clean temporary state. Nonzero exits,
malformed JSON and schema violations are errors. No persistent service or hooks.

Search response has exactly `protocol_version: 1` and `results`, an ordered list
of at most 50 distinct `{id, sha256}` records. IDs/hashes must match the current
request. Scores/text from providers are not accepted. Index response has exactly
`protocol_version: 1` and `indexed`, the integer number of supplied notes.

Core rechecks current approvals, registered project IDs and note content after
execution, excluding changed/deleted notes, then returns current Markdown text
with source references. Pending/rejected candidates never enter the corpus.
Rank fusion sums `1/(60 + rank)` for each selected ranking and a literal ranking;
exact title/ID matches sort first, then fusion score, then note ID. Bounded outgoing
wikilinks and cycle deduplication remain core behavior. Ranking is not evidence
confidence; absence and conflicts still need honest explanation.

### Cache and lifecycle

Core copies the previous owned `index` to a disposable directory. Providers may
read it for queries and atomically replace it during indexing. On successful index
acknowledgement, core accepts one regular file <=128 MiB and transactionally saves
it under `.tdt/state/capabilities/<id>/index`, with hash and snapshot ownership in
`.tdt/state/capability-state.json`. Failed/interrupted invocations discard temporary
work and keep the prior index. A missing index requires explicit indexing.
Queries do not persist cache changes. The workspace lock serializes indexing,
queries and stack mutations. Core updates invalidate the cache; uninstall deletes
unchanged owned cache files, refusing user modifications. Unrelated additions and
brain notes remain untouched. Empty directories may remain, with no registration.

Providers must reconcile edits/deletions on index, omit stale IDs on query, and
version model/config caches. Trusted subprocesses retain the user's OS and network
access. Process separation contains failures; it does not enforce a permission or
network sandbox. Offline behavior is a provider requirement, verified separately.

New bundles require normalized IDs. Existing ownership records with dotted IDs
remain readable for use and removal; they are not automatically renamed.

## Marketplace metadata in stack.json

For marketplace publication, add a `marketplace` object to `stack.json` (v1 or
v2). It is optional for local-only stacks, but required by the marketplace.
The website reads metadata at the pinned release commit. The form asks for a
name, GitHub URL, required curated category and description. The listing category
is authoritative; do not put categories in new manifests. Only tags are copied
from manifests into a searchable release array; there is no editable tags field.
A repository URL selects GitHub's latest stable release; a release URL selects that version. Verification displays the
resolved version and commit before submission and checks them again on submit.

Required fields in `marketplace`:

- `extension_type`: `functionality`, `capability` or `both`.
- `tags`: up to twenty lowercase hyphen-separated slugs, at most 64 characters
  each. Readers deduplicate and sort them before indexing.
- `supported_agents`: one or both of `claude` and `codex`, reflecting verification.
- `dependencies`: registry prerequisite objects (up to fifty), including type,
  ref, name, required, purpose, HTTPS setup_url, nullable version_constraint,
  authentication_required and payment_required booleans.
- `capabilities`: registry disclosure objects (up to fifty) with type, scope,
  purpose and data_leaves_machine. Types are file_read, file_write, network,
  process, connector and other. Declare effects requested through skills too.
- `icon`: null or an object with HTTPS `url` and `alt`.
- `screenshots`: up to eight objects with HTTPS `url` and `alt`.
- `documentation_url`, `support_url`: null or credential-free HTTPS URLs without fragments.

Use empty arrays or null explicitly where appropriate; do not omit disclosures
for executable hooks or providers. Top-level v2 `capabilities` still declares
runtime providers; `marketplace.capabilities` describes effects and data flows.
The packaged `marketplace/manifest.schema.json` defines exact fields and bounds.
Changes require a new release commit and review. The database keeps listing
presentation, repository ownership, pinned release references, digests and review
records and indexed release tags, but no other manifest metadata. Public reads
fail as unavailable if any required pinned manifest cannot be read or validated; they never substitute branch content
or empty disclosures. Published manifests must remain readable at their commits.

Legacy published manifests may retain `marketplace.categories`: readers validate
its old shape then ignore it. New authoring schemas omit it. Do not rewrite old
releases, tags or digests. Listing/feed categories contain the selected category.
Public tags come only from the latest approved active release; with no active
release they are empty, even when the page shows an older approved release.
Staff must compare indexed tags with the pinned manifest before approval.
