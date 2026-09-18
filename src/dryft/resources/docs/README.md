# Your Dryft workspace

Run the setup examples from a parent directory outside your projects and the
Dryft source checkout. Paths are relative to that directory.

Dryft keeps reviewed knowledge in local Markdown and links projects at their
existing paths. Claude or Codex supplies the active agent; optional stacks add
workflows. A new workspace has zero stacks and zero registered projects.

Use skills in your agent for everyday work. These guides show Claude's
`/dryft-*` names; in Codex use the same name with `$` or the skill picker.
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
- [External projects and onboarding](projects.md)
- [Local stacks and marketplace installation](stacks.md)
- [Installed stack documentation](../.dryft/stack-docs.md)
- [Creating and sharing a stack](authoring.md)
- [DUI browser interviews](ui.md)
- [Troubleshooting and recovery](troubleshooting.md)

`brain/` holds knowledge; `.dryft/` holds skills, configuration and working state;
`docs/` holds these guides. Provider instructions and skill bridges point into
`.dryft/`. Keep the workspace outside the Dryft source repository and keep your
external projects at their original locations.

Use `/dryft-workspace` to inspect the workspace and explain diagnostics.
For a terminal check, run `dryft doctor` from the workspace or a subdirectory. Elsewhere, use
`dryft --workspace "./my workspace" doctor`. A healthy file layout does
not prove that your host has trusted or executed its hooks.

Initialization preserves unrelated files and refuses ownership conflicts and
managed-path symlinks. Ask your agent to refresh core resources after an upgrade.
For technical users, repeat `dryft init` to update unchanged owned core
resources and guides; it does not repair arbitrary missing or edited files.
Back up your workspace before upgrades and see [recovery](troubleshooting.md).
