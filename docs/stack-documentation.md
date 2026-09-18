# Maintaining the stack documentation catalog

`src/dryft/stack_docs.py` builds `.dryft/stack-docs.md` from installed stack records.
Declared documents stay in their bundles. `.dryft/state/stack-docs.json` stores
the catalog's ownership digest; avoid adding a second document registry.

## Declare and discover guides

List each guide in the manifest's optional `docs` array under the
[stack contract](../src/dryft/resources/harness/contracts/stack.md). Only declared
files appear in the catalog. Documentation does not become approved brain knowledge.

```sh
dryft stack docs
dryft stack docs example-stack
```

The commands return local paths grouped by stack ID and version without opening
a browser or making network requests. Include a clear empty state and identify
installed stacks with no declared docs.

## Keep the view transactional

Install, update and remove operations must include the rendered catalog and its
digest in the same transaction as installed records. Reinitialization uses the
workspace lock and ownership preflight before rebuilding the view.

Escape local Markdown links correctly for spaces and Unicode. Validate declared
paths and reject managed symlinks. Keep skill and stack-ID naming rules separate
from document filename rules.

## Repair without losing edits

```sh
dryft stack docs --rebuild
dryft doctor
```

An edited or unowned catalog blocks mutation. Preserve useful edits in a separate
notes location, then rebuild the derived file. Missing declared bundle documents
need their original content restored; catalog rebuilding cannot recreate them.
Doctor compares the complete expected view to detect missing, stale or broken
links as well as ownership conflicts.

## Verify changes

Use bundles with no docs, several guides and filenames containing spaces or
Unicode. Check install, version update, removal and rollback. Exercise an edited
catalog, missing guide and escaping symlink, and confirm refusal preserves bytes.
Check that catalog commands remain local and work with zero stacks.
