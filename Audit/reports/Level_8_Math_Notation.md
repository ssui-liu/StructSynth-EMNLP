# Level 8 Audit: Mathematical Notation & Equations

**Paper:** StructSynth  
**Files audited:** `method.tex`, `experiments.tex`, `appendix.tex`, `introduction.tex`  
**Date:** 2026-05-22

---

## 8.1 Notation Consistency

### 8.1.1 Notation Inventory

| Symbol | Meaning | Introduced in | Convention |
|--------|---------|---------------|------------|
| `\mathcal{D}_{train}` | Training dataset | method.tex L4 | Calligraphic set -- OK |
| `\mathcal{D}_{synth}` | Synthetic dataset | method.tex L4 | Calligraphic set -- OK |
| `\mathcal{D}_{few_shot}` | Few-shot subset | method.tex L21 | Calligraphic set -- OK |
| `\mathcal{D}_{test}` | Test dataset | experiments.tex L11 | Calligraphic set -- OK |
| `\mathcal{D}_{aug}` | Augmented dataset | experiments.tex L11 | Calligraphic set -- OK |
| `\mathcal{D}_{real}` | All real data (train+test) | appendix.tex L247 | Calligraphic set -- OK |
| `\mathbf{X}_{train}` | Feature matrix | method.tex L4 | Uppercase bold matrix -- OK |
| `\mathbf{A}` | Attribute set | method.tex L4 | Uppercase bold -- see Issue 1 |
| `n` | Number of training instances | method.tex L4 | Lowercase italic scalar -- OK |
| `K` | Number of attributes | method.tex L4 | Uppercase italic scalar -- OK |
| `s` | Number of synthetic samples | experiments.tex L15 | Lowercase italic scalar -- OK |
| `f_{LLM}` | LLM-based generator function | method.tex L4 | Italic function -- OK |
| `G = (V, E)` | DAG (nodes, edges) | method.tex L12 | Italic uppercase -- OK |
| `V` | Node set of DAG | method.tex L12 | Italic uppercase -- see Issue 3 |
| `E` | Edge set of DAG | method.tex L12 | Italic uppercase -- OK |
| `A_i` | Individual attribute (node) | method.tex L29 | Italic uppercase -- OK |
| `\mathcal{S}(A_i)` | Association scores | method.tex L29 | Calligraphic -- OK |
| `\pi_{source}`, `\pi_{generate}`, etc. | Prompt templates | method.tex L23,32,38 | Greek italic -- OK |
| `P_i` | Proposed successors set | method.tex L32 | Italic uppercase -- OK |
| `\Psi` | Set of all cycles | method.tex L38 | Greek uppercase -- OK |
| `\psi` | Individual cycle | method.tex L38 | Greek lowercase -- OK |
| `G_t` | Graph at iteration t | method.tex L30 | Italic with subscript -- OK |
| `\mathcal{L}` | Topological layers | method.tex L94 | Calligraphic -- OK |
| `L_i` | Layer i | method.tex L94 | Italic uppercase -- OK |
| `\Gamma^{-}(L_i)` | Parent nodes of layer | method.tex L94 | Greek uppercase -- OK |
| `G_i` | Dependency subgraph for layer | method.tex L94 | Italic uppercase -- OK |
| `\tilde{\mathbf{x}}_j` | Synthetic data point (vector) | method.tex L90 | Bold lowercase tilde -- OK |
| `A_{iso}` | Isolated attributes | method.tex L103 | Italic uppercase -- OK |
| `r` | Pearson's correlation coefficient | appendix.tex L55-58 | Lowercase italic -- see Issue 2 |
| `\eta` | Correlation ratio | appendix.tex L62-64 | Greek lowercase -- OK |
| `V_{corr}` | Bias-corrected Cramer's V | appendix.tex L80-81 | Italic uppercase -- see Issue 3 |
| `\phi^2_{corr}` | Bias-corrected phi-squared | appendix.tex L72-73 | Greek lowercase -- OK |
| `r` (rows), `k` (columns) | Contingency table dimensions | appendix.tex L69 | Lowercase italic -- see Issue 2 |
| `\rho` | Pearson correlation (in fidelity) | appendix.tex L268-270 | Greek lowercase -- see Issue 4 |
| `\Delta(C_i, C_j)` | Pairwise difference score | appendix.tex L265 | Greek uppercase -- see Issue 5 |
| `\Delta` | Privacy risk deviation | experiments.tex L166 | Greek uppercase -- see Issue 5 |
| `d(x_i, x_j)` | Distance function | appendix.tex L249-251 | Lowercase italic -- OK |
| `NN(\tilde{x})` | Nearest neighbor function | appendix.tex L253-255 | Upright uppercase -- OK |
| `C_i, C_j` | Column pair | appendix.tex L265 | Italic uppercase -- OK |
| `\mathbb{I}` | Indicator function | appendix.tex L251 | Blackboard bold -- OK |
| `\mathbb{R}` | Real numbers | method.tex L29 | Blackboard bold -- OK |

