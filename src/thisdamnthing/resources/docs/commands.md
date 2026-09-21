# CLI command reference

Use the related skill below for guided work in chat. Names use Claude's `/`
syntax; in Codex use `$` or the skill picker. The CLI column is a secondary
reference for technical users. “Ask your agent” means there is no dedicated skill
for that operation. Skills run the same commands and preserve their review and
trust requirements.

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Run commands from your workspace or a subdirectory. From elsewhere, put
`tdt --workspace "."` before the command. Use `tdt --help`
and `tdt COMMAND --help` for options; nested commands also accept `--help`.
Paths with spaces need shell quotes. Replace example IDs and hashes with actual
values returned by inspection; a placeholder is never approval.

| Skill or chat request | CLI command | Purpose |
| --- | --- | --- |
| Ask your agent to initialize or refresh setup | `tdt init [PATH] --agent both` | Initialize or refresh unchanged owned core files; omit PATH for the current directory. Select `claude`, `codex`, `both` or `none`. |
| `/tdt-workspace` | `tdt doctor` | Check local layout, ownership and recovery state. |
| Ask your agent to enable or disable an integration | `tdt agent enable codex` / `tdt agent disable codex` | Add or remove that workspace-local host integration; also supports `claude`. |
| `/tdt-constitution` | `tdt constitution show` | Read the current workspace policy and revision hash. |
| `/tdt-review-brain` | `tdt brain candidates --status all` | Inspect pending, approved and rejected proposals. Default is pending. |
| Ask your agent to inspect incomplete capture requests | `tdt brain requests` | List incomplete capture requests. |
| `/tdt-search` | `tdt brain search "query" --limit 10 --depth 1` | Retrieve current eligible notes with bounded links. |
| `/tdt-search` with a provider request | `tdt brain providers` | List installed search providers without executing them. |
| `/tdt-search` with an explicit indexing request | `tdt brain index --provider ID --rebuild` | Explicitly rebuild a selected provider index; omit rebuild to reconcile. |
| `/tdt-search` with the selected provider | `tdt brain search "query" --provider ID` | Select a provider for this query; repeat the option to combine rankings. |
| `/tdt-add-project` | `tdt project add PATH` / `tdt project list` | Register an external directory unchanged, or list registrations. |
| `/tdt-add-project` | `tdt project inspect ID` | Reread bounded onboarding evidence. |
| Ask your agent to validate only; also used by `/tdt-install-stack` and optional `/tdt-stack-builder-create` | `tdt stack validate PATH` | Validate a local bundle and inspect disclosures. |
| `/tdt-install-stack` | `tdt stack install PATH` | Install a local bundle; catalog IDs also work when the registry is available. |
| `/tdt-install-stack` with an inspection-only request | `tdt stack install ID --inspect` | Download and verify a catalog release without installing. |
| `/tdt-workspace` | `tdt stack list` / `tdt stack docs ID` | Inspect installed provenance or find a stack's local guides. Omit ID to list all guides. |
| `/tdt-update-stack` | `tdt stack update ID --check` | Inspect a newer replacement without changing workspace state. |
| `/tdt-update-stack` after review | `tdt stack update ID --approve HASH` | Apply the exact inspected and user-approved replacement. |
| `/tdt-remove-stack` | `tdt stack remove ID` | Uninstall owned stack runtime files, preserving brain knowledge; `uninstall` is an alias. |
| Ask your agent to recover an interrupted operation | `tdt stack recover` | Recover an interrupted lifecycle, refresh or host-integration transaction. |
| `/tdt-install-stack` | `tdt marketplace search "query"` | Search the selected HTTPS registry; requires network access. |
| `/tdt-find-skills` for inventory; ask your agent for recovery | `tdt skill list` / `tdt skill recover` | Inspect skills/proposals or recover an interrupted user-skill save. |
| `/tdt-ui` | `tdt ui read SESSION --after 0` | Read retained interview responses. |
| `/tdt-ui` | `tdt ui close SESSION` / `tdt ui cleanup SESSION` | Stop the service, or delete retained session data. |

Review and policy writes require an actual decision on displayed contents. Use
[brain](brain.md), [constitution](constitution.md) and [skills](skills.md) for
proposal, hash and JSON-input details. Executable stack trust is separate from
update approval: see [stacks](stacks.md). For browser start, present, wait and
acknowledgement commands, see [UI](ui.md).
