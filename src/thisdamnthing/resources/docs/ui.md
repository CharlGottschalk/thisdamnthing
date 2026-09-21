# Use UI

Say “use ui” to request a local browser interview, or use `/tdt-ui`. You can
answer in chat/TUI instead. No stack or additional model subscription is needed.
The active agent must wait/read responses; a browser cannot wake a stopped agent.
In Codex, use `$tdt-ui` or the skill picker. Describe the interview you want;
the skill prepares the page, reads your answers and handles follow-up questions.
Ask it to resume an interrupted interview, close a session or clean up retained
responses when you no longer need them.

## Technical reference: session commands and page examples

The skill uses the commands below. You only need these details when operating
UI directly or authoring a custom page.

```sh
tdt ui start --no-open
tdt ui present SESSION business.json
tdt ui wait SESSION --after 0 --timeout 20
tdt ui ack SESSION 1
tdt ui present SESSION follow-up.json
tdt ui close SESSION
tdt ui cleanup SESSION
```

Use the real session ID returned by start and open its URL. Keep the URL private.
The wait command above is one iteration: while the interview is waiting and no
events arrive, the agent repeats it with the same cursor. A 20-second timeout
ends that command, not the interview or the agent turn. This applies after every
follow-up page too. The agent should keep waiting until submission, cancellation,
chat fallback or an explicit pause, with occasional progress updates. Finished
or cancelled status ends the loop. Host interruption or execution limits can
still stop the agent; in that case send a chat message to resume and read the
retained response. Browser submission alone does not restart a stopped host.
Read the full public contract at `.tdt/contracts/ui.md`. Resume after a crash
with `tdt ui start --session SESSION --no-open` and open the new URL. Read
retained answers with `tdt ui read SESSION --after 0`. A stopped or expired
server does not remove answers. Cleanup deletes that session's retained answers;
close only stops the service. Choose a shorter `--idle` when appropriate.

## Business plan, with zero stacks

Save this as `business.json`, present it, and use the submitted audience and goal
to ask about the first offer and price or write the first business-plan paragraph.

```json
{"version":1,"title":"Shape your business","description":"Start with the people you want to help.","steps":[{"title":"People and purpose","fields":[{"id":"audience","type":"text","label":"Who will you help?","required":true},{"id":"goal","type":"multiline","label":"What problem will you solve?","required":true},{"id":"stage","type":"single","label":"Where are you today?","options":["An idea","First customers","Growing"],"alternative":true}]}]}
```

## Multiple questions, one answer payload

A page can contain many fields across grouped steps. Review displays all answers;
one explicit submit returns them together as `event.answers`, keyed by stable
field IDs. For the business page above, the answers portion could be:

```json
{"audience":"Neighbourhood bakeries","goal":"Reduce unsold bread","stage":"An idea"}
```

The event also includes session, round, event and submission IDs, the action,
creation time, and optional custom data. The agent should use the answers together
to advance the work. Read/wait includes the original page under `prompts` so
follow-ups do not lose the meaning of an earlier answer.

## Showing code and Markdown

In standard page `description`, field `help`, and answer previews, wrap code or
literal Markdown in triple-backtick fences, with an optional language such as
`python`, `json` or `markdown`. UI shows an inset monospace block, preserves
indentation and allows horizontal scrolling. Use single backticks for inline
code. Other Markdown stays literal; text is never interpreted as HTML.

For example, a JSON description can be:

```json
"description": "Review this command:\n\n```sh\ntdt doctor\n```"
```

Custom pages use `<pre class="tdt-code"><code></code></pre>` and set the code
element's `textContent` to the source. The shared styles are available inside
the sandbox too. Do not inject user text through `innerHTML`.

## Custom interaction

A stack can list a JSON template containing custom_html in its ordinary
`templates` array; it needs no hooks or manifest changes. This two-dimensional
priority pad submits structured custom data, then the agent can interpret the
selected urgency/impact and ask a follow-up.

```json
{"version": 1, "title": "Choose a priority", "custom_html": "<main><h2>Where does this idea sit?</h2><p>Click the pad, or focus it and use arrow keys. Left/right changes urgency; up/down changes impact.</p><button id='pad' style='width:100%;height:180px;background:var(--inset)' aria-label='Priority pad'>Select priority</button><p id='selection' role='status'>No selection</p><button id='send' disabled>Submit priority</button></main><script>const pad=document.getElementById('pad'),out=document.getElementById('selection'),send=document.getElementById('send');let point;function show(){out.textContent=JSON.stringify(point);send.disabled=false}pad.onclick=e=>{if(e.detail===0){point=point||{urgency:50,impact:50}}else{const r=pad.getBoundingClientRect();point={urgency:Math.round(100*(e.clientX-r.left)/r.width),impact:Math.round(100*(1-(e.clientY-r.top)/r.height))}}show()};pad.onkeydown=e=>{if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();point=point||{urgency:50,impact:50};const k=e.key==='ArrowLeft'||e.key==='ArrowRight'?'urgency':'impact';point[k]=Math.max(0,Math.min(100,point[k]+(['ArrowRight','ArrowUp'].includes(e.key)?5:-5)));show()};send.onclick=()=>tdt.submit(point);</script>"}
```

The pad supports keyboard selection and exposes its selected values as status
text. Supply comparable keyboard alternatives for your own custom interactions.
Custom code is optional executable content: keep it small and inspect it first.
Installing a stack never starts its interview or executes its custom templates.

When switching to chat, your agent retains submitted answers. Unsubmitted edits
remain only in the browser tab. Submit those explicitly if you want to carry them
over; showing a default or changing a control does not authorize an action.
Responses are local interview state, not approved brain knowledge. Avoid entering
secrets. After completion, close the session and clean up when no longer needed.
