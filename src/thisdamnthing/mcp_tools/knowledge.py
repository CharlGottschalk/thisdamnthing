"""Approved knowledge, candidate review and scratchpad adapters."""
import hashlib
from .. import brain, notes
from ..workspace import WorkspaceError
from .common import Refused, check_registry, inventory_page, serialized, workspace_key
from .models import (
    CandidateReviewed,
    CandidateStatus,
    Evidence,
    NoteSaveInput,
    ProviderSearchInput,
    RelatedNote,
    RelatedPage,
    SavedNote,
    SearchResults,
    StoredNote,
    StoredPage,
    StoredSummary,
)
from .providers import installed_stacks


def evidence(root, note):
    path, title, content = note
    # This revision identifies exactly the returned evidence, including sources.
    revision = brain.digest(serialized([path, title, content]))
    return Evidence(path=path, uri=f'tdt://{workspace_key(root)}/{path}',
                    revision=revision, title=title, content=content)


def search(root, args):
    check_registry(root)
    omissions = []
    providers = args.providers if isinstance(args, ProviderSearchInput) else ()
    if providers:
        installed_stacks(root)
    hits = brain.search(root, args.query, args.limit, args.depth, providers=providers, omissions=omissions)
    return SearchResults(items=[evidence(root, hit) for hit in hits],
                         limit=args.limit, depth=args.depth,
                         limit_reached=len(hits) == args.limit), omissions


def note_read(root, args):
    check_registry(root)
    omissions = []
    notes = brain.eligible_notes(root, omissions=omissions)
    # References must resolve through current eligibility, never arbitrary paths.
    for note in notes.values():
        item = evidence(root, note)
        if args.reference in (item.path, item.uri):
            return item, omissions
    raise Refused('not_found', 'No eligible approved note matches this workspace reference')


def stored_inventory(root, category):
    items, omissions = [], []
    revision = hashlib.sha256()
    for path in brain.note_files(root, (category,)):
        try:
            meta, _, markdown = brain.read_note(root, path, include_text=True)
            if category == 'notes':
                if meta['status'] != 'scratchpad':
                    raise brain.NoteError('Expected scratchpad status')
                try:
                    note_tags = notes.tags(meta.get('tags'))
                except WorkspaceError as exc:
                    raise brain.NoteError('Invalid scratchpad tags') from exc
            else:
                if meta['status'] not in ('pending', 'rejected'):
                    raise brain.NoteError('Expected candidate status')
                note_tags = []
        except (brain.NoteError, ValueError):
            omissions.append(path)
            revision.update(serialized([path, 'omitted']).encode())
            continue
        item = StoredSummary(id=meta['id'], path=path,
            uri=f'tdt://{workspace_key(root)}/{path}', revision=brain.digest(markdown),
            status=meta['status'], title=meta['title'], tags=note_tags)
        revision.update(serialized(item.model_dump()).encode())
        items.append(item)
    return items, omissions, revision.hexdigest()


def stored_list(root, args, category):
    items, omissions, revision = stored_inventory(root, category)
    status = args.status if category == 'candidates' else 'scratchpad'
    selected = [item for item in items if status == 'all' or item.status == status]
    page, cursor = inventory_page(root, args, category, status, revision, selected)
    return StoredPage(items=page, next_cursor=cursor,
                      inventory_revision=revision), omissions


def stored_read(root, args, category):
    items, omissions, _ = stored_inventory(root, category)
    matches = [item for item in items if args.reference in (item.id, item.path, item.uri)]
    if not matches:
        raise Refused('not_found', 'No note matches this workspace reference and category')
    if len(matches) != 1:
        raise Refused('operation_refused', 'Duplicate note identity; use an exact path')
    item = matches[0]
    _, _, markdown = brain.read_note(root, item.path, include_text=True)
    if brain.digest(markdown) != item.revision:
        raise Refused('stale_revision', 'Note changed during read; reread the inventory')
    return StoredNote(**item.model_dump(), markdown=markdown), omissions


def candidate_list(root, args):
    return stored_list(root, args, 'candidates')


def candidate_read(root, args):
    return stored_read(root, args, 'candidates')


def candidate_review_status(root, args):
    # Read under the writer lock so a promotion cannot appear missing between stores.
    with brain.locked(root):
        candidate = brain.find_note(root, 'candidates', args.id)
        canonical = brain.find_note(root, 'knowledge', args.id)
        path = canonical or candidate
        if path is None:
            raise Refused('not_found', 'No candidate or promoted knowledge matches this ID')
        meta, _, markdown = brain.read_note(root, path, include_text=True)
        if meta['status'] not in ('pending', 'approved', 'rejected'):
            raise Refused('operation_refused', 'Unexpected review state')
        return CandidateStatus(id=args.id, status=meta['status'], path=path,
            revision=brain.digest(markdown), markdown=markdown,
            approval_destination=canonical or brain.canonical_path(root, meta),
            pending_cleanup=bool(canonical and candidate)), []


def candidate_review(root, args):
    action = args.decision.action
    edited = args.decision.summary.model_dump() if action == 'edit' else None
    brain.review(root, args.id, action, args.user_instruction, args.expected_sha256, edited)
    # Fixed receipt fits the minimum budget, with no fallible post-write read.
    return CandidateReviewed(id=args.id,
        status={'approve': 'approved', 'reject': 'rejected', 'edit': 'pending'}[action]), []


def scratchpad_list(root, args):
    return stored_list(root, args, 'notes')


def scratchpad_read(root, args):
    return stored_read(root, args, 'notes')


def scratchpad_search(root, args):
    query = brain.clean_text(args.query, 'query', 300).casefold()
    items, omissions, revision = stored_inventory(root, 'notes')
    selected = []
    for item in items:
        meta, body, markdown = brain.read_note(root, item.path, include_text=True)
        if brain.digest(markdown) != item.revision:
            raise Refused('stale_revision', 'Scratchpad changed during search; restart the query')
        if query in (meta['title'] + '\n' + body + '\n' + ' '.join(item.tags)).casefold():
            selected.append(item)
    page, cursor = inventory_page(root, args, 'note-search', query, revision, selected)
    return StoredPage(items=page, next_cursor=cursor, inventory_revision=revision), omissions


def scratchpad_related(root, args):
    items, omissions, revision = stored_inventory(root, 'notes')
    matches = [item for item in items if item.id == args.id]
    if not matches:
        raise Refused('not_found', 'Unknown scratchpad note ID')
    if len(matches) != 1:
        raise Refused('operation_refused', 'Duplicate scratchpad identity')
    tags = set(matches[0].tags)
    selected = [RelatedNote(**item.model_dump(), shared_tags=sorted(tags.intersection(item.tags)))
                for item in items if item.id != args.id and tags.intersection(item.tags)]
    selected.sort(key=lambda item: (-len(item.shared_tags), item.path))
    page, cursor = inventory_page(root, args, 'note-related', args.id, revision, selected)
    return RelatedPage(items=page, next_cursor=cursor, inventory_revision=revision), omissions


def explicit_save(root, args):
    scratchpad = isinstance(args, NoteSaveInput)
    result = notes.save(root, args.summary.model_dump(), args.user_instruction,
                        scratchpad=scratchpad)
    # Keep the receipt bounded even for an existing note with a long moved path.
    # Complete content and its current path are available through the ID readers.
    return SavedNote(id=result['id'], result=result['status'],
                     status='scratchpad' if scratchpad else 'approved'), []
