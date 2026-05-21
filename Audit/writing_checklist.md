# StructSynth EMNLP Paper — Writing Audit Checklist

> Scope: pure writing quality (logic, rhetoric, grammar, LaTeX typesetting).
> Not covering: experimental correctness, math derivation validity, or novelty judgment.
>
> Usage: go through each level top-down; mark items `[x]` when verified, annotate issues inline.

---

## Level 0: Global Narrative & Story Arc

### 0.1 One-sentence message
- [ ] Can you state the paper's core contribution in one sentence without jargon?
- [ ] Does every section serve that one sentence? (If a section doesn't connect back, it's structural bloat.)

### 0.2 Narrative arc (Problem → Gap → Approach → Evidence → Impact)
- [ ] **Problem**: Is the real-world problem established in the first paragraph of the introduction?
- [ ] **Gap**: Is the specific research gap explicitly stated (not just implied)?
- [ ] **Approach**: Is the proposed method introduced as a natural response to the gap (not as an arbitrary design)?
- [ ] **Evidence**: Do experiments directly validate the claims made in the introduction?
- [ ] **Impact**: Does the conclusion circle back to the real-world problem, not just list numbers?

### 0.3 Claim–Evidence alignment
- [ ] List every claim made in the abstract and introduction. Does each have a corresponding experiment/analysis?
- [ ] Are there experiments whose purpose is never motivated in the introduction? (orphan experiments)
- [ ] Are there claims that are only supported by qualitative arguments but presented as if empirically validated?

### 0.4 Reader expectation management
- [ ] Does the reader know, by the end of the introduction, exactly what will be presented in each subsequent section?
- [ ] Are there any "surprises" in later sections that should have been foreshadowed earlier?

---

## Level 1: Section-Level Structure & Function

### 1.1 Abstract (`sections/abstract.tex`)
- [ ] Follows the **Background → Problem → Method → Results → Significance** arc (roughly one sentence each)?
- [ ] Contains at least one concrete quantitative result (e.g., "X% improvement over Y")?
- [ ] Avoids undefined acronyms or paper-specific notation?
- [ ] Stays within the EMNLP word limit (typically ~250 words for the abstract)?
- [ ] Does not contain citations?
- [ ] First sentence anchors the reader in a known domain, not a method description?

### 1.2 Introduction (`sections/introduction.tex`)
- [ ] **P1 (Hook)**: Opens with a broadly accessible motivation, not a technical definition?
- [ ] **Problem scope**: Clearly states what the paper addresses and what it does *not* address?
- [ ] **Gap statement**: Uses explicit language ("However, ...", "Despite ...", "A key limitation ...") to mark the gap?
- [ ] **Contribution list**: Contributions are listed (numbered or bulleted) and each is concrete and falsifiable?
- [ ] Each contribution corresponds to a specific section or experiment?
- [ ] No contribution is merely "we propose X" without stating what X achieves?
- [ ] **Flow**: Does the narrative move from broad → narrow → contributions without backtracking?
- [ ] Avoids the "laundry list" anti-pattern (listing prior work without synthesizing)?
- [ ] Introduces the method name (StructSynth) with a brief intuitive description before any formalism?

### 1.3 Related Work (`sections/related_work.tex`)
- [ ] Organized thematically (not chronologically or author-by-author)?
- [ ] Each paragraph/subsection ends with a positioning statement distinguishing this work?
- [ ] Covers the expected categories: (1) tabular data synthesis, (2) dependency/structure discovery, (3) low-data learning?
- [ ] Avoids straw-man descriptions of prior work?
- [ ] Avoids redundancy with the introduction (related work goes deeper; intro only surveys enough to motivate)?
- [ ] Recent work (2023-2025) is adequately represented?
- [ ] No "orphan citations" — every cited work is discussed, not just name-dropped?

### 1.4 Method (`sections/method.tex`)
- [ ] Opens with a high-level overview (pipeline figure reference, intuitive description) before diving into formalism?
- [ ] Notation is introduced before first use and consistent throughout?
- [ ] Each subsection corresponds to a clear, named component of the pipeline?
- [ ] Design choices are justified ("We use X because Y"), not just described?
- [ ] Reader can reconstruct the method from this section alone (reproducibility test)?
- [ ] Equations are numbered only if referenced later; unnumbered otherwise?
- [ ] Algorithm pseudocode (if present) matches the text description with no silent discrepancies?
- [ ] Transitions between subsections explain how components connect?

