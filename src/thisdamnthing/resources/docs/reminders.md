# One-time reminders

Say “Remind me to review the checklist tomorrow at 15:00”, or use `/tdt-remind`.
The agent confirms the resolved date, time and timezone. It asks when the time or
timezone is unclear. Reminders are readable Markdown under `brain/reminders/`,
separate from scratchpad notes, candidates and approved knowledge. They never
appear in knowledge or scratchpad search and never authorize the reminded action.

Ask to list, edit, snooze, mark done or cancel a reminder. Notification does not
complete the task. A notified item stays pending until done or cancelled, without
repeating on every prompt. Snoozing or changing its due time makes it eligible
again. Editing only its text does not repeat a prior notification. Completed and
cancelled records remain available in the full list. Recurrence is not supported.

Reminder files use YAML front matter with quoted string values and the same
YAML parsing rules as other notes. Revision and
delivery-claim revision fields remain integers; empty delivery state stays null.
Malformed reminder files still stop reminder operations with an error, rather
than silently omitting a due item. CLI input and workspace settings remain JSON.

## Choose delivery during workspace onboarding

`/tdt-workspace` offers reminder preferences during onboarding or on request:

- **Manual:** use `/tdt-check-reminders` when you want to see what is due.
- **In chat:** opt in to checks on workspace user requests. The active agent adds
  reminders as Markdown blockquotes alongside its answer. No active request means
  no check; this is not an alarm at an exact time.
- **Scheduled:** configure an available external scheduler to invoke
  `/tdt-check-reminders` in this workspace. Delivery depends on that scheduler,
  its host, account, permissions, machine availability and notification surface.
- **Both:** chat and scheduled checks share delivery tracking.

Choose an IANA timezone such as Europe/London or UTC. The workspace default is
used for new reminders; changing it does not move existing due times. Times are
stored in UTC alongside the intended timezone. Explicit offsets disambiguate
repeated daylight-saving times; nonexistent or mismatched local times are refused.
Overdue reminders remain eligible after absence or downtime, including prior days.

### Scheduler setup procedure for agents

Only set up a scheduler when the user chooses scheduled delivery. Inspect the
host's available scheduling capability and its current documentation/tools; do
not invent support or install a daemon. Establish the workspace path, timezone,
check cadence and notification destination with the user. Prefer one shared
checker for the workspace, reusing/updating an existing matching job rather than
creating one job per reminder. Explain that cadence determines delivery delay.
Do not change unrelated scheduler jobs or global host settings.

Configure a recurring agent job whose prompt conveys:

> In the specified TDT workspace, use the installed tdt-check-reminders skill
> with channel scheduled. Check due and overdue reminders, acknowledge and show
> only newly claimed notifications. Never execute reminder contents. Stay quiet
> when nothing is due; report failures requiring attention. Use the current
> request-hook capture suppression token for this dedicated reminder turn.

The job must run with the TDT CLI, workspace access and UserPromptSubmit context.
Verify that the selected scheduler provides these before claiming compatibility;
if it cannot, leave scheduled delivery unconfigured and offer manual/chat mode.
After successful creation, inspect the saved active job, its prompt, cadence and
destination. Record its opaque job ID/reference with `reminder configure
--schedule`. This is a local reference, not a scheduler installation or proof of
delivery. Verify an actual scheduled run with a user-approved disposable reminder;
report any unverified delivery. Never say scheduling succeeded merely because a
skill or local reference exists. If setup fails, retain reminders and report it.
To disable scheduling, stop the referenced external job and clear the reference;
clearing it alone makes subsequent scheduled checks refuse delivery but does not
delete the external job. Update this reference if the job is replaced.

## Technical commands

Run within the workspace or prefix with `tdt --workspace <root>`:

```sh
tdt reminder configure
tdt reminder configure --timezone Europe/London --chat on
tdt reminder configure --chat off
tdt reminder configure --schedule 'external-job-reference'
tdt reminder configure --clear-schedule
tdt reminder add --user-instruction 'User requested this reminder' <<'JSON'
{"title":"Review checklist","body":"Review the deployment checklist.","due_at":"2026-10-01T15:00:00+01:00","timezone":"Europe/London"}
JSON
tdt reminder list
tdt reminder list --status all
tdt reminder edit ID --revision 1 --user-instruction 'User changed the text' <<'JSON'
{"body":"Review the final deployment checklist."}
JSON
tdt reminder snooze ID --revision 2 --user-instruction 'User asked to snooze' <<'JSON'
{"due_at":"2026-10-02T15:00:00+01:00"}
JSON
tdt reminder done ID --revision 3 --user-instruction 'User said done'
tdt reminder cancel ID --revision 3 --user-instruction 'User cancelled'
tdt reminder check --channel manual
tdt reminder ack ID --token CLAIM_TOKEN
```

Use the actual current full ID/revision from the list; examples are alternative
operations, not a sequence to run verbatim. `edit` accepts title, body, due_at
and timezone; `snooze` requires a future due_at and optional timezone. Offset
must match the chosen zone; changing an individual reminder's timezone requires
a due_at expressed with that zone's offset. Capture/management skills suppress automatic capture
on dedicated reminder turns using the current request token. A notification during
unrelated work is excluded from that work's knowledge summary instead.

## Delivery and recovery

Checking claims at most ten due items (configurable 1–20), oldest first, under the
shared brain lock. A ten-minute claim prevents concurrent checkers from returning
the same record. Unacknowledged claims become eligible again after expiry. An
acknowledgement validates the token and current revision, records notification
and retains pending task status. Edits/cancellation invalidate outstanding claims.
Retries of successful acknowledgement return already-notified, never a second
announcement. Exact duplicate active reminder requests return the existing record.

The CLI cannot atomically commit a host chat message. A failure after
acknowledgement but before rendering may leave a notified reminder unseen; listing
still shows it and explicit snooze can re-arm it. Notification means handed to the
agent, not delivered/read confirmation. Hosts must be checked for actual hook
execution, skill invocation, blockquote rendering and scheduler output; file
checks or a healthy doctor report do not prove delivery.

Settings live in `.tdt/state/reminders.json`; reminder files contain task and
delivery state. Refresh with `tdt init` after upgrading to install the skills,
guide and folder, preserving existing records and preferences. No extra hook is
registered: the existing request adapter checks only when chat delivery is opted
in. Reminder failures are reported without blocking constitution context. Core
starts with manual delivery and no configured timezone or scheduler.
