# Response to Reviewer 7Wh2

We thank Reviewer 7Wh2 for the careful, expert-level review. We acknowledge that PAFT should have been cited and contrasted explicitly. Below we address the four concerns in order using (i) Exp-1, a bidirectional StructSynth–PAFT component-transfer study; (ii) Exp-2, a task-and-field anonymization study; and (iii) submitted evidence on GraDe, structural ablations, privacy–fidelity trade-offs, and boundary conditions. Evidence already in the submission is marked [Submitted].

## W1: Relationship to PAFT and Novelty

> "My main concern with this paper is that it is quite close to the paper by S. Xu et al. 'Why LLMs Are Bad at Synthetic Table Generation and what to do about it' […] Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data."

We appreciate this important correction to our related-work positioning. **Direct answer.** The overlap is real at the level of “discover structure, then use it,” but PAFT compiles functional dependencies into a fine-tuning permutation, whereas StructSynth executes a directed graph as an inference-time plan for a black-box LLM; we will cite PAFT and narrow our claims accordingly.

[Submitted, §3.2, l.281–297 and Eq. 4] The three structure-aware LLM routes differ operationally. PAFT turns discovered FDs into a global feature permutation for LoRA fine-tuning of DistilGPT2. GraDe injects FD supervision through dynamic sparse attention and an FD-alignment objective during GPT-2 fine-tuning. StructSynth performs no parameter update: topological layers set generation order, parent sets define conditioning context, and local subgraphs delimit prompt scope at inference time. Our contribution is therefore not first-mover status for structure-aware synthesis, but the explicit execution of a directed dependency graph as a generation plan in a low-data, black-box setting.

[Submitted, Table 1] The evaluation already includes GraDe, a representative FD-guided fine-tuned generator. Under identical 100-shot splits and the same evaluation pipeline, StructSynth leads GraDe on all six datasets (average utility 75.01 vs. 51.05). This coverage does not replace a direct PAFT comparison, which we now provide.

[New, Exp-1] We evaluated bidirectional component transfer at 100 real rows and 1,000 synthetic rows with a unified XGBoost evaluator.

| Generator | Structural source | Avg. AUC | Avg. R² | Fidelity error ↓ | DCR deviation ↓ |
|---|---|---:|---:|---:|---:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

**Takeaway:** Both graph representations can be used across the two generation mechanisms, while PAFT retains better pairwise fidelity and StructSynth retains stronger utility and privacy behavior in this descriptive comparison.

This comparison is descriptive, not factorial: our PAFT reproduction uses a local approximation rather than full HyFD, conditions use 5 versus 10 seeds, and generators differ (fine-tuned DistilGPT2 vs. a black-box LLM). It cannot isolate graph or generator effects or support a definitive ranking.

[Submitted, Table 3; Appendix H.1/Figure 6] Complementary evidence shows that removing the graph (−1.6 AUC), ignoring topological order (−1.1), or replacing the LLM generator with a Bayesian sampler (−4.4) harms utility; the case study compares dependency pathways rediscovered from synthetic data with the reference graph. We present these as supporting, not conclusive, evidence of structural preservation.

Downstream utility remains an indirect structural measure, so none of these results proves faithful recovery of every dependency. Direct FD-violation rates and conditional-distribution fidelity would provide a stronger test; we will identify both as future evaluation directions rather than infer them from utility.

**Revision (R1–R3, R7).** We will cite and position PAFT in §1–§2, narrow the contribution claim to inference-time graph execution, include Exp-1 with all caveats, correct Appendix G.2 to state that GraDe uses its official implementation rather than SynthCity, and flag direct structural metrics as future work.

## W2: Scope of the Privacy Evaluation

> "Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution."

We agree that the current privacy evidence should not be elevated into a standalone contribution. **Direct answer.** DCR is an empirical diagnostic of nearest-neighbor behavior, not a claimed privacy guarantee.

