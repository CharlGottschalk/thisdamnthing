# Developing the marketplace client

`src/thisdamnthing/marketplace.py` validates registry feeds and fetches selected archives.
Installation uses the ordinary stack transaction. Keep the
[public contract](marketplace-contract.md),
[registry schema](../src/marketplace/registry.schema.json) and
[packaged schema](../src/thisdamnthing/resources/marketplace/registry.schema.json) consistent.

## Follow the discovery and installation flow

```sh
tdt marketplace search "query"
tdt stack install example-stack --inspect
```

Use a configured HTTPS registry for explicit discovery and installation. Validate
its schema and semantic constraints before selecting a version. Show prerequisites,
review metadata and executable content before approval. Resolve GitHub releases
to immutable revisions and verify both archive and selected-content digests.

Record endpoint, repository, release reference, resolved commit and digests in
provenance. The install skill must use the same public commands as the CLI.
Doctor and local inventory operations should not trigger registry requests.

## Keep transport and extraction bounded

Validate HTTPS origins and redirects, response type/encoding, byte limits and
complete response bodies. Treat truncation and overflow as errors. Do not disable
TLS verification to accommodate a fixture.

Preflight ZIPs before writing: reject traversal, absolute paths, backslashes,
symlinks, duplicate or case-normalized collisions, excessive nesting and ambiguous
roots. Match extracted manifests and selected files against the inspected registry
metadata before the installer mutates workspace state.

Refuse withdrawn and absent/unapproved selections, including pinned versions.
Apply the contract's deprecation rules. Local installation does not consult a
registry and therefore cannot enforce registry withdrawal. Prerequisites require
explicit verification; the client is not a dependency solver.

## Use local integration fixtures explicitly

A registry on loopback can describe real GitHub releases. Supply its HTTPS endpoint
with `--registry` and retain default GitHub archive transport. If its certificate
needs local trust, use a per-process CA bundle that also trusts public GitHub roots.

For explicitly selected local archives, add `--local-archive-origin` matching the
registry's literal-loopback HTTPS origin. This option derives the local immutable
archive route and records the transport and actual archive URL in provenance.
It applies to install/inspect; updates do not inherit it. Keep every manifest,
archive, content, prerequisite and trust check enabled. Never use it as fallback
for a failed public request.

See the [installed stack guide](../src/thisdamnthing/resources/docs/stacks.md) for complete
local transport commands. Recompute archive digests for the bytes served by each
transport; two ZIPs with identical selected content can have different hashes.

## Verify changes

Exercise parser/schema errors, ineligible versions, altered digests, unsafe ZIPs,
same-origin and cross-origin redirects, truncated bodies and size limits. Snapshot
a disposable workspace to confirm refusals leave its files unchanged.

Separate parser fixtures, real loopback TLS, public archive downloads and public
registry installation in verification records. Run the installed CLI and live
install skill for each affected host. Website authoring, review and submission
belong to the website service and require their own verification.

## Local registry integration checks

For explicitly selected archives hosted by a local registry, use both
`--registry https://127.0.0.1:3443/registry/v1/index.json` and
`--local-archive-origin https://127.0.0.1:3443` on `stack install`, including
`--inspect`. The origin must be a literal-loopback HTTPS origin matching the
registry, without credentials, path, query or fragment. Trust the local service's
certificate per process with `SSL_CERT_FILE=./local/cert.pem`; never disable
TLS verification. This opt-in derives `/registry/local/archives/<id>/<commit>`
after approved-release selection. Default downloads still use GitHub codeload.
Local archives still require both verified digests,
manifest/hook identity, prerequisite confirmation and explicit executable trust.
Provenance records `archive_transport: local-loopback` and the actual `archive_url`;
a local archive does not establish that its repository is publicly available.
Never enable this mode implicitly or use it as fallback after a refusal.
This option applies to install/inspect only; registry updates do not inherit it.

A local registry can also describe real published GitHub releases. For those,
use `--registry` without `--local-archive-origin`; verify the GitHub archive digest.
If the registry uses a local certificate, provide a per-process CA bundle that
trusts both that certificate and the normal public roots used by GitHub.
