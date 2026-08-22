# Import necessary libraries
import argparse
from pathlib import Path
import pandas as pd
import yaml
from typing import List

from data.utils import load_dataset, split_dataset

def generate_few_shot_data(
    config_path: str,
    shots: List[int] = [10, 20, 50, 100],
    seeds: List[int] = [42, 43, 44, 45, 46]
) -> None:
    """
    Generate and save few-shot datasets with different numbers of samples and random seeds.
    
    Args:
        config_path (str): Path to the configuration file
        shots (List[int]): List of few-shot sample sizes to generate
        seeds (List[int]): List of random seeds for reproducibility
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get base directory and dataset name from config
    # base_dir = Path(config['data']['base_dir'])
    base_dir = Path("data")
    dataset_name = config['data']['dataset_name']
    
    # Create dataset directory if it doesn't exist
    dataset_dir = base_dir / dataset_name
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the full dataset
    df = load_dataset(dataset_name, seed=42)
    
    # Generate few-shot datasets for each combination of shot and seed
    for shot in shots:
        shot_dir = dataset_dir / f"{shot}_shot"
        shot_dir.mkdir(exist_ok=True)
        
        for seed in seeds:
            # Create seed-specific directory
            seed_dir = shot_dir / f"seed_{seed}"
            seed_dir.mkdir(exist_ok=True)
            
            # Split dataset with current shot size and seed
            df_few_shot, df_oracle, df_test = split_dataset(
                df,
                test_size=0.2,
                few_shot_size=shot,
                seed=seed,
                label_column=config['data'].get('target_column', None)
            )
            
            # Save all splits for each seed
            df_few_shot.to_csv(seed_dir / "train.csv", index=False)
            df_oracle.to_csv(seed_dir / "oracle.csv", index=False)
            df_test.to_csv(seed_dir / "test.csv", index=False)  # Save test set for each seed
            
            print(f"Generated {shot}-shot dataset with seed {seed}")

def main():
    """Main function to run data generation script."""
    parser = argparse.ArgumentParser(description='Generate few-shot datasets')
    parser.add_argument('--config', type=str, help='Path to configuration file',
                        default='configs/churn_config.yaml')
    parser.add_argument('--shots', type=int, nargs='+', default=[20, 40, 50, 60, 80, 100, 200],
                        help='List of few-shot sample sizes')
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
                        help='List of random seeds')
    
    args = parser.parse_args()
    
    # Generate datasets
    generate_few_shot_data(
        config_path=args.config,
        shots=args.shots,
        seeds=args.seeds
    )

if __name__ == "__main__":
    main() 