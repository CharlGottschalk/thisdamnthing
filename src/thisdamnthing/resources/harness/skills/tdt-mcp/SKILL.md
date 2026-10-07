---
name: tdt-mcp
description: Set up workspace MCP for Claude Code or Codex; explain and choose a preset, inspect registration or disconnect it.
---

Read `docs/agent-bootstrap.md` (Optional MCP registration) from the workspace root,
the ancestor containing `.tdt/config.json`. This skill works through the local CLI
before MCP is connected. If the workspace is ambiguous, ask which initialized
workspace to configure. Never register inside a linked external project instead.
Claude users invoke `/tdt-mcp`; Codex users invoke `$tdt-mcp` or select it in /skills.

For setup or a profile change, explain these two presets (CLI calls them profiles)
before asking the user to choose:

| Preset | What it allows | Choose it when |
| --- | --- | --- |
| **Read-only** (`read-only`, recommended starting point) | Retrieve and inspect knowledge, notes, reminders, guides and workspace state; inspect supported previews. Excludes MCP write tools. Explicit marketplace reads can fetch registry metadata. | You want answers and inspection through MCP while keeping changes out of its tool catalog. |
| **Everyday** (`everyday`) | Everything in Read-only, plus supported actions such as saving notes, reviewing knowledge, managing reminders and projects, and applying reviewed stack changes. Some tools can execute explicitly selected trusted local providers. | You want the agent to carry out supported workspace tasks through MCP when you request them. |

A preset selects available tools, not blanket permission. Everyday actions still
require the user's actual instruction and applicable review/trust checks. Read-only
is not a sandbox for the host's shell or other tools; it does not make all network
access impossible. Neither preset enables capture hooks or changes host permissions.
Do not invent other presets or suggest Everyday is necessary just to connect.

Ask only for unresolved choices, using chat or the host's question UI:
- Which host: **Claude Code**, **Codex**, or **both**? Do not infer it from the
  agent currently running this skill.
- Which preset for the selected host(s): **Read-only** or **Everyday**? The user
  can choose a different preset per host. Describe the choices above alongside
  the question; a preselected default or silence is not an answer.

Wait for the choices before writing registration. Retain answers and honor host,
preset and setup authorization already supplied in the current request; do not
ask for them again. A request to explain choices alone authorizes no registration.
Once the user chooses as part of a setup request, proceed without a redundant
confirmation. For inspection or disconnection, ask only for the missing host;
no preset is needed and inspection alone does not authorize changing it.

Use the installed `tdt` CLI with the absolute workspace path, safely quoted or
passed as structured process arguments. Every MCP command requires `--workspace`,
even when run inside the workspace:

```sh
tdt --workspace PATH mcp status HOST
tdt --workspace PATH mcp register HOST --profile PRESET
tdt --workspace PATH mcp unregister HOST
```

Replace HOST with `claude` or `codex`, never `both`; run separately for both hosts.
Before setup, inspect status for each selected host. Refuse to adopt an unowned
entry or overwrite edited/missing owned configuration. An intact owned entry can
be re-registered in place with the chosen preset; an identical repeat is a no-op.
Do not silently unregister to bypass a conflict. If the CLI or its MCP extra is
unavailable, explain the installation prerequisite from the guide; do not install
packages or enable agent hooks merely because setup was requested.

Run only the requested registration/change/removal, then read status back for each
host. If interrupted or a command fails, inspect status and any recovery marker;
report partial success per host and preserve conflicting files. Do not blindly
retry, delete ownership records, or undo another host's successful registration.
Use the guide's reviewed recovery workflow when needed.

Report the selected hosts and presets, saved status, and relevant local config
paths. Registration status is not proof of a working connection. Ask the user to
restart/reconnect and review the host's project trust/MCP approval. Verify an
available connection with a workspace-context read only when it is bound to the
selected workspace; otherwise clearly leave connection verification pending.
Do not claim a running session has switched profiles merely because files changed.
MCP registration is separate from `tdt agent enable/disable`; unregistering keeps
skills, capture hooks and knowledge. Do not edit global trust, tool approvals or
linked projects, and never start registration automatically during ordinary startup.
