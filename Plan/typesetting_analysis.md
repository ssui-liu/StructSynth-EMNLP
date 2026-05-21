# StructSynth LaTeX Typesetting Analysis Report

> Analysis Date: 2026-05-18
> Target Venue: EMNLP 2026
> PDF Analyzed: `EMNLP26_StructSynth.pdf` (26 pages, compiled from `Latex-EMNLP/`)
> Source Directories: `Latex-EMNLP/` (EMNLP submission), root `/` (ACM/TKDD journal version)

---

## Executive Summary

The PDF was compiled from the `Latex-EMNLP/` directory, which correctly uses the ACL review template. Cross-references between the main body and appendix are properly wired. The most critical issues are: **(1)** the main body exceeds EMNLP's typical 8-page limit by ~2.5 pages, **(2)** a table column header is visually truncated in the appendix, and **(3)** a table uses non-standard double horizontal rules. Below is the complete issue list with severity ratings, locations, and fix recommendations.

### Fixed Issues (2026-05-18)
- **Table width overflow** (Tables 1, 2, Dataset table, Token Usage table): Applied `\resizebox{\textwidth}{!}{...}` wrapper and removed vertical `|` rules from column specs in `Latex-EMNLP/sections/method.tex`, `experiments.tex`, and `appendix.tex`.
- **Table 2 double rule**: Changed `\bottomrule\toprule` to `\midrule\midrule` in `experiments.tex`.

---

## Issue Index

| # | Severity | Category | Short Description | Location (EMNLP) |
|---|----------|----------|-------------------|-------------------|
| 1 | CRITICAL | Page Limit | Main body ~10.5 pages, exceeds 8-page limit | Overall structure |
| 2 | HIGH | Table Formatting | Table 2: `\bottomrule` + `\toprule` double rule | `experiments.tex:64-65` |
| 3 | HIGH | Table Overflow | Table 4: "Pre-LLM Knowledge Cutoff" header truncated | `appendix.tex` (dataset table) |
| 4 | HIGH | Table Placement | Table 1 (performance) defined inside `method.tex` | `method.tex:81-121` |
| 5 | MEDIUM | Figure Naming | `shd_comparison_acm.pdf` contains "acm" in filename | `experiments.tex:104` |
| 6 | MEDIUM | Ablation Table Style | Table 3 uses `\hline` instead of `booktabs` rules | `experiments.tex:125,127-129,134,138` |
| 7 | MEDIUM | Root Version Sync | Root `main.tex` uses ACM `acmart` class, not ACL | `(root) main.tex:16` |
| 8 | LOW | Email Typo | Author email `ssui.liu1022` may be typo for `siliu.1022` | `(root) main.tex:113` |
| 9 | LOW | Acknowledgments | Acknowledgments section is empty/commented | `Latex-EMNLP/main.tex:128-129` |
| 10 | LOW | Commented Code | Commented-out paragraph block in `experiments.tex` | `experiments.tex:148` |

---

## Detailed Analysis

### Issue 1: Main Body Exceeds EMNLP Page Limit [CRITICAL]

**Observation (from PDF):**
The main body (Abstract through end of Conclusion) spans approximately pages 1-10.5. EMNLP typically allows 8 pages for the main content (excluding references and appendix). The paper is ~2.5 pages over.

**Page breakdown from PDF:**
| Pages | Content |
|-------|---------|
| 1-2 | Title, Abstract, Introduction |
| 3 | Related Work (Section 2) |
| 4-6 | Methodology (Section 3), incl. Figure 2 |
| 6-9 | Experiments (Section 4), incl. Tables 1-3, Figures 3-5 |
| 10-11 | Experiments continued, Conclusion (Section 5), Limitations |
| 11-13 | References |
| 14-26 | Appendix (A-I) |

**Root cause:** The experiments section is very dense, containing:
- 3 large tables (performance, privacy/fidelity, ablation)
- 3 figures (SHD, influence_n, llm_compare)
- 7 subsections of analysis text

**Fix recommendations (choose combination):**
1. Move Table 2 (Privacy/Fidelity, ~1 page) to appendix, keep summary in text
2. Move Figure 3 (SHD comparison) to appendix, summarize key numbers inline
3. Condense "Influence of Training Sample Size" section (Section 4.5) -- move Figure 4 to appendix
4. Merge "Influence of Different Language Models" (Section 4.6) into a shorter paragraph referencing appendix
5. Remove the "DDPM" baseline row (DDPM performs very poorly) to shrink tables

**Priority:** Must be resolved before submission.

---

### Issue 2: Table 2 Double Horizontal Rule [HIGH]

**File:** `Latex-EMNLP/sections/experiments.tex`, lines 64-65

