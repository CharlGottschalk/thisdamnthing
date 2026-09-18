# Development setup

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

Start with [the development index](README.md) for orientation. Follow
[making a change](contributing.md) after setup; [packaging](releasing.md) covers
distributable checks.

The [development constitution](../.dev/CONSTITUTION.md) governs how agents work
in this repository. Product architecture and behavior live in
[the MVP specification](mvp.md) and its linked contracts. Development skills also
follow the Agent Skills naming convention documented there.

After cloning, open this repository in Claude Code or Codex and say **"onboard
me"**. The agent follows [source onboarding](../.dev/ONBOARDING.md), interviews
you, checks tools and prepares your ignored `.dev/developer.json`.

Use [source onboarding](../.dev/ONBOARDING.md) for setup questions. The
[portable example](../.dev/developer.example.json) covers identity and executable
paths. Existing local settings are preserved.

The read-only standard-library helper works without installing Dryft:

```sh
python3 .dev/config.py get toolchain.python
# Use that interpreter for this check:
python3 .dev/config.py check
```

Python 3.11+ and Git are required. Selected agent executable paths are checked;
this does not prove account access or runtime support.

The existing agent-session hook loads only `.dev/CONSTITUTION.md`. It returns
SessionStart JSON for both hosts and ignores events outside this source repository.

- Claude Code uses `.claude/settings.json`.
- Codex uses `.codex/hooks.json`; `.dev/hooks/codex.json` is its reviewable source.
- `AGENTS.md` and `CLAUDE.md` provide the constitution-reading fallback.

Hook trust uses each host's native review with user authorization. Check output
with `python3 .dev/hooks/session-start.py`; direct invocation does not prove live
session delivery. The loader works without any developer profile.

Keep private tooling details in ignored `.dev/local/onboarding.md`. Use focused
manual verification; do not add automated tests or additional development hooks.

## Repository Git safeguards

After cloning, activate the tracked hooks for this clone:

```sh
python3 .dev/git-hooks/setup.py
python3 .dev/git-hooks/setup.py --check
```

On Windows, use an available Python 3.11+ command; Git for Windows supplies the
shell used by the wrappers. Verify wrapper execution on the target platform before relying on protection.
Onboarding includes activation. The setup command sets repository-local
`core.hooksPath` to `.dev/git-hooks`, preserves existing custom hooks/configuration
by refusing conflicts, and can be repeated. No global settings change. Git does
not automatically activate hooks just because their files were cloned.

The tracked `.dev/git-hooks/policy.json` is shared across developer machines:

- `main` and `master` are protected by default. Commits require a named working
  branch; protected branches and detached HEAD are refused. Create one
  with `git switch -c <working-branch>`. This also restricts detached rebase/edit
  commits; finish them under a deliberately agreed workflow rather than assume
  hooks enforce every Git history operation.
- Push checks use destination refs, so pushing `feature:main`, force-pushing or
  deleting a protected branch is refused. Push a working branch for review.
- Commit subjects use `type(scope)!: description`; scope and `!` are optional.
  Types are listed in the policy file. A body requires a separating blank line.
  Example: `fix(cli): preserve existing workspace files`. Generated merge/revert/
  fixup messages receive no exemption; supply a compliant message when committing.
- Privacy checks inspect full staged versions of changed files, staged names and
  the complete proposed commit message. They detect common credential/token forms,
  private keys, personal paths (home folders, mounted drives, Windows profiles
  and UNC shares), emails and international
  phone patterns. Example domains and generic path placeholders are allowed.
  Personal names, addresses and arbitrary identifiers are not comprehensively
  detected; use the fuller agent review described below. No network/model call occurs.
- Binary, large (>1 MiB), non-UTF-8, LFS and submodule content is reported as
  incomplete and blocks the commit pending explicit review. The index is never
  changed by scanning. `.env`, `.dev/developer.json` and `.dev/local/` staging is
  refused even with a privacy exception.

Findings identify a file by the first 12 hex characters of SHA256 of its
repository-relative path and line number (zero means the name itself), avoiding
printing sensitive filenames or values. Inspect your local staged diff to fix
findings. For an intentional public value or manually reviewed unsupported file,
a developer can approve the exact content interactively:

```sh
python3 .dev/git-hooks/check.py scan
python3 .dev/git-hooks/check.py approve-file relative/path
python3 .dev/git-hooks/check.py approve-message .dev/local/proposed-message.txt
```

The command requires typing `APPROVE` after review. Approvals are local/ignored in
`.dev/local/git-privacy-approvals.json`, bound to the exact path/content (or message),
and do not cover later edits. They never waive branch or commit-format checks.
Message comments are scanned conservatively before formatting cleanup. A subsequent
Git hook/editor may change content; these checks do not prove final commit bytes
or examine all previously committed history. Changing a tracked hook/policy affects
local behavior immediately, as with any client-side hook.

Local hooks can be bypassed with Git options such as `--no-verify`, plumbing
commands or configuration changes, and fast-forward branch movements do not run
commit hooks. For enforcement independent of developer machines, configure remote
branch rules/required checks separately. These hooks do not configure GitHub or
intercept all pushes from other clients. A failed setup must not be described as
active protection. Preserve custom hooks and integrate them explicitly before
changing their configuration.

## Agent privacy review

Run `python3 .dev/skills/setup.py` to expose `/dryft-dev-pii` through this
repository's Claude/Codex discovery. It preserves conflicting entries, never
registers globally and reports read-only directories as pending. AGENTS.md also
points directly to the canonical skill. Read
[the review procedure](../.dev/skills/dryft-dev-pii/review.md) before any authorized
agent commit. The read-only helper adds exact snapshot/message evidence and
heuristics; semantic review is required in addition to the existing Git hooks.
No new hooks are introduced. All development skills stay outside the wheel.
