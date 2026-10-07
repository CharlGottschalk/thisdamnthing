"""Explicit network discovery; registry metadata never grants executable trust."""
import json
from typing import Literal
from pydantic import Field
from .. import brain, marketplace
from .common import Refused, inventory_page, serialized
from .models import Model, ReadInput


class MarketplaceInput(ReadInput):
    registry_url: str = Field(default=marketplace.DEFAULT_REGISTRY, min_length=1, max_length=2048)
    budget_bytes: int = Field(default=32768, ge=1024, le=1048576)


class MarketplaceSearchInput(MarketplaceInput):
    query: str = Field(default='', max_length=500)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    tag: str | None = Field(default=None, min_length=1, max_length=64)
    author: str | None = Field(default=None, min_length=1, max_length=80)
    agent: Literal['claude', 'codex'] | None = None
    browse: Literal['new', 'featured', 'popular'] = 'new'
    limit: int = Field(default=20, ge=1, le=50)
    cursor: str | None = Field(default=None, max_length=512)


class MarketplaceReadInput(MarketplaceInput):
    id: str = Field(pattern=r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$', max_length=80)


class MarketplaceSummary(Model):
    id: str
    name: str
    summary: str
    extension_type: str
    author: dict
    categories: list[str]
    tags: list[str]
    listing_url: str
    latest_version: str | None
    status: dict
    github_stars: int | None
    github_stars_fetched_at: str | None


class MarketplacePage(Model):
    registry_url: str
    generated_at: str
    feed_revision: str
    total: int
    items: list[MarketplaceSummary]
    next_cursor: str | None


class MarketplaceRead(Model):
    registry_url: str
    generated_at: str
    feed_revision: str
    listing: dict


def read_feed(args):
    # Shared CLI transport validates HTTPS, same-origin redirects, size/time,
    # schema and semantic constraints. No persistent cache or workspace reads.
    data = marketplace.load(args.registry_url)
    revision = brain.digest(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                      separators=(',', ':')))
    return data, revision


def marketplace_search(root, args):
    data, revision = read_feed(args)
    filters = {key: getattr(args, key) for key in
               ('query', 'category', 'tag', 'author', 'agent', 'browse')}
    selected = marketplace.search(data, **filters)
    items = [MarketplaceSummary(**{key: item[key] for key in MarketplaceSummary.model_fields})
             for item in selected]
    selection = serialized([args.registry_url, filters])
    page, cursor = inventory_page(root, args, 'marketplace', selection, revision, items)
    return MarketplacePage(registry_url=args.registry_url, generated_at=data['generated_at'],
                           feed_revision=revision, total=len(items), items=page,
                           next_cursor=cursor), []


def marketplace_read(root, args):
    data, revision = read_feed(args)
    listing = next((item for item in data['stacks'] if item['id'] == args.id), None)
    if listing is None:
        raise Refused('not_found', 'Unknown marketplace stack ID')
    # Inspection preserves withdrawn tombstones and all historical releases;
    # selection for installation remains the separate CLI validation path.
    return MarketplaceRead(registry_url=args.registry_url, generated_at=data['generated_at'],
                           feed_revision=revision, listing=listing), []
