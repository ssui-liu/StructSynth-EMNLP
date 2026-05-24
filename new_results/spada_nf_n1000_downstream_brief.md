# SPADA-NF n1000 Downstream Results

Values are `mean (variance)` across seeds. Variance is computed as `std^2` from the existing summary files.

| Dataset | Task | Seeds | Accuracy | F1 | AUC | MAE | RMSE | R2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| adult | classification | 4 | 0.7855 (0.000040) | 0.5171 (0.000829) | 0.8125 (0.000183) | - | - | - |
| anxiety | classification | 5 | 0.4934 (0.000630) | 0.4934 (0.000630) | 0.6539 (0.000695) | - | - | - |
| compas | classification | 5 | 0.6275 (0.000876) | 0.5977 (0.002041) | 0.6558 (0.000912) | - | - | - |
| salary | regression | 5 | - | - | - | 34.1025 (2.626863) | 48.1914 (3.793534) | 0.3570 (0.003248) |
| obesity_reg | regression | 5 | - | - | - | 14.0992 (0.759674) | 19.2020 (0.682208) | 0.4573 (0.002047) |
| churn | classification | 5 | 0.8781 (0.000104) | 0.5705 (0.002873) | 0.8755 (0.000154) | - | - | - |

Note: `adult` currently has 4 seeds (`44-47`); the other datasets have 5 seeds (`42-46`).
