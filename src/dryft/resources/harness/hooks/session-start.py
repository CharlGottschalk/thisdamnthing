"""Thin installed entry point; shared behavior lives in the Dryft package."""
from pathlib import Path
from dryft.hosts import session_start

if __name__ == "__main__":
    raise SystemExit(session_start(Path(__file__).resolve().parents[2]))
