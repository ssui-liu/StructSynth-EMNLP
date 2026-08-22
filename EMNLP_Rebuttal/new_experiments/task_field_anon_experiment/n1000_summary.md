# n=1000 Summary: Downstream (AUC/R²), Fidelity, Privacy

Extracted from `results_summary.md` / `fidelity_privacy_eval.json`, focused on the n=1000 synthetic sample size only. Downstream is reported as a single metric per dataset: **AUC-ROC** for anxiety (classification), **R²** for salary (regression) — salary has no AUC since it is a regression task.

| Dataset | Condition | Downstream (Anxiety: AUC / Salary: R²) | Fidelity (↓ better) | Privacy DCR (→0.5 better) |
|---------|-----------|:---:|:---:|:---:|
| Anxiety | field_anon | **0.877** | **0.490** | 0.870 |
| Anxiety | no_anon | 0.871 | 0.531 | **0.690** |
| Salary | field_anon | 0.470 | **0.674** | **0.766** |
| Salary | no_anon | **0.569** | 0.709 | 0.931 |

## Notes

- **Downstream**: Anxiety — field_anon slightly ahead (0.877 vs 0.871 AUC). Salary — no_anon clearly ahead (0.569 vs 0.470 R²); this is the only metric among the three where no_anon wins decisively.
- **Fidelity**: field_anon is better on both datasets (lower pairwise correlation difference), suggesting the sparser, data-driven graph gives a better structural prior.
- **Privacy DCR**: mixed — no_anon closer to 0.5 on anxiety (0.690), field_anon closer to 0.5 on salary (0.766).

Source data: `results_summary.md` (Table 1, n=1000 rows) and `fidelity_privacy_eval.json`; per-condition raw metrics in `downstream_summaries/*_n1000.md`.
