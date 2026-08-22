
import os
import argparse
import pathlib
import itertools
import copy

from structure_learning.data.data_loader import DataLoader
from structure_learning.discovery.bfs_causal_discovery import BfsLLMCausalDiscovery
from data_generation.utils import ConfigLoader


def parse_list_argument(arg_value):
    """
    Parse a command line argument that can be either a single value or a comma-separated list.
    
    Args:
        arg_value (str): The argument value from command line
        
    Returns:
        list: List of integers parsed from the argument
    """
    if arg_value is None:
        return None
    
    # Split by comma and convert to integers
    try:
        return [int(x.strip()) for x in arg_value.split(',')]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid list format: {arg_value}. Use comma-separated integers.")


def normalize_to_list(value):
    """
    Normalize a value to be a list. If it's already a list, return as-is.
    If it's a single value, wrap it in a list.
    
    Args:
        value: The value to normalize (can be int, list, etc.)
        
    Returns:
        list: The value as a list
    """
    if isinstance(value, list):
        return value
    elif value is not None:
        return [value]
    else:
        return []


def parse_args():
    """
    Parse command line arguments for BFS-based causal discovery.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run BFS LLM-based Causal Discovery")

    # Determine the script's directory to make the default config path relative to project root
    script_dir = pathlib.Path(__file__).resolve().parent
    # The config file is in the 'config' directory at the project root.
    default_config_path = script_dir / "config" / "structure_learning_config.json"

    parser.add_argument("--config", type=str, default=str(default_config_path),
                        help=f"Path to configuration file (default: {default_config_path})")
    parser.add_argument("--dataset_name", type=str,
                        help="Name of the dataset (overrides config's data_config.dataset_name)")
    parser.add_argument("--num_shots", type=str,
                        help="Number of shots for the dataset - single value or comma-separated list (overrides config's data_config.num_shots)")
    parser.add_argument("--seed", type=str,
                        help="Seed for the dataset - single value or comma-separated list (overrides config's data_config.seed)")
    parser.add_argument("--output_dir", type=str,
                        help="Base output directory (overrides config's output.output_dir)")

    return parser.parse_args()


def run_single_experiment(config, num_shots, seed, experiment_id, total_experiments):
    """
    Run a single causal discovery experiment with specific num_shots and seed using BFS.
    
    Args:
        config (dict): The configuration dictionary
        num_shots (int): Number of shots for this experiment
        seed (int): Seed for this experiment
        experiment_id (int): Current experiment number (1-indexed)
        total_experiments (int): Total number of experiments
        
    Returns:
        tuple: (graph, report) from the discovery pipeline
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT {experiment_id}/{total_experiments}")
    print(f"num_shots: {num_shots}, seed: {seed}")
    print(f"{'='*60}")
    
    # Create a deep copy of config for this experiment to avoid cross-contamination
    experiment_config = copy.deepcopy(config)
    
    # Set specific num_shots and seed for this experiment
    experiment_config["data_config"]["num_shots"] = num_shots
    experiment_config["data_config"]["seed"] = seed
    
    # Create hierarchical output directory: base_output_dir/dataset_name/model/temp/seed
    base_output_dir = config["output"]["output_dir"]  # Use original config's base dir
    dataset_name = experiment_config["data_config"].get("dataset_name", "unknown_dataset")
    llm_config = experiment_config.get("llm_config", {})
    model_name = llm_config.get("model_name", "unknown-model").replace("/", "_")
    temperature = llm_config.get("temperature", 0.0)
    
    experiment_output_dir = os.path.join(
        base_output_dir, dataset_name, model_name, str(temperature), str(seed)
    )
    experiment_config["output"]["output_dir"] = experiment_output_dir
    
    print(f"Experiment output directory: {experiment_output_dir}")
    
    # Initialize DataLoader for this experiment
    print(f"Initializing DataLoader for shots={num_shots}, seed={seed}...")
    data_loader = DataLoader(experiment_config["data_config"])
    
    # Initialize BfsLLMCausalDiscovery for this experiment
    print(f"Initializing BfsLLMCausalDiscovery for shots={num_shots}, seed={seed}...")
    bfs_discovery = BfsLLMCausalDiscovery(config=experiment_config, 
                                          data_loader=data_loader,
                                          discovery_method="bfs")
    
    # Run causal discovery pipeline
    print(f"Running BFS causal discovery for shots={num_shots}, seed={seed}...")
    if data_loader.dataset_path:
        print(f"Using dataset related to: {data_loader.dataset_path}")
    elif experiment_config["data_config"].get('dataset_name'):
        print(f"Using dataset name: {experiment_config['data_config'].get('dataset_name')}")
    
    # Run the discovery pipeline
    graph, report = bfs_discovery.run_discovery_pipeline()
    
    print(f"Experiment {experiment_id}/{total_experiments} completed successfully!")
    print(f"Results saved in: {bfs_discovery.experiment_output_dir}")
    
    return graph, report


