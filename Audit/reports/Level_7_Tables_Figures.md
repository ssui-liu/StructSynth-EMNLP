# Level 7 Audit Report: Tables & Figures

**Paper:** StructSynth (EMNLP submission)  
**Date:** 2026-05-22

---

## 7.1 Tables

### Inventory of Tables

| Label | File | Placement | Caption above? |
|---|---|---|---|
| `tab:results_comparison_performance` | `sections/method.tex:44` | `[ht]` | Yes (line 47, tabular at line 50) |
| `tab:results_comparison_merged` | `sections/experiments.tex:18` | `[ht]` | Yes (line 20, tabular at line 24) |
| `tab:ablation_study` | `sections/experiments.tex:109` | `[t!]` | Yes (line 113, tabular at line 115) |
| `tab:dataset_summary` | `sections/appendix.tex:161` | `[t]` | Yes (line 163, tabular at line 167) |
| `tab:hyperparameters` | `sections/appendix.tex:193` | `[t]` | Yes (line 195, tabular at line 197) |
| `tab:downstream_sensitivity` | `sections/appendix.tex:355` | `[h]` | Yes (line 358, tabular at line 360) |
| `tab:token_usage` | `sections/appendix.tex:401` | `[t]` | Yes (line 403, tabular at line 409) |

### 7.1.1 Every table referenced in text?

**PASS.** All seven table labels are referenced via `Table~\ref{}`.

### 7.1.2 Table captions self-contained?

**PASS.** All table captions provide sufficient context (metrics, notation conventions, task types).

### 7.1.3 Caption placed above the table?

**PASS.** In all seven tables, `\caption{}` appears before `\begin{tabular}`.

### 7.1.4 booktabs rules (no vertical lines)?

**FINDING (Medium).** Two tables use `\hline` and vertical column separator `|` instead of `booktabs` rules:

1. **`tab:ablation_study`** (`sections/experiments.tex:115`): Column spec `{ll|ccc}` with vertical line; uses `\hline` (lines 116, 118, 120, 125, 129).
2. **`tab:downstream_sensitivity`** (`sections/appendix.tex:360`): Column spec `{ll|ccc}` with vertical line; uses `\hline` (lines 361, 363, 369, 375, 381, 387).

All other five tables correctly use `\toprule`/`\midrule`/`\bottomrule` without vertical lines.

**Recommendation:** Replace `\hline` with booktabs rules and remove `|` from column specs to match the other tables and EMNLP style.

### 7.1.5 Best results bolded? Convention stated in caption?

**PASS** for the main results tables. Both `tab:results_comparison_performance` and `tab:results_comparison_merged` captions state "Best results are in **bold**; second-best are underlined." The `tab:downstream_sensitivity` caption also states "Best per cell in **bold**."

**Minor note:** The ablation table caption ("Ablation Study on Adult Datasets.") does not explicitly state the bold convention. Consider adding "Best in **bold**" for completeness.

### 7.1.6 Column headers clear?

**PASS.** All headers are self-explanatory. Dataset names include (C)/(R) task annotations.

### 7.1.7 Decimal alignment consistent within columns?

**PASS.** Consistent two-decimal-place formatting. Token usage table uses `siunitx` `S` columns.

### 7.1.8 Table overflow margins?

**PASS.** Wide tables use `\resizebox{\textwidth}{!}{...}`. Single-column tables use `\small` and reduced `\tabcolsep`.

---

## 7.2 Figures

### Inventory of Figures

| Label | File | Placement | Format | Caption below? |
|---|---|---|---|---|
| `fig:teaser` | `introduction.tex:4` | `[t]` | PNG | Yes |
| `fig:pipeline` | `related_work.tex:4` | `[t]` | PNG | Yes |
| `fig:shd` | `experiments.tex:93` | `[t!]` | PDF | Yes |
| `fig:influence_n` | `experiments.tex:141` | `[t!]` | PDF | Yes |
| `fig:llm_compare` | `experiments.tex:148` | `[h]` | PDF | Yes |
| `fig:structure` (with 3 subfigures) | `appendix.tex:301` | `[t!]` | PDF | Yes |
| `fig:structure_examples` | `appendix.tex:343` | `[t!]` | PNG | Yes |

