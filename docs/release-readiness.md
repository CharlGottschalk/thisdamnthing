# Release readiness

Use [packaging and release](releasing.md) for artifact checks and
[the workspace walkthrough](e2e-runbook.md) for manual acceptance.

## Compatibility

The Python distribution is `usedryft`; the command and import are `dryft`.
Core is Apache-2.0 and initializes with zero stacks. Python 3.11+ is required.
Supported platform claims are limited to Linux x86_64 with Python 3.12.
macOS, native Windows and other architectures are unverified.

Optional stacks declare their own versions, dependencies and platform requirements.
Validate those requirements before including a stack in a release.

## Publication checklist

- Select the reviewed source revision. Build a wheel and sdist; inspect their
  contents, metadata, installed resources and artifact hashes.
- Exercise the intended artifacts in disposable workspaces, including fresh-host
  discovery and the documented CLI and agent workflows.
- Review source and actual archives for private data, credentials and unintended
  development files. Keep detailed local reports outside public source.
- Validate each included stack and its license, compatibility, immutable release
  commit, archive digest and selected-content digest.
- Verify production website and registry contracts, access controls, abuse limits,
  response-size limits, dependency advisories and public links.
- Exercise the public registry with the CLI and both hosts: discovery,
  inspection, authorized installation, invocation and refusal/preservation paths.
- After publication, verify a fresh `pipx install usedryft`, then follow the README
  through initialization, doctor and first agent use.

Keep verification evidence outside public source. Trusted hooks and providers
retain OS access; agent instructions are not a sandbox.
