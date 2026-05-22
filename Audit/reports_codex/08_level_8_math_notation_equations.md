# Level 8 审计报告：数学符号与公式

## 1. 标题与范围

本报告独立审计 `Latex-EMNLP` 论文在 Writing Checklist Level 8（Mathematical Notation & Equations）上的表现，覆盖：

- 8.1 符号一致性：符号复用、首次使用前定义、标量/向量/矩阵/集合样式，以及方法、实验、附录之间的一致性。
- 8.2 公式排版：行内/展示公式选择、公式标点、长公式换行、算子与文本的数学排版。
- 8.3 公式引用：编号公式是否被引用、引用格式是否统一、是否存在未编号但被引用的公式。

审计依据为 `Audit/writing_checklist.md` 的 Level 8 条目，以及 `Latex-EMNLP/**` 中的 LaTeX 源文件。

## 2. 判定摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 8.1 notation consistency | 部分通过，需修订 | 主方法段落的核心符号较清楚，但属性集合、数据矩阵、合成样本、数据集下标风格在方法、算法、附录指标定义之间不一致；`r` 与 `V` 存在跨语境复用风险。 |
| 8.2 equation formatting | 未完全通过 | 多数重要公式使用 display math，函数和文本大多没有裸斜体；但多处公式缺少句末标点，若干长公式存在双栏溢出风险，`align` 对齐方式不够自然。 |
| 8.3 equation referencing | 未通过 | 全文存在 17 个 `equation` 和 1 个 `align` 环境，但未发现 `\eqref{}` 或 `Equation~...` 形式引用；这些公式会自动编号，却没有被引用或加标签。 |

## 3. 优点

- 主方法开头给出了核心数据符号：`Latex-EMNLP/sections/method.tex:4` 定义 `\mathcal{D}_{\mathtt{train}} = (\mathbf{X}_{\mathtt{train}}, \mathbf{A})`、`n`、`K`、`f_{\mathtt{LLM}}` 和 `\mathcal{D}_{\mathtt{synth}}`，读者能较快进入形式化部分。
- 主要算子和文本在数学环境中总体较规范。例如 `\max`、`\min`、`\arg\min`、`\text{...}`、`\mathbb{I}` 的使用出现在 `Latex-EMNLP/sections/appendix.tex:73`, `Latex-EMNLP/sections/appendix.tex:81`, `Latex-EMNLP/sections/appendix.tex:255`, `Latex-EMNLP/sections/appendix.tex:251`。
- 向量/矩阵样式在主方法中基本可读：`Latex-EMNLP/sections/method.tex:90-107` 使用 `\tilde{\mathbf{x}}_j` 表示合成记录，使用 `\mathbf{X}_{\mathtt{synth}}` 表示合成数据矩阵。
- 实验节与主方法对核心数据集符号大体一致：`Latex-EMNLP/sections/experiments.tex:11` 使用 `\mathcal{D}_{\mathtt{aug}}`、`\mathcal{D}_{\mathtt{train}}`、`\mathcal{D}_{\mathtt{synth}}`、`\mathcal{D}_{\mathtt{test}}`。

## 4. 问题（按严重程度排序）

### 严重：所有展示公式默认编号，但没有公式引用

证据：`equation` 环境出现在 `Latex-EMNLP/sections/method.tex:22`, `31`, `39`, `96`, `104`，以及 `Latex-EMNLP/sections/appendix.tex:56`, `63`, `72`, `76`, `80`, `240`, `250`, `254`, `258`, `269`, `281`, `287`；`align` 环境出现在 `Latex-EMNLP/sections/appendix.tex:274`。对 `Latex-EMNLP/main.tex` 与 `Latex-EMNLP/sections/*.tex` 的扫描未发现 `\eqref{}` 或 `Equation~` 引用。

影响：这直接违反 8.3 的“编号公式必须被引用”要求，也会让 PDF 中出现一串无用途的公式编号，增加审稿人的阅读噪音。

### 严重：主文与算法附录的矩阵、属性集合、样本向量样式不一致

证据：主方法用 `\mathbf{X}_{\mathtt{train}}` 与 `\mathbf{A}`，见 `Latex-EMNLP/sections/method.tex:4`；但算法输入输出改为普通斜体 `X_{\mathtt{train}}`、`A`，见 `Latex-EMNLP/sections/appendix.tex:95-96`。主方法用 `\tilde{\mathbf{x}}_{j,L_i}`，见 `Latex-EMNLP/sections/method.tex:97`；算法改为 `\tilde{x}_{j,L_i}`，见 `Latex-EMNLP/sections/appendix.tex:142`。

