# Level 2: Paragraph-Level Coherence Audit Report

**Paper:** StructSynth (EMNLP submission)  
**Date:** 2026-05-22  
**Scope:** All sections (abstract, introduction, related work, methodology, experiments, conclusion, limitations)

---

## 2.1 Topic Sentences

**Overall Assessment: PASS (with minor issues)**

### Section-by-Section Analysis

**Abstract (single paragraph):**  
The opening sentence ("Tabular data derives its value from inter-feature dependencies, yet preserving them during synthesis is fragile when samples are scarce.") immediately establishes the problem domain and the core challenge. Effective.

**Introduction:**
- **P1** (L13--15): "Low-data tabular synthesis...poses several intertwined challenges." Clear topic sentence establishing the problem space. PASS.
- **P2** (L17--20): "As illustrated in Figure 1, existing tabular generators handle dependencies in three important but partial ways." Clear topic sentence previewing a structured survey of limitations. PASS.
- **P3** (L22--26): "A natural response is to make dependencies explicit in the generation process." States the paragraph's argument clearly. PASS.
- **P4** (L28--31): "We answer this question with StructSynth..." Clear topic sentence introducing the proposed solution. PASS.

**Related Work:**
- **P1** (Tabular Synthesis): "Deep generative models...capture the joint distribution end-to-end but are data-hungry..." The topic sentence fuses the category with its limitation. PASS.
- **P2** (LLM-Based): "Fine-tuning approaches such as GReaT...serialize rows as text..." Opens with the sub-topic clearly. PASS.
- **P3** (LLM-Assisted Discovery): "LLMs have been applied to structure learning itself." Clean topic sentence. PASS.

**Methodology:**
- **Opening P1** (L3--4): "Synthesizing realistic tabular data from scarce samples requires preserving the dependency relationships among features..." Establishes the problem formally. PASS.
- **Opening P2** (L6--8): "We address this by representing inter-feature dependencies as a DAG and using it as a generation plan..." Clear topic sentence connecting to the design. PASS.
- **Sec 3.1 opening** (L12): "The dependency structure is represented as a DAG G=(V,E)..." States the representation. PASS.
- **Design Rationale** (L14--18): "Three complementary mechanisms adapt this stage to data-scarce settings." Clear topic sentence previewing a list. PASS.
- **Graph Initialization** (L21--25): "The graph construction begins by identifying source nodes..." PASS.
- **Expansion** (L29--34): "In each BFS iteration t, a node A_i is dequeued..." **WEAK.** This sentence jumps directly into procedural detail without first stating the paragraph's purpose (i.e., that the graph is expanded by proposing successors grounded in both structure and statistics). The reader must parse the mechanics to understand the intent.
- **Cycle Resolution** (L38--42): "Integrating the proposed edges into G_t may introduce cycles." PASS -- the topic (cycle handling) is stated up front.
- **Sec 3.2 opening** (method.tex L90): "Upon learning the dependency structure G=(V,E), we utilize it to guide synthetic tabular data generation." PASS.
- **Generating Graph-Based Values** (L94--99): "The nodes V are partitioned into topological layers..." **WEAK.** Similar to Expansion, this opens with a procedural step rather than a statement of intent.
- **Completing Synthesis** (L103--107): "Values for isolated attributes...are generated in a single step..." PASS, though slightly procedural.

