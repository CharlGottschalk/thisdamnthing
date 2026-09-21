# Troubleshooting and recovery

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Start with `/tdt-workspace` and describe what went wrong. In Codex, use
`$tdt-workspace` or the skill picker. It runs diagnostics and explains the
results; repairs need a separate request. If skills cannot load, ask your agent
to inspect setup using this guide.

Terminal alternative: run `tdt --workspace "." doctor`. Save its output and
the failed command. Doctor checks local paths, ownership and state; it does not
prove host authentication, trust or live hook execution.

The table pairs skill guidance with technical fallback details. Setup and generic
recovery have no dedicated skill; your agent can run those commands for you.

| Symptom | What to do |
| --- | --- |
| `tdt` is not found | Check the pipx installation and its application directory in PATH; reopen the shell after PATH changes. |
| No workspace found | Run from the workspace or put `--workspace PATH` before the subcommand. `doctor` also accepts it after the subcommand. |
| Init refuses the source directory | Choose a separate workspace outside the source checkout and other workspaces. |
| Skills or capture are missing | Repeat init with the intended `--agent`, open a fresh session in the workspace, inspect skill discovery and review installed hooks in the host. Check for disabled hooks in other settings layers. |
| Doctor passes but no candidate appears | Check live Stop output and `tdt brain requests`. The agent may have skipped a turn with nothing durable. File checks alone do not prove hook execution. |
| Search misses a proposal | Use `/tdt-review-brain` to inspect pending candidates and `/tdt-search` to retry the question. Default search uses literal phrases and bounded approved links; try a shorter phrase. For selected providers, check `brain providers` and rebuild the index after changes. |
| Review refuses a stale hash | Use `/tdt-review-brain` to redisplay the candidate and obtain a decision on its current contents; use its new hash. |
| Init/remove reports edited or missing owned files | Save your edits separately and restore the exact recorded version from backup before retrying. Do not delete ownership state or overwrite the edits to suppress the error. |
| A stack operation was interrupted | Ask the active `/tdt-update-stack` or `/tdt-remove-stack` workflow to recover, or ask your agent directly. Keep other host sessions idle. Technical recovery: run `tdt stack recover`, then doctor and retry. Preserve the journal if recovery fails. |
| Workspace is busy | Let the other TDT operation finish, then retry. Do not run simultaneous init or bypass the lock. |
| Project path is unavailable | Restore it at the recorded location or use `/tdt-add-project` to register its new path as a new identity. Approved notes are not automatically refreshed. |
| Registry access fails | Ask `/tdt-install-stack` to explain the failure. Confirm the explicit HTTPS endpoint and connectivity. There is no cached/offline catalog fallback; local directory installation remains available. |
| Archive/digest/withdrawal checks refuse an install | Stop and have the publisher resolve the metadata or release problem. Do not bypass validation. Existing installs are not automatically revoked. |
| A prerequisite is unresolved | Verify the declared tool, stack or other requirement; confirm only what you actually checked. ThisDamnThing does not install dependencies or configure credentials. |
| UI answers seem missing | Use `/tdt-ui` to resume the session. Keep the agent active, read retained events and acknowledge handled IDs. A closed server retains answers until cleanup. See the UI guide for resuming a session. |

Incomplete capture requests can be retried with a safe summary while the source
context is still available, or skipped. Follow [brain recovery](brain.md); never
invent lost facts. Pending candidates can contain sensitive material despite
heuristic filtering: inspect them before approval or sharing.

## Back up, upgrade or move

Ask your agent to help with the operation using [workspace care](workspace-care.md),
then use `/tdt-workspace` to check the result. Technical procedure follows.

With agent sessions and UI services stopped and TDT writes idle, back up the
whole workspace, including hidden harness/provider directories and brain files.
Back up linked project source separately: it lives outside the workspace. Keep
backups private; UI responses and local configuration can contain private data.

After upgrading the CLI or moving the workspace, rerun `tdt init PATH` to
refresh saved integrations. Use `--agent` only when adding a host. Review hook paths
and run doctor before a fresh host session. Init updates unchanged owned core
resources and documentation and preserves unrelated content; it refuses edited
owned files. Use `/tdt-update-stack` for optional stacks (terminal: `tdt stack update`); init does not upgrade them. A move does
not rewrite external project identities or references inside your knowledge.

If a write failed partway through init, preserve a copy of the damaged workspace
and restore a consistent backup. Init is not a general repair tool. Do not remove
`.tdt/` as a repair shortcut: it contains identity, ownership and recovery state.
