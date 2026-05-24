# SPADA NF n=1000 Privacy and Fidelity

| Method | Metric | Adult | Anxiety | Compas | Salary | Obesity | Churn | Average |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPADA_nf_gpt-4o-mini | Privacy DCR | 95.20 +- 0.71 | 78.76 +- 15.53 | 57.86 +- 11.26 | 94.98 +- 0.88 | 83.08 +- 1.69 | 92.30 +- 1.49 | 83.70 |
| SPADA_nf_gpt-4o-mini | Statistical Fidelity | 83.14 +- 0.73 | 45.92 +- 1.33 | 53.62 +- 1.55 | 61.79 +- 0.55 | 55.29 +- 0.85 | 47.85 +- 1.17 | 57.93 |

- Note: Compas fidelity replaced with SPADA_kde_gpt-4o-mini because NF was NaN.

Privacy DCR is better when closer to 50. Statistical Fidelity is better when lower.