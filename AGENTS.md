# Dryft development

Read `.dev/CONSTITUTION.md` at session start if it was not already injected by
the SessionStart hook. Then read `.dev/CONTINUITY.md` if present. Read
`docs/mvp.md` before working on the MVP.

Keep `.dev/CONTINUITY.md` current with useful context, decisions, verification
results and next steps when completing or pausing work. This file is ignored and
untracked; each developer maintains their own. If absent, create it from the
current session without copying another developer's local context.

This is the source repository, not an installed Dryft workspace. `src/` holds
shipped source, `.dev/` is the development harness, and `docs/` is development
documentation. Follow the user's current instructions and keep the MVP small.

When a developer says **"onboard me"**, follow `.dev/ONBOARDING.md`. This sets up
source development, not a user's installed workspace or an external project.

Before an authorized agent commit, run `/dryft-dev-pii` from
`.dev/skills/dryft-dev-pii/SKILL.md` for the exact staged snapshot and complete
message. Findings or incomplete review pause the commit; preserve explicit
unchanged-content decisions. Review does not authorize staging, commit or push.
