# Level 7 Tables & Figures 独立审计报告

## 1. 标题与范围

本报告审计 `Latex-EMNLP` 论文在 Writing Checklist Level 7: Tables & Figures 上的完成度，依据 `Audit/writing_checklist.md:267-294` 的 7.1 表格、7.2 图、7.3 放置位置要求。审计对象包括 `Latex-EMNLP/main.tex`、`Latex-EMNLP/sections/*.tex` 与 `Latex-EMNLP/figures/**` 的本地文件元数据。未修改论文源文件。

说明：本机未提供 `latexmk` / `pdflatex`，因此未能进行最终 PDF 视觉页检；以下结论基于 LaTeX 源码、图像文件类型与浮动体位置的静态审计。

## 2. Verdict Summary

| 项目 | 结论 | 摘要 |
|---|---|---|
| 7.1 Tables | 部分通过 | 所有表都有文本引用，caption 基本放在表格上方，主结果表多处使用 booktabs；但至少两张表仍使用竖线和 `\hline`，部分 caption 过短，若干宽表依赖 `\resizebox` + `\small`，可读性有风险。 |
| 7.2 Figures | 部分通过 | 所有图均有引用，caption 放在图下方，核心曲线图多为 PDF；但 teaser/pipeline/拼接图仍是 PNG，若干 caption 只描述内容而未写关键结论，拼接多面板图缺少 LaTeX 子图标签与逐面板引用。 |
| 7.3 Placement | 未通过，需要重点修订 | 多个浮动体不在首次提及附近，甚至跨章节放置；`[h]` 与多张 `[t!]` 浮动体可能造成页面空隙或图表聚集。 |

## 3. Strengths

- 引用完整性较好：已检出的表格和图形标签均有文本引用，例如 `fig:teaser` 在 `Latex-EMNLP/sections/introduction.tex:17` 引用，`tab:results_comparison_merged` 在 `Latex-EMNLP/sections/experiments.tex:90` 引用，附录中的 `fig:structure_examples` 和 `tab:token_usage` 也分别在 `Latex-EMNLP/sections/appendix.tex:329`、`Latex-EMNLP/sections/appendix.tex:395` 引用。
- caption 位置总体符合 LaTeX/ACL 惯例：表格 caption 多在 `tabular` 之前，如 `Latex-EMNLP/sections/experiments.tex:20`、`Latex-EMNLP/sections/appendix.tex:403`；图 caption 位于 `\includegraphics` 之后，如 `Latex-EMNLP/sections/experiments.tex:95-97`、`Latex-EMNLP/sections/appendix.tex:345-347`。
- 主结果表 caption 解释了任务类型、单位、post-cutoff 标记以及 bold/underline 规则，较为自包含，例如 `Latex-EMNLP/sections/method.tex:47` 和 `Latex-EMNLP/sections/experiments.tex:20`。
- 多数核心曲线/图结构资源为 PDF 矢量格式，例如 `figures/shd_comparison_acm.pdf`、`figures/influence_n/vary_n_all.pdf`、`figures/llm_compare.pdf` 与三张 graph PDF。
- `siunitx` 已在 `Latex-EMNLP/main.tex:55-63` 配置，且 token usage 表使用 `S[table-format=+3.1]`（`Latex-EMNLP/sections/appendix.tex:409`），这是数字列对齐的好基础。

## 4. Issues 按严重程度排序

### 高：若干关键图表放置远离首次提及，影响读者阅读路径

- `fig:pipeline` 的浮动体写在 Related Works 开头（`Latex-EMNLP/sections/related_work.tex:4-9`），但首次正文引用在 Method 中（`Latex-EMNLP/sections/method.tex:6`）。这是方法框架图，却出现在 related work 源文件中，章节语义和首次提及均不匹配。
- `tab:results_comparison_performance` 写在 Method 中（`Latex-EMNLP/sections/method.tex:44-85`），首次引用却在 Experiments 主结果段（`Latex-EMNLP/sections/experiments.tex:84`）。主结果表提前跨章节出现，不符合“near first mention”。
- `fig:shd` 定义在 `Latex-EMNLP/sections/experiments.tex:93-98`，首次详细引用在 `Latex-EMNLP/sections/experiments.tex:161`；`fig:influence_n` 定义在 `Latex-EMNLP/sections/experiments.tex:141-146`，首次引用在 `Latex-EMNLP/sections/experiments.tex:166`；`fig:llm_compare` 定义在 `Latex-EMNLP/sections/experiments.tex:148-153`，首次引用在 `Latex-EMNLP/sections/experiments.tex:172`。这些图集中放在相关小节之前，容易导致浮动体堆叠。

### 高：部分表格违反 checklist 的 booktabs / 无竖线规范

- Ablation 表使用 `\begin{tabular}{ll|ccc}` 与多处 `\hline`（`Latex-EMNLP/sections/experiments.tex:115-129`），违反 `Audit/writing_checklist.md:273` 的 booktabs/no vertical lines 要求。
- Downstream sensitivity 表同样使用 `\begin{tabular}{ll|ccc}` 和多处 `\hline`（`Latex-EMNLP/sections/appendix.tex:360-388`）。该表位于附录但仍应与全文表格风格一致。

### 中：多个 caption 未明确陈述关键 takeaway，自包含性不稳定

