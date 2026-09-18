"""Create and inspect plain-file workspaces without replacing user files."""

import json
from importlib.resources import files
from pathlib import Path


class WorkspaceError(Exception):
    """An actionable workspace problem."""


DIRECTORIES = (
    "brain", "brain/projects", "brain/sessions", "brain/knowledge",
    "brain/candidates", ".dryft", ".dryft/contracts", ".dryft/skills",
    ".dryft/hooks", ".dryft/stacks", ".dryft/state", "docs",
)
TEMPLATES = {
    ".dryft/contracts/stack.md": "harness/contracts/stack.md",
    "docs/stacks.md": "docs/stacks.md",
    "brain/index.md": "workspace/index.md",
    "docs/README.md": "docs/README.md",
}
CONFIG = {"format_version": 1, "kind": "dryft-workspace", "adapters": {}}
STATE = {
    ".dryft/state/stacks.json": [],
    ".dryft/state/projects.json": [],
    ".dryft/state/owned-files.json": sorted([
        *TEMPLATES, ".dryft/config.json", ".dryft/state/stacks.json",
        ".dryft/state/projects.json", ".dryft/state/owned-files.json",
    ]),
}


def managed_path(root, relative):
    path = root
    for part in Path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise WorkspaceError(f"Refusing symlink in workspace-owned path: {path}")
    return path


def read_json(root, relative):
    path = managed_path(root, relative)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WorkspaceError(f"Cannot read {path}: {exc}") from exc


def read_config(root):
    config = read_json(root, ".dryft/config.json")
    if (not isinstance(config, dict)
            or config.get("kind") != "dryft-workspace"
            or type(config.get("format_version")) is not int
            or config["format_version"] != 1
            or not isinstance(config.get("adapters"), dict)):
        raise WorkspaceError(f"Unsupported or invalid workspace config in {root}")
    return config


def resolve_workspace(explicit=None):
    start = Path(explicit).expanduser().resolve() if explicit else Path.cwd().resolve()
    for root in ([start] if explicit else [start, *start.parents]):
        if (root / ".dryft").exists() or (root / ".dryft").is_symlink():
            read_config(root)
            return root
    raise WorkspaceError("No Dryft workspace found. Run dryft init <directory> "
                         "or pass --workspace <path>.")


def resource_text(relative):
    return files("dryft").joinpath("resources", *relative.split("/")).read_text(
        encoding="utf-8")


