# Building DUI interactions

DUI provides local browser questions and custom pages through `src/dryft/ui.py`
and packaged assets in `resources/ui/`. Follow the
[DUI contract](../src/dryft/resources/harness/contracts/ui.md) and
[installed usage guide](../src/dryft/resources/docs/ui.md) for schemas and examples.
No stack is required.

## Run a session

```sh
dryft ui start --no-open
dryft ui present SESSION questions.json
dryft ui wait SESSION --after 0 --timeout 20
dryft ui ack SESSION 1
dryft ui present SESSION follow-up.json
dryft ui close SESSION
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
input remains visible text. Shared `dui-code` styling is available to custom pages.

For custom interaction, use inline HTML/JavaScript and the supported `dui.submit`
or declared `dui.action` bridge. Provide keyboard input and readable selection
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
`dryft ui start --session SESSION --no-open` and open the returned URL. Do not reuse
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
