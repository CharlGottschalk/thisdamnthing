# Care for your workspace

For terminal examples, run workspace commands from the workspace root. External
projects and stack bundles are sibling directories; adjust their relative paths.

Your brain is readable local Markdown. Keep the whole workspace together:
`.dryft/` also holds configuration, ownership records, pending operations and
canonical skills. Host directories contain workspace-local bridges and settings.
External projects remain at their registered paths and need separate backups.

## Back up and restore

Close DUI sessions, stop agent sessions and let Dryft writes finish before copying
the entire workspace, including hidden directories. Keep backups private and
preserve file contents and directory structure. Restore a consistent whole copy,
then use `/dryft-workspace` in a fresh agent session to check it (terminal:
`dryft --workspace PATH doctor`). Doctor checks files and state; check host
trust and skill discovery separately. Do not discard ownership
records to make an edited file pass validation.

## Upgrade or move

Ask your agent to help back up and upgrade or move the workspace, giving the
intended destination or release. There is no dedicated core upgrade or move
skill. Use `/dryft-workspace` to check the result and `/dryft-update-stack` for
optional stack updates. In Codex, use `$` in place of `/` or the skill picker.

### Technical procedure

Back up first. For a release installed from PyPI, use `pipx upgrade usedryft`. For a
source installation, run `pipx install --force .` from the chosen newer checkout.
Then run `dryft init "."` to refresh unchanged owned core resources,
guides and hook paths for saved enabled hosts. Init preserves unrelated files and
refuses edited or missing owned content. Preserve edits separately and reconcile
against your backup before retrying. Keep the pipx environment available because
hooks refer to its Python interpreter.

After moving the workspace, rerun init at the new location, inspect generated
hook paths and review host trust again. A move does not relocate external projects
or rewrite references inside notes. Registering a moved project path creates a
new identity; approved project knowledge is not automatically refreshed.

Core refresh does not update optional stacks. Use `/dryft-update-stack` for each
selected stack. Terminal alternative: run `dryft stack update ID --check`,
review the replacement, then approve its exact token. Review executable trust and
prerequisites separately. Restart host sessions after core, stack or skill changes.
See [recovery](troubleshooting.md) for interrupted operations.

## Know what is private

Candidates, approved notes, project paths, local configuration, skill proposals
and DUI responses can contain private information. Brain approval makes a note
eligible for retrieval; it does not authorize publishing or sharing it. Secret
filters are heuristic, so inspect content before approval, backup sharing or export.
Full conversation transcripts stay with the host; Dryft capture stores summaries
and provenance references rather than full transcripts. Optional history discovery
reads only identified accessible histories and does not persist its raw output.

DUI close stops the service and retains responses; cleanup deletes that session's
retained data. Keep session URLs private. Provider indexes are disposable local
state and may also contain sensitive derived data. Markdown remains authoritative.
Trusted hooks, providers and custom browser code must be reviewed: local provider
subprocesses retain normal OS access, and workspace policy is agent guidance rather
than an operating-system sandbox. Dryft does not change host permission settings.
