# Implementing host adapters

Host-specific behavior belongs in `src/thisdamnthing/hosts.py` and the packaged adapter
resources. Core modules operate on normalized inputs so Claude Code and Codex
share capture, policy and stack behavior.

## Keep canonical instructions in one place

Full skills live in the installed `.tdt/skills/` directory. Enabled hosts receive
thin discovery bridges in `.claude/skills/` or `.agents/skills/`, plus owned root
instruction blocks. Skill names and directories use `tdt-*`; stack IDs and repository folders use lowercase hyphen-separated names.

Generate only the selected host's resources. Preserve unrelated settings and
record bridge ownership with the skill's original owner. Use the shared
[enablement path](agent-enablement.md) when changing registrations.

Hook commands include the installing interpreter and script path. Quote paths
for the supported shell, including spaces. Reinitializing a relocated workspace
refreshes owned commands; the host may require review of changed definitions.

## Normalize events at the boundary

Validate the host envelope and canonical session working directory before calling
shared code. Exclude outside sessions and nested independent workspaces. Keep
host transcript formats in the host/history adapters, with bounded reads and
explicit handling of unsupported input.

| Event | ThisDamnThing behavior |
| --- | --- |
| SessionStart | Supplies workspace context and current policy. |
| UserPromptSubmit | Reads current workspace policy for the request. |
| Stop | Requests or accepts a concise capture summary and dispatches applicable stack notifications. |

Keep response JSON valid for the selected host. Route diagnostics so they cannot
corrupt protocol output. Hook trust and execution remain host responsibilities;
ThisDamnThing must not change permission settings to make a hook run.

## Preserve the capture handshake

A Stop hook records a capture request and asks the active agent to continue with
a fenced `tdt-capture` JSON summary. The next Stop validates that response and
persists pending knowledge through the shared capture code. The summary is visible
in the conversation. This path uses the active agent; Python does not call a model
or read transcripts to produce the summary.

Keep request identity, replay deduplication and incomplete-request recovery intact.
Only user review can promote a candidate to approved knowledge. Follow the
[capture contract](../src/thisdamnthing/resources/harness/contracts/capture-event.md)
for payload fields and refusal behavior. No pre-compaction capture hook is installed.

## Verify an adapter change

Start with harmless direct payloads for each host: valid in-workspace events,
outside paths, malformed input, repeated capture and interrupted requests. Inspect
both the emitted protocol and the resulting files.

Then initialize a disposable workspace and start a fresh session in each host.
Check discovery, actual skill invocation and actual hook delivery separately.
Reading a bridge manually does not establish native discovery; directly running
a wrapper does not establish host execution. Exercise resume or compaction only
when the host exposes those events, and report unsupported surfaces explicitly.

For policy loading and fallback behavior, see
[workspace constitution](workspace-constitution.md).
