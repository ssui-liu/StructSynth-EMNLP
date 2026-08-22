# StructSynth

This repository, StructSynth, is dedicated to generating synthetic tabular data by first learning the underlying causal structure from a small, low-data regime sample. The process is divided into three main stages: data splitting, structure learning, and data generation. This approach allows for the creation of high-fidelity synthetic data that preserves the complex relationships present in the original dataset.

##  Project File Tree

This document outlines the structure of the StructSynth repository, detailing the role of each file and directory.

```
StructSynth/
│
├── config/
│   ├── data_generation_config.yaml     # Configuration for the data generation process
│   └── structure_learning_config.json  # Configuration for the structure learning process
│
├── data/
│   ├── adult/
│   │   ├── dataset_info.json           # Metadata and information about the adult dataset
│   │   └── raw_data.csv                # The raw adult dataset
│   └── utils.py                        # Utility functions for data handling
│
├── data_generation/
│   ├── evaluation/
│   │   ├── dcr_evaluation_pipeline.py  # Pipeline for Distance to Closest Record (DCR) evaluation
│   │   ├── downstream_performance_evaluation.py # Evaluates synthetic data on downstream machine learning tasks
│   │   ├── metrics.py                  # Defines various evaluation metrics for synthetic data
│   │   └── pairwise_correlation_evaluation.py # Evaluates the pairwise correlations of the synthetic data
│   │
│   ├── models/
│   │   ├── generator.py                # Core generator model for creating synthetic data
│   │   └── structure_llm/
│   │       ├── basic_llm.py            # Basic Large Language Model (LLM) implementation
│   │       ├── basic_prompt_templates.py # Basic prompt templates for the LLM
│   │       ├── llm_provider.py         # Provides an interface to different LLM APIs
│   │       ├── structure_graph_processor.py # Processes the structure graph for the LLM
│   │       ├── structure_llm.py        # LLM specifically tailored for structured data
│   │       └── structure_prompt_templates.py # Prompt templates for the structured data LLM
│   │
│   └── utils/
│       ├── config.py                   # Utility functions for handling configurations
│       └── preprocess.py               # Preprocessing utilities for data generation
│
├── results/
│   ├── structure_graph/                # Output directory for the learned structure graphs
│   │   └── adult/
│   │       └── gpt_4o_mini/            # Results from the gpt-4o-mini model
│   │           ├── graph.json          # The learned graph structure in JSON format
│   │           ├── graph.png           # A visualization of the learned graph
│   │           ├── relationships.txt   # The relationships learned by the model
│   │           └── report.md           # A report of the structure learning process
│   │
│   └── synth_data/                     # Output directory for the generated synthetic data
│
├── structure_learning/
│   ├── data/
│   │   └── data_loader.py              # Loads data for the structure learning process
│   │
│   ├── discovery/
│   │   ├── basic_causal_discovery.py   # A basic causal discovery algorithm
│   │   └── bfs_causal_discovery.py     # A Breadth-First Search (BFS) based causal discovery algorithm
│   │
│   ├── graph/
│   │   └── structure_graph.py          # Represents and manipulates the structure graph
│   │
│   ├── llm/
│   │   ├── llm_base.py                 # Base class for LLM implementations
│   │   ├── llm_generate.py             # Functions for generating text with the LLM
│   │   ├── llm_init.py                 # Initializes the LLM
│   │   ├── llm_interface.py            # An interface for interacting with the LLM
│   │   ├── llm_resolve.py              # Functions for resolving ambiguities with the LLM
│   │   └── utils.py                    # Utility functions for the LLM
│   │
│   └── utils.py                        # General utility functions for structure learning
│
├── .env.example                        # Example environment file
├── README.md                           # An overview of the project and how to run it
├── requirements.txt                    # Python dependencies for the project
├── run_data_generation.py              # Main script to run the data generation process
├── run_data_split.py                   # Main script to split the data into few-shot samples
└── run_structure_learning.py           # Main script to run the structure learning process 
```
## Workflow

The project follows a sequential workflow, where each step builds upon the output of the previous one.

### 1. Data Splitting

The first step is to preprocess the raw data and create multiple random splits, which is essential for working in a low-data regime. This is handled by the `run_data_split.py` script.

**`run_data_split.py`**

This script takes a dataset and generates several "few-shot" versions of it. Each version contains a small number of samples, simulating a scenario where only limited data is available. The script creates multiple splits with different random seeds to ensure the robustness of the learned structure in later stages.

### 2. Structure Learning

Once the data is split, the next step is to learn the causal structure from one of the generated few-shot datasets. This is accomplished using the `run_structure_learning.py` script.

**`run_structure_learning.py`**

This script implements a causal discovery algorithm to infer the dependency graph of the variables in the dataset. It uses a Breadth-First Search (BFS) approach, combined with a Large Language Model (LLM), to identify the relationships between different columns in the data. The output is a dependency graph that represents the underlying causal structure.

### 3. Data Generation

With the dependency graph in hand, the final step is to generate synthetic data. The `run_data_generation.py` script is responsible for this task.

**`run_data_generation.py`**

This script uses the learned dependency graph to generate new tabular data that follows the same causal relationships as the original data. By leveraging the hierarchical structure of the graph, it can produce synthetic data that is both realistic and diverse. The generated data can then be used for various downstream tasks, such as model training and data augmentation.

## How to Run

To run the complete pipeline, follow these steps in order:

1. **Run Data Split**: Execute `run_data_split.py` to preprocess the data and create the few-shot splits.
2. **Run Structure Learning**: Run `run_structure_learning.py` to learn the dependency graph from the data.
3. **Run Data Generation**: Finally, run `run_data_generation.py` to generate the synthetic tabular data based on the learned structure.

Make sure to configure the necessary paths and parameters in the respective configuration files before running each script.

## Disclaimer

This repository is intended to showcase the core logic of the StructSynth project and may not be fully polished. The code is organized to prioritize clarity of the fundamental concepts and, as a result, may contain some inconsistencies in file organization and function arguments. It is provided as-is for demonstration purposes. 