**Experiments:**
- **Datasets** (L4): "We conduct experiments on six real-world tabular datasets..." PASS.
- **Baselines** (L8): "We compare our method against twelve baselines..." PASS.
- **Evaluation Metrics** (L11): "Following previous work, we evaluate synthetic data along three axes..." PASS.
- **Implementation Details** (L15): "We use gpt-4o-mini with a temperature of 0.9..." PASS (though this is more a detail dump than a topic-sentence-driven paragraph).
- **Downstream Model Performance** (L84): "Table 1 summarizes the downstream results." Minimal but functional. PASS.
- **Privacy Preservation** (L90): "Table 2 reveals a fundamental tension between fidelity and privacy..." Strong topic sentence. PASS.
- **Ablation Study intro** (L105): "To isolate the contributions of our method's two main stages, we evaluate seven variants." PASS.
- **Ablation results** (L136): "The results (Table 3) yield three insights." Clear topic sentence. PASS.
- **Structural Fidelity** (L159): "We evaluate structure discovery quality on three bnlearn benchmarks..." PASS.
- **Influence of Training Sample Size** (L166): "To evaluate data efficiency, we vary the training size..." PASS.
- **Influence of Different LMs** (L172): "To assess generalizability, we benchmark StructSynth against CLLM..." PASS.

**Conclusion:** All three paragraphs open with clear topic sentences. PASS.

**Limitations:** All three `\paragraph{}` blocks open with clear statements of the limitation. PASS.

### Skimming Test
A reader skimming only topic sentences would recover: problem statement -> existing approaches -> gap -> proposed solution -> method details (DAG discovery, synthesis) -> experimental setup -> results on utility, privacy, ablation, structure quality, data efficiency, LLM choice -> conclusion -> limitations. The argument is largely reconstructable.

### Specific Issues
1. **Sec 3.1.2, Expansion and Reasoned Link Generation** (method.tex L29): Topic sentence should state the paragraph's purpose before diving into BFS iteration mechanics.
2. **Sec 3.2.1, Generating Graph-Based Values** (method.tex L94): Similar issue -- leads with procedural detail rather than intent.

### Suggestions
- **Expansion (Sec 3.1.2):** Prepend a sentence like: "The graph is expanded by iteratively proposing successors for each frontier node, using both statistical associations and LLM reasoning."
- **Generating Graph-Based Values (Sec 3.2.1):** Rewrite opening as: "Synthesis proceeds layer by layer in topological order, with each layer's features conditioned on their parent values. Specifically, the nodes V are partitioned into topological layers..."

---

## 2.2 Paragraph Unity

**Overall Assessment: PASS (with two issues)**

### Section-by-Section Analysis

**Abstract:** Single paragraph, makes one unified point (problem, gap, solution, result). At ~9 sentences it is dense but acceptable for an abstract. PASS.

**Introduction:**
- P1 (3 sentences): One point -- the problem of low-data tabular synthesis. PASS.
- P2 (4 sentences): One point -- three paradigms and their limitations. PASS.
- P3 (4 sentences): One point -- recent graph-aware methods and the remaining gap. PASS.
- P4 (4 sentences + bullet list): One point -- the proposed solution and contributions. PASS.

**Related Work:** All three `\paragraph{}` blocks are unified around a single topic each. PASS.

**Methodology:** All paragraphs make exactly one point. PASS.

**Experiments:**
- **Downstream Performance** (L84): 3 sentences. One point. PASS.
- **Privacy Preservation** (experiments.tex L90): **FAIL** -- This paragraph makes multiple points: (a) the fidelity-privacy tension with examples from baselines, (b) StructSynth's privacy advantage, (c) the argument that high fidelity does not guarantee utility (the Bayesian Sampler argument), and (d) an explanation of why the DAG serves as a regularizer. This is approximately 6 sentences covering at least three distinct arguments. **Should be split.**
- **Ablation intro** (L105): Unified around defining ablation variants. PASS.
- **Ablation results** (L136--137): Three insights labeled "First... Second... Finally..." plus a wrap-up sentence. Unified around interpreting one table. PASS.

**Conclusion:** Three short paragraphs, each making one point. PASS.

**Limitations:** Three paragraphs, each making one point. PASS.

### Single-Sentence Paragraphs
- **Sec 3.1** (method.tex L12): Single sentence, but functions as a section-opening definition before the `\paragraph{Design Rationale}` block. Acceptable.
- **Sec 3.2** (method.tex L90): Also a section-opening single sentence. Acceptable.
- **Sec 4, experiments.tex L155**: "The above gains generalize beyond the XGBoost evaluator..." -- This single sentence sits between the ablation analysis and the next subsection. It is an **orphan sentence** that should be folded into the preceding ablation paragraph or expanded.

