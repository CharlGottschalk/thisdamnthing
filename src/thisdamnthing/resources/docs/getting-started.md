# Getting started

Setup starts in a parent directory outside your projects and the ThisDamnThing source
checkout. After `cd`, the remaining commands run from the new workspace root.

ThisDamnThing gives your agent a local knowledge workspace. You can capture and review
knowledge, link existing projects and add stacks as you need them.

## Install ThisDamnThing

You need Python 3.11 or later and pipx in your shell. Install Claude Code or Codex
separately if you want an agent integration, including its account access and
subscription. Linux is the initial target; do not assume macOS or native Windows
compatibility.

Ask your agent to handle setup:

> Install ThisDamnThing using its release instructions, create a workspace at my chosen
> directory, and check it.

There is no ThisDamnThing setup skill before installation. Once the workspace is ready,
use `/tdt-workspace` to check it. Throughout these guides, Codex users can use
`$` in place of `/` for skill names, or use the skill picker.

For terminal setup, the public installation command, once the ThisDamnThing release is
available on PyPI, is:

```sh
pipx install thisdamnthing
tdt --version
tdt --help
```

The Python package is named `thisdamnthing`; the terminal command is `tdt`.
Follow the release's installation instructions for the package you are using.
If you are working from a supplied source checkout, run `pipx install .` from that
checkout. If pipx asks you to update PATH, follow its instructions and reopen your
shell. Keep the pipx environment installed: workspace hooks use its interpreter.

## Create your workspace

Choose a folder outside your existing projects, any other ThisDamnThing workspace and
the ThisDamnThing source checkout. Give your agent the chosen path and ask it to create
the workspace. For terminal setup, replace the example path with your own:

```sh
tdt init "./my workspace"
tdt --workspace "./my workspace" doctor
cd "./my workspace"
```

If you have already used `cd` to enter your chosen folder, run `tdt init`
without a path to initialize that folder, then run `tdt doctor`.

Initial setup detects Claude and Codex on PATH. Add `--agent claude`, `--agent codex`
or `--agent both` to select explicitly, or `--agent none` to start with only the
CLI and UI. You can enable an agent later. A new workspace has no installed
stacks or registered projects.

Open a fresh agent session in this folder. Review workspace trust and generated
hooks through your host's controls. Invoke `/tdt-workspace` in Claude or
`$tdt-workspace` in Codex, or select the skill through the host's picker.
See [agent setup](agent-bootstrap.md) if skills or hooks are missing.

## Save and find a decision

Discuss a useful decision with your agent, such as your team's weekly planning
day. With capture hooks enabled and trusted, ThisDamnThing asks the active agent for a
concise summary after the turn. That extra continuation is visible in the chat.
The summary becomes a proposal awaiting your review; a turn with nothing worth
retaining may be skipped.

Use `/tdt-review-brain` to approve, reject or edit proposals. Edits still need
approval. You can inspect the queue from the terminal:

```sh
tdt brain candidates
```

Then use `/tdt-search` to ask about the decision. Answers should cite approved
notes and acknowledge missing or conflicting information. Direct search is also
available:

```sh
tdt brain search "planning" --limit 10 --depth 1
```

Pending and rejected proposals stay out of ordinary search. See
[capture and review](brain.md) for review commands and recovery.

## Set your working preferences

Use `/tdt-constitution` to give your agents rules, such as when to ask before
opening websites or accessing external folders. Review the proposed wording
before saving it. These rules guide agent behavior; your host's permissions
still apply. See [workspace constitution](constitution.md).

Say “use ui” when you prefer questions in a local browser. Keep your agent active
so it can read the submitted answers and continue. You can answer in chat instead.
See [UI](ui.md).

## Link an existing project

Use `/tdt-add-project` with the project's path to register it and get an
explanation of its purpose and structure. Registration leaves its source where it
is and does not edit it. Review any proposed project knowledge through
`/tdt-review-brain`. See [projects](projects.md).

Terminal alternative:

```sh
tdt project add "../existing project"
tdt project list
```

## Add a stack

Use `/tdt-install-stack` for guided discovery and installation, including local
bundles. Use `/tdt-workspace` to find installed stack guides.

Terminal alternative for a local bundle:

```sh
tdt stack validate "../stack bundle"
tdt stack install "../stack bundle"
tdt stack docs
```

Inspect executable content and approve its exact digest when required. Start a
fresh agent session to discover installed skills. Each stack's guides explain its
workflow; [stacks](stacks.md) covers installation, updates and removal.

Keep backups before upgrades or moving your workspace. See
[workspace care](workspace-care.md) and [troubleshooting](troubleshooting.md).
