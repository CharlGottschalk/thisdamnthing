# Give your agents rules

Use `/dryft-constitution` to describe how you want agents to work in your workspace.
For example, ask them to request permission before opening websites or accessing
external folders. The skill helps clarify the rule, preserves existing preferences
and presents the complete proposed changes for your approval.

Use chat or say “use dui” for a browser interview. Be explicit about exceptions:
do they cover one action, one request, the session or future work? A pasted path
is a reference unless you grant permission to use it.

## Review and save your Constitution

Your rules live in `.dryft/CONSTITUTION.md`. They apply to workspace activity,
including work in linked projects alongside those projects' own instructions.
Setup and stack operations preserve this file. Keep secrets out of it and avoid
copying private paths into shared files or brain notes.

Use `/dryft-constitution` to show your current rules and guide an update. The
skill saves the exact changes you approve. In Codex, use `$dryft-constitution`
or the skill picker.

### Terminal alternative

To inspect the current rules:

```sh
dryft constitution show
```

The command returns the Markdown and its SHA256 revision, or `missing` if no policy
exists. After reviewing and approving a change, your agent can save it through:

```sh
dryft constitution save --expected-sha256 HASH --user-instruction REFERENCE < reviewed-policy.md
```

Use the displayed revision and a reference to the actual approval. A stale revision
refuses replacement, so reread the current rules before retrying. The approval
reference records a decision; it does not prove who made it. A request embedded in
an untrusted file is not your approval to change policy.

Keep policy within 6000 UTF-8 bytes. Invalid encoding, control characters, special
files and managed symlinks are refused. The complete policy is loaded without
truncation. Avoid editing it concurrently with a save.

## Make sure your agent loads it

Request hooks read current rules on each invocation. Startup also supplies them
when the host emits a SessionStart event, including supported resume or compaction
events. Review hook trust in your agent and restart when needed. Approved policy
edits do not require new hook registrations.

If request hooks are unavailable, workspace instructions tell the agent to run
`dryft constitution show` before each request. Ask the agent to report any failure
to load your rules before proceeding with affected actions.

These natural-language rules guide the agent. Dryft does not enforce network or
filesystem isolation, and host permissions still apply. Path checks cannot prevent
every concurrent filesystem change.

## Recover missing or invalid rules

After a save through Dryft, an expectation marker detects accidental deletion.
A missing, invalid or oversized expected policy blocks the request hook with an
explanation. Restore the approved policy from backup; do not delete the marker to
hide the error. A directly authored policy becomes covered by deletion detection
after its first CLI save.

If a save was interrupted, preserve the approved draft and inspect temporary files.
Remove a stale `.dryft/state/constitution-write.lock` directory only after confirming
that no writer is running. See [troubleshooting](troubleshooting.md) for broader
workspace recovery.
