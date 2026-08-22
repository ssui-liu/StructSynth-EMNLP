# Response to Reviewer 7Wh2 (1/2)

We thank Reviewer 7Wh2 for the careful and thorough review. The central question is whether StructSynth is redundant given PAFT. We show it is not, at three levels: mechanism (inference-time execution vs. fine-tuning compilation), family-level evidence already in the submission (GraDe, Table 1), and a new direct comparison (Exp-1); Exp-2 additionally probes the opaque-schema boundary (W4).

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W1: Relationship to PAFT and Novelty

> "My main concern with this paper is that it is quite close to the paper by S. Xu et al. 'Why LLMs Are Bad at Synthetic Table Generation and what to do about it' [...] Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data. As a result, the novelty here is limited and further the experimental results need to be contrasted with this above paper and their PAFT algorithm [...]"

**Both methods are structure-aware, but the structure plays a different operational role.** PAFT mines functional dependencies and compiles them into a global feature order for LoRA fine-tuning; StructSynth builds a DAG from semantic and statistical evidence and executes it at inference to control generation order, conditioning context, and prompt scope for a black-box LLM, without parameter updates (§3.1–§3.2; Eq. 4).

We agree both methods follow a "discover structure, then generate" template, and PAFT should have been cited — we will position it in §1–§2. The template, however, is where the operational overlap ends: this distinction is most consequential in our target low-data regime, where semantic priors complement weak association estimates and StructSynth achieves the lowest or near-lowest SHD at n ≤ 50 (§4.4).

The family-level contrast the review asks for is already in the submission: GraDe is, like PAFT, an FD-discovery-plus-FD-guided generator trained by fine-tuning, and under identical 100-shot splits and the same evaluation pipeline StructSynth leads it on all six datasets (average utility 75.01 vs. 51.05; Table 1). To our knowledge, no prior method executes a discovered dependency graph as the generation plan for a black-box LLM; structure-aware predecessors (PAFT, GraDe) inject structure at fine-tuning time.

Exp-1 now extends the comparison to PAFT itself: we evaluated bidirectional component transfer at 100 real rows and 1,000 synthetic rows with a unified XGBoost evaluator.

| Generator | Structural source | Avg. AUC | Avg. R² | Fidelity error ↓ | DCR deviation ↓ |
|---|---|---:|---:|---:|---:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

**In this descriptive comparison, the full StructSynth system leads the full PAFT system on every utility and privacy column (AUC 0.830 vs. 0.752; R² 0.591 vs. 0.360; DCR deviation 0.032 vs. 0.154).** The component-transfer rows isolate the contribution of the structural source: holding the generator fixed, the StructSynth dependency graph consistently improves downstream utility over the PAFT FD graph. Under the PAFT generator it raises classification AUC by +0.030 (0.752 → 0.782) and R² by +0.044; under the StructSynth executor the gains are similar (AUC 0.808 → 0.830; R² 0.550 → 0.591). Cross-compatibility is preserved in the reverse direction (a PAFT FD graph can still drive the StructSynth executor at AUC 0.808), confirming the two structural representations are interchangeable at the interface level while differing in downstream strength.

## W2: Scope of the Privacy Evaluation

> "Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution."

We agree DCR evidence alone should not be read as a standalone privacy contribution; the revision will replace the "privacy preservation" wording (abstract, §1, §4.2, §5) with empirical-privacy language.

**StructSynth pairs the best utility rank (1.00) with the best privacy rank (1.50), which we attribute to conditioning each generation call on a local subgraph (§4.2; Appendix K.2).**

DCR is not differential privacy; the regularization effect was not designed as a privacy mechanism; and the submitted Ethics section already states that StructSynth offers no formal privacy guarantee (Ethics, l.574–578). Appendix K.2 discusses the resulting fidelity–privacy trade-off.

*(continued in the next comment)*

<!-- BOX SPLIT -->

# Response to Reviewer 7Wh2 (2/2)

Continuing from (1/2); experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W3: Statistical Fidelity Trade-off

> "The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results)."

The reviewer is correct about the mixed ranking.

**Pairwise fidelity and downstream utility are different objectives: the Bayesian-Sampler ablation attains the lowest fidelity error (48.86) yet the worst utility (81.17), while StructSynth holds utility rank 1.00 — the objective for which augmentation is deployed (Table 3).**

Fidelity error measures pairwise-correlation matching, whereas the generation graph encodes conditional parent–child dependencies (§4.2, l.356–359 and l.413–417; Appendix K.2). The same tension appears among the real baselines, where high fidelity often stems from memorization: BN ranks 3.00 on fidelity error but 9.00 on privacy, and GReaT ranks 4.00 on fidelity error with the worst privacy risk (90.15%) (§4.2, l.396–404; Table 2). The submitted profile is utility rank 1.00, privacy rank 1.50, fidelity rank 8.50; the revision will report this trade-off explicitly in §5, and we do not claim comprehensive superiority.

## W4: Opaque and Anonymized Schemas

> "The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies)."

Opaque schemas do weaken the semantic prior — the submission flags exactly this boundary (Appendix K.3).

**Under full anonymization of names and descriptions, StructSynth stays functional — classification loses 1.5 AUC points while fidelity improves — because association scores keep the graph populated when semantics are absent (Exp-2).**

We anonymized all column names and task/column descriptions while keeping values unchanged (Exp-2) *(gpt-5-mini, 100 real rows, 1,000 synthetic rows; 0–1 scale)*.

| Dataset | Condition | Utility | Fidelity ↓ | DCR (ideal 0.50) |
|---|---|---:|---:|---:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R² 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | 0.615 | 0.412 |

Salary's larger regression drop (R² 0.560 → 0.462) shows semantic priors matter most for fine-grained continuous dependencies (full analysis in our response to Reviewer iRH3, W3). This limitation is mirrored on the PAFT side: FD discovery plus fine-tuning requires statistical signal and parameter access — the two resources scarcest in our target regime — whereas StructSynth runs against black-box APIs and its graph transfers across eight backbones (§4.6, Figure 5). The two approaches therefore compose rather than compete: when schemas are opaque, a statistically discovered FD graph plugs directly into StructSynth's executor — Exp-1's transfer cell (StructSynth generator + PAFT graph, AUC 0.808) already demonstrates this fallback.

**Revision plan.** We will: (1) cite/position PAFT §1–§2 (W1); (2) sharpen the contribution statement to inference-time graph execution, add Exp-1, and include PAFT as a baseline in the main comparison (W1); (3) correct GraDe description in Appendix G.2 (W1); (4) empirical-privacy wording in the abstract, §1, §4.2, §5, and Limitations (W2); (5) three-dimensional profile §5/Appendix K.2 (W3); (6) add Exp-2, opaque-schema boundary + statistical-graph fallback (W4); (7) direct structural metrics as future work (W1/W4).

We hope these results address your concerns — in particular the novelty assessment, in light of the two-step differentiation, the family-level GraDe comparison already in Table 1, and the direct PAFT study (Exp-1). We would be glad to run further analyses during the discussion period.
