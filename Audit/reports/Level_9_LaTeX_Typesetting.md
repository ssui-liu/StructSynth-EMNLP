# Level 9: LaTeX Typesetting & Formatting Audit Report

**Paper:** StructSynth (EMNLP submission)
**Date:** 2026-05-22

---

## 9.1 Spacing

### 9.1.1 Non-breaking spaces before `\ref{}`

**PASS** -- All cross-references use the correct `~` non-breaking space. Every instance of `Table~\ref`, `Figure~\ref`, `Section~\ref`, `Appendix~\ref`, and `Algorithm~\ref` is correct. No instances of `Eq. \ref` or `Eq.~\ref` exist (equations are not cross-referenced by number).

### 9.1.2 Manual spacing hacks

**MINOR / ACCEPTABLE**

`\vspace` usage:
- `appendix.tex:98` -- `\vspace{0.2cm}` inside Algorithm environment
- `appendix.tex:132` -- `\vspace{0.3cm}` inside Algorithm environment
- `appendix.tex` (lines 516, 536, 565, 572, 579, 586, and many more) -- `\vspace{\medskipamount}` inside tcolorbox prompt boxes

The algorithm vspace and tcolorbox vspace are all standard formatting in non-body environments. No problematic `\\[` manual spacing found.

`\hspace` usage limited to `\hspace{\algorithmicindent}` inside the Algorithm environment -- standard.

### 9.1.3 Double spaces in source

**PASS** -- No problematic double spaces in running text.

---

## 9.2 Hyphenation and Dashes

### 9.2.1 Hyphenation consistency

**PASS** -- All key compound terms are consistently hyphenated:
- `fine-tuning` / `fine-tunes` / `fine-tuned` -- hyphenated throughout
- `pre-training` / `pre-trained` -- hyphenated throughout
- `state-of-the-art` -- used consistently as adjective
- `low-data` -- consistent compound modifier
- `data-scarce` / `data scarcity` -- correctly hyphenated as modifier, unhyphenated as noun

### 9.2.2 En-dash usage for ranges

**PASS** -- All number ranges use `--` correctly: `42--51` (appendix.tex:183), `1.0--1.4` (experiments.tex:136), negative indicators `--1.6`, `--1.1`, `--4.4` (experiments.tex:136).

### 9.2.3 En-dash for compound names -- ISSUE FOUND

| Location | Text | Issue |
|----------|------|-------|
| `appendix.tex:26` | `Peter--Clark` | Correct |
| `experiments.tex:105` | `Peter--Clark` | Correct |
| **`appendix.tex:191`** | **`Peter-Clark`** | **Uses single hyphen instead of en-dash** |

**Fix needed:** `appendix.tex:191` -- Change `Peter-Clark` to `Peter--Clark`.

### 9.2.4 Em-dash usage

**PASS** -- Em-dashes (`---`) used consistently throughout for parenthetical asides. No confusion between `--` and `---`.

---

## 9.3 Consistent Formatting

### 9.3.1 Method/model name formatting -- ISSUES FOUND

**StructSynth:** The main body consistently uses `\textsf{StructSynth}`. However, the appendix extended discussion (appendix.tex) uses plain `StructSynth` (without `\textsf{}`) extensively:
- `appendix.tex:37, 92, 346, 362, 450, 454, 456, 458, 462, 466, 468, 472, 474, 476, 479, 481, 483`
- Also in table cells: `method.tex:80`, `experiments.tex:54, 75` (tables are less critical)

**CLLM:** Most of the paper uses plain `CLLM`. However, in the efficiency analysis section (appendix.tex), CLLM switches to `\textsc{CLLM}`:
- `appendix.tex:395, 397, 403, 413, 435`

**bnlearn:** Inconsistent formatting:
- `experiments.tex:159` -- `\texttt{bnlearn}` (correct, software package)
- `experiments.tex:4` -- plain `bnlearn` (inconsistent)
- `appendix.tex:346` -- plain `bnlearn` (inconsistent)

### 9.3.2 Dataset name formatting

**PASS** -- Dataset names (Adult, Anxiety, Compas, Salary, Obesity, Churn, Asia, Child, Insurance) are consistently in plain text throughout.

### 9.3.3 Metric name formatting

**PASS** -- AUC, SHD, $R^2$, Statistical Fidelity, Privacy Risk are consistently formatted.

---

## 9.4 Cross-references

### 9.4.1 Unresolved references

**PASS** -- No `??` patterns found. All `\ref{}` targets have corresponding `\label{}` definitions. Every referenced label is defined.

### 9.4.2 Label naming convention -- MINOR INCONSISTENCY

