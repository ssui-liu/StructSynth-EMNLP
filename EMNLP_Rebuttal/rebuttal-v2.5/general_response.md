# General Response to All Reviewers

We thank all reviewers for the constructive feedback. The reviews ask us to clarify novelty relative to PAFT (Exp-1), isolate semantic priors (Exp-2), justify evaluation choices (Exp-3/4), surface the submitted artifacts (see Artifacts below), and calibrate privacy and fidelity claims (wording revisions; no new experiments required). We use the following shared experiment numbering throughout.

- **Exp-1 — Cross-system component transfer (StructSynth × PAFT).** In the bidirectional 2×2 table, swapping in the StructSynth graph raises average AUC under both generators (0.030 with the PAFT generator, 0.022 with the StructSynth generator), while conditions using the StructSynth generator have higher average AUC (0.056 with the PAFT graph, 0.048 with the StructSynth graph) and lower DCR deviation. PAFT retains better pairwise fidelity. Because the cells are not strictly matched, we use these results only as component-compatibility evidence. [7Wh2-W1]

- **Exp-2 — Feature anonymization.** After replacing all column names and descriptions with generic identifiers, StructSynth remains functional because statistical association scores compensate for the absent semantic prior. Results are task-dependent: classification utility degrades modestly (AUC 0.865 → 0.850), while regression degrades more (R² 0.560 → 0.462). [7Wh2-W4; iRH3-W3]

- **Exp-3 — Post-cutoff vary-n experiments.** On Anxiety and Salary, both released after the LLM knowledge cutoff, StructSynth leads CLLM across all sample sizes on classification (largest margin at n=20: +3.31 AUC). StructSynth also leads at every sample size on Salary, though with smaller margins (+1.5 to +2.6 R² points). [q74j-W2]

- **Exp-4 — Qwen3-32B backbone check.** StructSynth maintains modest advantages under Qwen3-32B on both post-cutoff datasets (e.g., Anxiety AUC 0.856 vs. 0.843, 0–1 scale), supporting LLM-backbone generality. [q74j-W2]

Together, these results support that StructSynth's improvements arise from the explicit graph-as-generation-plan design rather than LLM memorization, hold across post-cutoff datasets and LLM backbones, and complement rather than duplicate PAFT's fine-tuning approach.

**Artifacts.** The anonymized repository was already included in the submission [Submitted, Appendix A, l.855–859]. The revision will additionally provide preprocessed datasets, exact splits, configurations, seeds, and preprocessing scripts.

**Revision plan.** We will (1) position PAFT in §1–§2 [7Wh2-R1]; (2) narrow the contribution to inference-time graph execution [7Wh2-R2]; (3) correct GraDe in Appendix G.2 and justify baselines in §4.1 [7Wh2-R3; q74j-R1]; (4) use empirical privacy language in §4.2/Limitations [7Wh2-R4]; (5) report the utility–privacy–fidelity trade-off in §5/Appendix K.2 [7Wh2-R5]; (6) add Exp-1–4, surface the direction-aware SHD evaluation in §4.4 [iRH3-R1], and clarify low-data/opaque-schema boundaries in §4.5/Appendix [7Wh2-R6; iRH3-R2/R3; q74j-R2]; and (7) move the generation-plan definition earlier, expand the Appendix A artifact checklist, and identify direct structural metrics as future work [q74j-R3/R4; 7Wh2-R7].