def main():
    """
    Main entry point for the BFS-based causal discovery pipeline.
    Supports running multiple experiments with different num_shots and seed combinations.
    """
    args = parse_args()

    # Load configuration
    config = ConfigLoader.load_and_merge_config(args.config)

    # Override data_config with command line arguments if provided
    data_cfg = config.setdefault("data_config", {})
    if args.dataset_name:
        data_cfg["dataset_name"] = args.dataset_name
    
    # Handle num_shots and seed as potentially lists
    if args.num_shots:
        data_cfg["num_shots"] = parse_list_argument(args.num_shots)
    if args.seed:
        data_cfg["seed"] = parse_list_argument(args.seed)

    # Override output_config output_dir with command line argument if provided
    output_cfg = config.setdefault("output", {})
    if args.output_dir:
        output_cfg["output_dir"] = args.output_dir
    
    # Force the output directory to the desired path
    output_cfg["output_dir"] = os.path.join("results", "structure_graph")

    # BasicLLMCausalDiscovery expects 'output_dir' within the 'output' part of its config.
    if "output_dir" not in output_cfg or not output_cfg["output_dir"]:
        print("Error: 'output_dir' must be specified in the 'output' section of the "
              "configuration file or via the --output_dir command-line argument.")
        return

    # BasicLLMCausalDiscovery expects 'llm_config' at the root of its config.
    if "llm_config" not in config:
        print("Warning: 'llm_config' not found at the root of the configuration. "
              "LLMInterface may use default settings or fail if it expects specifics.")
        config["llm_config"] = {}  # Add an empty dict to prevent potential KeyError

    # Normalize num_shots and seed to lists
    num_shots_list = normalize_to_list(data_cfg.get("num_shots", [20]))  # Default to [20] if not specified
    seed_list = normalize_to_list(data_cfg.get("seed", [42]))  # Default to [42] if not specified
    
    # Generate all combinations of num_shots and seed
    experiment_combinations = list(itertools.product(num_shots_list, seed_list))
    total_experiments = len(experiment_combinations)
    
    print(f"Starting BFS causal discovery experiments...")
    dataset_name = data_cfg.get("dataset_name", "unknown_dataset")
    print(f"Dataset: {dataset_name}")
    print(f"LLM Provider: {config.get('llm_config', {}).get('provider_type', 'N/A')}")
    print(f"LLM Model: {config.get('llm_config', {}).get('model_name', 'N/A')}")
    print(f"num_shots options: {num_shots_list}")
    print(f"seed options: {seed_list}")
    print(f"Total experiments to run: {total_experiments}")
    print(f"Base output directory: {output_cfg['output_dir']}")
    
    # Store results from all experiments
    all_results = []
    
    # Run experiments for each combination
    for experiment_id, (num_shots, seed) in enumerate(experiment_combinations, 1):
        # try:
        graph, report = run_single_experiment(
            config, num_shots, seed, experiment_id, total_experiments
        )

        # Store results with metadata
        all_results.append({
            'num_shots': num_shots,
            'seed': seed,
            'graph': graph,
            'report': report,
            'experiment_id': experiment_id
        })

    
    # Print summary
    print(f"\n{'='*60}")
    print("ALL EXPERIMENTS COMPLETED")
    print(f"{'='*60}")
    print(f"Successfully completed {len(all_results)}/{total_experiments} experiments")
    print(f"Results are organized in subdirectories under: {output_cfg['output_dir']}")
    
    # Print individual experiment results summary
    for result in all_results:
        dataset_name = config["data_config"].get("dataset_name", "unknown_dataset")
        llm_config = config.get("llm_config", {})
        model_name = llm_config.get("model_name", "unknown-model").replace("/", "_")
        temperature = llm_config.get("temperature", 0.0)
        experiment_dir = f"{dataset_name}/{model_name}/{temperature}/{result['seed']}"
        print(f"  - Experiment {result['experiment_id']}: {experiment_dir}/")
    
    print(f"\nEach experiment directory contains:")
    print(f"  - Causal graph (from BFS)")
    print(f"  - Detailed discovery report")
    print(f"  - Visualizations (if enabled)")


if __name__ == "__main__":
    main() 