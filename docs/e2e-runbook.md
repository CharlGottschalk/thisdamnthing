# Full workspace E2E runbook

Use this runbook to verify a packaged build through a complete workspace workflow.
Run each affected host separately and keep results outside this guide. The
[component checklist](acceptance.md) helps narrow checks for smaller changes.

## Prepare the run

Use an installed build outside the source tree, two fresh disposable workspaces
(one for Claude, one for Codex), a scratch external source project, local copies
of the optional bundles needed by the workflow and a community-style bundle with
a harmless hook and knowledge note. Include spaces in workspace paths. Keep source repositories
and personal workspaces out of destructive fixtures.

Record the source revision and dirty state, wheel SHA256, Python/pipx/OS and host
versions, stack versions/digests, starting configuration and exact commands in
ignored `.dev/local/`. Keep this guide as a reusable procedure.
Prepare real host authentication and review each generated hook through normal
host trust. Do not infer runtime support from generated configuration or doctor.

For public integration, obtain actual GitHub release destinations/licenses and
the deployed Sites registry URL. If unavailable, report that phase as deferred.
A local feed/archive fixture can exercise the live install skill independently;
label fixture transport explicitly. It does not prove public GitHub or Sites.
Do not weaken production HTTPS or archive validation to make a fixture work.

## Execute in order, separately on each host

| Step | Action | Evidence required |
| --- | --- | --- |
| 1. Source install | Follow installed getting-started instructions with isolated pipx directories. | Version/help, package contents, no development harness/docs or bundled optional stacks. |
| 2. Zero-stack start | Init a path with spaces, configure the selected host, doctor/list. | Correct installed tree, all usage links resolve, empty stacks/projects. |
| 3. Preservation | Add unrelated provider settings and user files; repeat init. | Their hashes/values survive, repeated init is stable. |
| 4. Live startup | Open a fresh trusted host session and invoke workspace orientation. | Skill invocation plus actual SessionStart output, not merely instruction-file reading. |
| 5. Capture/review | Discuss two harmless decisions, display generated proposals, explicitly approve one and reject the other. | Automatic Stop capture, sources, pending exclusion, exact user decisions and approved-only search. Do not fabricate approval. |
| 6. Retrieval | Ask a linked question, an absent-evidence question and a conflicting-evidence question. | Actual dryft-search invocation, cited note paths, honest gaps and unresolved conflict. |
| 7. Project onboarding | Hash scratch source, invoke add-project, review proposed knowledge. | Canonical ID/path, evidence-based onboarding, identical external source hashes after registration. |
| 8. DUI | Use a grouped interview, submit in the browser and answer a follow-up. | Real event IDs and answers read/acknowledged by the active agent; chat fallback works. Close service. |
| 9. Stack builder | Install local builder, create/validate/install a minimal stack, invoke it. | Real output, explicit selected files, refusal to overwrite existing source. |
| 10. Software workflow | Install software-production; create brief, init tasks, build/close one tiny change in scratch source. | Project artifacts, observable behavior, task state and workspace handoffs. Exercise task/tasks/triage as applicable. |
| 11. Community bundle | Install harmless fixture with hooks and knowledge through ordinary public commands. | Digest-bound explicit hook trust, real host notification, pending knowledge excluded until approved. |
| 12. Marketplace | Discover the selected releases; install via CLI and live install skill, including a community-style entry. | Transport type, registry/repo/tag/commit and both digests; prerequisites, withdrawal refusal and no install on refusal. |
| 13. Website submission | Follow the actual Sites author submission/review flow for an authorized sample. | Submitted/reviewed listing result or explicit unavailable status; a draft file is not submission. |
| 14. Removal | Snapshot brain and unrelated host files, remove stacks, doctor and use core again. | Brain/user settings preserved, owned skills removed, zero-stack brain/project/DUI behavior remains. |

Use approved disposable content for replay/deduplication and stale-hash probes.
Observe that repeated capture delivery does not duplicate the proposal. Keep
failures/recovery observations, and fix blockers before rerunning affected steps.
No automated suite or new development hooks are required.

## Record verification results

For every step, record each host separately as passed, failed or unverified, with
artifact references in private verification records. Separate CLI-only and direct-hook
probes from live agent results. Local catalog fixtures, public downloads and website
submission are distinct checks. State exactly which platforms and interpreter
versions were exercised.

Use the results to support review and release claims. Keep execution chronology,
logs and resume notes outside the developer guides. Publication claims require
verification of the actual published artifact and destination.
