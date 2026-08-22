# Rebuttal v2 Canonical Evidence Blocks

This internal file preserves the numerical results and interpretations already present in rebuttal_drafts/ and rebuttal-v1/. The v2 responses may reorganize and polish those materials, but must not recompute, reconcile, replace, or reinterpret their reported results.

Reviewer-visible numbering is fixed as follows: Exp-1 = E1 + E2, Exp-2 = E3, Exp-3 = E4, and Exp-4 = E5.

## E1 — StructSynth × PAFT component transfer (Exp-1)

**Draft source:** rebuttal_drafts/reviewer_7Wh2.md.

**Protocol stated in the draft:** 100 real rows, 1,000 synthetic rows, unified XGBoost evaluation.

| Generator | Structural source | Avg. AUC | Avg. R² | Fidelity error ↓ | DCR deviation ↓ |
|---|---|---:|---:|---:|---:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

**Draft interpretation:** The two graph representations can be used by both generation mechanisms. Conditions using the StructSynth graph have higher average AUC by +0.030/+0.022; conditions using the StructSynth generator differ by +0.056/+0.048 and have lower DCR deviation. PAFT retains better pairwise fidelity.

**Required draft caveats:** The PAFT reproduction uses a local FD approximation rather than the full HyFD pipeline; seed counts differ across conditions (5–10); and PAFT uses fine-tuned DistilGPT2 while StructSynth uses a black-box LLM. The table is descriptive rather than a controlled factorial ablation and must not be used to claim independent causal effects.

## E2 — PAFT / GraDe / StructSynth positioning (Exp-1)

**Draft source:** rebuttal_drafts/reviewer_7Wh2.md and rebuttal-v1/reviewer_7Wh2.md.

| Method | Structure use | Training / inference route |
|---|---|---|
| PAFT | Functional dependencies compiled into a global feature permutation | LoRA fine-tuning of DistilGPT2 |
| GraDe | Dynamic sparse attention graph and FD-alignment objective | GPT-2 fine-tuning |
| StructSynth | Directed graph executed as generation order, conditioning context, and prompt scope | Black-box inference; no parameter update |

**Draft-reported comparison:** Under the same 100-shot splits, ten seeds, 1,000 generated samples, and evaluation pipeline, StructSynth outperforms GraDe on all six datasets, with average utility 75.01 vs. 51.05.

**Draft-reported supporting results:** Removing the graph lowers AUC by 1.6 points; ignoring topological order lowers AUC by 1.1 points; replacing the LLM generator with a Bayesian sampler lowers AUC by 4.4 points. The Bayesian sampler obtains fidelity 48.86 and AUC 81.17.

## E3 — Feature anonymization (Exp-2)

**Draft source:** rebuttal_drafts/reviewer_7Wh2.md, rebuttal_drafts/reviewer_iRH3.md, and the corresponding v1 responses.

**Protocol stated in the draft:** gpt-5-mini, seed 42, 100 real training samples, and 1,000 synthetic samples. Column names, task descriptions, and column descriptions are anonymized; cell values are unchanged.

| Dataset | Condition | Utility | Fidelity ↓ | DCR → 0.50 |
|---|---|---:|---:|---:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R² 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | 0.615 | 0.412 |

**Draft interpretation:** Anxiety shows a modest utility decrease and improved fidelity after anonymization. Salary shows a larger regression decrease. The result is mixed rather than uniformly robust, and PAFT may be less sensitive to opaque schemas.

## E4 — Post-cutoff vary-n comparison (Exp-3)

**Canonical source for this result:** rebuttal-v1/reviewer_q74j.md. The same values are synchronized into rebuttal_drafts/reviewer_q74j.md and the v2 response.

**Protocol stated in the draft:** gpt-5-mini, five seeds, 100 real rows per n, 1,000 synthetic rows per seed.

| Dataset / Method | n=20 | n=50 | n=100 | n=200 |
|---|---:|---:|---:|---:|
| Anxiety AUC / CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
| Anxiety AUC / StructSynth | 80.83 | 83.50 | 86.45 | 87.23 |
| Salary R² / CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
| Salary R² / StructSynth | 50.56 | 54.90 | 55.98 | 63.54 |

**Draft interpretation:** StructSynth leads CLLM at every n on both datasets. On Anxiety, the largest margin is +3.31 AUC at n=20. On Salary, StructSynth leads at every n with margins ranging from +1.5 to +2.6 R² points, smaller than Anxiety's margins.

## E5 — Qwen3-32B backbone check (Exp-4)

**Draft source:** rebuttal_drafts/reviewer_q74j.md and rebuttal-v1/reviewer_q74j.md.

**Protocol stated in the draft:** five seeds, 100 real samples, and 1,000 synthetic rows per seed.

| Dataset | Metric | CLLM | StructSynth |
|---|---|---:|---:|
| Anxiety | AUC | 0.8432 ± 0.0118 | 0.8564 ± 0.0141 |
| Salary | R² | 0.5179 ± 0.0374 | 0.5318 ± 0.0355 |

**Draft interpretation:** StructSynth shows modest advantages under Qwen3-32B on both post-cutoff datasets, with mean differences small relative to five-seed variation. This is presented as support for backbone generality.

## E6 — Artifact wording

The v2 writing plan requires the q74j response to surface that an anonymized repository was included in Appendix A, l.855–859:

The URL is included in Appendix A of the submitted PDF but must not be pasted into the rebuttal text (platform policy).

The revision commitment is to additionally provide preprocessed datasets, exact splits, configurations, seeds, and preprocessing scripts. This organizational correction does not alter any experimental result.
