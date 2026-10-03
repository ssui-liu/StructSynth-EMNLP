import json

import pytest

from structsynth.graph import DependencyGraph


def edge(source, target):
    return {"from": source, "to": target, "reasoning": "dependency"}


def test_longest_path_not_bfs_distance_controls_generation():
    graph = DependencyGraph(["A", "B", "C"], ["A", "B", "C"], [edge("A", "B"), edge("A", "C"), edge("B", "C")])
    assert graph.layers() == [["A"], ["B"], ["C"]]
    levels = {node: index for index, layer in enumerate(graph.layers()) for node in layer}
    assert all(levels[e["from"]] < levels[e["to"]] for e in graph.edges)


def test_selected_edgeless_nodes_are_not_outside_graph_columns():
    graph = DependencyGraph(["A", "B", "C", "D"], ["C", "A", "B"], [edge("A", "B")])
    assert graph.nodes == ["A", "B", "C"]
    assert graph.layers() == [["A", "C"], ["B"]]
    assert graph.isolated_columns == ["D"]
    assert graph.parents("C") == []


def test_empty_selected_graph_is_a_valid_all_completion_plan():
    graph = DependencyGraph(["A", "B"], [], [])
    assert graph.layers() == []
    assert graph.isolated_columns == ["A", "B"]


def test_local_subgraph_is_induced_and_keeps_parent_to_parent_edges():
    graph = DependencyGraph(["A", "B", "C", "D"], ["A", "B", "C", "D"], [edge("A", "B"), edge("A", "C"), edge("B", "C"), edge("A", "D")])
    local = graph.local_subgraph(["C"])
    assert local["nodes"] == ["A", "B", "C"]
    assert local["edges"] == [edge("A", "B"), edge("A", "C"), edge("B", "C")]
    assert graph.parents("C") == ["A", "B"]


def test_serialization_keeps_nodes_without_edges_and_ignores_stale_hierarchy():
    graph = DependencyGraph(["A", "B", "C"], ["B", "A"], [edge("A", "B")])
    payload = json.loads(json.dumps(graph.to_dict(), allow_nan=False))
    payload["layers"] = [["B"], ["A"]]
    payload["hierarchical_structure"] = {"levels": {"0": ["A", "B", "C"]}}
    restored = DependencyGraph.from_dict(payload)
    assert restored.layers() == [["A"], ["B"]]
    assert restored.isolated_columns == ["C"]
    singleton = DependencyGraph.from_dict({"nodes": ["A"], "edges": []}, columns=["A", "B"])
    assert singleton.nodes == ["A"]
    assert singleton.isolated_columns == ["B"]


@pytest.mark.parametrize(
    "columns,nodes,edges,match",
    [
        (["A", "B"], ["A", "B"], [edge("A", "B"), edge("B", "A")], "acyclic"),
        (["A"], ["A"], [edge("A", "A")], "Self dependency"),
        (["A", "B"], ["A"], [edge("A", "B")], "outside selected"),
        (["A"], ["unknown"], [], "unknown"),
        (["A", "A"], ["A"], [], "duplicate"),
        (["A", "B"], ["A", "B"], [edge("A", "B"), edge("A", "B")], "Duplicate dependency"),
    ],
)
def test_invalid_graphs_are_rejected_before_synthesis(columns, nodes, edges, match):
    with pytest.raises(ValueError, match=match):
        DependencyGraph(columns, nodes, edges)


def test_changed_public_edge_lists_cannot_bypass_dag_validation():
    graph = DependencyGraph(["A", "B"], ["A", "B"], [edge("A", "B")])
    graph.edges.append(edge("B", "A"))
    with pytest.raises(ValueError, match="acyclic"):
        graph.layers()


def test_order_uses_dataset_schema_independently_of_insertion_order():
    graph = DependencyGraph(["D", "C", "B", "A"], ["A", "B", "C", "D"], [edge("B", "C"), edge("A", "C")])
    assert graph.layers() == [["D", "B", "A"], ["C"]]
    assert graph.parents("C") == ["B", "A"]
