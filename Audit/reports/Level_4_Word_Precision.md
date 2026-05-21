# Level 4: Word-Level Precision Audit Report

**Paper:** StructSynth (EMNLP submission)  
**Date:** 2026-05-22  
**Files audited:** `abstract.tex`, `introduction.tex`, `related_work.tex`, `method.tex`, `experiments.tex`, `conclusion.tex`, `limitations.tex`

---

## 4.1 Terminology Consistency

### 4.1.1 Term Glossary

| Concept | Preferred Term | Variants Found | Severity |
|---------|---------------|----------------|----------|
| The DAG used to organize synthesis | **generation plan** | "blueprint", "executable blueprint", "generative blueprint", "structural blueprint", "generation blueprint", "executable generation plan", "dependency blueprint" | Medium |
| The process of building the graph | **graph induction** (stage name) | "structure discovery", "structure learning", "graph discovery", "graph learning", "graph construction", "dependency discovery" | Medium |
| The statistical signals fed to the LLM | **association cues** / **association scores** | "correlation scores", "statistical signals", "statistical scores", "statistical evidence" | Medium |
| Table columns / data dimensions | **features** (most frequent) | "attributes", "columns", "variables" | Low |
| The evaluation metric for distribution matching | **Statistical Fidelity** | "Structural Fidelity" (section heading) | High |
| The LLM domain knowledge | **semantic prior** | "world knowledge", "informative prior", "semantic priors" (plural) | Low |
| Data shortage condition | **data scarcity** | "sample scarcity", "scarce samples", "limited samples", "limited data", "few samples", "low-data", "data-scarce" | Low |

### 4.1.2 Detailed Findings

**Finding 1 (HIGH): "Structural Fidelity" vs. "Statistical Fidelity"**

The metric is consistently defined and referred to as **"Statistical Fidelity"** throughout the paper (abstract, introduction, experiments Sec. 5.1.3, Sec. 5.2.2, Sec. 5.4, conclusion). However, a section heading uses a different term:

- `experiments.tex` line 157: `\subsection{Structural Fidelity under Ground-Truth Graphs}`

This heading uses "Structural Fidelity" while every other mention uses "Statistical Fidelity." The subsection actually discusses graph-structure recovery quality (measured by SHD), not distributional fidelity, so the heading is semantically correct for its content -- but the near-identical wording causes confusion with the metric.

> **Suggestion:** Rename the heading to avoid collision: `\subsection{Structure Recovery under Ground-Truth Graphs}` or `\subsection{Graph Recovery Quality}`.

**Finding 2 (MEDIUM): "generation plan" vs. "blueprint" proliferation**

"Generation plan" is the primary term for the core concept. However, "blueprint" appears with 6+ distinct compound modifiers:

- `related_work.tex` line 7: `"leverages the learned graph as a blueprint"`
- `related_work.tex` line 19: `"an explicit generation blueprint"`
- `introduction.tex` line 30 footnote: `"a generative blueprint"`
- `introduction.tex` line 34: `"an executable blueprint"`
- `method.tex` line 8: `"an executable blueprint"`
- `experiments.tex` line 84: `"a structural blueprint"`
- `experiments.tex` line 90: `"The structural blueprint"`
- `experiments.tex` line 136: `"the structural blueprint"`
- `experiments.tex` line 166: `"the structural blueprint"`
- `conclusion.tex` line 5: `"a reliable dependency blueprint"`

> **Suggestion:** Standardize on "generation plan" in formal definitions and use plain "blueprint" as the sole stylistic variant. Avoid the compound modifier proliferation (structural/executable/generative/dependency).

**Finding 3 (MEDIUM): "association cues" vs. "association scores" vs. "correlation scores"**

- `abstract.tex`, `introduction.tex` lines 30/34, `conclusion.tex` line 3, `limitations.tex` line 6: `"statistical association cues"`
- `method.tex` line 7: `"statistical association cues"` and `"statistical scores"`
- `method.tex` line 29: `"association scores"`
- `experiments.tex` line 105: `"statistical correlation scores"` (ablation: "No-Correlation Score")

The ablation variant "No-Correlation Score" uses "correlation" while the method itself uses "association."

> **Suggestion:** Unify to "association scores" (matching notation $\mathcal{S}$) for the technical term. Consider renaming the ablation from "No-Correlation Score" to "No-Association Score."

**Finding 4 (MEDIUM): "structure discovery" vs. "structure learning" vs. "graph induction"**

The official stage name is "Evidence-Grounded Graph Induction," but:

- `experiments.tex` line 105: `"the structure learning stage"`
- `experiments.tex` line 136: `"structure learning under data scarcity"`
- `experiments.tex` lines 4, 159: `"structure discovery quality"`
- `method.tex` line 18: `"structure discovery"`
- `related_work.tex` line 23: both `"structure learning"` and `"structure discovery"`
- `limitations.tex` line 4: `"structure discovery quality"`

> **Suggestion:** Prefer "structure discovery" or "graph induction" over "structure learning," which connotes parameter-based optimization.

**Finding 5 (LOW): "features" vs. "attributes" vs. "columns" vs. "variables"**

- `method.tex` line 4: `"$K$ attributes"` (formal definition)
- `related_work.tex` line 18: `"treats each column independently"`
- `related_work.tex` line 23: `"variable semantics"`
- `limitations.tex` line 4: `"feature names"`

