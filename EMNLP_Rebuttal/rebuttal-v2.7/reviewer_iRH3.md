# Response to Reviewer iRH3

We thank Reviewer iRH3 for the careful and constructive review. We respond to each weakness in order, foregrounding (i) the direction-aware structural evaluation already in the submission (§4.4) and (ii) a new task-and-field anonymization ablation (Exp-2).

Experiment numbering (Exp-1–4) is shared across all responses and defined in the General Response.

## W1: Direction-Aware Structural Recovery

> "[I]t would also be valuable to evaluate the correctness of the learned graph structure, particularly edge directions, on datasets where ground-truth dependency structures are available."

This is an important criterion that deserved greater visibility. **Section 4.4 already includes this evaluation: SHD against three ground-truth DAGs (Asia, Child, Insurance), where every reversed edge is explicitly penalized (§4.4, Figure 3, l.470–490).**

We evaluate Asia (8 nodes), Child (20), and Insurance (27) for n ∈ {20, 50, 100, 200}. Structural Hamming Distance counts the edge insertions, deletions, and reversals needed to recover the reference DAG; StructSynth attains the lowest or near-lowest SHD on all three, with its clearest advantage at n ≤ 50. Directionality is functionally necessary because the DAG defines the topological generation schedule, but it is not an ontological or causal claim (Appendix D). Consistent with this functional role, removing topological order alone lowers AUC by 1.1 points (Table 3). Replacing the StructSynth graph with PC- or NoTears-discovered alternatives — which differ in both edge set and orientation — lowers it by 1.0 and 1.4 points respectively.

## W2: Behavior Beyond the Low-Data Regime

> "Experiments with larger sample sizes would help clarify the trade-off between the advantages of LLM-based graph construction and purely data-driven alternatives."

**From n = 20 to 200, StructSynth remains stable across utility, fidelity, and privacy, with its largest advantage at n ≤ 50; the convergence trend the reviewer anticipates is already measurable in range (§4.5, Figure 4; §4.4, Figure 3).**

n ≤ 200 is the designed operating range (§1, l.040–047). The utility gap narrows toward n = 200, and FCI and NoTears approach StructSynth's SHD as n increases (§4.4, Figure 3) — exactly the trade-off the reviewer asks about. The paper already identifies the method as best suited to severely limited data (especially n ≤ 100) and notes diminished advantages when statistical structure learning becomes reliable (Appendix K.3).

These observations motivate the hypothesis that beyond n = 200, stronger association estimates will reduce the relative value of the LLM semantic prior while StructSynth's absolute performance remains competitive.

## W3: Task-and-Field Anonymization

> "An informative additional experiment would be to anonymize feature names [...] and evaluate how much the performance depends on semantic information provided by the feature names."

**StructSynth remains functional without semantic headers — statistical association scores compensate — with a task-dependent contribution from semantic priors (Exp-2).**

StructSynth pairs semantic reasoning with observed association scores (Cramér's V, |r|, and correlation ratio), so the statistical channel remains available when names are opaque (§3.1.2, l.249–258). We anonymized all column names and task/column descriptions while keeping values unchanged (Exp-2) *(gpt-5-mini, 100 real rows, 1,000 synthetic rows; 0–1 scale)*.

| Dataset | Condition | Utility | Fidelity ↓ | DCR (ideal 0.50) |
|---|---|---:|---:|---:|
| Anxiety | Original | AUC 0.865 | 0.579 | 0.447 |
| Anxiety | Anonymized | AUC 0.850 | 0.534 | 0.564 |
| Salary | Original | R² 0.560 | 0.646 | 0.501 |
| Salary | Anonymized | R² 0.462 | 0.615 | 0.412 |

On Anxiety, anonymization costs 1.5 AUC points (0.865 → 0.850) but improves fidelity (0.579 → 0.534), suggesting the two channels play complementary roles: association-only graphs track pairwise statistics more tightly, while semantic edges add utility-relevant structure. On Salary, the original retains a larger advantage (R² 0.560 → 0.462), indicating that semantic priors contribute more to regression tasks involving fine-grained continuous dependencies.

**Revision plan.** We will: (1) rename §4.4 to surface SHD's edge-reversal penalty and direction-aware evaluation (W1); (2) state the operating range, convergence evidence, and clearly qualified n > 200 hypothesis in Limitations (W2); (3) add the anonymization ablation and semantic-prior boundary conditions to the appendix (W3).

We hope these results address your concerns; we would be glad to run further analyses during the discussion period.
