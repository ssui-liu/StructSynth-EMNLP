from dataclasses import asdict
from pathlib import Path

import pytest
import yaml

from structsynth.config import (DataConfig, EvaluationConfig, ExperimentConfig, GenerationConfig,
                               LLMConfig, load_config)


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


@pytest.mark.parametrize("field", ["temperature", "top_p", "frequency_penalty", "presence_penalty", "timeout", "retry_delay"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), True, "0.5"])
def test_llm_numeric_settings_reject_nonfinite_and_coercible_non_numbers(field, value):
    # These values previously reached JSON/HTTP or retry sleep as malformed
    # requests; validation is now independent of credentials and transport.
    with pytest.raises(ValueError, match="finite number"):
        LLMConfig(**{field: value})


@pytest.mark.parametrize("changes", [
    {"model": 7}, {"model": " "}, {"api_key_env": []}, {"api_key_env": "KEY=value"},
    {"json_mode": "false"}, {"json_mode": 0}, {"frequency_penalty": 2.1},
    {"presence_penalty": -2.1}, {"timeout": 0}, {"retry_delay": -1},
])
def test_llm_configuration_rejects_settings_that_would_change_request_meaning(changes):
    with pytest.raises(ValueError):
        LLMConfig(**changes)


@pytest.mark.parametrize("url", [
    1, "https://example.org:bad", "https://example.org:65536", "https://example.org:0",
    "https://example.org/\napi", "https://[invalid",
])
def test_malformed_endpoint_fails_during_configuration(url):
    with pytest.raises(ValueError):
        LLMConfig(base_url=url)


def test_valid_local_ipv6_endpoint_and_boundary_parameters_remain_supported():
    config = LLMConfig(base_url="http://[::1]:8080/v1", temperature=0, top_p=1,
                       frequency_penalty=-2, presence_penalty=2, retry_delay=0, json_mode=False)
    assert config.base_url == "http://[::1]:8080/v1"
    assert not config.json_mode


@pytest.mark.parametrize("changes", [
    {"seeds": [2 ** 32]}, {"seeds": [-1]}, {"seeds": [True]}, {"seeds": [[42]]},
    {"shots": [[100]]}, {"test_size": float("nan")}, {"test_size": "0.2"},
    {"target_column": 1}, {"name": 1}, {"path": 1}, {"task_type": []},
])
def test_data_configuration_rejects_invalid_types_and_sklearn_seed_range(changes):
    values = {"name": "toy", "path": "data.csv", "metadata": "meta.json", **changes}
    with pytest.raises(ValueError):
        DataConfig(**values)


def test_seed_endpoints_and_programmatic_path_objects_remain_supported(tmp_path):
    data = DataConfig("toy", tmp_path / "data.csv", tmp_path / "meta.json", seeds=[0, 2 ** 32 - 1])
    config = ExperimentConfig(data, output_dir=tmp_path / "runs")
    assert isinstance(data.path, str)
    assert config.output_dir == str(tmp_path / "runs")


@pytest.mark.parametrize("values", [[[1]], [True], [2, 2], "100"])
def test_generation_sample_counts_raise_clear_configuration_errors(values):
    with pytest.raises(ValueError):
        GenerationConfig(n_samples=values)


@pytest.mark.parametrize("params", [
    {"alpha": float("nan")}, {"nested": {"value": float("inf")}},
    {1: "invalid-key"}, {"alpha": {1, 2}},
])
def test_evaluation_parameters_must_have_finite_persistable_values(params):
    with pytest.raises(ValueError):
        EvaluationConfig(model_params=params)


def test_programmatic_estimator_tuple_and_json_settings_remain_supported():
    params = {"hidden_layer_sizes": (32, 16), "early_stopping": True, "activation": "relu", "max_fun": 1000}
    assert EvaluationConfig(model="mlp", model_params=params).model_params == params


def test_experiment_rejects_boolean_version_and_unconstructed_sections():
    data = DataConfig("toy", "data.csv", "meta.json")
    with pytest.raises(ValueError, match="version"):
        ExperimentConfig(data, version=True)
    with pytest.raises(ValueError, match="DataConfig"):
        ExperimentConfig({"name": "toy"})
    with pytest.raises(ValueError, match="LLMConfig"):
        ExperimentConfig(data, discovery_llm={})


def test_yaml_numeric_field_names_fail_with_clear_error(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("data:\n  name: toy\n  path: x\n  metadata: m\n  1: unexpected\n")
    with pytest.raises(ValueError, match="field names must be strings"):
        load_config(path)