### 7.2.1 Every figure referenced in text?

**PASS.** All 10 figure labels (including 3 subfigure labels) are referenced in the text.

### 7.2.2 Figure captions self-contained?

**PASS.**

### 7.2.3 Caption placed below the figure?

**PASS.** In all figures, `\includegraphics` appears before `\caption{}`.

### 7.2.4 Figures vector graphics (PDF) where possible?

**FINDING (Low).** Three figures use PNG raster format where vector PDF would be preferable:

1. `figures/intro2.png` (teaser/conceptual diagram)
2. `figures/pipeline.png` (method overview diagram)
3. `figures/collage_3x2.png` (graph structure comparison)

The remaining figures correctly use PDF: `shd_comparison_acm.pdf`, `vary_n_all.pdf`, `llm_compare.pdf`, and all three graph subfigures (`reference.pdf`, `llm.pdf`, `structsynth.pdf`).

**Recommendation:** Convert to PDF if vector sources are available.

### 7.2.5 Subfigures labeled (a), (b)?

**PASS.** `fig:structure` uses the `subcaption` package with three `\begin{subfigure}` environments, each with its own caption. Automatic (a), (b), (c) labeling is handled correctly.

### 7.2.6 Figure references use consistent format?

**PASS.** All references use `Figure~\ref{fig:...}` consistently. No abbreviated "Fig." forms appear in rendered text.

---

## 7.3 Cross-Reference Consistency

### 7.3.1 Missing non-breaking space (`~`)?

**PASS.** All table and figure references use `~` (non-breaking space). No instances of `Table \ref` or `Figure \ref` without `~` were found.

### 7.3.2 Label naming convention consistency?

**PASS.** All labels use consistent prefixes: `tab:` for tables, `fig:` for figures, `sec:`/`app:` for sections, `alg:` for algorithms.

### 7.3.3 Orphan or dangling references?

**PASS.** Every defined `tab:` and `fig:` label is referenced. Every `\ref{tab:...}` and `\ref{fig:...}` points to a defined label.

---

## 7.4 Placement

### 7.4.1 Float placement hints?

All floats use standard hints (`[t]`, `[t!]`, `[ht]`, or `[h]`).

### 7.4.2 Forced [H] placement?

**PASS.** No `[H]` placement is used anywhere.

**Minor note:** Two floats use `[h]` alone (`tab:downstream_sensitivity` at `appendix.tex:355` and `fig:llm_compare` at `experiments.tex:148`). Consider `[ht]` for more robust placement.

---

## Summary

### Issues Requiring Attention

| # | Severity | Checklist Item | Location | Description |
|---|---|---|---|---|
| 1 | **Medium** | 7.1.4 | `sections/experiments.tex:115`, `sections/appendix.tex:360` | Two tables (`tab:ablation_study`, `tab:downstream_sensitivity`) use `\hline` and vertical lines (`|` in column spec) instead of booktabs rules. Inconsistent with the other five tables and EMNLP style. |
| 2 | **Low** | 7.2.4 | `sections/introduction.tex`, `sections/related_work.tex`, `sections/appendix.tex` | Three figures (`intro2.png`, `pipeline.png`, `collage_3x2.png`) use PNG raster format; vector PDF is preferred for diagrams. |

### Minor Suggestions

| # | Item | Location | Description |
|---|---|---|---|
| 3 | 7.1.5 | `sections/experiments.tex:113` | Ablation table caption omits the bold convention statement present in other tables. |
| 4 | 7.4.1 | `sections/appendix.tex:355`, `sections/experiments.tex:148` | Two floats use `[h]` alone; `[ht]` would be more robust. |

### All Passing Items

7.1.1 (all tables referenced), 7.1.2 (captions self-contained), 7.1.3 (captions above), 7.1.5 (best bolded with convention stated), 7.1.6 (headers clear), 7.1.7 (decimal alignment consistent), 7.1.8 (no overflow), 7.2.1 (all figures referenced), 7.2.2 (captions self-contained), 7.2.3 (captions below), 7.2.5 (subfigures labeled), 7.2.6 (consistent format), 7.3.1 (non-breaking spaces), 7.3.2 (label conventions), 7.3.3 (no orphans/danglers), 7.4.2 (no forced [H]).
