"""Thin installed Stop hook."""
from pathlib import Path
from dryft.capture import main

if __name__ == "__main__":
    raise SystemExit(main(Path(__file__).resolve().parents[2]))
