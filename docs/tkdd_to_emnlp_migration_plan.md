# TKDD → EMNLP LaTeX 模板迁移计划

> **目标**：将当前基于 `acmart` (TKDD journal) 格式的论文 100% 内容还原迁移至 EMNLP (`acl.sty`) 格式。  
> **范围**：仅关注格式与展示层迁移，不修改论文内容本身。  
> **原则**：使用 subagent 进行逐项内容比对与校验，确保迁移后内容零丢失。

---

## 一、两模板核心差异总览

| 维度 | TKDD (`acmart`) | EMNLP (`acl.sty`) |
|:---|:---|:---|
| 文档类 | `\documentclass[acmsmall]{acmart}` | `\documentclass[11pt]{article}` + `\usepackage[review]{acl}` |
| 引文样式 | `ACM-Reference-Format.bst` (数字式) | `acl_natbib.bst` (作者-年式, natbib) |
| 引用命令 | `\cite` (数字) | `\citet` / `\citep` / `\cite` (作者-年) |
| 作者格式 | `\author{}` + `\affiliation{}` + `\email{}` (结构化) | `\author{}` 内自由文本块 |
| 版权/期刊元数据 | `\setcopyright`, `\acmJournal{TKDD}`, `\acmDOI` 等 | 无 |
| Abstract | `\begin{abstract}...\end{abstract}` (独立文件) | 同, 但位于 `\maketitle` 之前 |
| Keywords | `\keywords{...}` | 无标准命令; 可删除或用 `\paragraph{Keywords}` |
| Acknowledgments | `\begin{acks}...\end{acks}` | `\section*{Acknowledgments}` |
| 页面限制 | 期刊无严格限制 | Long paper: **8页正文** + 无限 references + appendix |
| 双栏/单栏 | 单栏 (`acmsmall`) | 双栏 (`acl.sty` 自动) |
| 行号 | 无 | Review 模式自动添加 |
| Appendix | `\appendix` + `\section{}` | 同, 位于 references 之后 |
| `table*` / `figure*` | 跨栏使用 `table*` / `figure*` | 同 (`acl.sty` 支持双栏) |
| `algorithm*` | `algorithm*` 跨栏 | 需 `\usepackage{algorithm}` + `algorithm*` |

---

## 二、文件结构规划

### 2.1 目标文件结构

```
Latex-EMNLP/
├── main.tex                  # 新主文件
├── acl.sty                   # 已有
├── acl_natbib.bst            # 已有
├── references.bib            # 从根目录复制
├── README.md                 # 简要编译说明
├── sections/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── method.tex
│   ├── experiments.tex
│   ├── discussion.tex
│   ├── limitations.tex
│   ├── conclusion.tex
│   └── appendix.tex
└── figures/
    ├── intro2.png
    ├── pipeline.png
    ├── shd_comparison_acm.pdf
    ├── collage_3x2.png
    ├── llm_compare.pdf
    ├── graph/
    │   ├── reference.pdf
    │   ├── llm.pdf
    │   └── structsynth.pdf
    └── influence_n/
        └── vary_n_all.pdf
```

### 2.2 需复制/链接的资源

| 源路径 | 目标路径 | 操作 |
|:---|:---|:---|
| `references.bib` | `Latex-EMNLP/references.bib` | 复制 |
| `sections/*.tex` (9个文件) | `Latex-EMNLP/sections/*.tex` | 复制并修改 |
| `figures/*` 及子目录 | `Latex-EMNLP/figures/*` | 复制或符号链接 |

---

## 三、迁移执行计划

### Phase 0: 环境准备

**Subagent 任务**: 验证 EMNLP 模板编译环境

- [ ] 确认 `acl.sty`, `acl_natbib.bst` 存在于 `Latex-EMNLP/`
- [ ] 确认 `references.bib` 已替换模板 `custom.bib`
- [ ] 用 `main.tex` 做空白编译测试，确认模板可用
- [ ] 创建 `sections/` 和 `figures/` 子目录

