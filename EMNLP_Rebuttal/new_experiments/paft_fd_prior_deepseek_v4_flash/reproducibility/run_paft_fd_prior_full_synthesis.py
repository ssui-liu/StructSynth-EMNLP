#!/usr/bin/env python3
"""Run StructSynth data synthesis with PAFT-FD graph priors."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
PAFT_ROOT = WORKSPACE_ROOT / "Permutation-aided-Fine-tuning"
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils import (  # noqa: E402
    evaluate_and_save_results,
    print_token_usage,
    save_token_usage_stats,
    update_token_usage,
)
from src.models.generator import HierarchicalSyntheticDataGenerator  # noqa: E402


DATASETS = ["adult", "anxiety", "compas", "salary", "obesity_reg", "churn"]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and evaluate synthetic tables using PAFT-FD graph priors."
    )
    parser.add_argument("--datasets", nargs="+", default=DATASETS)
    parser.add_argument("--shot", type=int, default=100)
    parser.add_argument("--seeds", type=parse_int_list, default=[42])
    parser.add_argument("--n-samples-list", type=parse_int_list, default=[100, 200, 500, 1000])
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--max-tokens", type=int, default=8000)
    parser.add_argument("--max-concurrency", type=int, default=int(os.getenv("SYNTH_MAX_CONCURRENCY", "4")))
    parser.add_argument("--samples-per-call", type=int, default=int(os.getenv("SYNTH_SAMPLES_PER_CALL", "20")))
    parser.add_argument("--data-root", type=Path, default=PAFT_ROOT / "data" / "structsynth")
    parser.add_argument("--graph-root", type=Path, default=PROJECT_ROOT / "paft_fd_causal_results")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "results" / "paft_fd_prior_llm_synthesis",
    )
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def effective_api_key(model: str) -> str | None:
    model_lower = model.lower()
    # `deepseek-v4-flash` is served through the project's XiaoAI
    # OpenAI-compatible gateway (see CLLM.__init__), so it must use the
    # gateway credential rather than the official DeepSeek credential.
    if model_lower == "deepseek-v4-flash":
        return (
            os.getenv("XIAOAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("DEEPSEEK_API_KEY")
        )
    if "deepseek" in model_lower:
        return os.getenv("DEEPSEEK_API_KEY")
    if "qwen" in model_lower:
        return os.getenv("DASHSCOPE_API_KEY")
    return (
        os.getenv("XIAOAI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )


def make_eval_config(target_column: str) -> SimpleNamespace:
    return SimpleNamespace(
        data=SimpleNamespace(
            target_column=target_column,
            categorical_columns=None,
        )
    )


def token_usage_zero() -> dict[str, int]:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def run_one(args: argparse.Namespace, dataset: str, seed: int, total_usage: dict[str, int]) -> dict[str, Any]:
    shot = args.shot
    n_samples_list = sorted(args.n_samples_list)
    max_n_samples = max(n_samples_list)
    method_name = f"paft_fd_prior_{args.model}"

    train_path = args.data_root / dataset / f"{shot}_shot" / f"seed_{seed}" / "train.csv"
    test_path = args.data_root / dataset / f"{shot}_shot" / f"seed_{seed}" / "test.csv"
    info_path = args.data_root / dataset / "dataset_info.json"
    graph_path = args.graph_root / dataset / f"shot_{shot}" / f"seed_{seed}" / "graph.json"
    metadata_path = args.graph_root / dataset / f"shot_{shot}" / f"seed_{seed}" / "graph_metadata.json"

    seed_dir = args.output_root / dataset / f"{shot}_shot" / method_name / f"seed_{seed}"
    summary_path = seed_dir / "run_summary.json"

    if args.skip_existing and all((seed_dir / f"n{n}" / "synthetic_data.csv").exists() for n in n_samples_list):
        print(f"SKIP {dataset}/seed_{seed}: existing outputs found")
        return read_json(summary_path) if summary_path.exists() else {
            "dataset": dataset,
            "seed": seed,
            "skipped": True,
            "passed": True,
        }

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    dataset_info = read_json(info_path)
    graph_data = read_json(graph_path)
    graph_metadata = read_json(metadata_path) if metadata_path.exists() else {}
    target_col = dataset_info["label_column"]

    seed_dir.mkdir(parents=True, exist_ok=True)
    write_json(seed_dir / "graph_snapshot.json", graph_data)
    write_json(seed_dir / "graph_metadata_snapshot.json", graph_metadata)

    with open(seed_dir / "causal_graph_info.txt", "w", encoding="utf-8") as f:
        f.write("Causal Prior: PAFT FD graph\n")
        f.write(f"Graph File: {graph_path}\n")
        f.write(f"Nodes: {len(graph_data.get('nodes', []))}\n")
        f.write(f"Edges: {len(graph_data.get('edges', []))}\n")
        f.write(f"Raw PAFT FD Edges: {graph_metadata.get('raw_fd_edge_count')}\n")
        f.write(f"Dropped PAFT Edges: {graph_metadata.get('dropped_edge_count')}\n")

    generator = HierarchicalSyntheticDataGenerator(
        few_shot_df=train_df,
        meta_data=dataset_info,
        graph_file=str(graph_path),
        n_row_samples_per_class=10,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        api_key=effective_api_key(args.model),
        dataset=dataset,
        use_naive=True,
    )

    seed_usage = token_usage_zero()
    shot_usage = token_usage_zero()

    generator.fit()
    X_syn_max, y_syn_max, usage = generator.cllm_model.generate(
        max_n_samples,
        return_token_usage=True,
        max_concurrency=args.max_concurrency,
        samples_per_call=args.samples_per_call,
    )

    original_features = [col for col in train_df.columns if col != target_col]
    X_syn_max = X_syn_max.reindex(columns=original_features)

    update_token_usage(usage, seed_usage, shot_usage, total_usage)
    print_token_usage(usage, f"{dataset}/seed_{seed} generation")

    eval_config = make_eval_config(target_col)
    samples = []
    for n_samples in n_samples_list:
        n_dir = seed_dir / f"n{n_samples}"
        n_dir.mkdir(parents=True, exist_ok=True)
        X_syn = X_syn_max.head(n_samples)
        y_syn = y_syn_max.head(n_samples)

        evaluate_and_save_results(
            X_syn=X_syn,
            y_syn=y_syn,
            few_shot_df=train_df,
            test_df=test_df,
            config=eval_config,
            dataset_name=dataset,
            model_name="paft_fd_prior_cllm",
            shot=shot,
            seed=seed,
            n_samples=n_samples,
            save_dir=n_dir,
            custom_path=method_name,
        )

        synthetic_path = n_dir / "synthetic_data.csv"
        metrics_path = n_dir / "metrics.json"
        line_count = sum(1 for _ in synthetic_path.open()) if synthetic_path.exists() else 0
        samples.append(
            {
                "n_samples": n_samples,
                "synthetic_data_path": str(synthetic_path),
                "metrics_path": str(metrics_path),
                "line_count": line_count,
                "expected_line_count": n_samples + 1,
                "passed": synthetic_path.exists() and metrics_path.exists() and line_count == n_samples + 1,
            }
        )
        print(f"  Saved {dataset}/seed_{seed}/n{n_samples}: lines={line_count}")

    save_token_usage_stats(
        args.output_root,
        seed_usage,
        dataset_name=dataset,
        shot=shot,
        causal_path=method_name,
        seed=seed,
    )

    summary = {
        "dataset": dataset,
        "shot": shot,
        "seed": seed,
        "method": method_name,
        "model": args.model,
        "train_path": str(train_path),
        "test_path": str(test_path),
        "graph_path": str(graph_path),
        "output_dir": str(seed_dir),
        "graph_edges": len(graph_data.get("edges", [])),
        "paft_raw_fd_edges": graph_metadata.get("raw_fd_edge_count"),
        "paft_dropped_edges": graph_metadata.get("dropped_edge_count"),
        "generation_order": graph_data.get("hierarchical_structure", {}).get("generation_order", []),
        "token_usage": seed_usage,
        "samples": samples,
        "passed": all(sample["passed"] for sample in samples),
    }
    write_json(summary_path, summary)
    return summary


def write_manifest(args: argparse.Namespace, summaries: list[dict[str, Any]], total_usage: dict[str, int]) -> None:
    manifest = {
        "passed": all(summary.get("passed") for summary in summaries),
        "n_summaries": len(summaries),
        "datasets": args.datasets,
        "shot": args.shot,
        "seeds": args.seeds,
        "n_samples_list": sorted(args.n_samples_list),
        "model": args.model,
        "max_concurrency": args.max_concurrency,
        "samples_per_call": args.samples_per_call,
        "output_root": str(args.output_root),
        "total_token_usage": total_usage,
        "summaries": summaries,
    }
    write_json(args.output_root / "manifest.json", manifest)


def main() -> None:
    args = parse_args()
    unknown = sorted(set(args.datasets) - set(DATASETS))
    if unknown:
        raise ValueError(f"Unknown dataset(s): {unknown}. Supported: {DATASETS}")

    args.output_root.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    total_usage = token_usage_zero()

    for dataset in args.datasets:
        for seed in args.seeds:
            print(f"\n=== PAFT-FD prior synthesis: {dataset}/seed_{seed} ===")
            summary = run_one(args, dataset, seed, total_usage)
            summaries.append(summary)
            write_manifest(args, summaries, total_usage)
            status = "PASS" if summary.get("passed") else "FAIL"
            print(f"{status} {dataset}/seed_{seed}: out={summary.get('output_dir')}")

    write_manifest(args, summaries, total_usage)
    if not all(summary.get("passed") for summary in summaries):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
