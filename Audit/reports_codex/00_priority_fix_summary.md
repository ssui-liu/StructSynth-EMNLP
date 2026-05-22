# StructSynth EMNLP 优先级修复清单

本文档基于 `Audit/reports_codex` 中 10 份独立审阅报告整理，目标是把当前论文中需要修复的问题按优先级去重、合并，并转化为可执行清单。这里不重新评价实验正确性，只汇总写作、结构、LaTeX、引用、合规和表达层面的修复项。

## 来源报告

| 编号 | 来源 |
|---|---|
| R01 | `01_level_0_1_global_narrative_section_structure.md` |
| R02 | `02_level_2_paragraph_coherence.md` |
| R03 | `03_level_3_sentence_clarity_style.md` |
| R04 | `04_level_4_word_precision.md` |
| R05 | `05_level_5_grammar_syntax.md` |
| R06 | `06_level_6_citations_references.md` |
| R07 | `07_level_7_tables_figures.md` |
| R08 | `08_level_8_math_notation_equations.md` |
| R09 | `09_level_9_latex_typesetting_formatting.md` |
| R10 | `10_level_10_emnlp_acl_requirements.md` |

## 优先级定义

| 优先级 | 含义 |
|---|---|
| P0 阻断项 | 可能直接影响匿名审稿、ACL/EMNLP 合规、引用/公式规范或最终编译验收；应先修。 |
| P1 高优先级 | 影响核心故事线、主要 claim、章节功能、读者信任或关键图表阅读路径；应在正文重写阶段修。 |
| P2 中优先级 | 影响可读性、可复现感、术语一致性、表格/图形质量和局部逻辑；应在第二轮修订中系统处理。 |
| P3 低优先级 | 语言、格式、单复数、搭配、局部 polish；应在最终通读和编译前扫清。 |

---

## P0 阻断项

### P0-1 匿名提交源码仍暴露作者身份

- 来源：R10
- 证据：`Latex-EMNLP/main.tex:93-103` 明文包含作者姓名、机构、邮箱；`main.tex:100` 包含 `\thanks{Corresponding author.}`。
- 风险：即使 `\usepackage[review]{acl}` 会匿名化 PDF 首页，提交源码或补充材料时仍可能破坏双盲匿名；还需检查 review PDF 是否残留 corresponding-author 脚注。
- 修复动作：为 review 版删除或条件编译真实 `\author{...}`、邮箱、机构和 `\thanks`；仅在 camera-ready 版恢复。
- 验收标准：匿名 PDF、源码包和补充材料中均无作者姓名、邮箱、机构、个人仓库或 corresponding-author 信息。

### P0-2 缺少 Ethics Statement 和 Responsible NLP checklist 支撑材料

- 来源：R10
- 证据：`main.tex` 仅输入 introduction、related work、method、experiments、conclusion、limitations；未发现 ethics、responsible checklist、impact statement 等章节或文件。
- 风险：EMNLP/ACL submission readiness 不足，尤其论文涉及 Adult、Compas、Anxiety、Obesity 等敏感或社会属性相关数据集。
- 修复动作：新增 `\section*{Ethics Statement}`；补充 Responsible NLP checklist 对应支撑内容。
- 验收标准：伦理声明至少覆盖数据来源/许可、PII/敏感属性、IRB/consent 是否适用、误用风险、偏见/公平性限制、商业 LLM API 数据治理、合成数据使用边界。

### P0-3 全文 93 个实际 citation 命令均为裸 `\cite{}`，不符合 ACL natbib 写法

- 来源：R06
- 证据：静态检查显示实际 citation 命令分布为 `\cite`: 93，正文未实际使用 `\citep` 或 `\citet`。
- 风险：直接违反 citation checklist；作者-年份引用语法可能不符合 ACL 风格。
- 修复动作：按语义区分替换：括号引用用 `\citep{...}`，作者作为句子主语时改写为 `\citet{...}`。
- 验收标准：正文和附录无裸 `\cite{}`；无双括号、citation-only sentence 或句号后引用。

### P0-4 参考文献库有大量未使用条目

- 来源：R06
- 证据：`references.bib` 共 211 个条目，唯一已引用 key 约 59 个，约 152 个看似未使用。
- 风险：违反 “every entry in references.bib is cited at least once” 的清单要求，也增加维护噪音。
- 修复动作：删除或移出未使用 bib 条目；确实需要保留的条目必须在正文中有语义支撑的引用。
- 验收标准：`references.bib` 中所有条目都被实际引用；不使用 `\nocite{*}` 掩盖 orphan entries。

