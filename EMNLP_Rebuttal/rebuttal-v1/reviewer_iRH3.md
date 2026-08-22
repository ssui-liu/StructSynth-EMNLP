# Response to Reviewer iRH3

**Total response word count: ~800 words (excluding tables and reviewer quotations)**

## Reviewer Scores

| Dimension | Score |
|---|---|
| Overall Assessment | 3 (Findings) |
| Confidence | 3 |
| Soundness | 3.5 |
| Excitement | 3 |
| Reproducibility | 4 |
| Datasets | 3 |
| Software | 4 |

We sincerely thank Reviewer iRH3 for the careful reading and constructive feedback. We appreciate the recognition of our work's practical value, the convincing experimental results, and the qualitative insights from the learned dependency graphs. We address each weakness below, including a new anonymization experiment (Exp-2; see also General Response).

---

## W1: Graph Structure Correctness Evaluation
**[Evaluating correctness of learned graph structure, particularly edge directions, on ground-truth datasets]**

> "it would also be valuable to evaluate the correctness of the learned graph structure, particularly edge directions, on datasets where ground-truth dependency structures are available."

Thank you for this suggestion. We would like to draw attention to the fact that our paper already includes exactly the evaluation you describe. In Section 4.4 "Structural Fidelity under Ground-Truth Graphs" (l.470--490), we evaluate structure discovery quality on three bnlearn benchmark datasets with known ground-truth DAGs -- Asia (8 nodes), Child (20 nodes), and Insurance (27 nodes) -- using the **Structural Hamming Distance (SHD)**, which counts edge insertions, deletions, and reversals needed to recover the true graph (lower is better).

As shown in Figure 3, StructSynth achieves the lowest or near-lowest SHD on all three datasets across varying sample sizes (n in {20, 50, 100, 200}). The advantage is most pronounced in low-data settings (n <= 50), where purely data-driven graph-learning methods such as FCI, GOGGLE, and NoTears produce substantially higher structural errors. This confirms that the LLM's semantic prior effectively complements weak statistical signals, enabling robust structure recovery -- including edge directions -- even from severely limited samples.

These findings are further corroborated by our ablation study (Table 3, Section 4.3), where substituting our LLM-guided graph discovery with classical alternatives -- PC Discovery (-1.0 AUC) and NoTears Discovery (-1.4 AUC) -- degrades downstream performance, while ignoring topological order (-1.1 AUC) confirms that the learned edge directions carry functional signal for generation quality.

We apologize if these results were not sufficiently prominent; we will revise the section title to make it more immediately clear that this evaluation directly addresses edge direction accuracy on ground-truth DAGs (e.g., "Edge Direction Accuracy on Ground-Truth DAGs").

---

## W2: Larger Sample Sizes (n > 200)
**[Understanding method behavior as more data become available]**

> "it is important to understand how the method behaves as more data become available. Experiments with larger sample sizes would help clarify the trade-off between the advantages of LLM-based graph construction and purely data-driven alternatives."

Thank you for raising this point. Following previous work on LLM-based tabular synthesis -- including CLLM (Seedat et al., 2024) and GReaT (Borisov et al., 2023) -- our experiments focus on the **low-data regime (n <= 200)**, which is the setting where StructSynth's core contribution is most relevant: leveraging LLM semantic priors to compensate for insufficient statistical signals in structure discovery (l.040--047).

Our existing vary-n analysis (Section 4.5, Figure 4) on the Adult dataset already provides insight into the scaling trend. StructSynth maintains high AUC, low fidelity error, and near-zero privacy deviation across all sample sizes, with the advantage most pronounced at n <= 50 where baselines like BN and GOGGLE require significantly more samples to become competitive (l.496--500). The generation plan acts as a regularizer that prevents record-level overfitting, yielding a stable utility-fidelity-privacy balance independent of sample size (l.500--505).

Based on these trends and the method's design, we expect that as n grows beyond 200, StructSynth will **not degrade** -- its statistical association component (Cramer's V, |r|, correlation ratio) naturally becomes more accurate with larger samples -- but its **marginal advantage over purely data-driven methods will narrow**, as the LLM semantic prior's relative contribution diminishes. This is consistent with the SHD trends in Figure 3, where data-driven methods (FCI, NoTears) gradually approach StructSynth's structural accuracy as n increases. We will add an explicit discussion of StructSynth's target operating range and the expected convergence with data-driven alternatives in the revision.

---

## W3: Anonymized Feature Names
**[Fairness of comparison given that LLM baselines exploit semantic feature names]**

> "An informative additional experiment would be to anonymize feature names (e.g., replacing them with V1, V2, ...) and evaluate how much the performance depends on semantic information provided by the feature names."

We fully agree with this concern and have conducted the suggested experiment (Exp-2). We anonymized all column names (e.g., Age to feature_01), replaced domain-specific task descriptions with generic text, and anonymized column descriptions -- while keeping cell values intact. Experiments used 100 real training samples.

| Dataset | Condition | Utility | Fidelity (lower is better) | DCR (ideal = 0.50) |
|---|---|---|---|---|
| Anxiety | Original | AUC **0.865** | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | **0.534** | 0.564 |
| Salary | Original | R^2 **0.560** | 0.646 | 0.501 |
| Salary | Anonymized | R^2 0.462 | **0.615** | 0.412 |

On Anxiety, the anonymized variant shows a modest utility decrease (AUC 0.865 to 0.850) but substantially better fidelity (0.579 to 0.534), suggesting that some semantically inferred edges may be spurious and a sparser data-driven graph can provide a more precise structural prior. On Salary, the original retains a clear advantage (R^2 0.560 vs. 0.462), indicating that semantic priors contribute more to regression tasks involving fine-grained continuous dependencies.

This mixed result is informative: StructSynth remains functional under anonymization because the statistical association scores (Cramer's V, |r|, correlation ratio; Section 3.1.2) compensate for the absent semantic prior -- confirming the design rationale described in l.249--258. Importantly, even in the worst case (Salary), the anonymized variant's R^2 of 0.462 remains well above the levels achieved by unstructured baselines in Table 1, demonstrating that the performance gains stem primarily from the learned structural dependencies rather than memorized domain knowledge from feature names. We will include these results in the revision alongside an honest discussion of the task-dependent contribution of semantic priors.

---

**Revision plan.** In the camera-ready version, we will: (1) revise the Section 4.4 title to explicitly reference edge direction evaluation on ground-truth DAGs; (2) add a discussion of StructSynth's target operating range and expected behavior at larger sample sizes; (3) include the anonymization experiment with full results and analysis in the appendix.

We are grateful for the reviewer's thoughtful and constructive suggestions, each of which has helped strengthen the paper. We hope our responses adequately address the concerns raised and would be happy to provide any additional clarification.
