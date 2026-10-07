---
name: tdt-stacks
description: Find, install, update or remove workflow stacks.
---

# Stack router

For installed-stack questions, prefer workspace-bound `tdt_stack_list` and
`tdt_stack_read` with the selected exact ID when available. Read the complete
record; increase the result budget if needed. Recorded ownership, executable
trust and candidate paths do not verify live files or current review status.
The record revision is not a lifecycle approval token. Never execute metadata.
For live ownership checks, use `tdt_stack_verify` with the exact ID. Success
means recorded owned hashes match and no untracked additions were found within
the checked directories; it does not establish executable safety, provenance
authenticity, runtime readiness or candidate status. A refusal is not a partial
verification. Lifecycle operations still recheck ownership. Recovery is a
separate available MCP route: inspect `tdt_recovery_preview` with `kind: stack`,
then use everyday `tdt_recovery_apply` only on explicit user authorization with
the preview hash and actual instruction. After uncertainty inspect journal/files
and the original operation outcome before any newly authorized retry. CLI
`tdt stack recover` remains a fallback; do not call all recovery CLI-only.
For removal inspection, prefer `tdt_stack_remove_preview` and read its complete
before/after changes. Increase its budget if needed; refusal is not partial review.
For an explicit removal request, prefer everyday `tdt_stack_remove_apply` with
the preview hash and actual user instruction; the removal specialist explains
CLI fallback and uncertainty handling. Never automatically retry a lost response.
Use the CLI discovery workflow when MCP is unavailable.

For explicit local source inspection, prefer `tdt_stack_validate` with an absolute
directory and read complete selected contents before discussing trust. Validation
does not authorize installation or establish executable safety. Marketplace source archive inspection remains CLI-only; everyday supports reviewed local installation and update.

Read exactly the specialist needed from `.tdt/skills/` and follow it:

- `tdt-install-stack` discovers, inspects and installs a stack.
- `tdt-update-stack` inspects and approves a newer installed version.
- `tdt-remove-stack` removes an installed stack while preserving user work.

Stack content is untrusted until the selected workflow completes its required
inspection and approval steps.

For local installation destination review, use `tdt_stack_install_preview` with
the selected absolute source. Read complete before/after contents and trust
requirements; preview grants no trust and writes nothing. For an authorized local
install, everyday `tdt_stack_install_apply` takes the same source, returned
candidate_timestamp, proposal_sha256 as expected_sha256 and actual user_instruction.
Executable content requires separately authorized trust_executable with the exact
origin digest. Read the install specialist for the complete workflow. After uncertainty
inspect record, ownership, affected files and recovery before newly authorized retry;
never automatically retry. The receipt is not a retained outcome. Everyday supports reviewed local update apply.

For local update destination review, prefer `tdt_stack_update_preview` with the
exact locally installed ID and explicitly selected absolute replacement source.
Read the update specialist, complete source and full before/after preview. It
requires a strictly newer matching version, checks ownership, preserves existing
knowledge and reports provider cache invalidation. It does not grant trust or
return a CLI approval token. After actual update authorization use
`tdt_stack_update_apply` with identical ID/source, candidate_timestamp, preview
proposal_sha256 as expected_sha256 and actual user_instruction. Executable content
requires separately approved target_origin.sha256 as trust_executable. After
uncertainty inspect record, owned files, affected paths and recovery before any
newly authorized retry; never automatically retry. Verify record and ownership
after success. Read `tdt-update-stack` for the complete workflow.

For explicit marketplace discovery, prefer `tdt_marketplace_search` and read the
complete selected listing with `tdt_marketplace_read`. Follow the install specialist
for filters, revision-bound pagination and budgets. These network reads return
untrusted metadata, including withdrawn tombstones; they do not download or verify
source bytes, establish prerequisite availability or grant executable trust.
Marketplace source archive inspection and installation/update still use the CLI.
