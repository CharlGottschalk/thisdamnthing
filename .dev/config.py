"""Read local settings and check source-development tooling."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import os

REPO = Path(__file__).resolve().parent.parent
AGENTS = ("claude", "codex")


def load(path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(data, dict):
        raise ValueError("configuration must be an object")
    return data


def text(value):
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


def executable(value):
    if not text(value):
        return None
    path = Path(value)
    if path.is_absolute():
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    if path.name != value:
        return None
    return shutil.which(value)


def problems(data):
    errors = []
    if not text(data.get("name")):
        errors.append("name must be a nonempty string")
    if not isinstance(data.get("slug"), str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
        errors.append("slug must contain lowercase letters/digits separated by hyphens")
    if data.get("tasks") != "internal":
        errors.append("tasks must be internal")
    agents = data.get("agents")
    if (not isinstance(agents, list)
            or any(not isinstance(a, str) or a not in AGENTS for a in agents)
            or len(set(agents)) != len(agents)):
        errors.append("agents must be unique claude/codex identifiers, or []")
        agents = []
    toolchain = data.get("toolchain")
    if not isinstance(toolchain, dict):
        errors.append("toolchain must be an object")
        toolchain = {}
    for tool in ("git", "python", *agents):
        if not executable(toolchain.get(tool)):
            errors.append(f"toolchain.{tool} must resolve to an executable")
    python = executable(toolchain.get("python"))
    if python and Path(python).resolve() != Path(sys.executable).resolve():
        errors.append("run this helper with the selected toolchain.python interpreter")
    if sys.version_info < (3, 11):
        errors.append("Python 3.11 or newer is required")
    # Unused legacy fields are deliberately neither validated nor acted upon.
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPO / ".dev/developer.json")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("check", help="validate identity and selected executable paths")
    getter = sub.add_parser("get", help="read a dotted setting")
    getter.add_argument("setting")
    args = parser.parse_args()
    try:
        data = load(args.config)
        if args.action == "get":
            keys = args.setting.split(".")
            value = data
            for key in keys:
                if not isinstance(value, dict) or key not in value:
                    raise ValueError(f"unknown setting: {args.setting}")
                value = value[key]
            print(value if isinstance(value, str) else json.dumps(value, indent=2))
            return 0
        errors = problems(data)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        print("OK: developer identity and selected executable paths.")
        print("Model access is unverified. No agents are launched.")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Cannot read profile: {error}\nSay 'onboard me' to configure source development.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
