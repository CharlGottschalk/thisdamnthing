# Enabling and disabling agent integrations

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

Use `src/thisdamnthing/agents.py` and `bootstrap.py` for workspace host selection and
registration. Agent detection checks executable availability; it does not verify
account access, hook trust or runtime discovery.

## Select hosts

```sh
tdt init ../workspace --agent none
tdt --workspace ../workspace agent enable claude
tdt --workspace ../workspace agent enable codex
tdt --workspace ../workspace agent disable claude
```

Initial setup detects `claude` and `codex` on PATH unless `--agent` selects
`claude`, `codex`, `both` or `none`. The workspace saves `enabled_agents` in its
configuration. Subsequent initialization refreshes that saved set; an explicit
selection adds integrations. Use `agent disable` to remove one.

Desktop-only hosts or executables outside PATH need explicit selection. Core
works without enabled hosts.

## Maintain ownership across features

Enabling a host adds bridges for core, stack and approved user skills, owned
instruction blocks and hook registrations. Canonical skills stay in `.tdt/`.
Record each new bridge with its original owner so stack removal and skill updates
can manage it later.

Disabling removes only recorded integration assets for the selected host. Preserve
canonical skills, brain notes, the other host and unrelated configuration. Refuse
edited owned files and name collisions rather than overwriting them. Existing
sessions can retain loaded skills; use a fresh session to verify removal.

For workspaces without saved selection, infer integrations from recorded adapter,
instruction and bridge ownership. Directory presence alone is insufficient.

## Use the shared transaction

Existing-workspace refresh and enablement coordinate configuration, owner records,
settings and core resources through the stack transaction journal. Recover an
interrupted operation before retrying:

```sh
tdt --workspace ../workspace stack recover
```

User-skill saves have a separate journal and `tdt skill recover` command. Each
operation refuses the other's pending transaction. Enabling a host can change the
ownership snapshot of a pending skill update; re-propose it against current state
before seeking approval.

An interrupted initial creation without a valid configuration needs inspection
of partial files before retrying. Do not treat that case as an ordinary refresh.

## Check changes manually

Exercise fresh setup with no hosts, each host and both. Check saved selection after
PATH changes, repeated enablement, disable/re-enable and refresh while disabled.
Include stack and user skills so ownership is checked beyond core resources.

Snapshot unrelated settings, instructions and brain files before mutation. Confirm
preservation on success and byte-identical refusal for edited bridges or occupied
names. Exercise interruption and recovery in a disposable workspace. Finally,
check fresh-session discovery and invocation on each affected host.
