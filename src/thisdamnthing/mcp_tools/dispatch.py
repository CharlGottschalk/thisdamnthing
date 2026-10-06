"""Validated MCP dispatch, result budgets and refusal mapping."""
from pydantic import ValidationError
from .. import reminders
from ..workspace import WorkspaceError
from .catalog import WRITES, catalog_for
from .common import Refused, serialized
from .models import Coverage, Error, ProjectInspection, Result, WorkRead, WorkResults
from .projects import ProjectReferencesPage


def execute(root, name, arguments, profile='read-only'):
    catalog = catalog_for(profile)
    entry = catalog.get(name)
    if entry is None:
        return Result(ok=False, error=Error(code='profile_disabled',
                      message='Tool is unavailable in the selected catalog')).model_dump()
    input_type, output_type, operation, _ = entry
    try:
        args = input_type.model_validate(arguments)
        data, omissions = operation(root, args)
        if name == 'tdt_workspace_context':
            data.profile = profile
            data.tools = list(catalog)
        truncated = (isinstance(data, ProjectInspection)
                     and (data.inventory_truncated or any(doc.truncated for doc in data.documents)))
        if isinstance(data, WorkResults):
            truncated = data.scan_truncated or data.limit_reached or data.content_truncated
        elif isinstance(data, WorkRead):
            truncated = data.content_truncated
        elif isinstance(data, ProjectReferencesPage):
            truncated = data.scan_truncated
        result = Result[output_type](data=data, coverage=Coverage(truncated=truncated, omissions=omissions))
        value = result.model_dump()
        if len(serialized(value).encode('utf-8')) > args.budget_bytes:
            code = 'policy_read_required' if name == 'tdt_workspace_context' else 'result_too_large'
            message = 'Result exceeds budget; increase budget_bytes or request fewer results.'
            if name == 'tdt_workspace_context':
                message += ' Read complete policy with tdt_constitution_read before proceeding.'
            raise Refused(code, message)
        return value
    except Refused as exc:
        error = Error(code=exc.code, message=exc.message)
    except reminders.StaleRevision:
        error = Error(code='stale_revision', message='Reminder changed; reread before editing')
    except ValidationError:
        error = Error(code='invalid_input', message='Arguments do not match the tool input schema')
    except (WorkspaceError, OSError, ValueError, RecursionError):
        # Avoid echoing model input, filesystem content or tracebacks over the wire.
        error = Error(code='operation_refused',
                      message='Operation refused or workspace state unavailable; inspect before retrying',
                      retry='inspect_outcome' if name in WRITES else 'reread')
    return Result[output_type](ok=False, error=error).model_dump()
