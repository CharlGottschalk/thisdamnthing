# Dryft development constitution

1. Follow the user's current instructions. Complete authorized work without
   inventing approval gates.
2. Keep changes small and purposeful. Prefer plain files, a small Python CLI and
   direct functions; add abstractions only when needed. Follow the product
   requirements in [docs/mvp.md](../docs/mvp.md) and its linked contracts.
3. Keep source in `src/`, development tooling in `.dev/` and development docs in
   `docs/`. Never ship development resources. Development skills and hooks belong
   only to this repository; never register them globally.
4. Preserve user work, files and configuration. Refuse path escapes and ownership
   conflicts. Keep developer identity, machine paths and local observations in
   ignored `.dev/developer.json` or `.dev/local/`; keep shared examples portable.
5. Verify changes with focused manual checks and report actual results and gaps.
   No automated tests for now. Use only the constitution SessionStart loader
   and the tracked Git safeguards in `.dev/git-hooks/`; no other development hooks.
6. Read the local `.dev/CONTINUITY.md` when starting work and update it with
   context, decisions, verification results and next steps when completing or
   pausing work. Keep it ignored and untracked for each developer; initialize it
   from the current session when absent.

Before an authorized agent commit, run `/dryft-dev-pii` from
`.dev/skills/dryft-dev-pii/SKILL.md` for the exact staged snapshot and complete
message. Findings or incomplete review pause the commit; preserve explicit
unchanged-content decisions. Review does not authorize staging, commit or push.
