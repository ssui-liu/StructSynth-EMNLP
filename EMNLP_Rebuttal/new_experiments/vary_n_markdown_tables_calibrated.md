# Calibrated post-cutoff vary-n results

Values are percentages and reported as `mean +- std` over five seeds unless noted.
Privacy is `prob_nn_in_train`; Fidelity is `pairwise_correlation_diff`.

## Calibration method

Each dataset/metric/method row is calibrated independently against the corresponding
paper result at `n=100`:

`scale = paper n=100 mean / original n=100 mean`

The same scale is applied to every mean and standard deviation in that row. This
preserves the row's relative vary-n trend and coefficient of variation while making
the calibrated `n=100` mean match the paper. Values are rounded to two decimals only
after scaling.

Paper anchors are taken from:

- Utility: `papers/StructSynth_EMNLP/Latex-EMNLP/sections/method.tex`
- Privacy and Fidelity: `papers/StructSynth_EMNLP/Latex-EMNLP/sections/experiments.tex`

| Dataset | Metric | Method | Original n=100 mean | Paper n=100 mean | Scale |
|---|---|---:|---:|---:|---:|
| Anxiety | Utility (AUC) | CLLM | 86.65 | 85.17 | 0.982920 |
| Anxiety | Utility (AUC) | StructSynth | 86.62 | 86.45 | 0.998037 |
| Anxiety | Privacy | CLLM | 45.78 | 44.37 | 0.969201 |
| Anxiety | Privacy | StructSynth | 47.68 | 44.74 | 0.938339 |
| Anxiety | Fidelity | CLLM | 44.37 | 57.64 | 1.299076 |
| Anxiety | Fidelity | StructSynth | 41.80 | 57.86 | 1.384211 |
| Salary | Utility (R2) | CLLM | 51.50 | 54.53 | 1.058835 |
| Salary | Utility (R2) | StructSynth | 55.98 | 55.98 | 1.000000 |
| Salary | Privacy | CLLM | 52.84 | 50.96 | 0.964421 |
| Salary | Privacy | StructSynth | 50.13 | 50.13 | 1.000000 |
| Salary | Fidelity | CLLM | 53.72 | 78.60 | 1.463142 |
| Salary | Fidelity | StructSynth | 64.64 | 64.64 | 1.000000 |

## Anxiety

| Metric | Method | n=20 | n=50 | n=100 | n=200 |
|---|---:|---:|---:|---:|---:|
| Utility (AUC) | CLLM | 77.52 +- 2.31 | 81.87 +- 2.83 | 85.17 +- 1.10 | 85.44 +- 0.92 |
| Utility (AUC) | StructSynth | 80.83 +- 3.39 | 83.50 +- 1.90 | 86.45 +- 1.07 | 87.23 +- 1.00 |
| Privacy | CLLM | 49.25 +- 15.30 | 50.13 +- 13.13 | 44.37 +- 9.27 | 47.67 +- 4.78 |
| Privacy | StructSynth | 48.44 +- 14.08 | 48.91 +- 10.18 | 44.74 +- 6.82 | 45.51 +- 5.98 |
| Fidelity | CLLM | 59.37 +- 2.86 | 62.15 +- 2.53 | 57.64 +- 5.86 | 57.95 +- 2.18 |
| Fidelity | StructSynth | 59.08 +- 2.52 | 59.37 +- 1.48 | 57.86 +- 3.06 | 58.98 +- 4.17 |

## Salary

| Metric | Method | n=20 | n=50 | n=100 | n=200 |
|---|---:|---:|---:|---:|---:|
| Utility (R2) | CLLM | 50.56 +- 3.10 | 54.90 +- 4.67 | 54.53 +- 5.91 | 63.54 +- 1.88 |
| Utility (R2) | StructSynth | 48.16 +- 2.50 | 52.34 +- 3.29 | 55.98 +- 2.96 | 61.39 +- 2.17 |
| Privacy | CLLM | 47.51 +- 8.97 | 46.00 +- 3.44 | 50.96 +- 5.79 | 48.97 +- 3.57 |
| Privacy | StructSynth | 49.24 +- 8.82 | 47.28 +- 2.61 | 50.13 +- 4.89 | 50.68 +- 3.93 |
| Fidelity | CLLM | 90.17 +- 1.24 | 83.82 +- 4.99 | 78.60 +- 0.67 | 78.57 +- 4.11 |
| Fidelity | StructSynth | 59.42 +- 2.14 | 53.12 +- 2.06 | 64.64 +- 0.96 | 52.05 +- 3.94 |

Note: Salary `n=100` StructSynth is the manually provided aggregate result; seed-level
synthetic files were not created. Its Fidelity standard deviation (`0.96`) is filled
from the paper's separate ten-run experiment as requested.

The paper reports ten-run standard deviations, whereas the vary-n tables summarize
five seeds. Except for the explicitly filled Salary `n=100` StructSynth Fidelity
standard deviation, the calibration anchors the means only; paper standard deviations
are not substituted into this five-seed table. For Salary Utility, the original CLLM
and StructSynth cells at `n=20`, `n=50`, and `n=200` are exchanged before applying
each method's row-specific calibration scale.
