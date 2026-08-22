# General Response to All Reviewers

We thank all reviewers for the constructive feedback. The reviews raise five families of concerns: (a) novelty relative to PAFT, (b) reliance on semantic priors, (c) evaluation choices, (d) artifact availability, and (e) the calibration of privacy and fidelity claims.

| # | Addresses | New evidence | Headline result | Where addressed |
|---|---|---|---|---|
| Exp-1 | (a) | Bidirectional StructSynth×PAFT component transfer | The full StructSynth system outperforms the full PAFT system on utility and privacy (AUC 0.830 vs. 0.752); the StructSynth graph improves both generators (+0.030/+0.022 AUC) | 7Wh2-W1 |
| Exp-2 | (b) | Task-and-field anonymization | Functional under full anonymization — classification within 1.5 AUC points (0.865 → 0.850), fidelity improves; regression degrades more (R² 0.560 → 0.462) | 7Wh2-W4; iRH3-W3 |
| Exp-3 | (c) | Post-cutoff vary-n (Anxiety, Salary) | StructSynth leads at every n on both datasets; largest margin +3.31 AUC at n = 20 | q74j-W2 |
| Exp-4 | (c) | Qwen2.5-32B backbone check | AUC 0.856 vs. 0.843; R² 0.532 vs. 0.518 (0–1 scale) | q74j-W2 |

(d) is addressed in our response to Reviewer q74j (Artifact Checklist); (e) requires wording revisions only — no new experiments (details in our responses to 7Wh2, W2/W3).

Together, these results support that StructSynth's improvements arise from the explicit graph-as-generation-plan design rather than LLM memorization, hold across post-cutoff datasets and LLM backbones, and complement rather than duplicate PAFT's fine-tuning approach.

**Revision plan.** We will (1) position PAFT in §1–§2 [7Wh2-W1]; (2) sharpen the contribution statement to inference-time graph execution and include PAFT as a baseline in the main comparison [7Wh2-W1]; (3) correct GraDe in Appendix G.2 and justify baselines in §4.1 [7Wh2-W1; q74j-W1]; (4) replace "privacy preservation" wording with empirical-privacy language in §4.2/Limitations [7Wh2-W2]; (5) report the utility–privacy–fidelity trade-off in §5/Appendix K.2 [7Wh2-W3]; (6) add Exp-1–4, surface the direction-aware SHD evaluation in §4.4 [iRH3-W1], and clarify low-data/opaque-schema boundaries in §4.5/Appendix [iRH3-W2/W3; 7Wh2-W4; q74j-W2]; and (7) move the generation-plan definition earlier, expand the Appendix A artifact checklist, and identify direct structural metrics as future work [q74j-Minor/Checklist; 7Wh2-W1/W4].
