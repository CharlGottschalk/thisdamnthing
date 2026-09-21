# ThisDamnThing's UI contract v1

Public core interface for all stacks and agents; no stack manifest extension.
JSON commands use `tdt --workspace PATH ui …` outside the workspace. Errors
exit nonzero. All successful UI command output is one JSON object.

## Page

`present SESSION PAGE.json` accepts UTF-8 JSON, maximum 256 KiB. Required:
`version: 1`, `title` (string ≤160 characters). Optional `description` (≤4000),
`steps` (≤12), `actions` (≤12 unique ID strings), `custom_html` (≤180000).
At least steps or custom_html is required. Unknown properties are rejected.
A step has `title` (≤160) and `fields` (array). Across steps, at most 60 fields,
each with a unique `id` matching `[a-zA-Z0-9_-]{1,64}`, `type` and `label` (≤300).
Optional `help` (≤4000), `required`/`alternative` (booleans), `default`, and finite
numeric `min`, `max`, positive `step`. Types: text, multiline, single, multiple,
boolean, number, scale. Scale requires min/max. Single/multiple require `options`
(1–40 unique nonempty strings ≤200). `alternative: true` permits other strings.
Text answers ≤4000. Choices ≤200, multiple answers ≤41 unique strings. Booleans
are actual JSON booleans; false is a valid required answer. Empty/null/missing
values are accepted only for optional fields. Numeric bounds and step apply to
number/scale answers. Defaults undergo the same validation but are not consent.

The standard shell groups steps, preserves tab-local draft values through back,
review and refresh, and only submits explicitly. Required validation occurs on
submit, returning per-field errors and focusing the first invalid control.
Descriptions, field help and answer previews support triple-backtick fenced
code blocks (optional language label) and single-backtick inline code. Other
Markdown is literal text; HTML is never interpreted. Code preserves indentation
and scrolls horizontally. An unclosed fence displays the remaining text as code.
This is presentation only: stored prompts/answers and validation are unchanged.
Custom HTML replaces the standard form; it may also declare fields for server
validation and pass their values through the bridge. It owns its draft UI.

## Events and actions

`submit` and `cancel` are reserved actions. Additional named actions must be
listed in the page. A named action validates supplied field values; submit also
validates all required values. Cancel must have empty answers and no custom data. One accepted action
ends the round. Present again to start another round; round IDs are generated
by core and never reused. Presenting a round leaves submitted history intact.

Envelope: `version`, `session_id` (32 hex), `round_id` (32 hex), `event_id`
(monotonic integer within that session), `submission_id` (ID string), `action`,
`answers` (field-ID object), `data` (custom JSON or null), `created` (Unix seconds).
Custom data is untrusted opaque JSON bounded by the total 256 KiB request limit.
The browser includes the round ID and a randomly generated submission ID.
Exact retries return the same event; changing the payload under the same
submission ID is rejected. Stale rounds and second answers are rejected.
At most 1000 events, 100 rounds and 8 MiB of stored state per session; start
another session for more. Read/wait also return `prompts`, keyed by round ID,
so every returned event can be matched to its original page, even after updates.

`read SESSION --after N` and `wait SESSION --after N --timeout 20` return events
strictly after N, stored acknowledgement cursor, status and timeout flag. Wait
is bounded to 0–30 seconds; timeout is not consent. While status is waiting and
no events arrive, the active agent repeats bounded waits with the same cursor
instead of ending its turn. Repeat for each follow-up round; stop on cancellation,
finished status, chat fallback or an explicit pause. A host interruption may
require a user chat message to resume; the browser cannot restart a stopped host.
Default cursor is zero for
explicit replay. `ack SESSION N` works for retained offline sessions too and monotonically advances the stored handled
cursor (0 through last event). The caller must choose its read cursor. Re-reading
never implicitly executes an event. Record downstream effects separately;
there is no exactly-once promise for arbitrary agent actions.

## Custom bridge and isolation

Inline `custom_html` can use `tdt.submit(data, answers={})` or
`tdt.action(name, data, answers={})`. Shared CSS variables and system font stacks
are injected before the custom page. HTML/CSS/JS must be self-contained; no file
paths, asset directory serving, uploads or external dependencies. Small data
images are allowed. Use textContent for user text.
For code in custom pages, use `<pre class="tdt-code"><code>…</code></pre>`
and set code text with textContent. Shared code styles are injected with tokens;
custom HTML does not automatically parse Markdown.

Custom pages run in an opaque-origin iframe with only allow-scripts. The custom
HTTP response also enforces CSP sandbox allow-scripts, including when its URL is
opened directly. A separate
unpredictable per-round capability loads that page; it grants no API permission.
Core checks message source, opaque origin, bridge key, current round, action,
size and server-side field validation. The session API credential stays in the
parent tab. Browser storage and parent DOM are inaccessible to custom code.
CSP denies fetch, subframes, forms and external scripts/styles/images. The
sandbox denies popups, downloads and top-level navigation. The parent shell's
frame-src policy restricts frame navigation to the same loopback origin. Ordinary link clicks
are suppressed. Do not treat a browser sandbox as protection against a user
explicitly copying answers into hostile custom code; custom code sees its own
interaction data. Core never interprets custom text as shell/Python commands.

## Lifetime and recovery

`start [--no-open] [--idle 1800]` creates a session and returns actual loopback
URL and session ID only after authenticated readiness. Browser launch failure
still leaves the usable link. `start --session ID` resumes retained active state,
choosing a fresh available port after process failure or expiry. It cannot
reopen a finished/cancelled interview. `status SESSION` reports connection and
logical status; read/wait work even while disconnected. Session statuses are
waiting, received, cancelled and finished. Validation errors leave waiting
intact; disconnection is a separate connection state, never a response.

Each session has a private directory under `.tdt/state/ui/`, a JSON state file
(atomically replaced) and a process-held advisory lock. One process serves one
session. Close uses the authenticated endpoint, never a stored PID or kill of
an unknown process. Idle expiry is 30–3600 seconds (default 30 minutes), measured
since startup or last successful mutation. Browser polling does not extend it.
Closing a tab is not cancel. `close SESSION` stops the owned server; `cleanup
SESSION` refuses a running server, symlinks and unexpected files, then deletes
only that session. Files persist until explicit cleanup, including after expiry
and crashes. UI does not write to the brain. An independently configured host
capture hook may summarize the conversation into pending candidates; ordinary
explicit review is still required for promotion. Reads may contain private
answers; do not log them unnecessarily. No defence against another local process
already authorized to read these files, or a compromised browser extension.

Server binds 127.0.0.1 only, validates exact Host and any supplied Origin, requires
an unpredictable bearer credential for every API request, and denies cross-site
browser requests. Static serving is a fixed asset allowlist. No workspace files
are served. No CORS. The URL fragment is never sent in HTTP requests; the parent
keeps its credential in tab-local session storage for refresh recovery. No
third-party font requests; Geist/Geist Mono use installed fonts or system fallbacks.
