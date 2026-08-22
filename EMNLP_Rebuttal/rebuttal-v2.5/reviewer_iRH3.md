# Response to Reviewer iRH3

We thank Reviewer iRH3 for the careful and constructive review. We respond to each weakness in order, foregrounding (i) the direction-aware structural evaluation already in the submission, marked [Submitted], and (ii) a new task-and-field anonymization ablation, marked [New, Exp-2].

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W1: Direction-Aware Structural Recovery

> "[I]t would also be valuable to evaluate the correctness of the learned graph structure, particularly edge directions, on datasets where ground-truth dependency structures are available."

This is an important criterion that deserved greater visibility. **Direct answer.** Section 4.4 already performs exactly this evaluation: SHD against three ground-truth DAGs, where every reversed edge is explicitly penalized.

[Submitted, §4.4, Figure 3, l.470–490] We evaluate Asia (8 nodes), Child (20), and Insurance (27) for n ∈ {20, 50, 100, 200}. Structural Hamming Distance counts the edge insertions, deletions, **and reversals** needed to recover the reference DAG; StructSynth attains the lowest or near-lowest SHD on all three, with its clearest advantage at n ≤ 50. Directionality is functionally necessary because the DAG defines the topological generation schedule, but it is not an ontological or causal claim [Submitted, Appendix D]. Consistent with this functional role, removing topological order lowers AUC by 1.1 points, while PC- and NoTears-discovered graphs lower it by 1.0 and 1.4 points [Submitted, Table 3].

**Takeaway:** The submitted evaluation measures directional errors directly, while Appendix D carefully limits what those directions are claimed to mean.

**Revision (R1).** We will rename §4.4 "Structural Recovery on Ground-Truth DAGs (including edge directions)" and make SHD's reversal penalty explicit in the opening sentence.

## W2: Behavior Beyond the Low-Data Regime

> "Experiments with larger sample sizes would help clarify the trade-off between the advantages of LLM-based graph construction and purely data-driven alternatives."

We appreciate the request to clarify the method's operating range. **Direct answer.** StructSynth targets the n ≤ 200 low-data regime; not testing n > 200 is a scope boundary, and behavior beyond that range should be presented as a hypothesis rather than an established result.

[Submitted, §1, l.040–047; §4.5, Figure 4, l.496–505] From n = 20 to 200, StructSynth remains stable across utility, fidelity, and privacy, while its largest advantage occurs at n ≤ 50 and the gap narrows toward 200. [Submitted, §4.4, Figure 3] FCI and NoTears likewise approach StructSynth's SHD as n increases. [Submitted, Appendix K.3] The paper already identifies the method as best suited to severely limited data (especially n ≤ 100) and notes diminished advantages when statistical structure learning becomes reliable.

These observations motivate — but do not prove — the hypothesis that beyond n = 200, stronger association estimates will reduce the relative value of the LLM semantic prior while StructSynth's absolute performance remains competitive.

**Takeaway:** Existing results show the trade-off changing through n = 200; claims beyond that point remain outside the evaluated scope.

**Revision (R2).** We will add the evaluated operating range, convergence trend, and clearly qualified n > 200 hypothesis to the Limitations section, with pointers to §4.4, §4.5, and Appendix K.3.

## W3: Task-and-Field Anonymization

> "An informative additional experiment would be to anonymize feature names [...] and evaluate how much the performance depends on semantic information provided by the feature names."

This is a well-motivated fairness check. **Direct answer.** Task-and-field anonymization removes exactly the semantic advantage identified by the reviewer, leaving a like-for-like test of whether statistical evidence and the resulting generation plan remain useful.

[Submitted, §3.1.2, l.249–258] StructSynth pairs semantic reasoning with observed association scores (Cramér's V, |r|, and correlation ratio), so the statistical channel remains available when names are opaque. [New, Exp-2] In an exploratory run, we anonymized all column names and task/column descriptions while keeping values unchanged *(gpt-5-mini, single seed 42, 100 real rows, 1,000 synthetic rows; fidelity and DCR on 0–1 scale)*.

| Dataset | Condition | Utility | Fidelity ↓ | DCR (ideal 0.50) |
|---|---|---:|---:|---:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R² 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | 0.615 | 0.412 |

On Anxiety, anonymization produces a modest utility decrease (AUC 0.865 → 0.850) but better fidelity (0.579 → 0.534), suggesting that some semantically inferred edges may be spurious. On Salary, the original retains a larger advantage (R² 0.560 → 0.462), indicating that semantic priors contribute more to regression tasks involving fine-grained continuous dependencies.

**Takeaway:** StructSynth remains functional without semantic headers, while the mixed results show a task-dependent contribution from semantic priors.

**Revision (R3).** We will add the anonymization results to the appendix and discuss opaque schemas and task-dependent semantic priors as boundary conditions.

## Summary of Revisions

| # | Change | Where |
|---|---|---|
| R1 | Surface SHD's edge-reversal penalty and direction-aware evaluation | §4.4 |
| R2 | State the operating range, convergence evidence, and qualified n > 200 hypothesis | Limitations; §4.4–§4.5; Appendix K.3 |
| R3 | Add the anonymization ablation and semantic-prior boundary conditions | Appendix; Limitations |

These commitments make no claims beyond the submitted and new evidence above. If our responses resolve the concerns, we would be grateful if the reviewer would consider revisiting the assessment.