### 8.1.2 Issues Found

**Issue 1 (Medium): Bold for attribute set `\mathbf{A}` is inconsistent with its use as a set.**
- In method.tex L4 and L107, the attribute set is written as `\mathbf{A}` (bold, typically reserved for matrices/vectors).
- In appendix.tex Algorithm 1 (L95, L96, L147, L154), it appears as plain `A` (non-bold), inconsistent with the method section.
- As a *set* of attributes, calligraphic `\mathcal{A}` would be more conventional, or at least the bold/non-bold usage should be consistent across method and algorithm.

**Issue 2 (Medium): Symbol `r` used for three different meanings.**
- In appendix.tex L55-58: `r` = Pearson's correlation coefficient.
- In appendix.tex L69: `r` = number of rows in a contingency table.
- In appendix.tex L114: `r_{ij}` = rationale for a proposed edge.
- The Pearson `r` and contingency table row count `r` co-occur in the same section (Statistical Association Measures). Although they appear in separate subsections, the potential for confusion is real since `r` appears in the Cramer's V formula alongside `r_{corr}`, and Pearson's `r` was just defined a few paragraphs earlier.

**Issue 3 (Minor): Symbol `V` used for two different meanings.**
- In method.tex L12 and throughout: `V` = node set of the DAG.
- In appendix.tex L80-81: `V_{corr}` = bias-corrected Cramer's V statistic.
- These two uses are in different sections (method vs. appendix association measures), but a reader encountering `V_{corr}` after the DAG notation may momentarily confuse it with a corrected node set. This is a standard statistical notation, so the risk is low but worth noting.

