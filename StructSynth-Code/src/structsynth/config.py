"""One validated configuration for the complete experiment."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
import math
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

import yaml


def _positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _text(value, name, *, path=False):
    if path and isinstance(value, Path):
        value = str(value)
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _finite_number(value, name):
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite number, not a boolean or string")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name} must be a finite number")


def _choice(value, choices, name):
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"Unknown {name}")


def _json_parameters(value, name):
    """Validate serializable estimator settings without importing an evaluator."""
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        _finite_number(value, name)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _json_parameters(item, name)
    elif isinstance(value, dict):
        for key, item in value.items():
            _text(key, f"{name} key")
            _json_parameters(item, f"{name}.{key}")
    else:
        raise ValueError(f"{name} must contain only finite JSON-compatible settings")


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
        self.name = _text(self.name, "data.name")
        self.path = _text(self.path, "data.path", path=True)
        self.metadata = _text(self.metadata, "data.metadata", path=True)
        if self.task_type is not None:
            _choice(self.task_type, {"classification", "regression"}, "data.task_type")
        if self.target_column is not None:
            _text(self.target_column, "data.target_column")
        _choice(self.cleaning, {"none", "adult", "anxiety"}, "data.cleaning")
        _finite_number(self.test_size, "data.test_size")
        if not 0 < self.test_size < 1:
            raise ValueError("data.test_size must lie in (0, 1)")
        for key in ("shots", "seeds"):
            values = getattr(self, key)
            if not isinstance(values, list) or not values:
                raise ValueError(f"data.{key} must be a nonempty list of unique integers")
            if any(isinstance(v, bool) or not isinstance(v, int) or v < (1 if key == "shots" else 0) for v in values):
                raise ValueError(f"Invalid data.{key}")
            if len(set(values)) != len(values):
                raise ValueError(f"data.{key} must contain unique integers")
            if key == "seeds" and any(value > 2 ** 32 - 1 for value in values):
                raise ValueError("data.seeds must lie in [0, 2**32 - 1] for reproducible sklearn splits")
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
        _text(self.model, "llm.model")
        _text(self.api_key_env, "llm.api_key_env")
        if "=" in self.api_key_env:
            raise ValueError("llm.api_key_env must be an environment variable name")
        _text(self.base_url, "llm.base_url")
        if any(char.isspace() for char in self.base_url):
            raise ValueError("llm.base_url must not contain whitespace")
        try:
            endpoint = urlsplit(self.base_url)
            port = endpoint.port  # Access validates malformed/out-of-range ports.
        except ValueError as exc:
            raise ValueError("Invalid model endpoint URL") from exc
        if (not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment
                or port == 0
                or not (endpoint.scheme == "https" or
                        (endpoint.scheme == "http" and endpoint.hostname in {"localhost", "127.0.0.1", "::1"}))):
            raise ValueError("Use HTTPS or a local HTTP model endpoint")
        for name in ("temperature", "top_p", "frequency_penalty", "presence_penalty", "timeout", "retry_delay"):
            _finite_number(getattr(self, name), f"llm.{name}")
        if not 0 <= self.temperature <= 2 or not 0 < self.top_p <= 1:
            raise ValueError("Invalid LLM temperature or top_p")
        if not -2 <= self.frequency_penalty <= 2 or not -2 <= self.presence_penalty <= 2:
            raise ValueError("LLM frequency_penalty and presence_penalty must lie in [-2, 2]")
        if self.timeout <= 0 or self.retry_delay < 0:
            raise ValueError("Invalid timeout/retry_delay")
        if type(self.json_mode) is not bool:
            raise ValueError("llm.json_mode must be boolean")
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
        if not isinstance(self.n_samples, list) or not self.n_samples:
            raise ValueError("generation.n_samples must be a nonempty list of unique sample counts")
        for n in self.n_samples:
            _positive_int(n, "generation.n_samples")
        if len(set(self.n_samples)) != len(self.n_samples):
            raise ValueError("generation.n_samples must contain unique sample counts")
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
        if type(self.enabled) is not bool or not isinstance(self.model_params, dict):
            raise ValueError("evaluation.enabled must be boolean and model_params must be a mapping")
        _choice(self.model, {"xgboost", "random_forest", "logistic", "ridge", "mlp"}, "evaluation.model")
        _choice(self.protocol, {"augmentation", "synthetic_only", "real_only"}, "evaluation.protocol")
        _choice(self.numeric_scaling, {"none", "train_range"}, "evaluation.numeric_scaling")
        _choice(self.fidelity_reference, {"train_test", "test", "train"}, "evaluation.fidelity_reference")
        _json_parameters(self.model_params, "evaluation.model_params")


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
        if type(self.version) is not int or self.version != 1:
            raise ValueError("Unsupported configuration version")
        for name, expected in (("data", DataConfig), ("discovery_llm", LLMConfig), ("generation_llm", LLMConfig),
                               ("generation", GenerationConfig), ("evaluation", EvaluationConfig)):
            if not isinstance(getattr(self, name), expected):
                raise ValueError(f"{name} must be a {expected.__name__} instance")
        _positive_int(self.discovery_attempts, "discovery_attempts")
        _positive_int(self.max_cycles, "max_cycles")
        self.output_dir = _text(self.output_dir, "output_dir", path=True)

    def to_dict(self):
        return asdict(self)


def _construct(cls, values, section):
    if not isinstance(values, dict):
        raise ValueError(f"{section} must be a mapping")
    if any(not isinstance(key, str) for key in values):
        raise ValueError(f"{section} field names must be strings")
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
