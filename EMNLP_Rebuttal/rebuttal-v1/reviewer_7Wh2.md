# Response to Reviewer 7Wh2

**Total response word count: ~1,200 words (excluding tables and reviewer quotations)**

## Reviewer Scores

| Dimension | Score |
|---|---|
| Overall Assessment | 2 (Resubmit next cycle) |
| Confidence | 5 |
| Soundness | 3 |
| Excitement | 1.5 |
| Reproducibility | 4 |
| Datasets | 4 |
| Software | 4 |

We thank Reviewer 7Wh2 for the careful reading and expert-level feedback. We acknowledge the missing PAFT citation and address each concern below with new cross-system experiments and an anonymization study.

---

## W1: Relationship to PAFT and Novelty
**[Novelty limited relative to PAFT (Xu et al., 2024); both learn a DAG and use it for generation; experimental comparison needed]**
> "My main concern with this paper is that it is quite close to the paper by S. Xu et al. 'Why LLMs Are Bad at Synthetic Table Generation and what to do about it' [...] Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data. As a result, the novelty here is limited and further the experimental results need to be contrasted with this above paper and their PAFT algorithm."

We should have cited and discussed PAFT. We will add the citation and a detailed comparison in the revision. PAFT and StructSynth share the insight that autoregressive tabular synthesis benefits from explicit dependency structure, but operationalize it through different paradigms. We will revise our contribution statement accordingly and clarify that our novelty lies not in being the first structure-aware approach, but in using a directed dependency graph as an inference-time generation plan in a low-data, black-box setting.

**Mechanism distinction.** PAFT, GraDe (already included in our baselines), and StructSynth all leverage dependency structure for tabular synthesis but differ in three key dimensions. PAFT compiles discovered functional dependencies into a global feature permutation for LoRA fine-tuning (DistilGPT2). GraDe injects FD supervision through a dynamic sparse attention graph and an FD-alignment objective during GPT-2 fine-tuning. StructSynth instead uses a directed dependency graph as an inference-time generation plan (§3.2, l.281--297): topological layers determine generation order, parent-node sets determine conditioning context, and local subgraphs determine prompt scope (Eq. 4). Thus, our contribution concerns how dependency structure is explicitly executed at generation time in a black-box, zero-parameter-update setting, rather than the broader idea of structure-aware tabular synthesis itself.

**Existing coverage of FD-guided generators.** Our submitted evaluation already includes GraDe (Table 1), a structure-aware LLM generator that builds on the diagnosis that random feature orders may violate functional dependencies. Both PAFT and GraDe use externally extracted functional dependencies, although they inject them differently: PAFT converts them into a fixed topological permutation, whereas GraDe uses a learned sparse attention graph and an FD-alignment objective. Under the same 100-shot splits, ten seeds, 1,000 generated samples, and evaluation pipeline, StructSynth outperforms GraDe on all six datasets (avg. 75.01 vs. 51.05). This comparison shows that our evaluation already covers a representative FD-guided, fine-tuned generator, but it does not substitute for a direct comparison with PAFT.

**Component-transfer comparison with PAFT.** To provide a direct comparison, we conducted a component-transfer experiment (100 real rows, 1,000 synthetic rows, unified XGBoost evaluation) and present the four generator--structural-source combinations below:

| Generator | Structural source | Avg AUC | Avg R^2 | Fidelity error (lower is better) | DCR deviation (lower is better) |
|:--|:--|--:|--:|--:|--:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

We note several methodological caveats: (1) our PAFT reproduction uses a local FD approximation rather than the full HyFD pipeline; (2) seed counts differ across conditions (5--10); and (3) PAFT uses fine-tuned DistilGPT2 while StructSynth uses a black-box LLM, reflecting each method's design rather than a controlled variable. Accordingly, the 2x2 layout is descriptive rather than a controlled factorial design. We interpret the results as preliminary evidence that the two types of graph representations are usable across both generation mechanisms, not as estimates of independent component effects or a definitive ranking.

**Supporting evidence from existing results.** We acknowledge that downstream utility is only an indirect measure of structural preservation. StructSynth's consistent rank-1 performance across six datasets (Table 1) indicates that the generated data preserve statistical signals useful for both classification and regression, but does not by itself establish faithful dependency preservation. Our ablation study (Table 3) offers complementary evidence: removing the graph (−1.6 AUC), ignoring topological order (−1.1 AUC), or replacing the LLM generator (−4.4 AUC) each reduces downstream performance. In addition, the case study in §4.5 shows qualitative similarity between dependency pathways rediscovered from synthetic data and the reference graph. We will present these as supporting rather than conclusive evidence in the revision.

