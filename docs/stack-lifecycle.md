# Stack lifecycle and recovery

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

`stacks.py` handles validation, installation and removal. `stack_updates.py`
prepares approved replacements. Use these shared paths for local and registry
stacks so ownership, trust and recovery remain consistent.

## Inspect before changing installed content

```sh
tdt stack validate ../example-stack
tdt stack install ../example-stack --inspect
tdt stack update example-stack --check
```

Validation checks the manifest and selected files. Inspection discloses content,
prerequisites and executable trust requirements without activating the stack.
Update inspection binds its approval hash to installed ownership, replacement
content, provenance and registry disclosures.

For an interactive update, the terminal requires an explicit yes. For agent-driven
or noninteractive use, pass the inspected hash only after approval:

```sh
tdt stack update example-stack --approve APPROVAL_SHA256
```

Changed inputs require a new inspection and approval. Executable trust is separate
and bound to the target content digest. A failed update check is an error; do not
report it as “up to date.”

## Preserve source identity

Registry updates retain the exact endpoint and repository. An origin-only legacy
record needs its original endpoint supplied explicitly, with origin checks.
Local updates use the recorded source or an explicit `--source` directory. Do not
silently switch local and registry source kinds.

Refuse downgrades, same-version replacements and ineligible registry selections.
Recheck required prerequisites under the mutation lock. Prerequisite confirmation
does not install dependencies or authenticate services.

## Write through the transaction

Update owned bundle files, canonical skills, enabled-host bridges, trust records
and the [docs catalog](stack-documentation.md) together. Remove obsolete owned
files and empty directories. Unchanged stack knowledge need not be imported again;
changed knowledge becomes a pending candidate and follows ordinary review.

Use the existing journal and cooperating-writer lock. Keep hosts idle during
mutation. After an interrupted operation:

```sh
tdt stack recover
```

Recovery must preserve unexpected edits and report conflicts. It does not protect
against hostile concurrent filesystem replacement or guarantee power-loss durability.

## Remove only owned runtime assets

```sh
tdt stack uninstall example-stack
tdt stack list
tdt stack docs
tdt doctor
```

`uninstall` and `remove` use the same implementation. Remove the bundle, owned
entry points and runtime eligibility while preserving brain notes, approved user
skills and unrelated configuration. Refuse missing or edited assets and untracked
additions in owned directories; preserve and reconcile them before retrying.
The shared hook dispatcher reads installed/trust records, so removal must revoke
eligibility there too.

## Verify lifecycle changes

Prepare two harmless versions that change a skill name and a declared guide.
Inspect, decline, approve the exact replacement, and confirm old entry points
are gone. Repeat with edited owned files, stale approval and an interrupted write.
Compare file hashes for unrelated content after success, refusal and recovery.

Use fresh host sessions to check discovery after update and removal. CLI state,
loaded host context and native skill invocation need separate checks. Registry
transport coverage belongs in [marketplace verification](marketplace.md).