### P0-5 展示公式自动编号但没有引用

- 来源：R08
- 证据：全文有 17 个 `equation` 和 1 个 `align` 环境，但未发现 `\eqref{}`、`Eq.~(...)` 或 `Equation~(...)` 引用。
- 风险：违反公式引用规范，PDF 会出现无用途编号。
- 修复动作：不需要引用的公式改为 `equation*`、`\[...\]` 或 `align*`；保留少数关键编号公式时加 `\label{eq:...}` 并正文引用。
- 验收标准：无编号但未引用公式；引用格式统一。

### P0-6 最终 PDF 编译和视觉验收尚未完成

- 来源：R07、R09
- 证据：审阅环境缺少 `latexmk` / `pdflatex` / `bibtex` / `tectonic`，表格溢出、页数、float 位置、图中文字大小、overfull boxes 未被实际 PDF 验证。
- 风险：多处 `\resizebox`、`\small`、`figure*`、`table*`、`[h]` 可能在双栏 ACL 模板中造成不可读或页数问题。
- 修复动作：完成结构、引用、公式和表格修改后，在可用 TeX 工具链环境中完整编译。
- 验收标准：无 undefined refs/citations、无明显 overfull boxes、主文页数合规、图表不越界、字体不低于可读阈值、float 不集中堆叠。

---

## P1 高优先级

### P1-1 摘要、引言和结论中的强 claim 需要数值化和限定

- 来源：R01、R03、R04
- 证据：`abstract.tex:3`、`introduction.tex:35`、`conclusion.tex:4` 使用 “state-of-the-art downstream utility and privacy preservation”“competitive statistical fidelity”“especially in low-data scenarios”等表述。
- 问题：证据存在但表述过宽。privacy 若依据 average rank，应写成 “best average privacy rank”；fidelity 平均排名并不突出；样本量 sweep 主要在 Adult 上，不应暗示所有数据集都验证了低数据变化。
- 修复动作：用关键数字替换形容词，例如 average downstream score 75.01、+1.65 over CLLM、best privacy average rank 1.50、fidelity avg. rank 7.92，并明确 `n=100` 和 Adult sample-size sweep 的范围。
- 验收标准：abstract、contribution 和 conclusion 中每个主要结果 claim 都可在表/图中直接找到对应证据。

### P1-2 Abstract 缺少具体量化结果，且 `LLM` 首次出现未展开

- 来源：R01、R03
- 证据：`abstract.tex:3` 含 `LLM` 与主要结果句，但无具体数字。
- 修复动作：首次写作 “large language model (LLM)”；加入 1-2 个最关键定量结果。
- 验收标准：摘要保留 Background -> Problem -> Method -> Results -> Significance 结构，含至少一个具体数值，且不引入未定义缩写。

### P1-3 Introduction 没有充分预告后续实验地图

- 来源：R01、R02
- 证据：`introduction.tex:32-35` 贡献列表较短，未预告 ground-truth DAG/SHD、sample-size sweep、LLM backend、downstream model sensitivity 等分析。
- 问题：读者到 experiments 才遇到多项未 foreshadow 的实验，显得像额外堆叠。
- 修复动作：贡献后加简短 roadmap，明确六数据集主实验、ablation、structure recovery、sample-size、downstream learner、LLM backend。
- 验收标准：每个实验模块都能回到 introduction 中的某个 claim 或 roadmap 句。

### P1-4 Introduction 的方法介绍和贡献列表挤在同一逻辑块，贡献边界偏宽

- 来源：R01、R02、R03
- 证据：`introduction.tex:28-36` 同时回答 research question、定义 StructSynth、介绍两阶段、列贡献；第一条 contribution 同时包含 generation plan、graph induction、conditional synthesis。
- 修复动作：拆成两个段落：先介绍两阶段设计，再列贡献；贡献项改为 3-4 条，每条只保留一个可验证主张。
- 验收标准：贡献项具体、可证伪，并能映射到方法或实验小节。

### P1-5 主结果表放在 Method 源文件中，破坏章节功能和 float 路径

- 来源：R01、R02、R07、R09
- 证据：`method.tex:44-85` 放置 `tab:results_comparison_performance`，但首次解释/引用在 `experiments.tex:84`；`method.tex:109` 还有迁移注释。
- 风险：方法两个阶段之间被实验结果表打断；PDF float 也可能跨章节提前出现。
- 修复动作：将该表整体移到 `experiments.tex` 的 main results / downstream performance 小节附近，保留原 label。
- 验收标准：Method 中只解释方法；结果表靠近首次引用和结果讨论。

