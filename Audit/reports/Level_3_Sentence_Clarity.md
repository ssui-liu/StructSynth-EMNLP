# Level 3: Sentence-Level Clarity & Style -- Audit Report

**Paper:** StructSynth (EMNLP submission)
**Date:** 2026-05-22

---

## 3.1 Sentence Length and Complexity

### 3.1-A: Sentences exceeding ~40 words -- suggest splits

**Issue 1 (introduction.tex, line 18):**

> "Deep generative models capture the joint distribution end-to-end, implicitly learning inter-feature dependencies through distribution fitting; however, their performance varies across architectures, with many requiring substantially more samples to converge reliably."

Word count: ~34. The semicolon creates two independent ideas. Consider splitting.

**Suggested rewrite:**
> "Deep generative models capture the joint distribution end-to-end, implicitly learning inter-feature dependencies through distribution fitting. However, their performance varies across architectures, and many require substantially more samples to converge reliably."

---

**Issue 2 (introduction.tex, line 20):**

> "Large Language Models (LLMs) exploit attribute names, descriptions, and in-context examples as semantic priors, but most LLM-based synthesizers encode dependencies only through flat textualization of attribute--value pairs, without explicitly modeling dependency directions or conditional independence structure."

Word count: ~40. The sentence packs two distinct ideas (what LLMs do well, and their limitation). Consider splitting at "but."

**Suggested rewrite:**
> "Large Language Models (LLMs) exploit attribute names, descriptions, and in-context examples as semantic priors. However, most LLM-based synthesizers encode dependencies only through flat textualization of attribute--value pairs, without explicitly modeling dependency directions or conditional independence structure."

---

**Issue 3 (introduction.tex, line 24):**

> "These designs validate the importance of sparse dependency structure, yet neither treats the graph as a generation plan that organizes the LLM's own generation process---the graph serves as an internal attention mask or a distribution prior rather than determining what to generate, in what order, and conditioned on which context."

Word count: ~50. This sentence is overloaded with subordinate clauses and an em-dash parenthetical.

**Suggested rewrite:**
> "These designs validate the importance of sparse dependency structure, yet neither treats the graph as a generation plan that organizes the LLM's generation process. Instead, the graph serves as an internal attention mask or a distribution prior rather than determining what to generate, in what order, and conditioned on which context."

---

**Issue 4 (introduction.tex, line 30):**

> "In Evidence-Grounded Graph Induction, LLM-based reasoning is integrated with statistical association cues to construct a Directed Acyclic Graph (DAG) from limited samples, with a cycle resolution mechanism ensuring acyclicity."

Word count: ~33. Acceptable, but the trailing participial phrase buries an important design element.

**Suggested rewrite:**
> "In Evidence-Grounded Graph Induction, we integrate LLM-based reasoning with statistical association cues to construct a Directed Acyclic Graph (DAG) from limited samples. A dedicated cycle resolution mechanism ensures acyclicity."

---

**Issue 5 (introduction.tex, line 34, contribution item 1, second sentence):**

> "We instantiate this idea in StructSynth, where Evidence-Grounded Graph Induction fuses LLM semantic priors with statistical association cues to discover reliable structures from limited samples, and Graph-Planned Conditional Synthesis enforces the discovered topology as an executable blueprint for layer-wise generation."

Word count: ~47. This sentence tries to describe both stages at once.

**Suggested rewrite:**
> "We instantiate this idea in StructSynth. In the first stage, Evidence-Grounded Graph Induction fuses LLM semantic priors with statistical association cues to discover reliable structures from limited samples. In the second stage, Graph-Planned Conditional Synthesis enforces the discovered topology as an executable blueprint for layer-wise generation."

---

**Issue 6 (method.tex, line 18):**

> "The decoupled architecture itself reduces per-stage sample complexity: structure discovery only needs to identify which dependencies exist (a discrete, lower-dimensional problem), while generation only needs to model conditional distributions along the discovered graph---a factorization substantially easier than jointly learning both structure and generation."

