# Save and reuse workflows

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Dryft can offer to save a reusable workflow during ordinary work. One clearly
reusable request is enough for a live offer; the original work continues whether
you accept or decline. The proposal names the skill and describes its future
behavior. Existing skills and remembered declines are checked first. Stack-builder
remains the separate workflow for authoring distributable stacks.

Use `/dryft-find-skills` with “Save this workflow as a skill I can use again,”
or ask your agent directly. The skill also handles approved live workflow
suggestions; a history scan is not needed for a live suggestion. Review the
proposed steps before approving them, then invoke the saved skill in a fresh
session. In Codex, use `$dryft-find-skills` or the skill picker.

For example, unread-email triage takes a mailbox/filter, time range, summary format
and priority criteria. A proposed output could include subject, short summary,
priority, evidence and uncertainty. Urgency inferred from wording must be labelled;
sender role, explicit deadlines and user criteria supply evidence. Use the user's
available authorized Gmail connector. Missing access is a prerequisite to explain,
not permission to install/connect one. Saving or running a summarization workflow
does not authorize sending, deleting, archiving or marking messages read.

## Find workflows in previous sessions

Ask `/dryft-find-skills 5` to look for repeated workflows in up to five completed
sessions of this workspace. Your agent needs access to their histories and reliable
completion information. If it cannot obtain those, it should explain the gap
instead of claiming a complete scan. Review any suggested skills before saving.

## Technical reference: propose, review and update a skill

`/dryft-find-skills` handles the following commands for live suggestions and
history-based proposals. Technical users can use the same commands directly.

Agents use this same path for live suggestions and discovered candidates. Run
`dryft skill list` first: it includes core, stack, unmanaged and user skills in all
three local skill directories, plus retained pending/approved/declined proposals.
Read relevant overlaps before offering a new name. A matching non-user skill can
be invoked; suggest an update through its owning core/stack workflow rather than
claiming ownership. Do not rename a declined workflow to offer it again.

Submit a generalized proposal with `dryft skill propose` (JSON on stdin, at most
16 KiB). Use these fields:

```json
{
  "name": "dryft-unread-triage",
  "description": "Summarize unread email and estimate priority using explicit criteria when asked to triage a mailbox.",
  "instructions": "Ask for the mailbox/filter, time range and priority criteria if missing. Use only an available authorized email reader. Read without changing read status. Output a table of subject, summary, priority, evidence and uncertainty. Infer urgency only with a label; use explicit deadlines and user criteria as evidence. Never send, delete, archive or mark read without separate authorization. If read-only access is unavailable, explain the missing prerequisite and stop.",
  "sources": ["claude:session-id:turn-id"]
}
```

Instructions should cover reusable steps, variable inputs, output expectations,
tool prerequisites and relevant limits. Omit private content, credentials, raw
transcripts and incidental values. Descriptions are at most 1024 characters,
instructions 10000; up to 40 source references of 160 characters each. Live
suggestions may use an empty source list. Do not store raw approval messages;
use a short user-message reference for the decision.

Show the exact proposal and returned content ID. After actual user approval:

```text
dryft skill review <id> --decision approve --user-instruction <user-message-reference>
dryft skill review <id1> <id2> --decision approve --user-instruction <user-message-reference>
dryft skill review <id> --decision decline --user-instruction <user-message-reference>
```

Select 1–20 distinct IDs, one version per name, per review. Batch preflight refuses
all writes if any selected skill conflicts. Refine by submitting a changed proposal
and displaying it for approval. Repeated identical submissions retain pending/declined decisions. An approved
version that is still installed remains approved. If a different version is now
installed, resubmitting the earlier behavior reopens it as pending against current
ownership; show it for fresh approval before restoring it. Directly approving the
old ID without resubmitting is refused. Do not repeatedly offer unchanged declines. If the user explicitly revisits
a declined proposal, their new approval can select the same ID; do not solicit
that reversal automatically. Approval is a
conversation responsibility: the CLI records the supplied decision reference; it
cannot independently authenticate user intent. Never fabricate it.

