---
name: tdt-note
description: Save a tagged scratchpad idea when the user says add a note, take a note, or jot this down; connect notes about the same subject.
---

Find the workspace root (ancestor containing .tdt/config.json). Save rough ideas,
intentions and things to investigate in brain/notes, separate from approved
knowledge. A clear "add a note" request is sufficient authorization. If "note"
seems to mean an observation rather than a request to save, ask whether to save
it. Do not turn ordinary conversation into scratchpad entries automatically.

Before saving, run the exact `tdt ... brain review-turn <token>` command from the
current UserPromptSubmit context to prevent a second automatic candidate. If the
command or token is unavailable, explain and stop before saving.

Search existing notes using `tdt --workspace <root> brain search <subject>
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
recast an intention as a completed action. Use `index` as the fallback link.
Submit JSON on stdin via a quoted heredoc to
`tdt --workspace <root> brain note --user-instruction <actual-request-or-reference>`.
The CLI writes metadata and returns the saved path and related notes sharing
tags. Cite the path and briefly name useful connections. Do not directly rewrite
older notes: relationships are computed from shared tags in either direction.
No promotion to knowledge occurs. For scratchpad questions use tdt-search-notes.
