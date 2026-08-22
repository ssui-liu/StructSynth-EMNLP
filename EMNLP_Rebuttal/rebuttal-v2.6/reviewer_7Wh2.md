# Response to Reviewer 7Wh2 (1/2)

We thank Reviewer 7Wh2 for the careful and thorough review. We acknowledge that PAFT should have been cited and contrasted explicitly. Below we address the four concerns in order using (i) Exp-1, a bidirectional StructSynth–PAFT component-transfer study; (ii) Exp-2, a task-and-field anonymization study; and (iii) submitted evidence on GraDe, structural ablations, privacy–fidelity trade-offs, and boundary conditions.

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W1: Relationship to PAFT and Novelty

> "My main concern with this paper is that it is quite close to the paper by S. Xu et al. 'Why LLMs Are Bad at Synthetic Table Generation and what to do about it' [...] Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data."

**The overlap is real at 'discover structure, then use it': PAFT compiles functional dependencies into a fine-tuning permutation, whereas StructSynth executes a directed dependency graph as an inference-time plan for a black-box LLM (Exp-1).**

The three structure-aware LLM routes differ operationally. PAFT turns discovered FDs into a global feature permutation for LoRA fine-tuning of DistilGPT2. GraDe injects FD supervision through dynamic sparse attention and an FD-alignment objective during GPT-2 fine-tuning. StructSynth performs no parameter update (§3.2, l.281–297; Eq. 4): topological layers set generation order, parent sets define conditioning context, and local subgraphs delimit prompt scope at inference time. Our contribution is therefore not first-mover status for structure-aware synthesis, but the explicit execution of a directed dependency graph as a generation plan in a low-data, black-box setting.

The evaluation already includes GraDe, a representative FD-guided fine-tuned generator (Table 1). Under identical 100-shot splits and the same evaluation pipeline, StructSynth leads GraDe on all six datasets (average utility 75.01 vs. 51.05). This coverage does not replace a direct PAFT comparison, which we now provide.

We evaluated bidirectional component transfer at 100 real rows and 1,000 synthetic rows with a unified XGBoost evaluator (Exp-1).

| Generator | Structural source | Avg. AUC | Avg. R² | Fidelity error ↓ | DCR deviation ↓ |
|---|---|---:|---:|---:|---:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

Both graph representations can be used across the two generation mechanisms, while PAFT retains better pairwise fidelity and StructSynth retains stronger utility and privacy behavior in this comparison. 

Complementary evidence shows that removing the graph (−1.6 AUC), ignoring topological order (−1.1), or replacing the LLM generator with a Bayesian sampler (−4.4) harms utility (Table 3); the case study compares dependency pathways rediscovered from synthetic data with the reference graph (Appendix H.1/Figure 6). We present these as supporting evidence of structural preservation.

*(continued in the next comment)*

<!-- BOX SPLIT -->

# Response to Reviewer 7Wh2 (2/2)

Continuing from (1/2); experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W2: Scope of the Privacy Evaluation

> "Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution."

**We agree the current privacy evidence should not be elevated into a standalone contribution: DCR is an empirical diagnostic of nearest-neighbor behavior, not a claimed privacy guarantee.**

DCR measures the proportion of synthetic records whose nearest neighbor is in the training rather than test set, with 0.50 as the empirical ideal (§4.2, l.394–421; Appendix K.2; Ethics, l.574–578). StructSynth has privacy rank 1.50 while retaining utility rank 1.00, consistent with the observed regularization effect of conditioning each call on a local subgraph. However, DCR is not differential privacy; the regularization effect was not designed as a privacy mechanism; and the submitted Ethics section explicitly states that StructSynth offers no formal privacy guarantee. Appendix K.2 already discusses the resulting fidelity–privacy trade-off.

## W3: Mixed Statistical Fidelity

> "The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results)."

The reviewer is correct about the mixed ranking. **StructSynth's submitted profile is a three-dimensional trade-off — utility rank 1.00, privacy rank 1.50, fidelity rank 8.50 — rather than uniform dominance, and we do not claim comprehensive superiority.**

Moderate pairwise fidelity is consistent with a design emphasizing conditional generation and downstream utility. Statistical Fidelity Error measures pairwise-correlation matching, whereas the generation graph encodes conditional parent–child dependencies (§4.2, l.356–359 and l.413–417; Table 3; Appendix K.2). The Bayesian-Sampler ablation makes the distinction unusually clear: it attains the best fidelity (48.86) yet the lowest AUC (81.17). Thus, pairwise correlation recovery and downstream utility are different objectives; stronger performance on one does not establish strength on the other.

## W4: Opaque and Anonymized Schemas

> "The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies)."

We appreciate the reviewer identifying this genuine comparative advantage of statistical FD discovery. **StructSynth remains functional under anonymization (Exp-2), but the mixed results confirm that semantic priors contribute to utility, especially for regression.**

The paper already identifies opaque schemas as a boundary condition and positions StructSynth as best suited to low-data settings with interpretable fields (Appendix K.3). In an exploratory run (Exp-2), we anonymized all column names and task/column descriptions while keeping values unchanged *(gpt-5-mini, single seed 42, 100 real rows, 1,000 synthetic rows; 0–1 scale)*.

| Dataset | Condition | Utility | Fidelity ↓ | DCR (ideal 0.50) |
|---|---|---:|---:|---:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R² 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | 0.615 | 0.412 |

Anxiety shows a modest utility decrease but better fidelity, while Salary shows a larger regression decrease. The result is mixed rather than uniformly robust. Classification utility degrades modestly while regression degrades more, confirming that semantic priors contribute to performance — especially for fine-grained continuous dependencies. See the full analysis in our response to Reviewer iRH3. This is a genuine trade-off — yet the two approaches compose rather than compete: when schemas are opaque, a statistically discovered FD graph can be plugged directly into StructSynth's executor — Exp-1's transfer cell (StructSynth generator + PAFT FD graph) already demonstrates this fallback path.

**Revision plan.** We will: (1) cite/position PAFT §1–§2 (W1); (2) narrow contribution to inference-time graph execution, add Exp-1 with caveats (W1); (3) correct GraDe description in Appendix G.2 (W1); (4) empirical-DCR wording §4.2/Limitations (W2); (5) three-dimensional profile §5/Appendix K.2 (W3); (6) add Exp-2, opaque-schema boundary + statistical-graph fallback (W4); (7) direct structural metrics as future work (W1/W4).

We hope these results address your concerns; we would be glad to run further analyses during the discussion period — particularly the novelty assessment in light of the clarified mechanism and the direct PAFT comparison.
