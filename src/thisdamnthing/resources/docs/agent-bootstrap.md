# Set up your agents

Run the initial setup from a parent directory outside your projects and source
checkout, then open the created workspace for agent work. Paths are relative to
the current shell directory.

TDT connects Claude Code, Codex or both to one workspace. Install and sign in
to your chosen agent separately. Integrations are scoped to the workspace;
they do not change global agent settings or register skills in linked projects.

## Choose an agent

Ask your agent to set up TDT for Claude, Codex or both, giving the workspace
path. There is no dedicated skill for installation or enabling/disabling hosts.
Once enabled, `/tdt-workspace` checks setup and explains what is available;
it also offers reminder preferences during onboarding, without changing host trust.

Technical setup details follow.

On first setup, `tdt init "./workspace"` detects `claude` and `codex` on
PATH. Use `--agent claude`, `--agent codex`, `--agent both` or `--agent none` to
choose explicitly. Desktop-only apps and executables outside PATH need an explicit
selection. Detection alone does not establish account access or hook trust.

TDT remembers enabled agents in `.tdt/config.json`. Repeating init refreshes
that saved set. A changed PATH does not remove an integration, and `--agent none`
does not disable agents already enabled.

To add an integration later, ask your agent to enable Claude or Codex for this
workspace. Terminal alternatives (choose the host you want):

```sh
tdt agent enable claude
tdt agent enable codex
```

Run from the workspace. Elsewhere, replace `PATH` with the workspace path and use
`tdt --workspace PATH agent enable HOST`. Replace `HOST` with `claude` or `codex`.
Enablement adds instructions, hooks and skill entry points for core, installed
stacks and approved user skills. Repeating the command preserves existing content.

## Open the workspace and review trust

Launch your agent in the workspace root. Review its workspace trust controls and
generated SessionStart, UserPromptSubmit and Stop hook definitions. Inspect `/hooks`
where the host provides it. Other settings layers may disable hooks, and changed
hook definitions may need renewed review.

Invoke `/tdt-workspace` in Claude or `$tdt-workspace` in Codex, or use the
host's skill picker. These guides use `/tdt-*` names; use the corresponding
`$` form or picker in Codex. The skill runs diagnostics for you.

Terminal alternative:

```sh
tdt doctor
```

Doctor checks installed files, ownership and saved integrations. Check actual skill
discovery and hook output in the host as well. Reading `AGENTS.md` or `CLAUDE.md`
does not mean a startup hook ran. If capture is missing, see
[troubleshooting](troubleshooting.md).

## Understand the workspace files

Full skills and context live under `.tdt/`. Enabled agents receive pointers in
`.claude/skills/` or `.agents/skills/`, marked root instruction blocks and entries
in `.claude/settings.json` or `.codex/hooks.json`.

Hooks apply to sessions in this workspace and its subdirectories; outside sessions
are excluded. Startup supplies workspace context, request hooks load the current
[Constitution](constitution.md), and Stop hooks support [knowledge capture](brain.md).
TDT preserves unrelated settings and text outside its owned entries.

## Disable an integration

Ask your agent to disable the selected TDT integration in this workspace.
Terminal alternatives (choose the host you want to disable):

```sh
tdt agent disable claude
tdt agent disable codex
```

Disabling removes only that agent's recorded TDT instruction blocks, hooks and
skill entry points. It keeps the brain, canonical skills, stacks, other agent and
unrelated settings. It does not uninstall the agent application. Repeating disable
is safe; enable adds the integration again.

Start a fresh session after enabling, disabling or changing skills. Existing
sessions may retain previously loaded instructions. Empty settings files and
directories containing user files may remain after disabling.

## Refresh or recover setup

Ask your agent to refresh setup after an upgrade or move, or to inspect an
interrupted operation. These maintenance operations have no dedicated skill.
Use `/tdt-workspace` for diagnostics after recovery.

Technical procedure:

After upgrading TDT or moving the workspace, repeat `tdt init PATH` to refresh
unchanged owned resources and hook paths for saved agents. Keep the Python
environment available and review changed hooks in the host.

Edited or missing owned files, name clashes and managed symlinks cause refusal.
Preserve your changes separately and reconcile them before retrying. Do not delete
ownership records to force a refresh. Older workspaces infer agents from recorded
TDT ownership; unrelated agent directories do not enable an integration.

