import yaml
from dataclasses import dataclass
from typing import List, Optional, Union
from pathlib import Path

@dataclass
class ClassifierConfig:
    """Configuration for the classifier model."""
    max_depth: int
    learning_rate: float
    n_estimators: int
    seed: int

@dataclass
class DataConfig:
    """Configuration for data handling."""
    base_dir: str
    dataset_name: str
    shots: List[int]
    seeds: List[int]
    target_column: str
    categorical_columns: Optional[List[str]]


@dataclass
class SyntheticConfig:
    """Configuration for synthetic data generation."""
    n_samples_list: List[int]

@dataclass
class ModelConfig:
    """Configuration for the language model."""
    name: str
    temperature: float
    max_tokens: int
    api_key: Optional[str]

@dataclass
class Config:
    """Main configuration class containing all sub-configurations."""
    data: DataConfig
    synthetic: SyntheticConfig
    classifier: ClassifierConfig
    model: ModelConfig


def load_config(config_path: str) -> Config:
    """
    Load and parse the YAML configuration file.
    
    Args:
        config_path (str): Path to the YAML configuration file
        
    Returns:
        Config: Parsed configuration object with type hints
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If required configuration fields are missing
    """
    try:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['data', 'structure', 'synthetic', 'classifier', 'model']
        missing_sections = [section for section in required_sections if section not in config_dict]
        if missing_sections:
            raise ValueError(f"Missing required configuration sections: {missing_sections}")
        
        # Convert dictionary to dataclass objects
        data_config = DataConfig(**config_dict['data'])
        synthetic_config = SyntheticConfig(**config_dict['synthetic'])
        classifier_config = ClassifierConfig(**config_dict['classifier'])
        model_config = ModelConfig(**config_dict['model'])
        
        return Config(
            data=data_config,
            synthetic=synthetic_config,
            classifier=classifier_config,
            model=model_config
        )
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    except TypeError as e:
        raise ValueError(f"Invalid configuration structure: {e}")