[Submitted, §4.2, l.394–421; Appendix K.2; Ethics, l.574–578] DCR measures the proportion of synthetic records whose nearest neighbor is in the training rather than test set, with 0.50 as the empirical ideal. StructSynth has privacy rank 1.50 while retaining utility rank 1.00, consistent with the observed regularization effect of conditioning each call on a local subgraph. However, DCR is not differential privacy; the regularization effect was not designed as a privacy mechanism; and the submitted Ethics section explicitly states that StructSynth offers no formal privacy guarantee. Appendix K.2 already discusses the resulting fidelity–privacy trade-off.

**Takeaway:** The result supports favorable empirical privacy behavior under DCR, but neither a formal guarantee nor a privacy contribution.

**Revision (R4).** We will replace “privacy preservation” with “empirical privacy behavior,” state DCR’s limitations, and identify membership-inference evaluation and formal privacy integration as future work.

## W3: Mixed Statistical Fidelity

> "The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results)."

The reviewer is correct about the mixed ranking. **Direct answer.** Moderate pairwise fidelity is consistent with a design emphasizing conditional generation and downstream utility, and we will not imply comprehensive superiority.

[Submitted, §4.2, l.356–359 and l.413–417; Table 3; Appendix K.2] Statistical Fidelity Error measures pairwise-correlation matching, whereas the generation graph encodes conditional parent–child dependencies. The Bayesian-Sampler ablation makes the distinction unusually clear: it attains the best fidelity (48.86) yet the lowest AUC (81.17). Thus, pairwise correlation recovery and downstream utility are different objectives; stronger performance on one does not establish strength on the other.

**Takeaway:** StructSynth’s submitted profile is a three-dimensional trade-off—utility rank 1.00, privacy rank 1.50, and fidelity rank 8.50—rather than uniform dominance.

**Revision (R5).** We will replace “competitive statistical fidelity” in §5 with this precise utility–privacy–fidelity profile and retain the full trade-off discussion in Appendix K.2.

## W4: Opaque and Anonymized Schemas

> "The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies)."

We appreciate the reviewer identifying this genuine comparative advantage of statistical FD discovery. **Direct answer.** StructSynth remains functional under anonymization, but the mixed results confirm that semantic priors contribute to utility, especially for regression.

[Submitted, Appendix K.3] The paper already identifies opaque schemas as a boundary condition and positions StructSynth as best suited to low-data settings with interpretable fields. [New, Exp-2] In an exploratory run, we anonymized all column names and task/column descriptions while keeping values unchanged *(gpt-5-mini, single seed 42, 100 real rows, 1,000 synthetic rows)*.

| Dataset | Condition | Utility | Fidelity ↓ | DCR → 0.50 |
|---|---|---:|---:|---:|
| Anxiety | Original | **AUC 0.865** | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | **0.534** | 0.564 |
| Salary | Original | **R² 0.560** | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | **0.615** | 0.412 |

**Takeaway:** Anxiety shows a modest utility decrease but better fidelity, while Salary shows a larger regression decrease. The result is mixed rather than uniformly robust.

StructSynth remains functional because the statistical association scores can compensate for missing semantic cues, but the reviewer is correct that PAFT's statistical FD discovery may be less sensitive to opaque schemas. This is a genuine trade-off between the two approaches.

**Revision (R6).** We will add Exp-2 to the appendix, state the opaque-schema limitation explicitly, and describe statistical graph priors as the appropriate fallback when semantic evidence is weak.

## Summary of Revisions

| # | Change | Where |
|---|---|---|
| R1 | Cite and position PAFT within structure-aware synthesis | §1, §2 |
| R2 | Narrow the contribution to inference-time graph execution; add Exp-1 with caveats | §1, Appendix |
| R3 | Correct the GraDe implementation description | Appendix G.2 |
| R4 | Replace privacy-guarantee language with empirical DCR language | §4.2, Limitations |
| R5 | Report the three-dimensional utility–privacy–fidelity trade-off | §5, Appendix K.2 |
| R6 | Add Exp-2 and make the opaque-schema boundary explicit | Appendix, Limitations |
| R7 | Identify direct structural metrics (e.g., FD violations and conditional fidelity) as future work | Limitations |

These commitments make no claims beyond the submitted and new evidence above. If our responses resolve the concerns, we would be grateful if the reviewer would consider revisiting the assessment, particularly the novelty concern in light of the clarified mechanism and direct PAFT comparison.