影响：同一对象在主文和算法中看起来像不同类型：矩阵从粗体变普通斜体，记录向量从粗体变标量，属性集合从 `\mathbf{A}` 变 `A`。这削弱可复现性和符号表的一致性。

### 高：集合样式与清单约定不匹配，且与 Cramér's V 形成复用风险

证据：清单要求集合用 calligraphic；主文把属性集合写作 `\mathbf{A}`，节点集和边集写作 `V, E`，见 `Latex-EMNLP/sections/method.tex:4` 和 `Latex-EMNLP/sections/method.tex:12`。同时，附录中 Cramér's V 使用 `V_{\text{corr}}`，见 `Latex-EMNLP/sections/appendix.tex:68-81`。

影响：`V` 既像图的节点集，又出现在 Cramér's V 指标中；`A`/`\mathbf{A}` 也同时承担属性集合和单个属性下标的角色。虽然领域习惯允许 `V,E` 表示图集合，但若按 checklist 执行，应优先改为 `\mathcal{A}`、`\mathcal{V}`、`\mathcal{E}`，保留 `A_i` 表示单个属性。

### 高：同一数据集下标风格在主文/实验和指标附录间漂移

证据：主文和实验使用 `\mathcal{D}_{\mathtt{train}}`、`\mathcal{D}_{\mathtt{synth}}`，见 `Latex-EMNLP/sections/method.tex:4` 与 `Latex-EMNLP/sections/experiments.tex:11`；附录指标定义改用 `\mathcal{D}_{\text{train}}`、`\mathcal{D}_{\text{synth}}`、`\mathcal{D}_{\text{real}}`，见 `Latex-EMNLP/sections/appendix.tex:239-247`。

影响：`\mathtt` 与 `\text` 视觉风格不同，同一 split 名称在 PDF 中不一致。建议选一种风格贯穿全文，尤其是 `train/synth/test/aug/real/few_shot`。

### 中：`r` 在同一关联度附录中代表不同含义

证据：`Latex-EMNLP/sections/appendix.tex:55-59` 中 `r` 是 Pearson 相关系数；`Latex-EMNLP/sections/appendix.tex:69` 中 `r \times k` 的 `r` 又是列联表维度；`Latex-EMNLP/sections/appendix.tex:77-81` 继续使用 `r_{\text{corr}}`。

影响：读者在关联度定义小节内会看到 `r` 从统计量变成维度变量。建议 Pearson 系数统一改为 `\rho`，或把列联表维度改为 `R \times C`。

### 中：prompt 符号命名不一致

证据：方法和算法使用 `\pi_{\mathtt{generate}}`，见 `Latex-EMNLP/sections/method.tex:30-32` 与 `Latex-EMNLP/sections/appendix.tex:113`；提示模板说明和标题使用 `\pi_\mathtt{generation}`，见 `Latex-EMNLP/sections/appendix.tex:489` 与 `Latex-EMNLP/sections/appendix.tex:603`。

影响：`generate` 与 `generation` 看似指同一提示，但符号不同。建议统一为一个符号，并在首次出现时明确“where `\pi_{\mathtt{...}}` denotes the corresponding prompt template”。

### 中：公式标点不系统

证据：方法中有些公式带句点，如 `Latex-EMNLP/sections/method.tex:23`, `40`, `97`, `105`；但 `Latex-EMNLP/sections/method.tex:32` 无句末标点。附录中多处定义公式也无标点，如 `Latex-EMNLP/sections/appendix.tex:57`, `64`, `73`, `77`, `81`, `241`, `251`, `255`, `259`, `270`, `282`, `288`。

影响：公式作为句子的一部分时，缺标点会让段落节奏断裂，也违反 8.2 的显式要求。

### 中：长公式和 `align` 排版有潜在双栏风险

证据：主文的生成公式较长，见 `Latex-EMNLP/sections/method.tex:97` 与 `Latex-EMNLP/sections/method.tex:105`；距离公式较长，见 `Latex-EMNLP/sections/appendix.tex:251`；TVD 公式用 `align`，但对齐点放在概率项前后而非关系或减号结构处，见 `Latex-EMNLP/sections/appendix.tex:274-278`。

影响：未编译 PDF 的情况下不能断言一定溢出，但这些单行公式在 EMNLP 双栏版式中风险较高。`align` 公式的编号也会落在最后一行且未引用。

### 轻：若干函数名更适合声明为数学算子

