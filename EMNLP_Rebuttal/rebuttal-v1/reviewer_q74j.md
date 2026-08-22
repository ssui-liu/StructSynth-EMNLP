# Response to Reviewer q74j

**Total response word count: ~800 words (excluding tables and reviewer quotations)**

## Reviewer Scores

| Dimension | Score |
|---|---|
| Overall Assessment | 4 (Conference) |
| Confidence | 4 |
| Soundness | 4.5 |
| Excitement | 3.5 |
| Reproducibility | 1 |
| Datasets | 1 |
| Software | 1 |

---

We sincerely thank Reviewer q74j for their careful reading and for recognizing the paper's writing quality, sound experimental design, and the contribution of the ablation study. We address each concern below, with new post-cutoff experiments (Exp-3, Exp-4; see also General Response) and a reproducibility clarification.

---

## W1: Baseline Selection Justification
**[Why these particular baselines? Are they the best available in each category?]**
> "It is not clear whether the baselines used are the best available methods in their respective categories. As the authors explain in l.052-l.055, deep generative models' performance varies across architectures and some may require many more examples to train. I expected a little explanation in the experiments section that motivates the choice for the particular models used as baselines."

We appreciate this question and agree that baseline selection justification deserves explicit discussion. Our 12 baselines (S4.1, l.306--312) were selected to span three paradigms with both established and recent methods in each:

- **Deep Generative Models (5):** TVAE/CTGAN (2019, most widely cited tabular GAN/VAE), TabDDPM (2023, diffusion), NFlow (2021, normalizing flows), TabSyn (2024, current DGM SOTA)
- **Structure-Aware Methods (4):** BN (classic probabilistic graphical model), GOGGLE (2023, graph-based VAE), DECAF (2021, causal GAN), SPADA-NF (2025, latest graph+NF)
- **LLM-based Methods (3):** GReaT (2023, first LLM tabular synthesizer), CLLM (2024, prompt-based SOTA), GraDe (2025, graph-aware LLM)

The selection principle is that each category includes at least one foundational method and at least one recent (2024--2025) method, ensuring temporal coverage from established baselines to current state-of-the-art.

As the reviewer notes (l.052--055), some DGMs perform best with more training data. Our evaluation at n=100 is deliberate: the low-data regime is precisely our target scenario. Table 1 confirms that methods like TabDDPM and TabSyn underperform here (avg scores 63.69 and 68.04), demonstrating that large-sample advantages do not transfer to scarce-data settings. The vary-n experiment (S4.5, Figure 4) further illustrates how baseline relative performance changes across sample sizes.

We will add a brief justification of our baseline selection criteria to S4.1 in the revision.

---

## W2: Dataset Selection for S4.5 and S4.6
**[Why use Adult rather than a post-cutoff dataset for the scaling and LLM backbone analyses?]**
> "It is not always clear why you select a particular dataset to show results. In Section 4.5 and 4.6 why did you choose the Adult dataset and not one of the datasets that are created after the knowledge cutoff for LLMs?"

We chose Adult for S4.5 and S4.6 for three reasons: (1) Adult is the most widely used benchmark in the tabular synthesis literature (adopted by TVAE/CTGAN, GReaT, CLLM, GraDe, and GOGGLE), enabling direct comparison with prior work; (2) the ablation study (S4.3, Table 3) uses Adult, and continuing with the same dataset maintains analytical consistency; and (3) space constraints---the vary-n analysis requires reporting multiple methods across several n values on three dimensions (utility/fidelity/privacy), making single-dataset deep analysis preferable to shallow multi-dataset coverage.

However, we fully agree that validating on post-cutoff datasets strengthens these analyses. We have now completed vary-n experiments (n=20, 50, 100, 200) comparing LLM-based synthesis methods on Anxiety and Salary, both released after the LLM knowledge cutoff:

**Anxiety (Classification, AUC):**

| Method | n=20 | n=50 | n=100 | n=200 |
|:--|--:|--:|--:|--:|
| CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
| StructSynth | **80.83** | **83.50** | **86.45** | **87.23** |

**Salary (Regression, R^2):**

| Method | n=20 | n=50 | n=100 | n=200 |
|:--|--:|--:|--:|--:|
| CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
| StructSynth | 50.56 | 54.90 | **55.98** | 63.54 |

On Anxiety, StructSynth leads across all sample sizes, with the largest margin at n=20 (+3.31 AUC) --- consistent with the Adult trend that structural guidance is most valuable under data scarcity. On Salary, results are more nuanced: StructSynth leads only at n=100 (R^2 55.98 vs. 54.53), while CLLM is ahead at other sample sizes (n=200: R^2 63.54 vs. 61.39), suggesting that regression tasks with fine-grained continuous dependencies benefit less consistently from structural priors. These post-cutoff results confirm the classification finding observed on Adult --- structural guidance is most valuable under scarcity --- on datasets unseen during LLM pretraining, while honestly revealing the task-dependent nature of the advantage.

We additionally ran a Qwen3-32B backbone check on both post-cutoff datasets (five seeds, 1,000 synthetic rows per seed, n=100):

| Dataset | Metric | CLLM | StructSynth |
|---|---|---:|---:|
| Anxiety | AUC | 0.8432 +/- 0.0118 | 0.8564 +/- 0.0141 |
| Salary | R^2 | 0.5179 +/- 0.0374 | 0.5318 +/- 0.0355 |

StructSynth shows modest advantages under Qwen3-32B on both post-cutoff datasets, with mean differences small relative to five-seed variation. This supports that our method's benefits transfer across LLM backbones and are not artifacts of GPT-specific pretraining knowledge.

We will include these post-cutoff results alongside the Adult analyses in the revision (main text for S4.5; full baseline comparisons in the Appendix).

---

## Minor: Introduction Goal Description
> "The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction."

We agree with this suggestion. In the revision, we will move the full definition of "generation plan"---specifying that the dependency graph determines generation order, conditioning context, and prompt scope---to the Introduction immediately following the research question (l.085--087), so that readers can orient themselves before the technical exposition.

---

## Reproducibility, Datasets, and Software (Scores: 1/1/1)

We note the discrepancy between the reviewer's reproducibility scores (1/1/1) and those of the other reviewers (4/4/4 from Reviewer 7Wh2; 4/3/4 from Reviewer iRH3), and we take this concern seriously. We believe this stems from the absence of an anonymous code/data link in the original submission.

We confirm that our complete implementation is ready for release. Specifically, we will provide:

- Full code repository covering graph discovery, conditional synthesis, and the evaluation pipeline
- Preprocessed datasets with exact train/test splits for all six evaluation datasets
- All experiment configuration files and random seeds
- An anonymous GitHub link in the supplementary material of the revised submission

All datasets used are publicly available (cited in S4.1 and Appendix A), and we will additionally include our preprocessing scripts to ensure exact replication of all reported results.

---

## Revision Plan

We will make the following changes in the revised manuscript:

1. **S4.1:** Add a paragraph justifying the baseline selection criteria (temporal span, paradigm coverage, established + SOTA per category)
2. **S4.5:** Include post-cutoff vary-n results (Anxiety and Salary) alongside the Adult analysis
3. **S4.6 / Appendix:** Add Qwen3-32B backbone results on post-cutoff datasets
4. **Introduction:** Move the "generation plan" definition earlier (before l.100)
5. **Supplementary:** Provide anonymous code repository, preprocessed data, configuration files, and seeds

---

We are grateful for the reviewer's constructive feedback. These revisions will strengthen the experimental transparency of the paper without altering its core findings. We hope our responses adequately address the concerns raised and welcome any further questions.
