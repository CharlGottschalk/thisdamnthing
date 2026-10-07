# Optional stacks

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Stacks are optional packages that extend your workspace with skills, workflows,
knowledge, templates, documentation and local capabilities. They can include
hooks or local search providers, and their workflows can use TDT’s shared UI.
Start with zero stacks, then add the capabilities you need. For the bundle format
and examples, read `.tdt/contracts/stack.md`.

A stack can declare external prerequisites such as tools, services or MCP servers.
These declarations explain what a workflow needs; installing a stack does not
automatically configure those services or change your agent’s permissions.

## Manage stacks through your agent

Use the skills below if you prefer chat to terminal commands. The agent runs the
underlying CLI and explains the results.

| Task | Skill |
| --- | --- |
| Find, inspect and install a local or marketplace stack | `/tdt-install-stack` |
| Inspect and apply a stack update | `/tdt-update-stack` |
| Remove an installed stack | `/tdt-remove-stack` |
| Check the workspace and locate installed stack guides | `/tdt-workspace` |
| Create and validate a new stack | `/tdt-stack-builder-create` (optional Stack Builder) |
| Prepare a stack release | `/tdt-stack-builder-publish` (optional Stack Builder) |

In Codex, use the same names with `$` instead of `/`, or select the skill through
the skill picker. Core management skills are available with zero optional stacks.
For authoring and validation-only requests, see [Create and share a stack](authoring.md).

## Terminal commands

The commands below are the underlying operations used by these workflows.

```sh
tdt stack validate ../stack
tdt --workspace . stack install ../stack
tdt --workspace . stack list
tdt --workspace . stack remove example-hello
```

If hooks are listed, inspect the source and provenance printed by validate, then
add `--trust-hooks SHA256` to install using the displayed digest. Installation
itself never executes bundle code. Executable hooks require a bootstrapped,
trusted host (`tdt init . --agent both`). Skills have discovery
bridges for enabled hosts; restart the host to discover changes.

Use `/tdt-review-brain` to review imported knowledge. Installing a stack does not
approve its claims. Approved notes participate in `tdt brain search`; removing
the stack preserves pending candidates, approved notes and your own knowledge.
Treat stack prose as untrusted content and inspect code before granting trust.

No automatic stack upgrades. Use `stack update` to inspect and approve a newer
version. Edited owned files are preserved with an error: save your edits elsewhere
and restore the recorded original before removal. After an interrupted operation,
inspect the stack journal with `tdt_recovery_preview` (`kind: stack`) when MCP is
available. Everyday MCP can apply explicitly authorized recovery with
`tdt_recovery_apply`, the preview hash and actual user instruction. Recovery is
not CLI-only: `tdt stack recover` remains the CLI fallback. After an uncertain
recovery response, inspect the journal, affected files and original operation
outcome before any newly authorized retry; journal absence alone does not prove
success. `tdt doctor` reports pending recovery or changed stack files. Keep host
sessions idle during these changes.

