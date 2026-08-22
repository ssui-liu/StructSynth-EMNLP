# Response to Reviewer q74j

We thank Reviewer q74j for the careful and constructive review, and especially for recognizing the paper's writing, experimental design, and ablations. Below, we address each point in order. New evidence comprises [New, Exp-3], a post-cutoff vary-$n$ study, and [New, Exp-4], a Qwen3-32B backbone check; evidence already present in the submission is marked [Submitted].

Before the itemized responses, we would like to clarify one factual point regarding the Reproducibility / Datasets / Software assessments (1/1/1). [Submitted, Appendix A, l.855-859] An anonymized implementation and accompanying instructions were included in the original submission. We suspect this artifact may have been missed; the additional replication assets are detailed in the checklist below.

## W1: Baseline Selection

> "It is not clear whether the baselines used are the best available methods in their respective categories. [...] I expected a little explanation in the experiments section that motivates the choice for the particular models used as baselines."

The request for a clearer selection rationale is well taken. **Direct answer.** We selected twelve baselines to cover three distinct paradigms, with both a foundational method and a recent representative in each, under the same low-data setting targeted by StructSynth.

[Submitted, §4.1, l.334-348] The suite covers DGMs (TVAE/CTGAN, TabDDPM, NFlow, TabSyn), structure-aware methods (BN, GOGGLE, DECAF, SPADA-NF), and LLM-based methods (GReaT, CLLM, GraDe). TabSyn (2024), SPADA-NF (2025), and GraDe (2025) ensure that every category includes a recent method, while the established methods provide recognizable anchors. Evaluating all methods at $n=100$ is deliberate because data scarcity is the paper's target condition; Table 1 reports average scores of 63.69 for TabDDPM and 68.04 for TabSyn in this regime, illustrating why large-sample reputation alone is not an adequate selection criterion here.

**Takeaway:** The comparison is broad across paradigms and current within each paradigm, but the manuscript should state this selection rule explicitly.

**Revision (R1).** We will add the paradigm coverage, temporal coverage, and low-data relevance criteria to §4.1.

## W2: Adult versus Post-Cutoff Datasets

> "In Section 4.5 and 4.6 why did you choose the Adult dataset and not one of the datasets that are created after the knowledge cutoff for LLMs?"

This is a useful challenge to our dataset choice. **Direct answer.** Adult was chosen for comparability with prior tabular-synthesis work and consistency with the Adult ablation in Table 3; we now complement that focused analysis with Anxiety and Salary, which were released after the LLM knowledge cutoff.

[Submitted, §4.1, l.321-325; §4.3, Table 3] The submission already identifies Anxiety and Salary as post-cutoff datasets, while using Adult across the ablation, vary-$n$, and backbone analyses enables a controlled analytical thread. [New, Exp-3] We compared CLLM and StructSynth on both post-cutoff datasets for $n\in\{20,50,100,200\}$:

| Dataset / Method | $n=20$ | $n=50$ | $n=100$ | $n=200$ |
|---|---:|---:|---:|---:|
| Anxiety AUC / CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
| Anxiety AUC / StructSynth | **80.83** | **83.50** | **86.45** | **87.23** |
| Salary $R^2$ / CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
| Salary $R^2$ / StructSynth | 50.56 | 54.90 | **55.98** | 63.54 |

**Takeaway:** StructSynth leads on Anxiety at every $n$, with the largest margin at $n=20$ (+3.31 AUC points), whereas Salary is task-dependent and favors StructSynth only at $n=100$.

[New, Exp-4] We also ran a Qwen3-32B backbone check on both post-cutoff datasets *(five seeds, $n=100$, 1,000 synthetic rows per run)*:

| Dataset | Metric | CLLM | StructSynth |
|---|---|---:|---:|
| Anxiety | AUC | 0.8432 $\pm$ 0.0118 | **0.8564 $\pm$ 0.0141** |
| Salary | $R^2$ | 0.5179 $\pm$ 0.0374 | **0.5318 $\pm$ 0.0355** |

**Takeaway:** StructSynth shows modest advantages under Qwen3-32B on both post-cutoff datasets, with mean differences small relative to the reported variation. This supports that the benefit transfers across LLM backbones and is not an artifact of GPT-specific pretraining knowledge.

**Revision (R2).** We will explain the Adult choice, add Exp-3 to §4.5, and report Exp-4 in §4.6 and the Appendix.

## Minor: Earlier Goal Description

> "The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction."

We appreciate this presentation suggestion. **Direct answer.** We will move the complete definition of a "generation plan" to immediately after the research question in the Introduction.

[Submitted, l.085-087; §3, l.197-214] The Introduction currently poses the question there, but the later definition makes the three operational roles explicit: generation order, conditioning context, and prompt scope.

**Revision (R3).** We will place this three-part definition after l.085-087 so that the paper's goal is clear before the technical exposition.

## Artifact Checklist

> "Reproducibility: 1 [...] Datasets: 1 [...] Software: 1"

We appreciate the reproducibility concern. **Direct answer.** The anonymous software artifact was already submitted, and we will make the remaining data-to-result path explicit and self-contained.

| Artifact | Status and evidence |
|---|---|
| Code and instructions | [Submitted, Appendix A, l.855-859] Anonymous repository and usage instructions included in the original submission. |
| Dataset provenance and protocol | [Submitted, §4.1; Appendix G.1, Table 4] All six datasets are public and cited; Appendix G.1 specifies the 8:2 split and seeds 42-51. |
| Exact replication inputs | We will add preprocessed datasets, exact split files, and configurations. |
| Preprocessing and evaluation | We will add the preprocessing scripts and an artifact index mapping each reported result to its command/configuration. |

**Takeaway:** Appendix A already provides usable software; the added assets will remove ambiguity about exact data preparation and experimental replay.

**Revision (R4).** We will expand Appendix A into an artifact checklist and release the listed replication assets with the revision.

## Summary of Revisions

| # | Change | Where |
|---|---|---|
| R1 | State the baseline-selection criteria | §4.1 |
| R2 | Explain the Adult choice and add post-cutoff Exp-3/Exp-4 results | §4.5, §4.6, Appendix |
| R3 | Move the three-part generation-plan definition earlier | Introduction |
| R4 | Add an artifact checklist and exact replication assets | Appendix A / repository |

These commitments involve no claims beyond the evidence above. If our responses resolve the concerns, we would be grateful if the reviewer would consider revisiting the assessment, including the Reproducibility, Datasets, and Software dimensions, in light of the anonymized repository already included in Appendix A.
