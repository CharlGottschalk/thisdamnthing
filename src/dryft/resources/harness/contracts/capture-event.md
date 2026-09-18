# Capture event and summary input v1

`dryft.hosts.normalize_event(host, payload)` maps a host JSON object to a plain
Python dictionary. No transcript is read and no note is created by this adapter.
The Stop handler in dryft.capture requests an active-agent summary and persists
its structured response through dryft.brain.

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

The first Stop writes a requested record under .dryft/state/captures/ and returns
`decision: block` with a reason asking the active agent for a summary. Its next
final response must be exactly a fenced `dryft-capture` JSON envelope with
`request_id` and `summary`. The handler accepts it only for a request from the same
host/session. A response is processed before the stop_hook_active recursion guard;
that guard never schedules another continuation. Replays do not create duplicates.
Malformed responses remain recoverable requests and never trigger repeated loops.
No full payload, message body or transcript is stored as capture state.

Summary fields and limits are in docs/brain.md. The only alternate summary is
`{"skip":true}`. Capture cannot accept approval fields or invoke review. Pending
Markdown, host provenance and explicit review history are separate from approved
canonical notes. PreCompact normalization remains available but is not wired:
there is no portable pre-compaction active-agent continuation contract here.
