# Level 9 LaTeX Typesetting & Formatting 审计报告

## 1. 标题与范围

本报告独立审计 `Latex-EMNLP/**` 的 Level 9：LaTeX Typesetting & Formatting。范围覆盖非换行空格、手动间距、label/ref、方法/数据集/模型/指标格式一致性、连字符与破折号、页数预算风险和 LaTeX 源码卫生。审计依据为 `Audit/writing_checklist.md` 中 9.1--9.5 条目；本次以静态分析为主，因本机缺少 `latexmk`、`pdflatex`、`bibtex`、`tectonic`，未能编译 PDF 验证实际页数和 overfull boxes。

## 2. 结论概览

| 条目 | 结论 | 摘要 |
|---|---|---|
| 9.1 Spacing | 部分通过 | `Figure~\ref{}`、`Table~\ref{}`、`Appendix~\ref{}` 等引用前非换行空格整体做得好；但主文和附录存在多处 `\resizebox`、`\small`、`\vspace`、`\hspace`、`\setlength{\tabcolsep}{...}`。 |
| 9.2 Hyphenation/dashes | 基本通过 | `low-data`、`structure-aware`、`LLM-based` 等复合修饰语较一致；范围使用 `--`，插入说明多用 `---`。未发现严重 dash 误用。 |
| 9.3 Consistent formatting | 未完全通过 | `\textsf{StructSynth}` 与 plain `StructSynth` 混用；`CLLM` 在主文多为 plain，在附录效率表中为 `\textsc{CLLM}`；指标大小写/缩写也有混用。 |
| 9.4 Cross-references | 基本通过 | 静态比对未发现未定义引用或重复 label，也未发现 `Table \ref` 这类明显漏 `~` 的模式；但存在同一位置双 label 和非标准 label 前缀需要统一规范。 |
| 9.5 Page budget | 有风险 | 主文已有多个 `figure*`/`table*`，且用 `\resizebox`、`\small`、极小 `\tabcolsep` 压缩表格；无法本地编译确认是否满足 EMNLP 页数限制。 |

## 3. 优点

- 交叉引用写法总体稳健：正文中可见 `Figure~\ref{fig:teaser}`、`Appendix~\ref{app:datasets}`、`Table~\ref{tab:results_comparison_performance}` 等，静态扫描未发现空格版 `Figure \ref` / `Table \ref`。
- label/ref 静态集合完整：未发现 unresolved refs 或 duplicate labels；`fig:`、`tab:`、`sec:`、`app:`、`alg:` 主体前缀基本可读。
- dash 使用整体成熟：例如范围 `1.0--1.4`、随机种子 `42--51`，以及解释性插入 `---` 在 LaTeX 源中基本符合习惯。
- 代码/命令名大体使用 `\texttt{}`，如 `\texttt{gpt-4o-mini}` 与 `\texttt{bnlearn}`。

## 4. 问题清单（按严重程度）

### 严重：主文表格存在明显压缩，影响可读性与页数合规判断

- `Latex-EMNLP/sections/method.tex:48-49` 对下游性能大表同时使用 `\resizebox{\textwidth}{!}` 和 `\small`。
- `Latex-EMNLP/sections/experiments.tex:22-23` 对隐私/保真度大表同样使用 `\resizebox{\textwidth}{!}` 和 `\small`。
- `Latex-EMNLP/sections/experiments.tex:110`、`Latex-EMNLP/sections/experiments.tex:114` 对 ablation 表使用 `\small` 和 `\setlength{\tabcolsep}{1mm}`。

这属于 9.1/9.5 的核心风险：即使能编译通过，也可能把表格字体压到 ACL/EMNLP 审稿可读性边缘，并掩盖真实页数压力。

### 较严重：结果表源码放在 `method.tex`，与引用位置和论文结构不一致

- `Latex-EMNLP/main.tex:120-121` 先输入 `sections/method`，再输入 `sections/experiments`。
- `Latex-EMNLP/sections/method.tex:44-85` 却放置了 “Comparison of Models on Downstream Model Performance” 结果表。
- 该表在实验部分才被引用：`Latex-EMNLP/sections/experiments.tex:84`。
- `Latex-EMNLP/sections/method.tex:109` 还有注释 `%% Experiments section - migrated from AAAI source`，显示迁移后源码边界未完全清理。

这会增加 float 出现在方法段附近的风险，也让后续维护、页数排查和表格重排更难。

### 中等：方法名和模型名格式不统一