### Phase 1: 主文件 (`main.tex`) 迁移

#### 1.1 文档类与宏包替换

**TKDD 原始 (main.tex)**:
```latex
\documentclass[acmsmall]{acmart}
```

**EMNLP 目标**:
```latex
\documentclass[11pt]{article}
\usepackage[review]{acl}
\usepackage{times}
\usepackage{latexsym}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage{inconsolata}
```

#### 1.2 宏包兼容性映射

| TKDD 宏包 | EMNLP 状态 | 处理 |
|:---|:---|:---|
| `algorithm`, `algorithmicx`, `algpseudocode` | 需保留 | 直接 `\usepackage` |
| `amsmath`, `amssymb`, `amsfonts` | 需保留 | `acl.sty` 已含 amsmath, 其余保留 |
| `booktabs`, `multirow`, `makecell`, `subcaption` | 需保留 | 直接 `\usepackage` |
| `xcolor`, `colortbl`, `pifont` | 需保留 | 注意 `acl.sty` 已加载 xcolor |
| `tcolorbox` (+ skins) | 需保留 | appendix 中大量使用 |
| `enumitem` | 需保留 | `leftmargin=*` 在多处使用 |
| `siunitx` | 需保留 | Table 5 (token usage) 使用 `S` 列格式 |
| `graphicx` | 需保留 | `acl.sty` 可能已含, 安全重复加载 |
| `hyperref` | **冲突风险** | `acl.sty` 自动加载, **需删除手动 `\usepackage{hyperref}`** |

**⚠️ 关键注意事项**:
1. **删除** `\usepackage{hyperref}` — `acl.sty` 已内置，重复加载会报错
2. **删除** `\AtBeginDocument{\providecommand\BibTeX{{Bib\TeX}}}` — ACL 模板已提供
3. **删除** 所有 ACM 元数据命令:
   - `\setcopyright{acmlicensed}`
   - `\copyrightyear{2025}` / `\acmYear{2025}`
   - `\acmDOI{...}` / `\acmJournal{TKDD}`
   - `\acmVolume{0}` / `\acmNumber{0}` / `\acmArticle{0}` / `\acmMonth{0}`
4. **删除** `\renewcommand{\shortauthors}{Liu et al.}` — ACL 无此机制

#### 1.3 自定义命令迁移

以下自定义命令 **全部保留**，直接复制到新 `main.tex` 的 preamble 中:

```latex
\colorlet{SubtotalGray}{black!8}
\definecolor{RedOrange}{RGB}{255,69,0}
\definecolor{BlueGreen}{RGB}{0,128,128}
\definecolor{mygray}{gray}{0.4}
\definecolor{darksalmon}{rgb}{0.91, 0.59, 0.48}
\definecolor{green(pigment)}{rgb}{0.0, 0.65, 0.31}

\newcommand{\cmark}{\color{mygray}\ding{51}}
\newcommand{\xmark}{\color{mygray}\ding{55}}
\newcommand{\XSolidBrush}{\ding{55}}
\newcommand{\Checkmark}{\ding{51}}
\newcommand{\blue}[1]{$_{\color{BlueGreen}\downarrow #1}$}
\newcommand{\red}[1]{$_{\color{RedOrange}\uparrow #1}$}

\hyphenpenalty = 5000
\tolerance = 2000
```

**⚠️ 注意**: `\graphicspath{{figures/}}` 需确认与目标目录结构一致。

#### 1.4 作者信息格式转换

**TKDD 格式**:
```latex
\author{Siyi Liu}
\email{ssui.liu1022@gmail.com}
\affiliation{%
  \institution{The Hong Kong University of Science and Technology (Guangzhou)}
  \city{Guangzhou}
  \country{China}
}
```

