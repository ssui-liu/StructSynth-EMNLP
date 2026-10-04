# StructSynth

Paper-aligned research code for **evidence-grounded graph induction** and
**graph-planned conditional tabular synthesis**. A dependency DAG plans the
generation order; it is not a claim of causal identification.

Method interpretations and implementation choices are documented for
[graph induction](docs/decisions_graph.md), [generation](docs/decisions_generation.md)
and [data/evaluation](docs/decisions_evaluation.md). Engineering tests do not
establish reproduction of the paper's reported scores.

## Install and verify without an API key

Use Python 3.9 or newer; Python 3.11 is the primary tested environment.
From this directory, create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Choose the installation that matches your work. Dependencies and optional extras
are defined in [`pyproject.toml`](pyproject.toml):

| Use | Command |
|---|---|
| Core package and offline demo | `python -m pip install -e .` |
| Paper experiments with XGBoost | `python -m pip install -e '.[evaluation]'` |
| Development, tests and builds | `python -m pip install -e '.[dev,evaluation]'` |

After the development installation, verify the pipeline without an API key:

```bash
python -m pytest -q
ruff check src tests scripts
structsynth demo --output-dir runs/demo --model xgboost --max-workers 2
structsynth demo --output-dir runs/demo --model xgboost --max-workers 2 --resume
```

The demo uses a deterministic client that copies training rows. It exercises the
complete pipeline, real local XGBoost evaluation, concurrent batches, artifacts,
and resumption. Its metrics are **not LLM generation-quality results**. No network
requests are made by the demo or test suite. The default demo evaluator is logistic
regression, which works with the core installation (`pip install -e .`).

Editable installation (`-e`) uses the working tree directly. Omit `-e` for a
regular installation. There is no separate dependency list to keep in sync.

## Run an experiment

All input/output paths inside a configuration are relative to **that configuration
file**, independent of the shell's working directory. The included Adult data and
metadata are used by `configs/adult.yaml`.

```bash
structsynth plan --config configs/adult.yaml --seeds 42
export OPENAI_API_KEY='your-key'
structsynth run --config configs/adult.yaml --seeds 42
structsynth run --config configs/adult.yaml --seeds 42 --resume
```

`plan` reports run locations and request limits without contacting a model or
creating experiment artifacts. Omit `--seeds 42` to run the configured seeds 42–51.
`--shots` and `--seeds` select experiments; selecting a subset for recovery does
not change the identity of an individual experiment.

The default configuration uses 100 real training rows; synthesizes 1,000 rows
once; and evaluates prefixes of 100, 200, 500 and 1,000 rows. Prefixes within a seed
are paired, not independent generation runs. Each seed learns its own graph.
The default evaluation fits XGBoost on **real train + synthetic data** and scores
it on the held-out test set. A real-only baseline is fitted and saved before
model requests, which also catches invalid evaluator parameters early.

The shared client sends JSON chat-completion requests to the configured
`base_url`. The endpoint must support the selected model and request parameters.
No model or parameter is silently substituted. Each stage's `api_key_env` names
the environment variable read at request time; it defaults to `OPENAI_API_KEY`,
set with `export` as shown above. Configure `base_url`, `model` and `api_key_env`
in the YAML file for other endpoints. `.env` files are not loaded automatically,
and key values are not stored in run identities or request logs.

The stages can also be run separately:

```bash
structsynth split --config configs/adult.yaml --seeds 42
structsynth discover --config configs/adult.yaml --seeds 42 --resume
structsynth generate --config configs/adult.yaml --seeds 42 --resume
structsynth evaluate --config configs/adult.yaml --seeds 42 --resume
```

The three Python entry scripts live in [`scripts/`](scripts/README.md) and share
the CLI's configuration and arguments. After installing the package, run them
from the project root:

```bash
python scripts/run_data_split.py --config configs/adult.yaml --seeds 42
python scripts/run_structure_learning.py --config configs/adult.yaml --seeds 42 --resume
python scripts/run_data_generation.py --config configs/adult.yaml --seeds 42 --resume
structsynth evaluate --config configs/adult.yaml --seeds 42 --resume
```

The scripts map to `split`, `discover` and `generate`, respectively. `generate`
does not run evaluation. Use `--resume` to continue the same experiment across stages.

## Method and data boundaries

1. Split the original table 80:20, then sample `shot` rows from the training pool.
   Unused training-pool rows are never passed to either LLM or downstream training.
   Prompt examples are sampled only from the finite training set.
2. Ask for source nodes, expand successors by BFS with train-only association
   evidence, and resolve every elementary cycle. Validate the final DAG.
3. Generate topological layers conditioned on **all previously generated values**
   and the local induced subgraph. Complete attributes outside the selected graph
   last. Selected zero-degree nodes remain graph roots.
4. Evaluate augmentation utility, mixed-distance nearest-neighbor privacy risk,
   and pairwise fidelity. Fidelity defaults to the real train-plus-test reference;
   this reference is used only for evaluation.

Classification splits preserve classes. Regression is selected explicitly via
`task_type`. Metadata accepts the existing `label_column`/`description` aliases,
or a schema such as:

```json
{
  "name": "example",
  "target_column": "outcome",
  "task_type": "classification",
  "categorical_columns": ["group", "outcome"],
  "integer_columns": ["age"],
  "descriptions": {"age": "Age in years", "group": "Group", "outcome": "Label"},
  "task": "Describe the table's prediction task."
}
```

