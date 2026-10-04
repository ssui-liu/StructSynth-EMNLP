"""Protect experiment identities when code moves into nested packages."""
from structsynth.pipeline import source_fingerprint
from structsynth.pipeline import identity


def test_source_identity_covers_nested_files_and_uses_relative_paths(tmp_path, monkeypatch):
    package = tmp_path / "structsynth"
    (package / "pipeline").mkdir(parents=True)
    (package / "generation").mkdir()
    root_file = package / "__init__.py"
    child_file = package / "generation" / "__init__.py"
    root_file.write_text('VERSION = "test"\n')
    child_file.write_text('PROMPT = "first"\n')
    monkeypatch.setattr(identity, "__file__", str(package / "pipeline" / "identity.py"))
    before = source_fingerprint()
    child_file.write_text('PROMPT = "changed"\n')
    changed = source_fingerprint()
    assert changed != before
    root_file.write_text('VERSION = "new"\n')
    assert source_fingerprint() != changed  # Repeated basenames must not collide.
    before_rename = source_fingerprint()
    child_file.rename(child_file.with_name("prompts.py"))
    assert source_fingerprint() != before_rename
    stable = source_fingerprint()
    (package / "README.md").write_text("Documentation does not change the algorithm.")
    (package / "generation" / "__pycache__").mkdir()
    (package / "generation" / "__pycache__" / "prompts.pyc").write_bytes(b"bytecode")
    assert source_fingerprint() == stable
    relocated = tmp_path / "installed_package"
    package.rename(relocated)
    monkeypatch.setattr(identity, "__file__", str(relocated / "pipeline" / "identity.py"))
    assert source_fingerprint() == stable


def test_graph_compatibility_imports_share_the_canonical_types_and_functions():
    from structsynth.associations import association_score as old_score
    from structsynth.discovery import DiscoveryError as OldError, discover_structure as old_discover
    from structsynth.graph import DependencyGraph as OldGraph
    from structsynth.reporting import summarize_runs as old_summary
    from structsynth.structure import DependencyGraph, DiscoveryError, association_score, discover_structure
    from structsynth.evaluation.reporting import summarize_runs

    assert OldGraph is DependencyGraph
    assert OldError is DiscoveryError
    assert old_score is association_score
    assert old_discover is discover_structure
    assert old_summary is summarize_runs
