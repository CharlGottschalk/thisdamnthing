# Marketplace contract

This contract defines the public registry consumed by ThisDamnThing and the requirements
for approving and installing registry releases. Website implementation and hosting
are separate from this repository. Submission, accounts and ratings have no public
write API in this contract; payments and automated submission are outside its scope.

Use these sources together:

- [Registry schema](../src/marketplace/registry.schema.json) and its identical
  [packaged copy](../src/thisdamnthing/resources/marketplace/registry.schema.json) define
  exact fields, types and bounds. The [example feed](../src/marketplace/registry.example.json)
  contains fictional data, not approved or downloadable releases.
- [Stack contract](../src/thisdamnthing/resources/harness/contracts/stack.md) defines
  manifests, selected files, compatibility, asset limits and executable trust.
- [Client development](marketplace.md) covers implementation and verification;
  [stack lifecycle](stack-lifecycle.md) covers approved updates and removal.

## Identity and metadata

Stack IDs contain 1–80 lowercase letters, digits and single separating hyphens,
starting with a letter, such as `tdt-search-sqlite`. Use the same ID for the
source directory and repository name. Listing IDs, release manifest identities,
stack dependency references and replacement IDs must satisfy this format.

MVP releases come from public GitHub repositories with one stack at repository
root. Repository URLs use `https://github.com/<owner>/<repo>` without a `.git`
suffix. Installations target full immutable commit SHAs, never moving branches.
Only published, non-draft, non-prerelease GitHub releases qualify. Their tags must
match the manifest's numeric `MAJOR.MINOR.PATCH` version after removing at most
one leading `v`.

Manifest metadata lives only in `stack.json` under `marketplace`. The submission
form collects name, GitHub URL and description. All other listing and release
metadata is read from the pinned commit. The database stores no copy, including
no dependency, capability, hook or supported-agent columns. Review records and
immutable release references/digests remain in the database. Search filters and
the registry are built from manifests, and unavailable manifests fail the read.

The required `extension_type` describes purpose and grants no permissions:

| Value | Meaning |
| --- | --- |
| `functionality` | Extends ThisDamnThing itself, such as a search provider. |
| `capability` | Adds skills or workflows for a kind of work. |
| `both` | Combines functionality with domain skills or workflows. |

Show this classification on listing cards and detail pages and verify it during
review. It is distinct from tags, release capability disclosures and manifest v2
runtime-provider declarations.

Each release resolves its immutable manifest identity, supported agents (`claude`,
`codex`), prerequisites, capabilities and hooks. Compatibility claims must reflect
reviewed environments. Listing summary, author name and license match the latest
active release; older installations compare against their own release identity.

Prerequisite types are `mcp`, `connector`, `service`, `stack`, `cli` and `runtime`.
Each declares its reference, name, necessity, purpose, setup URL and optional
version constraint, authentication and payment requirements. Stack references are
ThisDamnThing stack IDs; other references identify the provider or package. Constraints
are display-only, not executable expressions. ThisDamnThing does not install dependencies,
solve versions or collect credentials. Unknown availability must stay unknown
until verified; required prerequisites must be confirmed before installation.

Capability disclosures cover file access, network activity, process execution,
connector use, scope, purpose and data leaving the machine, including effects
requested by skills. Hooks must match manifest event/path declarations exactly.
Disclosures and registry approval are neither a sandbox nor execution consent.

## Approval and immutable releases

1. Authenticate the submitting author and verify repository control before
   assigning ownership of a stack ID. First-party and community stacks follow
   the same review process for every version.
2. Resolve the eligible release tag to a full commit SHA. Fetch its immutable
   archive and validate the root manifest with ThisDamnThing. Match ID, version, author,
   license and description against the submitted release metadata.
3. Review selected content, prerequisites, capabilities, security, privacy and
   data flows. Test in a disposable environment without production credentials;
   never execute submissions in the website request process. Keep review evidence
   and reviewer identity private.
4. Approve the exact archive SHA256 and ThisDamnThing selected-content digest. Publish
   only approved versions. Commit, version, tag, manifest identity, dependencies
   and capabilities cannot be edited in place; changes require a new release
   and review. Moderate presentation edits and audit status changes.

A moved tag must never retarget an approved entry. If archive bytes change, refuse
the hash mismatch; the content digest cannot bypass it. Never silently replace an
approved digest or reuse an ID/version for different content. Repository transfers
and ownership changes require review. Draft/submitted/rejected review states stay
out of the public feed.

## Status and version selection

Listings and versions have `active`, `deprecated` or `withdrawn` status.
Non-active status requires a public reason and timestamp; replacement ID is
optional. Withdrawal overrides deprecation, including at listing level.

- Deprecation warns before installation and presents replacement guidance.
- Withdrawal retains the public page and version tombstone but refuses new
  registry installation, including explicitly pinned versions. Never fall back
  silently, delete installed files or revoke local permissions.
- `latest_version` is the highest numeric active approved version. It is null
  when none exists or the listing is withdrawn. Selecting an older active or
  deprecated version is explicit; default selection never chooses deprecated
  content when no active release exists.

No background updates or withdrawal checks occur. Explicit updates use the
approval-bound [stack lifecycle](stack-lifecycle.md), preserving source identity,
prerequisites, executable trust and ownership. Ordinary install refuses replacing
an installed ID. Local directory installation does not consult the registry and
cannot enforce its withdrawal state.

## Public read interface

