# Level 5: Grammar & Syntax Audit Report

**Paper:** StructSynth (EMNLP submission)
**Date:** 2026-05-22

---

## 5.1 Subject-Verb Agreement

### Issue 5.1.1 -- "data" consistency

The paper treats "data" as a mass (uncountable/singular) noun throughout, which is consistent and acceptable:

- abstract.tex: "Tabular data derives its value" (singular verb)
- method.tex: "synthetic tabular data generation" (uncountable)
- experiments.tex: "synthetic data along three axes" (uncountable)

**Verdict:** Consistent usage. No issue.

### Issue 5.1.2 -- Adjective misused as adverb (experiments.tex, Section 4.2.1)

**Quoted sentence:**
> "Standard DGMs and structure-aware models perform notably weaker, as implicit distribution learning and data-driven graph discovery are unreliable when training samples are scarce ($n=100$)."

**Error:** "perform notably weaker" is grammatically incorrect. "Perform" is a verb and requires an adverb modifier, but "weaker" is a comparative adjective.

**Correction:**
> "Standard DGMs and structure-aware models **are notably weaker**, as implicit distribution learning and data-driven graph discovery are unreliable when training samples are scarce ($n=100$)."

### Issue 5.1.3 -- Collective noun check

No issues found with collective nouns. Phrases like "the union of all removed edges" correctly use singular verbs ("forms"). Compound subjects like "edges and nodes" correctly take plural verbs ("are extracted").

---

## 5.2 Tense Consistency

### Issue 5.2.1 -- Tense shift in Related Work (related_work.tex, paragraph "LLM-Assisted Dependency Discovery")

**Quoted sentence:**
> "Early work demonstrated that LLMs can accurately judge pairwise causal directions from variable semantics alone."

The surrounding sentences predominantly use present tense ("LLMs have been applied," "strategies reframe," "a complementary line integrates," "these methods target"). Within this present-tense paragraph, "demonstrated" shifts abruptly to simple past.

**Correction:**
> "Early work **demonstrates** that LLMs can accurately judge pairwise causal directions from variable semantics alone."

### Other tense checks

- Related Work "Tabular Synthesis" paragraph: consistent present tense ("capture," "address," "degrades"). No issue.
- Method section: consistent present tense ("constructs," "proceeds," "are partitioned"). No issue.
- Experiment results: consistent present tense ("achieves," "shows," "confirms," "outperforms"). No issue.

---

## 5.3 Article Usage (a/an/the)

### Issue 5.3.1 -- Missing article before "BFS" (method.tex, Section 3.1)

**Quoted sentence:**
> "The graph is constructed iteratively via BFS as described below."

**Error:** "BFS" here refers to a specific algorithmic procedure. When used as a noun denoting a process instance, it should carry an article or be rephrased.

**Correction:**
> "The graph is constructed iteratively via **a** BFS **traversal** as described below."

Or: "The graph is constructed iteratively **using** BFS as described below."

### Other article checks

- "A DAG" -- correct; "DAG" is pronounced /daeg/ (consonant), so "a" is right. Consistent throughout.
- "StructSynth" used without article as a proper name -- correct and consistent.
- No missing articles before countable singular nouns detected elsewhere.

---

## 5.4 Comma Usage

### Issue 5.4.1 -- Missing Oxford comma (experiments.tex, Section 4.1.1)

**Quoted sentence:**
> "These datasets cover a range of domains (e.g., social, medical, business) and downstream tasks including binary/multi-class classification and regression."

**Error:** The parenthetical list "social, medical, business" omits the serial comma before "business." The rest of the paper consistently uses the Oxford comma (e.g., "the generation order, conditioning context, and scope"; "healthcare, finance, and education").

**Correction:**
> "These datasets cover a range of domains (e.g., social, medical**,** and business) and downstream tasks..."

### Other comma checks

- Comma after introductory clauses: consistently applied throughout. No issue.
- No comma splices found anywhere.
- Non-restrictive clauses properly set off with commas throughout.

---

## 5.5 Common Syntax Errors

### Issue 5.5.1 -- Broken parallelism (introduction.tex)

