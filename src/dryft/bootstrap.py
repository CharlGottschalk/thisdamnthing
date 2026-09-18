"""Preflight and merge owned adapter entries without changing host permissions."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shlex
import sys

from .workspace import WorkspaceError, managed_path, read_json, resource_text

MANIFEST = ".dryft/state/bootstrap.json"
PROVIDERS = {"claude": ("CLAUDE.md", ".claude/skills", ".claude/settings.json"),
             "codex": ("AGENTS.md", ".agents/skills", ".codex/hooks.json")}
SKILLS = ("dryft-constitution", "dryft-workspace", "dryft-review-brain", "dryft-search", "dryft-add-project", "dryft-ui", "dryft-install-stack", "dryft-find-skills", "dryft-update-stack", "dryft-remove-stack")
LEGACY_SKILLS = {name.replace('dryft-', 'dryft.', 1): name for name in SKILLS}
LEGACY_SKILLS.update({'dryft.ask-brain': 'dryft-search', 'dryft-ask-brain': 'dryft-search'})
# Original core-only templates had no bootstrap ownership manifest. Adopt only
# these exact shipped bytes (or today's bytes), never arbitrary user edits.
LEGACY_STACK_DOCS = {
    "docs/README.md": "1a61c9f1b17d09bd94ceeb794b7c69737096bfd12a86523e8b7e93b549fea759",
    '.dryft/contracts/stack.md': '9bceaa545780b68c06aadfe4c32393e45f2a83e8d19428abf7162c9859892d6d',
    'docs/stacks.md': 'aa6771c1535a4ebf6e227226e7b4b3933b587272a4d44726ab709b8e82840218',
}
RESOURCES = {
    "docs/constitution.md": "docs/constitution.md",
    ".dryft/hooks/constitution.py": "harness/hooks/constitution.py",
    ".dryft/skills/dryft-constitution/SKILL.md": "harness/skills/dryft-constitution/SKILL.md",
    **{f"docs/{name}.md": f"docs/{name}.md" for name in
       ("README", "getting-started", "troubleshooting", "authoring", "commands", "workspace-care", "core-skills")},
    ".dryft/contracts/stack.md": "harness/contracts/stack.md",
    "docs/stacks.md": "docs/stacks.md",
    **{f".dryft/skills/{name}/SKILL.md": f"harness/skills/{name}/SKILL.md"
       for name in ("dryft-search", "dryft-add-project", "dryft-install-stack", "dryft-update-stack", "dryft-remove-stack")},
    ".dryft/skills/dryft-find-skills/SKILL.md": "harness/skills/dryft-find-skills/SKILL.md",
    "docs/skills.md": "docs/skills.md",
    "docs/projects.md": "docs/projects.md",
    ".dryft/hooks/capture.py": "harness/hooks/capture.py",
    ".dryft/skills/dryft-review-brain/SKILL.md": "harness/skills/dryft-review-brain/SKILL.md",
    "docs/brain.md": "docs/brain.md",
    ".dryft/context.md": "harness/context.md",
    ".dryft/skills/dryft-workspace/SKILL.md": "harness/skills/dryft-workspace/SKILL.md",
    ".dryft/hooks/session-start.py": "harness/hooks/session-start.py",
    ".dryft/contracts/capture-event.md": "harness/contracts/capture-event.md",
    "docs/agent-bootstrap.md": "docs/agent-bootstrap.md",
}
BEGIN, END = "<!-- dryft:begin -->", "<!-- dryft:end -->"
BLOCK = (BEGIN + "\nRead .dryft/context.md at session start. The canonical Dryft\n"
         "skills and hooks live under .dryft/. Before each user request, run\n"
         "`dryft constitution show` and follow the current workspace policy. Report\n"
         "load failures before affected actions. This is a guidance-only fallback\n"
         "when request hooks are unavailable. See docs/constitution.md and\n"
         "docs/agent-bootstrap.md for host\n"
         "invocation and trust requirements. This workspace starts with zero stacks.\n"
         "Enable another host with `dryft agent enable claude` or `dryft agent enable codex`.\n"
         + END)


def parse_settings(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise WorkspaceError(f"Duplicate provider JSON key: {key}")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def encode(value):
    return json.dumps(value, indent=2) + "\n"


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def existing_text(root, relative):
    path = managed_path(root, relative)
    for parent in path.parents:
        if parent == root.parent:
            break
        if parent.exists() and not parent.is_dir():
            raise WorkspaceError(f"Expected directory: {parent}")
    if not path.exists():
        return None
    if not path.is_file():
        raise WorkspaceError(f"Expected file: {relative}")
    return path.read_bytes().decode("utf-8")


def load_manifest(root):
    if not managed_path(root, MANIFEST).exists():
        return {"format_version": 1, "files": {}, "instructions": {}, "hooks": {}, "capture_hooks": {}, "policy_hooks": {}}
    data = read_json(root, MANIFEST)
    if (not isinstance(data, dict) or data.get("format_version") != 1
            or any(not isinstance(data.get(k), dict)
                   for k in ("files", "instructions", "hooks"))):
        raise WorkspaceError("Invalid bootstrap ownership record")
    data.setdefault("policy_hooks", {})
    if not isinstance(data["policy_hooks"], dict) or set(data["policy_hooks"]) - {p[2] for p in PROVIDERS.values()}:
        raise WorkspaceError("Invalid policy hook ownership record")
    data.setdefault("capture_hooks", {})
    if not isinstance(data["capture_hooks"], dict):
        raise WorkspaceError("Invalid capture hook ownership record")
    # Never use recorded paths to write arbitrary files.
    allowed_files = {*RESOURCES, *(f"{p[1]}/{skill}/SKILL.md"
                                   for p in PROVIDERS.values()
                                   for skill in SKILLS)}
    for old, new in LEGACY_SKILLS.items():
        allowed_files.update(path.replace('/' + new + '/', '/' + old + '/')
                             for path in tuple(allowed_files) if '/' + new + '/' in path)
    if (set(data["files"]) - allowed_files
            or set(data["instructions"]) - {"README.md", *(p[0] for p in PROVIDERS.values())}
            or set(data["hooks"]) - {p[2] for p in PROVIDERS.values()}
            or set(data["capture_hooks"]) - {p[2] for p in PROVIDERS.values()}):
        raise WorkspaceError("Unexpected paths in bootstrap ownership record")
    return data


def plan_bootstrap(root, agent, config, owned):
    """Return all changes only after every requested path and merge is checked."""
    from .agents import enabled
    selected = enabled(root, config) if managed_path(root, ".dryft/config.json").exists() else []
    requested = list(PROVIDERS) if agent == "both" else ([agent] if agent not in (None, "none") else [])
    selected = list(dict.fromkeys([*selected, *requested]))
    state = load_manifest(root)
    pending = {}
    generated = {target: resource_text(source) for target, source in RESOURCES.items()}
    config = deepcopy(config)
    config["enabled_agents"] = selected
    readme = existing_text(root, "README.md") or ""
    previous_readme = state["instructions"].get("README.md")
    guidance = BEGIN + "\n" + resource_text("workspace/README.md").rstrip() + "\n" + END
    if previous_readme is not None:
        if (not isinstance(previous_readme, str) or readme.count(BEGIN) != 1
                or readme.count(END) != 1 or previous_readme not in readme):
            raise WorkspaceError("Owned README block changed or missing")
        updated_readme = readme.replace(previous_readme, guidance, 1)
    else:
        if BEGIN in readme or END in readme:
            raise WorkspaceError("Unowned Dryft README marker")
        updated_readme = readme + ("\n\n" if readme else "") + guidance + "\n"
    if readme != updated_readme:
        pending["README.md"] = updated_readme
    state["instructions"]["README.md"] = guidance
    for host in selected:
        instruction, skills, settings = PROVIDERS[host]
        if host == "claude":
            legacy = managed_path(root, ".claude/commands/dryft-workspace.md")
            if legacy.exists():
                raise WorkspaceError("Claude command name conflict: .claude/commands/dryft-workspace.md")
        generated[f"{skills}/dryft-workspace/SKILL.md"] = (
            "---\nname: dryft-workspace\ndescription: Orient the user in a Dryft workspace "
            "and diagnose its core files and agent setup.\n---\n\n"
            "Read and follow .dryft/skills/dryft-workspace/SKILL.md from the\n"
            "workspace root (the ancestor containing .dryft/config.json).\n")
        if host == "claude" and managed_path(root, ".claude/commands/dryft-review-brain.md").exists():
            raise WorkspaceError("Claude command name conflict: dryft-review-brain")
        generated[f"{skills}/dryft-review-brain/SKILL.md"] = (
            "---\nname: dryft-review-brain\ndescription: Review pending knowledge candidates "
            "and apply explicit user approval, edits or rejection.\n---\n\n"
            "Read and follow .dryft/skills/dryft-review-brain/SKILL.md from the workspace root.\n")
        for name, description in (("dryft-update-stack", "Inspect and approve a newer installed stack version."), ("dryft-remove-stack", "Uninstall a selected stack while preserving user work."), ("dryft-constitution", "Define or update workspace permission rules in natural language."), ("dryft-find-skills", "Find reusable workflows in completed workspace sessions and propose skills for approval."), ("dryft-install-stack", "Discover, inspect and install optional workflow stacks."), ("dryft-ui", "Use DUI for local browser questions and custom interactive interviews."), ("dryft-search", "Answer using approved linked knowledge with references and honest gaps."),
                                  ("dryft-add-project", "Register an external project and offer bounded onboarding.")):
            if host == "claude" and managed_path(root, f".claude/commands/{name}.md").exists():
                raise WorkspaceError(f"Claude command name conflict: {name}")
            generated[f"{skills}/{name}/SKILL.md"] = (
                f"---\nname: {name}\ndescription: {description}\n---\n\n"
                f"Read and follow .dryft/skills/{name}/SKILL.md from the workspace root.\n")
        current = existing_text(root, instruction) or ""
        previous = state["instructions"].get(instruction)
        if previous is not None:
            if (not isinstance(previous, str) or current.count(BEGIN) != 1
                    or current.count(END) != 1 or previous not in current):
                raise WorkspaceError(f"Owned instruction block changed or missing: {instruction}")
            updated = current.replace(previous, BLOCK, 1)
        else:
            if BEGIN in current or END in current:
                raise WorkspaceError(f"Unowned Dryft instruction marker: {instruction}")
            updated = current + ("\n\n" if current else "") + BLOCK + "\n"
        if current != updated:
            pending[instruction] = updated
        state["instructions"][instruction] = BLOCK

        raw = existing_text(root, settings)
        data = parse_settings(raw) if raw is not None else {}
        if not isinstance(data, dict):
            raise WorkspaceError(f"Expected settings object: {settings}")
        hooks = data.setdefault("hooks", {})
        if not isinstance(hooks, dict):
            raise WorkspaceError(f"Expected hooks object: {settings}")
        for event, script, record_key in (("SessionStart", "session-start.py", "hooks"),
                                          ("Stop", "capture.py", "capture_hooks"),
                                          ("UserPromptSubmit", "constitution.py", "policy_hooks")):
            entries = hooks.setdefault(event, [])
            if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
                raise WorkspaceError(f"Expected {event} object list: {settings}")
            command = shlex.join([sys.executable, str(root / f".dryft/hooks/{script}"), host])
            entry = {"hooks": [{"type": "command", "command": command, "timeout": 10}]}
            if host == "codex" and event in ("UserPromptSubmit", "SessionStart"):
                entry["hooks"][0]["additionalContextLimit"] = 10000
            previous = state[record_key].get(settings)
            if previous is not None:
                if entries.count(previous) != 1:
                    raise WorkspaceError(f"Owned {event} hook changed, duplicated or missing: {settings}")
                index = entries.index(previous)
                others = entries[:index] + entries[index + 1:]
            else:
                index, others = len(entries), entries
            if any(".dryft/" in json.dumps(e) for e in others):
                raise WorkspaceError(f"Unowned Dryft hook conflict: {settings}")
            if previous is None:
                entries.append(entry)
            else:
                entries[index] = entry
            state[record_key][settings] = entry
        if raw is None or parse_settings(raw) != data:
            pending[settings] = encode(data)
        config["adapters"][host] = {"bootstrap_version": 1,
                                    "capture": "Stop continuation; runtime unverified"}

    # Rename only hash-verified files that this bootstrap already owns. Keep
    # unselected hosts discoverable too, without changing their settings/hooks.
    for relative, expected in list(state['files'].items()):
        replacement = relative
        for old, new in LEGACY_SKILLS.items():
            replacement = replacement.replace('/' + old + '/', '/' + new + '/')
        if replacement == relative:
            continue
        current = existing_text(root, relative)
        if current is None or digest(current) != expected:
            raise WorkspaceError(f'Owned legacy skill changed or missing: {relative}')
        for old, new in LEGACY_SKILLS.items():
            current = current.replace(old, new)
        generated.setdefault(replacement, current)
        pending[relative] = None
        del state['files'][relative]

    for relative, content in generated.items():
        if relative.startswith('.claude/skills/'):
            name = Path(relative).parent.name
            if managed_path(root, f'.claude/commands/{name}.md').exists():
                raise WorkspaceError(f'Claude command name conflict: {name}')
        current = existing_text(root, relative)
        previous = state["files"].get(relative)
        if previous is not None:
            if current is None or digest(current) != previous:
                raise WorkspaceError(f"Owned bootstrap file changed or missing: {relative}")
        elif current is not None and not (relative in LEGACY_STACK_DOCS
                and digest(current) in (digest(content), LEGACY_STACK_DOCS[relative])):
            raise WorkspaceError(f"Bootstrap name conflict; existing file preserved: {relative}")
        # Reserve skill directories as a whole to avoid hijacking existing skills.
        if relative.endswith("/SKILL.md") and previous is None:
            parent = managed_path(root, str(Path(relative).parent))
            if parent.exists():
                raise WorkspaceError(f"Bootstrap skill directory conflict: {parent}")
        if current != content:
            pending[relative] = content
        state["files"][relative] = digest(content)
    if not isinstance(owned, list) or any(not isinstance(v, str) for v in owned):
        raise WorkspaceError("Invalid owned-files list")
    pending[MANIFEST] = encode(state)
    pending[".dryft/state/owned-files.json"] = encode(sorted((set(owned) | {
        *state["files"], MANIFEST}) - {p for p, text in pending.items() if text is None}))
    pending[".dryft/config.json"] = encode(config)
    # Includes manifests and state; fail before the first write on all path conflicts.
    for relative in pending:
        existing_text(root, relative)
    return pending


def diagnose_adapters(root, config):
    lines, healthy = [], True
    state = {}
    try:
        state = load_manifest(root)
        for relative, expected in state["files"].items():
            current = existing_text(root, relative)
            if current is None or digest(current) != expected:
                raise WorkspaceError(f"Bootstrap file missing or changed: {relative}")
        for relative, block in state["instructions"].items():
            current = existing_text(root, relative) or ""
            if (not isinstance(block, str) or block not in current
                    or current.count(BEGIN) != 1 or current.count(END) != 1):
                raise WorkspaceError(f"Bootstrap instruction missing or changed: {relative}")
        recorded_hooks = [(relative, entry, "SessionStart", "session-start.py")
                          for relative, entry in state["hooks"].items()]
        recorded_hooks += [(relative, entry, "Stop", "capture.py")
                           for relative, entry in state["capture_hooks"].items()]
        recorded_hooks += [(relative, entry, "UserPromptSubmit", "constitution.py")
                           for relative, entry in state["policy_hooks"].items()]
        for relative, entry, event, script in recorded_hooks:
            raw = existing_text(root, relative)
            if raw is None:
                raise WorkspaceError(f"Missing hook configuration: {relative}")
            data = parse_settings(raw)
            hooks = data.get("hooks", {}) if isinstance(data, dict) else {}
            entries = hooks.get(event, []) if isinstance(hooks, dict) else []
            if not isinstance(entries, list) or entries.count(entry) != 1:
                raise WorkspaceError(f"{event} hook missing or changed: {relative}")
            try:
                handler = entry["hooks"][0]
                argv = shlex.split(handler["command"])
                if (len(argv) != 3 or not Path(argv[0]).is_file()
                        or argv[1] != str(root / f".dryft/hooks/{script}")):
                    raise ValueError("stale Python or workspace path")
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise WorkspaceError(f"Invalid startup command in {relative}; "
                                     "rerun init --agent for this host") from exc
            if data.get("disableAllHooks") is True:
                lines.append(f"WARNING: hooks disabled in {relative}")
                healthy = False
        from .agents import enabled, detected
        selected, installed = enabled(root, config), detected()
        for host, (instruction, skills, settings) in PROVIDERS.items():
            executable = "found on PATH" if host in installed else "not found on PATH"
            lines.append(f"{host.capitalize()} executable: {executable}")
            if host not in selected:
                lines.append(f"{host.capitalize()} integration: disabled; use dryft agent enable {host}")
                continue
            adapter = config["adapters"].get(host)
            if not isinstance(adapter, dict) or adapter.get("bootstrap_version") != 1:
                raise WorkspaceError(f"{host} ownership recognized but adapter needs refresh; run dryft agent enable {host}")
            if (instruction not in state["instructions"] or settings not in state["hooks"]
                    or settings not in state["capture_hooks"]
                    or settings not in state["policy_hooks"]
                    or f"{skills}/dryft-review-brain/SKILL.md" not in state["files"]
                    or f"{skills}/dryft-workspace/SKILL.md" not in state["files"]
                    or any(f"{skills}/{name}/SKILL.md" not in state["files"] for name in SKILLS)
                    or not set(RESOURCES).issubset(state["files"])):
                raise WorkspaceError(f"Incomplete {host} bootstrap ownership record")
            lines.append(f"{host.capitalize()} integration: enabled; files installed; runtime unverified")
            if host == "codex":
                lines.append("  Trust required: trusted project layer and review SessionStart, UserPromptSubmit and Stop hooks in /hooks.")
            else:
                lines.append("  Review project trust and /hooks; host or managed settings may disable hooks.")
    except (WorkspaceError, ValueError, OSError) as exc:
        lines.append(f"ERROR: {exc}")
        healthy = False
    lines.append("Automatic capture: Stop continuation installed; requires live host trust"
                 if state.get("capture_hooks") else "Automatic capture: no Stop hooks installed")
    from .constitution import load as load_policy
    try:
        policy = load_policy(root)
        lines.append("Workspace constitution: " + policy["sha256"] + "; guidance only, live request delivery unverified")
    except (WorkspaceError, ValueError, OSError) as exc:
        lines.append(f"ERROR: workspace constitution: {exc}")
        healthy = False
    from .brain import candidates
    try:
        pending = len(candidates(root))
        requests = managed_path(root, ".dryft/state/captures")
        incomplete = sum(read_json(root, str(p.relative_to(root))).get("status") == "requested"
                         for p in requests.glob("*.json"))
        lines.append(f"Brain: {pending} pending candidates; {incomplete} incomplete capture requests")
    except (WorkspaceError, ValueError, OSError) as exc:
        lines.append(f"ERROR: brain state: {exc}")
        healthy = False
    return lines, healthy
