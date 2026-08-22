import json
import os
from typing import Dict, List, Any, Optional


class StructureGraphProcessor:
    """
    Handles loading, parsing, and processing of structure graph structures for hierarchical generation.
    This class manages the structure relationships, hierarchical levels, and generation order.
    """
    
    def __init__(self, graph_file: str):
        """
        Initialize the structure graph processor.
        
        Args:
            graph_file: Path to the structure graph JSON file
        """
        self.graph_file = graph_file
        self.hierarchical_structure = None
        self.generation_order = None
        self.levels = None
        self.structure_edges = None
        self.non_structure_variables = None
        
        # Load the graph structure on initialization
        self._load_graph_structure()
    
    def _load_graph_structure(self):
        """Load and parse the hierarchical graph structure from JSON file."""
        try:
            # Handle both absolute and relative paths correctly
            if os.path.isabs(self.graph_file):
                # If it's already an absolute path, use it directly
                graph_path = self.graph_file
            else:
                # If it's a relative path, check if it exists relative to current working directory first
                if os.path.exists(self.graph_file):
                    graph_path = self.graph_file
                else:
                    # Fall back to joining with current file's directory
                    graph_path = os.path.join(os.path.dirname(__file__), self.graph_file)
            
            # Normalize the path to resolve any '..' or '.' components
            graph_path = os.path.normpath(graph_path)
            
            print(f"Attempting to load graph from: {graph_path}")
            
            with open(graph_path, 'r') as f:
                graph_data = json.load(f)
            
            # Extract hierarchical structure components
            self.hierarchical_structure = graph_data.get('hierarchical_structure', {})
            self.generation_order = self.hierarchical_structure.get('generation_order', [])
            self.levels = self.hierarchical_structure.get('levels', {})
            self.structure_edges = graph_data.get('edges', [])
            self.non_structure_variables = self.levels.get('others', [])
            
            print(f"Successfully loaded hierarchical structure with {len(self.generation_order)} structure variables")
            print(f"Generation order: {self.generation_order}")
            print(f"Non-structure variables: {self.non_structure_variables}")
            
        except FileNotFoundError:
            # Provide more helpful error information
            attempted_paths = []
            if os.path.isabs(self.graph_file):
                attempted_paths.append(self.graph_file)
            else:
                attempted_paths.append(self.graph_file)
                attempted_paths.append(os.path.join(os.path.dirname(__file__), self.graph_file))
            
            error_msg = f"Graph file '{self.graph_file}' not found. Attempted paths:\n"
            for path in attempted_paths:
                normalized_path = os.path.normpath(path)
                error_msg += f"  - {normalized_path} (exists: {os.path.exists(normalized_path)})\n"
            
            raise FileNotFoundError(error_msg)
        except Exception as e:
            raise Exception(f"Error loading graph structure from '{graph_path}': {str(e)}")
    
    def get_parent_child_relationships(self) -> Dict[str, List[str]]:
        """
        Extract parent-child relationships from the hierarchical structure.
        
        Returns:
            Dictionary mapping each variable to its list of parent variables
        """
        relationships = {}
        variable_info = self.hierarchical_structure.get('variable_info', {})
        
        for var, info in variable_info.items():
            if info.get('in_graph', False):
                relationships[var] = info.get('parents', [])
        
        return relationships
    
    def get_structure_context_for_level(self, variables: List[str]) -> str:
        """
        Generate structure context description for all variables in a level.
        
        Args:
            variables: List of variables being generated at this level
            
        Returns:
            Formatted structure context string for the entire level
        """
        # Find all edges that lead to variables in this level
        relevant_edges = []
        for variable in variables:
            edges_to_var = [edge for edge in self.structure_edges if edge['to'] == variable]
            relevant_edges.extend(edges_to_var)
        
        if not relevant_edges:
            return ""
        
        # Sort edges by source variable for consistent output
        edges_sorted = sorted(relevant_edges, key=lambda x: (x["from"], x["to"]))
        
        structure_context = "\nSTRUCTURE RELATIONSHIPS FOR THIS LEVEL:\n"
        structure_context += "=" * 45 + "\n"
        
        for i, edge in enumerate(edges_sorted, 1):
            # Format: 1. source -> target
            structure_context += f"{i}. {edge['from']} -> {edge['to']}\n"
            structure_context += f"Confidence: {edge['confidence']}\n"
            structure_context += f"Association Value: {edge['association_value']}\n"
            structure_context += f"Reasoning: {edge.get('reasoning', 'No reasoning provided')}\n"
            
            # Add blank line between relationships except for the last one
            if i < len(edges_sorted):
                structure_context += "\n"
        
        structure_context += "\n" + "=" * 45 + "\n"
        structure_context += "GENERATION INSTRUCTIONS:\n"
        structure_context += f"Generate values for {', '.join(variables)} that are structurally consistent with the above relationships.\n"
        structure_context += "Use the parent variable values provided to inform your generation decisions.\n"
        structure_context += "Maintain realistic distributions while respecting these structural constraints.\n"
        
        return structure_context
    
    def get_structure_context_for_variable(self, variable: str, parent_values: Dict[str, Any]) -> str:
        """
        Generate structure context description for a variable based on its parents' values.
        
        Args:
            variable: Target variable to generate
            parent_values: Dictionary of parent variable names and their generated values
            
        Returns:
            Formatted structure context string
        """
        # Find edges that lead to this variable
        relevant_edges = [edge for edge in self.structure_edges if edge['to'] == variable]
        
        if not relevant_edges or not parent_values:
            return ""
        
        structure_context = f"\nSTRUCTURE CONTEXT FOR {variable.upper()}:\n"
        structure_context += f"Generate '{variable}' values based on the following structural relationships:\n\n"
        
        for edge in relevant_edges:
            parent = edge['from']
            if parent in parent_values:
                structure_context += f"• {parent} → {variable}:\n"
                structure_context += f"  - Confidence: {edge['confidence']}\n"
                structure_context += f"  - Reasoning: {edge['reasoning']}\n"
                structure_context += f"  - Current {parent} value: {parent_values[parent]}\n\n"
        
        structure_context += f"Generate '{variable}' values that are structurally consistent with the above parent values.\n"
        structure_context += "Maintain realistic distributions while respecting these structural relationships.\n"
        
        return structure_context
    
    def generate_simple_relationships_text(self) -> str:
        """
        Generate a simple text format containing all structure relationships in the graph.
        
        Returns:
            String containing the simple relationships format
        """
        edges = self.structure_edges
        
        text = "Identified Structural Relationships:\n"
        text += "=" * 50 + "\n"
        
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
            text += "No structural relationships identified in this graph.\n"
        
        text += "\n" + "=" * 50
        
        return text
    
    def get_max_level(self) -> int:
        """
        Get the maximum level number in the hierarchical structure.
        
        Returns:
            Maximum level number, or -1 if no numeric levels found
        """
        return max([int(k) for k in self.levels.keys() if k.isdigit()] + [-1])
    
    def get_level_variables(self, level: int) -> List[str]:
        """
        Get the variables assigned to a specific level.
        
        Args:
            level: Level number to get variables for
            
        Returns:
            List of variable names for the specified level
        """
        return self.levels.get(str(level), [])
    
    def filter_available_variables(self, variables: List[str], available_columns: List[str]) -> List[str]:
        """
        Filter a list of variables to only include those available in the dataset.
        
        Args:
            variables: List of variable names to filter
            available_columns: List of available column names in the dataset
            
        Returns:
            Filtered list of variables that exist in the dataset
        """
        return [var for var in variables if var in available_columns] 