Appendix sections inconsistently use `sec:` vs `app:` prefixes. Some sections have dual labels on the same target:
- `appendix.tex:86-87` -- `\label{sec:algorithm}` and `\label{app:algorithm}` on same section
- `appendix.tex:49-50` -- `\label{sec:association_scores}` and `\label{app:association_scores}` on same section

Orphan labels (defined but never `\ref`-ed): `app:adult_graph`, `app:algorithm`, `app:detailed_experimental_setup`, `app:fidelity_metric`, `app:privacy_metric`, `app:structure_examples`, `app:structure_learning_background`, `box:textualization_examples`, `prompt:*` (5 labels), `sec:association_scores`, `sec:fidelity_discussion`, `sec:structure_discussion`, `sec:when_helps` -- 17 total. Some of these are used via `\hyperref[]` rather than `\ref{}`.

### 9.4.3 Cross-reference capitalization

**PASS** -- `Section~\ref{}`, `Table~\ref{}`, `Figure~\ref{}`, `Appendix~\ref{}`, `Algorithm~\ref{}` are all consistently capitalized.

---

## 9.5 Page Budget & Layout

### 9.5.1 Review mode

**PASS** -- `main.tex:18` correctly sets `\usepackage[review]{acl}`.

### 9.5.2 Font size changes

**PASS** -- All `\small` usage is within table/figure/box environments (appropriate). No `\footnotesize`, `\tiny`, `\scriptsize`, `\large`, or `\Large` anywhere. No font size changes in main running text.

### 9.5.3 Page break commands

**ACCEPTABLE**:
- `main.tex:140` -- `\newpage` before `\appendix` (standard practice)
- `appendix.tex:805` -- `\clearpage` at end of appendix (flushes floats)

### 9.5.4 `\setlength` modifications

**ACCEPTABLE** -- Both are scoped within table environments:
- `experiments.tex:114` -- `\setlength{\tabcolsep}{1mm}` (ablation table)
- `appendix.tex:359` -- `\setlength{\tabcolsep}{0.9mm}` (downstream sensitivity table)

### 9.5.5 Hyphenation/tolerance overrides

**NOTE**:
- `main.tex:69` -- `\hyphenpenalty = 5000`
- `main.tex:70` -- `\tolerance = 2000`

These global settings discourage hyphenation aggressively. Values are within reason but may cause underfull hbox warnings. Worth verifying in the compiled PDF.

---

## Summary of Issues Found

### Must Fix (Error)

| # | File:Line | Issue | Fix |
|---|-----------|-------|-----|
| 1 | `appendix.tex:191` | `Peter-Clark` uses single hyphen instead of en-dash | Change to `Peter--Clark` |

### Should Fix (Inconsistencies)

| # | File:Lines | Issue | Fix |
|---|------------|-------|-----|
| 2 | `appendix.tex:37,92,346,362,450,454,456,458,462,466,468,472,474,476,479,481,483` | `StructSynth` as plain text instead of `\textsf{StructSynth}` | Wrap in `\textsf{}` |
| 3 | `appendix.tex:395,397,403,413,435` | `\textsc{CLLM}` used only here; plain `CLLM` everywhere else | Unify to one format |
| 4 | `experiments.tex:4` and `appendix.tex:346` | `bnlearn` in plain text vs `\texttt{bnlearn}` in `experiments.tex:159` | Use `\texttt{bnlearn}` consistently |

### Cosmetic / Optional

| # | Location | Issue |
|---|----------|-------|
| 5 | `appendix.tex` (various) | Mixed `sec:` / `app:` label prefixes for appendix sections; some dual labels |
| 6 | `appendix.tex` (various) | 17 orphan labels (defined but not referenced) |
| 7 | `main.tex:69-70` | `\hyphenpenalty=5000`, `\tolerance=2000` -- verify no underfull hbox warnings in PDF |

### All Passing Items

- Non-breaking spaces before all `\ref{}` commands
- No double spaces in running text
- Consistent hyphenation of all compound terms
- Correct en/em-dash usage (except the one Peter-Clark instance)
- No unresolved references
- Consistent dataset and metric name formatting
- `\usepackage[review]{acl}` correctly set
- No font size changes in main running text
- Page breaks appropriately placed
- `\setlength` modifications properly scoped

**Overall Assessment:** The paper is in very good typesetting shape. There is 1 clear error (the `Peter-Clark` hyphen at appendix.tex:191), 3 formatting inconsistencies to address (StructSynth sans-serif in appendix, CLLM small-caps inconsistency, bnlearn texttt inconsistency), and a few optional cleanups.
