import argparse
import pandas as pd
from pathlib import Path
# import torch
import json

from data_generation.utils.config import load_config
from data_generation.models.generator import HierarchicalSyntheticDataGenerator
from data_generation.evaluation.metrics import EvaluationMetrics
from data_generation.utils.utils import (
    get_data_paths,
    update_token_usage, save_token_usage_stats, print_token_usage,
    evaluate_and_save_results
)

def main(config_path: str):
    # Load configs using new config loader
    config = load_config(config_path)
    
    # Load dataset info from JSON file
    dataset_name = config.data.dataset_name
    dataset_info_path = Path(config.data.base_dir) / dataset_name / "dataset_info.json"
    
    if dataset_info_path.exists():
        with open(dataset_info_path, 'r') as f:
            dataset_info = json.load(f)
        print(f"Loaded dataset info for {dataset_name}")
    else:
        print(f"Warning: No dataset_info.json found at {dataset_info_path}")
        dataset_info = None
    
    # Create base results directory with new structure
    results_dir = Path("./results/synth_data")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create a consistent causal method name for directory structure
    model_prefix = "hier"
    evaluation_model_name = f"{model_prefix}"
    
    # Initialize token usage tracking
    total_token_usage = {
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    }
    
    # For each shot setting
    for shot in config.data.shots:
        print(f"\nProcessing {shot}-shot setting...")
        
        # Track token usage per shot
        shot_token_usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
        
        # Create shot directory with consistent causal method naming
        shot_dir = results_dir / config.data.dataset_name / f"{shot}_shot"
        shot_dir.mkdir(parents=True, exist_ok=True)
        
        # For each seed
        for seed in config.data.seeds:
            # Track token usage per seed
            seed_token_usage = {
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0
            }
            
            print(f"\nUsing seed {seed}")
            
            # Get data paths and load few-shot and corresponding test data
            few_shot_path, test_path = get_data_paths(
                config.data.base_dir,
                config.data.dataset_name,
                shot,
                seed
            )
            few_shot_df = pd.read_csv(few_shot_path)
            test_df = pd.read_csv(test_path)
            
            # Define path to load hierarchical causal graph
            # Using llmcd structure but looking for graph.json: llmcd_causal_results/{dataset}/shot_{shot}/seed_{seed}/graph.json
            causal_root_path = Path(f"./results/structure_graph/{dataset_name}/{shot}_shot/seed_{seed}")
            graph_file_path = causal_root_path / "graph.json"
            
            # Load causal graph from file - no fallback logic
            if graph_file_path.exists():
                print(f"\nLoading hierarchical causal graph from: {graph_file_path}")
                with open(graph_file_path, 'r') as f:
                    graph_data = json.load(f)
                print(f"Graph contains {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
            else:
                raise ValueError(f"Causal graph file not found at expected location: {graph_file_path}")
            
            # Create a base directory for this seed to store common files
            seed_base_dir = shot_dir / f"seed_{seed}"
            seed_base_dir.mkdir(parents=True, exist_ok=True)
            
            # Save causal graph info at the seed level for reference
            causal_info_path = seed_base_dir / "causal_graph_info.txt"
            with open(causal_info_path, 'w') as f:
                f.write(f"Graph File: {graph_file_path}\n")
                f.write(f"Nodes: {len(graph_data.get('nodes', []))}\n")
                f.write(f"Edges: {len(graph_data.get('edges', []))}\n\n")
                f.write("Graph Structure:\n")
                f.write(json.dumps(graph_data, indent=2))
            
            # Initialize hierarchical generator
            generator = HierarchicalSyntheticDataGenerator(
                few_shot_df=few_shot_df,
                meta_data=dataset_info,
                graph_file=str(graph_file_path),  # Pass the graph file path
                n_row_samples_per_class=10,
                model=config.model.name,
                temperature=config.model.temperature,
                max_tokens=config.model.max_tokens,
                api_key=config.model.api_key,
                dataset=config.data.dataset_name,
            )
            
            # Get the maximum number of samples needed
            max_n_samples = max(sorted(config.synthetic.n_samples_list))
            
            # Generate synthetic data for maximum samples once
            # No causal_info parameter needed since it comes from graph file
            generator.fit()
            X_syn_max, y_syn_max, usage = generator.generate(max_n_samples, return_token_usage=True)
            
            # Print generation order and causal relationships for debugging
            print(f"\nHierarchical generation order: {generator.get_generation_order()}")
            print(f"Causal relationships: {generator.get_causal_relationships()}")
            
            # Filter synthetic data to keep only original features
            if set(few_shot_df.columns) != set(X_syn_max.columns):
                print(f"\nFiltering synthetic data to keep only original features")
                # Get the label column name from dataset_info or use default
                if dataset_info and 'label_column' in dataset_info:
                    label_col = dataset_info['label_column']
                else:
                    # Default label column name - adjust as needed for your dataset
                    label_col = 'label'  # or another appropriate default
                
                # Keep only columns that were in the original dataset (excluding the label)
                original_features = [col for col in few_shot_df.columns if col != label_col]
                filtered_columns = [col for col in X_syn_max.columns if col in original_features]
                
                # If there are columns to filter
                if len(filtered_columns) < len(X_syn_max.columns):
                    print(f"Removing {len(X_syn_max.columns) - len(filtered_columns)} additional factor columns")
                    X_syn_max = X_syn_max[filtered_columns]
                    print(f"Synthetic data now has {len(X_syn_max.columns)} features")
                else:
                    print(f"No additional columns to filter out")
            
            # Update token usage for the max sample generation
            update_token_usage(usage, seed_token_usage, shot_token_usage, total_token_usage)
            print_token_usage(usage, "maximum sample generation")
            
            # Process each sample size by taking subsets
            for n_samples in sorted(config.synthetic.n_samples_list):
                print(f"\nProcessing {n_samples} samples...")
                
                # Create n_samples directory under seed directory (new structure)
                n_samples_dir = seed_base_dir / f"n{n_samples}"
                n_samples_dir.mkdir(parents=True, exist_ok=True)
                
                # Take subset of the maximum generated samples
                X_syn = X_syn_max.head(n_samples)
                y_syn = y_syn_max.head(n_samples)
                
                # Evaluate and save results for this subset
                evaluate_and_save_results(
                    X_syn=X_syn,
                    y_syn=y_syn,
                    few_shot_df=few_shot_df,  # Use original few_shot_df for evaluation
                    test_df=test_df,
                    config=config,
                    dataset_name=config.data.dataset_name,
                    model_name=evaluation_model_name,  # Use updated model name
                    shot=shot,
                    seed=seed,
                    n_samples=n_samples,
                    save_dir=n_samples_dir,
                    custom_path=causal_path_name
                )
                
                print(f"\nResults saved for n={n_samples}, seed {seed}")
            
            # Save token usage statistics for this seed
            save_token_usage_stats(
                results_dir, 
                seed_token_usage,
                dataset_name=config.data.dataset_name,
                shot=shot,
                causal_path=causal_path_name,
                seed=seed
            )
            
            print(f"\nAll sample sizes processed for seed {seed}")
            print_token_usage(seed_token_usage, f"seed {seed}")
        
        print(f"\nAll seeds processed")
        print_token_usage(shot_token_usage, f"{shot}-shot")
        
        # Save token usage statistics for this shot
        save_token_usage_stats(
            results_dir, 
            shot_token_usage,
            dataset_name=config.data.dataset_name,
            shot=shot,
            causal_path=causal_path_name
        )
        
        # Generate comparison across different causal methods for this shot
        EvaluationMetrics.compare_causal_methods(
            dataset_name=config.data.dataset_name,
            shot=shot,
            base_results_dir=results_dir
        )
    
    print(f"\nTotal token usage across all experiments:")
    print_token_usage(total_token_usage, "all experiments")
    
    # Save token usage statistics at the global level
    save_token_usage_stats(results_dir, total_token_usage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/data_generation_config.yaml")
    args = parser.parse_args()
    main(args.config) 