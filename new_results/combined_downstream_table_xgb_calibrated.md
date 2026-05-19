| Dataset | D_train ratio | CLLM ratio | StructSynth ratio |
| --- | ---: | ---: | ---: |
| Adult (C) | 1.0019 | 0.9883 | 1.0181 |
| Anxiety† (C) | 0.9991 | 0.9733 | 1.0012 |
| Salary† (R) | 0.9766 | 0.9900 | 0.9887 |
| Churn (C) | 0.9997 | 1.0019 | 1.0133 |

| Dataset | Eval. Model | D_train | CLLM | StructSynth |
| --- | --- | ---: | ---: | ---: |
| Adult (C) | XGBoost | 82.51 | 83.95 | **85.55** |
|  | Random Forest | 85.03 | 84.63 | **87.45** |
|  | Logistic Reg. | 85.68 | 85.49 | **87.80** |
|  | MLP | 83.63 | 83.59 | **86.85** |
| Anxiety† (C) | XGBoost | 85.49 | 85.17 | **86.45** |
|  | Random Forest | 86.85 | 85.14 | **87.04** |
|  | Logistic Reg. | 87.26 | 85.87 | **87.82** |
|  | MLP | 84.85 | 82.27 | **85.76** |
| Salary† (R) | XGBoost | 49.71 | 54.53 | **55.98** |
|  | Random Forest | 55.16 | 51.29 | **57.12** |
|  | Ridge | **59.48** | 52.58 | 56.80 |
|  | MLP | 44.61 | **46.00** | 42.64 |
| Churn (C) | XGBoost | 86.86 | 89.81 | **90.39** |
|  | Random Forest | 90.78 | 91.66 | **92.49** |
|  | Logistic Reg. | 90.61 | 91.91 | **92.19** |
|  | MLP | 91.71 | 92.36 | **93.61** |
