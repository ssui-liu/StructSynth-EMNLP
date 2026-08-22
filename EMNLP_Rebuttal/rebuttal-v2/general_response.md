# General Response to All Reviewers

We thank all reviewers for the constructive feedback. The reviews ask us to clarify novelty relative to PAFT, isolate semantic priors, calibrate privacy and fidelity claims, justify evaluation choices, and surface the submitted artifacts. We use the following shared experiment numbering throughout.

- **Exp-1 — Cross-system component transfer (StructSynth × PAFT).** In the bidirectional 2×2 table, conditions using the StructSynth graph have higher average AUC by +0.030/+0.022, while conditions using the StructSynth generator have higher average AUC by +0.056/+0.048 and lower DCR deviation. PAFT retains better pairwise fidelity. Because the cells are not strictly matched, we use these results only as component-compatibility evidence. [7Wh2-W1]

- **Exp-2 — Feature anonymization.** After replacing all column names and descriptions with generic identifiers, StructSynth remains functional because statistical association scores compensate for the absent semantic prior. Results are task-dependent: classification utility degrades modestly (AUC 0.865→0.850), while regression degrades more (R² 0.560→0.462). Even the worst case exceeds unstructured baselines. [7Wh2-W4; iRH3-W3]

- **Exp-3 — Post-cutoff vary-n experiments.** On Anxiety and Salary, both released after the LLM knowledge cutoff, StructSynth leads CLLM across all sample sizes on classification (largest margin at n=20: +3.31 AUC). Regression is mixed: StructSynth leads only at n=100 (R² 55.98 vs. 54.53), with CLLM ahead at the other sample sizes. [q74j-W2]

- **Exp-4 — Qwen3-32B backbone check.** StructSynth maintains modest advantages under Qwen3-32B on both post-cutoff datasets, supporting LLM-backbone generality. [q74j-W2]

Together, these results support that StructSynth's improvements arise from the explicit graph-as-generation-plan design rather than LLM memorization, hold across post-cutoff datasets and LLM backbones, and complement rather than duplicate PAFT's fine-tuning approach.

**Artifacts.** The anonymized repository was already included in the submission [Submitted, Appendix A, l.855–859]. The revision will additionally provide preprocessed datasets, exact splits, configurations, seeds, and preprocessing scripts.

**Revision plan.** We will (1) position PAFT in §1–§2; (2) narrow the contribution to inference-time graph execution; (3) correct GraDe in Appendix G.2 and justify baselines in §4.1; (4) use empirical privacy language in §4.2/Limitations; (5) report the utility–privacy–fidelity trade-off in §5/Appendix K.2; (6) add Exp-1–4 and clarify low-data/opaque-schema boundaries in §4.5/Appendix; and (7) move the generation-plan definition earlier, expand the Appendix A artifact checklist, and identify direct structural metrics as future work.