证据：算法中使用 `\mathtt{Dequeue}`、`\mathtt{DetectCycles}`、`\mathtt{concat}`，见 `Latex-EMNLP/sections/appendix.tex:110`, `119`, `151`；最近邻写作 `NN(\tilde{x})`，见 `Latex-EMNLP/sections/appendix.tex:255`。

影响：这不是裸斜体错误，但作为函数时 `\operatorname{Dequeue}`、`\operatorname{DetectCycles}`、`\operatorname{concat}`、`\operatorname{NN}` 的间距更自然。

## 5. 简明符号表/检查表

| 对象 | 当前写法 | 建议写法 | 状态 |
|---|---|---|---|
| 数据集 | `\mathcal{D}_{\mathtt{train}}` / `\mathcal{D}_{\text{train}}` | 统一为 `\mathcal{D}_{\mathtt{train}}` 或统一为 `\mathcal{D}_{\mathrm{train}}` | 需统一 |
| 数据矩阵 | 主文 `\mathbf{X}_{\mathtt{train}}`；算法 `X_{\mathtt{train}}` | `\mathbf{X}_{\mathtt{train}}`、`\mathbf{X}_{\mathtt{synth}}` | 需统一 |
| 单条记录/向量 | 主文 `\tilde{\mathbf{x}}_j`；算法 `\tilde{x}_j` | `\tilde{\mathbf{x}}_j` | 需统一 |
| 属性集合 | `\mathbf{A}` / `A` | `\mathcal{A}` | 建议按 checklist 修订 |
| 单个属性 | `A_i` | `A_i` | 可保留 |
| 图节点/边集合 | `V, E` | `\mathcal{V}, \mathcal{E}` 或明确说明沿用图论习惯 | 建议明确 |
| Pearson 相关 | `r` | `\rho` | 建议修订以避开 `r \times k` |
| 列联表维度 | `r \times k` | `R \times C` 或 `n_r \times n_c` | 建议修订 |
| Prompt | `\pi_{\mathtt{generate}}` / `\pi_\mathtt{generation}` | 统一一个名称 | 需统一 |
| 函数/算法操作 | `\mathtt{concat}`、`NN` | `\operatorname{concat}`、`\operatorname{NN}` | 建议修订 |

## 6. 可操作修订建议

1. 先处理公式编号：若公式后文不引用，将所有 `\begin{equation}` 改为 `\begin{equation*}` 或 `\[...\]`，将 `align` 改为 `align*`；若主文需要引用关键公式，只保留少数编号公式，加 `\label{eq:...}` 并在正文使用统一格式 `Eq.~(\ref{eq:...})` 或 `Equation~(\ref{eq:...})`。
2. 建立并执行一张全局符号表：建议在方法开头或附录算法前列出 `\mathcal{D}`、`\mathbf{X}`、`\mathbf{x}`、`\mathcal{A}`、`\mathcal{V}`、`\mathcal{E}`、`G`、`\mathcal{S}`、`\pi` 的含义。
3. 统一主文与算法：把 `Latex-EMNLP/sections/appendix.tex:95-96`, `136`, `139`, `142`, `148`, `151-154` 中的 `X`、`A`、`\tilde{x}` 调整为与 `method.tex` 同一套粗体/集合风格。
4. 统一数据集下标：在 `method.tex`、`experiments.tex`、`appendix.tex` 中选择 `\mathtt` 或 `\mathrm` 一种风格；不建议同一对象在主文用 `\mathtt`、指标附录用 `\text`。
5. 消除符号复用：把 Pearson 的 `r` 改为 `\rho`，把列联表维度改为 `R \times C`；若保留 Cramér's V 的 `V_{\text{corr}}`，则把图节点集改为 `\mathcal{V}`，避免视觉冲突。
6. 补齐公式标点：每个展示公式按句子语法加逗号或句号；例如定义后接 “where ...” 的公式末尾通常用逗号，定义段落结束的公式末尾用句号。
7. 拆分长公式：对 `method.tex:97`, `method.tex:105`, `appendix.tex:251`, `appendix.tex:274-278` 使用 `aligned`/`split`，并把对齐点放在 `=` 或主要运算符处。
8. 将函数名改为算子：把 `\mathtt{Dequeue}`、`\mathtt{DetectCycles}`、`\mathtt{concat}`、`NN` 统一成 `\operatorname{...}` 或用 `\DeclareMathOperator` 声明。

## 7. 独立性说明

本次审计仅访问了 `Audit/writing_checklist.md` 与 `Latex-EMNLP/**`，未访问 `Audit/reports`，也未读取 `Audit/reports_codex` 中的其他报告。