`GET https://stacks.usethisdamnthing.com/registry/v1/index.json` returns one UTF-8 JSON
feed with `application/json`, schema version and `generated_at`. No login, cookies,
API key or client identifier is required. Publish atomically, with at most 5 MiB
of decoded data and 1,000 listings. No pagination or server-side search is defined;
exceeding these bounds requires a new contract, not silent truncation.

Servers should support ETag/Last-Modified for explicit requests. Any conditional
reuse requires server confirmation; offline cached-feed installation is not
supported. The current client fetches a fresh feed without caching.

Reject unknown schema versions/fields, duplicate JSON keys, stack IDs or versions,
invalid tag/version or manifest identity, duplicate prerequisite type/reference
pairs, unsafe or duplicate hook paths, invalid status metadata and incorrect
latest-version selection. Enforce schema and semantic checks together.

Canonical listing URLs are `https://stacks.usethisdamnthing.com/<stack-id>`; a configured
registry uses its own origin plus the same ID path. Preserve the page after
withdrawal. Optional rating links may append `#ratings`; ratings stay outside the
CLI feed and open only on user request or acceptance. Do not put workspace,
project, conversation or user identifiers in those URLs.

Search is case-insensitive literal text across name, summary, description, tags
and author display name. Category, tag, author ID and agent filters match exactly;
combine filters with AND. Agent filtering uses the latest active release.

| Browse mode | Order |
| --- | --- |
| New | Initial approval time descending. |
| Featured | Staff rank ascending; only ranked listings. |
| Popular | GitHub stars descending; unknown counts last. |

Use ID ascending to break ties. Fetch stars on the website backend, record their
fetch time and display unavailable counts as unknown, not zero. Non-null stars
require a timestamp. Do not substitute install/download counters or client telemetry.

## Archive transport and installation

Derive `https://codeload.github.com/<owner>/<repo>/zip/<commit>` from validated
repository and commit fields. The registry cannot supply arbitrary archive URLs.
Use verified HTTPS without credentials. Registry redirects stay on the configured
registry origin; archive redirects stay on the intended GitHub archive origin.
Require unencoded HTTP 200 responses, bounded streaming reads and complete bodies.

| Bound | Maximum |
| --- | ---: |
| Request duration | 30 seconds |
| Downloaded archive | 384 MiB |
| Expanded archive | 512 MiB |
| ZIP entries | 12,000 |
| Entry path components | 20 |

Preflight every ZIP entry before writing. Reject absolute paths, traversal,
backslashes, symlinks, special files, encrypted entries, duplicate/normalized
collisions and excessive expansion. Require exactly one top-level directory with
`stack.json` directly inside it. Never execute content during fetch or validation.

Apply the stack contract's stricter selected-file limits. V2 assets have per-file
SHA256/size declarations, a 128 MiB per-file limit and a 384 MiB total bundle
limit, plus ThisDamnThing/platform/Python compatibility. V1 limits remain unchanged.
Match approved manifest identity, exact hooks and both archive/content digests.

Before activation, disclose repository, version, commit, status, prerequisites,
capabilities and executable hooks/providers. Require explicit trust bound to the
selected content and enforce normal ownership/conflict checks. Registry approval
never supplies user trust. CLI and the install skill share this installation path.
Record registry origin and endpoint, repository, tag, commit and both digests in
local provenance. Fail clearly on unavailable/ineligible releases, transport,
validation, prerequisite, trust or ownership errors; never substitute unverified
bytes, another release or `main`.

Discovery/downloads are explicit user operations. No analytics, install callbacks,
rating writes, background polling or automatic browser launches. Startup, doctor,
local listing and local validation stay offline. Minimize service logs; ordinary
HTTP requests do not demonstrate successful installation.

## Explicit local archive transport

For local integration, install/inspect may receive `--local-archive-origin` with
`--registry`. Require a canonical, credential-free HTTPS origin using a literal
loopback IP, with no path/query/fragment and matching the registry origin.
Derive the archive route by appending
`registry/local/archives/<stack-id>/<immutable-commit>` to that origin.

This adds no feed field and never changes default GitHub transport or creates an
implicit fallback/persistent setting. Preserve TLS, origin, time/size, archive,
manifest, digest, prerequisite and trust checks. Local provenance adds
`archive_transport=local-loopback` and `archive_url`. Updates do not inherit this
option. Local integration does not establish public deployment or transport.

## Marketplace metadata in stack.json

For marketplace publication, add a `marketplace` object to `stack.json` (v1 or
v2). It is optional for local-only stacks, but required by the marketplace.
The manifest is the only metadata source: the website reads it at the pinned
release commit and does not store a copy in its database. The form asks only
for a name, GitHub URL and description. A repository URL selects GitHub's latest
stable release; a release URL selects that version. Verification displays the
resolved version and commit before submission and checks them again on submit.

Required fields in `marketplace`:

- `extension_type`: `functionality`, `capability` or `both`.
- `categories`: one to five controlled marketplace category slugs.
- `tags`: up to twenty unique lowercase hyphen-separated slugs.
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
records, but no manifest metadata. Public reads fail as unavailable if any required
pinned manifest cannot be read or validated; they never substitute branch content
or empty disclosures. Published manifests must remain readable at their commits.


The manifest-only transition preserves old release and review records privately.
A verification timestamp (not metadata) gates public visibility and approval.
Releases without a compatible manifest at their pinned commit must publish a new
version; neither old approved commits nor their manifests are rewritten.