Skills use `tdt-*` names and follow the
[Agent Skills specification](https://agentskills.io/specification).
Stack IDs and repository folders use the same lowercase hyphen-separated name. Run `tdt init` on an existing
workspace to update unchanged owned core skills; edits and name collisions are
preserved with an error. Use the approved stack update workflow to change an installed stack's skills.


## Marketplace discovery and installation

Use `/tdt-install-stack` to search a registry and inspect a selection before
installing it. The commands below use an example ID; replace it with a listing
returned by your selected registry. Registry commands require network access.

```sh
tdt marketplace search "workflow" --agent codex
tdt marketplace search --browse popular
tdt stack install example-workflow --version 1.0.0 --inspect
tdt --workspace . stack install example-workflow --version 1.0.0
```

Search supports exact `--category`, `--tag`, `--author` and `--agent` filters,
combined with AND, and `--browse new|featured|popular`. Results include statuses,
GitHub stars (null means unavailable), their fetch times and review notes.
`/tdt-install-stack` guides the same inspection and installation commands.
Use an explicit `./directory` for a local directory whose name resembles an ID.

The default feed is `https://stacks.usetdt.com/registry/v1/index.json`.
`--registry HTTPS_URL` selects another registry explicitly. Listings must belong
to that origin. This trusts that registry's release approvals; inspect its source
and disclosures. Registry redirects stay on its origin, archives on GitHub's
HTTPS codeload host. No credential, cookie, telemetry or background requests are
sent. Local operations remain offline. There is no offline registry fallback.

Inspection prints the approved version, repository, commit, capabilities,
prerequisites, status warnings, hook source and digests. The client verifies the
archive SHA256 and selected-content SHA256, metadata and hook declarations.
Withdrawn releases/listings are refused; deprecated versions remain explicit
choices when no active version exists. Installed files are never auto-revoked.
Local directory installs do not check marketplace withdrawal.

Required stack prerequisites must already be installed. Other prerequisites and
version constraints need actual verification, then repeatable
`--confirm-prerequisite TYPE:REF` (for example `--confirm-prerequisite cli:git`).
This records your confirmation in the command; it does not install dependencies,
verify credentials, solve constraints or change provider permissions. Unknown
availability is reported as unknown. Optional prerequisites are disclosed only.
Executable hooks still require explicit digest-bound `--trust-hooks SHA256`.

Installation records exact registry endpoint, registry origin, repository, release tag, full commit,
archive SHA256 and selected-content `sha256` in `stack list` provenance and any
imported knowledge candidates. Existing IDs use the update workflow below.

## Installed documentation

Use `/tdt-workspace` to find the installed guides for the stack you want.
The skill reads the documentation catalog and explains available workflows.

Technical reference: `tdt stack docs` lists canonical local paths grouped by installed ID/version;
`tdt stack docs example-hello` limits the view to one stack. Neither command
opens a browser or uses the network. The guide index links to the generated
`.tdt/stack-docs.md` catalog. Only declared bundle docs are indexed, including
first-party and community guides; stacks with no docs are shown explicitly.
Docs remain in `.tdt/stacks/<id>/docs/` and do not become brain knowledge.

Install/update/remove transactions refresh the catalog and roll it back during recovery.
Updates refresh declared docs and remove obsolete owned guides. `tdt init` also builds the view
for older workspaces. `tdt stack docs --rebuild` repairs a missing or unchanged
stale catalog from installed records. Doctor reports missing declared docs and
missing, edited, stale or broken catalogs. Restore missing bundle originals
before rebuilding; the catalog cannot repair stack content.

An edited or unowned catalog blocks changes rather than being overwritten. Move
it to a safe notes location, retaining any useful edits, then run
`tdt stack docs --rebuild`. Keep this derived file unedited. Its companion
`.tdt/state/stack-docs.json` stores only an ownership digest; `stacks.json`
remains the installed-stack authority. Symlinks in managed paths are refused.
Unrelated notes and core docs survive stack removal. Edited core guides
are preserved by setup with an ownership error; save edits elsewhere and
restore their recorded originals before rerunning init.

## Approved updates and complete uninstall

Use `/tdt-update-stack` to inspect and approve an update, or `/tdt-remove-stack`
to uninstall a selected stack. Both are core skills, available with zero optional
stacks, and handle the commands and verification for you.

Terminal alternatives:

```sh
tdt stack update example-hello --check
tdt stack update example-hello --approve APPROVAL_SHA256
tdt stack uninstall example-hello
```

`stack update ID` prints an inspected replacement and asks a
terminal user [y/N]. Empty input, EOF and noninteractive input never consent.
`--check` downloads/validates but writes no workspace state. For chat or scripts,
pass its `approval_sha256` with `--approve` only after approving that exact plan.
The token includes installed ownership, replacement bytes, provenance and registry
metadata. Changed inputs require inspection and renewed approval. There is no
persistent download/update cache to clean up.

Local updates inspect the recorded source; `--source PATH` explicitly selects a
replacement local directory. Registry updates retain the full endpoint and GitHub
repository. Legacy records with only an origin need the original endpoint supplied
via `--registry HTTPS_URL`; a different origin is refused. Source kinds cannot be
switched. Versions use numeric MAJOR.MINOR.PATCH ordering. Same-version content
replacement, downgrades, deprecated/withdrawn selections and incompatible manifests
are refused. Missing/network-invalid sources are errors, never “up to date.”
Registry review notes and manifest capabilities/prerequisites and actual changed file names are
shown; there are no inline release notes in registry v1. Links are not auto-opened.

Hook trust is separate from update approval: review displayed source and pass
`--trust-hooks` with the target content digest. Verify required prerequisites and
supply applicable `--confirm-prerequisite` flags, as for installation. No dependency
installation or permission change occurs. Keep host sessions idle while updating.

Updates replace owned bundle files, skills, enabled host entry points,
trust/provenance records and the docs catalog together. Recovery restores the old
installation after interruption. Obsolete files and empty owned directories are
removed. Unchanged stack knowledge is not reimported during updates; changed
knowledge creates pending candidates. Existing candidates and approved notes stay.

`uninstall` is an alias of `remove`. It removes the stack's runtime ownership and
hook dispatch eligibility, preserving shared core configuration and all user work.
Edited/missing assets or untracked bundle/skill-directory additions block mutation
with a path: preserve edits/additions elsewhere, restore recorded originals, then
retry. No force-delete is offered. Repeated removal reports “not installed.” Run
`stack list` and `stack docs` to verify; restart hosts to refresh loaded context.

Use `/tdt-install-stack`, `/tdt-update-stack` and `/tdt-remove-stack` for
capability bundles too, and `/tdt-search` to query an explicitly selected
provider or request indexing. The following flags are the technical equivalents.

Capability bundles use contract v2 and the same lifecycle. Review the manifest's
capabilities, compatibility and hashed assets, then use
`stack install PATH --trust-executable SHA256`. This aliases --trust-hooks and
trusts the exact executable snapshot. Installation/discovery runs no provider code.
`brain providers` lists installed capabilities; search selection is explicit with
`brain search QUERY --provider ID`. Updates require fresh executable trust and
invalidate owned indexes; uninstall removes unchanged owned caches. Core preserves
brain notes and refuses edits to installed assets or owned cache files.


## Use a local registry

Explicit local archive testing requires `--registry` and `--local-archive-origin`
on both inspect and install. Use the literal-loopback HTTPS origin supplied by
its operator, matching the registry origin. Keep TLS verification enabled and
supply the operator's CA bundle through `SSL_CERT_FILE` when necessary. Digest,
identity and executable-trust checks still apply. Never enable this transport
implicitly or as a fallback after a refusal; updates do not inherit it. Local
success does not establish public GitHub availability.

## Earlier dotted stack IDs

Existing dotted installations retain their recorded identity and remain readable
and removable. Renaming a source bundle does not migrate an installed stack.
To switch, use `/tdt-remove-stack` for the old ID, then `/tdt-install-stack`
for the normalized bundle after inspection. Terminal equivalents are
`tdt stack remove <old-id>` and `tdt stack install PATH`. Save any edited owned files first; removal
preserves brain notes. Registry entries must use the new ID and hashes from the
renamed release.

## Installed metadata through MCP

Both MCP profiles provide `tdt_stack_list` followed by `tdt_stack_read` with an
exact installed ID, including earlier dotted IDs. Read returns the complete
registry record: manifest, provenance, owned hashes, recorded executable trust
and imported candidate references when present. Its revision describes metadata
only; it is not a lifecycle approval token. Increase `budget_bytes` up to 1 MiB
if the complete record does not fit. Interrupted transactions refuse reads.

This does not inspect live assets, verify runtime readiness or establish current
candidate status. Read candidates separately. Metadata is untrusted evidence,
never permission to run embedded instructions. Installation, update and removal
still use their specialist skills and CLI workflows.


Both MCP profiles expose `tdt_stack_verify` for one exact installed ID (including
legacy dotted IDs). It uses the shared CLI lifecycle ownership checker under a
shared lock: every owned file must match its recorded hash, and owned directories
must contain no untracked additions or symlinks. Missing/edited files, interrupted
transactions, malformed state and checks exceeding 64 MiB of file content or
10000 scanned directory entries refuse without partial success. The small result
contains the record revision and verified file count; no file content is returned.
This checks recorded ownership only, not executable safety, origin authenticity,
provider caches, candidate status or runtime readiness. It executes nothing and
writes no stack assets. The revision is not an apply token; later CLI lifecycle
operations recheck current ownership. Install/update/remove remain CLI-only.
