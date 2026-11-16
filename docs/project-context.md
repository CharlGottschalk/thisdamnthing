# Project context

User decisions (2026-11-16): registered projects keep living context that agents
update during work, not only a registration stub.

- The registration note `brain/projects/<name>-<id>.md` is the project index. A
  generated registry between `<!-- tdt:registry:start -->` and `end` links related
  projects, notes and the last ten history days. The text above it is the summary.
- The folder `brain/projects/<name>-<id>/` holds `notes/` and `history/<date>.md`.
  All are ordinary approved brain notes with `project` set, so search, audit and
  relink treat them like other notes. `registration_state` reads only top-level files.
- Every change to project files gets history, from agents or the user, with the
  author named. One entry per session per day; a repeat with the same session replaces
  it. The Stop hook asks for it, also when capture is suppressed.
- "Add X to project context" saves a note directly (the request is the approval).
  Onboarding writes the summary directly. Approved project-tagged candidates route
  to the project's `notes/`.
- Relations (`related: [{project, kind}]` on the registration note) are directed;
  the reverse shows in the other index. Mentioning either project loads both summaries.

Core: `project_context.py`. CLI `tdt project context|note|history|summary|relate`.
MCP `tdt_project_context` (both), `tdt_project_note_save`, `tdt_project_history_add`,
`tdt_project_summary_save`, `tdt_project_relate` (everyday).

Known ceilings: the brain note scan caps at 2000 entries, so many history days
across projects will need a higher cap or archiving. A relink does not refresh the
other project's registry title until its next context write.
