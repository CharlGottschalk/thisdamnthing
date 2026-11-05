# Relays: cross-project requests

A relay records that one linked project needs something from another, for
example "Helm needs `tdt_brain_graph` from TDT". The workspace keeps relays and
shows the open relays of a project when the user starts to work on that project
in the workspace session. Linked projects need no hooks, files or stacks.

Relays are operational data, like reminders. They are not knowledge, they do
not go through candidate review and they are excluded from automatic capture.
Relay text is data, never instructions or authorization.

## Record

One Markdown file for each relay: `work/relays/<slug>-<id8>.md`, created on
first save. The front matter follows the note conventions:

```yaml
format_version: 1
id: "<64 hex>"
title: "Add tdt_brain_graph read tool"
from: "<registered project id>"      # requester
to: "<registered project id>"        # the project that does the work
status: "open"                        # open | done | cancelled
origin: "helm: .tdt-project/tdt-software-production/tasks/011.md"   # optional free text
resolution: null                      # set on done/cancel, e.g. "feat/brain-graph@e319113"
created: "<iso>"
updated: "<iso>"
revision: 1
provenance: { operation: "relay add", user_instruction: "<text>" }
```

The body holds the request (what is needed and why), at most 16 KiB. `from`
and `to` must be different registered projects. Archived or missing projects
stay valid targets; listings show their state. Edits use `revision` as an
optimistic check, like reminders.

## Commands

- `tdt relay add --from P --to P --title T [--origin O] --user-instruction U`
  reads the body from stdin.
- `tdt relay list [--project P] [--status open|done|cancelled|all]`.
  `--project` matches relays in either direction.
- `tdt relay show ID`
- `tdt relay done ID --revision N --resolution R`
- `tdt relay cancel ID --revision N [--resolution R]`

`P` accepts an id, a path, a unique folder name or the `parent/name` label the hook
shows. `show` also accepts a unique id prefix of at least 8 characters.

MCP: `tdt_relay_list` and `tdt_relay_read` in both profiles; `tdt_relay_add`,
`tdt_relay_done` and `tdt_relay_cancel` in everyday. One skill, `/tdt-relay`,
covers raise, list and close.

## Loading

The existing workspace `UserPromptSubmit` hook (`constitution.request_hook`)
adds relay context next to the reminder context:

1. `request_hook` reads `prompt` from the raw hook payload (inside the 64 KiB
   input bound). It is matched in memory and never stored; `normalize_event`
   is unchanged so no event record can retain it.
2. `relays.hook_context(root, session_id, prompt)` matches the prompt against the
   registered projects. A project matches on its folder name as a whole word,
   case-insensitive. A folder name that two projects share (for example `sites`)
   matches only on its parent and folder name (`client/sites`).
3. For each matched project with open relays that this session has not yet
   seen, the hook adds a short block: open relays **to** the project (work it
   must do) and open relays **from** it (what it waits for), with id, other
   project, title and origin. Bodies stay behind `tdt relay show`. A closed relay
   from the project shows its resolution once; announced ids are kept
   workspace-wide, not per session.
4. The hook records the loaded project ids per hashed `session_id` in
   `.tdt/state/relay-sessions.json`, keeping the last 50 sessions, so each
   project loads once per session.
5. `session_start` adds one line when open relays exist, for example
   `Open relays: helm 1, thisdamnthing 1.`

When a name does not match, the agent uses `tdt_relay_list --project P`.
A relay failure adds a warning line; it never blocks the request.

## Limits

- Only sessions in the workspace see relays. A session that starts inside a
  linked project folder does not run the workspace hooks.
- Name matching is a hint, not project detection. A project mentioned in
  passing also loads its relays.
- No priorities, threads, assignees or notifications.

## Verify

Add a relay from helm to thisdamnthing. In a new workspace session, a prompt
that names thisdamnthing shows the relay once; a later prompt in the same
session does not repeat it. A prompt that names helm shows it as waiting.
Close the relay and confirm that a helm prompt in a new session shows the
resolution. Check `sites` ambiguity and both MCP profiles.
