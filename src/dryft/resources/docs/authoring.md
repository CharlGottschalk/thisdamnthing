# Create and share a stack

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

First-party and community stacks use the same [public contract](../.dryft/contracts/stack.md)
and installer. Work in a separate source directory. Core installs no stack source.
## Create through your agent

For guided authoring, install the optional Stack Builder through
`/dryft-install-stack`, supplying its local source directory or selecting an
available registry listing. In a fresh host session, use
`/dryft-stack-builder-create` and describe the workflow you want. The skill
creates the bundle and runs validation for you. Use
`/dryft-stack-builder-publish` when you want help preparing a release; marketplace
submission still uses the website. Ask `/dryft-workspace` to find the builder's
installed guide and available skills.

These names use Claude's invocation syntax. In Codex, use `$dryft-…` with the
same skill name or select it through the skill picker.

`dryft stack validate PATH` belongs to core, so it also works without Stack
Builder. The builder's create skill and core's `/dryft-install-stack` both use it
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
  "skills": ["skills/dryft-example-hello/SKILL.md"],
  "hooks": [],
  "knowledge": []
}
```

Create `skills/dryft-example-hello/SKILL.md`:

```markdown
---
name: dryft-example-hello
description: Give a greeting when the user requests this example workflow.
---

Ask for the user's name if missing, then greet them by name.
```

Replace the example identity, author and license before distribution. The
example's `UNLICENSED` value is a placeholder, not a license grant. Only files
explicitly listed in the manifest are selected. Optional `templates` and `docs`
arrays can select supporting files; keep references relative to the installed
bundle at `.dryft/stacks/<stack-id>/`. Use that canonical workspace-relative
path in projected skills, whose directory differs from the bundle. Declared docs
appear in `.dryft/stack-docs.md`; they are not copied into workspace `docs/`.
Validate every local guide link from an installed scratch bundle, including
linked supporting files, before publishing. Stack IDs use lowercase hyphen-separated names; skills use matching `dryft-*` directories
and frontmatter names. See the contract for field limits and hook payloads.

```sh
dryft stack validate "../example-hello"
dryft --workspace "../scratch workspace" stack install "../example-hello"
```

Open a fresh host session, invoke the skill, then remove the stack and check that
user notes remain. Add hooks only when the workflow needs executable behavior;
inspect their source, disclose capabilities and use the explicit digest trust
flow. Imported knowledge becomes pending review, never automatically approved.

For browser interviews, reuse core [DUI](ui.md) and its
[contract](../.dryft/contracts/ui.md). Put optional interview JSON in a listed
template; do not create a second server or response protocol.

## Marketplace publication

Use the marketplace website's submission flow when it is available; Dryft has no
CLI submission command. The website handles author accounts, release submissions,
review and listings.

Prepare a public GitHub repository and a release whose version matches
`stack.json`. Registry metadata records the approved tag, immutable commit,
archive and selected-content digests, capabilities and prerequisites. Dependencies
belong in listing metadata, not new fields in the strict v1 stack manifest.
Submissions require review before approval. Use the website's submission flow
when available; creating a local bundle or draft submission does not publish it.

## Capability stacks

Use stack contract v2 for executable `brain.search` providers; see
`.dryft/contracts/stack.md` for the complete schema, JSON protocol, budgets and
cache lifecycle. Keep implementation/model/runtime assets in your separate stack
repository, explicitly list every file with byte size/SHA256 and ship required
third-party licenses. Do not add dependencies to core or run install scripts.
Declare only platform/Python combinations demonstrated offline. V1 workflow stacks
remain valid unchanged. Inspect, trust, install, query, update and remove a local
artifact before publication. Hosting a large binary artifact must satisfy the marketplace size and
compatibility contract. Validation alone does not publish the bundle.
