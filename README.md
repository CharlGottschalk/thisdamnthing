![Dryft — Agentic Workspace](https://raw.githubusercontent.com/1one8/dryft/HEAD/docs/assets/banner.png)

# Dryft

A local workspace for Claude Code and Codex, with a knowledge brain that grows
with your work and stacks that extend what your agents can do.

> [!NOTE]
> **Version 0.1.0** has only been tested on Linux. Windows and macOS testing is
> underway. You're welcome to try installing it on either platform and report
> what works or any issues you encounter through [GitHub Issues](https://github.com/1one8/dryft/issues).

## Make your workspace your own

| Feature | What you can do |
| --- | --- |
| **Build your brain** | Keep useful facts and decisions as linked Markdown notes. Choose what to remember through review. |
| **Find answers with sources** | Ask your brain questions and get references to approved knowledge. |
| **Give your agents rules** | Set working preferences and boundaries with a workspace Constitution. |
| **Use DUI (Dryft UI)** | Say “use dui” to answer questions and work through choices in a local browser. |
| **Bring your projects** | Link existing project folders and get oriented without moving their source. |
| **Extend with Stacks** | Add skills, workflows and capabilities when you need them. |

## Install and create a workspace

You need Python 3.11+ and pipx. Install Claude Code or Codex separately if you
want an agent integration.

The commands below describe the planned public installation. PyPI publication
and installation from the public registry are still awaiting release verification.

Ask your agent:

> Install and set up Dryft via pipx, create a workspace at [my chosen directory],
> and check it.

Replace the bracketed directory with your preferred location. Setup has no
Dryft skill before installation. Open the created workspace in your agent,
review its workspace and hook trust prompts, and use `/dryft-workspace` in
Claude or `$dryft-workspace` in Codex, or select it from the skill picker.

For terminal setup, run these examples from a parent directory outside your
projects and the Dryft source checkout. Paths are relative to that directory.

```sh
pipx install usedryft
dryft init "./my workspace"
dryft --workspace "./my workspace" doctor
```

You can also `cd` into your chosen folder and run `dryft init` without a path
to initialize the current directory, then run `dryft doctor`.

Choose a workspace folder outside your existing projects. If pipx asks you to
update PATH, follow its instructions and reopen your shell. Dryft starts with
zero stacks and detects Claude and Codex on PATH. Add `--agent claude`,
`--agent codex`, `--agent both` or `--agent none` to `init` to choose explicitly.
Existing unrelated files are preserved; conflicting files are refused.

Read the [usage guides](https://usedryft.com/docs), or open the local guides in
your workspace's `docs/` folder.

---

## Developing Dryft

Working on Dryft itself? Start with the [developer documentation](https://github.com/1one8/dryft/blob/HEAD/docs/README.md)
for setup, architecture and development practices. Open this source checkout in
your agent and say **“onboard me”** for guided development setup.

[Development setup](https://github.com/1one8/dryft/blob/HEAD/docs/development.md) · [Architecture](https://github.com/1one8/dryft/blob/HEAD/docs/architecture.md) ·
[Making a change](https://github.com/1one8/dryft/blob/HEAD/docs/contributing.md)

Licensed under [Apache-2.0](https://github.com/1one8/dryft/blob/HEAD/LICENSE).
