"""Bounded working-file discovery and read adapters."""
from .. import projects
from .common import Refused, workspace_key
from .models import WorkMatch, WorkRead, WorkResults


def work_search(root, args):
    value = projects.search_work(root, args.query, args.limit)
    items = [WorkMatch(path='work/' + item['relative'],
                       uri=f"tdt://{workspace_key(root)}/work/{item['relative']}",
                       content_truncated=item['content_truncated'], text_readable=item['text_readable'])
             for item in value['results']]
    return WorkResults(items=items, scan_truncated=value['scan_truncated'],
                       content_truncated=value['content_truncated'], limit_reached=value['limit_reached']), value['omissions']


def work_read(root, args):
    reference = args.reference
    prefix = f'tdt://{workspace_key(root)}/'
    if reference.startswith('tdt://'):
        if not reference.startswith(prefix):
            raise Refused('not_found', 'Reference belongs to another workspace')
        reference = reference[len(prefix):]
    value = projects.read_work(root, reference)
    return WorkRead(**value, uri=prefix + reference), (
        ['Working-file content is limited to a 32 KiB UTF-8 prefix'] if value['content_truncated'] else [])
