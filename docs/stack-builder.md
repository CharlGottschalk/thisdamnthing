# Authoring with Stack Builder

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

`tdt-stack-builder` is an optional stack maintained in its own repository.
Core ships the stack contract and installer; authoring templates belong to the
builder bundle.

## Install the authoring workflow

```sh
tdt stack validate ../tdt-stack-builder
tdt --workspace ../workspace stack install ../tdt-stack-builder
```

Start a fresh host session and invoke `tdt-stack-builder-create` through its
skill interface. Supply the purpose, a new target directory outside the workspace,
normalized stack ID, author, license and desired skill behavior. Read the installed
bundle's guide for supported authoring options.

## Keep a small explicit bundle

Start with one skill and add hooks, knowledge or capabilities only when needed.
Use a normalized stack ID such as `example-greeter` and a matching Agent Skills directory
such as `tdt-example-greet`. List selected files explicitly in `stack.json`.
A Python file selected as an inert template must not become an executable hook.

The builder can gather missing details through core UI or chat. Reuse submitted
answers when switching interfaces and skip questions already answered by the brief.
Keep generated source outside the installed workspace, and refuse to overwrite
existing target content.

Run public validation on the result. Installation is a separate requested action;
executable hooks or providers also require exact-content trust. Draft registry
metadata stays outside the stack manifest and does not constitute publication.

## Prepare a release

Invoke `/tdt-stack-builder-publish` (Codex: `$tdt-stack-builder-publish`) with
the source directory and intended version. The builder checks the stack contract,
PII/security and repository/listing metadata, prepares release notes, and offers
Git tag creation/push and `gh` publication for the checked commit once the whole
worktree is clean. Missing or declined `gh` leads to a manual release checklist.

The installed bundle's `docs/publishing.md` covers history and archive review,
version agreement, immutable release verification and partial-failure recovery.
Authors visit https://stacks.usethisdamnthing.com to submit the verified release for review;
the skill does not perform marketplace submission or approval.

## Change the builder safely

Update templates and authoring instructions together. Check generated names,
manifest file selection and links against the
[stack contract](../src/thisdamnthing/resources/harness/contracts/stack.md). Use core
[UI](ui.md) and [capability](stack-capabilities.md) interfaces instead of adding
parallel runtime mechanisms.

Generate a harmless bundle into an empty directory, validate and install it through
the public CLI, then invoke its skill in a fresh host session. Check overwrite
refusal and preservation of the original target. Remove the generated stack and
confirm user knowledge remains. Treat builder instructions as an agent workflow;
host permissions still govern file access and execution.