If a refresh or integration change is interrupted:

1. Keep host sessions idle.
2. If a user-skill save is unfinished, run `tdt skill recover` first.
3. Run `tdt stack recover`.
4. Run `tdt doctor` to check the workspace.
5. If recovery succeeds, retry the original operation.

If initial creation stopped before a valid
workspace configuration was written, preserve the partial folder and inspect it
before retrying in an empty destination. See [workspace care](workspace-care.md).

## Reminder preferences

During onboarding, `/tdt-workspace` offers manual, in-chat, scheduled or combined
reminder delivery and a workspace timezone. Chat checks are opt-in through the
existing request hook; scheduled delivery needs an available external scheduler
and a verified job. See [reminders](reminders.md) for setup and delivery limits.

## Optional MCP registration

Invoke `/tdt-mcp` in Claude Code or `$tdt-mcp` in Codex (or use the skill picker).
The skill asks whether to configure Claude Code, Codex or both, explains the
presets and waits for your choice. You can supply the host and preset up front
or choose different presets for each host. It also supports status and removal.

- **Read-only** (`read-only`, recommended to start): retrieve and inspect workspace
  information and supported previews, without MCP write tools. Explicit marketplace
  reads can fetch registry metadata. Use it for answers and inspection.
- **Everyday** (`everyday`): adds supported writes such as saving notes, reviewing
  knowledge, managing reminders/projects and applying reviewed stack changes. Some
  actions execute explicitly selected trusted local providers. Use it to carry out
  requested workspace tasks through MCP.

These presets select tools; they do not authorize every action. Review requirements
and host permissions still apply. Read-only does not restrict the host shell or
other tools, and neither preset enables automatic capture. Registration works
through the CLI before MCP connects; it does not require an existing MCP server.

Install the MCP extra first (see [commands](commands.md#local-mcp-reads)).
Manual configuration remains
available. Replace `/path/to/workspace` with your initialized workspace path.
These are separate examples; select the operation and host you need:

```sh
tdt --workspace /path/to/workspace mcp register claude
tdt --workspace /path/to/workspace mcp register codex --profile everyday
tdt --workspace /path/to/workspace mcp status codex
tdt --workspace /path/to/workspace mcp unregister codex
```

All MCP commands require explicit `--workspace PATH`, even from the workspace
directory; there is no current-directory fallback. Re-run `mcp register HOST`
with `--profile read-only` or `--profile everyday` to change an intact owned entry
in place. An identical registration is a no-op. A refusal requires inspection and
manual reconciliation, not an automatic unregister/register retry.

Registration defaults to `read-only`; `everyday` must be selected explicitly. It
records the current Python interpreter and absolute workspace path, so run it from
the installation containing the MCP extra. Re-register after moving the workspace
or replacing that environment. Restart the host after changes.

Claude uses the `thisdamnthing` entry in workspace `.mcp.json`; Codex uses a marked
`[mcp_servers.thisdamnthing]` block in workspace `.codex/config.toml`. Ownership lives
in `.tdt/state/mcp.json`. TDT refuses unowned names and edited or missing owned entries.
It also refuses an unowned entry with identical values. Resolve conflicts manually;
registration never adopts them. Unregister removes only the owned entry and leaves
configuration files in place. Claude JSON formatting may change; other settings
retain their values. Codex preserves unrelated text and refuses TOML structures
that cannot safely accommodate its block. Inputs and outputs are capped at 1 MiB
per file. Transactions share the workspace lock and stack recovery journal.
After an interruption, inspect `tdt_recovery_preview` or use `tdt stack recover`.
Then inspect registration status. Status checks saved local ownership.
It does not check the connection or effective settings inherited from other host scopes.

Registration is independent of `tdt agent enable/disable` (skills and capture
hooks). To remove both, unregister MCP and disable the agent separately. It does
not edit global settings, host trust, tool approvals or linked projects, and does
not start a host or enable automatic capture. Review Claude project MCP approval
and Codex project trust yourself; other host configuration layers may override
these entries. Start the host in the workspace; linked external project sessions
do not inherit this registration. See the official
[Codex MCP documentation](https://developers.openai.com/codex/mcp) and
[Claude MCP scopes](https://code.claude.com/docs/en/mcp).