**EMNLP 格式**:
```latex
\author{
  Siyi Liu \\
  The Hong Kong University of Science and Technology (Guangzhou) \\
  \texttt{ssui.liu1022@gmail.com} \\\And
  Yujia Zheng \\
  Carnegie Mellon University \\
  \texttt{yujiazh@cmu.edu} \\\And
  Yongqi Zhang \\
  The Hong Kong University of Science and Technology (Guangzhou) \\
  \texttt{yzhangee@connect.ust.hk}
}
```

**⚠️ Review 模式**: `\usepackage[review]{acl}` 会自动匿名化作者信息，但作者块仍需完整填写。

#### 1.5 文档主体结构调整

**TKDD 顺序**:
```
\input{sections/abstract}  →  \keywords{...}  →  \maketitle
→ introduction → related_work → method → experiments → discussion → limitations → conclusion
→ \begin{acks} → bibliography → \appendix → appendix
```

**EMNLP 目标顺序**:
```
\begin{abstract}...\end{abstract}  →  \maketitle
→ introduction → related_work → method → experiments → discussion → limitations → conclusion
→ \section*{Limitations} (EMNLP 要求)
→ % \section*{Acknowledgments} (review 模式下注释掉)
→ \bibliography{references}
→ \appendix → appendix
```

**关键变化**:
1. `\keywords{...}` **删除** — EMNLP 无标准 keywords 命令
2. `\begin{acks}...\end{acks}` → `% \section*{Acknowledgments}` (review 模式下注释掉)
3. `\bibliographystyle{ACM-Reference-Format}` → `\bibliographystyle{acl_natbib}`
4. `\bibliography{references}` → `\bibliography{references}` (文件名不变)
5. Abstract 仍使用 `\input{sections/abstract}`，但需确认文件内已有 `\begin{abstract}...\end{abstract}`

---

### Phase 2: 引文格式迁移 (最高风险)

#### 2.1 引文样式变更

| 维度 | TKDD (ACM-Reference-Format) | EMNLP (acl_natbib) |
|:---|:---|:---|
| 格式 | 数字式: `[1]`, `[2,3]` | 作者-年: `(Smith, 2020)`, `Smith (2020)` |
| 默认命令 | `\cite` → `[1]` | `\cite` → `(Smith, 2020)` |
| 文本中引用 | N/A | `\citet{key}` → `Smith (2020)` |
| 括号引用 | N/A | `\citep{key}` → `(Smith, 2020)` |
| 多引用 | `\cite{a,b}` → `[1,2]` | `\citep{a,b}` → `(Smith, 2020; Jones, 2021)` |

#### 2.2 引用命令检查清单

**Subagent 任务**: 扫描所有 `sections/*.tex` 文件中的 `\cite` 使用

- [ ] 统计所有 `\cite{}` 出现次数和位置
- [ ] 检查是否有 `\citep` / `\citet` (当前 TKDD 版本可能不使用)
- [ ] 在 EMNLP 模板中，`\cite` 默认等同 `\citep`，所以大多数情况 **不需要修改**
- [ ] 检查文本中 "Author (Year)" 模式的引用是否需要改为 `\citet`
- [ ] 特别注意表格中的引用 `\cite{...}` 确保在双栏下正常显示

#### 2.3 BibTeX 文件适配

- [ ] 确认 `references.bib` 中所有条目都有完整的 `author`, `year`, `title` 字段
- [ ] 检查 `@misc` 条目是否有 `year` 字段 (作者-年格式必须)
- [ ] 检查 `howpublished` 字段中的 URL 是否需要迁移到 `url` 字段
- [ ] **特别注意**: ACL 要求引用中包含 DOI (当可用时)

---

### Phase 3: Section 文件逐一迁移

#### 3.1 `abstract.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\begin{abstract}...\end{abstract}` 保留 | ⬜ | 无需修改 |
| 字数 ≤ 200 词 | ⬜ | EMNLP 要求; 需计数确认 |
| 无特殊格式依赖 | ⬜ | `\textsf`, `\textit` 均兼容 |

**Subagent 任务**: 统计 abstract 字数并报告