> **Suggestion:** Prefer "attributes" in formal/definitional contexts (matching notation $\mathbf{A}$), "features" in ML discussion. Avoid "columns."

---

## 4.2 Academic Register

### 4.2.1 Contractions
**No contractions found.** Clean.

### 4.2.2 First-Person Singular
**No instances of "I."** Consistently uses "we."

### 4.2.3 Informal Language
**No instances** of "a lot of," "kind of," "pretty good," "get rid of," "stuff," or "things."

### 4.2.4 Borderline Register Issues

**Finding 6 (LOW): "outsized returns"**
- `conclusion.tex` line 5: `"investing in a reliable dependency blueprint yields outsized returns in generation quality"`

Financial idiom. > **Suggestion:** `"yields disproportionate gains in generation quality"`.

**Finding 7 (LOW): "synergy is vital"**
- `experiments.tex` line 136: `"Finally, \textbf{synergy is vital}:"`

Business buzzword in bold. > **Suggestion:** `"Finally, \textbf{the two components are complementary}:"`.

**Finding 8 (LOW): "data-hungry"**
- `related_work.tex` line 12: `"but are data-hungry"`

Colloquial but widely accepted in ML. No change required.

---

## 4.3 Commonly Confused Words

**All checks passed:**

- **which/that**: All ", which" clauses are non-restrictive (correct). All "that" clauses are restrictive (correct). No errors found.
- **e.g./i.e.**: Four instances of "e.g." (experiments.tex lines 4, 172; limitations.tex line 5 x2), all used correctly to introduce examples. No "i.e." instances. No misuse.
- **compare to/with**: Not used; the paper uses "compare...against" (acceptable).
- **fewer/less**: No confusable instances. `"less scalable"` (experiments.tex line 105) correctly modifies an adjective.
- **affect/effect**: Not used. No issues.

---

## 4.4 Overused Words

### 4.4.1 Word Counts

| Word | Count |
|------|-------|
| leverage | 3 |
| utilize | 2 |
| novel | 0 |
| significant/significantly | 1 |
| robust/robustness | 3 |
| paradigm | 1 |
| state-of-the-art | 3 |
| **substantial/substantially** | **6** |
| most pronounced | 3 |

### 4.4.2 Flagged

**Finding 9 (MEDIUM): "substantial/substantially" -- 6 occurrences**

- `introduction.tex` line 18: `"requiring substantially more samples"`
- `method.tex` line 18: `"a factorization substantially easier"`
- `related_work.tex` line 23: `"substantially reducing the number of LLM calls"`
- `experiments.tex` line 84: `"yields substantial gains"`
- `experiments.tex` line 161: `"produce substantially higher errors"`
- `experiments.tex` line 172: `"can substantially boost weaker models"`

> **Suggestion:** Replace 2-3 instances with "considerably," "markedly," "meaningfully," or "much."

**Finding 10 (LOW): "most pronounced" -- 3 consecutive uses**

- `experiments.tex` line 161: `"the advantage most pronounced in low-data settings"`
- `experiments.tex` line 166: `"The advantage is most pronounced in the low-data regime"`
- `experiments.tex` line 172: `"The gain is most pronounced for models with moderate native capabilities"`

> **Suggestion:** Replace at least two: `"largest"`, `"greatest"`, `"The gap widens"`, `"The improvement peaks"`.

**Finding 11 (LOW): "state-of-the-art" -- 3 identical phrases**

- `abstract.tex`: `"achieves state-of-the-art downstream utility"`
- `introduction.tex` line 35: `"achieves state-of-the-art downstream utility"`
- `conclusion.tex` line 4: `"achieves state-of-the-art downstream utility"`

> **Suggestion:** Consider varying one to `"achieves the best downstream utility"` or `"attains leading downstream utility"`.

---

## 4.5 Preposition Accuracy

**No preposition errors found.** All checked usages are correct:
- `"based on"` (not "based off")
- `"rely on"` (not "rely of")
- `"aligned with"`, `"at the cost of"`, `"complementary to"`, `"robustness to"` -- all correct.

---

## Summary

| # | Severity | Category | Issue |
|---|----------|----------|-------|
| 1 | **HIGH** | Terminology | "Structural Fidelity" heading vs. "Statistical Fidelity" metric -- naming collision |
| 2 | MEDIUM | Terminology | "generation plan" vs. 7+ "blueprint" compound variants |
| 3 | MEDIUM | Terminology | "association cues" vs. "association scores" vs. "correlation scores" |
| 4 | MEDIUM | Terminology | "structure discovery" vs. "structure learning" vs. "graph induction" |
| 5 | LOW | Terminology | "features" vs. "attributes" vs. "columns" vs. "variables" |
| 6 | LOW | Register | "outsized returns" -- financial idiom |
| 7 | LOW | Register | "synergy is vital" -- business buzzword |
| 8 | LOW | Register | "data-hungry" -- colloquial (acceptable) |
| 9 | MEDIUM | Overuse | "substantial/substantially" x6 |
| 10 | LOW | Overuse | "most pronounced" x3 in consecutive subsections |
| 11 | LOW | Overuse | "state-of-the-art" x3 with identical phrasing |

**Passed:** No contractions, no informal language, no first-person singular, all which/that and e.g./i.e. correct, no preposition errors.

**Total: 11 actionable items (1 high, 4 medium, 6 low).**