### Specific Issues
1. **Experiments, Privacy Preservation paragraph (experiments.tex L90):** Covers fidelity-privacy tension, StructSynth results, a counter-argument about Bayesian Sampler, and a theoretical explanation. Too many points for one paragraph.
2. **Experiments, L155:** Orphan single sentence about downstream model generalization.

### Suggestions
- **Split Privacy Preservation into two paragraphs:** (a) The fidelity-privacy tension with examples from baselines and StructSynth's position; (b) The argument that high pairwise fidelity does not guarantee utility, using the Bayesian Sampler ablation as evidence, and the explanation of the DAG as a regularizer.
- **L155 (downstream generalization):** Either merge this sentence into the preceding ablation paragraph or expand it into a short paragraph with one additional sentence of analysis.

---

## 2.3 Transitions

**Overall Assessment: PASS (with minor issues)**

### Section-by-Section Analysis

**Introduction:**
- P1 -> P2: "As illustrated in Figure 1, existing tabular generators handle dependencies in three important but partial ways." Bridges from the problem (P1) to the landscape survey (P2). PASS.
- P2 -> P3: "A natural response is to make dependencies explicit in the generation process." Excellent bridge from the gap to the response. PASS.
- P3 -> P4: P3 ends with a research question; P4 opens "We answer this question with StructSynth." Textbook transition. PASS.

**Related Work:** Paragraph transitions are handled by `\paragraph{}` headings. The progression (Tabular Synthesis -> LLM-Based Generation -> LLM-Assisted Discovery) follows a logical narrowing funnel. PASS.

**Methodology:**
- Opening P1 -> P2: P1 defines the problem; P2 opens "We address this by..." Clear logical connective. PASS.
- Sec 3.1 opening -> Design Rationale: The `\paragraph{Design Rationale}` heading handles this, but the transition from the one-sentence DAG definition to the design rationale is **slightly abrupt**. Minor issue.
- Within Sec 3.1 (Init -> Expansion -> Cycle Resolution): Sequential subsubsections with clear ordering. PASS.
- Sec 3.1 -> Sec 3.2: The opening sentence of 3.2 ("Upon learning the dependency structure...") explicitly bridges from discovery to synthesis. PASS.

**Experiments:**
- Ablation results -> L155 (downstream generalization) -> Structural Fidelity: The orphan sentence about downstream model generalization is followed directly by a subsection on ground-truth graph evaluation. The topics are unrelated, and the single sentence provides no bridge. **Minor issue** (mitigated by subsection heading).
- All other transitions are handled by subsection headings and are adequate. PASS.

**Conclusion:** Natural progression (summary -> results -> broader implication). PASS.

**Limitations:** Three independent `\paragraph{}` blocks. No transitions needed. PASS.

### Specific Issues
1. **Methodology, Sec 3.1:** The single-sentence DAG definition (method.tex L12) transitions to a `\paragraph{Design Rationale}` block. The jump from "here is the representation" to "here is why this works in low-data regimes" could use a brief bridge.
2. **Experiments, L155 -> Sec 4.4:** The orphan sentence about downstream generalization sits awkwardly before a topically unrelated subsection.

### Suggestions
- **Sec 3.1, after DAG definition:** Add a brief transition such as: "Before detailing the construction procedure, we motivate three design choices that make this approach effective under data scarcity."
- **L155:** Move this sentence to the end of the ablation results paragraph, or fold it into a brief "Generalization" paragraph at the end of the ablation subsection.

---

## 2.4 Information Flow (Given -> New)

**Overall Assessment: PASS (with minor issues)**

### Section-by-Section Analysis

**Abstract:** Clean Given->New progression: known problem (tabular data + dependencies) -> gap (existing methods) -> new concept (generation plan) -> new method (StructSynth) -> stages -> results. PASS.

