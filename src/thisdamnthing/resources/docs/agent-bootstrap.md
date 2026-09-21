# Set up your agents

Run the initial setup from a parent directory outside your projects and source
checkout, then open the created workspace for agent work. Paths are relative to
the current shell directory.

ThisDamnThing can connect Claude Code, Codex or both to one workspace. Install and sign in
to your chosen agent separately. ThisDamnThing's integrations are local to the workspace;
they do not change global agent settings or register skills in linked projects.

## Choose an agent

Ask your agent to set up ThisDamnThing for Claude, Codex or both, giving the workspace
path. There is no dedicated skill for installation or enabling/disabling hosts.
Once enabled, `/tdt-workspace` checks setup and explains what is available;
it does not change integrations or host trust.

Technical setup details follow.

On first setup, `tdt init "./workspace"` detects `claude` and `codex` on
PATH. Use `--agent claude`, `--agent codex`, `--agent both` or `--agent none` to
choose explicitly. Desktop-only apps and executables outside PATH need an explicit
selection. Detection alone does not establish account access or hook trust.

ThisDamnThing remembers enabled agents in `.tdt/config.json`. Repeating init refreshes
that saved set. A changed PATH does not remove an integration, and `--agent none`
does not disable agents already enabled.

To add an integration later, ask your agent to enable Claude or Codex for this
workspace. Terminal alternatives (choose the host you want):

```sh
tdt agent enable claude
tdt agent enable codex
```

Run from the workspace, or prefix the command with `tdt --workspace PATH`.
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
ThisDamnThing preserves unrelated settings and text outside its owned entries.

## Disable an integration

Ask your agent to disable the selected ThisDamnThing integration in this workspace.
Terminal alternatives (choose the host you want to disable):

```sh
tdt agent disable claude
tdt agent disable codex
```

Disabling removes only that agent's recorded ThisDamnThing instruction blocks, hooks and
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

After upgrading ThisDamnThing or moving the workspace, repeat `tdt init PATH` to refresh
unchanged owned resources and hook paths for saved agents. Keep the Python
environment available and review changed hooks in the host.

Edited or missing owned files, name clashes and managed symlinks cause refusal.
Preserve your changes separately and reconcile them before retrying. Do not delete
ownership records to force a refresh. Older workspaces infer agents from recorded
ThisDamnThing ownership; unrelated agent directories do not enable an integration.

After an interrupted refresh or integration change, keep host sessions idle and
run `tdt stack recover`, then doctor and retry. An unfinished user-skill save
needs `tdt skill recover` first. If initial creation stopped before a valid
workspace configuration was written, preserve the partial folder and inspect it
before retrying in an empty destination. See [workspace care](workspace-care.md).