Word count: ~47. Two em-dashes and a colon create nested subordination that is hard to parse.

**Suggested rewrite:**
> "The decoupled architecture itself reduces per-stage sample complexity. Structure discovery only needs to identify which dependencies exist---a discrete, lower-dimensional problem. Generation only needs to model conditional distributions along the discovered graph, a factorization substantially easier than jointly learning both structure and generation."

---

**Issue 7 (experiments.tex, line 105):**

> "For the structure learning stage: 1) PC Discovery, substituting our LLM-guided discovery with the classical Peter--Clark algorithm; 2) NoTears Discovery, replacing our method with the continuous optimization-based NoTears algorithm; 3) No-Correlation Score, removing statistical correlation scores from the prompt to examine their guiding influence; and 4) Pairwise Discovery, replacing the efficient BFS traversal with less scalable pairwise queries to evaluate the performance-efficiency trade-off."

Word count: ~65. This is a single run-on sentence with four enumerated items.

**Suggested rewrite:** Use a proper enumerated list or split into shorter sentences:
> "For the structure learning stage, we test four variants: (1) PC Discovery substitutes our LLM-guided discovery with the classical Peter--Clark algorithm. (2) NoTears Discovery replaces our method with the continuous optimization-based NoTears algorithm. (3) No-Correlation Score removes statistical correlation scores from the prompt. (4) Pairwise Discovery replaces the efficient BFS traversal with pairwise queries to evaluate the performance-efficiency trade-off."

---

**Issue 8 (experiments.tex, line 137):**

> "Taken together, these results clarify why StructSynth's advantage over CLLM is not merely incremental: CLLM processes features in an arbitrary serialized order, implicitly inducing dependencies from the input sequence, whereas StructSynth encodes dependencies as an explicit DAG that ensures relationships are discovered rather than incidentally induced."

Word count: ~47. The colon introduces a long comparative clause.

**Suggested rewrite:**
> "Taken together, these results clarify why StructSynth's advantage over CLLM is not merely incremental. CLLM processes features in an arbitrary serialized order, implicitly inducing dependencies from the input sequence. By contrast, StructSynth encodes dependencies as an explicit DAG, ensuring that relationships are discovered rather than incidentally induced."

---

### 3.1-B: Clusters of very short sentences

No significant clusters of choppy short sentences were found. The paper generally errs on the side of long sentences.

---

## 3.2 Active vs. Passive Voice

**Issue 1 (introduction.tex, line 30):**

> "LLM-based reasoning **is integrated** with statistical association cues to construct a Directed Acyclic Graph (DAG) from limited samples."

Problem: Unnecessary passive obscures the agent.

**Suggested rewrite:**
> "We integrate LLM-based reasoning with statistical association cues to construct a Directed Acyclic Graph (DAG) from limited samples."

---

**Issue 2 (method.tex, line 90):**

> "Constructing each synthetic data point **is performed** in two sequential phases aligned with the underlying data structure."

Problem: "is performed" is a passive nominalization. "Constructing" is already active, making "is performed" redundant.

**Suggested rewrite:**
> "We construct each synthetic data point in two sequential phases aligned with the underlying data structure."

---

**Issue 3 (method.tex, line 29-30):**

> "The LLM **is then queried** with a prompt that integrates the current graph state, the node, and the association scores."

Problem: Passive voice hides the agent.

**Suggested rewrite:**
> "The framework then queries the LLM with a prompt that integrates the current graph state, the node, and the association scores."

---

**Issue 4 (method.tex, line 38):**

> "For each cycle, the LLM **is queried** with the resolve prompt, which presents the conflicting edges together with their rationales."

Problem: Same unnecessary passive pattern.

**Suggested rewrite:**
> "For each cycle, we query the LLM with the resolve prompt, presenting the conflicting edges together with their rationales."

---

**Issue 5 (experiments.tex, line 15):**

> "Downstream performance **is assessed** using an XGBoost model."

**Suggested rewrite:**
> "We assess downstream performance using an XGBoost model."

---

