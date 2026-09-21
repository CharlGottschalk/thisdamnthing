# Architecture

ThisDamnThing is a small Python CLI around a local Markdown knowledge brain. Core works
without stacks, a database or a background service. Optional stacks add domain
workflows or local search providers. [MVP scope](mvp.md) explains the boundaries.

## Where to look

All modules below are in `src/thisdamnthing/`.

| Area | Modules | Responsibility |
| --- | --- | --- |
| Entry points | `cli.py`, `__main__.py` | Parse commands and call core functions. |
| Workspace | `workspace.py`, `bootstrap.py` | Initialize and refresh owned resources. |
| Agents | `hosts.py`, `agents.py` | Detect, enable and disable host integrations. |
| Knowledge | `capture.py`, `brain.py` | Persist candidates, apply review and retrieve approved notes. |
| Projects | `projects.py` | Register external directories and build grounded project context. |
| Policy | `constitution.py` | Read and save reviewed workspace policy. |
| Skills | `skills.py`, `history.py` | Manage reusable-skill proposals and bounded history discovery. |
| Stacks | `stacks.py`, `stack_updates.py`, `stack_docs.py` | Validate, install, update, remove and catalog owned content. |
| Search extensions | `capabilities.py` | Discover and invoke explicitly selected local providers. |
| Marketplace | `marketplace.py` | Validate feeds and fetch explicitly requested archives. |
| UI | `ui.py`, `ui_resources.py` | Serve local questions and return submitted events. |

`resources/workspace/` holds initial workspace files. `resources/harness/` holds
contracts, canonical skills, hooks and context. `resources/docs/` holds installed
usage guides, `resources/ui/` holds browser assets, and `resources/marketplace/`
holds the packaged registry schema. Package-data rules are in `pyproject.toml`.

## Main flows

Initialization writes a brain, `.tdt/` harness and local user docs. Enabled
hosts get thin skill/configuration bridges; `.tdt/` stays canonical. Setup
preserves unrelated content and refuses ownership conflicts.

Capture hooks ask the active agent for a concise sourced summary. Core saves
it as a pending candidate. User review promotes only approved knowledge to
canonical Markdown. Search excludes pending/rejected content, follows bounded
links and returns note references. Host transcripts stay with the host.

Project registration records an external directory and bounded context; it does
not move or edit its source. Later project work follows that project's instructions
and the user's authorization.

Stack installation validates declared files and trust before writing owned
assets. Updates and removal use ownership and recovery records to preserve user
content. Search providers run on demand as trusted local subprocesses; their
indexes are disposable and Markdown stays authoritative. Process separation
is not an OS permission or network sandbox.

UI starts an on-demand local browser service. The active agent waits for events,
reads answers and can ask follow-ups. A browser submission cannot restart a
stopped agent. UI state is separate from approved brain knowledge.

## Shared formats

Follow the [runtime contracts](README.md#runtime-contracts) rather than creating
a second API. Stacks support v1 workflows and v2 capabilities/assets. The
[marketplace contract](marketplace-contract.md) owns public registry requirements.
See the implementation guides in [the index](README.md) for extension patterns
and verification procedures.