**Issue 4 (Minor): Pearson correlation denoted `r` in one place and `\rho` in another.**
- In appendix.tex L55-58 (Pearson's R subsection), Pearson's correlation is `r`.
- In appendix.tex L268-270 (Statistical Fidelity), Pearson correlation coefficients are denoted `\rho`.
- These are in different subsections and contexts (formula definition vs. metric definition), but using different symbols for the same statistical quantity is mildly confusing.

**Issue 5 (Minor): Symbol `\Delta` used for two different meanings.**
- In experiments.tex L166: `\Delta = |PrivacyRisk - 0.5|` (privacy risk deviation).
- In appendix.tex L265: `\Delta(C_i, C_j)` (pairwise fidelity difference score).
- In appendix.tex L436-438 (token usage table): `\Delta` = difference in token counts.
- Three distinct meanings. The first two are the most problematic since both are formal metric definitions.

**Issue 6 (Medium): `\mathtt{}` vs. `\text{}` subscript inconsistency for dataset labels.**
- In method.tex and experiments.tex (main body), dataset subscripts consistently use `\mathtt{}`: `\mathcal{D}_{\mathtt{train}}`, `\mathcal{D}_{\mathtt{synth}}`, `\mathcal{D}_{\mathtt{aug}}`, `\mathcal{D}_{\mathtt{test}}`.
- In appendix.tex Sections 5 (Metrics, L239-289), these switch to `\text{}`: `\mathcal{D}_{\text{train}}`, `\mathcal{D}_{\text{synth}}`, `\mathcal{D}_{\text{aug}}`, `\mathcal{D}_{\text{test}}`, `\mathcal{D}_{\text{real}}`.
- The same symbols render in different fonts between the main paper and appendix. This should be unified.

**Issue 7 (Medium): Bold `\tilde{\mathbf{x}}_j` in method vs. non-bold `\tilde{x}_j` in algorithm.**
- In method.tex (L90, L95, L97, L99, L103, L105), synthetic data points are consistently bold: `\tilde{\mathbf{x}}_j`, `\tilde{\mathbf{x}}_{j,L_i}`, etc.
- In appendix.tex Algorithm 1 (L139, L142, L143, L148, L151), these same quantities appear without bold: `\tilde{x}_{j,V}`, `\tilde{x}_{j,L_i}`, etc.
- Since these represent row vectors (multiple feature values), the bold notation from the method section is correct and should be used consistently in the algorithm.

**Issue 8 (Medium): Bold `\mathbf{X}_{train}` in method vs. non-bold `X_{train}` in algorithm.**
- In method.tex L4 and L107: `\mathbf{X}_{\mathtt{train}}`, `\mathbf{X}_{\mathtt{synth}}` (bold, correct for matrices).
- In appendix.tex Algorithm 1 (L95, L96, L136, L152, L154): `X_{\mathtt{train}}`, `X_{\mathtt{synth}}` (non-bold).
- The data matrix should be bold in both locations.

---

## 8.2 Equation Formatting

### 8.2.1 Inline vs. Display Math

All major formulas (Eq. 1-5 in method, all equations in appendix) use display math (`\begin{equation}` or `\begin{align}`). Simple variable references use inline math. **No issues found.**

### 8.2.2 Column Overflow

- method.tex Eq. 4 (L96-98): moderately long but uses `\!` spacing to compress. Likely fits.
- method.tex Eq. 5 (L104-106): uses aggressive `\!=\!` spacing to compress. Likely fits but is on the edge.
- appendix.tex L270: single-column equation with `|\rho(...)- \rho(...)|`; may be tight in single-column appendix format.
- **No confirmed overflows**, but Eq. 5 in method.tex should be verified in compiled output.

### 8.2.3 Equation Punctuation

**Issue 9 (Major): 12 out of 17 display equations lack terminal punctuation.**

Equations in **method.tex** -- all 5 end with periods. **Correct.**

Equations in **appendix.tex** -- issues:

| Location | Equation | Punctuation |
|----------|----------|-------------|
| L56-58 (Pearson's r) | `r = ...` | **Missing** |
| L63-65 (Correlation ratio) | `\eta = ...` | **Missing** |
| L72-74 (phi-squared) | `\phi^2_{corr} = ...` | **Missing** |
| L76-78 (corrected dimensions) | `r_{corr} = ..., k_{corr} = ...` | **Missing** |
| L80-82 (Cramer's V) | `V_{corr} = ...` | **Missing** |
| L240-242 (D_aug) | `\mathcal{D}_{aug} = ...` | **Missing** |
| L250-252 (distance) | `d(x_i, x_j) = ...` | **Missing** |
| L254-256 (NN) | `NN(\tilde{x}) = ...` | **Missing** |
| L258-260 (PrivacyRisk) | `PrivacyRisk = ...` | **Missing** |
| L269-271 (Delta num-num) | `\Delta(C_i, C_j) = ...` | **Missing** |
| L274-278 (Delta cat-cat, align) | TVD formula | **Missing** |
| L281-283 (Delta num-cat) | `\Delta(C_i, C_j) = ...` | **Missing** |
| L287-289 (StatisticalFidelity) | `StatisticalFidelity = ...` | **Missing** |

All 12+ appendix display equations lack punctuation (period or comma). The 5 method equations are all correct.

### 8.2.4 Multi-line Equation Alignment

- appendix.tex L274-278 uses `\begin{align}` with alignment at `&` before `P_{\text{real}}` and `P_{\text{synth}}`. This is acceptable since the `=` is on the first line before the line break. **Acceptable.**

### 8.2.5 Math Operators

- `\max` used correctly in appendix.tex L73 and L81.
- `\min` used correctly in appendix.tex L81.
- `\arg\min` used correctly in appendix.tex L255 (via `\underset{...}{\arg\min}`).
- No instances of bare italic `max`, `min`, `log`, `argmin` found. **No issues.**

### 8.2.6 Text in Math Mode

- `\text{}` is used correctly throughout for textual subscripts: `\text{corr}`, `\text{numerical}`, `\text{categorical}`, `\text{real}`, `\text{synth}`, `\text{PrivacyRisk}`, `\text{StatisticalFidelity}`.
- `\mathtt{}` is used for code-like identifiers: `\mathtt{train}`, `\mathtt{synth}`, `\mathtt{LLM}`, `\mathtt{source}`, etc.
- `\mathrm{}` used for `\mathrm{Age}`, `\mathrm{Income}` in appendix.tex L40. **Correct.**
- **No bare italic text in math mode found.**

---

## 8.3 Equation Referencing

### 8.3.1 Numbered Equations

**Total display equations:** 17 numbered equations (5 in method.tex using `equation`, 12 in appendix.tex using `equation`, plus 1 `align` environment).

**Equation labels:** Zero. No `\label{eq:...}` found in any file.

**Issue 10 (Major): None of the 17 numbered equations have labels, and none are referenced by number anywhere in the text.**

All equations use the `equation` environment (which auto-numbers them), but no `\label` is attached and no `\ref{eq:...}` or `\eqref{...}` appears anywhere in the paper. The equations are instead referenced by prose description (e.g., "The graph is then updated:" followed by the equation). This means:

- Every numbered equation is unreferenced (wastes the equation number).
- If equations need to be cross-referenced in reviews or revisions, there is no mechanism to do so.

**Recommendation:** Either add `\label{eq:...}` to each equation and reference them by number, or switch to `equation*` (unnumbered) if cross-referencing is not needed. The current state -- numbered but unreferenced -- is the worst of both options.

### 8.3.2 Equation Reference Format

Not applicable -- no equation references exist in the paper. **No format consistency to check.**

---

## Summary of Issues

| # | Severity | Section | Description |
|---|----------|---------|-------------|
| 1 | Medium | 8.1 | `\mathbf{A}` (bold) in method vs. plain `A` in algorithm for attribute set |
| 2 | Medium | 8.1 | Symbol `r` used for Pearson correlation, contingency table rows, and edge rationale |
| 3 | Minor | 8.1 | Symbol `V` used for DAG node set and Cramer's V statistic |
| 4 | Minor | 8.1 | Pearson correlation denoted `r` in definition but `\rho` in fidelity metric |
| 5 | Minor | 8.1 | `\Delta` used for privacy deviation, fidelity score, and token difference |
| 6 | Medium | 8.1 | `\mathtt{}` subscripts in main text vs. `\text{}` subscripts in appendix for dataset identifiers |
| 7 | Medium | 8.1 | Bold `\tilde{\mathbf{x}}_j` in method vs. non-bold `\tilde{x}_j` in algorithm |
| 8 | Medium | 8.1 | Bold `\mathbf{X}_{train}` in method vs. non-bold `X_{train}` in algorithm |
| 9 | Major | 8.2 | 12 of 17 display equations (all in appendix) lack terminal punctuation |
| 10 | Major | 8.3 | All 17 equations are numbered but none have labels or are referenced by number |

**Overall Assessment:** The main-body equations (method.tex) are well-formatted with consistent punctuation. The primary concerns are: **(a)** the appendix equations uniformly lacking punctuation (Issue 9), **(b)** the complete absence of equation labels/references despite all equations being numbered (Issue 10), and **(c)** several notation inconsistencies between the method section and the appendix/algorithm -- most notably the bold vs. non-bold distinction for data matrices/vectors (Issues 7, 8) and the `\mathtt{}` vs. `\text{}` font mismatch for dataset subscripts (Issue 6).
