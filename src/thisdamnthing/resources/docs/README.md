# Your TDT workspace

Run the setup examples from a parent directory outside your projects and the
TDT source checkout. Paths are relative to that directory.

ThisDamnThing is a persistent local workspace for AI agents. Your reviewed
knowledge, Constitution, linked projects and reusable skills stay with the
workspace across sessions and when you switch between Claude Code and Codex.
The active agent does the work; TDT keeps the context in files you own.

Knowledge stays in readable Markdown, and linked projects stay at their existing
paths. Optional Stacks package skills, workflows, knowledge, templates and local
capabilities. A new workspace has zero stacks and zero registered projects.

Use skills in your agent for everyday work. These guides show Claude's
`/tdt-*` names; in Codex use the same name with `$` or the skill picker.
The agent runs the underlying commands for you. Terminal examples are secondary
instructions for technical users. Setup and some maintenance operations have no
dedicated skill; you can ask your agent to carry them out.

Start with [getting started](getting-started.md), then use these guides:

- [Core skills](core-skills.md)
- [Agent setup and trust](agent-bootstrap.md)
- [Workspace constitution and permissions](constitution.md)
- [Save and reuse workflows](skills.md)
- [CLI command reference](commands.md)
- [Backups, upgrades and private data](workspace-care.md)
- [Capture, review and search your brain](brain.md)
- [One-time reminders](reminders.md)
- [External projects and onboarding](projects.md)
- [Local stacks and marketplace installation](stacks.md)
- [Installed stack documentation](../.tdt/stack-docs.md)
- [Creating and sharing a stack](authoring.md)
- [UI browser interviews](ui.md)
- [Troubleshooting and recovery](troubleshooting.md)

`brain/` holds knowledge; `.tdt/` holds skills, configuration and working state;
`docs/` holds these guides. Provider instructions and skill bridges point into
`.tdt/`. Keep the workspace outside the TDT source repository and keep your
external projects at their original locations.

Use `/tdt-workspace` to inspect the workspace and explain diagnostics.
For a terminal check, run `tdt doctor` from the workspace or a subdirectory. Elsewhere, use
`tdt --workspace "./my workspace" doctor`. A healthy file layout does
not prove that your host has trusted or executed its hooks.

Initialization preserves unrelated files and refuses ownership conflicts and
managed-path symlinks. Ask your agent to refresh core resources after an upgrade.
For technical users, repeat `tdt init` to update unchanged owned core
resources and guides; it does not repair arbitrary missing or edited files.
Back up your workspace before upgrades and see [recovery](troubleshooting.md).