**Revision commitments:**
1. Cite PAFT in the Introduction and Related Work; position PAFT, GraDe, and StructSynth within a shared structure-aware synthesis space, clarifying their distinct paradigms
2. Narrow the contribution statement to focus on using a directed dependency graph as an inference-time generation plan, rather than implying first-mover status in structure-aware tabular synthesis
3. Include the PAFT component-transfer comparison with methodological caveats explicitly disclosed
4. Correct the Appendix §A.2 baseline description: GraDe uses the authors' official implementation (including HyFD-based FD extraction and dynamic graph attention), not the SynthCity library
5. Demote backbone and post-cutoff experiments to supplementary evidence
6. Discuss more direct structural evaluation metrics (e.g., FD violation rates, conditional-distribution fidelity) as an important future work direction

---

## W2: Underdeveloped Privacy Evaluation
**[Privacy evaluation feels underdeveloped and is not quite a contribution]**
> "Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution."

We agree that privacy should not be overclaimed. Our paper (Section 4.2, l.394--421) uses Privacy Risk (DCR) -- the proportion of synthetic records whose nearest neighbor is in the training set (ideal = 0.50) -- as an **empirical diagnostic**, not a formal privacy guarantee. StructSynth achieves the best privacy rank (1.50) among all methods while maintaining competitive utility (Table 2), and we attribute this to the generation plan's **regularization effect** (l.417--421): constraining each LLM call to a local subgraph prevents overfitting to individual records.

However, we acknowledge that: (a) DCR is an empirical nearest-neighbor metric, not a formal guarantee such as differential privacy; (b) the regularization effect is an architectural observation, not an intentionally designed privacy mechanism; and (c) the paper's Ethics section (l.574--578) already states that "StructSynth is not a formal privacy mechanism."

**Revision commitment.** We will replace "privacy preservation" with "empirical privacy behavior," explicitly define DCR's limitations, list the absence of formal privacy guarantees as a limitation, and discuss membership-inference evaluation and formal privacy integration as future work.

---

## W3: Mixed Statistical Fidelity Results
**[The algorithm appears middle of the pack on statistical fidelity]**
> "The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results)."

The moderate fidelity is a **predictable consequence of StructSynth's design, not a deficiency**. Statistical Fidelity Error (l.356--359) measures **pairwise correlation** matching, whereas StructSynth's DAG encodes **conditional dependencies** between parent and child nodes -- the relationships that actually drive downstream model performance (l.413--417). The Bayesian Sampler ablation (Table 3) makes this explicit: it achieves the **best fidelity (48.86)** yet the **lowest AUC (81.17)**, confirming that pairwise-correlation recovery and downstream utility are fundamentally different objectives.

StructSynth's overall profile is a coherent three-dimensional trade-off: **utility rank 1.00** (Table 1), **privacy rank 1.50**, and **fidelity rank 8.50** (Table 2). The generation plan regularizes against record-level memorization, which improves utility and privacy at the cost of exact marginal-correlation recovery. We will revise language such as "competitive statistical fidelity" (Section 5, l.530--531) to report this trade-off more precisely.

---

## W4: Opaque / Anonymized Schemas
**[Opaque schemas weaken the LLM semantic prior; PAFT may not have this problem]**
> "The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies)."

Our Limitations section (l.539--550) already acknowledges this boundary. We conducted an **anonymization experiment** to quantify the impact. Column names were replaced with `feature_01, feature_02, ...`, task and column descriptions were replaced with generic text, while cell values were kept intact (100 real shots, 1,000 synthetic rows):

| Dataset | Condition | Utility | Fidelity (lower is better) | DCR (ideal = 0.50) |
|:--|:--|:--|--:|--:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R^2 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R^2 0.462 | 0.615 | 0.412 |

StructSynth **remains functional** under anonymization: the statistical association scores (Cramer's V, |r|, correlation ratio; Section 3.1.2, l.249--258) take over graph discovery. On Anxiety, anonymization slightly reduces utility (AUC 0.865 to 0.850) but improves fidelity (0.579 to 0.534), suggesting some semantically inferred edges were spurious. On Salary, the drop is larger (R^2 0.560 to 0.462), indicating semantic priors contribute more to regression tasks. Even in the worst case, the anonymized R^2 of 0.462 remains above unstructured baselines in Table 1.

The result is **mixed rather than uniformly robust** -- we will report this honestly. The reviewer is correct that PAFT's purely statistical FD discovery may be less sensitive to opaque schemas; this is a genuine trade-off between the two approaches.

---

## Revision Summary

1. Cite PAFT and position it in Related Work as the fine-tuning route complementary to StructSynth's inference-time plan route; include the 2x2 cross-system experiment as supplementary evidence
2. Replace "privacy preservation" with "empirical privacy behavior" and list the formal privacy guarantee gap as a limitation
3. Report the utility--fidelity--privacy trade-off explicitly, replacing "competitive statistical fidelity" with precise three-dimensional language
4. Include the anonymization experiment with honest mixed conclusions; position opaque schemas as an explicit limitation

We hope these results and clarifications address the reviewer's concerns. We would be glad to run further analyses during the discussion period.