- `tab:ablation_study` caption 仅为 “Ablation Study on Adult Datasets.”（`Latex-EMNLP/sections/experiments.tex:113`），没有说明 AUC/Fidelity/Privacy 的方向、单位、bold/underline 含义，也没有写出关键结论。
- `fig:llm_compare` caption 仅说明比较对象（`Latex-EMNLP/sections/experiments.tex:151`），未说明核心发现：StructSynth across LLMs consistently outperforms CLLM，或指出最大增益。
- `fig:structure` 的总 caption 仅为视觉分析标题（`Latex-EMNLP/sections/appendix.tex:323`），未直接说明三图对齐说明了 synthetic data preserving structure。
- `tab:dataset_summary` caption 过短（`Latex-EMNLP/sections/appendix.tex:163`），且表头 “Pre-LLM Knowledge Cutoff” 与勾/叉符号（`Latex-EMNLP/sections/appendix.tex:169-176`）缺少 caption 解释，读者可能不清楚勾号表示 pre-cutoff 还是 post-cutoff。

### 中：PNG 和拼接图影响矢量化、缩放清晰度与可编辑性

- `fig:teaser` 使用 `figures/intro2.png`（`Latex-EMNLP/sections/introduction.tex:6`），`fig:pipeline` 使用 `figures/pipeline.png`（`Latex-EMNLP/sections/related_work.tex:6`），`fig:structure_examples` 使用 `figures/collage_3x2.png`（`Latex-EMNLP/sections/appendix.tex:345`）。本地 `file` 输出显示三者均为 PNG，其中 pipeline 为 5840x3460、intro2 为 3516x3840、collage 为 2184x2391。若这些图含文字或线条，应优先导出 PDF/SVG-to-PDF。
- checklist 明确要求 “Figures are vector graphics (PDF) where possible”（`Audit/writing_checklist.md:284`）。目前核心曲线图做得较好，但框架图、teaser、多面板结构图仍有改进空间。

### 中：多面板图的子图标签与引用不一致

- Adult structural fidelity 图使用了 `subfigure`、子 caption 与子 label（`Latex-EMNLP/sections/appendix.tex:303-324`），且正文逐一引用 `fig:structure_llmcd`、`fig:structure_groundtruth`、`fig:structure_structsynth`（`Latex-EMNLP/sections/appendix.tex:299`），这一点符合要求。
- Asia 结构比较图却是单张 `collage_3x2.png`（`Latex-EMNLP/sections/appendix.tex:343-347`）。正文在 `Latex-EMNLP/sections/appendix.tex:333-339` 分别讨论 GraDe/GOGGLE/NoTears/FCI，但没有 `(a)`, `(b)` 等可引用子图标签，也无法在 LaTeX 中逐面板引用。

### 中：宽表和缩放策略可能牺牲可读性

- 主性能表与 privacy/fidelity 表均使用 `\resizebox{\textwidth}{!}` 加 `\small`（`Latex-EMNLP/sections/method.tex:48-50`，`Latex-EMNLP/sections/experiments.tex:22-24`）。这能避免溢出，但可能把字体压到 ACL 可读阈值附近。
- 数据集表也采用同样的缩放方式（`Latex-EMNLP/sections/appendix.tex:165-167`）。如果最终 PDF 中字体小于 8pt 或列距过紧，需要拆分列或压缩文字而不是整体缩放。
- `fig:llm_compare` 使用 `[h]`（`Latex-EMNLP/sections/experiments.tex:148`），在双栏 ACL 模板中可能造成局部空白或位置不稳定。

### 低：表格数字对齐和风格仍可进一步统一

- 多数手写表格使用普通 `c` 列而非 `siunitx` 的 `S` 列，如 `Latex-EMNLP/sections/method.tex:50`、`Latex-EMNLP/sections/experiments.tex:24`、`Latex-EMNLP/sections/experiments.tex:115`。虽然小数位大多一致，但 `\pm` 形式、百分比、rank 混排时不易精确对齐。
- Hyperparameter 表中存在连续 `\midrule`（`Latex-EMNLP/sections/appendix.tex:217-218`），视觉上可能显得比其他 booktabs 表更重。

## 5. Actionable Revision Suggestions

1. 将 `fig:pipeline` 的 figure 环境从 `related_work.tex` 移到 `method.tex` 中首次引用附近；将 `tab:results_comparison_performance` 从 `method.tex` 移到 `experiments.tex` 的 Downstream Model Performance 小节附近。
2. 把 `fig:shd`、`fig:influence_n`、`fig:llm_compare` 分别放到对应小节首次提及前后；优先使用 `[t]` 或 `[tb]`，谨慎使用 `[h]`。
3. 将 ablation 表和 downstream sensitivity 表改为 booktabs 风格：去掉 `|`，把 `\hline` 替换为 `\toprule`、`\midrule`、`\bottomrule`，必要时用 `\cmidrule` 分组。
4. 扩写短 caption，使其至少包含：指标含义/方向、单位、bold/underline 规则、核心结论。例如 ablation 表 caption 可说明 “StructSynth has the best AUC; Bayesian Sampler improves pairwise fidelity but hurts utility.”
5. 对 `intro2.png`、`pipeline.png`、`collage_3x2.png` 寻找源文件并导出 PDF；若只能保留 PNG，应在最终 PDF 中检查缩放后文字是否仍大于 8pt。
6. 将 `collage_3x2.png` 拆成 LaTeX `subfigure` 或在图内/源码中明确 `(a)`-`(f)` 标签，并在正文中引用关键面板，而不是只引用整图。
7. 对宽表优先通过缩短列名、拆分主表/附表、使用 `S` 列和更紧凑但可读的列距来解决宽度问题；仅把 `\resizebox` 当作最后手段。
8. 最终提交前必须在有 LaTeX 工具链的环境中编译 PDF，逐页检查：表格是否越界、图中文字是否可读、legend 是否遮挡数据、浮动体是否造成大空白或集中堆叠。

独立性说明：本次审计未访问 `Audit/reports`，也未读取 `Audit/reports_codex` 中的其他 Codex 报告。