Optional `categories` supplies explicit hard domains. Otherwise, ordinary
categorical features may take previously unseen values; observed training values
are hints. Classification targets use a train-only closed label domain. Optional
`boolean_columns` and `nullable_columns` make these types explicit. Privacy and
fidelity require finite numeric observations under the paper's definitions;
evaluation fails before model requests if real numeric data is missing/non-finite.
Disable evaluation explicitly for a generation-only task that permits such data.

The Adult and Anxiety historical transformations are explicit `data.cleaning`
modes. Other data defaults to `none`. See [data/evaluation decisions](docs/decisions_evaluation.md)
for stratification, prompt balancing, categorical encoding, missing metrics,
privacy ties and fidelity binning.

## Inspect artifacts and resume

Each experiment is stored under:

```text
runs/<dataset>/<shot>_shot/seed_<seed>/<identity-prefix>/
  manifest.json                   inputs, environment, source hash, stages, artifact hashes
  split.json, schema.json          row provenance and train-derived metadata
  train.csv, test.csv, examples.csv
  real_baseline.json               local real-only utility baseline
  graph.json, discovery_events.json
  discovery_requests.jsonl         durable request reservations and outcomes
  generation_requests.jsonl        prompts, responses, errors and usage
  checkpoints/                    per-layer/batch progress and attempt counters
  synthetic.csv, synthetic.json    full table, with JSON type preservation
  generation_events.json
  n100/metrics.json, n100/synthetic.csv, ...
  metrics.json, usage.json
  failure_details.json            diagnostic events when an algorithm fails
```

Request logs include the supplied example rows and model responses so that the
experiment can be audited. Keep them with the run. Completed artifacts and request
logs are hashed; deleting a started stage's journal cannot reset its request
budget. An OS lock prevents two processes from writing the same run. Atomic
checkpoints preserve completed rows and consumed attempts across interruption.

`--resume` verifies the configuration, inputs, source code, dependency versions
and completed artifacts. Changes produce a distinct run identity. Generation
resumes verified batches; interrupted discovery restarts induction using the
existing request budget. It does not currently resume a partially constructed
graph. Retry exhaustion remains exhaustion after restarting.

`request_limit` bounds attempted API calls including transport retries.
`token_limit`, when supplied, stops future calls after reported usage reaches the
limit; a response or concurrent in-flight responses can cross it. Missing token
usage is recorded as unknown, never zero, and prevents further token-limited
calls. `usage.json` distinguishes API attempts from offline replay.

## Replay and summarize

To replay a completed run with the same input/configuration and prompt protocol:

```bash
structsynth run --config configs/adult.yaml --shots 100 --seeds 42 \
  --replay-dir runs/adult/100_shot/seed_42/<source-run-id>
```

Replay never calls the network. It is identified separately by the source journal
hashes and records zero new API consumption; original usage stays in `source_usage`
inside its journal. Missing or mismatching recorded requests fail explicitly.
Choose exactly one shot and seed for each pair of source journals. A remote seed
does not imply deterministic LLM output; replay reproduces recorded responses.

Full experiment runs write JSON/CSV summaries beneath `runs/summaries/`.
To summarize selected run directories independently:

```bash
structsynth report --run-dirs <run-directory-1> <run-directory-2> \
  --output-dir runs/review
```

Compatible seeds are combined using a mean and sample standard deviation.
Missing/undefined metrics and duplicate seeds are reported explicitly; unrelated
models, inputs, protocols, code/environment versions and offline/live backends
are kept in separate groups. One seed has no estimated standard deviation.

## Project layout

```text
StructSynth-Code/
  configs/                  example experiment configurations
  data/adult/               sample dataset and metadata
  docs/                     method and implementation notes
  scripts/                  Python entry scripts for individual stages
  src/structsynth/           installable package
  tests/                    offline regression tests
  pyproject.toml            dependencies, CLI, wheel and development-tool settings
  MANIFEST.in               additional files for the source distribution
```

The package is organized by responsibility:

| Module | Responsibility |
|---|---|
| `schema.py`, `config.py`, `artifacts.py` | Shared data/configuration contracts and atomic storage |
| `data/` | Loading, validation, train-only metadata and sampling |
| `structure/` | Association evidence, dependency DAGs, induction and prompts |
| `generation/` | Planning, prompts, validation, checkpoints and synthesis orchestration |
| `llm/` | Request/response contracts, provider client, accounting and replay |
| `evaluation/` | Preprocessing, utility/privacy/fidelity metrics and multi-seed reports |
| `pipeline/`, `cli.py`, `demo.py` | Experiment identity, stages, commands and offline verification |

See [the package reading and maintenance guide](src/structsynth/README.md) for the
module map, dependency direction and where to make each kind of change.
Existing public imports remain available; root-level `graph.py`, `associations.py`,
`discovery.py` and `reporting.py` are compatibility exports.

Run `python -m build` to create a wheel and source distribution. CI runs lint,
tests, an offline XGBoost demo and package builds. [`MANIFEST.in`](MANIFEST.in)
adds the stage scripts, example configuration, Adult data, method notes and tests
to the source distribution. `pyproject.toml` selects the `structsynth` package
and its reading guide for the wheel, and defines the `structsynth` command.
Generated runs, build output, caches and local environments are excluded from Git
and release packages.
