"""One validated configuration for the complete experiment."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

import yaml


def _positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


@dataclass
class DataConfig:
    name: str
    path: str
    metadata: str
    task_type: Optional[str] = None
    target_column: Optional[str] = None
    cleaning: str = "none"
    shots: list[int] = field(default_factory=lambda: [100])
    seeds: list[int] = field(default_factory=lambda: list(range(42, 52)))
    test_size: float = 0.2
    example_rows: int = 20

    def __post_init__(self):
        if not self.name or not self.path or not self.metadata:
            raise ValueError("data.name, path and metadata are required")
        if self.task_type not in {None, "classification", "regression"}:
            raise ValueError("Unknown data.task_type")
        if not 0 < self.test_size < 1:
            raise ValueError("data.test_size must lie in (0, 1)")
        for key in ("shots", "seeds"):
            values = getattr(self, key)
            if not isinstance(values, list) or not values or len(set(values)) != len(values):
                raise ValueError(f"data.{key} must be a nonempty list of unique integers")
            if any(isinstance(v, bool) or not isinstance(v, int) or v < (1 if key == "shots" else 0) for v in values):
                raise ValueError(f"Invalid data.{key}")
        _positive_int(self.example_rows, "data.example_rows")


@dataclass
class LLMConfig:
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    api_key_env: str = "OPENAI_API_KEY"
    temperature: float = 0.9
    top_p: float = 0.95
    max_tokens: int = 8000
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: float = 60.0
    max_attempts: int = 3
    retry_delay: float = 1.0
    request_limit: int = 2000
    token_limit: Optional[int] = None
    json_mode: bool = True

    def __post_init__(self):
        if not self.model or not self.api_key_env:
            raise ValueError("LLM model and api_key_env must be nonempty")
        endpoint = urlsplit(self.base_url)
        if (not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment
                or not (endpoint.scheme == "https" or
                        (endpoint.scheme == "http" and endpoint.hostname in {"localhost", "127.0.0.1", "::1"}))):
            raise ValueError("Use HTTPS or a local HTTP model endpoint")
        if not 0 <= self.temperature <= 2 or not 0 < self.top_p <= 1:
            raise ValueError("Invalid LLM temperature or top_p")
        if self.timeout <= 0 or self.retry_delay < 0:
            raise ValueError("Invalid timeout/retry_delay")
        for key in ("max_tokens", "max_attempts", "request_limit"):
            _positive_int(getattr(self, key), f"llm.{key}")
        if self.token_limit is not None:
            _positive_int(self.token_limit, "llm.token_limit")


@dataclass
class GenerationConfig:
    n_samples: list[int] = field(default_factory=lambda: [100, 200, 500, 1000])
    batch_size: int = 10
    max_attempts: int = 5
    max_workers: int = 1

    def __post_init__(self):
        if not isinstance(self.n_samples, list) or not self.n_samples or len(set(self.n_samples)) != len(self.n_samples):
            raise ValueError("generation.n_samples must be a nonempty list of unique sample counts")
        for n in self.n_samples:
            _positive_int(n, "generation.n_samples")
        for key in ("batch_size", "max_attempts", "max_workers"):
            _positive_int(getattr(self, key), f"generation.{key}")


@dataclass
class EvaluationConfig:
    enabled: bool = True
    protocol: str = "augmentation"
    model: str = "xgboost"
    model_params: dict[str, Any] = field(default_factory=dict)
    numeric_scaling: str = "none"
    fidelity_reference: str = "train_test"

    def __post_init__(self):
        if self.protocol not in {"augmentation", "synthetic_only", "real_only"}:
            raise ValueError("Unknown evaluation.protocol")
        if self.numeric_scaling not in {"none", "train_range"}:
            raise ValueError("Unknown evaluation.numeric_scaling")
        if self.fidelity_reference not in {"train_test", "test", "train"}:
            raise ValueError("Unknown evaluation.fidelity_reference")


@dataclass
class ExperimentConfig:
    data: DataConfig
    discovery_llm: LLMConfig = field(default_factory=LLMConfig)
    generation_llm: LLMConfig = field(default_factory=LLMConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output_dir: str = "runs"
    discovery_attempts: int = 3
    max_cycles: int = 1000
    version: int = 1

    def __post_init__(self):
        if self.version != 1:
            raise ValueError("Unsupported configuration version")
        _positive_int(self.discovery_attempts, "discovery_attempts")
        _positive_int(self.max_cycles, "max_cycles")
        if not self.output_dir:
            raise ValueError("output_dir must be nonempty")

    def to_dict(self):
        return asdict(self)


def _construct(cls, values, section):
    if not isinstance(values, dict):
        raise ValueError(f"{section} must be a mapping")
    unknown = set(values) - {f.name for f in fields(cls)}
    if unknown:
        raise ValueError(f"Unknown {section} fields: {sorted(unknown)}")
    try:
        return cls(**values)
    except TypeError as exc:
        raise ValueError(f"Invalid {section}: {exc}") from exc


def load_config(path: str | Path) -> ExperimentConfig:
    path = Path(path).resolve()
    with path.open(encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict) or "data" not in raw:
        raise ValueError("Configuration must contain a data mapping")
    raw = dict(raw)
    for key, cls in (("data", DataConfig), ("discovery_llm", LLMConfig), ("generation_llm", LLMConfig),
                     ("generation", GenerationConfig), ("evaluation", EvaluationConfig)):
        raw[key] = _construct(cls, raw.get(key, {}), key)
    config = _construct(ExperimentConfig, raw, "experiment")
    # Every path is relative to the config file, never the invoking shell.
    for name in ("path", "metadata"):
        value = Path(getattr(config.data, name)).expanduser()
        setattr(config.data, name, str((path.parent / value).resolve()))
    config.output_dir = str((path.parent / Path(config.output_dir).expanduser()).resolve())
    return config
