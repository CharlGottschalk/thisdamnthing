# Implementing stack search capabilities

Contract v2 adds hashed assets, compatibility declarations and the `brain.search`
interface to the ordinary stack lifecycle. Workflow-only v1 stacks keep their
existing restrictions and digest format. The
[stack contract](../src/thisdamnthing/resources/harness/contracts/stack.md) defines the
manifest and provider protocol; `src/thisdamnthing/capabilities.py` implements the host side.

## Choose a provider explicitly

```sh
tdt brain providers
tdt brain index --provider PROVIDER_ID
tdt brain index --provider PROVIDER_ID --rebuild
tdt brain search "query" --provider PROVIDER_ID
```

Repeat `--provider` to combine providers. Selection applies to the invocation;
core literal search remains available without stacks. Discovery and installation
must not execute provider code.

The SQLite stack uses FTS5 for weighted title/body ranking and incremental index
reconciliation. The semantic stack bundles a local embedding model and runtime,
using a separate cache without requiring SQLite. Their source and binary assets
belong in separate stack repositories, outside the core wheel.

## Declare a self-contained capability

List selected assets with their size and SHA256, executable entry point, interface
version and platform/Python compatibility. Bundle runtime dependencies and required
licenses for an offline provider. Reject unsupported environments rather than
silently downloading software or installing dependencies.

Executable approval covers the exact selected snapshot. Stream integrity checks
for large assets. Keep immutable bundle files separate from disposable owned
indexes, and invalidate caches when provider/model identity changes.

## Validate results against current knowledge

Core supplies eligible approved canonical notes and authorized project identities.
Providers return IDs and content hashes. Recheck eligibility and current Markdown
before returning content and references to the caller; a stale index must not
resurrect deleted, edited or unapproved knowledge.

Combined retrieval uses reciprocal ranks with literal ranking and exact-title/ID
preference, followed by bounded outgoing links. Scores rank candidates; agents
must still inspect the evidence, cite it and disclose gaps or conflicts.

## Bound subprocess execution

Use JSON pipes, separate index/query budgets, output bounds and process-group
cleanup. Run against isolated working copies of cache files and promote only a
successful result. Malformed output, unknown IDs, stale hashes, timeout or nonzero
exit must produce explicit errors while preserving the durable cache.

Trusted providers run with local process permissions. Subprocess separation is
failure isolation, not an OS or network sandbox. Large binary assets also affect
installation memory because transaction snapshots encode binary content in the
journal; measure installation separately from query execution.

## Verify a provider

Build a harmless corpus with literal matches, paraphrases, absent evidence,
conflicting notes, linked notes and evidence near the end of a long note. Compare
core, individual-provider and combined results, then inspect the actual cited
passages. Do not judge correctness from ranking alone.

Change or delete notes, revoke eligibility and change model identity. Confirm stale
entries are excluded and rebuild guidance is actionable. Probe malformed output,
size limits, timeouts, altered assets and incompatible environments. Interrupt an
index operation and verify the previous cache survives.

For an offline claim, run install, index and query inside a verified network-disabled
environment using the packaged artifact. Record startup latency, peak memory,
artifact size and index size in private verification records. Exercise ordinary
update/removal and confirm brain files are unchanged.
