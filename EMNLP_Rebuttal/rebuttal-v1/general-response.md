# General Response to All Reviewers

We thank all reviewers for their thorough and constructive feedback. The reviews collectively raise concerns about (a) novelty relative to PAFT and the broader graph-aware synthesis literature, (b) the role and limitations of the LLM semantic prior, (c) privacy evaluation scope, (d) dataset and baseline selection transparency, and (e) artifact availability for reproduction. During the response period we conducted four new experiments and analyses that address these concerns with quantitative evidence. They are referenced as **Exp-1 through Exp-4** in the individual responses:

- **Exp-1 -- Cross-system component transfer (StructSynth × PAFT).** A bidirectional 2×2 experiment under unified XGBoost evaluation shows that graph source and generation mechanism are separable components: the inference-time generation mechanism is the larger contributor (AUC +0.076/+0.048, R² +0.166/+0.231), while graph discovery gains are task-selective. PAFT retains better pairwise fidelity; StructSynth leads on utility and privacy. [7Wh2-W1]

- **Exp-2 -- Feature anonymization.** Anonymizing all column names and descriptions to generic identifiers, StructSynth remains functional (statistical association scores compensate for the absent semantic prior), though results are task-dependent: classification utility degrades modestly (AUC 0.865→0.850) while regression degrades more (R² 0.560→0.462). Even the worst case exceeds unstructured baselines. [7Wh2-W4, iRH3-W3]

- **Exp-3 -- Post-cutoff vary-n experiments.** On Anxiety and Salary (both released after the LLM knowledge cutoff), StructSynth leads CLLM across all sample sizes on classification (largest margin at n=20: +3.31 AUC). Regression results are mixed: StructSynth leads only at n=100 (R² 55.98 vs. 54.53), with CLLM ahead at other sample sizes. These confirm that structural guidance is most valuable under scarcity for classification tasks, on datasets unseen during LLM pretraining. [q74j-W2]

- **Exp-4 -- Qwen3-32B backbone check.** StructSynth maintains consistent advantages under Qwen3-32B on both post-cutoff datasets, supporting LLM-backbone generality. [q74j-W2]

Together, these results confirm that StructSynth's improvements are attributable to the explicit graph-as-generation-plan design rather than LLM memorization, hold across post-cutoff datasets and LLM backbones, and complement rather than duplicate PAFT's fine-tuning approach.

**Artifacts.** We confirm that a complete code repository (graph discovery, conditional synthesis, evaluation pipeline), preprocessed datasets with train/test splits, configuration files, and random seeds are ready for release. An anonymous repository link will be provided in the revised submission.

**Revision plan.** In the revision we will: (1) cite PAFT and position it in Related Work as the fine-tuning route complementary to StructSynth's inference-time plan route, with the cross-system experiment as supplementary evidence; (2) replace "privacy preservation" with "empirical privacy behavior" and list formal privacy guarantees as a limitation; (3) report the utility–fidelity–privacy trade-off explicitly rather than implying comprehensive superiority; (4) include the anonymization and post-cutoff experiments; (5) move the "generation plan" definition earlier in the Introduction; (6) add baseline selection justification; (7) provide an anonymous code repository with all reproducibility artifacts.

We address each reviewer's concerns point-by-point in the individual responses below.
