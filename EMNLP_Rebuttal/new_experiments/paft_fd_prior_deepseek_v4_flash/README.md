# PAFT-FD Graph Prior Synthesis with DeepSeek V4 Flash

This experiment uses PAFT-derived functional-dependency graph priors as the hierarchical graph input for StructSynth/NaiveHierarchicalCLLM synthesis.

## Setup

- Model: `deepseek-v4-flash`
- Downstream learner: StructSynth XGBoost evaluator
- Thinking/reasoning: disabled by using the non-reasoner flash model path
- Datasets: `adult`, `anxiety`, `compas`, `salary`, `obesity_reg`, `churn`
- Shot/seeds: `100_shot`, `seed_42`--`seed_46`
- Sample sizes: `100`, `200`, `500`, `1000`
- Generation concurrency: `max_concurrency=8`, `samples_per_call=20`
- Output root: `results/`

## Completion

- Manifest passed: `True`
- Completed dataset runs: `30` (6 datasets x 5 seeds)
- Generated synthetic CSVs: `120` (6 datasets x 5 seeds x 4 sample sizes)
- Each CSV line count matches expected `n + 1` including header.
- The final manifest records 14,113,601 generated-run tokens (10,485,477 prompt; 3,628,124 completion).

## n=1000 Downstream Metrics

| Dataset | Task | Main metrics |
|---|---:|---|
| `adult` | classification | Acc=0.7992 +/- 0.0102, F1=0.6070 +/- 0.0208, AUC=0.8504 +/- 0.0122 |
| `anxiety` | classification | Acc=0.7307 +/- 0.0172, F1=0.7307 +/- 0.0172, AUC=0.8671 +/- 0.0086 |
| `compas` | classification | Acc=0.6699 +/- 0.0100, F1=0.6387 +/- 0.0163, AUC=0.7094 +/- 0.0132 |
| `salary` | regression | RMSE=41.2523 +/- 1.6580, MAE=30.3330 +/- 1.3207, R2=0.5287 +/- 0.0441 |
| `obesity_reg` | regression | RMSE=16.2224 +/- 1.5196, MAE=12.2708 +/- 1.1303, R2=0.6108 +/- 0.0709 |
| `churn` | classification | Acc=0.8502 +/- 0.0278, F1=0.6063 +/- 0.0395, AUC=0.8848 +/- 0.0094 |

## n=1000 Fidelity and Privacy Metrics

These metrics were evaluated over the same five seeds with the shared evaluator used for the PAFT three-variant experiment. Fidelity is pairwise correlation difference (lower is better). For DCR / `Prob(NN in Train)`, 0.50 is ideal.

| Dataset | Fidelity diff | DCR | \|DCR - 0.50\| |
|---|---:|---:|---:|
| `adult` | 0.4724 +/- 0.0147 | 0.4408 +/- 0.0327 | 0.0592 |
| `anxiety` | 0.6207 +/- 0.0275 | 0.4696 +/- 0.0708 | 0.0304 |
| `compas` | 0.5844 +/- 0.0205 | 0.6214 +/- 0.0394 | 0.1214 |
| `churn` | 0.6546 +/- 0.0246 | 0.4862 +/- 0.0870 | 0.0138 |
| `obesity_reg` | 0.6036 +/- 0.0087 | 0.5588 +/- 0.0196 | 0.0588 |
| `salary` | 0.5435 +/- 0.0246 | 0.5366 +/- 0.0258 | 0.0366 |
| **Average** | **0.5798** | **0.5189** | **0.0534** |

## Files

- `results/manifest.json`: run manifest and per-dataset summaries
- `results/metrics_summary.csv`: metrics for every dataset and sample size
- `evaluation_outputs/fidelity_privacy_detailed.csv`: per-seed fidelity and DCR at n=1000
- `evaluation_outputs/fidelity_privacy_overview.csv`: five-seed fidelity and DCR summaries
- `results/{dataset}/100_shot/paft_fd_prior_deepseek-v4-flash/seed_{42..46}/n{N}/synthetic_data.csv`: generated tables
- `reproducibility/refresh_result_indexes.py`: rebuilds the two flat indexes from per-seed artifacts
- `reproducibility/run_paft_fd_prior_full_synthesis.py`: runner used for this experiment
