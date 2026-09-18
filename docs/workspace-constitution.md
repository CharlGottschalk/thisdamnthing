# Workspace constitution

`src/dryft/constitution.py` manages the workspace's user-authored policy at
`.dryft/CONSTITUTION.md`. Core initialization, stack operations and integration
changes must preserve it. Project-specific rules are a separate concern; see
[project constitution integration](constitution-privacy-integration.md).

## Read and save policy

```sh
dryft constitution show
dryft constitution save --expected-sha256 HASH --user-instruction REFERENCE < reviewed-policy.md
```

Read the complete policy and its revision before proposing changes. Clarify
ambiguous permissions, contradictions and exception duration through chat or DUI.
Show the exact revised text and save only after approval. The reference records
that decision; it cannot authenticate human intent.

Saves validate bounded UTF-8 Markdown, use a cooperating-writer lock and compare
the expected revision before atomic replacement. Refuse stale revisions, invalid
content and symlinked managed paths. Avoid concurrent editing: a noncooperating
writer can still race the final check and replacement.

## Load current rules

Workspace-local UserPromptSubmit hooks read fresh policy for each invocation.
SessionStart also supplies it when the host emits startup, resume or compaction
context. Scope checks exclude outside sessions and nested independent workspaces.
Root instructions provide a `constitution show` fallback when hooks are unavailable.

Once policy is activated, an expectation marker makes unexpected deletion an error.
An expected missing, malformed or oversized policy blocks the request hook. Restore
the approved file; do not remove the marker to conceal missing policy. Inspect a
stale writer lock and establish that no writer is active before removing it.

## Keep permission semantics explicit

Rules describe how the agent should behave. They do not install a pre-tool policy
evaluator or provide filesystem/network isolation. Host permissions still apply.
A pasted path is a reference unless the user grants access. Distinguish one-action,
one-request, session and persistent exceptions when interpreting permission.

Canonical path checks reject siblings and symlink escapes at check time; they do
not eliminate filesystem races. Never claim a rule is enforced merely because its
text was delivered to the model.

## Verify changes

Check save/update, stale revision refusal, repeat initialization and preservation
through stack lifecycle changes. Use harmless paths to check outside, sibling and
nested-workspace exclusion. Inspect valid, missing, oversized and malformed policies.

Separately exercise live interviews and policy delivery on each host: load a rule,
change it with approval and observe a subsequent request using the new revision.
Check fallback behavior when hooks are unavailable. Direct wrapper execution and
live request delivery are distinct checks.
