# Reviewing staged content for privacy

Before an authorized agent commit in this repository, use
[the development privacy skill](../.dev/skills/dryft-dev-pii/SKILL.md) and its
[review procedure](../.dev/skills/dryft-dev-pii/review.md). Review the exact staged
snapshot and complete proposed message, including body and trailers.

## Review the bytes that will be committed

Inspect full staged versions of changed files, staged names and the complete
message. Working-tree content can differ from the index, especially with partial
staging. The helper is read-only and must leave both index and working files intact.

Use the helper's snapshot identity to bind review to specific content. Pair pattern
checks with semantic review for personal names, account details, private paths and
other sensitive material. A clean pattern result covers only the detected patterns.
Use private local inspection for context that cannot safely appear in transcripts.

## Resolve findings and coverage gaps

Reports redact sensitive values and filenames. Preserve those reporting boundaries
when changing the helper. Binary, oversized, non-UTF-8, LFS and submodule content
require explicit handling; unavailable context leaves review incomplete.

Pause the commit for unresolved findings or incomplete coverage. If the user
explicitly accepts unchanged content, keep that decision bound to the exact finding
and content. Unrelated edits do not erase an applicable decision, while changes to
the accepted material require renewed review.

Scanning, accepting an exception and approving a source edit do not authorize
staging, committing or pushing. Git editors, hooks or concurrent writes may change
content after review; verify the resulting commit or disclose that final-byte
coverage could not be established.

## Keep review tooling scoped

Development helpers remain in `.dev/` and never ship in the wheel. The optional
Software Production stack carries its own standalone review resources without
imports from this repository's development harness. See
[project integration](constitution-privacy-integration.md) for that boundary.

## Verify helper changes

Use harmless synthetic sensitive values and a proposed message file. Include a
partially staged file, unusual filenames, a linked worktree and unsupported binary
content. Confirm redaction, stable finding identities for unchanged content and
snapshot changes when staged bytes or the message changes. Check that the helper
never modifies the index, executes a commit or prints raw sensitive excerpts.