### P1-6 Pipeline figure 放在 Related Work 中，章节功能错位

- 来源：R01、R07
- 证据：`related_work.tex:4-9` 放置 `fig:pipeline`，首次正文引用在 `method.tex:6`。
- 问题：pipeline 是方法总览，不应由 Related Work 承担框架说明功能。
- 修复动作：将 `fig:pipeline` 移到 Method 开头或 Introduction 末尾。
- 验收标准：Related Work 只承担文献定位；pipeline 图靠近方法总览首次引用。

### P1-7 Experiments 的 privacy/fidelity 段落过载，并提前使用未定义 ablation 概念

- 来源：R01、R02、R03、R04
- 证据：`experiments.tex:90` 同时解释 privacy-fidelity tension、多个 baseline、StructSynth 位置、Bayesian Sampler ablation、pairwise vs conditional dependency；`Bayesian Sampler` 到 `experiments.tex:105` 才正式定义。
- 修复动作：拆成多个段落；先报告 observation，再解释 privacy/fidelity tension；Bayesian Sampler 例子移到 ablation 后，或用 “as later confirmed...” 明确前置。
- 验收标准：主结果段不要求读者提前理解后文 ablation；观察和解释分开。

### P1-8 主文和附录重复展开同一 privacy/fidelity 机制解释

- 来源：R02
- 证据：`experiments.tex:90` 与 `appendix.tex:462-468` 逻辑高度重复。
- 修复动作：主文保留 2-3 句 takeaway；详细机制解释留在附录，并加交叉引用。
- 验收标准：主文推进叙事，附录补充细节，不重复同一论证。

### P1-9 Method 对附录依赖过重，主文最小可复现信息不足

- 来源：R01、R10
- 证据：association scores、prompt templates、algorithm、DAG 选择理由等大量关键细节依赖附录。
- 修复动作：Method 中加入最小可复现摘要表：stage、input、operation、output、appendix pointer；正文保留 association scores、cycle resolution、generation handling 的边界说明。
- 验收标准：不读附录也能理解 StructSynth 的核心输入、输出和每一步决策。

### P1-10 “非因果依赖图”定位与 causal wording 冲突

- 来源：R01、R03、R04、R08
- 证据：虽然 `introduction.tex:30` 脚注说明 DAG 不是 ground-truth causal claim，但附录/prompt 中仍有 `caused`、`effects`、`true parent nodes`、`valid causal path` 等表达。
- 风险：审稿人可能质疑论文是否在暗示 causal discovery。
- 修复动作：一般方法和 prompt 中统一改为 dependency / conditioning / predecessor / successor；仅在 ground-truth causal benchmark 语境保留 causal，并说明其作为 dependency proxy。
- 验收标准：全稿能清楚区分 “dependency graph as generation plan” 与 “causal graph”。

### P1-11 表格压缩和主文宽表可读性风险较高

- 来源：R07、R09
- 证据：`method.tex:48-49`、`experiments.tex:22-23` 同时使用 `\resizebox{\textwidth}{!}` 和 `\small`；`experiments.tex:110/114` 使用 `\small` 与 `\tabcolsep=1mm`。
- 修复动作：优先重排表结构，而不是继续压缩：拆表、缩短列名、使用 `tabular*` / `siunitx`、把次要结果移入附录。
- 验收标准：最终 PDF 表格字体可读，无越界，列对齐稳定。

### P1-12 Ablation 表和 downstream sensitivity 表不符合 booktabs/no vertical lines 风格

- 来源：R07
- 证据：`experiments.tex:115-129`、`appendix.tex:360-388` 使用 `ll|ccc`、`\hline`。
- 修复动作：去掉竖线，用 `\toprule`、`\midrule`、`\bottomrule`、`\cmidrule`。
- 验收标准：全文表格风格统一，符合 ACL/booktabs 惯例。

### P1-13 关键 caption 自包含性不足，缺少 takeaway

- 来源：R07
- 证据：`tab:ablation_study` caption 仅为 “Ablation Study on Adult Datasets.”；`fig:llm_compare`、`fig:structure`、`tab:dataset_summary` caption 未充分说明指标方向、符号含义或核心发现。
- 修复动作：扩写 caption，至少包含指标方向/单位、bold/underline 规则、关键结论。
- 验收标准：读者只读 caption 也能理解表/图要证明什么。

### P1-14 数据隐私、敏感属性、公平性和误用风险缺少正文说明

