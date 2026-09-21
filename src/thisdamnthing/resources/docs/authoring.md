# Create and share a stack

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

First-party and community stacks use the same [public contract](../.tdt/contracts/stack.md)
and installer. Work in a separate source directory. Core installs no stack source.
## Create through your agent

For guided authoring, install the optional Stack Builder through
`/tdt-install-stack`, supplying its local source directory or selecting an
available registry listing. In a fresh host session, use
`/tdt-stack-builder-create` and describe the workflow you want. The skill
creates the bundle and runs validation for you. Use
`/tdt-stack-builder-publish` when you want help preparing a release; marketplace
submission still uses the website. Ask `/tdt-workspace` to find the builder's
installed guide and available skills.

These names use Claude's invocation syntax. In Codex, use `$tdt-…` with the
same skill name or select it through the skill picker.

`tdt stack validate PATH` belongs to core, so it also works without Stack
Builder. The builder's create skill and core's `/tdt-install-stack` both use it
for local bundles. There is no dedicated validation-only skill; you can ask your
agent, “Validate the stack at `../example-hello` and explain the results without
installing it.” The agent runs the command; you do not need to type it in a terminal.

## Create manually

The contract example below works with zero stacks. Commands are provided for
users who prefer the terminal and for agents carrying out the workflow.

Create a sibling directory `../example-hello`; put the following `stack.json`
and skill file inside it:

```json
{
  "contract_version": 1,
  "id": "example-hello",
  "version": "1.0.0",
  "description": "A small greeting workflow",
  "author": "Example author",
  "license": "UNLICENSED",
  "skills": ["skills/tdt-example-hello/SKILL.md"],
  "hooks": [],
  "knowledge": []
}
```

Create `skills/tdt-example-hello/SKILL.md`:

```markdown
---
name: tdt-example-hello
description: Give a greeting when the user requests this example workflow.
---

Ask for the user's name if missing, then greet them by name.
```

Replace the example identity, author and license before distribution. The
example's `UNLICENSED` value is a placeholder, not a license grant. Only files
explicitly listed in the manifest are selected. Optional `templates` and `docs`
arrays can select supporting files; keep references relative to the installed
bundle at `.tdt/stacks/<stack-id>/`. Use that canonical workspace-relative
path in projected skills, whose directory differs from the bundle. Declared docs
appear in `.tdt/stack-docs.md`; they are not copied into workspace `docs/`.
Validate every local guide link from an installed scratch bundle, including
linked supporting files, before publishing. Stack IDs use lowercase hyphen-separated names; skills use matching `tdt-*` directories
and frontmatter names. See the contract for field limits and hook payloads.

```sh
tdt stack validate "../example-hello"
tdt --workspace "../scratch workspace" stack install "../example-hello"
```

Open a fresh host session, invoke the skill, then remove the stack and check that
user notes remain. Add hooks only when the workflow needs executable behavior;
inspect their source, disclose capabilities and use the explicit digest trust
flow. Imported knowledge becomes pending review, never automatically approved.

For browser interviews, reuse core [UI](ui.md) and its
[contract](../.tdt/contracts/ui.md). Put optional interview JSON in a listed
template; do not create a second server or response protocol.

## Marketplace publication

Use the marketplace website's submission flow when it is available; ThisDamnThing has no
CLI submission command. The website handles author accounts, release submissions,
review and listings.

Prepare a public GitHub repository and a release whose version matches
`stack.json`. The registry resolves capabilities and prerequisites from stack.json at the approved
commit. The database records listing presentation/category, release references, digests,
review records and indexed tags from the pinned manifest. Dependencies
belong in the marketplace object in stack.json.
Submissions require review before approval. Use the website's submission flow
when available; creating a local bundle or draft submission does not publish it.

## Capability stacks

Use stack contract v2 for executable `brain.search` providers; see
`.tdt/contracts/stack.md` for the complete schema, JSON protocol, budgets and
cache lifecycle. Keep implementation/model/runtime assets in your separate stack
repository, explicitly list every file with byte size/SHA256 and ship required
third-party licenses. Do not add dependencies to core or run install scripts.
Declare only platform/Python combinations demonstrated offline. V1 workflow stacks
remain valid unchanged. Inspect, trust, install, query, update and remove a local
artifact before publication. Hosting a large binary artifact must satisfy the marketplace size and
compatibility contract. Validation alone does not publish the bundle.

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