**Issue 6 (experiments.tex, line 15):**

> "All experiments **are repeated** 10 times, and we report results as mean +/- standard deviation to ensure robustness."

Problem: Mixed voice within the same sentence -- passive ("are repeated") then active ("we report").

**Suggested rewrite:**
> "We repeat all experiments 10 times and report results as mean +/- standard deviation to ensure robustness."

---

## 3.3 Hedging

### 3.3-A: Over-hedged statements that weaken clear results

**Issue 1 (introduction.tex, line 18):**

> "...their performance **varies across architectures**, with **many** requiring substantially more samples to converge reliably."

Problem: "varies across architectures" and "many" are vague hedges.

**Suggested rewrite:**
> "...most architectures require substantially more samples to converge reliably."

---

**Issue 2 (experiments.tex, line 166):**

> "**This suggests** that the structural blueprint acts as a regularizer..."

Problem: "This suggests" is a hedge. The experimental evidence directly supports the claim.

**Suggested rewrite:**
> "The structural blueprint thus acts as a regularizer..."

---

### 3.3-B: Under-hedged claims that overstate evidence

**Issue 1 (abstract.tex, line 3):**

> "...none treats the graph as a generation plan that organizes the LLM's generation process."

Problem: "None" is an absolute claim. Can the authors be certain no prior or concurrent work does this?

**Suggested rewrite:**
> "...to our knowledge, none treats the graph as a generation plan that organizes the LLM's generation process."

---

**Issue 2 (conclusion.tex, line 5):**

> "...investing in a reliable dependency blueprint yields **outsized returns** in generation quality."

Problem: "outsized returns" is informal and potentially overstates the magnitude. The actual gains are consistent but moderate (e.g., +1.65 average AUC over CLLM).

**Suggested rewrite:**
> "...investing in a reliable dependency blueprint yields substantial and consistent improvements in generation quality."

---

## 3.4 Specificity

### 3.4-A: Vague phrases lacking specifics

**Issue 1 (introduction.tex, line 13):**

> "...poses **several intertwined challenges**."

Problem: "Several intertwined challenges" is vague. The sentence immediately narrows to one challenge, making "several" misleading.

**Suggested rewrite:**
> "...poses multiple challenges, chief among them preserving inter-feature dependencies."

---

**Issue 2 (experiments.tex, line 4):**

> "These datasets cover **a range of domains** (e.g., social, medical, business)..."

Problem: "A range of domains" is vague; the parenthetical does the actual work.

**Suggested rewrite:**
> "These datasets span social, medical, and business domains..."

---

**Issue 3 (related_work.tex, line 17):**

> "...but are **computationally expensive** and degrade under data scarcity."

Problem: "Computationally expensive" is vague. Compared to what? In what metric?

**Suggested rewrite:**
> "...but require full model fine-tuning and degrade under data scarcity."

---

**Issue 4 (experiments.tex, line 172):**

> "The gain is **most pronounced** for models with **moderate native capabilities** (e.g., Maverick: +0.028 AUC)..."

Problem: "Moderate native capabilities" is subjective.

**Suggested rewrite:**
> "The gain is largest for mid-tier models such as Maverick (+2.8 AUC points)..."

---

### 3.4-B: Quantitative claims missing numbers

**Issue 1 (introduction.tex, line 19):**

> "...the quality of the learned graph degrades under scarcity---errors in the discovered structure propagate directly into generation."

Problem: No quantitative grounding. The paper has SHD results that could support this claim. Consider adding a forward reference.

---

**Issue 2 (experiments.tex, line 84):**

> "Standard DGMs and structure-aware models perform **notably weaker**..."

Problem: "Notably weaker" without quantification.

**Suggested rewrite:**
> "Standard DGMs and structure-aware models lag behind, averaging 5--13 AUC points below StructSynth..."

---

## 3.5 Conciseness

### 3.5-A: Filler phrases

**Issue 1 (experiments.tex, line 4):**

> "**Additionally**, for evaluating structure discovery quality, we **utilize** three benchmark datasets..."

