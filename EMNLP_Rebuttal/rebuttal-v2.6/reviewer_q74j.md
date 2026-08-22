# Response to Reviewer q74j (1/2)

We thank Reviewer q74j for the careful and constructive review, and especially for recognizing the paper's writing, experimental design, and ablations. Below, we address each point in order.

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

Before the itemized responses, we would like to clarify one factual point regarding the Reproducibility / Datasets / Software assessments (1/1/1). An anonymized implementation and accompanying instructions were included in the original submission (Appendix A, l.855–859). We suspect this artifact may have been missed; the additional replication assets are detailed in the checklist in the second part of this response (2/2).

## W1: Baseline Selection

> "It is not clear whether the baselines used are the best available methods in their respective categories. [...] I expected a little explanation in the experiments section that motivates the choice for the particular models used as baselines."

**We selected twelve baselines to cover three paradigms — DGMs, structure-aware, and LLM-based — with a foundational method and a recent representative in each, under the same low-data setting (§4.1, l.334–348).**

The suite covers DGMs (TVAE/CTGAN, TabDDPM, NFlow, TabSyn), structure-aware methods (BN, GOGGLE, DECAF, SPADA-NF), and LLM-based methods (GReaT, CLLM, GraDe). TabSyn (2024), SPADA-NF (2025), and GraDe (2025) ensure that every category includes a recent method, while the established methods provide recognizable anchors. Evaluating all methods at n = 100 is deliberate because data scarcity is the paper's target condition; Table 1 reports average scores of 63.69 for TabDDPM and 68.04 for TabSyn in this regime — large-sample reputation alone is not an adequate selection criterion.

## W2: Adult versus Post-Cutoff Datasets

> "In Section 4.5 and 4.6 why did you choose the Adult dataset and not one of the datasets that are created after the knowledge cutoff for LLMs?"

**Adult was chosen for comparability with prior work and consistency with the Table 3 ablation; we now complement it with Anxiety and Salary, both released after the LLM knowledge cutoff (Exp-3, Exp-4).**

The submission already identifies Anxiety and Salary as post-cutoff datasets (§4.1, l.321–325; §4.3, Table 3), while using Adult across the ablation, vary-n, and backbone analyses enables a controlled analytical thread. We compared CLLM and StructSynth on both post-cutoff datasets for n = 20, 50, 100, 200 (Exp-3):

*(gpt-5-mini, five seeds, 1,000 synthetic rows per run)* (AUC / R² × 100)

| Dataset / Method | n = 20 | n = 50 | n = 100 | n = 200 |
|---|---:|---:|---:|---:|
| Anxiety AUC / CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
| Anxiety AUC / StructSynth | **80.83** | **83.50** | **86.45** | **87.23** |
| Salary R² / CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
| Salary R² / StructSynth | **50.56** | **54.90** | **55.98** | **63.54** |

StructSynth leads at every n on both datasets; the largest margin is +3.31 AUC at n = 20.

We also ran a Qwen3-32B backbone check on both post-cutoff datasets (Exp-4) *(five seeds, n = 100, 1,000 synthetic rows per run; 0–1 scale)*:

| Dataset | Metric | CLLM | StructSynth |
|---|---|---:|---:|
| Anxiety | AUC | 0.843 ± 0.012 | **0.856 ± 0.014** |
| Salary | R² | 0.518 ± 0.037 | **0.532 ± 0.036** |

StructSynth shows modest advantages under Qwen3-32B on both post-cutoff datasets, with mean differences small relative to the reported variation. This supports backbone generality: the benefit is not an artifact of GPT-specific pretraining knowledge.

*(continued in the next comment)*

<!-- BOX SPLIT -->

# Response to Reviewer q74j (2/2)

Continuing from (1/2); experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## Minor: Earlier Goal Description

> "The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction."

We appreciate this presentation suggestion. The three-part definition of a generation plan (generation order, conditioning context, prompt scope) will move to the Introduction immediately after the research question at l.085–087.

## Artifact Checklist

> "Reproducibility: 1 [...] Datasets: 1 [...] Software: 1"

**The anonymous software artifact was already part of the original submission (Appendix A, l.855–859); the checklist below makes the remaining data-to-result path explicit.**

| Artifact | Status and evidence |
|---|---|
| Code and instructions | Anonymous repository and usage instructions included in the original submission (Appendix A, l.855–859). |
| Dataset provenance and protocol | All six datasets are public and cited; Appendix G.1 specifies the 8:2 split and seeds 42–51 (§4.1; Appendix G.1, Table 4). |
| Exact replication inputs | We will add preprocessed datasets, exact split files, and configurations. |
| Preprocessing and evaluation | We will add the preprocessing scripts and an artifact index mapping each reported result to its command/configuration. |

Appendix A already provides usable software; the added assets will remove ambiguity about exact data preparation and experimental replay.

**Revision plan.** We will: (1) add paradigm-coverage and low-data criteria to §4.1 (W1); (2) explain Adult choice, add Exp-3 to §4.5 and Exp-4 to §4.6/Appendix (W2); (3) move generation-plan definition after l.085–087 (Minor); (4) expand Appendix A into an artifact checklist with replication assets (Checklist).

We hope these results address your concerns; we would be glad to run further analyses during the discussion period — including any further information relevant to the Reproducibility, Datasets, and Software assessments, in light of the anonymized repository already included in Appendix A.
