"""Command line entry points for the same validated experiment pipeline."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import logging
from pathlib import Path
import sys

from . import __version__
from .config import load_config


def build_parser():
    parser = argparse.ArgumentParser(prog="structsynth", description="Paper-aligned tabular synthesis experiments")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "split", "discover", "generate", "evaluate", "plan"):
        task = sub.add_parser(command)
        task.add_argument("--config", type=Path, required=True, help="Paths inside this file are config-relative")
        task.add_argument("--shots", nargs="+", type=int)
        task.add_argument("--seeds", nargs="+", type=int)
        if command != "plan":
            task.add_argument("--resume", action="store_true", help="Verify and reuse completed run artifacts")
            task.add_argument("--replay-dir", type=Path, help="Offline replay of discovery_requests.jsonl and generation_requests.jsonl")
    demo = sub.add_parser("demo", help="Offline plumbing check using copied training rows, not an LLM benchmark")
    demo.add_argument("--output-dir", type=Path, default=Path("runs/offline_demo"))
    demo.add_argument("--resume", action="store_true")
    demo.add_argument("--max-workers", type=int, default=1)
    demo.add_argument("--model", choices=["logistic", "random_forest", "xgboost"], default="logistic")
    report = sub.add_parser("report", help="Summarize compatible seeds from explicit run directories")
    report.add_argument("--run-dirs", nargs="+", type=Path, required=True)
    report.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.command == "report":
            from .evaluation.reporting import write_summary
            print(write_summary(args.run_dirs, args.output_dir))
            return 0
        elif args.command == "demo":
            from .demo import run_demo
            paths = run_demo(args.output_dir, resume=args.resume, max_workers=args.max_workers, model=args.model)
            print("OFFLINE DEMO: copies training records; these metrics are not LLM quality results.")
        else:
            from .pipeline import plan_experiments, run_experiments
            config = load_config(args.config)
            if args.shots is not None:
                config.data.shots = args.shots
            if args.seeds is not None:
                config.data.seeds = args.seeds
            config.data.__post_init__()
            if args.command == "plan":
                print(json.dumps(plan_experiments(config), indent=2))
                return 0
            factory = None
            backend = "live"
            if args.replay_dir:
                if len(config.data.shots) != 1 or len(config.data.seeds) != 1:
                    raise ValueError("Replay requires one shot and seed; select them with --shots and --seeds")
                from .llm import ReplayClient
                from .artifacts import file_hash
                replay_dir = args.replay_dir.resolve()
                def factory(name, _config, _ledger, _train, _spec):
                    model = ReplayClient(replay_dir / f"{name}_requests.jsonl", ledger=_ledger)
                    if model.identity.get("kind") == "openai-compatible" and model.identity.get("config") != asdict(_config):
                        raise ValueError(f"Replay {name} model configuration differs from the source journal")
                    return model
                backend = {"kind": "replay", "source_ledgers": {
                    name: file_hash(replay_dir / f"{name}_requests.jsonl")
                    for name in ("discovery", "generation")}}
            paths = run_experiments(config, stage="all" if args.command == "run" else args.command,
                                    resume=args.resume, client_factory=factory, backend=backend)
        for path in paths:
            print(path)
        return 0
    except (ValueError, RuntimeError, OSError, ImportError) as exc:
        if args.verbose:
            raise
        print(f"structsynth: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
