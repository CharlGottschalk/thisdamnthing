---
name: tdt-note
description: Save tagged scratchpad ideas and find related notes.
---

Find the workspace root (ancestor containing .tdt/config.json). Save rough ideas,
intentions and things to investigate in work/notes, separate from approved
knowledge. A clear "add a note" request is sufficient authorization. If "note"
seems to mean an observation rather than a request to save, ask whether to save
it. Do not turn ordinary conversation into scratchpad entries automatically.

Before saving, prefer `tdt_capture_suppress` on the workspace-bound MCP server
with the current UserPromptSubmit token. If unavailable, run the exact
`tdt ... brain review-turn <token>` command from that context. If the current
token or both transports are unavailable, explain and stop before saving.

Use `tdt_note_list` and `tdt_note_read` on that server to inspect existing
subjects and tags, paging as needed. CLI search remains available using `tdt --workspace <root> brain search <subject>
--scope notes`. Inspect matching notes' tags with `tdt brain notes --tag <tag>`
(using the workspace option outside the root). Reuse existing tags for the same
entity or subject. Choose 1–8 specific lowercase tags, with hyphens between
words. Prefer project/product/entity names and precise topics. Do not use broad
tags such as idea, note, plan, investigate or work as relationship keys.
Resolve obvious naming variants to an existing tag; ask when entities are
ambiguous. Do not invent project registration IDs from product names.

For example, a mastering-module investigation and a module-colour idea for the
same product share that product's tag, with their own topic tags. A personal
travel idea uses destination/travel tags, not the product tag. Shared tags mean
related subjects, not supporting evidence or identical facts. Avoid storing
sensitive personal details in tags unnecessarily.

Preserve what the user actually said, including tentative wording and questions.
Use the summary schema in docs/brain.md plus a required `tags` array. Use kind
question for something to investigate or fact for a stated intention; do not
recast an intention as a completed action. Scratchpad links use the returned
`work/notes/<filename>` path without `.md`; approved links remain brain-relative.
Use `index` as the fallback link.
Prefer `tdt_note_save` on the workspace-bound MCP server with the tagged summary
and `user_instruction` containing the actual request or reference. Read its
returned ID with `tdt_note_read` for the saved path and content; use the note
inventory to identify shared tags. If MCP is unavailable, submit the identical
JSON on stdin via a quoted heredoc to
`tdt --workspace <root> brain note --user-instruction <actual-request-or-reference>`.
After an uncertain response, inspect the note inventory before an identical retry
through either transport. Normalized title, kind, body, sources, project and sorted
unique tags determine identity; links and audit references do not. An existing
result preserves original content. Never alter content to force a retry or use
fallback to bypass validation or permission refusal.
Cite the saved path and briefly name useful connections. Do not directly rewrite
older notes: relationships are computed from shared tags in either direction.
No promotion to knowledge occurs. For scratchpad questions use tdt-search-notes.
