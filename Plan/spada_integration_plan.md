# Plan: 将 SPADA 引用正式纳入论文

## Context

SPADA-NF 已作为 baseline 出现在三张实验表格中（downstream performance, privacy, fidelity），并在 §5 Discussion 中被简要提及。但目前 **缺少正式引用**（bib 条目和 `\cite{}`），也未在 Related Work 或 Appendix 中作为方法加以介绍。需要补齐引用并在关键位置做克制的文字整合。

## BibTeX 条目

```bibtex
@inproceedings{yang2025doubling,
  title={Doubling Your Data in Minutes: Ultra-fast Tabular Data Generation via LLM-Induced Dependency Graphs},
  author={Yang, Shuo and Zhang, Zheyu and Prenkaj, Bardh and Kasneci, Gjergji},
  booktitle={Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing},
  pages={10337--10358},
  year={2025},
  publisher={Association for Computational Linguistics}
}
```

## 修改计划（共 4 处，均为小幅增补）

### 1. `references.bib` — 添加 bib 条目
- **用户要求不修改 bib 文件**，仅将上述条目记录在计划中供用户自行添加。

### 2. `Latex-EMNLP/sections/experiments.tex` Line 8 — Baselines 段落
**当前**：`...DECAF, and SPADA-NF; and 3)~...`
**改为**：`...DECAF, and SPADA-NF~\cite{yang2025doubling}; and 3)~...`

仅添加引用标记，不增加额外描述文字。

### 3. `Latex-EMNLP/sections/related_work.tex` Line 19 — LLM-Based Tabular Generation 段落末尾
在 GraDe 那句之后（当前段落最后一句），追加一句关于 SPADA 的描述：

**插入位置**：Line 19 末尾之后，Line 20 (`\paragraph{LLM-Assisted...}`) 之前

**插入内容**：
```
SPADA~\cite{yang2025doubling} further decouples the two stages by replacing LLM-based generation with lightweight statistical estimators (KDE, normalizing flows), greatly accelerating sampling but relying on sufficient data to fit reliable conditional distributions.
```

简洁点出：解耦 + 轻量生成器 + 速度优势 + 低数据局限，篇幅与 GraDe 那句匹配。

### 4. `Latex-EMNLP/sections/appendix.tex` — Extended Related Work → Structure-Aware 小节
在 Appendix 的 Structure-Aware Generative Methods 小节（Line 17）末尾追加一句：

**插入内容**：
```
More recently, SPADA~\cite{yang2025doubling} employs an LLM to annotate sparse feature dependencies as a directed graph, then synthesizes data by traversing the graph with kernel density estimation or conditional normalizing flows, bypassing LLM-based generation entirely to achieve substantial sampling speedups.
```

纯方法描述，不加评价，与 appendix 的综述风格一致。

## 不修改的位置

- **Introduction**：当前段落已隐含覆盖（"Structure-aware methods isolate graph learning as a prerequisite, yet rely on purely statistical algorithms"），无需显式提及 SPADA。
- **Experiments §5.2 Discussion**（Line 90）：当前已有"SPADA-NF attains strong fidelity at the cost of poor privacy"的分析，足够克制，无需扩展。
- **Ablation / Other sections**：无关，不触及。

## 验证
- 编译 LaTeX 确认无引用错误（需用户先将 bib 条目添加到 references.bib）
- 检查 Related Work 段落长度是否与其他方法描述一致