**Problem:** The table separating Privacy Preservation and Statistical Fidelity results uses:
```latex
\bottomrule
\toprule
```
This creates a visually jarring double thick rule in the middle of the table (visible on PDF page 8). In `booktabs` convention, `\bottomrule` and `\toprule` are only for table boundaries.

**Fix:**
```latex
% Replace lines 64-65:
\bottomrule
\toprule
% With:
\midrule
\midrule
```

Or, better yet, use a section header with a single rule:
```latex
\midrule
\addlinespace[3pt]
\multicolumn{10}{l}{{Results for \textbf{Statistical Fidelity}.} ...} \\
\midrule
```

---

### Issue 3: Table 4 Column Header Truncated [HIGH]

**Observation (PDF page 18):** The last column header of Table 4 (Summary of Dataset Characteristics) reads "Pre-LLM Knowledge Cu" -- the word "Cutoff" is truncated because the table is too wide for the column.

**File:** This table exists in `(root) sections/experiments.tex:8-24` and was moved to the appendix in the EMNLP version.

**Root cause:** The column header "Pre-LLM Knowledge Cutoff" is too long for the available column width in the `tabular` environment.

**Fix options:**
1. Abbreviate the header:
```latex
% Change:
\textbf{Pre-LLM Knowledge Cutoff}
% To:
\textbf{Pre-LLM}
```
And add a footnote explaining the column meaning.

2. Use `\makecell` for line breaking:
```latex
\textbf{\makecell{Pre-LLM\\Knowledge\\Cutoff}}
```

3. Use `tabular*` or `\resizebox` to fit the table:
```latex
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
...
\end{tabular}}
```

4. Rotate the header text:
```latex
\rotatebox{90}{\textbf{Pre-LLM Knowledge Cutoff}}
```

**Recommended:** Option 3 (`\resizebox`) for minimal visual disruption.

---

### Issue 4: Table 1 (Performance) Placed in method.tex [HIGH]

**File:** `(root) sections/method.tex:81-121`

**Problem:** Table 1 (`\label{tab:results_comparison_performance}`) contains experimental results but is defined inside `method.tex` rather than `experiments.tex`. This causes two problems:
1. Logical mismatch -- results data defined in methodology section code
2. LaTeX float placement becomes harder to control since the table definition is far from where it's referenced

**Note:** In the EMNLP version (`Latex-EMNLP/sections/method.tex`), the same table appears -- it was NOT moved to experiments. The EMNLP method.tex ends at line ~127 with the algorithm being moved to appendix, but the performance table is still in method.tex.

**Fix:** Move the `\begin{table*}...\end{table*}` block (lines 81-121 in root; check corresponding lines in EMNLP) to the beginning of experiments.tex, just before the "Main Results" subsection.

---

### Issue 5: Figure Filename Contains "acm" [MEDIUM]

**File:** `figures/shd_comparison_acm.pdf`
**Referenced in:** `experiments.tex:104`

**Problem:** The filename `shd_comparison_acm.pdf` contains "acm", suggesting it was generated for ACM format. This is:
1. Confusing for maintainability
2. May have ACM-specific styling (font sizes, colors) that doesn't match EMNLP aesthetic

**Fix:** Rename to `shd_comparison.pdf` and update the reference:
```latex
\includegraphics[width=\textwidth]{figures/shd_comparison.pdf}
```

---

### Issue 6: Ablation Table Uses `\hline` Instead of `booktabs` [MEDIUM]

**File:** `Latex-EMNLP/sections/experiments.tex:118-143`

**Problem:** Table 3 (Ablation Study) uses `\hline` for horizontal rules while all other tables use `booktabs` commands (`\toprule`, `\midrule`, `\bottomrule`). This creates an inconsistent visual style across tables.

**Current:**
```latex
\hline
\multicolumn{2}{c|}{\textbf{Method}} & ...
\hline
```

**Fix:**
```latex
\toprule
\multicolumn{2}{c}{\textbf{Method}} & ...   % also remove | from column spec
\midrule
```

Also update the column specification from `ll|ccc` to `ll ccc` to remove vertical rules, matching the `booktabs` convention used in Tables 1 and 2.

---

### Issue 7: Root `main.tex` Uses Wrong Document Class [MEDIUM]

**File:** `(root) main.tex:16`

**Problem:** The root-level `main.tex` uses:
```latex
\documentclass[acmsmall]{acmart}
```
with ACM metadata (TKDD journal, lines 91-101), while the target venue is EMNLP. This file is the ACM/TKDD journal version, separate from the EMNLP submission.

