# Integrating the Software Production stack

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

`dryft-software-production` is an optional stack in a separate source repository.
It coordinates work in linked software projects using core registration, skills
and DUI. Its bundle guides define the project artifact formats.

## Install and inspect the workflow

```sh
dryft stack validate ../dryft-software-production
dryft --workspace ../workspace stack install ../dryft-software-production
dryft --workspace ../workspace stack docs dryft-software-production
```

Start a fresh host session to discover its skills. Use the full
`dryft-software-production-` prefix with `brief`, `init`, `add`, `task`, `build`,
`close`, `tasks`, `triage`, `constitution` or `pii`.

## Keep workflow authority clear

A brief defines the project. Initialization derives work from its approved content.
Adding an existing project uses core registration and offers onboarding. Building
operates at the linked source path and follows that project's instructions.
Closure records the outcome and preserves work unless deletion is explicitly chosen.
Listing and triage read and organize retained work without inventing new scope.

Internal work states are draft, ready, doing, done, blocked and cancelled. If an
external provider is selected and connected, that provider owns descriptions and
status; local files retain references and implementation context. This integration
is agent guidance, not a background synchronization service.

Core DUI can collect context, briefs and plans. Carry submitted answers into chat
fallback and reuse approved content without repeating interviews.

## Separate project, workspace and knowledge records

Shared brief, project configuration and work records live in the project's
`.dryft/` directory. Ignore private developer configuration before populating it.
Workspace `.dryft/state/software-production` holds project and work-item handoffs.
These operational records are separate from approved brain notes.

Core registration must leave external source unchanged. Later project edits require
the user's work authorization. Uninstall owns stack runtime assets, not generated
project files. Follow [project constitution and privacy integration](constitution-privacy-integration.md)
when changing policy setup or commit guidance.

## Verify a workflow change

Use a scratch Git project and a disposable workspace. Exercise an approved brief,
initialization, one small build and closure. Check observable project behavior and
retained artifacts, then use a fresh session to list and triage remaining work.
Confirm no duplicate work is created on resume and unrelated source is preserved.

Check both DUI and chat entry paths for changed interviews. Verify external-provider
behavior only with an available authorized connection. Removal should preserve
project records, workspace handoffs and brain content while removing owned stack
skills and documentation entries.