**Quoted sentence:**
> "...the graph serves as an internal attention mask or a distribution prior rather than determining what to generate, in what order, and conditioned on which context."

**Error:** The three elements after "determining" should be parallel. The first two are interrogative noun clauses ("what to generate," "in what order"), but the third shifts to a participial phrase ("conditioned on which context"), breaking the parallel structure.

**Correction:**
> "...rather than determining what to generate, in what order, and **on which context to condition**."

Or: "...rather than determining what to generate, in what order, and **with which conditioning context**."

### Issue 5.5.2 -- Awkward gerund-passive construction (method.tex, Section 3.2)

**Quoted sentence:**
> "Constructing each synthetic data point $\tilde{\mathbf{x}}_j$ is performed in two sequential phases aligned with the underlying data structure."

**Error:** "Constructing... is performed" is redundant. The gerund already implies the action, so "is performed" creates awkward double agency.

**Correction:**
> "Each synthetic data point $\tilde{\mathbf{x}}_j$ is constructed in two sequential phases aligned with the underlying data structure."

Or: "**Construction of** each synthetic data point $\tilde{\mathbf{x}}_j$ **proceeds** in two sequential phases aligned with the underlying data structure."

### Issue 5.5.3 -- Missing conjunction in two-item list (conclusion.tex)

**Quoted sentence:**
> "Separating graph induction from data generation allows each stage to leverage complementary signals---LLM semantic priors and statistical association cues for structure discovery, the discovered topology for dependency-faithful synthesis."

**Error:** After the em-dash, two items elaborate "complementary signals," but the lack of a conjunction before the second item makes the structure unclear.

**Correction:**
> "...complementary signals---LLM semantic priors and statistical association cues for structure discovery, **and** the discovered topology for dependency-faithful synthesis."

### Other syntax checks

- No sentence fragments found (beyond the borderline case in 5.5.3).
- No run-on sentences found.
- No erroneous "Compared with X, and Y achieves..." patterns.
- No "Not only X but also Y" parallelism issues (construction not used).

### Issue 5.5.4 -- Naming inconsistency (experiments.tex, not strictly grammar)

The baselines section text says "TabDDPM" but Table 1 column header lists "DDPM." This naming inconsistency could confuse readers.

---

## Summary of All Issues Found

| ID | File | Category | Severity | Description |
|----|------|----------|----------|-------------|
| 5.1.2 | experiments.tex (Sec 4.2.1) | Adjective as adverb | **Medium** | "perform notably weaker" should be "are notably weaker" |
| 5.2.1 | related_work.tex | Tense consistency | **Low** | "demonstrated" amid present-tense paragraph |
| 5.3.1 | method.tex (Sec 3.1) | Missing article | **Low** | "via BFS" should be "via a BFS traversal" or "using BFS" |
| 5.4.1 | experiments.tex (Sec 4.1.1) | Missing Oxford comma | **Low** | "social, medical, business" missing serial comma |
| 5.5.1 | introduction.tex | Broken parallelism | **Medium** | "conditioned on which context" breaks parallel structure |
| 5.5.2 | method.tex (Sec 3.2) | Awkward construction | **Low** | "Constructing... is performed" is redundant |
| 5.5.3 | conclusion.tex | Missing conjunction | **Low** | Two-item list after em-dash lacks "and" |

### Overall Assessment

The paper is generally well-written with consistent grammar throughout. Seven issues were identified, of which two are **medium severity**:

1. **"perform notably weaker"** (5.1.2) -- a clear grammatical error where a comparative adjective is used where an adverb or predicate adjective is needed.
2. **Broken parallelism** (5.5.1) -- the third element in a three-part parallel list shifts syntactic form from the interrogative clauses used in the first two elements.

The remaining five issues are **low severity**: a tense shift in related work, a missing article, a missing Oxford comma, an awkward gerund-passive construction, and a missing conjunction in a two-item list.

No comma splices, run-on sentences, or subject-verb agreement errors were found. Article usage with "data," "DAG," and "StructSynth" is correct and consistent. The Oxford comma is used consistently except in one instance. Tense usage is consistent within sections with one minor exception.
