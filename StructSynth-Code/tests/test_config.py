from dataclasses import asdict
from pathlib import Path

import pytest
import yaml

from structsynth.config import LLMConfig, load_config


def test_paths_follow_config_not_cwd(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config = config_dir / "experiment.yaml"
    config.write_text(yaml.safe_dump({"data": {"name": "toy", "path": "../toy.csv", "metadata": "meta.json"},
                                     "output_dir": "../out"}))
    monkeypatch.chdir(tmp_path.parent)
    loaded = load_config(config)
    assert loaded.data.path == str(tmp_path / "toy.csv")
    assert loaded.data.metadata == str(config_dir / "meta.json")
    assert loaded.output_dir == str(tmp_path / "out")


@pytest.mark.parametrize("section", [{"unexpected": 1}, {"shots": []}, {"seeds": [42, 42]},
                                     {"test_size": 1}, {"shots": [True]}, {"example_rows": 0}])
def test_reject_invalid_data_config(tmp_path, section):
    config = tmp_path / "bad.yaml"
    config.write_text(yaml.safe_dump({"data": {"name": "toy", "path": "x", "metadata": "m", **section}}))
    with pytest.raises(ValueError):
        load_config(config)


def test_checked_in_paper_config_loads():
    config = load_config(Path(__file__).parents[1] / "configs/adult.yaml")
    assert config.data.seeds == list(range(42, 52))
    assert config.data.shots == [100]
    assert config.evaluation.protocol == "augmentation"
    assert config.discovery_llm.max_tokens == 8000
    assert config.discovery_llm.temperature == 0.9
    assert Path(config.data.path).is_file()
    assert "api_key" not in asdict(config.discovery_llm)


@pytest.mark.parametrize("url", ["http://localhost.evil.example", "ftp://example.org", "https://key@example.org", "https://example.org/?key=secret"])
def test_endpoint_validation(url):
    with pytest.raises(ValueError):
        LLMConfig(base_url=url)
