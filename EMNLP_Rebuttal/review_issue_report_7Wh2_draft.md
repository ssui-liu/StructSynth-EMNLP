# Draft Review Issue Report for Reviewer 7Wh2

## Recommended selection

- Primary: **I11 Non Response**
- Optional, weaker secondary flag: **I3 Score Mismatch**
- Do not select I2, I5, I7, or I10 on the current record. The reviewer cites a specific related work and gives a rationale, and requesting a comparison with a close method is reasonable. The defensible issue is that the central novelty assessment has not acknowledged the mechanism-level distinction and the requested comparison supplied in the author response.

Do not argue that PAFT should carry less weight because it appeared at a workshop. Venue status does not determine whether a work is relevant prior art and would weaken the report.

## Justification (recommended, I11 only)

I11. Reviewer 7Wh2's principal concern is that StructSynth is "quite close" to PAFT because both discover structure and use it for generation, leading to the assessment that our novelty is limited [LINK TO REVIEW]. We agree that PAFT should have been cited and directly compared. However, the review characterizes our contribution at the generic level of a two-stage pipeline without addressing the mechanism explicitly stated in the submission: StructSynth executes a DAG at inference time to determine generation order, per-step conditioning context, and prompt scope for black-box LLM calls, without parameter updates (Sections 1 and 3.1-3.2; Eq. 4). The submission also evaluates GraDe, a related FD-guided fine-tuned generator, under the same protocol, with StructSynth leading on all six datasets (Table 1).

Our response directly addressed the requested comparison by explaining the PAFT-StructSynth mechanism difference, providing a direct PAFT and component-transfer study, acknowledging the missing citation, and committing to narrow the contribution claim and add PAFT to the revision [LINK TO RESPONSE 1/2; LINK TO RESPONSE 2/2]. As of 18 July 2026, the reviewer has not acknowledged this evidence or indicated whether it affects the central novelty assessment underlying the Overall 2 recommendation. We respectfully ask the chairs to ensure that this critical response is considered; we are not asking them to resolve a reasonable scientific disagreement in our favor.

## Optional additional paragraph (I3)

I3. The written review describes the empirical results as "strong," states that StructSynth achieves the best downstream performance on the evaluated datasets, and calls the ablations helpful. It also assigns Soundness 3, explicitly stating that the study provides sufficient support for its main claims, and Reproducibility 4. Nevertheless, the Overall Assessment is 2, characterized as requiring substantial revisions, with the PAFT-based novelty judgment serving as the only decisive concern. We recognize that novelty and excitement are partly subjective. In light of the unacknowledged mechanism-level distinction and requested comparison described above, we ask the chairs only to check whether the Overall recommendation remains calibrated to the review's written technical assessment [LINK TO REVIEW].

## Before submission

1. Confirm that Reviewer 7Wh2 still has not replied to or updated the review after the 14 July author responses. If the reviewer has acknowledged the response, do not use I11.
2. Replace all bracketed placeholders with OpenReview links to the specific review and response comments. The Issue Report form explicitly requests links to specific comments.
3. Prefer the I11-only version. Add I3 only if the chairs' local guidance encourages score-text consistency reports.
4. Do not quote the numerical component-transfer claims in the issue report. The report only needs to establish that the requested comparison and a mechanism-level distinction were supplied; it should not ask the chairs to adjudicate a new leaderboard result.

## Internal numerical caution - do not paste into OpenReview

- The posted response says GraDe's average utility is 51.05, whereas the submitted Table 1 gives 62.73; 51.05 is the BN fidelity average elsewhere in the paper.
- The posted PAFT table lists average R2 as 0.360 for PAFT full and 0.404 for PAFT plus StructSynth graph ordering. The archived aligned summary gives the reverse: 0.4039 and 0.3596. Accordingly, the response's claim of a +0.044 R2 gain from StructSynth ordering is not supported by the archived results.
- These discrepancies do not erase the mechanism-level distinction, but they make a numerical "we already proved superiority" argument risky. Keep the Issue Report focused on whether the reviewer acknowledged the distinction and the requested comparison, not on the comparison's numerical outcome.