- 来源：R10
- 证据：Adult/Compas/health 类数据集中含敏感或近似敏感字段；prompt 示例出现 `Sex`、`Race`、`Native country`，但正文只用 privacy metric 间接覆盖。
- 修复动作：在 Ethics 或 Limitations 中说明敏感属性处理、合成数据误用边界、偏见放大、公平性限制和高风险决策禁用场景。
- 验收标准：Responsible NLP checklist 中相关 “yes/no” 均有论文段落支撑。

### P1-15 复现性披露不足：API、代码、版本和计算成本不完整

- 来源：R10
- 证据：已有 model name、temperature、seeds、hyperparameters、token usage；但缺 API snapshot/调用日期、依赖版本、代码发布承诺、硬件、wall-clock time、API 成本、深度基线训练成本。
- 修复动作：增加 reproducibility paragraph/table，列 API provider/model snapshot/call date、软件版本、数据预处理、baseline 配置、匿名代码或发布计划、硬件和成本。
- 验收标准：商业 LLM API 和默认库配置的漂移风险被显式记录。

---

## P2 中优先级

### P2-1 Related Work 的 positioning 句不够鲜明

- 来源：R01
- 问题：按主题组织良好，但部分段落更像压缩综述，段尾没有稳定回答“已有工作缺什么，StructSynth 如何切入”。
- 修复动作：每个主题段结尾加定位句，突出 low-data LLM synthesis 下 graph-as-generation-plan 的差异。

### P2-2 Conclusion 没有充分回扣真实场景问题

- 来源：R01
- 问题：结尾停留在方法方向，没有回到 introduction 中 healthcare、finance、education 等低数据/敏感场景。
- 修复动作：最后补一句现实影响，同时避免泛化成“解决所有表格数据问题”。

### P2-3 实验数据集段落混合真实数据集和 bnlearn ground-truth DAG benchmark

- 来源：R02
- 证据：`experiments.tex:4` 同段介绍六个真实数据集和 Asia/Child/Insurance 结构恢复 benchmark。
- 修复动作：拆成两个段落：主数据集；结构恢复 benchmark。

### P2-4 `experiments.tex:155` 一句式段落造成叙事跳跃

- 来源：R02
- 问题：downstream model sensitivity 的一句摘要夹在 ablation 和 structural fidelity 之间。
- 修复动作：合并到 Main Results 末尾，或新增简短 `Sensitivity to Downstream Model Choice` 小节。

### P2-5 附录 critical information 和长综述段落需要分层

- 来源：R01、R02
- 问题：DAG rationale、algorithm、prompt、额外讨论、扩展相关工作较深；`appendix.tex:26`、`:29` 段落过长。
- 修复动作：附录开头加导航表；拆分长综述段落；主文只保留必要最小信息，附录承接细节。

### P2-6 核心口号和隐喻重复较多

- 来源：R02、R04
- 问题：`generation order, conditioning context, and scope` 以及 `blueprint/plan` 多处重复。
- 修复动作：首次完整定义，后续改成 `generation plan` 或 `graph-planned synthesis`；减少 `blueprint` 与 `plan` 并列替换。

### P2-7 句子过长，尤其在实验设置、消融、附录机制解释中

- 来源：R03、R05
- 证据：`experiments.tex:11`、`:105`、`:159`，`appendix.tex:26`、`:353`、`:395`、`:456` 等。
- 修复动作：每句只承载一个主要判断；指标定义、variant 列表、数据集/模型枚举拆成多句或列表。

### P2-8 结果解释中的强动词和强化词需要降调

- 来源：R03、R04
- 证据：`confirms`、`demonstrating`、`conclusively demonstrating`、`powerful evidence`、`will naturally align`、`remarkable` 等。
- 修复动作：除非补统计检验或因果隔离，否则改为 `supports`、`suggests`、`shows`、`provides evidence`。

### P2-9 方法描述中被动语态和名词化偏多

- 来源：R03
- 证据：`method.tex:12`、`:30`、`:38`、`:90` 等。
- 修复动作：改为 `We represent...`、`StructSynth queries...`、`StructSynth generates...`；`utilize` 改为 `use`。

### P2-10 `This/These` 指代和部分比较句不够明确

- 来源：R03
- 证据：`experiments.tex:4`、`:84`、`:90`，`appendix.tex:466`、`:483`。
- 修复动作：改为 `These benchmark graphs`、`This average score`、`This mismatch`、`The fidelity-utility discrepancy` 等。

