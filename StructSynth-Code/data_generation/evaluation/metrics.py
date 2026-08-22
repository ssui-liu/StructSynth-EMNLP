import glob
from sklearn.metrics import (
    accuracy_score, f1_score,
    precision_score, recall_score, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)
import pandas as pd
from pathlib import Path
import json
import os
import numpy as np
import argparse

from data_generation.evaluation.dcr_evaluation_pipeline import evaluate_dcr
from data_generation.evaluation.pairwise_correlation_evaluation import evaluate_pairwise_correlation
from data_generation.evaluation.downstream_performance_evaluation import calculate_downstream_performance


class EvaluationMetrics:
    # Define regression datasets - add your dataset names here
    REGRESSION_DATASETS = {
        'salary', 'obesity_reg'
    }

    @staticmethod
    def is_regression_task(dataset_name: str) -> bool:
        """Determine if the dataset is a regression task based on predefined list."""
        return dataset_name.lower() in EvaluationMetrics.REGRESSION_DATASETS

    @staticmethod
    def _save_report(content: str, save_path: Path, title: str = "Report") -> None:
        """
        Helper method to save a report to a file.
        """
        try:
            with open(save_path, 'w') as f:
                f.write(content)
            print(f"\nSaved {title} to {save_path}")
        except Exception as e:
            print(f"\nError saving {title} to {save_path}: {str(e)}")

    @staticmethod
    def _ensure_directory(path: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def evaluate_and_save(dataset_name, num_shot, method_name, n_samples=1000):
        """
        Main function to run all evaluations for a given setting and save the results.
        """
        print(f"Running all evaluations for {dataset_name}, method {method_name}, shots {num_shot}")

        synthetic_data_pattern = f"synth_data/{dataset_name}/{num_shot}_shot/{method_name}/n{n_samples}/seed_*/synthetic.csv"
        synthetic_files = glob.glob(synthetic_data_pattern)

        if not synthetic_files:
            print(f"No synthetic data found for the specified parameters.")
            return

        all_results = []

        for synth_file_path in synthetic_files:
            try:
                seed = int(Path(synth_file_path).parent.name.split('_')[-1])
                
                real_train_path = f"data/{dataset_name}/{num_shot}_shot/seed_{seed}/train.csv"
                real_test_path = f"data/{dataset_name}/{num_shot}_shot/seed_{seed}/test.csv"
                dataset_info_path = f"data/{dataset_name}/dataset_info.json"

                if not all(os.path.exists(p) for p in [real_train_path, real_test_path, dataset_info_path]):
                    print(f"Data or info not found for seed {seed}")
                    continue

                real_train_data = pd.read_csv(real_train_path)
                real_test_data = pd.read_csv(real_test_path)
                synth_data = pd.read_csv(synth_file_path)
                with open(dataset_info_path, 'r') as f:
                    dataset_info = json.load(f)

                synth_data = synth_data[real_train_data.columns]
                
                categorical_cols = real_train_data.select_dtypes(include=['object']).columns.tolist()
                numerical_cols = real_train_data.select_dtypes(include=np.number).columns.tolist()

                # Run all evaluations
                dcr_metrics = evaluate_dcr(synth_data, real_train_data, real_test_data, categorical_cols, numerical_cols, seed)
                pairwise_metrics = evaluate_pairwise_correlation(real_test_data, synth_data, numerical_cols, categorical_cols)
                downstream_metrics = calculate_downstream_performance(synth_data, real_test_data, dataset_name, dataset_info, numerical_cols, categorical_cols)

                # Combine results
                combined_metrics = {
                    "seed": seed,
                    **dcr_metrics,
                    **pairwise_metrics,
                    **downstream_metrics
                }
                all_results.append(combined_metrics)
                print(f"Processed seed {seed}, Metrics: {combined_metrics}")

            except Exception as e:
                print(f"Error processing file {synth_file_path}: {e}")

        if not all_results:
            print("No results to save.")
            return

        # Aggregate and save reports
        EvaluationMetrics.generate_summary_reports(dataset_name, num_shot, method_name, all_results)

    @staticmethod
    def generate_summary_reports(dataset_name, num_shot, method_name, all_results):
        """
        Generates and saves summary reports from the collected results.
        """
        results_dir = Path(f"results/{dataset_name}/{num_shot}_shot/{method_name}")
        EvaluationMetrics._ensure_directory(results_dir)

        df_results = pd.DataFrame(all_results)
        
        # Detailed results
        with open(results_dir / "detailed_results.json", "w") as f:
            json.dump(all_results, f, indent=4)

        # Summary statistics
        summary = {}
        metric_cols = [col for col in df_results.columns if col != 'seed']
        for col in metric_cols:
            mean_val = df_results[col].mean()
            std_val = df_results[col].std()
            summary[col] = f"{mean_val:.4f} +- {std_val:.4f}"

        with open(results_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=4)

        # Markdown summary
        md_content = f"# Evaluation Summary for {method_name}\n\n"
        md_content += f"**Dataset:** {dataset_name}\n"
        md_content += f"**Number of shots:** {num_shot}\n"
        md_content += f"**Number of seeds:** {len(all_results)}\n\n"
        md_content += "## Averaged Metrics\n\n"
        for key, value in summary.items():
            md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        EvaluationMetrics._save_report(md_content, results_dir / "summary.md", "Overall Summary")
        print(f"Results saved to {results_dir}")
        
    @staticmethod
    def generate_comparison_markdown(dataset_name, num_shot):
        """
        Generates a markdown file comparing metrics across different methods.
        """
        print(f"Generating comparison for {dataset_name}, shot {num_shot}")
        base_path = Path(f"results/{dataset_name}/{num_shot}_shot")
        method_dirs = [d for d in base_path.iterdir() if d.is_dir()]

        summaries = {}
        for method_dir in method_dirs:
            summary_path = method_dir / "summary.json"
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    summaries[method_dir.name] = json.load(f)

        if not summaries:
            print("No summaries found to generate comparison.")
            return

        comparison_dir = base_path / "comparison"
        EvaluationMetrics._ensure_directory(comparison_dir)
        comparison_md_path = comparison_dir / "comparison.md"
        
        # Determine all metric names from summaries
        first_summary = next(iter(summaries.values()))
        metrics = sorted(first_summary.keys())
        
        md_content = f"# Methods Comparison for {dataset_name} ({num_shot}-shot)\n\n"
        md_content += "| Method | " + " | ".join([m.replace('_', ' ').title() for m in metrics]) + " |\n"
        md_content += "|" + "---|" * (len(metrics) + 1) + "\n"

        for method, summary in sorted(summaries.items()):
            md_content += f"| {method} |"
            for metric in metrics:
                value = summary.get(metric, "N/A")
                md_content += f" {value} |"
            md_content += "\n"
        
        EvaluationMetrics._save_report(md_content, comparison_md_path, "Comparison Markdown")

