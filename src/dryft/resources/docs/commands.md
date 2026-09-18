# CLI command reference

Use the related skill below for guided work in chat. Names use Claude's `/`
syntax; in Codex use `$` or the skill picker. The CLI column is a secondary
reference for technical users. “Ask your agent” means there is no dedicated skill
for that operation. Skills run the same commands and preserve their review and
trust requirements.

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Run commands from your workspace or a subdirectory. From elsewhere, put
`dryft --workspace "."` before the command. Use `dryft --help`
and `dryft COMMAND --help` for options; nested commands also accept `--help`.
Paths with spaces need shell quotes. Replace example IDs and hashes with actual
values returned by inspection; a placeholder is never approval.

| Skill or chat request | CLI command | Purpose |
| --- | --- | --- |
| Ask your agent to initialize or refresh setup | `dryft init [PATH] --agent both` | Initialize or refresh unchanged owned core files; omit PATH for the current directory. Select `claude`, `codex`, `both` or `none`. |
| `/dryft-workspace` | `dryft doctor` | Check local layout, ownership and recovery state. |
| Ask your agent to enable or disable an integration | `dryft agent enable codex` / `dryft agent disable codex` | Add or remove that workspace-local host integration; also supports `claude`. |
| `/dryft-constitution` | `dryft constitution show` | Read the current workspace policy and revision hash. |
| `/dryft-review-brain` | `dryft brain candidates --status all` | Inspect pending, approved and rejected proposals. Default is pending. |
| Ask your agent to inspect incomplete capture requests | `dryft brain requests` | List incomplete capture requests. |
| `/dryft-search` | `dryft brain search "query" --limit 10 --depth 1` | Retrieve current eligible notes with bounded links. |
| `/dryft-search` with a provider request | `dryft brain providers` | List installed search providers without executing them. |
| `/dryft-search` with an explicit indexing request | `dryft brain index --provider ID --rebuild` | Explicitly rebuild a selected provider index; omit rebuild to reconcile. |
| `/dryft-search` with the selected provider | `dryft brain search "query" --provider ID` | Select a provider for this query; repeat the option to combine rankings. |
| `/dryft-add-project` | `dryft project add PATH` / `dryft project list` | Register an external directory unchanged, or list registrations. |
| `/dryft-add-project` | `dryft project inspect ID` | Reread bounded onboarding evidence. |
| Ask your agent to validate only; also used by `/dryft-install-stack` and optional `/dryft-stack-builder-create` | `dryft stack validate PATH` | Validate a local bundle and inspect disclosures. |
| `/dryft-install-stack` | `dryft stack install PATH` | Install a local bundle; catalog IDs also work when the registry is available. |
| `/dryft-install-stack` with an inspection-only request | `dryft stack install ID --inspect` | Download and verify a catalog release without installing. |
| `/dryft-workspace` | `dryft stack list` / `dryft stack docs ID` | Inspect installed provenance or find a stack's local guides. Omit ID to list all guides. |
| `/dryft-update-stack` | `dryft stack update ID --check` | Inspect a newer replacement without changing workspace state. |
| `/dryft-update-stack` after review | `dryft stack update ID --approve HASH` | Apply the exact inspected and user-approved replacement. |
| `/dryft-remove-stack` | `dryft stack remove ID` | Uninstall owned stack runtime files, preserving brain knowledge; `uninstall` is an alias. |
| Ask your agent to recover an interrupted operation | `dryft stack recover` | Recover an interrupted lifecycle, refresh or host-integration transaction. |
| `/dryft-install-stack` | `dryft marketplace search "query"` | Search the selected HTTPS registry; requires network access. |
| `/dryft-find-skills` for inventory; ask your agent for recovery | `dryft skill list` / `dryft skill recover` | Inspect skills/proposals or recover an interrupted user-skill save. |
| `/dryft-ui` | `dryft ui read SESSION --after 0` | Read retained interview responses. |
| `/dryft-ui` | `dryft ui close SESSION` / `dryft ui cleanup SESSION` | Stop the service, or delete retained session data. |

Review and policy writes require an actual decision on displayed contents. Use
[brain](brain.md), [constitution](constitution.md) and [skills](skills.md) for
proposal, hash and JSON-input details. Executable stack trust is separate from
update approval: see [stacks](stacks.md). For browser start, present, wait and
acknowledgement commands, see [DUI](ui.md).