Problem: "Additionally" is filler; "utilize" is a verbose synonym for "use."

**Suggested rewrite:**
> "To evaluate structure discovery quality, we use three benchmark datasets..."

---

**Issue 2 (related_work.tex, line 25):**

> "An extended discussion of all the above lines of work **is provided** in Appendix..."

Problem: Verbose passive.

**Suggested rewrite:**
> "Appendix A extends this discussion."

---

**Issue 3 (experiments.tex, line 11):**

> "**Following previous work**, we evaluate synthetic data **along three axes**..."

Problem: "Following previous work" is filler. The citations immediately follow.

**Suggested rewrite:**
> "We evaluate synthetic data on three axes..."

---

### 3.5-B: Redundant modifiers

**Issue 1 (introduction.tex, line 24):**

> "...the LLM's **own** generation process"

Problem: "Own" is redundant.

**Suggested rewrite:**
> "...the LLM's generation process"

---

### 3.5-C: Nominalizations

**Issue 1 (experiments.tex, line 159):**

> "...which counts the edge insertions, deletions, or reversals needed to recover the true graph..."

**Suggested rewrite:**
> "...which counts the edges that must be inserted, deleted, or reversed to recover the true graph..."

---

**Issue 2 (method.tex, line 90):**

> "Constructing each synthetic data point is performed in two sequential phases..."

Problem: "Constructing ... is performed" is a nominalization wrapped in passive voice. (Also flagged under 3.2.)

**Suggested rewrite:**
> "We construct each synthetic data point in two sequential phases..."

---

## 3.6 Parallelism

### 3.6-A: Contribution items

**Issue 1 (introduction.tex, lines 34--35):**

The two contribution bullets have inconsistent structures:
- Bullet 1: "We propose to treat..." (active, first-person method contribution)
- Bullet 2: "Experiments on six datasets show that..." (third-person empirical observation)

**Suggested rewrite:**
> - "We propose to treat a dependency graph as a generation plan..."
> - "We demonstrate through experiments on six datasets that StructSynth achieves..."

---

### 3.6-B: Lists within sentences

**Issue 1 (abstract.tex, line 3):**

> "Existing approaches either learn dependencies implicitly through distribution fitting, rely on statistical graph learning that becomes unstable with few samples, or encode structure through flat text serialization."

Problem: Items 1 and 3 follow verb+object+prep-phrase, but item 2 introduces a relative clause breaking the pattern.

**Suggested rewrite:**
> "Existing approaches either learn dependencies implicitly through distribution fitting, discover graph structure through statistical methods that become unstable with few samples, or encode structure through flat text serialization."

---

**Issue 2 (experiments.tex, line 136):**

> "...removing the graph (No Structure, --1.6 pts) or ignoring topological ordering (No Topological Order, --1.1 pts) both degrade utility."

**Suggested rewrite:**
> "Both removing the graph (No Structure, --1.6 pts) and ignoring topological ordering (No Topological Order, --1.1 pts) degrade utility."

---

## 3.7 Ambiguity

### 3.7-A: Pronouns with ambiguous antecedents

**Issue 1 (introduction.tex, line 24):**

> "**These** designs validate the importance of sparse dependency structure..."

Problem: "These designs" refers to GraDe and SPADA mentioned two sentences back.

**Suggested rewrite:**
> "Both GraDe and SPADA validate the importance of sparse dependency structure..."

---

**Issue 2 (introduction.tex, line 15):**

> "Without faithful dependencies..."

Problem: "Faithful" to what? The meaning is inferrable but could be more precise.

**Suggested rewrite:**
> "Without accurately preserved dependencies..."

---

**Issue 3 (experiments.tex, line 90):**

> "**This** is because Statistical Fidelity measures pairwise correlations..."

Problem: Bare "This" without a noun.

**Suggested rewrite:**
> "This gap arises because Statistical Fidelity measures pairwise correlations..."

---

**Issue 4 (experiments.tex, line 166):**

