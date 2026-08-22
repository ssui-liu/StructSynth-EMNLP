from typing import Dict, List, Any, Optional, Tuple, Set
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


class StructureGraph:
    """
    Class for managing causal graphs
    """
    def __init__(self):
        """
        Initialize an empty causal graph
        """
        # Using networkx DiGraph to represent the causal structure
        self.graph = nx.DiGraph()
        
    def add_edge(self, source: str, target: str,
                 confidence: str = "Low",
                 basis: str = "Knowledge",
                 reason: str = "No specific reason provided",
                 association_value: int = np.nan,
                 ) -> None:
        """
        Add a directed edge to the graph with annotations
        
        Args:
            source: Source node (variable)
            target: Target node (variable)
            confidence: Confidence level (High/Medium/Low)
            basis: Basis for the edge (Knowledge, Knowledge+WeakDataSupport, etc.)
            reason: Reason for the edge (optional)
        """
        # Add nodes if they don't exist
        if source not in self.graph.nodes:
            self.graph.add_node(source)
        if target not in self.graph.nodes:
            self.graph.add_node(target)
            
        # Add the edge with annotations
        self.graph.add_edge(source, target,
                            association_value=association_value,
                            confidence=confidence,
                            basis=basis,
                            reasoning=reason
                            )
    
    def remove_edge(self, source: str, target: str) -> None:
        """
        Remove an edge from the graph
        
        Args:
            source: Source node (variable)
            target: Target node (variable)
        """
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
    
    def has_cycle_if_edge_added(self, u: str, v: str) -> bool:
        """
        Check if adding a directed edge from u to v would create a cycle.

        Args:
            u: The source node.
            v: The target node.

        Returns:
            True if a cycle would be created, False otherwise.
        """
        # A self-loop is the simplest cycle.
        if u == v:
            return True

        # If v is an ancestor of u, adding u -> v creates a cycle.
        # We can check this by seeing if there is a path from v to u.
        if self.graph.has_node(u) and self.graph.has_node(v):
            if nx.has_path(self.graph, v, u):
                return True
        
        return False


    def has_cycles(self) -> bool:
        """
        Check if the graph has cycles
        
        Returns:
            True if the graph has cycles, False otherwise
        """
        return not nx.is_directed_acyclic_graph(self.graph)

    
    def get_edges(self) -> List[Dict[str, Any]]:
        """
        Get all edges with their annotations
        
        Returns:
            List of edge dictionaries with source, target, and annotations
        """
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "from": source,
                "to": target,
                "confidence": data.get("confidence", "Low"),
                "basis": data.get("basis", "Knowledge"),
                "reasoning": data.get("reasoning", "No specific reason provided (get_edges)"),
                "association_value": data.get("association_value", np.nan),
            })
        return edges
    
    def visualize(self, save_path: Optional[str] = None) -> None:
        """
        Visualize the causal graph
        
        Args:
            save_path: Optional path to save the visualization
        """
        # Mock implementation - in real code, would create a nice visualization
        # Create color map based on confidence
        edge_colors = []
        for _, _, data in self.graph.edges(data=True):
            confidence = data.get("confidence", "Low")
            if confidence == "High":
                edge_colors.append("green")
            elif confidence == "Medium":
                edge_colors.append("orange")
            else:
                edge_colors.append("red")
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color="lightblue", 
                node_size=500, font_size=10, font_weight="bold",
                edge_color=edge_colors, width=2, arrows=True)
        
        if save_path:
            plt.savefig(save_path)
        plt.close()
    
    def calculate_hierarchical_structure(self, all_variables: List[str]) -> Dict[str, Any]:
        """
        Calculate a comprehensive hierarchical structure for all variables in the graph.
        This structure is designed to facilitate hierarchical data generation where
        feature generation depends on parent features.
        
        Args:
            all_variables: Complete list of variables from the dataset
            
        Returns:
            Dictionary containing hierarchical structure information
        """
        # Initialize the structure
        hierarchy_info = {
            "variable_info": {},
            "levels": {},
            "generation_order": [],
            "max_depth": 0
        }
        
        # Get all nodes that are actually in the graph (have edges)
        graph_nodes = set(self.graph.nodes())
        
        # Initialize variable info for all variables
        for variable in all_variables:
            hierarchy_info["variable_info"][variable] = {
                "level": None,
                "parents": [],
                "children": [],
                "ancestors": set(),
                "descendants": set(),
                "in_graph": variable in graph_nodes
            }
        
        # Calculate direct relationships for nodes in the graph
        for node in graph_nodes:
            # Get direct parents and children
            parents = list(self.graph.predecessors(node))
            children = list(self.graph.successors(node))
            
            hierarchy_info["variable_info"][node]["parents"] = parents
            hierarchy_info["variable_info"][node]["children"] = children
        
        # Calculate levels using topological ordering
        if graph_nodes:
            # Find root nodes (no incoming edges)
            root_nodes = [node for node in graph_nodes if self.graph.in_degree(node) == 0]
            
            # If no root nodes (cycle), use nodes with minimum in-degree
            if not root_nodes:
                min_in_degree = min(self.graph.in_degree(node) for node in graph_nodes)
                root_nodes = [node for node in graph_nodes if self.graph.in_degree(node) == min_in_degree]
            
            # BFS to assign levels
            from collections import deque
            queue = deque([(node, 0) for node in root_nodes])
            visited = set()
            
            while queue:
                node, level = queue.popleft()
                
                if node in visited:
                    continue
                visited.add(node)
                
                # Update level (take maximum if node has multiple paths)
                current_level = hierarchy_info["variable_info"][node]["level"]
                if current_level is None or level > current_level:
                    hierarchy_info["variable_info"][node]["level"] = level
                    hierarchy_info["max_depth"] = max(hierarchy_info["max_depth"], level)
                
                # Add children to queue
                for child in self.graph.successors(node):
                    if child not in visited:
                        queue.append((child, level + 1))
        
        # Calculate ancestors and descendants for each node
        for node in graph_nodes:
            self._calculate_ancestors_descendants(node, hierarchy_info["variable_info"])
        
        # Group variables by level
        for variable, info in hierarchy_info["variable_info"].items():
            level = info["level"]
            if level is not None:
                if level not in hierarchy_info["levels"]:
                    hierarchy_info["levels"][level] = []
                hierarchy_info["levels"][level].append(variable)
            else:
                # Variables not in graph go to "others"
                if "others" not in hierarchy_info["levels"]:
                    hierarchy_info["levels"]["others"] = []
                hierarchy_info["levels"]["others"].append(variable)
        
        # Calculate generation order (topological sort)
        hierarchy_info["generation_order"] = self._calculate_generation_order(graph_nodes)
        
        # Convert sets to lists for JSON serialization
        for variable, info in hierarchy_info["variable_info"].items():
            info["ancestors"] = list(info["ancestors"])
            info["descendants"] = list(info["descendants"])
        
        return hierarchy_info
    
    def _calculate_ancestors_descendants(self, node: str, variable_info: Dict[str, Dict]) -> None:
        """
        Calculate all ancestors and descendants for a given node using DFS.
        
        Args:
            node: The node to calculate ancestors/descendants for
            variable_info: Dictionary containing variable information
        """
        # Calculate ancestors
        ancestors = set()
        
        def dfs_ancestors(current_node):
            for parent in variable_info[current_node]["parents"]:
                if parent not in ancestors:
                    ancestors.add(parent)
                    dfs_ancestors(parent)
        
        dfs_ancestors(node)
        variable_info[node]["ancestors"] = ancestors
        
        # Calculate descendants
        descendants = set()
        
        def dfs_descendants(current_node):
            for child in variable_info[current_node]["children"]:
                if child not in descendants:
                    descendants.add(child)
                    dfs_descendants(child)
        
        dfs_descendants(node)
        variable_info[node]["descendants"] = descendants
    
    def _calculate_generation_order(self, graph_nodes: Set[str]) -> List[str]:
        """
        Calculate the order in which variables should be generated to respect dependencies.
        Uses topological sorting.
        
        Args:
            graph_nodes: Set of nodes in the graph
            
        Returns:
            List of nodes in generation order
        """
        try:
            # Use NetworkX topological sort
            import networkx as nx
            topo_order = list(nx.topological_sort(self.graph))
            return topo_order
        except nx.NetworkXError:
            # If graph has cycles, return a best-effort ordering
            # Start with nodes that have no incoming edges
            remaining_nodes = set(graph_nodes)
            generation_order = []
            
            while remaining_nodes:
                # Find nodes with no incoming edges from remaining nodes
                available_nodes = []
                for node in remaining_nodes:
                    parents_in_remaining = [p for p in self.graph.predecessors(node) if p in remaining_nodes]
                    if not parents_in_remaining:
                        available_nodes.append(node)
                
                if not available_nodes:
                    # Break cycles by taking any remaining node
                    available_nodes = [next(iter(remaining_nodes))]
                
                # Sort for consistency
                available_nodes.sort()
                generation_order.extend(available_nodes)
                remaining_nodes -= set(available_nodes)
            
            return generation_order
    
    def to_dict(self, all_variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Convert the graph to a dictionary representation with hierarchy levels
        
        Args:
            all_variables: Complete list of variables to calculate hierarchy for
            
        Returns:
            Dictionary representation of the graph including hierarchy levels
        """
        result = {
            "nodes": list(self.graph.nodes()),
            "edges": self.get_edges(),
        }
        
        # Add hierarchy levels if all_variables is provided
        if all_variables:
            hierarchy = self.calculate_hierarchical_structure(all_variables)
            result["hierarchical_structure"] = hierarchy
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructureGraph':
        """
        Create a graph from a dictionary representation
        
        Args:
            data: Dictionary representation of the graph
            
        Returns:
            CausalGraph instance
        """
        graph = cls()
        
        for edge in data.get("edges", []):
            graph.add_edge(
                edge["from"], 
                edge["to"], 
                edge.get("confidence", "Low"),
                edge.get("basis", "Knowledge"),
                edge.get("reasoning", "No specific reason provided (from_dict)"),
                edge.get("association_value", np.nan)
            )
        
        return graph 