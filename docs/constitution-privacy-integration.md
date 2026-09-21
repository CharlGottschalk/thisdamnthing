# Project constitution and privacy integration

The optional Software Production stack provides project constitution setup and
pre-commit privacy review. Keep both workflows in the separate stack repository.
Core owns project registration and workspace policy; it does not ship the stack's
project templates or the source-development privacy harness.

## Set up project rules

Start from a registered external project and inspect its existing instructions.
Use the stack's constitution workflow to clarify and approve project rules, then
preview the generated files before writing. Registration itself must leave project
source unchanged.

Preserve unrelated settings and SessionStart entries. Repeated setup with identical
content should be stable; replacing owned content requires the expected prior
hash. Scope the loader to the project so outside directories and nested independent
Git projects do not receive its instructions.

Project policy can coexist with the workspace Constitution. Do not silently copy
ThisDamnThing's development rules into a user's project. Keep machine-specific developer
configuration ignored before writing local values.

## Make generated setup independent

Declare guides, templates and standalone helpers in the stack manifest. Project
setup must remain usable after the stack is removed: generated loaders cannot
import code from a bundle that uninstall will delete. Stack removal owns its
runtime assets, not the user's generated project configuration or constitution.

## Connect review to authorized commits

The stack's constitution, build and closure guidance directs agents to the shared
privacy procedure before a separately authorized commit. Review full staged files
and the complete message. An approved brief, rule change or setup operation does
not authorize a commit or publication of local configuration.

Follow [privacy review](privacy-review.md) for snapshot binding, retained decisions,
coverage gaps and final-byte verification. Keep stack helpers standalone and
behaviorally consistent with the development procedure when changing shared logic.

## Verify the integration

Install the stack in a disposable workspace and register a scratch Git project.
Check preview without writes, approved setup, repeat setup, scoped updates and
preservation of unrelated hooks. Invoke the loader directly for inside and outside
paths, then check actual delivery in a fresh host session.

Exercise privacy review with different staged and unstaged content and a complete
message. Uninstall the stack and confirm project policy, generated setup and loader
behavior survive. Check the stack catalog and doctor after removal.
