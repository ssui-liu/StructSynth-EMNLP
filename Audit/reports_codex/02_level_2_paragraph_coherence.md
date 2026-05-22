# Level 2 段落级连贯性审计报告

## 1. 标题与范围

本报告审计 `Latex-EMNLP` 论文的 Writing Checklist Level 2: Paragraph-Level Coherence。审计范围包括 `Audit/writing_checklist.md` 中 Level 2 标准，以及 `Latex-EMNLP/main.tex` 所组织的论文正文、限制与附录相关 `.tex` 文件。重点检查段落开头、段落长度、单段单点、段落间过渡、概念引入顺序、given-new 信息流，以及跨章节冗余。

## 2. 判定摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 2.1 Topic sentences | 基本达标 | 主文多数段落以明确主题句开头，尤其是引言、方法和实验小节；附录长综述段落的主题句可读，但读者只扫首句时难以恢复完整论证层级。 |
| 2.2 Paragraph unity | 部分达标 | 多数短段落单点明确；但实验主结果、引言贡献段、数据集设置和附录综述段存在“一段多任务”的问题。 |
| 2.3 Transitions | 部分达标 | 大章节之间总体有自然推进；但方法章节中结果表插入两段方法之间、实验中孤立的一句式段落、以及个别附录跳转削弱了段落间桥接。 |
| 2.4 Given-new flow | 部分达标 | 核心术语一般按“低数据合成→依赖→DAG→生成计划”顺序引入；主要问题是 `Bayesian Sampler` 在正式 ablation 列表前被用于解释主结果。 |
| 2.5 Redundancy | 需要修改 | “fidelity/privacy trade-off”“pairwise vs. conditional dependencies”“structural regularizer”等论证在主文和附录重复展开，应压缩主文或以交叉引用承接。 |

## 3. 优点

- 引言前三段的推进清晰：低数据表格合成问题、现有范式、图作为生成计划的缺口分别由清楚的主题句引出，见 `Latex-EMNLP/sections/introduction.tex:13`、`:17`、`:22`。
- 方法概述先给目标再给两阶段框架，段首直接说明 DAG 的角色，帮助读者建立全局地图，见 `Latex-EMNLP/sections/method.tex:3` 和 `:6`。
- 相关工作按主题组织，而不是作者流水账；三个 `\paragraph` 分别覆盖 low-data synthesis、LLM generation、dependency discovery，见 `Latex-EMNLP/sections/related_work.tex:11`、`:16`、`:22`。
- 实验后半部分的小节开头多用功能性主题句，例如 “To isolate...”、“To evaluate...”、“To assess...”，使读者能快速识别每段实验目的，见 `Latex-EMNLP/sections/experiments.tex:105`、`:166`、`:172`。
- Limitations 每个段落基本只处理一个限制点，段落标题与正文内容匹配，见 `Latex-EMNLP/sections/limitations.tex:3`、`:8`、`:12`。

## 4. 问题（按严重程度排序）

### 高：主结果中的隐私/保真段落承担过多功能，并提前使用后文概念

证据：`Latex-EMNLP/sections/experiments.tex:90` 的单段同时完成六件事：提出 privacy-fidelity tension、举 GReaT 和 SPADA-NF 例子、对比 CLLM、报告 StructSynth、引入 `Bayesian Sampler` ablation、解释 pairwise fidelity 与 conditional dependencies 的差异。`Bayesian Sampler` 直到 `Latex-EMNLP/sections/experiments.tex:105` 才在 ablation 变体列表中正式定义。

影响：该段违反“单段单点”和 given-new flow。读者在尚未理解 ablation 设计时，已经被要求用 `Bayesian Sampler` 支撑主结果解释，认知负担偏高。

### 高：主文与附录重复展开同一段 privacy/fidelity 解释

证据：主文 `Latex-EMNLP/sections/experiments.tex:90` 已完整解释 GReaT 记忆化、Bayesian Sampler 高 pairwise fidelity 但低 AUC、StructSynth 保留 conditional dependencies。附录 `Latex-EMNLP/sections/appendix.tex:462`-`:468` 又以几乎相同的逻辑重复展开该论证。

影响：跨章节冗余削弱段落层级。主文已经像附录一样解释机制，附录又没有明显新增不同层面的分析，导致读者遇到同一论点两次。

### 中高：引言方法介绍与贡献列表挤在同一逻辑块中

证据：`Latex-EMNLP/sections/introduction.tex:28`-`:36` 从回答研究问题、定义 StructSynth、列出两个要求、介绍两个阶段，直接进入贡献列表。第一条 contribution（`:34`）又同时陈述 generation plan 主张、框架实例化、graph induction、conditional synthesis。

影响：段落主题句本身清楚，但该段落承载“方法总览”和“贡献声明”两个功能；贡献 bullet 过长，也让 skimming 时难以一眼看出贡献边界。

### 中：方法章节中实验结果表插入两个方法子模块之间，打断局部连贯

