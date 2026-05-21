# Level 1: Section-Level Structure & Function Audit Report

**Paper:** StructSynth (EMNLP submission)
**Date:** 2026-05-22

---

## 1.1 Abstract (`sections/abstract.tex`)

### Follows Background -> Problem -> Method -> Results -> Significance arc?
**PASS.** The abstract follows a clear arc: (1) Background: "Tabular data derives its value from inter-feature dependencies"; (2) Problem: "preserving them during synthesis is fragile when samples are scarce"; (3) Method: "We introduce StructSynth..."; (4) Results: "achieves state-of-the-art downstream utility and privacy preservation"; (5) Significance: "both stages contribute independently."

### Contains at least one concrete quantitative result?
**FAIL.** The abstract says "achieves state-of-the-art downstream utility and privacy preservation" but provides zero numbers. Add at least one concrete figure, e.g., "avg. rank 1.00 across six datasets, +1.65 pp over the strongest baseline."

### Avoids undefined acronyms or paper-specific notation?
**PASS.** All acronyms are either defined (DAG, LLM) or well-known.

### Stays within ~250 words?
**PASS.** Well within the limit.

### Does not contain citations?
**PASS.** No citations in the abstract.

### First sentence anchors the reader in a known domain?
**PASS.** "Tabular data derives its value from inter-feature dependencies" -- immediately establishes the domain.

---

## 1.2 Introduction (`sections/introduction.tex`)

### P1 opens with broadly accessible motivation?
**PASS.** "Low-data tabular synthesis---generating realistic records from scarce samples in domains such as healthcare, finance, and education---poses several intertwined challenges."

### Problem scope clearly stated?
**PASS.** The problem is narrowed to "preserving inter-feature dependencies... under sample scarcity."

### Gap statement uses explicit language?
**PASS.** Uses "yet," "Moreover," and "This gap raises a natural question" to mark the gap clearly.

### Contributions are listed and each is concrete and falsifiable?
**PASS.** Two numbered contributions, both concrete and falsifiable.

### Each contribution corresponds to a specific section or experiment?
**PASS.** Contribution 1 maps to Section 3 (method); Contribution 2 maps to Section 4 (experiments).

### No contribution is merely "we propose X" without stating what X achieves?
**PASS.** Each contribution describes what is achieved.

### Flow moves from broad -> narrow -> contributions without backtracking?
**PASS.** Clean narrative flow.

### Avoids "laundry list" anti-pattern?
**PASS.** Prior work is synthesized, not listed.

### Method name introduced with intuitive description before formalism?
**PASS.** "We answer this question with StructSynth" followed by an intuitive description.

---

## 1.3 Related Work (`sections/related_work.tex`)

### Organized thematically?
**PASS.** Three thematic paragraphs: Tabular Synthesis, LLM-Based Generation, LLM-Assisted Discovery.

### Each paragraph ends with positioning statement?
**PASS.** Each paragraph concludes by distinguishing this work.

### Covers expected categories?
**PASS.** Covers DGMs, structure-aware methods, LLM-based generation, LLM-assisted discovery.

### Avoids straw-man descriptions?
**PASS.** Fair descriptions throughout.

### No redundancy with introduction?
**FAIL (minor).** GraDe and SPADA are described in nearly identical terms in both the introduction and related work. The introduction should compress this to a single high-level sentence and defer details to Related Work.

### Recent work (2023-2025) represented?
**PASS.** Well-represented.

### No orphan citations?
**PASS.** Every cited work is discussed.

---

## 1.4 Method (`sections/method.tex`)

### Opens with high-level overview before formalism?
**PASS.** Opens with problem statement and pipeline overview referencing Figure 2.

### Notation introduced before first use?
**PASS.** All notation defined before use.

### Each subsection = named pipeline component?
**PASS.** Sec 3.1 = Evidence-Grounded Graph Induction; Sec 3.2 = Graph-Planned Conditional Synthesis.

### Design choices justified?
**PASS.** "Design Rationale for Low-Data Regimes" paragraph provides justification.

