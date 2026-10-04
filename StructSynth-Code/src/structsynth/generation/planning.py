"""Translate the validated DAG into graph layers and final completion."""

from __future__ import annotations


def build_stages(graph, columns):
    graph_columns = list(graph.columns)
    if graph_columns != columns:
        raise ValueError("Graph columns must match DatasetSpec columns and order")
    layers = graph.layers()
    graph_nodes = set(graph.nodes)
    if not graph_nodes.issubset(columns):
        raise ValueError("Graph contains unknown dataset columns")
    seen = set()
    stages = []
    for variables in layers:
        variables = list(variables)
        if not variables or len(variables) != len(set(variables)) or seen.intersection(variables):
            raise ValueError("Graph layers must partition nodes without duplicates")
        parents = {parent for variable in variables for parent in graph.parents(variable)}
        if not parents.issubset(seen):
            raise ValueError("A graph parent is not in an earlier generation layer")
        related = set(variables) | parents
        stages.append({"variables": variables, "purpose": "generation.layer",
                       "subgraph": graph.local_subgraph(variables),
                       "example_columns": [column for column in columns if column in related]})
        seen.update(variables)
    if seen != graph_nodes:
        raise ValueError("Graph layers do not contain exactly the graph nodes")
    isolated = [column for column in columns if column not in graph_nodes]
    if isolated:
        stages.append({"variables": isolated, "purpose": "generation.isolated",
                       "subgraph": {"nodes": [], "edges": []},
                       "example_columns": list(columns)})
    return stages
