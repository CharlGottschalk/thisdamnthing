![ThisDamnThing](https://raw.githubusercontent.com/CharlGottschalk/thisdamnthing/HEAD/docs/assets/banner.png)

> First I called it **Dryft**, but that was taken.<br>
> Then I tried **Ryft**. Taken.<br>
> **Seska?** Ugh.<br>
> **Ardra?** Dammit!.<br>
> **Laya?** Of course that's taken.<br>
> And on and on and on..<br>
> Eventually I said "screw it!".<br>
> So just use **ThisDamnThing**.

# ThisDamnThing

A local workspace for Claude Code and Codex, with a knowledge brain that grows
with your work and stacks that extend what your agents can do.

> [!NOTE]
> **Version 0.1.0** has only been tested on Linux. Windows and macOS testing is
> underway. You're welcome to try installing it on either platform and report
> what works or any issues you encounter through [GitHub Issues](https://github.com/CharlGottschalk/thisdamnthing/issues).

## Make your workspace your own

| Feature | What you can do |
| --- | --- |
| **Build your brain** | Keep useful facts and decisions as linked Markdown notes. Choose what to remember through review. |
| **Find answers with sources** | Ask your brain questions and get references to approved knowledge. |
| **Give your agents rules** | Set working preferences and boundaries with a workspace Constitution. |
| **Use ThisDamnThing's UI** | Say “use ui” to answer questions and work through choices in a local browser. |
| **Bring your projects** | Link existing project folders and get oriented without moving their source. |
| **Extend with Stacks** | Add skills, workflows and capabilities when you need them. |

## Install and create a workspace

You need Python 3.11+ and pipx. Install Claude Code or Codex separately if you
want an agent integration.

The commands below describe the planned public installation. PyPI publication
and installation from the public registry are still awaiting release verification.

Ask your agent:

> Install and set up ThisDamnThing via pipx, create a workspace at [my chosen directory],
> and check it.

Replace the bracketed directory with your preferred location. Setup has no
ThisDamnThing skill before installation. Open the created workspace in your agent,
review its workspace and hook trust prompts, and use `/tdt-workspace` in
Claude or `$tdt-workspace` in Codex, or select it from the skill picker.

For terminal setup, run these examples from a parent directory outside your
projects and the ThisDamnThing source checkout. Paths are relative to that directory.

```sh
pipx install thisdamnthing
tdt init "./my workspace"
tdt --workspace "./my workspace" doctor
```

You can also `cd` into your chosen folder and run `tdt init` without a path
to initialize the current directory, then run `tdt doctor`.

Choose a workspace folder outside your existing projects. If pipx asks you to
update PATH, follow its instructions and reopen your shell. ThisDamnThing starts with
zero stacks and detects Claude and Codex on PATH. Add `--agent claude`,
`--agent codex`, `--agent both` or `--agent none` to `init` to choose explicitly.
Existing unrelated files are preserved; conflicting files are refused.

Read the [usage guides](https://usetdt.com/docs), or open the local guides in
your workspace's `docs/` folder.

---

## Developing ThisDamnThing

Working on ThisDamnThing itself? Start with the [developer documentation](https://github.com/CharlGottschalk/thisdamnthing/blob/HEAD/docs/README.md)
for setup, architecture and development practices. Open this source checkout in
your agent and say **“onboard me”** for guided development setup.

[Development setup](https://github.com/CharlGottschalk/thisdamnthing/blob/HEAD/docs/development.md) · [Architecture](https://github.com/CharlGottschalk/thisdamnthing/blob/HEAD/docs/architecture.md) ·
[Making a change](https://github.com/CharlGottschalk/thisdamnthing/blob/HEAD/docs/contributing.md)

Licensed under [Apache-2.0](https://github.com/CharlGottschalk/thisdamnthing/blob/HEAD/LICENSE).

---

> If you find any bugs, it's because I left them there, so I have something to do later.
