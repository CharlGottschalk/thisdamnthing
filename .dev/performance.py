#!/usr/bin/env python3
"""Measure TDT-owned context surfaces in disposable workspace profiles.

This deliberately reports bytes, characters and words rather than pretending
they are host/model tokens. Real host token counters belong in the accompanying
acceptance record.
"""

import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from thisdamnthing.bootstrap import BEGIN, END, PROVIDERS, load_manifest  # noqa: E402
from thisdamnthing.constitution import LIMIT, POLICY, EXPECTED, context as policy_context  # noqa: E402
from thisdamnthing.workspace import initialize  # noqa: E402
from thisdamnthing import skills, stacks  # noqa: E402


def size(text):
    return {
        "bytes": len(text.encode("utf-8")),
        "characters": len(text),
        "words": len(text.split()),
    }


def owned_block(path):
    text = path.read_text(encoding="utf-8")
    start = text.index(BEGIN)
    finish = text.index(END, start) + len(END)
    return text[start:finish]


def hook(root, host, event, turn_id=None):
    script = "session-start.py" if event == "SessionStart" else "constitution.py"
    payload = {
        "hook_event_name": event,
        "session_id": f"performance-{host}",
        "cwd": str(root),
        "transcript_path": None,
        "turn_id": turn_id,
        "source": "performance-harness",
    }
    result = subprocess.run(
        [sys.executable, str(root / ".tdt/hooks" / script), host],
        input=json.dumps(payload), text=True, capture_output=True, check=False,
        env={"PYTHONPATH": str(REPO / "src")},
    )
    if result.returncode or result.stderr:
        raise RuntimeError(
            f"{host} {event} hook failed ({result.returncode}): {result.stderr.strip()}"
        )
    envelope = json.loads(result.stdout)
    output = envelope["hookSpecificOutput"]["additionalContext"]
    return {"surface": size(output), "text": output}


