# Capture event and summary input v1

`tdt.hosts.normalize_event(host, payload)` maps a host JSON object to a plain
Python dictionary. No transcript is read and no note is created by this adapter.
The Stop handler in tdt.capture requests an active-agent summary and persists
its structured response through tdt.brain.

Fields: `format_version` (integer 1), `host` (claude or codex), `event` (session_start,
turn_complete or pre_compact), `session_id` (nonempty string), `cwd` (absolute path
string), `transcript_path` (absolute path string or null), `turn_id` (nonempty string
or null), `source` (string or null), `stop_hook_active` (boolean, default false).
Host events map SessionStart, Stop and PreCompact respectively. Unknown fields
are ignored; malformed known fields and unsupported events are rejected.
A Stop with stop_hook_active=true must not initiate recursive capture.

Transcript paths are untrusted source references, not permission to read files.
Future transcript readers must be host-specific and bound their reads. No raw
payload, full assistant message, transcript content or secrets are persisted here.
An event is not a summary. Stop additionally requires last_assistant_message
(nonempty string, bounded by the 256 KiB hook envelope). This text is hashed for
Claude boundary identity when no turn id exists, never copied into state. Request
ids hash host, session and turn id (or final-message hash). Exact repeated final
messages without turn ids coalesce within a session.

The first Stop writes a requested record under .tdt/state/captures/ and returns
`decision: block` with a reason asking the active agent for a summary. Its next
action prefers `tdt_capture_submit` on the MCP server bound to this workspace,
using the exact hook request ID and a summary/skip payload. If unavailable, submit
summary JSON on stdin to `tdt --workspace <root> brain capture <request-id>`.
Both transports validate and persist through the same core before success.
After an uncertain MCP response, read `tdt_capture_request_read` or
`tdt --workspace <root> brain request <request-id>` first. A captured/skipped
status is final; only requested permits one identical CLI retry, including partial
candidate recovery. Failed status reads leave recovery for later. Permission and
validation refusals never authorize a transport bypass. The final response
preserves the substantive answer and adds at most one capture confirmation,
only for a captured candidate; skipped turns add none. Never render capture
instructions or JSON as the answer. Tool/debug activity remains host-controlled.
Legacy fenced `tdt-capture` envelopes with `request_id` and `summary` remain
accepted only for a request from the same host/session. Legacy responses are
processed before the stop_hook_active recursion guard; that guard never schedules
another continuation. Replays do not create duplicates. Failed submissions remain
recoverable requests and never trigger repeated loops.
No full payload, message body or transcript is stored as capture state.

Summary fields and limits are in docs/brain.md. The only alternate summary is
`{"skip":true}`. Capture cannot accept approval fields or invoke review. Pending
Markdown, host provenance and explicit review history are separate from approved
canonical notes. PreCompact normalization remains available but is not wired:
there is no portable pre-compaction active-agent continuation contract here.

UserPromptSubmit issues a fresh opaque review-turn token in additional context.
The hook prefers `tdt_capture_suppress` on the workspace-bound MCP server;
`tdt brain review-turn <token>` remains the CLI fallback. Repeating the same token
after an uncertain response is safe, but stale-token and permission refusals must
not be bypassed. The review skill suppresses every review turn,
including follow-up decisions and empty listings. Direct capture and scratchpad
saving skills use the same command to avoid duplicate automatic proposals. State under
`.tdt/state/capture-turns/` is isolated by host and session and stores only the
current token, optional turn ID and suppression flag. Stale tokens are refused.
A suppressed Stop returns without requesting a summary, accepting a legacy
capture envelope, or notifying turn-complete stack hooks. Suppression persists
through repeated Stops and resets on the next user prompt; unrelated sessions
remain unaffected. No prompt matching or transcript parsing is used.

When the user prohibits saving brain notes or capturing knowledge for the work,
the active agent uses the same current token to suppress automatic capture.
If a Stop continuation is still requested, its instructions require submitting
`{"skip":true}` instead of a candidate. This records only skipped request state,
not brain content. Recognizing the user's restriction relies on active-agent
adherence; the hook does not interpret or retain the user's prompt.

Dedicated reminder creation, management and manual/scheduled checking turns also
use the current suppression token. An opted-in request hook may ask the agent to
check due reminders alongside unrelated work; that does not suppress the whole
turn. The capture continuation explicitly excludes reminder records, operations
and notifications from summaries while retaining unrelated durable knowledge.
This exclusion relies on active-agent adherence, like other summary boundaries.