> "**This** suggests that the structural blueprint acts as a regularizer: **it** prevents record-level overfitting..."

Problem: "This" without a noun; "it" has multiple possible antecedents (the suggestion, the blueprint, the regularizer).

**Suggested rewrite:**
> "This pattern suggests that the structural blueprint acts as a regularizer, preventing record-level overfitting and yielding a stable utility-privacy-fidelity balance regardless of sample size."

---

**Issue 5 (related_work.tex, line 24):**

> "However, these methods target causal graph identification as an end in itself..."

Problem: "These methods" could refer to BFS-based strategies, constraint-based integration, or all methods in the paragraph.

**Suggested rewrite:**
> "However, all of these discovery methods target causal graph identification as an end in itself..."

---

### 3.7-B: "This" used alone at sentence start

**Issue 1 (introduction.tex, line 26):**

> "**This** gap raises a natural question..."

Problem: Which gap? The graph-as-mask vs. graph-as-plan gap? The low-data gap? Both?

**Suggested rewrite:**
> "This design gap raises a natural question..."

---

**Issues 2--3:** The bare "This" in experiments.tex lines 90 and 166 are already flagged above under 3.7-A.

---

### 3.7-C: Dangling modifiers

**Issue 1 (method.tex, line 34):**

> "From P_i, new directed edges and previously unseen nodes are extracted and added to the graph and BFS queue, respectively."

Problem: "Respectively" creates ambiguity -- it is unclear whether edges go to the graph and nodes to the queue, or both go to both.

**Suggested rewrite:**
> "From P_i, new directed edges are added to the graph and previously unseen nodes are enqueued in the BFS queue."

---

### 3.7-D: Incomplete comparatives

**Issue 1 (experiments.tex, line 84):**

> "Standard DGMs and structure-aware models perform **notably weaker**..."

Problem: Weaker than what? The comparand is not explicit.

**Suggested rewrite:**
> "Standard DGMs and structure-aware models perform notably weaker than LLM-based methods..."

---

**Issue 2 (experiments.tex, line 172):**

> "Even top-tier models like GPT-4o show **measurable improvement**..."

Problem: Improvement over what? The comparison target is implicit.

**Suggested rewrite:**
> "Even with top-tier models like GPT-4o, StructSynth shows measurable improvement over CLLM..."

---

## Summary of Findings

| Checklist Item | Issues Found | Severity |
|---|---|---|
| 3.1 Sentence length/complexity | 9 issues (multiple sentences >40 words, run-on enumerations) | Medium-High |
| 3.2 Active vs. passive voice | 6 instances of unnecessary passive | Medium |
| 3.3 Hedging | 2 over-hedged, 2 under-hedged | Low-Medium |
| 3.4 Specificity | 4 vague phrases, 2 missing quantification | Medium |
| 3.5 Conciseness | 3 filler phrases, 1 redundant modifier, 2 nominalizations | Low-Medium |
| 3.6 Parallelism | 3 issues (contributions, lists, comparisons) | Low |
| 3.7 Ambiguity | 5 ambiguous pronouns, 3 bare "This", 1 dangling modifier, 2 incomplete comparatives | Medium-High |

### Top Priority Fixes

1. **Sentence length (3.1):** The introduction and method sections contain multiple sentences exceeding 40 words. The ablation variant listing (`experiments.tex`, line 105) at ~65 words is particularly dense. Split these for readability.

2. **Ambiguous "This" (3.7-B):** Three instances of bare "This" at sentence start (`introduction.tex` line 26, `experiments.tex` lines 90 and 166). Always follow "This" with a noun (e.g., "This gap," "This pattern," "This observation").

3. **Passive voice inconsistency (3.2):** Six method/experiment sentences use unnecessary passive voice ("is integrated," "is queried," "is performed," "is assessed," "are repeated") when active voice would be clearer and consistent with surrounding "we" sentences.

4. **Incomplete comparatives (3.7-D):** Two instances where comparative adjectives lack explicit comparands ("notably weaker," "measurable improvement"). Readers should not have to infer what is being compared.