def bridge_metadata(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Skill bridge has no front matter: {path}")
    front = text.split("---\n", 2)[1]
    selected = []
    for line in front.splitlines():
        if line.startswith(("name:", "description:")):
            selected.append(line + "\n")
    return "".join(selected)


def model_visible(path):
    text = path.read_text(encoding="utf-8")
    front = text.split("---\n", 2)[1]
    if "disable-model-invocation: true" in front.splitlines():
        return False
    policy = path.parent / "agents/openai.yaml"
    # Generated TDT bridges use this exact owned policy, without a YAML dependency.
    return not (policy.is_file() and
                "  allow_implicit_invocation: false" in policy.read_text().splitlines())


def measure(root, host):
    instruction, skills_dir, _settings = PROVIDERS[host]
    bridges = sorted((root / skills_dir).glob("*/SKILL.md"))
    visible = [path for path in bridges if model_visible(path)]
    metadata = "".join(bridge_metadata(path) for path in visible)
    owners = {path: "core" for path in load_manifest(root)["files"]}
    for stack in stacks.available(root):
        owners.update({path: stack["id"] for path in stack["files"]})
    for record in skills.state(root)["skills"].values():
        owners.update({path: "user" for path in record})
    groups = {}
    for path in bridges:
        owner = owners.get(path.relative_to(root).as_posix(), "unmanaged")
        groups.setdefault(owner, []).append(path)
    attribution = {}
    for owner, paths in groups.items():
        discovered = [path for path in paths if model_visible(path)]
        attribution[owner] = {
            "installed_skill_bridge_count": len(paths),
            "visible_skill_count": len(discovered),
            "visible_skill_metadata": size("".join(bridge_metadata(p) for p in discovered)),
        }
    startup = hook(root, host, "SessionStart")
    request = hook(root, host, "UserPromptSubmit", turn_id="turn-1")
    second_request = hook(root, host, "UserPromptSubmit", turn_id="turn-2")
    policy = policy_context(root)
    request_prefix = policy + "\n\n"
    context = (root / ".tdt/context.md").read_text(encoding="utf-8")
    if startup["text"] != context:
        raise RuntimeError(f"{host} SessionStart context attribution failed")
    if not request["text"].startswith(request_prefix):
        raise RuntimeError(f"{host} UserPromptSubmit policy attribution failed")
    if not second_request["text"].startswith(request_prefix):
        raise RuntimeError(f"{host} second UserPromptSubmit policy attribution failed")
    return {
        "root_instruction": size(owned_block(root / instruction)),
        "installed_skill_bridge_count": len(bridges),
        "visible_skill_count": len(visible),
        "visible_skill_metadata": size(metadata),
        "skill_metadata_by_owner": attribution,
        "session_start": startup["surface"],
        "session_start_policy": size(""),
        "user_prompt_submit": request["surface"],
        "second_user_prompt_submit": second_request["surface"],
        "user_prompt_policy": size(policy),
        "user_prompt_capture_turn": size(request["text"][len(request_prefix):]),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Measure source-checkout TDT context in a disposable workspace."
    )
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument(
        "--stack", action="append", type=Path, default=[],
        help="Local non-executable stack to install in the disposable profile; repeatable.",
    )
    parser.add_argument(
        "--user-skills", type=int, default=0, choices=range(0, 21), metavar="0..20",
        help="Number of synthetic approved user skills in the disposable profile.",
    )
    parser.add_argument(
        "--policy-matrix", action="store_true",
        help="Also measure synthetic 1,000-byte and maximum-size policies.",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="tdt-performance-") as temporary:
        with redirect_stdout(io.StringIO()):
            root, _created = initialize(Path(temporary) / "workspace", "both")
        manifest = load_manifest(root)
        result = {
            "format_version": 2,
            "source": str(REPO),
            "workspace_profile": "core-only; no constitution; no stacks; no user skills",
            "empty_workspace": {
                "tdt_owned_bytes": 0,
                "visible_tdt_skill_count": 0,
            },
            "owned_file_count": len(manifest["files"]),
            "hosts": {host: measure(root, host) for host in PROVIDERS},
            "notes": [
                "Counts are exact UTF-8 bytes/characters/whitespace words, not model tokens.",
                "Request-hook measurement mutates only the disposable workspace.",
                "Host-reported token totals and native discovery behavior require fresh live sessions.",
                "Capture-turn context contains the absolute workspace path; its length affects request bytes.",
            ],
        }
        if args.stack or args.user_skills:
            result["capability_profiles"] = {}
            installed = []
            for directory in args.stack:
                data, _files, origin = stacks.validate(directory)
                if data["hooks"] or data.get("capabilities"):
                    parser.error("Performance profiles accept only stacks without executable hooks/capabilities")
                stacks.install(root, directory)
                installed.append({"id": data["id"], "version": data["version"],
                                  "content_sha256": origin["sha256"]})
            if installed:
                result["capability_profiles"]["stacks"] = {
                    "stacks": installed,
                    "approved_user_skill_count": 0,
                    "hosts": {host: measure(root, host) for host in PROVIDERS},
                }
            for number in range(1, args.user_skills + 1):
                proposal = skills.propose(root, {
                    "name": f"tdt-fixture-summary-{number:02d}",
                    "description": f"Summarize fictional planning notes for fixture {number:02d}; use when asked for its status report.",
                    "instructions": "Read only the notes supplied in the current request. Summarize decisions and open questions; do not invent facts or write files.",
                })
                skills.review(root, [proposal["id"]], "approve",
                              "Synthetic fixture approval inside disposable performance workspace")
            if args.user_skills:
                result["capability_profiles"]["with-user-skills"] = {
                    "stacks": installed,
                    "approved_user_skill_count": args.user_skills,
                    "hosts": {host: measure(root, host) for host in PROVIDERS},
                }
            # Policy profiles remain a core-only comparison, independent of the
            # optional capabilities selected above.
            with redirect_stdout(io.StringIO()):
                # Same basename length keeps the absolute-path capture envelope comparable.
                root, _created = initialize(Path(temporary) / "core-only", "both")
        if args.policy_matrix:
            result["policy_profiles"] = {}
            for policy_bytes in (1000, LIMIT):
                # Synthetic ASCII keeps the fixture exact and free of local policy.
                heading = "# Performance fixture policy\n\n"
                policy = heading + "x" * (policy_bytes - len(heading) - 1) + "\n"
                (root / POLICY).write_text(policy, encoding="utf-8")
                (root / EXPECTED).write_text("expected\n", encoding="utf-8")
                result["policy_profiles"][str(policy_bytes)] = {
                    "policy_markdown": size(policy),
                    "hosts": {host: measure(root, host) for host in PROVIDERS},
                }
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
