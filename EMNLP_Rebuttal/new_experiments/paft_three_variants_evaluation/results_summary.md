# PAFT Three-Variant Evaluation Summary

Original evaluation: 2026-07-09  
XGBoost-aligned downstream re-evaluation: 2026-07-11

This folder archives the aligned evaluation results for three PAFT variants:

- `paft_full`: original full-header PAFT generation, 10 seeds.
- `paft_anon_headers`: PAFT generation with anonymized headers, mapped back to the original schema, 10 seeds.
- `paft_graph_orders`: PAFT generation using graph-based column orders, 5 seeds.

The evaluations are aligned with `30_evaluation/StructSynthEvaluation` and cover three aspects:

- Downstream utility: AUC/R2 from the StructSynth-aligned XGBoost evaluator (`xgboost==3.0.0`; max depth 6, learning rate 0.1, 100 estimators, seed 42), trained on the 100 real rows plus 1,000 synthetic rows.
- Statistical fidelity: mean pairwise correlation/distribution difference. Lower is better.
- Privacy proxy: DCR / `Prob(NN in Train)` as reported by the evaluator. The ideal value is 0.50, so cross-dataset privacy is summarized with the mean absolute deviation from 0.50.

Raw and detailed outputs are saved under `evaluation_outputs/`. The reusable evaluation script is saved under `reproducibility/run_paft_results.py`.

## Overall Averages

| Variant | Seeds | Mean classification AUC | Mean regression R2 | Mean fidelity diff | Mean DCR | Mean \|DCR-0.50\| |
|---|---:|---:|---:|---:|---:|---:|
| `paft_anon_headers` | 10 | 0.7672 | 0.3964 | 0.5454 | 0.6600 | 0.1600 |
| `paft_full` | 10 | 0.7521 | 0.4039 | 0.5374 | 0.6535 | 0.1535 |
| `paft_graph_orders` | 5 | 0.7818 | 0.3596 | 0.5400 | 0.6497 | 0.1497 |

## Dataset-Level Results

| Dataset | Variant | Seeds | DCR (ideal 0.50) | Fidelity diff | Utility |
|---|---|---:|---:|---:|---:|
| adult | `paft_anon_headers` | 10 | 0.7632 | 0.5205 | AUC 0.8083 |
| adult | `paft_full` | 10 | 0.7635 | 0.5166 | AUC 0.7870 |
| adult | `paft_graph_orders` | 5 | 0.7388 | 0.5030 | AUC 0.8170 |
| anxiety | `paft_anon_headers` | 10 | 0.6095 | 0.4351 | AUC 0.7304 |
| anxiety | `paft_full` | 10 | 0.6076 | 0.4296 | AUC 0.7217 |
| anxiety | `paft_graph_orders` | 5 | 0.5956 | 0.4308 | AUC 0.8386 |
| churn | `paft_anon_headers` | 10 | 0.6267 | 0.5593 | AUC 0.8910 |
| churn | `paft_full` | 10 | 0.6232 | 0.5472 | AUC 0.8988 |
| churn | `paft_graph_orders` | 5 | 0.6514 | 0.5429 | AUC 0.8849 |
| compas | `paft_anon_headers` | 10 | 0.7496 | 0.5534 | AUC 0.6393 |
| compas | `paft_full` | 10 | 0.7531 | 0.5386 | AUC 0.6007 |
| compas | `paft_graph_orders` | 5 | 0.7408 | 0.5563 | AUC 0.5868 |
| obesity_reg | `paft_anon_headers` | 10 | 0.5893 | 0.5693 | R2 0.3568 |
| obesity_reg | `paft_full` | 10 | 0.5708 | 0.5700 | R2 0.3601 |
| obesity_reg | `paft_graph_orders` | 5 | 0.5732 | 0.5764 | R2 0.3609 |
| salary | `paft_anon_headers` | 10 | 0.6217 | 0.6347 | R2 0.4359 |
| salary | `paft_full` | 10 | 0.6028 | 0.6222 | R2 0.4476 |
| salary | `paft_graph_orders` | 5 | 0.5984 | 0.6307 | R2 0.3582 |

## Main Takeaways

Under the aligned XGBoost evaluator, `paft_graph_orders` has the highest average classification AUC (0.7818), while `paft_full` has the strongest average regression R2 (0.4039) and the best statistical fidelity (0.5374). Graph ordering produces its largest utility gain on Anxiety, but reduces Salary R2, so the transfer remains task-selective. It currently has only 5 seeds and should be treated as preliminary until seeds 47--51 are completed.

## Files

- `evaluation_outputs/paft_overview.csv`: complete machine-readable overview with means and standard deviations.
- `evaluation_outputs/paft_overview.md`: Markdown version of the complete overview.
- `evaluation_outputs/{dataset}/100_shot/{variant}/detailed_results.csv`: per-seed results.
- `evaluation_outputs/{dataset}/100_shot/{variant}/summary.json`: per-dataset summary statistics.
- `rebuttal_table.tex`: compact LaTeX table for paper/rebuttal drafting.
- `reproducibility/run_paft_results.py`: evaluation wrapper used to align PAFT outputs with the shared evaluator.
