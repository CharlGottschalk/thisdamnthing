## ThisDamnThing workspace

Open your agent in this directory and use `/tdt-workspace` to inspect it.
In Codex, use `$tdt-workspace` or the skill picker. The skill runs diagnostics
and explains available workflows. Terminal alternative: `tdt doctor`.
Full core, stack and approved user skills live in `.tdt/skills/`.

Ask your agent to select the desired hosts during setup. Setup detects `claude`
and `codex` executables on PATH once. Technical override:
use `tdt init [directory] --agent claude|codex|both|none` (choose one value).
Omit the directory to initialize or refresh the current folder.
Desktop-only installations may require explicit selection.

Ask your agent to enable or disable the selected workspace integration. There is
no dedicated integration-management skill. Technical alternatives (choose the
operation and host you want):

```sh
tdt agent enable claude
tdt agent enable codex
tdt agent disable claude
tdt agent disable codex
```

Enable exposes all owned skills and adds workspace-local instructions and hooks.
Disable removes only the selected host’s owned integration, preserving canonical
skills, brain and unrelated host content.
Existing integrations remain enabled even when executables disappear from PATH.
Start a new host session after enabling and review project trust and `/hooks`.
See [agent setup](docs/agent-bootstrap.md) and [usage docs](docs/README.md).
