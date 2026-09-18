# Source-developer onboarding

Run this workflow when a developer says **"onboard me"**. It configures source
development in this clone, not an installed workspace or an external project.
It never automatically starts implementation.

## Orient and inspect

Read `AGENTS.md`, `.dev/CONSTITUTION.md` and the existing ignored
`.dev/developer.json`, if present. Explain that `src/` ships, `.dev/` develops it,
and `docs/` documents development. Preserve existing answers on a rerun and ask
only what the developer wants to change. Never import another person's profile.

Onboarding authorizes narrow read-only discovery of `git config user.name`,
executable paths and versions for Python, Git and selected agents. Do not inspect
credentials, shell history or unrelated directories. Accept supplied paths when
requested and report unchecked tools as unverified.

## Interview

1. Confirm the developer's name and a lowercase hyphenated slug. Propose existing
   values or the local Git name, stating the source. Keep identity out of tracked files.
2. Ask: **Which roles would you like to assign to which agent?** Briefly explain
   coordinator (scope and organize), investigator (research), implementer (build),
   verifier (check) and reviewer (assess changes). Accept any subset assigned to
   Claude or Codex, one agent for
   several roles, or no agents. Do not require all five assignments.
3. Confirm executable paths for Python, Git and the selected agents using focused
   detection. Keep existing model/effort preferences when present; do not require
   new model/effort choices just to record an agent assignment.

Do not ask for a dispatch mode, concurrency or staging directory. These settings
have no active behavior. Existing values remain untouched. Role assignments are
reference preferences; they do not start agents or control when work proceeds.

## Save the reference profile

Use `.dev/developer.example.json` for identity and tooling, then add a `roles`
object during this interview, for example `"roles": {"implementer": {"agent": "codex"}}`.
`tasks` is `internal`. Each selected role has
an `agent`; `model` and `effort` may be retained as optional reference values.
Human-only development uses empty `agents` and `roles` with Git/Python tooling.

For an existing profile, preserve its structure and all unrelated fields. If its
assignments use the legacy `orchestration` key, update only explicitly requested
assignments there; do not rename the key or migrate the profile. Never discard
saved model/effort values. The current user's instruction to leave a profile
unchanged takes precedence over this save step.

Show the concrete proposed JSON and save only under the user's authorization;
never ask again for values already approved. Use Python JSON support. Confirm
`.dev/developer.json` is ignored and untracked. Do not publish a tracked profile
or silently rewrite Git history. Record versions/readiness in ignored
`.dev/local/onboarding.md`, not in the profile. No credentials belong in either.

## Verify and finish

- Run `.dev/config.py check` with the selected Python 3.11+. It validates identity
  and executable availability only. Review role assignments directly against the
  answers collected above; no helper interprets them. Use
  `.dev/config.py get toolchain.python` to read the interpreter preference.
- Check versions of Git, Python and selected runtimes. Finding an executable does
  not prove authentication or model support. No live agent launches are required.
  Missing optional role tooling does not prohibit other authorized development.
- Activate the tracked repository Git safeguards with
  `python3 .dev/git-hooks/setup.py`, then `--check`. This onboarding authorizes
  repository-local activation only. Preserve conflicting custom hooks and report
  the conflict. See `docs/development.md` for scope and limitations.
- Expose the repository-only privacy review skill with
  `python3 .dev/skills/setup.py`; report conflicts or read-only discovery paths.
  Never register it globally.
- Explain the existing constitution-only SessionStart loader. Complete native
  hook trust only with authorization. A direct loader invocation verifies output,
  not live host delivery. Do not add development hooks or alter agent permissions.
- Record actual checks and gaps in `.dev/local/onboarding.md`. Finish with the
  assigned roles, tool readiness and any missing tools. Point to `docs/contributing.md` for the development workflow.

No database, automated tests, dependency installation, commit, push, publication
or deployment is part of this workflow. Automatic task execution belongs to a
future schema-driven feature, not onboarding.
