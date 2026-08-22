# Internal Rebuttal v2 Tracking

This file contains internal scores and length budgets removed from the reviewer-visible responses. Do not paste it into OpenReview.

## Reviewer scores from v1

| Dimension | 7Wh2 | q74j | iRH3 |
|---|---:|---:|---:|
| Overall Assessment | 2 (Resubmit next cycle) | 4 (Conference) | 3 (Findings) |
| Confidence | 5 | 4 | 3 |
| Soundness | 3 | 4.5 | 3.5 |
| Excitement | 1.5 | 3.5 | 3 |
| Reproducibility | 4 | 1 | 4 |
| Datasets | 4 | 1 | 3 |
| Software | 4 | 1 | 4 |

## Declared response-length metadata

Counts exclude tables and reviewer quotations.

| Response | v1 declared estimate | v2 headline target |
|---|---:|---:|
| Reviewer 7Wh2 | ~1,200 words | ~1,150–1,250 words |
| Reviewer q74j | ~800 words | ~750 words |
| Reviewer iRH3 | ~800 words | ~750 words |
| General Response | not declared in v1 | ~350–400 words |

## v2 section allocations from the writing plan

### Reviewer 7Wh2

| Section | Budget (words) |
|---|---:|
| Opening / roadmap | 90 |
| W1 — PAFT relationship and novelty | 450 |
| W2 — Privacy evaluation | 140 |
| W3 — Statistical fidelity | 150 |
| W4 — Opaque / anonymized schemas | 220 |
| Revision summary and ask | 120 |

### Reviewer q74j

| Section | Budget (words) |
|---|---:|
| Opening factual correction and roadmap | 130 |
| W1 — Baseline selection | 150 |
| W2 — Dataset selection / post-cutoff evidence | 260 |
| Minor — Earlier goal description | 50 |
| Artifact checklist | 130 |
| Revision summary and ask | 110 |

### Reviewer iRH3

| Section | Budget (words) |
|---|---:|
| Opening / roadmap | 70 |
| W1 — Ground-truth graph evaluation | 200 |
| W2 — Larger sample sizes | 230 |
| W3 — Semantic-prior fairness / anonymization | 250 |
| Revision summary and ask | 100 |

## Shared experiment numbering

| Reviewer-visible number | Internal block | Evidence |
|---|---|---|
| Exp-1 | E1 + E2 | StructSynth × PAFT component transfer plus PAFT/GraDe/StructSynth mechanism positioning |
| Exp-2 | E3 | Same-protocol task-and-field anonymization |
| Exp-3 | E4 | Post-cutoff vary-n comparison |
| Exp-4 | E5 | Qwen3-32B fixed-backbone check |
| — | E6 | Artifact availability and release checklist |

## Internal handling notes

- Remove all reviewer score tables and total-word-count lines from public drafts.
- q74j's 1/1/1 artifact dimensions are the main score-correction opportunity; the submitted Appendix A repository must be surfaced before itemized responses.
- 7Wh2 is the highest-confidence novelty challenge; allocate the largest share to W1.
- Use `evidence_blocks.md` as the only source for shared numbers and protocol labels.
