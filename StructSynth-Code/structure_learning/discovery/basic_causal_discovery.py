from typing import Dict, List, Any, Optional, Tuple, Set
import itertools
from tqdm import tqdm
import pandas as pd
import numpy as np
import time
import os
import json # Added for caching

from ..data.data_loader import DataLoader
from ..llm.llm_interface import LLMInterface, CausalRelationship
from ..graph.structure_graph import StructureGraph

class BasicLLMCausalDiscovery:
    """
    Basic class for LLM-based causal discovery that only performs initial hypothesis generation
    without refinement or contradiction checking
    """
    def __init__(self, config: Dict[str, Any], data_loader: DataLoader, discovery_method: str = "basic"):
        """
        Initialize the basic causal discovery pipeline
        
        Args:
            config: Configuration dictionary
            data_loader: An initialized DataLoader instance
            discovery_method: The discovery method variant to use ("basic" or "basic_no_corr")
        """

        self.config = config
        self.data_loader = data_loader
        self.discovery_method = discovery_method
        self.llm = LLMInterface(config.get("llm_config"))
        self.confidence_threshold = config.get("confidence_threshold", "Medium")
        
        # Get base output directory from config
        output_config = self.config.get("output")
        self.base_output_dir = output_config.get("output_dir")
        if not self.base_output_dir:
            raise ValueError("output_dir must be specified in the output configuration.")

        # Construct and store the experiment-specific output directory
        self.experiment_output_dir = self._construct_experiment_specific_dir(self.base_output_dir)
        
        # Cache path will be defined in initial_hypothesis_generation
        self.cache_path: Optional[str] = None
        self.associations = None
        # Ensure the experiment output directory exists
        os.makedirs(self.experiment_output_dir, exist_ok=True)
        
        # Attribute to store detailed variable descriptions
        self.variable_details: Optional[Dict[str, Dict[str, Any]]] = None 
        self.variables: Optional[List[str]] = None # To store variable names
        
        # Track token usage
        self.total_token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_cost": 0
        }
    
    def _update_token_usage(self, usage_info: Dict[str, Any]) -> None:
        """Update the total token usage statistics"""
        if not usage_info:
            return
            
        self.total_token_usage["prompt_tokens"] += usage_info.get("prompt_tokens", 0)
        self.total_token_usage["completion_tokens"] += usage_info.get("completion_tokens", 0)
        self.total_token_usage["total_cost"] += usage_info.get("total_cost", 0)
    
    def load_data(self) -> None:
        """
        Load the dataset and metadata using the configured DataLoader.
        Also loads detailed variable descriptions.
        This method assumes the DataLoader is already configured with paths.
        """
        # Load dataset and metadata if not already loaded
        if self.data_loader.dataset is None:
            self.data_loader.load_dataset()
        if self.data_loader.metadata is None:
            self.data_loader.load_metadata()

        if self.data_loader.dataset is None:
            print("BasicLLMCausalDiscovery.load_data: Critical - Dataset could not be loaded. Aborting further operations.")
            # Potentially raise an error or set a state indicating failure
            return
        if self.data_loader.metadata is None:
            print("BasicLLMCausalDiscovery.load_data: Critical - Metadata could not be loaded. Aborting further operations.")
            # Potentially raise an error or set a state indicating failure
            return

        # Get the list of variables
        self.variables = self.data_loader.get_variables()
        if not self.variables:
            print("BasicLLMCausalDiscovery.load_data: Critical - No variables found in the dataset. Aborting.")
            return

        # Get detailed variable descriptions
        self.variable_details = self.data_loader.get_variable_descriptions()
        if not self.variable_details or "error" in self.variable_details:
            error_msg = self.variable_details.get("error", "Unknown error") if isinstance(self.variable_details, dict) else "Unknown error"
            print(f"BasicLLMCausalDiscovery.load_data: Critical - Could not load variable descriptions: {error_msg}. Aborting.")
            self.variable_details = None  # Ensure it's None on failure
            return

        self.associations = self.data_loader.get_correlation_matrix()
        print("BasicLLMCausalDiscovery.load_data: Data, metadata, and variable descriptions loaded successfully.")

    def _construct_experiment_specific_dir(self, base_output_dir: str) -> str:
        """
        Construct the full experiment-specific directory path based on configuration.
        Since base_output_dir already contains the hierarchical structure (dataset_name/num_shots/seed),
        we only need to add the LLM model folder.
        
        Args:
            base_output_dir: The base directory where experiment outputs are stored (already hierarchical).
            
        Returns:
            str: The full path to the experiment-specific directory.
        """
        # Get LLM configuration for the model-specific folder
        llm_config = self.config.get("llm_config", {})
        llm_model_name = llm_config.get("model_name", "unknown_model")
        
        # Sanitize model name for use in file paths
        llm_model_name = llm_model_name.replace("/", "_").replace("\\", "_")
        
        # For basic discovery, we don't have max_iterations, so use a default marker
        max_iter_str = self.discovery_method
        
        # Create experiment-specific folder name
        experiment_folder_name = f"{llm_model_name}_{max_iter_str}"
        
        # Construct the final path by adding only the LLM model folder
        # base_output_dir is already: results/dataset_name/num_shots/seed/
        # Final path will be: results/dataset_name/num_shots/seed/llm_model_basic/
        experiment_dir_path = os.path.join(base_output_dir, experiment_folder_name)
        
        return experiment_dir_path

    def generate_simple_relationships_text(self, graph: StructureGraph) -> str:
        """
        Generate a simple text format containing only the causal relationships.
        
        Args:
            graph: CausalGraph to extract relationships from
            
        Returns:
            String containing the simple relationships format
        """
        edges = graph.get_edges()

        text = "Identified Causal Relationships:\n"

        # Sort edges by source variable for consistent output
        edges_sorted = sorted(edges, key=lambda x: (x["from"], x["to"]))

        for i, edge in enumerate(edges_sorted, 1):
            # Format: 1. A -> B
            text += f"{i}. {edge['from']} -> {edge['to']}\n"
            text += f"Confidence: {edge['confidence']}\n"
            text += f"Association Value: {edge['association_value']}\n"
            text += f"Reasoning: {edge.get('reasoning', 'No reasoning provided')}\n"

            # Add blank line between relationships except for the last one
            if i < len(edges_sorted):
                text += "\n"

        # If no relationships found
        if not edges:
            text += "No causal relationships identified in this graph.\n"

        return text

    def run_discovery_pipeline(self) -> Tuple[StructureGraph, Dict[str, Any]]:
        """
        Main entry point for the BFS-based discovery pipeline.

        Returns:
            A tuple containing the final causal graph and a report dictionary.
        """
        # Step 1: Load data and initialize structures
        print("Starting discovery pipeline...")
        self.load_data()
        if not self.variables or not self.variable_details:
            raise RuntimeError("Data loading failed, cannot proceed with discovery.")

        start_time = time.time()

        # Step 2: Run the specific discovery method (e.g., _bfs_discovery)
        # This method must be implemented by a subclass (like BfsLLMCausalDiscovery)
        final_graph = self._bfs_discovery()

        end_time = time.time()
        duration = end_time - start_time
        print(f"Discovery process finished in {duration:.2f} seconds.")

        # Step 3: Generate a report
        print("Generating final report...")
        report = self._generate_final_report(final_graph, duration)

        # Step 4: Save all results
        print("Saving results...")
        self._save_results(final_graph, report)

        return final_graph, report

    def _bfs_discovery(self) -> StructureGraph:
        """
        Placeholder for the BFS discovery logic. Subclasses must implement this.
        """
        raise NotImplementedError("Subclasses must implement the _bfs_discovery method.")

    def _generate_final_report(self, final_graph: StructureGraph, duration: float) -> Dict[str, Any]:
        """
        Generates a structured report of the discovery process and its outcome.

        Args:
            final_graph: The final causal graph.
            duration: The total time taken for the discovery process.

        Returns:
            A dictionary containing the structured report.
        """
        report = {
            "experiment_details": {
                "dataset_name": self.config["data_config"].get("dataset_name"),
                "num_shots": self.config["data_config"].get("num_shots"),
                "seed": self.config["data_config"].get("seed"),
                "discovery_method": self.discovery_method,
                "llm_model": self.config.get("llm_config", {}).get("model_name"),
                "duration_seconds": round(duration, 2),
                "output_directory": self.experiment_output_dir,
            },
            "graph_summary": {
                "num_nodes": final_graph.graph.number_of_nodes(),
                "num_edges": final_graph.graph.number_of_edges(),
            },
            "token_usage": self.total_token_usage,
            "causal_relationships": final_graph.get_edges(),
        }
        return report

    def _save_results(self, final_graph: StructureGraph, report: Dict[str, Any]) -> None:
        """
        Saves the final graph, a detailed report in JSON and Markdown, and a visualization.

        Args:
            final_graph: The final CausalGraph object.
            report: The structured report dictionary.
        """
        # Ensure the output directory exists
        os.makedirs(self.experiment_output_dir, exist_ok=True)

        # 1. Save the graph to a JSON file
        graph_path = os.path.join(self.experiment_output_dir, "causal_graph.json")
        graph_dict = final_graph.to_dict(all_variables=self.variables)
        with open(graph_path, 'w') as f:
            json.dump(graph_dict, f, indent=4)
        print(f"Saved final causal graph to: {graph_path}")

        # 2. Save the structured report to a JSON file
        report_json_path = os.path.join(self.experiment_output_dir, "report.json")
        with open(report_json_path, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"Saved detailed report to: {report_json_path}")

        # 3. Save a human-readable report to a Markdown file
        report_md_path = os.path.join(self.experiment_output_dir, "report.md")
        with open(report_md_path, 'w') as f:
            f.write(self._format_report_to_markdown(report))
        print(f"Saved markdown report to: {report_md_path}")

        # 4. Save a visualization of the graph
        vis_path = os.path.join(self.experiment_output_dir, "causal_graph.png")
        try:
            final_graph.visualize(vis_path)
            print(f"Saved graph visualization to: {vis_path}")
        except Exception as e:
            print(f"Could not save graph visualization: {e}")

    def _format_report_to_markdown(self, report: Dict[str, Any]) -> str:
        """
        Formats the structured report dictionary into a human-readable Markdown string.
        """
        md = f"# Causal Discovery Report\n\n"

        # Experiment Details
        md += "## Experiment Details\n"
        details = report.get("experiment_details", {})
        md += f"- **Dataset**: `{details.get('dataset_name', 'N/A')}`\n"
        md += f"- **Num Shots**: `{details.get('num_shots', 'N/A')}`\n"
        md += f"- **Seed**: `{details.get('seed', 'N/A')}`\n"
        md += f"- **Discovery Method**: `{details.get('discovery_method', 'N/A')}`\n"
        md += f"- **LLM Model**: `{details.get('llm_model', 'N/A')}`\n"
        md += f"- **Duration**: `{details.get('duration_seconds', 0)}` seconds\n"
        md += f"- **Output Directory**: `{details.get('output_directory', 'N/A')}`\n\n"

        # Graph Summary
        md += "## Graph Summary\n"
        summary = report.get("graph_summary", {})
        md += f"- **Number of Variables (Nodes)**: `{summary.get('num_nodes', 0)}`\n"
        md += f"- **Number of Causal Links (Edges)**: `{summary.get('num_edges', 0)}`\n\n"

        # Token Usage
        md += "## LLM Token Usage\n"
        usage = report.get("token_usage", {})
        md += f"- **Prompt Tokens**: `{usage.get('prompt_tokens', 0)}`\n"
        md += f"- **Completion Tokens**: `{usage.get('completion_tokens', 0)}`\n"
        md += f"- **Estimated Cost**: `${usage.get('total_cost', 0):.4f}`\n\n"

        # Causal Relationships
        md += "## Causal Relationships\n"
        relationships = report.get("causal_relationships", [])
        if not relationships:
            md += "No causal relationships were discovered.\n"
        else:
            for edge in sorted(relationships, key=lambda x: (x['from'], x['to'])):
                md += f"- **`{edge['from']}`** -> **`{edge['to']}`**\n"
                md += f"  - **Confidence**: {edge.get('confidence', 'N/A')}\n"
                md += f"  - **Reasoning**: {edge.get('reason', 'N/A')}\n"
                md += f"  - **Basis**: {edge.get('basis', 'N/A')}\n"
                md += f"  - **Association**: {edge.get('association_value', 'N/A'):.4f}\n"
        md += "\n"

        return md 