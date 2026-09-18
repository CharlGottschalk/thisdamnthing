# Documentation maintenance

## Put the guide where its reader needs it

| Location | Reader and purpose |
| --- | --- |
| Root `README.md` | Users choosing and installing Dryft; short features and setup. |
| Root `docs/` | Contributors: setup, architecture, implementation patterns and verification procedures. |
| `src/dryft/resources/docs/` | Users: guides installed into each workspace's `docs/`. |
| `src/dryft/resources/workspace/README.md` | Users opening an initialized workspace. |
| `src/dryft/resources/harness/contracts/` | Implementers and stack authors sharing formats. |
| `.dev/` records and ignored `.dev/local/` | Development coordination, execution results and private local evidence. |
| Separate stack repositories | Stack-specific usage, templates and authoring guidance. |

Full web usage docs will be at [usedryft.com/docs](https://usedryft.com/docs).
This source repository does not publish that site. Coordinate website changes
separately; do not describe a planned page as verified live.

## Keep it simple

User installation guidance should use `pipx install usedryft` and offer asking an
agent to install and set up Dryft via pipx. Keep cloning, source installation and
manual wheel installation in development guidance. Label the public command as
planned until the intended PyPI release is available.

Lead with what the reader can do. In user guides, lead with the related installed
skill and keep CLI commands as secondary technical instructions. Use Claude's
`/dryft-*` notation and explain Codex's `$` form or skill picker. When no dedicated
skill exists, offer a plain-language agent request without inventing a skill.
Keep setup usable before skills are installed, and preserve the command reference
for technical users. Use short steps and real command syntax.
Explain a technical detail only when it helps someone act or understand a limit.
Use portable placeholders, harmless examples and relative links. Keep personal
identity, machine paths and raw observations in ignored local files.

When behavior changes, update the installed guide and relevant design/contract
guide together. Add new development pages to [the index](README.md). Keep root
developer docs procedural: explain current behavior, commands, contracts and
practices. Exclude dated observations, implementation chronology, development
work-item references, PR summaries and completed-check reports. Store execution
records under `.dev/`; never turn an unrun check into a support claim.

## Check before delivery

Read each changed guide as its intended reader. Check local links and command
options against `PYTHONPATH=src python3 -m dryft --help` and subcommand help.
For changed installed resources, inspect a built wheel and initialize a disposable
workspace to confirm they ship and links work. For root docs-only changes, no
package build is needed. Run `git diff --check` and include actual checks in the
review summary.
