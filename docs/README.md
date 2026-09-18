# Dryft development

These guides explain how to change Dryft, extend its contracts and verify its
behavior. User guides live in
[src/dryft/resources/docs](../src/dryft/resources/docs/README.md) and are installed
into each workspace.

## Get started

You need Python 3.11+ and Git. Open the source checkout in Claude Code or Codex
and say **“onboard me”**, or follow [development setup](development.md).
Read the [development constitution](../.dev/CONSTITUTION.md) and
[product scope](mvp.md) before changing the product.

Keep shipped code in `src/`, development tooling in `.dev/` and developer guides
here. Use disposable workspaces for manual checks. Optional stacks have separate
source repositories and use the same contract and installer as community stacks.

## Development practices

| Guide | Use it to |
| --- | --- |
| [Development setup](development.md) | Configure local tools, agent startup and repository Git safeguards. |
| [Making a change](contributing.md) | Implement a bounded change and check preservation and failure behavior. |
| [Architecture](architecture.md) | Locate modules and follow the main data flows. |
| [Product scope](mvp.md) | Understand core boundaries, workspace layout and shared formats. |
| [Documentation maintenance](documentation.md) | Write and maintain developer and installed user guides. |
| [Packaging and release](releasing.md) | Inspect a wheel, verify installation and publish an authorized release. |
| [Release readiness](release-readiness.md) | Check compatibility limits and the publication checklist. |
| [Component verification](acceptance.md) | Choose focused manual checks for a change. |
| [Workspace walkthrough](e2e-runbook.md) | Verify the installed product across a complete workflow. |

## Implementation guides

| Area | Guides |
| --- | --- |
| Agents and skills | [Host adapters](agent-adapters.md), [enable and disable integrations](agent-enablement.md), [reusable skills and history discovery](skill-discovery.md) |
| Rules and privacy | [Workspace constitution](workspace-constitution.md), [project constitution and privacy integration](constitution-privacy-integration.md), [staged-content privacy review](privacy-review.md) |
| Stacks | [Authoring with Stack Builder](stack-builder.md), [Software Production integration](software-production.md), [lifecycle and recovery](stack-lifecycle.md), [documentation catalog](stack-documentation.md), [search capabilities](stack-capabilities.md) |
| Browser interaction | [DUI sessions and custom pages](ui.md) |
| Registry integration | [Marketplace client](marketplace.md) |

## Runtime contracts

Use the packaged contracts when changing shared formats:
[stacks](../src/dryft/resources/harness/contracts/stack.md),
[capture events](../src/dryft/resources/harness/contracts/capture-event.md) and
[DUI](../src/dryft/resources/harness/contracts/ui.md).
The [marketplace contract](marketplace-contract.md) defines registry behavior.
Keep the public [schema](../src/marketplace/registry.schema.json) and its
[packaged copy](../src/dryft/resources/marketplace/registry.schema.json) identical.