### P2-11 平行结构不稳定

- 来源：R03、R05
- 证据：`introduction.tex:24` 的三项并列；`experiments.tex:105` 的消融列表；`appendix.tex:183` 的 `tasks, number of features, and domain`。
- 修复动作：统一语法层级，例如 `what to generate, when to generate it, and which context to condition on`。

### P2-12 核心术语体系需要统一

- 来源：R04、R09
- 问题：`dependency graph`、`DAG`、`dependency structure`、`learned graph`、`blueprint`、`generation plan` 频繁切换；`StructSynth`、`CLLM` 格式也不统一。
- 修复动作：建立术语/宏：`\method`、`\cllm`；图对象统一 `dependency graph (DAG)`，功能统一 `generation plan`。

### P2-13 指标名称和方向需要统一

- 来源：R04、R09
- 问题：`Downstream Model Performance`、`downstream utility`、`AUC`、`Fidelity`、`Privacy`、`Privacy Risk`、`privacy preservation` 混用。
- 修复动作：首次定义正式指标名，后文固定简称；区分 raw score 与 average rank；说明 lower/better 或 closer-to-0.5 规则。

### P2-14 过度词、宣传化或口语化表达需要降调

- 来源：R04
- 例子：`data-hungry`、`wins`、`top-tier`、`outsized returns`、`weakest link`、`substantial(ly)`、`robust`、`significant(ly)`、`leverage/utilize`。
- 修复动作：改为学术中性表达；能量化的地方用数字替代形容词。

### P2-15 已引用 bib 条目元数据不完整

- 来源：R06
- 例子：部分 ICML/OpenReview/arXiv/NeurIPS 条目缺 pages、URL、DOI、eprint 或出版版本信息。
- 修复动作：补全已引用条目的 venue、pages、publisher、URL/DOI、arXiv eprint；有正式版本则优先引用正式版本。

### P2-16 多文献排序和 FCI 引用不一致

- 来源：R06
- 证据：`appendix.tex:29` 医学领域引用年份顺序不一致；`appendix.tex:481` FCI 使用 `spirtes2000causation`，与 `appendix.tex:26` 的 `spirtes1995causal` 不一致。
- 修复动作：统一多文献排序规则；FCI 引用使用更具体且前后一致的来源。

### P2-17 关键图表 float 位置需要靠近首次提及

- 来源：R07
- 证据：`fig:shd`、`fig:influence_n`、`fig:llm_compare` 定义位置早于对应详细讨论，可能造成图表堆叠。
- 修复动作：分别移到对应小节首次提及前后，优先 `[t]` 或 `[tb]`，谨慎使用 `[h]`。

### P2-18 PNG 图和拼接图需要提升矢量化与面板可引用性

- 来源：R07
- 证据：`intro2.png`、`pipeline.png`、`collage_3x2.png` 为 PNG；Asia collage 没有 LaTeX subfigure label。
- 修复动作：尽量导出 PDF；collage 拆成 `(a)`-`(f)` subfigures 或在图内明确标注并逐面板引用。

### P2-19 表格数字对齐和表格风格可进一步统一

- 来源：R07、R09
- 问题：多数手写表格使用普通 `c` 列；`siunitx` 已配置但未系统使用；hyperparameter 表有连续 `\midrule`。
- 修复动作：数值列改用 `S` 列；统一小数位、`\pm`、rank 和百分比格式。

### P2-20 数学符号主文、算法和附录之间不一致

- 来源：R08
- 证据：主文用 `\mathbf{X}_{\mathtt{train}}`、`\mathbf{A}`、`\tilde{\mathbf{x}}`；算法中变成 `X_{\mathtt{train}}`、`A`、`\tilde{x}`。
- 修复动作：建立全局符号表；矩阵、向量、集合、单个属性使用统一风格。

### P2-21 集合样式、符号复用和下标风格需要整理

- 来源：R08
- 问题：`V` 同时像节点集又与 Cramér's V 接近；`r` 同时表示 Pearson 相关和列联表维度；`\mathtt{train}` 与 `\text{train}` 混用；`\pi_{\mathtt{generate}}` 与 `\pi_{\mathtt{generation}}` 混用。
- 修复动作：集合改 `\mathcal{A}`、`\mathcal{V}`、`\mathcal{E}`；Pearson 用 `\rho`，列联表用 `R \times C`；统一 split 下标和 prompt 符号。

### P2-22 公式排版、标点和长公式有风险