**Introduction:** Each paragraph builds cleanly on the prior. PASS.

**Methodology:**
- **Generating Graph-Based Values (method.tex L94):** Introduces "topological layers L", "dependency subgraph G_i", and "parent nodes Gamma^-(L_i)" in rapid succession. **BORDERLINE.** Three new notations in one sentence is dense. The reader must absorb L, G_i, and Gamma^- simultaneously.
- All other paragraphs introduce new notation/concepts adequately. PASS.

**Experiments:**
- **Privacy Preservation (experiments.tex L90), mid-paragraph:** "Importantly, high pairwise fidelity does not guarantee downstream utility: the *Bayesian Sampler* ablation achieves the best raw fidelity (48.86) yet the lowest AUC (81.17)." The Bayesian Sampler ablation has **not been introduced yet** at this point in the paper -- it is defined later in the Ablation Study section (experiments.tex L105). **FAIL -- forward reference to an unexplained concept.**

**Key Terms Introduction Check:**
- "Generation plan": First introduced in the abstract, elaborated in the introduction. PASS.
- "DAG": First used in the abstract with definition, footnoted in the introduction. PASS.
- "BFS": Used in the method (method.tex L12, L29) **without expansion of the acronym**. While well-known in CS, a first-use expansion would be courteous for the NLP audience.
- "Bayesian Sampler" ablation: Referenced in the Privacy Preservation paragraph before it is defined in the Ablation Study. **FAIL -- forward reference.**
- "SHD" (Structural Hamming Distance): Introduced in the Datasets paragraph with full definition. PASS.

### Specific Issues
1. **Sec 3.2.1 (method.tex L94):** Three new notations (L, G_i, Gamma^-) in a single sentence.
2. **Experiments, Privacy Preservation (experiments.tex L90):** References the "Bayesian Sampler" ablation before it is defined in the Ablation section. This forces the reader to either skip ahead or accept an unexplained reference.
3. **"BFS"** is used without expansion at first occurrence.

### Suggestions
- **method.tex L94:** Break the dense notation into two sentences: "The nodes V are partitioned into topological layers L = (L_1, ..., L_m). For each layer L_i, we extract its dependency subgraph G_i, comprising the layer's nodes together with their parents Gamma^-(L_i), along with the corresponding columns from the few-shot examples."
- **experiments.tex L90 (Bayesian Sampler reference):** Either (a) move the "high fidelity does not guarantee utility" argument to the ablation section where Bayesian Sampler is defined, or (b) add a brief parenthetical definition: "...the *Bayesian Sampler* ablation (Sec 4.3, which replaces the LLM generator with a fitted Bayesian network) achieves..."
- **method.tex L12:** Expand "BFS" at first use: "...iteratively via breadth-first search (BFS) as described below."

---

## 2.5 Paragraph-Level Redundancy

**Overall Assessment: PASS (with two notable redundancies)**

### Cross-Section Redundancy Analysis

**Abstract vs. Introduction:** The introduction appropriately expands on the abstract's compressed claims without merely restating them. PASS.

**Introduction vs. Related Work:**
- The introduction's P3 discusses GraDe and SPADA specifically. The Related Work's "LLM-Based Tabular Generation" paragraph also discusses GraDe and SPADA with **nearly identical framing**:
  - **Intro (introduction.tex L23--24):** "GraDe injects a learned sparse dependency graph into the Transformer attention mechanism, while SPADA uses the graph to guide lightweight statistical estimators such as normalizing flows."
  - **Related Work (related_work.tex L19--20):** "GraDe moves closer to structure-aware LLM generation by injecting a learned sparse dependency graph into the Transformer attention mechanism... SPADA further decouples the two stages by replacing LLM-based generation with lightweight statistical estimators (KDE, normalizing flows)..."
  
  These two passages make nearly identical points about GraDe and SPADA. **FAIL -- redundant descriptions of the same two methods.**