def initialize(directory, agent=None):
    from .bootstrap import plan_bootstrap
    from .ui_resources import plan as ui_plan
    from . import stack_docs, stacks

    if agent not in (None, "claude", "codex", "both", "none"):
        raise WorkspaceError("Unknown agent selection")
    root = Path(directory).expanduser().resolve()
    for parent in [root, *root.parents]:
        if ((parent / ".dev/CONSTITUTION.md").is_file()
                and (parent / "docs/mvp.md").is_file()):
            raise WorkspaceError("This is the Dryft source repository. Choose a "
                                 "workspace directory outside it.")
        if parent != root and (parent / ".dryft").exists():
            raise WorkspaceError(f"Cannot nest a workspace inside {parent}")
    if root.exists() and not root.is_dir():
        raise WorkspaceError(f"Destination is not a directory: {root}")
    config_path = managed_path(root, ".dryft/config.json")
    if config_path.exists():
        config = read_config(root)
        # Reinitialization preserves edits and state; the derived catalog is rebuildable.
        for relative in [*DIRECTORIES, *TEMPLATES, *STATE]:
            managed_path(root, relative)
        from .brain import locked
        with locked(root):
            catalog = stack_docs.plan(root, stacks.available(root))
            pending = ui_plan(root)
            pending.update(plan_bootstrap(root, agent, config,
                                     read_json(root, ".dryft/state/owned-files.json")))
            from .agents import plan_skills
            pending.update(plan_skills(root, json.loads(pending[".dryft/config.json"])["enabled_agents"]))
            pending.update(catalog)
            stacks.transaction(root, pending)
            stacks.prune(root, [p for p, content in pending.items() if content is None])
        return root, False

    # Reserve the managed files and harness before making any changes. Other
    # documents and provider configuration can coexist with the workspace.
    if (root / ".dryft").exists():
        raise WorkspaceError(f"Conflicting harness at {root / '.dryft'}; "
                             "no valid workspace config. Choose another directory.")
    for relative in DIRECTORIES:
        path = managed_path(root, relative)
        if path.exists() and not path.is_dir():
            raise WorkspaceError(f"Expected a directory; existing file preserved: {path}")
    for relative in [*TEMPLATES, *STATE, ".dryft/config.json"]:
        path = managed_path(root, relative)
        if path.exists():
            raise WorkspaceError(f"Initialization conflict; existing path preserved: {path}")
    content = {target: resource_text(source) for target, source in TEMPLATES.items()}
    content.update({target: json.dumps(value, indent=2) + "\n"
                    for target, value in STATE.items()})
    # The config marks completed initialization and is deliberately written last.
    content[".dryft/config.json"] = json.dumps(CONFIG, indent=2) + "\n"
    if agent is None:
        from .agents import detected
        found = detected()
        agent = "both" if len(found) == 2 else (found[0] if found else "none")
    content.update(plan_bootstrap(root, agent, CONFIG,
                                  STATE[".dryft/state/owned-files.json"]))
    content.update(ui_plan(root))
    content.update(stack_docs.plan(root, []))
    # Keep the completion marker last, including when bootstrap adds files.
    config_content = content.pop(".dryft/config.json")
    content[".dryft/config.json"] = config_content
    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
    for relative, text in content.items():
        path = managed_path(root, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Provider settings/instructions were preflighted as merge targets.
        mode = "w" if relative in ("README.md", "AGENTS.md", "CLAUDE.md",
                                   ".codex/hooks.json", ".claude/settings.json") else "x"
        with path.open(mode, encoding="utf-8") as stream:
            stream.write(text)
    return root, True


def diagnose(root):
    """Return display lines and whether the core workspace is healthy."""
    lines = [f"Workspace: {root}"]
    healthy = True
    for relative in [*DIRECTORIES, *TEMPLATES, *STATE]:
        try:
            path = managed_path(root, relative)
            valid = path.is_dir() if relative in DIRECTORIES else path.is_file()
            if not valid:
                raise WorkspaceError(f"Missing or wrong path type: {relative}")
        except WorkspaceError as exc:
            lines.append(f"ERROR: {exc}")
            healthy = False
    for relative in TEMPLATES.values():
        try:
            resource_text(relative)
        except (OSError, ValueError) as exc:
            lines.append(f"ERROR: Missing package resource {relative}: {exc}")
            healthy = False
    for relative in STATE:
        try:
            value = read_json(root, relative)
            if not isinstance(value, list):
                raise WorkspaceError(f"Expected a JSON list in {relative}")
            if relative.endswith("stacks.json"):
                from .stacks import available, file_sha
                entries = available(root)
                from .stack_docs import diagnose as diagnose_docs
                diagnose_docs(root, entries)
                for entry in entries:
                    for relative, expected in entry["files"].items():
                        path = managed_path(root, relative)
                        if not path.is_file() or file_sha(path) != expected:
                            raise WorkspaceError(f"Stack file changed or missing: {relative}")
                lines.append(f"Installed stacks: {len(entries)}")
            elif relative.endswith("projects.json"):
                from .projects import registry, status
                entries = registry(root)
                lines.append(f"Registered projects: {len(entries)}")
                for entry in entries:
                    if status(entry) != "available":
                        lines.append(f"WARNING: project {entry['id']} missing or moved: {entry['path']}")
        except WorkspaceError as exc:
            lines.append(f"ERROR: {exc}")
            healthy = False
    from .ui_resources import plan as ui_plan
    try:
        pending = ui_plan(root)
        if len(pending) > 1 or not managed_path(root, ".dryft/state/ui-resources.json").exists():
            raise WorkspaceError("Core DUI resources need upgrade: rerun dryft init on this workspace")
        lines.append("Core DUI: resources installed")
    except WorkspaceError as exc:
        lines.append(f"ERROR: {exc}")
        healthy = False
    config = read_config(root)
    from .bootstrap import diagnose_adapters
    adapter_lines, adapters_healthy = diagnose_adapters(root, config)
    lines.extend(adapter_lines)
    lines.append("Core workspace: OK" if healthy else "Core workspace: needs attention")
    return lines, healthy and adapters_healthy
