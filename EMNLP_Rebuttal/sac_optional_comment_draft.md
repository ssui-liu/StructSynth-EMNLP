# Draft Optional Comment to SAC/PC (EMNLP 2026 Commitment)

## Positioning

This field is a decision memo, not a second rebuttal. Its job is to let the SAC separate three things: which concerns the author response already closed, which one remains genuinely open, and how the final version will narrow its claims. It should not restate the paper's strengths, re-argue reviewer behaviour, or re-post numbers from the response.

Target length is 130-170 words. The draft below is approximately 165.

## Draft text (submission-ready)

> We use this space only to record what remains unresolved and how the final version will be bounded.
>
> One clarification: our contribution is not the two-stage decomposition itself. The causal graph functions as an inference-time generation plan — it fixes the generation order, the conditioning context of each variable, and the scope of each prompt — and requires no fine-tuning. This is what distinguishes it from PAFT-style approaches, which modify the model rather than the generation procedure.
>
> On evidence: direction-aware SHD was already reported in the original submission; the author response adds a PAFT comparison, anonymization baselines, and post-cutoff evaluations, and two reviewers updated parts of their assessment following it.
>
> One question remains genuinely open: we have not evaluated n > 200. The final version will state explicitly that our claims hold in the low-data regime and make no claim about data-rich settings.
>
> The camera-ready will incorporate the response experiments, sharpen the PAFT positioning, and replace "privacy preservation" with empirical DCR-based privacy-risk evidence, stating that we offer no formal privacy guarantee.

## Structure of the argument

| Paragraph | Function | Why it earns its space |
|---|---|---|
| 1 | Frames the note as scope-setting | Signals to the SAC that this is not a rebuttal reprise |
| 2 | Objective technical clarification | The meta-review's "two-stage decomposition" summary is the root of the novelty concern; correcting it must happen now, not in camera-ready |
| 3 | Evidence status | Distinguishes "already in the submission" (direction-aware SHD) from "added in response"; closes the questions that are closed |
| 4 | Open boundary | Volunteering the n > 200 gap reframes the meta-review's largest concern as a stated scope limit rather than an unbounded flaw |
| 5 | Revision commitments | The privacy sentence is the only fully verifiable commitment in the note; keep it concrete |

## Optional cuts, by risk preference

1. **"and two reviewers updated parts of their assessment following it"** — factually accurate and independently checkable by the SAC (one reviewer raised Overall 3 to 3.5; another updated reproducibility, dataset, and software scores). Cut the clause if it reads as pressure on the chairs. Removing it does not affect the rest of the argument.
2. **"anonymization baselines"** — listed as a category only, with no number attached, so it does not expose the audited AUC issue directly. It does still direct the SAC's attention to that table. The conservative variant lists only the PAFT comparison and post-cutoff evaluations.
3. **"— it fixes the generation order, the conditioning context of each variable, and the scope of each prompt —"** — this is the load-bearing clause of the whole note. Do not cut it to save words; cut paragraph 1 instead.

## Internal caution - do not paste into OpenReview

- The draft contains no numerical results by design. The posted response has known discrepancies against the archived runs: the Salary vary-n rows are interchanged, the PAFT R2 cells for "PAFT full" and "PAFT + StructSynth ordering" are reversed relative to the archived summary, the anonymization AUC has no located source, and the GraDe utility average (51.05) was copied from the BN fidelity column instead of Table 1 (62.73). See `rebuttal-v2/00b_NUMERIC_AUDIT_PLAN.md`.
- Do not claim that the response "fully resolved" any concern, and do not claim comprehensive superiority over PAFT. The note only needs to establish that a mechanism-level distinction exists and that the requested comparison was supplied.
- The "1,000 synthetic rows" figure in the response is not a training-table experiment at n > 200. It must never be used to answer the meta-review's data-rich question. Paragraph 4 is written on the assumption that this experiment does not exist.

## Before submission

1. Re-verify the score-update claim in paragraph 3 against the current OpenReview record before submitting. If either reviewer has since reverted, cut the clause.
2. Confirm the paper's final claim wording is consistent with paragraph 4 — the abstract and Section 5 currently still say "privacy preservation" (`Latex-EMNLP/sections/abstract.tex:3`, `Latex-EMNLP/sections/experiments.tex:88`). The commitment in paragraph 5 is only credible if the revision actually makes this change.
3. Do not submit this note and the Issue Report with overlapping arguments. The Issue Report (`review_issue_report_7Wh2_draft.md`) is about whether a specific response was acknowledged; this note is about scope and revision. Keep them non-redundant.
4. Word-count the final text. If it exceeds 170 words, cut paragraph 1, not paragraph 2 or 4.