#### 3.2 `introduction.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\begin{figure}[t]` → 兼容 | ⬜ | ACL 双栏下 `\columnwidth` 自动调整 |
| `\includegraphics[width=\columnwidth]` | ⬜ | 双栏下 `\columnwidth` 更窄, 图片会自动缩小 |
| `Figure~\ref{fig:teaser}` 引用 | ⬜ | 无需修改 |
| `\begin{itemize}[leftmargin=*]` | ⬜ | 需 `enumitem` 包, 已加载 |
| `Section~\ref{sec:why_dag}` 交叉引用 | ⬜ | 无需修改 |

#### 3.3 `related_work.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\begin{figure*}[t]` (pipeline) | ⬜ | `figure*` 在 ACL 双栏下跨双栏, 兼容 |
| `\includegraphics[width=\textwidth]` | ⬜ | `\textwidth` 在双栏下指整页宽度, 兼容 |
| `\subsection{...}` / `\subsubsection{...}` | ⬜ | ACL 支持三级标题 |
| 管道图位于此文件而非 method.tex | ⬜ | 注意 label `fig:pipeline` 引用关系 |

#### 3.4 `method.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\paragraph{...}` 大量使用 | ⬜ | ACL 支持 `\paragraph` |
| 数学公式 (`equation` 环境) | ⬜ | 完全兼容 |
| `\begin{table*}[ht]` (Table 1: performance) | ⬜ | **注意**: 此表位于 method.tex 而非 experiments.tex |
| `\begin{algorithm*}` | ⬜ | 需确认 `algorithm` + `algorithm*` 在 ACL 下正常 |
| `\footnote{...}` | ⬜ | ACL 支持, 但双栏下可能布局不同 |
| `Section~\ref{...}` 交叉引用 | ⬜ | 需确保 label 未变 |

**⚠️ 高风险项**: Table 1 (`tab:results_comparison_performance`) 嵌入在 `method.tex` (line 81-121)。需确认此位置是否合理，或考虑迁移至 `experiments.tex`。但本迁移计划不涉及内容调整，因此保持原位。

#### 3.5 `experiments.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\begin{table*}[ht]` 多个大表 | ⬜ | 双栏下跨栏表, 需确认布局 |
| `\begin{table}[htbp]` 小表 | ⬜ | 单栏表, 需确认 `\columnwidth` 下可读性 |
| `\begin{figure*}[t!]` 多个大图 | ⬜ | 跨双栏图, 兼容 |
| `\begin{figure}[h]` 单栏图 | ⬜ | `llm_compare.pdf` 单栏, 需确认尺寸 |
| `\rowcolor{SubtotalGray}` (Table 5) | ⬜ | 需 `colortbl` 包, 已加载 |
| `S[table-format=+3.1]` siunitx 列格式 | ⬜ | 需 `siunitx` 包, 已加载 |
| `\makecell[l]{...}` | ⬜ | 需 `makecell` 包, 已加载 |
| `\small` / `\footnotesize` 表格缩放 | ⬜ | 双栏下列宽更窄, 可能需要调整字号 |

**⚠️ 双栏布局风险**: 
- `Table 2` (dataset_summary): 6 列, 双栏下可能溢出, 需测试
- `Table 3` (privacy+fidelity): 10 列 + 分组, 是最大风险项
- `Table 4` (ablation): 4 列, 安全
- `Table 5` (token_usage): 9 列 + siunitx, 需仔细测试
- 建议对宽表使用 `\resizebox{\textwidth}{!}{...}` 或 `\resizebox{\columnwidth}{!}{...}`

#### 3.6 `discussion.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| 纯文本 + `\ref{}` 引用 | ⬜ | 无特殊格式, 低风险 |
| `\ref{sec:why_dag}` 等内部引用 | ⬜ | 需确认 label 名称未变 |

#### 3.7 `limitations.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\section{Limitations and Future Directions}` | ⬜ | **EMNLP 要求**: 使用 `\section*{Limitations}` |
| `\paragraph{...}` 子段落 | ⬜ | 兼容 |
| `\ref{sec:why_dag}` 等引用 | ⬜ | 需确认 |