### Reproducible from section alone?
**FAIL (minor).** The main method text defers too many implementation-critical details to the appendix without inline summaries: how the few-shot subset is selected, which specific association measures are used (Pearson's R, Correlation Ratio, Cramer's V -- named only in the appendix), and how cycle detection works. Add brief inline specifications.

### Equations numbered only if referenced?
**PASS.** All numbered equations serve the narrative (though see Level 8 for referencing issues).

### Algorithm matches text?
**PASS.** Algorithm description matches the text.

### Transitions between subsections?
**PASS.** "Upon learning the dependency structure G=(V,E), we utilize it to guide..." bridges Sec 3.1 to 3.2.

---

## 1.5 Experiments (`sections/experiments.tex`)

### Setup covers datasets, baselines, metrics, implementation details?
**PASS.** All four covered in dedicated subsections.

### Baselines fairly described and include SOTA?
**PASS.** 12 baselines across 3 categories, including state-of-the-art methods.

### Each table/figure referenced and takeaway stated?
**PASS.** Every table and figure is referenced with explicit takeaways.

### Observation separated from interpretation?
**PASS.** Results discussion separates "X outperforms Y by Z%" from "This suggests..."

### Ablation connects to design choices?
**PASS.** Seven ablation variants directly test design choices.

### Statistical significance/variance reported?
**PASS.** Mean +/- std over 10 seeds reported throughout.

### Negative results discussed honestly?
**PASS.** Statistical Fidelity ranking (7.92) discussed honestly with explanation.

### No result without context?
**PASS.** All results are contextualized with baselines and explanations.

---

## 1.6 Conclusion (`sections/conclusion.tex`)

### Summarizes without copy-pasting abstract?
**PASS.** Restates contributions in different framing.

### States limitations or future work?
**FAIL.** The conclusion contains no mention of limitations or future work. Add 1-2 sentences such as: "Future work could extend the framework to cyclic dependencies, anonymized schemas, and local open-source LLMs."

### No new claims/results?
**PASS.** No new claims introduced.

### No over-generalization?
**PASS.** Uses "suggest" appropriately.

### Forward-looking ending?
**PASS.** "Investing in a reliable dependency blueprint yields outsized returns in generation quality."

---

## 1.7 Limitations (`sections/limitations.tex`)

### Identifies genuine limitations?
**PASS.** Three genuine limitations: semantic prior, DAG assumption, API dependence.

### Specific and actionable?
**PASS.** Each limitation is specific with clear implications.

### Acknowledges computational cost, dataset scope, assumptions?
**PASS.** DAG assumption and API cost explicitly discussed.

### Does not undermine contributions?
**PASS.** Framed as scope, not failure.

---

## 1.8 Appendix (`sections/appendix.tex`)

### Contains supplementary details?
**PASS.** Extensive supplementary material.

### Every item referenced from main text?
**PASS.** All items referenced.

### No critical info hidden?
**FAIL (minor).** The DAG justification ("Why a DAG?") is a fundamental design decision but is entirely in the appendix. Add a 2-3 sentence summary in the main method section.

### Well-organized?
**PASS.** Clearly organized with labeled sections.

---

## Summary

| Section | Issues Found | Severity |
|---------|-------------|----------|
| Abstract | Missing quantitative result | **Medium** |
| Introduction | All checks pass | -- |
| Related Work | GraDe/SPADA redundancy with intro | **Minor** |
| Method | Key details deferred to appendix | **Minor** |
| Conclusion | No limitations/future work mentioned | **Medium** |
| Limitations | All checks pass | -- |
| Appendix | DAG justification hidden in appendix | **Minor** |

**Overall: 4 failures (1 clear FAIL, 3 minor FAILs) out of 37 checklist items.** The paper is structurally strong overall.

### Priority Fixes

1. **Abstract:** Add at least one concrete quantitative result.
2. **Conclusion:** Add 1-2 sentences on limitations or future work.
3. **Method:** Add brief inline mention of association measures and DAG justification.
4. **Introduction/Related Work:** De-duplicate GraDe/SPADA descriptions.
