# Knowledge capture and review

ThisDamnThing turns useful facts, decisions and open questions from your conversations into
proposals for your brain. You decide which proposals become approved knowledge.
Use `/tdt-review-brain` to review them and `/tdt-search` to find what you know.

## Capture useful knowledge

With trusted capture hooks enabled, ThisDamnThing asks your active agent for a concise
summary after a turn. This adds a visible continuation using your host subscription.
The summary stays pending until reviewed. Full transcripts remain with the host,
and a turn with nothing useful to retain can be skipped. Capture runs after
supported turns; no pre-compaction capture hook is installed.

## Review proposals

Use `/tdt-review-brain` in Claude or `$tdt-review-brain` (or `/skills`) in Codex.
Show proposals first; only the user's explicit decision permits approval or
rejection. Edits remain pending until the edited proposal is approved.

For technical users, `tdt brain candidates` shows pending proposals and their
exact review hashes. Direct review example (replace all placeholders with values
from the proposal):

```sh
tdt brain review ID --decision approve --expected-sha256 HASH --user-instruction 'User approved the displayed proposal'
```

The CLI records the supplied instruction; it cannot authenticate a human or stop
an agent with filesystem access from recording an incorrect decision. Hooks never
invoke review. Review flags are mandatory, and a stale proposal hash refuses
the operation.

## Search and follow sources

Ask `/tdt-search` your question. It searches approved knowledge, follows bounded
links and answers with references, explaining missing or conflicting evidence.
In Codex, use `$tdt-search` or the skill picker. See [projects](projects.md)
for project onboarding.

### Technical search and note format

Notes use JSON front matter between `---` delimiters, followed by Markdown.
Metadata includes format_version, stable id, title, kind, created/updated UTC
timestamps, status, sources, host/session/turn provenance, optional project id,
links and review history. Links are brain-relative without `.md`, e.g.
`[[projects/example]]`. IDs and canonical `knowledge/<id>` paths never change.
Approval always creates a separate canonical note; it never overwrites an
existing fact or silently resolves conflicting evidence. Rejected candidates
remain for audit. `tdt brain search QUERY` searches approved canonical notes
and project registration notes, plus bounded outgoing approved links.
Use `--limit 10 --depth 1` (limit 1–50, depth 0–3). Literal case-insensitive
matching seeds retrieval; direct matches precede linked notes and cycles are
deduplicated. Pending/rejected notes never become link targets. Brain scans are
limited to 2000 entries and each note to 32 KiB. Missing links are ignored;
malformed notes or unsafe symlinks produce an error.

If `tdt-search` is missing after an upgrade, ask your agent to refresh the
workspace (terminal: `tdt init <workspace>`) and
start a fresh host session. Refresh migrates unchanged owned skill files and
refuses edited files or conflicting target directories without overwriting them.

## Recover an incomplete capture

Ask your agent to inspect incomplete capture requests and recover only what the
available conversation supports. There is no dedicated capture-recovery skill.
Use `/tdt-review-brain` once a recovered proposal is ready for review.

### Technical recovery details

Capture JSON (maximum 16 KiB input; 3000-character prose body):

```json
{"title":"Decision title","kind":"decision","body":"Concise supported decision and uncertainty.","sources":["User message: decision stated in this turn"],"links":["index"],"project":null}
```

Kinds: fact, decision, question, inference. Omit unsupported assertions and label
inference explicitly. Use references, not copied transcripts or tool output.
Never include secrets. Common credential patterns and code dumps are refused;
this filter cannot detect every secret or verify factual claims. Active-agent
judgment and user review are essential. Use `{"skip":true}` for nothing durable.

`tdt brain requests` lists incomplete capture requests. If the summary is malformed,
validation fails, or the host is interrupted, the request remains. Retry
`tdt brain capture ID` with a safe summary on stdin while the relevant context
is still available, or submit `{"skip":true}` if it cannot be recovered. Do not
invent lost facts. Replaying a Stop event does not repeatedly interrupt the host.
Only one continuation is requested; `stop_hook_active` prevents recursion.

Capture identities combine host, session and host turn id; when Claude supplies
no turn id, the last assistant message hash is the boundary. Identical final
answers in one such session coalesce. No message body is stored in capture state;
transcript paths are references only and transcripts remain with the host.
Writes use a workspace advisory lock and atomic replacement. A busy operation
fails with a retry message. Interrupted candidate/approval writes can be retried
with the same request/proposal; existing canonical content is preserved. These
protections coordinate TDT processes, not arbitrary concurrent file editors.

## Optional offline search stacks

Literal search remains the default with no extra dependencies. Use
`/tdt-install-stack` to inspect and install a compatible local
`tdt-search-sqlite` or `tdt-search-semantic` bundle. Both work independently
and require approval of their exact executable digest.

Then use `/tdt-search`, naming the installed provider you want. Ask it to build
or rebuild that provider's index when needed; installation does not select or
index it automatically.

Terminal alternatives:

```sh
tdt brain providers
tdt brain index --provider tdt-search-sqlite
tdt brain index --provider tdt-search-semantic --rebuild
tdt brain search "How do we reduce release risk?" --provider tdt-search-semantic
tdt brain search "release risk" --provider tdt-search-sqlite --provider tdt-search-semantic
```

Index after edits; queries never index automatically. Edits/deletions and changed
approval/project eligibility filter stale results immediately. Core returns current
Markdown evidence, never cached excerpts. Provider failure is explicit; omit
`--provider` to use literal search. Updates invalidate disposable indexes; rebuild
afterwards. Removal deletes unchanged owned indexes and preserves brain notes.
Use a provider compatible with your platform and Python version. Read its installed
guides for requirements, offline behavior and licenses before installing.
Semantic similarity may miss evidence or return irrelevant material. Inspect the
notes, cite sources, and describe absent/conflicting evidence rather than treating
rank as confidence. Local trusted provider processes retain normal OS access.