- 来源：R08
- 证据：部分公式缺句末标点；`method.tex:97`、`:105`、`appendix.tex:251`、`:274-278` 可能双栏溢出；函数名如 `\mathtt{concat}`、`NN` 间距不自然。
- 修复动作：补标点；长公式用 `aligned`/`split`；函数名用 `\operatorname{...}` 或 `\DeclareMathOperator`。

### P2-23 附录手动间距、小字号和 label 约定需要清理

- 来源：R09
- 证据：算法和 prompt boxes 中有多处 `\vspace`、`\hspace`、`\small`；同一 section 同时有 `sec:` 和 `app:` label；存在 `prompt:`、`box:` 自定义前缀。
- 修复动作：建立统一 prompt box 环境；减少散落 spacing hacks；统一 label prefix 约定。

---

## P3 低优先级

### P3-1 标题、单复数和术语大小写小修

- 来源：R04、R05
- 具体项：
  - `Related Works` -> `Related Work`
  - `Experimental Setups` -> `Experimental Setup`
  - `Ablation Study on Adult Datasets` -> `Ablation study on the Adult dataset`
  - `Machine Learning (ML)` 若非专名，统一小写 `machine learning`
  - `Peter--Clark` 与 `Peter-Clark` 统一

### P3-2 `post LLM knowledge cutoff` 表达不自然

- 来源：R04、R05
- 修复动作：改为 `after the LLM knowledge cutoff`，或标题式表达 `post-LLM-knowledge-cutoff datasets`。

### P3-3 Prompt 示例中 `Rational:` 词形错误

- 来源：R05
- 证据：`appendix.tex:522`、`:525`、`:528`、`:531`。
- 修复动作：全部改为 `Rationale:`。

### P3-4 个别并列和分词结构可更顺

- 来源：R05
- 例子：
  - `They differ in tasks, number of features, and domain.` -> `They differ in task type, feature count, and domain.`
  - SMOTE 句中 `addressing class imbalance but limited to...` 改为 `addressing ... while remaining limited to...`

### P3-5 介词和 caption 短语小修

- 来源：R04
- 例子：
  - `Comparison of Models on Downstream Model Performance` -> `Comparison of models for downstream performance`
  - `Ablation Study on Adult Datasets` -> `Ablation study on the Adult dataset`

### P3-6 低信息动词和 filler 扫描

- 来源：R03、R04
- 修复动作：大多数 `utilize/utilized` -> `use/used`；删减 `It is important to...`、`A key observation is...`、`More importantly` 等可直接进入主语和动词的表达。

### P3-7 重复口号局部压缩

- 来源：R02
- 修复动作：摘要和 introduction 保留完整三元组，后文改用 `this generation-plan role` 或 `graph-planned synthesis`。

---

## 建议执行顺序

1. **先修 P0 合规层**：匿名源码、ethics/checklist、citation 命令、bib 清理、公式编号。
2. **再修 P1 主线层**：摘要/贡献/结论 claim 数值化，重排结果表和 pipeline 图，改 introduction roadmap，处理 causal/dependency 边界。
3. **随后修 P1/P2 图表和复现层**：表格 booktabs、caption、float 位置、方法最小可复现摘要、API/版本/计算成本。
4. **再做 P2 语言和符号一致性**：术语宏、指标词表、数学符号表、长句拆分、hedging 降调。
5. **最后 P3 全文 polish + 编译验收**：单复数、冠词、词形、介词、spacing hacks、PDF 页检。

## 汇总性验收清单

- [ ] 匿名 review PDF、源码和补充材料均无身份暴露。
- [ ] 有 Ethics Statement 和 Responsible NLP checklist 支撑内容。
- [ ] 全文无裸 `\cite{}`，无未使用 bib 条目，无 unresolved citations。
- [ ] 无未引用编号公式，符号风格主文/算法/附录一致。
- [ ] Abstract 含展开的 LLM 和至少一个具体量化结果。
- [ ] Introduction 有清楚 roadmap，每个实验都被提前动机化。
- [ ] Method 中不夹主结果表；pipeline 图放在方法总览附近。
- [ ] Privacy/fidelity 相关 claim 区分 score、rank、pairwise fidelity 和 downstream utility。
- [ ] 非因果 dependency graph 与 causal benchmark 语言边界清楚。
- [ ] 主文大表不依赖过度压缩；booktabs 风格统一；caption 可自解释。
- [ ] PNG/拼接图在可行处转为 PDF 或明确子图标签。
- [ ] 最终 PDF 编译无引用/标签错误、无明显版式溢出、页数符合 EMNLP 要求。