**⚠️ EMNLP 特殊要求**: EMNLP 2024+ 要求论文包含 `\section*{Limitations}` 章节。当前 TKDD 版本使用 `\section{Limitations and Future Directions}` (编号节)。迁移时需改为 `\section*{Limitations}` (无编号) 以符合 EMNLP 规范。但**由于计划要求不修改内容**，此处仅记录差异，迁移时保持原标题或做最小改动。

#### 3.8 `conclusion.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| 纯文本 | ⬜ | 低风险 |

#### 3.9 `appendix.tex`

| 检查项 | 状态 | 说明 |
|:---|:---|:---|
| `\section{Detailed Prompts...}` | ⬜ | Appendix 在 `\appendix` 后变为 A, B... |
| `tcolorbox` 环境 (6 个 prompt box) | ⬜ | **高风险**: 双栏下 tcolorbox 宽度需调整 |
| `\begin{tcolorbox}[float*=t, width=\textwidth]` | ⬜ | `width=\textwidth` 在双栏下指整页宽, 需确认是否符合预期 |
| `\begin{verbatim}` 环境 | ⬜ | tcolorbox 内 verbatim 通常正常 |
| `\label{box:...}`, `\label{prompt:...}` | ⬜ | `\hyperref[...]{}` 引用需确认兼容性 |
| `\clearpage` | ⬜ | 保持 |

**⚠️ tcolorbox 风险**: 所有 6 个 tcolorbox 使用 `float*=t, width=\textwidth`，在 ACL 双栏下会跨双栏显示。这通常是期望行为 (prompt 模板需要宽空间)，但需编译验证。如果 `float*` 不被 `acl.sty` 支持，可能需要改用 `\begin{figure*}` 包装。

---

### Phase 4: 编译与验证

#### 4.1 编译命令

```bash
cd Latex-EMNLP
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

#### 4.2 验证清单 (Subagent 执行)

**Subagent A: 内容完整性验证**
- [ ] 逐节对比 TKDD 版本与 EMNLP 版本的文字内容
- [ ] 确认所有 `\ref{}` 引用均正确解析 (无 `??`)
- [ ] 确认所有 `\cite{}` 引用均正确显示 (无 `[?]`)
- [ ] 统计并对比两版本的章节数、表格数、图数、公式数
- [ ] 确认无丢失的段落或句子

**Subagent B: 图表完整性验证**
- [ ] 确认所有图片文件可被正确找到和渲染
- [ ] 逐一检查每个 Figure 的 `\label` 和 `\ref` 配对
- [ ] 逐一检查每个 Table 的 `\label` 和 `\ref` 配对
- [ ] 确认表格内容 (数值、文本) 与原版一致
- [ ] 检查表格在双栏下是否溢出页面

**Subagent C: 格式合规性验证**
- [ ] 确认页数 ≤ 8 页正文 (不含 references 和 appendix)
- [ ] 确认使用了 A4 纸张
- [ ] 确认 review 模式下行号正确显示
- [ ] 确认作者信息已匿名化
- [ ] 确认无 ACM/TKDD 残留元数据输出到 PDF
- [ ] 确认 `Limitations` 章节存在
- [ ] 确认 `Acknowledgments` 在 review 模式下被隐藏

---

## 四、迁移步骤详细时序

```
Step 1: 环境准备 (Phase 0)
  ├── 创建目录结构
  ├── 复制资源文件
  └── 空白编译测试

Step 2: 主文件构建 (Phase 1)
  ├── 创建 main.tex (文档类 + 宏包 + 自定义命令)
  ├── 转换作者信息格式
  ├── 调整文档结构顺序
  └── 首次编译测试 (空 body)

Step 3: Section 文件复制与适配 (Phase 3)
  ├── 复制 9 个 section 文件
  ├── 检查并修复已知兼容性问题
  └── 逐文件增量编译测试

