# Building UI interactions

UI provides local browser questions and custom pages through `src/thisdamnthing/ui.py`
and packaged assets in `resources/ui/`. Follow the
[UI contract](../src/thisdamnthing/resources/harness/contracts/ui.md) and
[installed usage guide](../src/thisdamnthing/resources/docs/ui.md) for schemas and examples.
No stack is required.

## Run a session

```sh
tdt ui start --no-open
tdt ui present SESSION questions.json
tdt ui wait SESSION --after 0 --timeout 20
tdt ui ack SESSION 1
tdt ui present SESSION follow-up.json
tdt ui close SESSION
```

Replace `SESSION` with the returned session ID and open its private local URL.
Present a page, wait for submitted events, read their answers and acknowledge the
event after handling it. Use the actual event ID and advance the cursor accordingly.
If a wait times out while the round is unanswered, repeat with the same cursor.
A command timeout does not end the interview. Apply this loop to follow-ups too.

A running agent must read events; browser submission cannot wake a stopped host.
After interruption, resume the agent and read retained events before asking the
same questions again. Acknowledgement does not guarantee exactly-once execution
of downstream actions; design those actions to handle replay deliberately.

## Design a page

Standard pages group fields into steps with stable IDs. One explicit submission
returns an answers object plus session, round, event and action metadata. Use
required-field validation and accessible labels. Defaults and unsubmitted drafts
are not answers or authorization.

Description, field help and answer previews support fenced code and inline
backticks. Other Markdown stays literal. Render source with text nodes so HTML-like
input remains visible text. Shared `tdt-code` styling is available to custom pages.

For custom interaction, use inline HTML/JavaScript and the supported `tdt.submit`
or declared `tdt.action` bridge. Provide keyboard input and readable selection
feedback. Stack authors can declare JSON interview templates through the ordinary
manifest; installing a template does not run its code.

## Preserve browser and state boundaries

The standard-library server runs on loopback, on demand, with one process per
session. It uses private session credentials, origin/host checks, bounded payloads,
locks and atomic state writes. Custom content uses iframe and response-level CSP
sandboxing. Keep browser assets local; do not expose arbitrary workspace paths or
add custom server endpoints for a page.

Accepted events retain their original prompts. Session JSON stays separate from
approved brain knowledge. `close` stops the service; `cleanup` deletes retained
session answers. Restart an expired or stopped session with
`tdt ui start --session SESSION --no-open` and open the returned URL. Do not reuse
a stale port or remove state while its owned server is active.

## Verify changes

Inspect a standard grouped page and a custom interaction at desktop and narrow
widths. Check required errors, keyboard focus, draft retention, browser refresh,
explicit submission and follow-up context. Read the persisted event to verify
that false, zero and multiple-choice answers survive intact.

Probe stale rounds, duplicate submission IDs, altered replays, wrong credentials,
cross-session access and oversized input. Check crash/restart, idle expiry,
offline read and cleanup. Use actual browser submissions with each live host when
changing the agent loop; direct HTTP requests alone do not verify that interaction.


## MCP access

Read the installed guide and contract with `tdt_guide_read` using `core/ui` and
`core/contracts/ui`. Both profiles expose these allowlisted documents.

Everyday MCP exposes `tdt_ui_start`, `tdt_ui_present`, `tdt_ui_status`,
`tdt_ui_read`, `tdt_ui_wait`, `tdt_ui_ack`, `tdt_ui_close` and `tdt_ui_cleanup`.
Present accepts the page object directly, using the same core validation as CLI.
Start defaults to no browser launch and returns the private local URL. Status
returns connection/round/cursor metadata without page content or credentials.
Read/wait include complete events and original prompts, defaulting to one event;
use `next_after` while `has_more` is true. Increase `budget_bytes` up to 1 MiB
for large events. Budget refusal never acknowledges events. Waits are bounded to
30 seconds and do not hold the MCP mutation lock. A cancelled MCP call does not
cancel the interview. After uncertain start/present responses inspect retained
state/current round before retrying; present always creates a new round.
Close retains answers; cleanup deletes them and requires explicit user instruction.
These tools do not submit answers on the user's behalf or promote them to knowledge.
