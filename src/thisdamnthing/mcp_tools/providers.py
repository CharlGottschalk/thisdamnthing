"""Installed stack discovery and explicit search-provider indexing adapters."""
import json
from pathlib import Path
from pydantic import Field, ValidationError
from .. import brain, capabilities, skills, stacks
from .common import Refused, bounded_text, inventory_page, serialized
from .models import Model, ReadInput, ProviderPage, ProviderSummary, StackPage, StackSummary
from .maintenance import BinaryContent


class StackValidateInput(ReadInput):
    source: str = Field(min_length=1, max_length=4096)
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)


class StackValidated(Model):
    manifest: dict
    files: dict[str, str | BinaryContent]
    origin: dict
    requires_executable_trust: bool


def stack_validate(root, args):
    # External reads require an explicit absolute directory, never an implicit
    # process working directory or a downloaded/selected replacement source.
    if not Path(args.source).is_absolute():
        raise Refused('invalid_input', 'Select an absolute local stack directory')
    manifest, files, origin = stacks.validate(args.source, bounded=True)
    return StackValidated(manifest=manifest, files=files, origin=origin,
                          requires_executable_trust=bool(manifest['hooks'] or
                                                         manifest.get('capabilities'))), []


class StackInstallationPreview(Model):
    id: str
    origin: dict
    requires_executable_trust: bool
    before: dict[str, str | BinaryContent | None]
    after: dict[str, str | BinaryContent | None]


def stack_install_preview(root, args):
    if not Path(args.source).is_absolute():
        raise Refused('invalid_input', 'Select an absolute local stack directory')
    bounded_text(root, '.tdt/config.json', 1048576)  # Lock initialization reads config.
    with brain.locked(root, shared=True):
        return StackInstallationPreview(**stacks.installation_preview(root, args.source)), []


class StackReadInput(ReadInput):
    id: str = Field(min_length=1, max_length=81)
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)


class StackRead(Model):
    id: str
    revision: str
    record: dict


def stack_read(root, args):
    if not (stacks.ID.fullmatch(args.id) or stacks.LEGACY_ID.fullmatch(args.id)):
        raise Refused('invalid_input', 'Invalid stack ID')
    with brain.locked(root, shared=True):
        entry = next((entry for entry in installed_stacks(root) if entry['id'] == args.id), None)
        if entry is None:
            raise Refused('not_found', 'Stack is not installed')
        # Preserve the complete recorded entry, including legacy/extension metadata.
        # This digest is a read revision, never a lifecycle approval token.
        revision = brain.digest(json.dumps(entry, ensure_ascii=False, sort_keys=True,
                                          separators=(',', ':')))
        return StackRead(id=args.id, revision=revision, record=entry), []



class StackVerified(Model):
    id: str
    record_revision: str
    verified_files: int


def stack_verify(root, args):
    with brain.locked(root, shared=True):
        record, _ = stack_read(root, args)
        stacks.check_owned(root, record.record, bounded=True)
        return StackVerified(id=args.id, record_revision=record.revision,
                             verified_files=len(record.record['files'])), []


class StackRemovalPreview(Model):
    id: str
    proposal_sha256: str
    before: dict[str, str | BinaryContent | None]
    after: dict[str, str | BinaryContent | None]


def stack_remove_preview(root, args):
    with brain.locked(root, shared=True):
        stack_read(root, args)  # Exact ID and bounded registry validation.
        _, preview = stacks.removal_preview(root, args.id)
        return StackRemovalPreview(**preview), []


class StackRemovalApplyInput(ReadInput):
    id: str = Field(min_length=1, max_length=81)
    expected_sha256: str = Field(pattern='^[a-f0-9]{64}$')
    user_instruction: str = Field(min_length=1, max_length=300)


class StackRemoved(Model):
    id: str
    proposal_sha256: str


def stack_remove_apply(root, args):
    skills.text_checked(args.user_instruction, 'user instruction reference', 300)
    if not (stacks.ID.fullmatch(args.id) or stacks.LEGACY_ID.fullmatch(args.id)):
        raise Refused('invalid_input', 'Invalid stack ID')
    stacks.remove(root, args.id, expected_sha256=args.expected_sha256)
    # No retained outcome: absence after a lost response is not proof of success.
    return StackRemoved(id=args.id, proposal_sha256=args.expected_sha256), []


def installed_stacks(root):
    skills.ready(root)
    entries = stacks.validate_registry(json.loads(bounded_text(root, stacks.REGISTRY, 1048576)))
    if len(entries) > 2000:
        raise Refused('operation_refused', 'Stack catalog exceeds 2000 entries')
    for entry in entries:
        if not isinstance(entry.get('version'), str) or not stacks.VERSION.fullmatch(entry['version']):
            raise Refused('operation_refused', 'Invalid installed stack version')
    return sorted(entries, key=lambda entry: entry['id'])


def stack_list(root, args):
    items = [StackSummary(id=e['id'], version=e['version'], origin=e['origin'])
             for e in installed_stacks(root)]
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    page, cursor = inventory_page(root, args, 'stacks', 'all', revision, items)
    return StackPage(items=page, next_cursor=cursor, inventory_revision=revision), []


def search_providers(root, args):
    entries = installed_stacks(root)
    for entry in entries:
        if entry['manifest'].get('capabilities') and 'compatibility' not in entry['manifest']:
            raise Refused('operation_refused', 'Invalid installed provider metadata')
    try:
        items = [ProviderSummary(**row) for row in capabilities.discover(root, entries=entries)]
    except ValidationError:
        raise Refused('operation_refused', 'Invalid installed provider metadata') from None
    revision = brain.digest(serialized([item.model_dump() for item in items]))
    page, cursor = inventory_page(root, args, 'providers', 'all', revision, items)
    return ProviderPage(items=page, next_cursor=cursor, inventory_revision=revision), []


class ProviderIndexInput(ReadInput):
    provider: str = Field(pattern=r"^[a-z][a-z0-9.-]{0,79}$")
    rebuild: bool = False
    user_instruction: str = Field(min_length=1, max_length=500)


class ProviderIndexed(Model):
    provider: str
    indexed: int
    rebuild: bool


def provider_index(root, args):
    if not args.user_instruction.strip():
        raise Refused('invalid_input', 'An actual user instruction is required')
    # One selected provider keeps the receipt below the minimum result budget
    # and avoids a partially completed batch across provider transactions.
    indexed = capabilities.index(root, [args.provider], rebuild=args.rebuild)
    return ProviderIndexed(provider=args.provider, indexed=indexed[args.provider],
                           rebuild=args.rebuild), []