**Impact:** Low for EMNLP submission (the `Latex-EMNLP/` version is correct), but risks confusion if collaborators edit the wrong `main.tex`.

**Fix:** Add a clear comment at the top of both files:
```latex
% ROOT main.tex:
%% WARNING: This is the TKDD journal version. For EMNLP submission, use Latex-EMNLP/main.tex

% EMNLP main.tex:
%% This is the EMNLP 2026 submission version (review format)
```

---

### Issue 8: Author Email Potential Typo [LOW]

**File:** `(root) main.tex:113`

**Problem:** The first author email is `ssui.liu1022@gmail.com`. The actual email may be `siliu.1022@gmail.com` (based on the user profile context). This could be intentional (using a different email) or a typo.

**Fix:** Verify and correct if needed:
```latex
\email{siliu.1022@gmail.com}   % or confirm ssui is correct
```

---

### Issue 9: Empty Acknowledgments Section [LOW]

**File:** `Latex-EMNLP/main.tex:128-129`

**Problem:** The acknowledgments section is commented out with a TODO:
```latex
% \section*{Acknowledgments}
% TODO: Add acknowledgments in the camera-ready version.
```

**Impact:** None for review (anonymous submission should not have acknowledgments). But ensure this is uncommented and filled for camera-ready.

**Fix:** No action needed for review submission. Add to camera-ready checklist.

---

### Issue 10: Commented-Out Code Block [LOW]

**File:** `Latex-EMNLP/sections/experiments.tex:148`

**Problem:** A large commented-out paragraph remains in the source:
```latex
% The results, summarized in Table \ref{tab:ablation_study}, confirm that ...
```

**Impact:** No visual effect, but clutters source code.

**Fix:** Remove the commented block.

---

## Additional Observations (Non-Issues, Verified OK)

| Item | Status | Notes |
|------|--------|-------|
| Cross-references (main body <-> appendix) | OK | All `\ref{}` and `\label{}` pairs verified in EMNLP version |
| Figure widths in EMNLP version | OK | Uses `\textwidth` in `figure*`, `\columnwidth` in `figure` |
| Line numbers (review mode) | OK | `\usepackage[review]{acl}` correctly enables line numbers |
| Citation format | OK | `acl_natbib.bst` applied automatically by `acl.sty` |
| `\hyphenpenalty=5000`, `\tolerance=2000` | OK | Aggressive but acceptable; may cause occasional wide spacing |
| `\textsf{StructSynth}` formatting | OK | Used consistently throughout all sections |
| Math notation (`\mathcal`, `\mathbf`, etc.) | OK | Consistent and correct |
| Appendix section ordering | OK | Logical flow: A (background) -> B (DAG justification) -> C-E (details) -> F-I (analysis, prompts) |

---

## Root vs. EMNLP Version Differences Summary

The two versions share figures but have separate `sections/` directories with meaningful differences:

| Aspect | Root (ACM/TKDD) | EMNLP |
|--------|-----------------|-------|
| Document class | `acmart` (acmsmall) | `article` + `acl.sty` |
| Discussion section | Included in main body | Moved to Appendix H |
| "Why a DAG?" section | In main body (Section 3.2) | Moved to Appendix B |
| Statistical Association Measures | In main body (Section 3.5) | Moved to Appendix C |
| Algorithm pseudocode | In main body | Moved to Appendix D |
| Dataset table (Table 4) | In experiments section | Moved to appendix |
| Hyperparameter table (Table 5) | In experiments section | Moved to appendix |
| Evaluation metric formulas | Inline in experiments | Moved to Appendix E.4 |
| Section order | ..., Discussion, Limitations, Conclusion | ..., Conclusion, Limitations |
| Token usage table | In experiments section | Moved to Appendix G |

**Key concern:** When editing shared content (e.g., figure files, references.bib), changes affect both versions. But section-specific text edits must be made in the correct `sections/` directory.

---

## Priority Action Plan

### Before Submission (Must Do)
1. **Reduce main body to 8 pages** -- see Issue 1 recommendations
2. **Fix Table 2 double rule** -- simple `\bottomrule\toprule` -> `\midrule\midrule` change
3. **Fix Table 4 header truncation** -- use `\resizebox` or abbreviate header

### Polish (Should Do)
4. Move Table 1 from `method.tex` to `experiments.tex`
5. Make Table 3 (ablation) use `booktabs` style consistently
6. Rename `shd_comparison_acm.pdf` -> `shd_comparison.pdf`
7. Clean up commented-out code blocks

### Camera-Ready Checklist
8. Fill in acknowledgments section
9. Verify author email addresses
10. Remove `[review]` option from `\usepackage[review]{acl}`
11. Remove line numbers by switching from review to final mode
