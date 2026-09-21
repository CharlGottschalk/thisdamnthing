# Exact-content privacy review

Direct invocation authorizes read-only review of the selected worktree/index and
proposed message. It does not authorize fixes, staging, commit, push, identity
changes, history rewriting or source removal. Preserve the original task intent.

1. Resolve the intended Git worktree, including linked worktrees and any explicit
   GIT_INDEX_FILE environment. Ask if the target is ambiguous. Use the companion
   helper with direct subprocess argument arrays, never shell interpolation of
   paths or messages. The helper resolves Git's actual index and uses NUL-delimited
   paths/object IDs. Do not replace index bytes with working-tree reads.
2. Obtain the complete proposed message (subject, body, trailers). For already
   authorized commit work, prepare a safe Conventional Commit message in a private
   literal file outside tracked content; otherwise request it. Without it, return
   incomplete/message pending. Never put detected values in the proposal.
3. Read the helper's sanitized JSON. Status pass means bounded pattern coverage
   only. Complete a semantic review of the full staged versions, staged paths and
   message: names, personal identifiers, private emails, phones, physical addresses,
   account/user IDs, internal organizations/customers, credentials/tokens and
   machine paths, including custom Unix roots, Windows profiles and UNC shares.
   For safe local inspection, use object IDs from Git's raw NUL-delimited staged
   diff with cat-file; never follow symlinks or external textconv/diff commands.
   Inspect only changed staged blobs (1 MiB each, 8 MiB total), not history or
   untracked/ignored files. Do not dump raw source/message into terminal logs or
   agent transcripts: use a private local viewer with the user where sensitive
   context is not already safely available. If semantic inspection is unavailable,
   return incomplete and request that bounded local review; do not invent a pass.
4. Return pass, findings, or incomplete with snapshot, coverage/gaps and masked
   findings. A file reference is SHA256 of its raw repository-relative path,
   first 12 hex digits; line numbers are one-based and location `path` refers to
   the filename. Message line 1 is the subject; later lines cover body/trailers.
   Keep entire excerpts `[redacted]`, since adjacent text may also be private.
   Use these references for local resolution; never log raw names/paths/secrets.
   Existing-context means an identical line exists in the immediate prior version
   (rename/copy source where Git detects it), not proof of prior public exposure.
   Duplicated/moved lines can be classified as existing; inspect that distinction
   semantically. A missing prior version is incomplete, not evidence of newness.
5. Explain heuristics: author/contact attribution may be intentionally public;
   example domains, generic placeholders and ordinary source/URL paths can be
   legitimate. Do not automatically delete or broadly exclude them. Suggest
   relative paths/placeholders, reserved example emails or a scoped untracking/
   ignore correction. Never print a credential as an example fix. Publication of
   author/committer identity is a separate optional concern; never change it silently.
6. Findings pause the agent commit until corrected or explicitly accepted by the
   user for the identified finding IDs and unchanged bytes. Preserve those exact
   decisions in the current conversation; do not ask again for unchanged IDs.
   Semantic findings need an equivalent digest of path/blob or complete message,
   category and location. Never accept on the user's behalf. Declined, unresolved
   findings and coverage gaps keep the commit paused. Unsupported files require
   bounded manual inspection; acceptance alone must not disguise missing coverage.
   If resuming without reliable decisions, report what is missing. Any retained
   decision file must be local, verified ignored, minimal (digests and decisions,
   no raw evidence), and never promoted to brain notes or tracked reports.
7. Fix only within existing authorization, preserving unrelated edits and partial
   staging. Show a sanitized scoped proposal if authorization is missing. Never
   broad `git add`, discard/rebuild the index, auto-remove files or rewrite history.
   A prior leak needs separate handling. Re-run review after fixes/staging/message
   changes. Reuse only unchanged finding decisions; review all new findings.
8. Immediately before an authorized agent commit, rerun the helper with the same
   complete message and require the snapshot to match the semantically reviewed
   snapshot. A mismatch requires renewed review. Pattern exit zero alone does not
   authorize a commit; only full coverage and resolved/accepted findings do.
   Use an argument array such as `['git', '-C', repo, 'commit', '--cleanup=verbatim',
   '-F', message_file]`; no `-a`, path-limited commit or extra message/trailer flags
   that change the reviewed selection. Honor existing Git safeguards. Editor/hooks
   and concurrent writers can still change bytes after review: do not claim final
   coverage unless the resulting commit tree/message are verified against the
   reviewed index entries/message. Otherwise explicitly report final-byte coverage
   unverified. On discrepancies pause further publication and report masked
   locations; do not undo the commit automatically.

This is agent workflow guidance, not guaranteed manual-commit interception. No
scan proves absence of private information. Project constitutions should reference this boundary; publication readiness
checks cover release contents and history separately. These workflows do not authorize either operation.
