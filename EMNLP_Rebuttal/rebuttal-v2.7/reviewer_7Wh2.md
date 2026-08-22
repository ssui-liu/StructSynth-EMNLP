# Response to Reviewer 7Wh2 (1/2)

We thank Reviewer 7Wh2 for the careful and thorough review. The central question is whether StructSynth is redundant given PAFT. We show it is not, at three levels: mechanism (inference-time execution vs. fine-tuning compilation), family-level evidence already in the submission (GraDe, Table 1), and a new direct comparison (Exp-1); Exp-2 additionally probes the opaque-schema boundary (W4).

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W1: Relationship to PAFT and Novelty

> "My main concern with this paper is that it is quite close to the paper by S. Xu et al. 'Why LLMs Are Bad at Synthetic Table Generation and what to do about it' [...] Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data. As a result, the novelty here is limited and further the experimental results need to be contrasted with this above paper and their PAFT algorithm [...]"

**PAFT compiles discovered dependencies into a feature order for fine-tuning an open-weight model; StructSynth executes the graph itself — generation order, conditioning context, prompt scope — as an inference-time plan for a black-box LLM (§3.2, l.281–297; Eq. 4).**

The three structure-aware routes differ operationally: PAFT turns discovered FDs into a global feature permutation for LoRA fine-tuning of DistilGPT2; GraDe injects FD supervision through dynamic sparse attention and an FD-alignment objective during GPT-2 fine-tuning; StructSynth performs no parameter update. To our knowledge, no prior method executes a discovered dependency graph as the generation plan for a black-box LLM; structure-aware predecessors (PAFT, GraDe) inject structure at fine-tuning time.

We agree both methods follow a "discover structure, then generate" template, and PAFT should have been cited — we will position it alongside GraDe in §1–§2. The template, however, is where the overlap ends.

The family-level contrast the review asks for is already in the submission: GraDe is, like PAFT, an FD-discovery-plus-FD-guided generator trained by fine-tuning, and under identical 100-shot splits and the same evaluation pipeline StructSynth leads it on all six datasets (average utility 75.01 vs. 51.05; Table 1). Exp-1 now extends the comparison to PAFT itself.

We evaluated bidirectional component transfer at 100 real rows and 1,000 synthetic rows with a unified XGBoost evaluator (Exp-1).

| Generator | Structural source | Avg. AUC | Avg. R² | Fidelity error ↓ | DCR deviation ↓ |
|---|---|---:|---:|---:|---:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

**The full StructSynth system leads the full PAFT system on every utility and privacy column (AUC 0.830 vs. 0.752; R² 0.591 vs. 0.360; DCR deviation 0.032 vs. 0.154).** Each component helps independently: swapping in the StructSynth graph improves both generators (+0.030/+0.022 AUC), and the StructSynth generator leads under both graphs (+0.056/+0.048). PAFT's stronger pairwise fidelity (0.537–0.540 vs. 0.580–0.595) reflects the fidelity–utility objective distinction discussed under W3. Protocol note: our PAFT reproduction uses a local FD approximation rather than full HyFD, so we read Exp-1 at the component level rather than as a leaderboard.

Because the plan is executed rather than trained in, the same discovered graph drives different backbones — the Qwen2.5-32B check preserves the advantage (Exp-4) — whereas a fine-tuned generator is bound to its base model. Removing the graph (−1.6 AUC), ignoring topological order (−1.1), or replacing the LLM executor with a Bayesian sampler (−4.4) each degrades utility (Table 3); the case study shows dependency pathways rediscovered from synthetic data (Appendix H.1, Figure 6).

*(continued in the next comment)*

<!-- BOX SPLIT -->

# Response to Reviewer 7Wh2 (2/2)

Continuing from (1/2); experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W2: Scope of the Privacy Evaluation

> "Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution."

We agree DCR evidence alone should not be read as a standalone privacy contribution, and the revision will reword §4.2 accordingly.

**StructSynth pairs the best utility rank (1.00) with the second-best privacy rank (1.50), a byproduct of conditioning each call on a local subgraph — observed under DCR (§4.2; Appendix K.2).**

DCR measures the proportion of synthetic records whose nearest neighbor is in the training rather than test set, with 0.50 as the empirical ideal (§4.2, l.394–421; Appendix K.2; Ethics, l.574–578). DCR is not differential privacy; the regularization effect was not designed as a privacy mechanism; and the submitted Ethics section already states that StructSynth offers no formal privacy guarantee. Appendix K.2 discusses the resulting fidelity–privacy trade-off.

## W3: Statistical Fidelity Trade-off

> "The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results)."

The reviewer is correct about the mixed ranking.

**Pairwise fidelity and downstream utility are different objectives: the Bayesian-Sampler ablation attains the best fidelity (48.86) yet the worst utility (81.17), while StructSynth holds utility rank 1.00 — the objective augmentation is used for (Table 3).**

Statistical Fidelity Error measures pairwise-correlation matching, whereas the generation graph encodes conditional parent–child dependencies (§4.2, l.356–359 and l.413–417; Appendix K.2). The submitted profile is utility rank 1.00, privacy rank 1.50, fidelity rank 8.50; the revision will report this trade-off explicitly in §5, and we do not claim comprehensive superiority.

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

Salary's larger regression drop (R² 0.560 → 0.462) shows semantic priors matter most for fine-grained continuous dependencies (full analysis in our response to Reviewer iRH3, W3). The two approaches compose rather than compete: when schemas are opaque, a statistically discovered FD graph plugs directly into StructSynth's executor — Exp-1's transfer cell (StructSynth generator + PAFT graph, AUC 0.808) already demonstrates this fallback.

**Revision plan.** We will: (1) cite/position PAFT §1–§2 (W1); (2) sharpen the contribution statement to inference-time graph execution, add Exp-1, and include PAFT as a baseline in the main comparison (W1); (3) correct GraDe description in Appendix G.2 (W1); (4) empirical-privacy wording in §4.2/Limitations (W2); (5) three-dimensional profile §5/Appendix K.2 (W3); (6) add Exp-2, opaque-schema boundary + statistical-graph fallback (W4); (7) direct structural metrics as future work (W1/W4).

We hope these results address your concerns — in particular the novelty assessment, in light of the clarified mechanism, the family-level GraDe comparison already in Table 1, and the direct PAFT study (Exp-1). We would be glad to run further analyses during the discussion period.
