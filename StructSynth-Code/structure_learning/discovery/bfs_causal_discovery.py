import collections
import os
import time
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from tqdm import tqdm
import networkx as nx

from ..data.data_loader import DataLoader
from ..llm.llm_interface import LLMInterface, Effect
from ..graph.structure_graph import StructureGraph
from .basic_causal_discovery import BasicLLMCausalDiscovery

class BfsLLMCausalDiscovery(BasicLLMCausalDiscovery):
    """
    Implements a Breadth-First Search (BFS) based causal discovery method.

    This method treats Large Language Model (LLM) queries as node expansions
    in a BFS process to build a Directed Acyclic Graph (DAG).
    """

    def __init__(self, config: Dict[str, Any], data_loader: DataLoader, discovery_method: str = "bfs"):
        """
        Initializes the BFS causal discovery process.
        """
        super().__init__(config, data_loader, discovery_method)
        # BFS specific attributes can be initialized here if needed


    def _validate_llm_variables(self, llm_variable_list: List[str], context_node: Optional[str] = None) -> List[str]:
        """
        Validates the list of variables returned by the LLM.

        This function ensures that each variable name exists in the dataset's master
        list of variables, filtering out any hallucinated or invalid names. It also
        handles cases where the LLM's output is not a list.

        Args:
            llm_variable_list: The list of variable names from the LLM.
            context_node: The source node for which we are validating effects (for logging).

        Returns:
            A cleaned list containing only valid variables.
        """
        if not isinstance(llm_variable_list, list):
            context_str = f"for node '{context_node}'" if context_node else "for root causes"
            print(f"Warning: LLM output {context_str} was not a list, but {type(llm_variable_list)}. Ignoring.")
            return []

        valid_variables = []
        for var in llm_variable_list:
            if var in self.variables:
                valid_variables.append(var)
            else:
                context_str = f"for node '{context_node}'" if context_node else "as a root cause"
                print(f"Warning: LLM suggested a non-existent variable '{var}' {context_str}. It will be ignored.")
        
        return valid_variables

    def _bfs_discovery(self) -> StructureGraph:
        """
        Performs the core BFS-based causal discovery.

        Returns:
            The constructed causal graph.
        """
        # Step 1: Initialization
        print("Step 1: Initializing BFS - Identifying root causes...")
        graph = StructureGraph()
        for var in self.variables:
            graph.graph.add_node(var)

        llm_root_causes, usage = self.llm.identify_root_causes(self.variable_details)
        self._update_token_usage(usage)
        
        # Since root causes don't have confidence/reasoning, we use the old validator
        root_causes = self._validate_llm_variables(llm_root_causes)
        print(f"Identified and validated root causes: {root_causes}")

        queue = collections.deque(root_causes)
        visited = set(root_causes)

        # Main BFS loop
        pbar = tqdm(total=len(self.variables), desc="BFS Discovery Progress")
        
        while queue:
            # Step 2: Expansion
            current_node = queue.popleft()
            pbar.set_postfix_str(f"Expanding: {current_node}")

            # Prepare current graph context for the prompt
            current_graph_str = self.generate_simple_relationships_text(graph)

            # Prepare correlation information for the prompt
            correlation_info_str = "Correlations with the source variable:\\n"
            if self.associations is not None and not self.associations.empty:
                try:
                    # Get correlations for the current node, excluding itself
                    if current_node in self.associations.index and current_node in self.associations.columns:
                        correlations = self.associations[current_node].drop(current_node)
                        for var, corr_val in correlations.items():
                            correlation_info_str += f"- {var}: {corr_val:.4f}\\n"
                    else:
                        correlation_info_str += f"'{current_node}' not found in correlation matrix.\\n"
                except (KeyError, AttributeError) as e:
                    print(f"Could not retrieve correlations for {current_node}: {e}")
                    correlation_info_str += "Not available.\\n"
            else:
                correlation_info_str += "Correlation matrix not available or empty.\\n"

            # Query for effects
            print(f"Step 2: Expanding '{current_node}' to find its direct effects...")
            llm_effects, usage = self.llm.identify_direct_effects(
                current_node, self.variable_details, current_graph_str, correlation_info_str
            )
            self._update_token_usage(usage)
            
            # Step 3: Insertion
            if not isinstance(llm_effects, list):
                print(f"Warning: LLM output for '{current_node}' was not a list, but {type(llm_effects)}. Ignoring.")
                llm_effects = []

            for effect in llm_effects:
                try:
                    child_node = effect.variable
                    if child_node not in self.variables:
                        print(f"Warning: LLM suggested a non-existent variable '{child_node}'. Skipping.")
                        continue

                    # Add child to queue if not visited
                    if child_node not in visited:
                        queue.append(child_node)
                        visited.add(child_node)
                        print(f"'{child_node}' added to the queue.")

                    # Get the association value for this specific pair
                    association_value = np.nan
                    if self.associations is not None and not self.associations.empty:
                        association_value = self.associations.loc[current_node, child_node]

                    # --- New Cycle Resolution Logic ---
                    if graph.has_cycle_if_edge_added(current_node, child_node):
                        print(f"Potential cycle detected by adding edge {current_node} -> {child_node}. Involving LLM to resolve.")

                        # Find the path that would form the cycle
                        path = list(nx.shortest_path(graph.graph, source=child_node, target=current_node))
                        cycle_edges_list = []
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i+1]
                            edge_data = graph.graph.get_edge_data(u, v)
                            cycle_edges_list.append({
                                'from': u,
                                'to': v,
                                'confidence': edge_data.get('confidence', 'Unknown'),
                                'reasoning': edge_data.get('reasoning', 'No reasoning provided.')
                            })
                        
                        # Add the new edge to the list for the LLM to consider
                        new_edge_info = {
                            'from': current_node,
                            'to': child_node,
                            'confidence': effect.confidence.value,
                            'reasoning': effect.reasoning
                        }
                        
                        # Let the LLM decide which edge to remove
                        edge_to_remove_src, edge_to_remove_tgt, usage = self.llm.resolve_cycle_conflict(
                            cycle_edges=cycle_edges_list,
                            new_edge=new_edge_info,
                        )
                        self._update_token_usage(usage)

                        # Update the graph
                        if edge_to_remove_src == current_node and edge_to_remove_tgt == child_node:
                            print(f"LLM decided not to add the new edge {current_node} -> {child_node} to resolve the cycle.")
                        else:
                            print(f"LLM decided to remove edge {edge_to_remove_src} -> {edge_to_remove_tgt} to resolve cycle.")
                            graph.remove_edge(edge_to_remove_src, edge_to_remove_tgt)
                            graph.add_edge(
                                source=current_node,
                                target=child_node,
                                confidence=effect.confidence.value,
                                basis="LLM-BFS-Resolved",
                                reason=effect.reasoning,
                                association_value=association_value
                            )
                    else:
                        # No cycle, add the edge directly
                        graph.add_edge(
                            source=current_node,
                            target=child_node,
                            confidence=effect.confidence.value,
                            basis="LLM-BFS",
                            reason=effect.reasoning,
                            association_value=association_value
                        )

                except (AttributeError, KeyError) as e:
                    print(f"Warning: Could not process a malformed effect object from LLM: {effect}. Error: {e}. Skipping.")
                    continue
            
            pbar.update(1)

        pbar.close()
        # Ensure all nodes are covered even if disconnected
        remaining_nodes = set(self.variables) - visited
        if remaining_nodes:
            print(f"Warning: The following nodes were not reached by BFS: {remaining_nodes}. They will be disconnected in the graph.")

        return graph