### 1.5 Experiments (`sections/experiments.tex`)
- [ ] **Setup** subsection covers: datasets, baselines, metrics, implementation details?
- [ ] Baselines are fairly described and include state-of-the-art methods?
- [ ] Each table/figure is referenced in the text and its key takeaway is stated explicitly?
- [ ] Results discussion separates observation ("X outperforms Y by Z%") from interpretation ("This suggests that...")?
- [ ] Ablation study isolates each component and connects back to method design choices?
- [ ] Statistical significance or variance is reported where appropriate?
- [ ] Negative or surprising results are discussed honestly, not swept under the rug?
- [ ] No result is presented without context (what does "85.3" mean if you don't know the baseline or human ceiling)?

### 1.6 Conclusion (`sections/conclusion.tex`)
- [ ] Summarizes contributions without copy-pasting the abstract?
- [ ] States limitations or future work (unless in a separate section)?
- [ ] Does not introduce new claims or results not covered in the body?
- [ ] Avoids over-generalization ("our method can solve all tabular data problems")?
- [ ] Ends on a forward-looking note, not just a summary?

### 1.7 Limitations (`sections/limitations.tex`)
- [ ] Identifies genuine limitations (not token gestures like "we only tested on English")?
- [ ] Limitations are specific and actionable, not vague?
- [ ] Acknowledges computational cost, dataset scope, or assumption constraints?
- [ ] Does not undermine the paper's contributions (frame as "scope" not "failure")?

### 1.8 Appendix (`sections/appendix.tex`)
- [ ] Contains supplementary details that would interrupt the main narrative?
- [ ] Every appendix item is referenced from the main text?
- [ ] No critical information is hidden in the appendix that a reviewer needs to evaluate the main claims?
- [ ] Prompt templates, hyperparameter tables, and additional results are clearly organized?

---

## Level 2: Paragraph-Level Coherence

### 2.1 Topic sentences
- [ ] Every paragraph begins with a sentence that states the paragraph's main point?
- [ ] A reader skimming only topic sentences can reconstruct the section's argument?

### 2.2 Paragraph unity
- [ ] Each paragraph makes exactly one point?
- [ ] No paragraph exceeds ~8-10 sentences (if it does, consider splitting)?
- [ ] No single-sentence paragraphs (except in rare rhetorical emphasis)?

### 2.3 Transitions
- [ ] Adjacent paragraphs are connected by logical connectives or bridging sentences?
- [ ] Transition words accurately reflect the logical relationship (contrast → "however"; cause → "therefore"; addition → "moreover")?
- [ ] No abrupt topic shifts without a transition?

### 2.4 Information flow (Given → New)
- [ ] Each sentence opens with known/given information and closes with new information?
- [ ] The reader is never required to hold too many new concepts simultaneously?
- [ ] Key terms are introduced before they are used in arguments?

### 2.5 Paragraph-level redundancy
- [ ] No two paragraphs make the same point in different words?
- [ ] If a concept is explained in the method section, the experiments section references it rather than re-explaining?

---

## Level 3: Sentence-Level Clarity & Style

### 3.1 Sentence length and complexity
- [ ] Average sentence length is 15–25 words?
- [ ] No sentence exceeds 40 words? (If it does, split or restructure.)
- [ ] Complex sentences (with multiple clauses) use parallelism and clear subordination?

### 3.2 Active vs. passive voice
- [ ] Active voice is used by default for clarity ("We propose X", not "X is proposed")?
- [ ] Passive is used only when the agent is unknown, irrelevant, or for stylistic variation?
- [ ] The paper does not flip between "we" and passive voice within the same paragraph?

### 3.3 Hedging
- [ ] Claims are appropriately hedged ("suggests", "indicates") vs. stated with certainty ("proves", "demonstrates")?
- [ ] No over-hedging that weakens clear empirical results ("Our method seems to possibly outperform...")?
- [ ] Hedging level matches evidence strength?

### 3.4 Specificity
- [ ] Vague phrases are replaced with specifics:
  - "significant improvement" → "7.3% improvement in F1"
  - "various datasets" → "five public benchmarks"
  - "recent work" → "Chen et al. (2024)"
- [ ] Quantitative claims always include numbers?

### 3.5 Conciseness
- [ ] No filler phrases: "It is worth noting that", "It should be mentioned that", "In order to", "Due to the fact that"?
- [ ] No redundant modifiers: "completely eliminate", "very unique", "highly novel"?
- [ ] No throat-clearing openings: "As we all know", "It is well known that"?
- [ ] Nominalizations are converted to verbs where possible: "make a comparison" → "compare"; "perform an analysis" → "analyze"?

### 3.6 Parallelism
- [ ] Items in lists (bulleted or inline) use parallel grammatical structure?
- [ ] Comparisons use parallel constructions: "X is faster than Y" not "X is faster than what Y achieves"?
- [ ] Contribution lists use consistent verb forms?

### 3.7 Ambiguity
- [ ] Every pronoun ("it", "this", "they", "which") has an unambiguous antecedent?
- [ ] "This" is never used alone at the start of a sentence — always "This approach", "This result"?
- [ ] No dangling modifiers ("Using our method, the accuracy improved" — who used the method?)?
- [ ] Comparatives are complete ("our method is better" → "better than what?")?

---

## Level 4: Word-Level Precision

### 4.1 Terminology consistency
- [ ] Key terms are used identically throughout (no switching between "dependency structure" / "dependence graph" / "structural dependencies" for the same concept)?
- [ ] Create a term glossary and verify each term is used consistently:
  - | Preferred Term | Variants to Avoid |
    |---|---|
    | (fill in) | (fill in) |

### 4.2 Academic register
- [ ] No informal language: "a lot of", "kind of", "pretty good", "get rid of"?
- [ ] No contractions: "don't", "can't", "it's" (as "it is")?
- [ ] No first-person singular "I" (use "we" throughout)?
- [ ] No colloquialisms or idioms that non-native speakers may not understand?

### 4.3 Commonly confused words
- [ ] "which" vs. "that" (restrictive vs. non-restrictive clauses)?
- [ ] "compare to" (analogy) vs. "compare with" (analysis)?
- [ ] "compose" vs. "comprise" (the whole comprises the parts)?
- [ ] "fewer" (countable) vs. "less" (uncountable)?
- [ ] "e.g." (examples) vs. "i.e." (clarification) — used correctly?
- [ ] "affect" (verb) vs. "effect" (noun)?
- [ ] "complementary" vs. "complimentary"?

### 4.4 Overused words
- [ ] Scan for overuse of: "leverage", "utilize", "novel", "significant", "robust", "paradigm", "state-of-the-art"?
- [ ] Vary vocabulary for repeated concepts (but not at the cost of clarity — see 4.1)?

### 4.5 Preposition accuracy
- [ ] "consist of" (not "consist in" for composition)?
- [ ] "depend on" (not "depend of")?
- [ ] "result in" (cause) vs. "result from" (effect)?
- [ ] "based on" (not "based off of")?

---

## Level 5: Grammar & Syntax

### 5.1 Subject-verb agreement
- [ ] Collective nouns: "the set of features *is*" (not "are")?
- [ ] "Data" treated consistently (singular or plural — either is fine, just be consistent)?
- [ ] "None of the methods *performs*" (formal) or "*perform*" (informal) — pick one?

### 5.2 Tense consistency
- [ ] Related work: past tense ("Chen et al. (2024) proposed...") or present tense ("Chen et al. (2024) propose...") — consistent within the section?
- [ ] Method description: present tense ("We compute the score...")?
- [ ] Experiment results: past tense ("Our method achieved...") or present tense ("Table 2 shows...") — consistent?
- [ ] No tense shifts within a paragraph?

### 5.3 Article usage (a/an/the)
- [ ] "The" for specific/previously introduced items; "a/an" for first mention or generic?
- [ ] No missing articles before countable singular nouns?
- [ ] Method names: "StructSynth" (no article) vs. "the StructSynth framework" (with article)?
- [ ] "A DAG" (not "an DAG") — article matches pronunciation, not spelling?

### 5.4 Comma usage
- [ ] Serial (Oxford) comma used consistently: "A, B, and C"?
- [ ] Comma after introductory clauses: "To address this, we..."?
- [ ] No comma splice (two independent clauses joined by only a comma)?
- [ ] Commas around non-restrictive clauses: "our method, which uses..., achieves..."?

### 5.5 Common syntax errors
- [ ] No sentence fragments (every sentence has subject + verb)?
- [ ] No run-on sentences?
- [ ] "Compared with X, Y achieves..." (not "Compared with X, and Y achieves...")?
- [ ] "Not only X but also Y" — both parts grammatically parallel?

---

## Level 6: Citations & References

### 6.1 Citation format
- [ ] `\citet` for textual citations: "Chen et al. (2024) show..."?
- [ ] `\citep` for parenthetical citations: "...as shown in prior work \citep{chen2024}"?
- [ ] No bare `\cite` commands (use `\citet` or `\citep` per ACL style)?
- [ ] No double parentheses: "(Smith et al. (2024))" → use `\citet` instead?

### 6.2 Citation placement
- [ ] Citations placed before periods, not after: "...as shown by Smith \citep{smith2024}." (period after closing brace)?
- [ ] Multiple citations in chronological order or alphabetical (be consistent)?
- [ ] No citation-only sentences: "This has been studied in \citep{a,b,c}." → Add context.

### 6.3 Reference completeness
- [ ] Every `\citep`/`\citet` resolves (no "?" in compiled PDF)?
- [ ] Every entry in `references.bib` is cited at least once (no orphan bib entries)?
- [ ] All references have complete metadata: authors, title, venue, year, pages?
- [ ] Venue names are consistent (not mixing "EMNLP" and "Proceedings of EMNLP")?
- [ ] arXiv preprints: if a published version exists, cite the published version?
- [ ] Author names in bib are consistent (no "Zhang, Y." in one entry and "Yongqi Zhang" in another)?

---

## Level 7: Tables & Figures

### 7.1 Tables
- [ ] Every table is referenced in the text with `Table~\ref{}`?
- [ ] Table captions are self-contained (reader can understand the table without reading the main text)?
- [ ] Caption is placed *above* the table (LaTeX/ACL convention)?
- [ ] Use `\toprule`, `\midrule`, `\bottomrule` (booktabs) — no vertical lines?
- [ ] Best results are bolded; second-best underlined (if this convention is used, state it in the caption)?
- [ ] Column headers are clear and include units where applicable?
- [ ] Decimal alignment: all numbers in a column have the same number of decimal places?
- [ ] Table does not overflow column/page margins?
- [ ] No table is split awkwardly across pages?

### 7.2 Figures
- [ ] Every figure is referenced in the text with `Figure~\ref{}`?
- [ ] Figure captions are self-contained?
- [ ] Caption is placed *below* the figure (LaTeX convention)?
- [ ] Figures are vector graphics (PDF) where possible, not rasterized (PNG/JPG)?
- [ ] Font size in figures is readable (at least 8pt after scaling)?
- [ ] Color is not the only distinguishing feature (consider colorblind readers)?
- [ ] Axis labels include units?
- [ ] Legends do not overlap data?
- [ ] All subfigures are labeled (a), (b), etc. and referenced individually where needed?

### 7.3 Placement
- [ ] Floats appear near their first mention in the text (use `[t]` or `[h]` placement)?
- [ ] No large gaps caused by float placement?
- [ ] Figures and tables are not all clustered at the end?

---

## Level 8: Mathematical Notation & Equations

### 8.1 Notation consistency
- [ ] Create a notation table and verify consistency:
  - Scalars: lowercase italic ($x$)
  - Vectors: lowercase bold ($\mathbf{x}$)
  - Matrices: uppercase bold ($\mathbf{X}$)
  - Sets: calligraphic ($\mathcal{X}$)
- [ ] Same symbol is never used for two different meanings?
- [ ] Notation introduced in the method section matches notation in the experiments?

### 8.2 Equation formatting
- [ ] Inline math for simple expressions; display math for important or complex equations?
- [ ] No equation overflows the column width?
- [ ] Equations end with appropriate punctuation (period, comma) as part of the sentence?
- [ ] Multi-line equations are aligned at `=` or other operators?
- [ ] Functions like `max`, `min`, `log`, `argmin` use `\operatorname{}` or `\max`, not italic?
- [ ] Text within math mode uses `\text{}` or `\mathrm{}`, not bare italic?

### 8.3 Equation referencing
- [ ] Equations are referenced as "Eq.~(\ref{})" or "Equation~(\ref{})" — consistent format?
- [ ] No equation is numbered but never referenced (remove the number)?
- [ ] No equation is referenced but unnumbered?

---

## Level 9: LaTeX Typesetting & Formatting

### 9.1 Spacing
- [ ] Non-breaking spaces before references: `Table~\ref{}`, `Figure~\ref{}`, `Eq.~(\ref{})`?
- [ ] No manual spacing hacks (`\vspace`, `\hspace`, `\\[..]`) unless absolutely necessary?
- [ ] No double spaces in source (compile to same output, but messy source)?
- [ ] `\,` used in large numbers if needed (e.g., $10{,}000$)?

### 9.2 Hyphenation and dashes
- [ ] Hyphen (-) for compound adjectives: "state-of-the-art", "low-data"?
- [ ] En-dash (--) for ranges: "pages 1--10", "2023--2024"?
- [ ] Em-dash (---) for parenthetical remarks (or use commas/parentheses instead)?
- [ ] No inconsistent hyphenation: "pre-training" vs. "pretraining" — pick one?

### 9.3 Consistent formatting
- [ ] Method names, dataset names, and model names formatted consistently (e.g., always `\textsc{StructSynth}` or always bold)?
- [ ] Metric names formatted consistently (e.g., F1, AUROC — always same casing)?
- [ ] Code/command names in `\texttt{}`?

### 9.4 Cross-references
- [ ] All `\ref{}` and `\label{}` pairs resolve (no "??" in PDF)?
- [ ] Labels follow a consistent scheme: `sec:`, `tab:`, `fig:`, `eq:`, `alg:`?
- [ ] Section references use `Section~\ref{}` (capitalized) at sentence start, `\S\ref{}` inline?

### 9.5 Page budget
- [ ] Main body fits within the EMNLP page limit (typically 8 pages for long, 4 for short)?
- [ ] No content is artificially compressed (tiny fonts, squeezed spacing) to fit?
- [ ] Appendix does not contain material that should be in the main body?

---

## Level 10: EMNLP / ACL Specific Requirements

### 10.1 Anonymization (for review submission)
- [ ] `\usepackage[review]{acl}` is set (enables line numbers and anonymization)?
- [ ] No self-citations that reveal identity ("In our prior work (Author, 2023)")?
- [ ] No identifying information in headers, footers, or acknowledgments?
- [ ] Supplementary material is also anonymized?
- [ ] No links to non-anonymous repositories, personal websites, or identifiable resources?

### 10.2 Ethics & reproducibility
- [ ] Limitations section is present and substantive?
- [ ] Ethics statement included if applicable (data privacy, bias, misuse potential)?
- [ ] Sufficient implementation details for reproducibility (or commitment to release code)?
- [ ] Hyperparameter settings documented?
- [ ] Computational cost (GPU hours, hardware) mentioned?

### 10.3 Responsible NLP checklist
- [ ] If EMNLP requires the Responsible NLP Research checklist, has it been completed?
- [ ] All "yes" answers in the checklist are supported by content in the paper?

---

## Audit Workflow

### Pass 1: Structure (Levels 0–1)
Read only section headings, topic sentences, and contribution lists. Verify the narrative arc and section functions.

### Pass 2: Coherence (Levels 2–3)
Read the full text paragraph by paragraph. Check transitions, topic sentences, and sentence clarity.

### Pass 3: Precision (Levels 4–5)
Slow read for terminology, grammar, and word choice. Use Ctrl+F for known problem patterns.

### Pass 4: Mechanics (Levels 6–9)
Compile the PDF and inspect: citations, tables, figures, equations, formatting.

### Pass 5: Compliance (Level 10)
Verify EMNLP-specific requirements against the call for papers.

### Recommended Ctrl+F Patterns
```
Filler:        "it is worth noting", "it should be mentioned", "it is important to note"
Vague:         "significant", "various", "several", "some", "many", "often"
Hedging:       "seems to", "appears to", "might", "could potentially"
Redundant:     "in order to", "due to the fact that", "for the purpose of"
Informal:      "a lot", "kind of", "pretty", "basically", "stuff", "things"
Overused:      "leverage", "utilize", "novel", "robust", "paradigm"
Ambiguous:     "This " (at sentence start — check for missing noun)
Citation:      "\cite{" (should be \citet or \citep)
Spacing:       "Table \ref" (missing ~), "Figure \ref" (missing ~)
```

---

*Last updated: 2026-05-22*