Approved files live at `.dryft/skills/<name>/SKILL.md`, where the full name
begins with `dryft-`. Names have at most 64
lowercase ASCII letters/digits/hyphens, no edge or consecutive hyphens, and must
match the directory. The writer emits valid quoted YAML frontmatter following the
[Agent Skills specification](https://agentskills.io/specification). Thin bridges
are registered at `.claude/skills/<name>/SKILL.md` and
`.agents/skills/<name>/SKILL.md` in this workspace only, for enabled hosts. No global or external project registrations are created.

Ownership and up to 100 bounded proposals/decisions live separately in
`.dryft/state/user-skills.json`. Identical behavior has the same ID even when source
references change. At the limit the command refuses new proposals; consciously
archive decided entries before pruning them, since deleting declines loses that
memory. Semantic duplicate detection belongs to the active agent. Creation checks
the selected skill directories and enabled Claude command collisions. Updates to an owned skill use a new
proposal and refuse edits/missing files or changed ownership since proposal. Preserve
and reconcile edited files explicitly before retrying; do not delete edits to force
an update. Core re-bootstrap and stack removal do not own these skills.

If interrupted, run `dryft skill recover`. It rolls back only files still matching
the journal's before/after content, leaving proposals reviewable; conflicts require
manual inspection with edits preserved. Then review the same approved proposal
again using the existing user authorization. Do not manually expose partial bridges.

Claude uses `/dryft-find-skills 5` and `/dryft-unread-triage`. Codex uses
`$dryft-find-skills 5` and `$dryft-unread-triage` (slash selection depends on its UI).
Restart/start a new session in the owning workspace if a new skill is not listed;
review workspace trust and bootstrap first. Saving a skill does not execute it.

### Provide history to the CLI

N means the most recent completed previous sessions of this workspace, not turns,
brain notes, or linked-project histories. Supported maximum: 20. History readers
support Claude Code conversation JSONL (`sessionId`, `cwd`, `uuid`, `message`) and
Codex rollout JSONL (`session_meta`, `response_item` messages). They do not query a
global history database, assume a fixed home directory, or parse brain summaries.
Host interfaces vary: the active agent must resolve accessible transcript paths
and a completion inventory through its available host session listing/export or
explicitly identified host files. Do not enumerate unrelated histories looking for
a match. If this capability is unavailable, say so and inspect zero sessions.

Pass the known active session ID and a bounded inventory to:

```text
dryft skill history 5 --host claude --active-session <actual-id>
dryft skill history 5 --host codex --active-session <actual-id>
```

JSON stdin (same 16 KiB command limit). Replace every placeholder, including
`HOST_COMPLETION_TIMESTAMP` with the actual ISO 8601 completion timestamp supplied
by the host. `HOST_TRANSCRIPT_PATH` must be its actual canonical absolute path;
for an explicitly supplied export such as `./history/session.jsonl`, resolve that
relative path from the current working directory before building the inventory.
The reader requires absolute paths to avoid ambiguity across host processes:

```json
{
  "sessions": [
    {"id": "previous-session-id", "path": "HOST_TRANSCRIPT_PATH", "completed_at": "HOST_COMPLETION_TIMESTAMP", "completion_evidence": "host session listing identifies this session as ended"}
  ],
  "limitations": ["Only the active host's accessible session inventory is available"]
}
```

The caller must establish session completion and inventory recency from actual
host evidence. Neither file modification time, a Stop hook, nor a completed turn
proves the session ended. If only a subset can be located, disclose that the most
recent N cannot be established; the output is a partial scan of located sessions.
An unavailable provider may be represented with an empty session list and a reason.
Do not invent completion dates or use the example IDs as real evidence.

At most 100 inventory entries are accepted. Entries are sorted by completed time;
active and duplicate IDs are removed before selecting N. Missing selected histories
are reported without silently replacing them with older sessions. Every selected
transcript must identify the requested session and exact canonical workspace cwd.
Subdirectories/linked projects and unknown metadata are conservatively skipped.
Only the selected host is read; the other provider is reported as unscanned.

Each read is capped at 128 KiB, with an incomplete boundary record omitted. Output
is capped at 24000 text characters per session and 6000 per message. Malformed,
missing, compacted and truncated input is reported. Tool/nontext/sidechain content
is omitted; coverage is always labelled partial. Claude duplicate UUIDs are removed;
Codex reads response messages only, omitting mirrored event messages. Line references
are used when stable message IDs are absent. The agent must still exclude retries,
copied context and equivalent duplicated records when counting independent occasions.
Raw output is evidence to analyze in the active conversation; never persist it in
Dryft. Summaries alone cannot establish independent recurrence reliably.

Return at most ten candidates with proposed name, purpose, reusable steps, inputs,
recurrence count, source session/turn references, limitations, overlapping skills
and why reuse helps. Two separate occasions may be in one session or several;
multiple tool calls for one request count once. Discovery never creates skills
until the user selects and approves them. If none qualify, show an empty result
and coverage limitations. Installing the discovery skill does not grant access
to conversation history.

## Enabled integrations

Approved skills always keep their full content in `.dryft/skills/`. Bridges are
created only for enabled hosts. Ask your agent to enable the other integration
when needed; there is no dedicated enablement skill. Terminal alternatives:
`dryft agent enable claude` or
`dryft agent enable codex` adds all existing skills to that host and keeps their
original ownership. Restart the host session for discovery. If a pending update
reports changed integration ownership, propose it again before reviewing it.