- 主文中方法名常用 `\textsf{StructSynth}`，如 `Latex-EMNLP/sections/introduction.tex:28`、`Latex-EMNLP/sections/experiments.tex:84`。
- 表格单元格中却出现 plain `StructSynth`：`Latex-EMNLP/sections/method.tex:80`、`Latex-EMNLP/sections/experiments.tex:54`、`Latex-EMNLP/sections/experiments.tex:75`。
- 附录讨论段也多次使用 plain `StructSynth`：`Latex-EMNLP/sections/appendix.tex:454`、`456`、`466`、`487`、`489`。
- `CLLM` 在主文多为 plain，如 `Latex-EMNLP/sections/experiments.tex:15`、`84`；但附录效率分析改为 `\textsc{CLLM}`，如 `Latex-EMNLP/sections/appendix.tex:395`、`403`、`413`。

这会让方法名和基线名在正文、表格、附录中的视觉身份不稳定。

### 中等：指标名称大小写和简称不够统一

- 正式定义处使用 `Downstream Model Performance`、`Statistical Fidelity`、`Privacy Risk`：`Latex-EMNLP/sections/experiments.tex:11`。
- 摘要、引言、结论使用 lowercase 描述：`downstream utility`、`privacy preservation`、`statistical fidelity`，如 `Latex-EMNLP/sections/abstract.tex:3`、`Latex-EMNLP/sections/introduction.tex:35`、`Latex-EMNLP/sections/conclusion.tex:4`。
- ablation 表头压缩为 `AUC`、`Fidelity`、`Privacy`：`Latex-EMNLP/sections/experiments.tex:117`。
- 图注又写成 lowercase `statistical fidelity` 和 `privacy risk deviation`：`Latex-EMNLP/sections/experiments.tex:144`。

建议明确哪些是正式指标名、哪些是普通语义描述；否则读者可能不确定 `Privacy Risk` 与 `privacy preservation` 是否同一量。

### 中等：附录大量手动间距和小字号，源码卫生压力较大

- 算法中使用 `\vspace{0.2cm}`、`\vspace{0.3cm}` 和多处 `\hspace{\algorithmicindent}`：`Latex-EMNLP/sections/appendix.tex:98`、`109`、`117`、`132`、`138`。
- prompt boxes 中大量 `\small` 与 `\vspace{\medskipamount}`：例如 `Latex-EMNLP/sections/appendix.tex:502`、`516`、`561`、`565`、`608`、`612`、`709`、`713`、`763`、`767`。
- 附录 token 表也使用 `\resizebox` + `\small`：`Latex-EMNLP/sections/appendix.tex:406-407`。

附录比主文更能容忍版式微调，但这些手工间距若继续累积，会使换模板或 camera-ready 调整时很脆。

### 较轻：label 前缀有双轨和局部非标准用法

- 同一附录 section 同时给 `sec:` 和 `app:` label：`Latex-EMNLP/sections/appendix.tex:49-50`、`86-87`。
- prompt/box 使用 `prompt:`、`box:`：`Latex-EMNLP/sections/appendix.tex:546`、`594`、`656`、`697`、`751`、`802`。

这些引用可解析，但应在源码约定中说明：section 是统一用 `sec:`，还是附录 section 用 `app:`；自定义 box/prompt 前缀是否被正式接受。

## 5. 可执行修改建议

1. 为专名建立宏：例如 `\newcommand{\method}{\textsf{StructSynth}}`、`\newcommand{\cllm}{\textsc{CLLM}}`，然后全文替换 plain `StructSynth`/不一致 `CLLM`。
2. 将 `method.tex:44-85` 的下游性能结果表移到 `experiments.tex` 对应首次引用附近；保留 `tab:results_comparison_performance`，避免破坏已有引用。
3. 优先重排主文大表，而不是同时使用 `\resizebox` 和 `\small`：可考虑拆分为两张表、减少列文本、使用 `tabular*`/`siunitx` 对齐、或把部分结果移入附录。
4. 把 ablation 表的 `\setlength{\tabcolsep}{1mm}` 放入局部 group，并尝试提升到更可读的列距；若仍超宽，改表结构而不是继续压缩。
5. 统一指标词表：正文首次定义使用正式名，后文固定为 `AUC`、`R^2`、`Statistical Fidelity`、`Privacy Risk` 或明确使用普通小写描述。
6. 对附录 prompt boxes 建立统一环境或宏来管理 `\small` 和段间距，减少散落的 `\vspace{\medskipamount}`。
7. 统一 label 策略：section 用 `sec:`，appendix-only anchors 若需要可用 `app:`，但避免同一标题同时挂两个 label；为 `prompt:` 和 `box:` 在源码注释中说明约定。
8. 在有 TeX 工具的环境中编译一次，检查主文页数、表格字体、float 位置、overfull/underfull box；这是 9.5 最后必须确认的一步。

## 6. 独立性说明

本报告仅基于 `Audit/writing_checklist.md`、`Latex-EMNLP/**` 及这些允许文件上的本地静态命令输出完成；我没有访问 `Audit/reports`，也没有读取 `Audit/reports_codex` 中的其他 Codex 报告。
