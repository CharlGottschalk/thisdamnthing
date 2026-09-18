"""The small public command-line interface."""

import argparse
import json
import sys

from . import __version__
from .workspace import WorkspaceError, diagnose, initialize, resolve_workspace


def main(argv=None):
    parser = argparse.ArgumentParser(prog="dryft", description="A local knowledge workspace.")
    parser.add_argument("--version", action="version", version=f"dryft {__version__}")
    parser.add_argument("--workspace", metavar="PATH", help="explicit workspace directory")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a workspace with zero stacks")
    init.add_argument("directory", nargs="?", default=".",
                      help="workspace destination (default: current directory; outside the source repository)")
    init.add_argument("--agent", choices=("claude", "codex", "both", "none"),
                      help="override initial PATH detection; none creates core only; existing hosts stay enabled")
    agent = commands.add_parser("agent", help="enable or disable a workspace host")
    agent_actions = agent.add_subparsers(dest="action", required=True)
    for action in ("enable", "disable"):
        agent_actions.add_parser(action).add_argument("host", choices=("claude", "codex"))
    doctor = commands.add_parser("doctor", help="check workspace paths, resources and adapters")
    doctor.add_argument("--workspace", metavar="PATH", default=argparse.SUPPRESS,
                        help="explicit workspace directory")
    policy = commands.add_parser("constitution", help="read or save reviewed workspace policy")
    policy_actions = policy.add_subparsers(dest="action", required=True)
    policy_actions.add_parser("show")
    policy_save = policy_actions.add_parser("save")
    policy_save.add_argument("--expected-sha256", required=True)
    policy_save.add_argument("--user-instruction", required=True)
    brain = commands.add_parser("brain", help="capture and review knowledge candidates")
    actions = brain.add_subparsers(dest="action", required=True)
    submit = actions.add_parser("capture", help="submit a summary for a host request, JSON on stdin")
    submit.add_argument("id")
    listing = actions.add_parser("candidates", help="show candidate proposals and review hashes")
    listing.add_argument("--status", choices=("pending", "approved", "rejected", "all"), default="pending")
    actions.add_parser("requests", help="list incomplete capture request ids for recovery")
    review = actions.add_parser("review", help="apply an explicitly instructed user review")
    review.add_argument("id")
    review.add_argument("--decision", choices=("approve", "reject", "edit"), required=True)
    review.add_argument("--user-instruction", required=True, help="actual user instruction or message reference")
    review.add_argument("--expected-sha256", required=True, help="hash from the displayed proposal")
    search = actions.add_parser("search", help="search approved knowledge only")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--depth", type=int, default=1)
    search.add_argument("--provider", action="append", default=[], help="explicit stack id; repeat to fuse rankings")
    providers = actions.add_parser("providers", help="discover providers without executing code")
    index = actions.add_parser("index", help="reconcile selected provider indexes")
    index.add_argument("--provider", action="append", required=True)
    index.add_argument("--rebuild", action="store_true")
    project = commands.add_parser("project", help="link external projects without modifying them")
    project_actions = project.add_subparsers(dest="action", required=True)
    project_add = project_actions.add_parser("add")
    project_add.add_argument("path")
    project_actions.add_parser("list")
    for action in ("inspect", "propose"):
        command = project_actions.add_parser(action)
        command.add_argument("id")
    stack = commands.add_parser("stack", help="validate and manage local workflow stacks")
    stack_actions = stack.add_subparsers(dest="action", required=True)
    for action in ("validate", "install"):
        command = stack_actions.add_parser(action)
        command.add_argument("directory")
        if action == "install":
            command.add_argument("--trust-executable", "--trust-hooks", dest="trust_hooks", metavar="SHA256")
            command.add_argument("--version", dest="stack_version")
            command.add_argument("--registry", default=None, metavar="HTTPS_URL")
            command.add_argument("--local-archive-origin", metavar="HTTPS_ORIGIN",
                help="explicit local test archive transport; literal-loopback HTTPS origin must match --registry")
            command.add_argument("--inspect", action="store_true", help="download and verify without installing")
            command.add_argument("--confirm-prerequisite", action="append", default=[], metavar="TYPE:REF")
    docs = stack_actions.add_parser("docs", help="list canonical installed docs or rebuild their catalog")
    docs.add_argument("id", nargs="?")
    docs.add_argument("--rebuild", action="store_true")
    stack_actions.add_parser("list")
    stack_actions.add_parser("recover")
    for action in ("remove", "uninstall"):
        stack_actions.add_parser(action).add_argument("id")
    update = stack_actions.add_parser("update", help="inspect and approve a newer stack version")
    update.add_argument("id")
    update.add_argument("--source", metavar="PATH")
    update.add_argument("--registry", metavar="HTTPS_URL")
    update.add_argument("--check", action="store_true")
    update.add_argument("--approve", metavar="SHA256")
    update.add_argument("--trust-executable", "--trust-hooks", dest="trust_hooks", metavar="SHA256")
    update.add_argument("--confirm-prerequisite", action="append", default=[])
    marketplace = commands.add_parser("marketplace", help="explicit marketplace discovery")
    market_actions = marketplace.add_subparsers(dest="action", required=True)
    market_search = market_actions.add_parser("search")
    market_search.add_argument("query", nargs="?", default="")
    market_search.add_argument("--registry", default=None, metavar="HTTPS_URL")
    for field in ("category", "tag", "author"):
        market_search.add_argument("--" + field)
    market_search.add_argument("--agent", choices=("claude", "codex"))
    market_search.add_argument("--browse", choices=("new", "featured", "popular"), default="new")
    from . import skills
    skills.add_parser(commands)
    from . import ui
    ui.add_parser(commands)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            if args.workspace:
                parser.error("init uses its directory argument; --workspace is for workspace commands")
            root, created = initialize(args.directory, args.agent)
            print(f"{'Initialized workspace' if created else 'Workspace initialized; existing content preserved'}: {root}")
            if created:
                print("Installed stacks: 0")
            else:
                print("Run dryft doctor to inspect its current state.")
            from .agents import enabled
            print("Enabled integrations: " + (", ".join(enabled(root)) or "none") + ". Run dryft doctor; review host trust before use.")
            return 0
        if args.command == "agent":
            from . import agents
            operation = agents.enable if args.action == "enable" else agents.disable
            print(operation(resolve_workspace(args.workspace), args.host))
            return 0
        if args.command == "constitution":
            from . import constitution
            root = resolve_workspace(args.workspace)
            if args.action == "show":
                result = constitution.load(root)
            else:
                result = constitution.save(root, sys.stdin.read(constitution.LIMIT + 1),
                    args.expected_sha256, args.user_instruction)
            print(json.dumps(result, indent=2))
            return 0
        if args.command == "marketplace":
            from . import marketplace
            data = marketplace.load(args.registry or marketplace.DEFAULT_REGISTRY)
            print(json.dumps(marketplace.search(data, args.query, category=args.category,
                tag=args.tag, author=args.author, agent=args.agent, browse=args.browse), indent=2))
            return 0
        if args.command == "stack" and args.action == "install":
            from pathlib import Path
            from . import marketplace, stacks
            # Existing directories remain local. Prefix ./ to disambiguate missing paths.
            if stacks.ID.fullmatch(args.directory) and not Path(args.directory).exists():
                root = None if args.inspect else resolve_workspace(args.workspace)
                result = marketplace.install(root, args.directory, version=args.stack_version,
                    registry_url=args.registry or marketplace.DEFAULT_REGISTRY,
                    trust=args.trust_hooks, inspect_only=args.inspect,
                    confirmed=args.confirm_prerequisite, local_origin=args.local_archive_origin)
                print(("Verified: " if args.inspect else "Installed: ") + result)
                return 0
            if args.registry or args.stack_version or args.confirm_prerequisite or args.local_archive_origin:
                raise WorkspaceError("Registry options require a catalog ID")
        if args.command == "stack" and args.action in ("validate", "install"):
            from . import stacks
            manifest, files, origin = stacks.validate(args.directory)
            print(json.dumps({"manifest": manifest, "origin": origin}, indent=2))
            for hook in manifest["hooks"]:
                print(f"Executable Python hook: {hook['event']} {hook['path']}\n{files[hook['path']]}")
            if args.action == "validate" or args.inspect:
                return 0
        root = resolve_workspace(args.workspace)
        if args.command == "ui":
            print(json.dumps(ui.cli(root, args), ensure_ascii=False))
            return 0
        if args.command == "stack":
            from . import stacks
            if args.action == "install":
                print("Installed: " + stacks.install(root, args.directory, args.trust_hooks))
            elif args.action == "update":
                from . import stack_updates
                print(stack_updates.update(root, args.id, source=args.source,
                    registry_url=args.registry, check=args.check, approve=args.approve,
                    trust=args.trust_hooks, confirmed=args.confirm_prerequisite))
            elif args.action in ("remove", "uninstall"):
                entry = next((e for e in stacks.available(root) if e['id'] == args.id), None)
                if entry:
                    print(json.dumps({"id": args.id, "removing_owned_files": sorted(entry['files']),
                        "retained": "Brain notes/candidates, user skills, linked projects and generated user artifacts"}, indent=2))
                print("Removed (brain preserved; restart hosts to clear loaded skills): " + stacks.remove(root, args.id))
            elif args.action == "docs":
                from . import stack_docs
                if args.rebuild:
                    print(stack_docs.rebuild(root))
                entries = stacks.available(root)
                if args.id:
                    entries = [e for e in entries if e['id'] == args.id]
                    if not entries:
                        raise WorkspaceError('Stack is not installed')
                groups = stack_docs.documents(root, entries)
                if not groups:
                    print('No stacks installed.')
                for stack_id, version, paths in groups:
                    print(f'{stack_id} {version}')
                    for path in paths:
                        print(root / '.dryft/stacks' / stack_id / path)
                    if not paths:
                        print('  No documentation declared.')
            elif args.action == "recover":
                from .brain import locked
                with locked(root):
                    print(stacks.recover(root))
            else:
                print(json.dumps(stacks.available(root), indent=2))
            return 0
        def input_json():
            raw = sys.stdin.read(16385)
            if len(raw) > 16384:
                raise ValueError("JSON input exceeds 16 KiB")
            return json.loads(raw)
        if args.command == "skill":
            print(json.dumps(skills.cli(root, args, input_json() if args.action in ("propose", "history") else None), indent=2, ensure_ascii=False))
            return 0
        if args.command == "project":
            from . import projects
            if args.action == "add":
                entry, created = projects.add(root, args.path)
                print(("Registered: " if created else "Already registered: ") + entry["id"])
                print(json.dumps(projects.inspect(root, entry["id"]), indent=2, ensure_ascii=False))
                print("Onboarding available: use /dryft-add-project. Interpretations require candidate review.")
            elif args.action == "list":
                for entry in projects.registry(root):
                    print(f"{entry['id']}  {projects.status(entry)}  {entry['path']}")
            elif args.action == "inspect":
                print(json.dumps(projects.inspect(root, args.id), indent=2, ensure_ascii=False))
            else:
                print(projects.propose(root, args.id, input_json()))
            return 0
        if args.command == "brain":
            from . import brain
            from .workspace import managed_path, read_json
            if args.action == "capture":
                print(brain.capture(root, args.id, input_json()))
            elif args.action == "candidates":
                with brain.locked(root):
                    for meta, body in brain.candidates(root, args.status):
                        path = managed_path(root, f"brain/candidates/{brain.identifier(meta['id'])}.md")
                        print(path.read_text(encoding="utf-8"))
                        print("Review SHA256: " + brain.digest(path.read_text(encoding="utf-8")))
            elif args.action == "requests":
                directory = managed_path(root, ".dryft/state/captures")
                for path in sorted(directory.glob("*.json")):
                    request = read_json(root, str(path.relative_to(root)))
                    if request.get("status") == "requested":
                        print(request["id"] + " " + request["created"])
            elif args.action == "review":
                print(brain.review(root, args.id, args.decision, args.user_instruction,
                                   args.expected_sha256, input_json() if args.decision == "edit" else None))
            elif args.action in ("providers", "index"):
                from . import capabilities
                if args.action == "providers":
                    print(json.dumps(capabilities.discover(root), indent=2))
                else:
                    print(json.dumps(capabilities.index(root, args.provider, args.rebuild)))
            else:
                hits = brain.search(root, args.query, args.limit, args.depth, args.provider)
                if not hits:
                    print("No approved evidence found for this query.")
                for path, title, body in hits:
                    print(f"{path}: {title}\n{body}\n")
            return 0
        lines, healthy = diagnose(root)
        print("\n".join(lines))
        return 0 if healthy else 1
    except (WorkspaceError, OSError, ValueError, RecursionError) as exc:
        if args.command == "ui":
            print(json.dumps({"error": str(exc)}), file=sys.stderr)
        else:
            print(f"dryft: {exc}", file=sys.stderr)
        return 1