Step 4: 引文迁移 (Phase 2)
  ├── 复制 references.bib
  ├── 更改 \bibliographystyle
  ├── 编译测试引文显示
  └── 检查所有引用命令

Step 5: 全量编译与验证 (Phase 4)
  ├── 完整编译 (pdflatex × 3 + bibtex)
  ├── Subagent A: 内容完整性
  ├── Subagent B: 图表完整性
  └── Subagent C: 格式合规性

Step 6: 差异修复
  ├── 修复验证中发现的问题
  ├── 二次编译验证
  └── 最终确认
```

---

## 五、风险矩阵与缓解策略

| 风险 | 严重度 | 可能性 | 缓解策略 |
|:---|:---|:---|:---|
| `hyperref` 重复加载导致编译失败 | 🔴 高 | 🔴 高 | 删除手动 `\usepackage{hyperref}` |
| 大表格在双栏下溢出 | 🔴 高 | 🟡 中 | 使用 `\resizebox` 或改用 `table*` |
| `tcolorbox` + `float*` 在 ACL 下不兼容 | 🟡 中 | 🟡 中 | 测试; 备选方案: 用 `figure*` 包裹 |
| 引用格式从数字变作者-年导致文本不通顺 | 🟡 中 | 🟡 中 | 检查所有 "作者 (年)" 模式, 改用 `\citet` |
| 正文超过 8 页限制 | 🔴 高 | 🟡 中 | EMNLP 允许 appendix, 非核心内容可移至 appendix |
| `siunitx` S 列格式在双栏下表现异常 | 🟡 中 | 🟢 低 | 编译后检查 Table 5 |
| `algorithm*` 在 ACL 双栏下不跨栏 | 🟡 中 | 🟢 低 | 测试; 必要时使用 `algorithm` + 单栏 |
| `\textsf{StructSynth}` 字体在 Times 下表现 | 🟢 低 | 🟢 低 | 视觉检查即可 |
| `green(pigment)` 颜色名含括号, 可能与某些包冲突 | 🟢 低 | 🟢 低 | 已在 TKDD 版本中工作, 大概率兼容 |

---

## 六、内容清单 (用于 Subagent 逐项校验)

### 6.1 Figure 清单

| # | Label | 文件 | 类型 | 位置 (section) |
|:---|:---|:---|:---|:---|
| 1 | `fig:teaser` | `figures/intro2.png` | 单栏 `[t]` | introduction |
| 2 | `fig:pipeline` | `figures/pipeline.png` | 双栏 `figure*` `[t]` | related_work |
| 3 | `fig:shd` | `figures/shd_comparison_acm.pdf` | 双栏 `figure*` `[t!]` | experiments |
| 4 | `fig:structure` | 3 × subfigure (`graph/*.pdf`) | 双栏 `figure*` `[h!]` | experiments |
| 5 | `fig:structure_examples` | `figures/collage_3x2.png` | 双栏 `figure*` `[t!]` | experiments |
| 6 | `fig:influence_n` | `figures/influence_n/vary_n_all.pdf` | 双栏 `figure*` `[t!]` | experiments |
| 7 | `fig:llm_compare` | `figures/llm_compare.pdf` | 单栏 `[h]` | experiments |

### 6.2 Table 清单

| # | Label | 列数 | 类型 | 位置 (section) |
|:---|:---|:---|:---|:---|
| 1 | `tab:results_comparison_performance` | 10 | `table*` | method |
| 2 | `tab:dataset_summary` | 7 | `table*` | experiments |
| 3 | `tab:results_comparison_merged` | 10 | `table*` | experiments |
| 4 | `tab:hyperparameters` | 2 | `table` (单栏) | experiments |
| 5 | `tab:ablation_study` | 4 | `table` (单栏) | experiments |
| 6 | `tab:token_usage` | 9 | `table*` + siunitx | experiments |

### 6.3 Algorithm 清单

| # | Label | 类型 | 位置 |
|:---|:---|:---|:---|
| 1 | `alg:structsynth` | `algorithm*` | method |

### 6.4 Equation 清单

| 文件 | 公式数 | 说明 |
|:---|:---|:---|
| `method.tex` | ~10 | Pearson's R, Cramér's V, Correlation Ratio 等 |
| `experiments.tex` | 4 | Statistical Fidelity, Privacy Risk 公式 |

### 6.5 Appendix 内容

| # | 类型 | Label | 说明 |
|:---|:---|:---|:---|
| 1 | Section + tcolorbox | `app:prompts` | Prompt 详细说明 |
| 2 | tcolorbox | `box:textualization_examples` | Box 1: 文本化示例 |
| 3 | tcolorbox | `prompt:source` | π_source prompt |
| 4 | tcolorbox | `prompt:generation` | π_generation prompt |
| 5 | tcolorbox | `prompt:resolve` | π_resolve prompt |
| 6 | tcolorbox | `prompt:data_gen` | π_data_gen prompt |
| 7 | tcolorbox | `prompt:data_gen_iso` | π_data_gen_iso prompt |

---

## 七、Subagent 任务分配汇总

| Subagent | 任务描述 | 输入 | 预期输出 |
|:---|:---|:---|:---|
| **A: 内容完整性** | 逐段比对 TKDD 源文件与迁移后文件的文本内容 | 9 对 section 文件 | 差异报告 (位置 + 内容) |
| **B: 图表校验** | 确认所有 figure/table/algorithm 的 label-ref 配对、文件存在性、渲染正确性 | 编译后的 PDF + log | 完整性清单 + 异常列表 |
| **C: 引文校验** | 检查所有 `\cite` 命令在新格式下正确显示，无 `[?]` | 编译后的 PDF + .bbl | 引用完整性报告 |
| **D: 格式合规** | 检查页数、匿名化、行号、A4 纸张、无 ACM 残留 | 编译后的 PDF | 合规性 checklist |
| **E: 交叉引用** | 检查所有 `\ref`, `\hyperref` 引用正确解析 | 编译后的 PDF + log | 未解析引用列表 |

---

## 八、执行命令速查

```bash
# Step 0: 创建目标目录
mkdir -p Latex-EMNLP/sections Latex-EMNLP/figures/graph Latex-EMNLP/figures/influence_n

# Step 1: 复制资源
cp sections/*.tex Latex-EMNLP/sections/
cp references.bib Latex-EMNLP/
cp figures/intro2.png Latex-EMNLP/figures/
cp figures/pipeline.png Latex-EMNLP/figures/
cp figures/shd_comparison_acm.pdf Latex-EMNLP/figures/
cp figures/collage_3x2.png Latex-EMNLP/figures/
cp figures/llm_compare.pdf Latex-EMNLP/figures/
cp figures/graph/*.pdf Latex-EMNLP/figures/graph/
cp figures/influence_n/vary_n_all.pdf Latex-EMNLP/figures/influence_n/

# Step 2: 编译 (在 Latex-EMNLP/ 下执行)
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

---

## 九、已知限制与后续工作

1. **页数压缩**: TKDD 为期刊格式无页数限制，当前正文可能在 EMNLP 8 页限制内溢出。若溢出，需考虑将部分内容 (如 Discussion 细节、Efficiency Analysis) 移至 Appendix。
2. **表格缩放**: 双栏下列宽约 7.7cm (vs TKDD 单栏 ~14cm)，部分宽表需缩放或重排。
3. **tcolorbox 跨栏**: `float*=t` 在 ACL 双栏下需实际编译验证。
4. **颜色名 `green(pigment)`**: 含括号的颜色名是合法 LaTeX 但不常见，已在 TKDD 版本中工作。
5. **`subcaption` vs `subfigure`**: 当前使用 `subcaption` 包的 `subfigure` 环境，需确认与 ACL 模板无冲突。
6. **引用格式差异**: 从数字引用变作者-年引用，某些上下文中 "as shown in [3]" 类表述需改为 "as shown in (Author, Year)"。