**Introduction vs. Methodology:**
- The introduction's P4 (introduction.tex L28--31) previews the two-stage design. The methodology's opening P2 (method.tex L6--8) restates the same two-stage overview in nearly identical language:
  - **Intro L30:** "In Evidence-Grounded Graph Induction, LLM-based reasoning is integrated with statistical association cues to construct a DAG..."
  - **Method L7:** "Evidence-Grounded Graph Induction constructs the DAG from limited data by combining LLM-based reasoning with statistical association cues..."
  
  **BORDERLINE.** The method section restates the overview instead of simply referencing the introduction and diving into details. Common in NLP papers but wastes space in a page-limited venue.

**Introduction vs. Conclusion:** The conclusion restates the core contribution. This is expected and standard. PASS.

**Method vs. Experiments:** The ablation study re-explains component roles briefly to orient the reader. These are functional, not redundant. PASS.

**Conclusion vs. Abstract:** The conclusion's P2 is nearly word-for-word identical to the abstract's final sentence. **BORDERLINE** -- standard for conclusions, but worth noting.

### Specific Issues
1. **Introduction P3 vs. Related Work (GraDe + SPADA):** Near-duplicate descriptions of two key prior methods.
2. **Introduction P4 vs. Method opening P2:** The two-stage overview is stated twice in very similar language.

### Suggestions
- **Introduction P3 (GraDe/SPADA):** Shorten to one sentence: "Recent graph-aware methods (GraDe, SPADA; see Sec 2) incorporate dependency structure into generation but treat the graph as an internal mechanism rather than an explicit generation plan, and neither targets the low-data regime." Defer the details to Related Work.
- **Method opening P2 (method.tex L6--8):** Rather than restating the two-stage overview, begin with what is new: "As depicted in Figure 2, StructSynth realizes this idea through two coupled stages." Then proceed directly to the details without re-summarizing what was already stated in the introduction.

---

## Summary Table

| Checklist Item | Verdict | Key Issues |
|---|---|---|
| 2.1 Topic Sentences | **PASS** (minor) | Sec 3.1.2 (Expansion) and Sec 3.2.1 (Graph-Based Values) open with procedural detail instead of stating intent |
| 2.2 Paragraph Unity | **PASS** (minor) | Privacy Preservation paragraph (Sec 4.2) covers 3--4 distinct points; orphan single sentence at experiments.tex L155 |
| 2.3 Transitions | **PASS** (minor) | Sec 3.1 DAG definition to Design Rationale is slightly abrupt; L155 orphan sentence before unrelated subsection |
| 2.4 Information Flow | **PASS** (minor) | Bayesian Sampler ablation forward-referenced before definition; dense notation in Sec 3.2.1; BFS not expanded |
| 2.5 Redundancy | **PASS** (minor) | GraDe/SPADA described nearly identically in Intro P3 and Related Work; two-stage overview restated in Method opening |

## Priority Fixes (ranked by impact)

1. **Split the Privacy Preservation paragraph (experiments.tex L90):** This is the most impactful fix -- the paragraph currently conflates baseline analysis, StructSynth positioning, a forward-referencing ablation argument, and a theoretical explanation. Split into two focused paragraphs.

2. **Fix the Bayesian Sampler forward reference (experiments.tex L90):** Either relocate the argument to the ablation section or add a parenthetical definition so the reader is not required to look ahead.

3. **De-duplicate GraDe/SPADA descriptions (introduction.tex P3 vs. related_work.tex):** Compress the introduction's treatment to a single sentence and let Related Work carry the detailed discussion.

4. **Strengthen topic sentences in method.tex Sec 3.1.2 and Sec 3.2.1:** Add intent-stating opening sentences before diving into procedural/mathematical detail.

5. **Minor:** Expand "BFS" at first use (method.tex L12); break dense notation in method.tex L94 across two sentences; resolve orphan sentence at experiments.tex L155.
