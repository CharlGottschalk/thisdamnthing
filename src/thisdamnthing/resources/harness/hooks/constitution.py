"""Workspace-local before-request adapter."""
from pathlib import Path
from thisdamnthing.constitution import request_hook

if __name__ == '__main__':
    raise SystemExit(request_hook(Path(__file__).resolve().parents[2]))
