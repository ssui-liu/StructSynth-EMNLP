# StructSynth

Paper-aligned research code for **evidence-grounded graph induction** and
**graph-planned conditional tabular synthesis**. A dependency DAG plans the
generation order; it is not a claim of causal identification.

The implementation replaces the earlier demonstration code. Method
interpretations and breaking changes are recorded in
[the refactoring record](docs/REFACTOR_PLAN.md) and [migration guide](docs/MIGRATION.md).
Engineering tests do not establish reproduction of the paper's reported scores.

## Install and verify without an API key

Use Python 3.9 or newer; Python 3.11 is the primary tested environment.
From this directory:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,evaluation]'
python -m pytest -q
ruff check src tests run_*.py
structsynth demo --output-dir runs/demo --model xgboost --max-workers 2
structsynth demo --output-dir runs/demo --model xgboost --max-workers 2 --resume
```

The demo uses a deterministic client that copies training rows. It exercises the
complete pipeline, real local XGBoost evaluation, concurrent batches, artifacts,
and resumption. Its metrics are **not LLM generation-quality results**. No network
requests are made by the demo or test suite. The default demo evaluator is logistic
regression, which works with the core installation (`pip install -e .`).

Dependencies are declared in `pyproject.toml`; `requirements.txt` is a compatibility
install entry point. `constraints-tested-py311.txt` records the exact environment
used for validation, rather than claiming a universal platform lock.

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
No model or parameter is silently substituted. Keys are read from `api_key_env`
at request time; `env.example` shows shell syntax. `.env` files are not loaded
automatically, and key values are not stored in run identities or request logs.

The stages can also be run separately:

```bash
structsynth split --config configs/adult.yaml --seeds 42
structsynth discover --config configs/adult.yaml --seeds 42 --resume
structsynth generate --config configs/adult.yaml --seeds 42 --resume
structsynth evaluate --config configs/adult.yaml --seeds 42 --resume
```

`run_data_split.py`, `run_structure_learning.py` and `run_data_generation.py`
are thin aliases for `split`, `discover` and `generate`; they require the installed
package and the same new YAML configuration. `generate` does not run evaluation.

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

## Code layout and author review

| Module | Responsibility |
|---|---|
| `schema.py`, `config.py`, `data.py` | Validated contracts, splitting and train-only metadata |
| `associations.py`, `graph.py`, `discovery.py` | Evidence, DAG validation and induction |
| `generation.py` | Layer/batch generation, row identity, retries and checkpoints |
| `llm.py`, `artifacts.py` | Provider boundary, accounting, replay and atomic storage |
| `evaluation.py`, `reporting.py` | Paper metrics and compatible multi-seed summaries |
| `pipeline.py`, `cli.py`, `demo.py` | Experiment stages, commands and offline verification |

Run `python -m build` to create a wheel and source distribution. CI runs lint,
tests, an offline XGBoost demo and package builds. Historical `results/` are kept
as historical examples and were not regenerated by this refactor.

作者检查入口：[总记录](docs/REFACTOR_PLAN.md)、[图诱导](docs/decisions_graph.md)、
[生成](docs/decisions_generation.md)、[评估](docs/decisions_evaluation.md)、
[迁移](docs/MIGRATION.md)、[验证记录](docs/VALIDATION.md)。
