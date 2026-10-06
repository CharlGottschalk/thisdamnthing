"""Installed stack and search-provider discovery adapters."""
import json
from pydantic import ValidationError
from .. import brain, capabilities, skills, stacks
from .common import Refused, bounded_text, inventory_page, serialized
from .models import ProviderPage, ProviderSummary, StackPage, StackSummary


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
