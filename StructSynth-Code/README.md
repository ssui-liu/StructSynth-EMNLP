# StructSynth

**Dependency Graphs as Generation Plans for Low-Data Tabular Synthesis with Language Models**

Siyi Liu, Yujia Zheng, Haoyang Li, and Yongqi Zhang

StructSynth uses a learned dependency graph to guide tabular data generation with
a black-box LLM in low-data settings. It combines **Evidence-Grounded Graph
Induction** with **Graph-Planned Conditional Synthesis**, without LLM fine-tuning.
See the paper for the method, experiments, and evaluation details.

## Installation

Requires Python 3.9 or newer; Python 3.11 is recommended. From the project root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[evaluation]'
```

Dependencies and optional extras are defined in [`pyproject.toml`](pyproject.toml).

## Quick start

### Offline demo

Run the complete pipeline without an API key:

```bash
structsynth demo --output-dir runs/demo --model xgboost
```

The demo uses a local client that copies training rows to check the software pipeline.

### Run the Adult example

The included data and experiment settings are configured in
[`configs/adult.yaml`](configs/adult.yaml). Set your API key, inspect the plan,
and start an experiment:

```bash
export OPENAI_API_KEY='your-key'
structsynth plan --config configs/adult.yaml --seeds 42
structsynth run --config configs/adult.yaml --seeds 42
```

Omit `--seeds 42` to run all configured seeds. To resume an existing run:

```bash
structsynth run --config configs/adult.yaml --seeds 42 --resume
```

For the paper's 100-shot prompt setting, change `data.example_rows` from `20` to
`100` and set `generation.n_samples` to `[1000]` in the YAML file.

Configure data paths, model endpoints, and generation settings in YAML. Paths
inside the file are relative to its location; default outputs are saved under
`runs/`. Use `structsynth --help` for available commands, or the
[stage scripts](scripts/README.md) to run splitting, graph induction, and generation
separately.

## Code organization

```text
configs/          experiment configurations
data/adult/       example dataset and metadata
docs/             implementation notes
scripts/          stage entry scripts
src/structsynth/   data, structure, generation, LLM, evaluation, and pipeline modules
tests/            offline tests
```

See the [package guide](src/structsynth/README.md) for module responsibilities and
reading order.

## Development

```bash
python -m pip install -e '.[dev,evaluation]'
python -m pytest -q
ruff check src tests scripts
python -m build
```

## Citation

If you use StructSynth, please cite the paper:

```bibtex
@misc{structsynth,
  title = {StructSynth: Dependency Graphs as Generation Plans for Low-Data Tabular Synthesis with Language Models},
  author = {Liu, Siyi and Zheng, Yujia and Li, Haoyang and Zhang, Yongqi},
  note = {Manuscript}
}
```