证据：`Latex-EMNLP/sections/method.tex:42` 刚结束图归纳流程，`Latex-EMNLP/sections/method.tex:87` 才进入 `Graph-Planned Conditional Synthesis`，中间 `Latex-EMNLP/sections/method.tex:44`-`:85` 是 downstream performance 结果表。

影响：即使该表可能在 PDF 中浮动，源码结构上它位于两个方法子阶段之间，会干扰“graph induction → conditional synthesis”的段落过渡。表格主题也属于实验结果，不属于方法解释。

### 中：实验数据集段落混合了两套评测对象

证据：`Latex-EMNLP/sections/experiments.tex:4` 先介绍六个真实世界数据集及任务、领域、LLM cutoff，然后同一段用 “Additionally” 引入三个 bnlearn ground-truth DAG benchmark。

影响：段首主题句说的是 six real-world tabular datasets，但段尾转到 structural recovery benchmark。两套评测服务不同实验目的，放在一段中降低 paragraph unity。

### 中：孤立的一句式段落造成实验叙事跳跃

证据：`Latex-EMNLP/sections/experiments.tex:155` 单独一句说明 “above gains generalize beyond the XGBoost evaluator...”，随后 `Latex-EMNLP/sections/experiments.tex:157` 进入 `Structural Fidelity under Ground-Truth Graphs`。

影响：这句话像 downstream model sensitivity 的结果摘要，但正文没有对应小节展开，且位于 ablation 和 structural fidelity 之间，过渡功能不足。

### 中低：附录综述段落过长，多个方法族被压进单段

证据：`Latex-EMNLP/sections/appendix.tex:26` 的 Conventional Structure Learning 段落覆盖 constraint-based、score-based、Markov equivalence、FCM、GIN 和 low-data limitation；`Latex-EMNLP/sections/appendix.tex:29` 的 LLM-based Structure Learning 段落覆盖 pairwise queries、BFS、iterative supervision、多个应用领域和本文动机。

影响：这些段落的首句能提示大主题，但不能帮助读者恢复内部论证层次。附录虽可更长，但仍应保持一个段落一个功能。

### 中低：核心口号重复频率偏高，应区分“锚定重复”和“解释重复”

证据：generation plan 的三要素 “order, conditioning context, and scope” 在摘要、图注、引言、结论中多次出现，例如 `Latex-EMNLP/sections/abstract.tex:3`、`Latex-EMNLP/sections/introduction.tex:7`、`:26`、`:28`、`:34`、`Latex-EMNLP/sections/conclusion.tex:3`。

影响：作为核心贡献短语，适度重复有利于记忆；但在相邻区域重复完整三元组时，会让段落显得在复述而非推进。尤其引言中可减少一次完整复述。

## 5. 可执行修改建议

1. 将 `experiments.tex:90` 拆成三个段落：第一段只解释 privacy-fidelity tension；第二段只报告 StructSynth 在 privacy/fidelity 上的位置；第三段解释为什么 pairwise fidelity 不等于 downstream utility。把 `Bayesian Sampler` 例子移到 ablation 段落之后，或改成 “as later confirmed by the Bayesian Sampler ablation” 并给出前置提示。
2. 精简主文的 privacy/fidelity 机制解释，把详细版本留在 `appendix.tex:462`-`:468`；主文可用 2-3 句总结并加 “We discuss this trade-off further in Appendix...”。这样主文推进结果，附录承担解释。
3. 拆分 `introduction.tex:28`-`:36`：先用一段介绍 StructSynth 的两阶段设计，再另起一段 “This paper makes two contributions.” 贡献列表中每个 bullet 只保留一个主谓结构，避免在第一条里同时塞入两个阶段的完整说明。
4. 将 `method.tex:44`-`:85` 的 downstream performance 表移动到 `experiments.tex` 的 Main Results 附近，最好紧邻首次引用 `Table~\ref{tab:results_comparison_performance}` 的 `experiments.tex:84`。方法章节中让 `method.tex:42` 后直接过渡到 `method.tex:87`。
5. 拆分 `experiments.tex:4`：第一段介绍六个真实数据集和下游任务；第二段以 “For structural recovery, we additionally use...” 开头介绍 Asia/Child/Insurance 与 SHD。
6. 处理 `experiments.tex:155` 的一句式段落：要么合并到 `Main Results` 作为最后一句，要么新增一个简短小节 `Sensitivity to Downstream Model Choice`，用 2-3 句说明表格在附录的位置和关键 takeaway。
7. 拆分附录长综述段落：`appendix.tex:26` 可按 constraint/score-based、FCM/GIN、low-data limitation 分段；`appendix.tex:29` 可按 pairwise LLM、BFS scaling、LLM+classical hybrid、本文定位分段。
8. 对重复口号做“首次完整、后续压缩”：摘要和引言保留完整 “generation order, conditioning context, and scope”；同一节后续可改成 “this generation-plan role” 或 “the graph-planned synthesis process”。

## 6. 独立性说明

本次审计未访问 `Audit/reports`，也未读取 `Audit/reports_codex` 中其他 Codex 报告；仅写入本报告文件。
