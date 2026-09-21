# Packaging and release

Run these examples from the source repository root; relative paths are resolved
from that directory. Keep disposable workspaces and stack checkouts outside it.

Publish the release wheel to PyPI so users can install with `pipx install thisdamnthing`.
Users can also ask their agent to install and set up ThisDamnThing via pipx; this follows
the same CLI installation, workspace initialization and doctor flow. No source
clone or manual wheel download is needed for the public user path.

The distribution and Python package are `thisdamnthing`; the CLI is `tdt`.
Canonical source is `https://github.com/CharlGottschalk/thisdamnthing`. The package description
uses the root README and declares Apache-2.0 with the included LICENSE file.
Setuptools 77.0.3 or newer is required to build this license metadata.
Verify README image/document links after moving the source to the canonical
repository and before publishing the package.

A working local build is not a public release. Python package publication,
stack artifact publication and the marketplace website are separate deliverables.
Verify each distribution path and target platform independently.

## Check a local package

Use the intended Python 3.11+ interpreter and available build tooling. From a
clean source checkout, build a wheel into a disposable directory:

```sh
python3 -m pip wheel . --no-deps --wheel-dir dist
```

Build tooling may need network access if it is not already available. For an
offline check, prepare it first rather than claiming the command is offline.
Inspect the wheel with Python's `zipfile` module or an archive viewer. It should
contain `thisdamnthing`, its runtime resources and package metadata. It must not contain
`.dev/`, root development docs, local profiles or optional stack source.

Install the wheel in a disposable environment outside the checkout. Run version,
help, init with `--agent none`, doctor and empty stack/project listing. Inspect
installed guides. For an upgrade, retain harmless brain notes and unrelated
configuration, refresh through the documented setup flow, and verify preservation
and refusal of edited owned files. Use [the runbook](e2e-runbook.md) for broader
agent and lifecycle coverage when relevant.

Record revision, wheel hash, Python/OS, actual results and gaps in release review
records. Keep raw logs and local locations under ignored `.dev/local/`.

## Prepare a public release

1. Confirm the package name, destination, version and release authorization.
2. Complete checks appropriate to the change and state platform/host limits.
3. Review the exact source and distributable for private content and unwanted files.
4. Prepare concise release notes and accurate installation guidance.
5. Publish only with authorization, then verify the actual download and installation.

Before release, label `pipx install thisdamnthing` as the planned public installation
command. After publishing, verify it resolves to the intended ThisDamnThing package and
installs successfully before claiming availability.
Stack releases also need an actual repository/license, immutable revision, selected
content hashes and archive digest required by the [marketplace contract](marketplace-contract.md).
Bundled provider assets must meet their declared platform, offline and license
requirements. A local archive or fixture feed does not prove a public release.

## Publication path policy

First-party file examples use relative paths with an explicit working directory.
Local generated state may retain canonical absolute paths required for project
identity, host transcripts, ownership and executable invocation; it is not release
source. Never include a developer workspace or local evidence in an artifact.

Unmodified third-party libraries may retain upstream build/system paths, public
author attribution, license contacts and protocol URLs. These accepted exceptions
do not permit private ThisDamnThing developer paths or credentials. Remove unnecessary
launchers/build metadata where safe; preserve licenses and native library bytes.
Record source snapshots, artifact hashes, the scoped review and remaining coverage
limits before publication.
