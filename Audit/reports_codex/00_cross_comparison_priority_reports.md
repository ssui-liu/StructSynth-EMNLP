# StructSynth EMNLP 优先级清单交叉对比分析报告

本文档综合对比以下两份优先级修复清单：

- `Audit/reports/00_优先级修复清单.md`
- `Audit/reports_codex/00_priority_fix_summary.md`

目标不是简单合并两份清单，而是识别二者的共识、差异、互补盲区与优先级冲突，并给出一个更稳健的综合修复顺序。

## 1. 总体结论

两份清单在核心方向上高度一致：当前论文最需要优先处理的是 EMNLP/ACL 合规、abstract/claim 数值化、引用与 bib、公式编号、实验叙事连贯性、术语一致性、表格排版，以及 ethics/reproducibility。

主要差异在于：

- `Audit/reports` 的清单更像精细执行单，列出了 52 个具体修复点，很多问题可直接转化为单行修改。
- `Audit/reports_codex` 的清单更像系统风险图，覆盖了匿名提交、裸 `\cite`、结果表/框架图位置、causal wording、caption 自解释、最终 PDF 编译等更高层的提交风险。
- 两份报告对若干问题的优先级不同。例如 abstract 缺少量化结果在 `Audit/reports` 中列为 P0，而在 `reports_codex` 中列为 P1；计算成本和代码发布在 `Audit/reports` 中是 P0，而在 `reports_codex` 中并入复现性 P1。

综合判断：应采用 `reports_codex` 的合规风险作为 P0 底座，同时吸收 `Audit/reports` 中更具体的局部修复项作为执行细则。

## 2. 结构对比

| 维度 | `Audit/reports` 清单 | `reports_codex` 清单 | 交叉判断 |
|---|---|---|---|
| 总条目数 | 52 项：P0 7、P1 10、P2 15、P3 20 | 51 项：P0 6、P1 15、P2 23、P3 7 | 数量接近，但粒度不同。前者更细，后者更系统。 |
| P0 口径 | 偏向审稿评分、伦理、计算成本、abstract、bib 和关键术语冲突 | 偏向匿名、ACL/EMNLP 合规、citation、bib、公式编号、编译验收 | 建议以 `reports_codex` 的 P0 作为提交阻断标准。 |
| P1 口径 | 偏向公式标点/编号、符号一致、语法硬伤、实验预告、段落拆分、booktabs | 偏向主线 claim、章节结构、图表位置、causal wording、可复现性、表格可读性 | 两者互补；合并后 P1 应覆盖正文重写和图表结构调整。 |
| P2 口径 | 偏向词汇术语、句子风格、引用元数据、格式一致性 | 偏向段落结构、术语系统、图表质量、数学符号、附录分层 | `Audit/reports` 可作为具体替换表，`reports_codex` 可作为分组依据。 |
| P3 口径 | 很细，包含 20 个局部 polish 点 | 较粗，只保留 7 类最终 polish | 建议保留 `Audit/reports` 的 P3 细项，作为最终扫尾清单。 |

## 3. 两份清单的高置信共识

这些问题在两份清单中都出现，或虽命名不同但指向同一修复簇。建议视为必须处理。

| 综合问题 | `Audit/reports` 对应项 | `reports_codex` 对应项 | 建议综合优先级 |
|---|---|---|---|
| Abstract 缺少量化结果，主要 claim 过泛 | P0-1、P3-4 | P1-1、P1-2 | P1，若时间很紧则提前到 P0 批处理 |
| Ethics / Responsible NLP / 社会风险不足 | P0-2、P2-15、P3-20 | P0-2、P1-14 | P0 |
| 计算成本、代码发布、复现性披露不足 | P0-3、P0-4 | P1-15 | P0/P1 之间；提交前必须解决 |
| references.bib 未使用条目过多 | P0-6 | P0-4 | P0 |
| 已发表版本、bib 元数据和 venue/作者格式需核查 | P0-7、P2-9、P2-10 | P2-15 | P2，个别关键条目可升 P1 |
| 公式编号但未引用 | P1-2 | P0-5 | P0 |
| 公式标点和数学符号一致性 | P1-1、P1-3、P1-4、P3-18 | P2-20、P2-21、P2-22 | P1/P2 |
| Introduction 缺少后续实验预告 | P1-6 | P1-3 | P1 |
| Privacy/fidelity 段落过载 | P1-8、P1-9 | P1-7、P1-8 | P1 |
| 表格 booktabs 风格不统一 | P1-10 | P1-12 | P1 |
| 术语和方法名格式不一致 | P2-1、P2-2、P2-3、P2-13、P3-12、P3-13 | P2-12、P2-13、P3-1 | P2 |
| 长句、被动语态、This 指代和平行结构问题 | P2-5、P2-6、P2-7、P2-8 | P2-7、P2-9、P2-10、P2-11 | P2 |
| PNG 非矢量图 | P3-10 | P2-18 | P2/P3 |
| Conclusion 需要回扣现实问题 | P1-7、P3-2 | P2-2 | P2 |
| 多文献排序和 FCI 引用不一致 | P3-14、P3-15 | P2-16 | P2 |

## 4. `Audit/reports` 独有或更具体的问题

这些问题在 `reports_codex` 中没有单独列出，或只是被更宽泛地覆盖。建议不要丢掉，因为它们多是高性价比局部修复。

| 问题 | 原优先级 | 是否建议保留 | 综合处理建议 |
|---|---|---|---|
| `Structural Fidelity` 小节标题与 `Statistical Fidelity` 指标名冲突 | P0-5 | 保留 | 升为 P1。改为 `Structure Recovery under Ground-Truth Graphs`，可快速降低误解风险。 |
| `qian2023synthcity` 已发表版本需更新 | P0-7 | 保留但需核验 | 归入 bib 元数据核查。最终修改前核查该条和其他 arXiv/preprint 是否已有正式版本。 |
| `"perform notably weaker"` 语法错误 | P1-5 | 保留 | 作为 P2/P3 语言扫尾中的硬错误优先修，改为 `perform notably worse` 或 `are notably weaker`。 |
| `association cues/scores/correlation scores` 三种说法不一致 | P2-2 | 保留 | 并入术语表；建议统一为 `association scores`，ablation 改为 `No-Association Score`。 |
| `structure discovery/structure learning/graph induction` 不一致 | P2-3 | 保留 | 并入术语表；阶段名保留 `Evidence-Grounded Graph Induction`，一般描述用 `graph induction` 或 `structure discovery`。 |
| Introduction 与 Related Work 中 GraDe/SPADA 描述重复 | P2-4 | 保留 | Introduction 只保留高层动机，细节移到 Related Work。 |
| Method 中 DAG 设计理由完全在 appendix | P2-11 | 保留 | 与 `reports_codex` 的“Method 最小可复现摘要”合并处理，在 Method 增加 2-3 句 `Why a DAG`。 |
| `BFS` 首次使用未展开 | P3-6 | 保留 | 最终 polish 时修。 |
| `method.tex L94` 一句引入 3 个新符号 | P3-7 | 保留 | 与数学符号统一和长句拆分一起修。 |
| appendix 中 17 个 orphan labels | P3-11 | 保留但需复查 | 与 `reports_codex` 的 label 约定清理合并。 |
| `most pronounced` 连续使用、`synergy is vital`、`outsized returns` | P3-3、P3-16、P3-17 | 保留 | 并入降调和学术语体 polish。 |
| Oxford comma 缺失 | P3-19 | 可保留 | 最终语言扫尾。 |

## 5. `reports_codex` 独有或更系统的问题

这些问题在 `Audit/reports` 中缺失或优先级较低，但对提交质量影响较大。

| 问题 | 原优先级 | 是否建议纳入最终清单 | 综合处理建议 |
|---|---|---|---|
| review 源码暴露作者、单位、邮箱和 corresponding-author 信息 | P0-1 | 必须纳入 | 作为最高优先级 P0。 |
| 全文 93 个 citation 命令均为裸 `\cite{}` | P0-3 | 必须纳入 | 比单纯 bib 清理更阻断，应在 citation pass 中优先处理。 |
| 最终 PDF 编译和视觉验收尚未完成 | P0-6 | 必须纳入 | 作为最终提交前 P0 gate。 |
| 主结果表放在 Method 源文件中 | P1-5 | 必须纳入 | 同时影响章节功能和 float 位置，应在正文重排时修。 |
| Pipeline figure 放在 Related Work 中 | P1-6 | 必须纳入 | 移到 Method 开头或 Introduction 末尾。 |
| Introduction 方法介绍和贡献列表挤在同一逻辑块 | P1-4 | 纳入 | 与 `Audit/reports` 的实验预告问题合并，重写 contribution block。 |
| 非因果 dependency graph 与 causal wording 冲突 | P1-10 | 必须纳入 | 这是 reviewer 可能抓住的概念边界问题。 |
| 表格过度压缩，宽表可读性风险 | P1-11 | 必须纳入 | 与 booktabs 一起做表格 pass。 |
| caption 缺少 takeaway，自包含性不足 | P1-13 | 纳入 | 与图表 pass 一起处理。 |
| Method 对附录依赖过重，主文最小可复现信息不足 | P1-9 | 纳入 | 与 `Why a DAG` 和复现性披露合并。 |
| 数据集段落混合真实数据与 bnlearn benchmark | P2-3 | 纳入 | 属于低成本段落结构修复。 |
| `experiments.tex:155` 单句段落 | P2-4 | 纳入 | `Audit/reports` 也列为 P3-9；综合升为 P2。 |
| PNG 拼接图缺少子图标签与逐面板引用 | P2-18 | 纳入 | 比单纯“PNG 非矢量”更具体，应补充到图表清单。 |
| 附录手动间距、小字号和 prompt box 环境分散 | P2-23 | 纳入 | 作为最终 LaTeX hygiene，不必早于主文修订。 |

## 6. 优先级冲突与综合裁决

| 议题 | `Audit/reports` 判断 | `reports_codex` 判断 | 综合裁决 |
|---|---|---|---|
| Abstract 缺少量化结果 | P0 | P1 | 作为 P1 主线问题处理，但应和 P0 合规 pass 同轮修，因为修改成本低、收益高。 |
| 计算成本与代码发布 | P0 | 并入 P1 复现性 | 综合定为 P0/P1 边界。若目标是 EMNLP 提交，必须在提交前补齐。 |
| Ethics / social risk | P0/P2/P3 分散 | P0/P1 | 综合定为 P0，并合并 social risk、dataset license、commercial API 数据治理。 |
| 公式编号未引用 | P1 | P0 | 综合定为 P0，因为这是可被 PDF 直接观察到的格式问题。 |
| 公式标点 | P1 | P2 | 综合定为 P2，但可在处理公式编号时顺手修。 |
| `Structural Fidelity` 标题冲突 | P0 | 未单列 | 综合定为 P1。不是提交阻断，但非常容易误导读者。 |
| `qian2023synthcity` 发表版本 | P0 | 泛化为 bib 元数据 P2 | 综合定为 P2，除非该引用出现在核心 baseline 描述中且格式明显错误。 |
| Conclusion future work | P1 | 现实场景回扣 P2 | 综合定为 P2；独立 Limitations 已存在，不必强制在 Conclusion 里重复 limitations。 |
| PNG 图 | P3 | P2 | 综合定为 P2/P3；若图中文字密集或需印刷质量，升 P2。 |
| orphan labels | P3 | label 策略 P2 | 综合定为 P3，除非编译出现 warning 或引用混乱。 |

## 7. 建议采用的综合修复清单

### P0：提交阻断与合规 gate

1. 匿名化 review 源码、PDF 和补充材料，移除作者、机构、邮箱、corresponding-author 信息。
2. 新增 Ethics Statement，并准备 Responsible NLP checklist 支撑材料。
3. 补充计算成本、API 成本、wall-clock time、硬件、依赖版本、代码/数据发布承诺。
4. 全文 `\cite{}` 改为 `\citep{}` / `\citet{}`，并检查 citation placement。
5. 清理 `references.bib` 未使用条目，补全核心已引用条目元数据。
6. 处理所有未引用编号公式：取消编号或加 label/ref。
7. 完成最终 PDF 编译和视觉验收。

### P1：核心叙事、claim 和章节结构

1. 重写 abstract 结果句，加入具体数字，首次展开 `LLM`。
2. 数值化并限定 abstract、introduction、conclusion 中的 `state-of-the-art`、`privacy preservation`、`competitive fidelity`、`low-data` claim。
3. 重写 Introduction contribution block：拆开方法介绍和贡献列表，加入后续实验 roadmap。
4. 将主结果表从 Method 移到 Experiments 首次引用附近。
5. 将 pipeline figure 从 Related Work 移到 Method 开头或 Introduction 末尾。
6. 将 `Structural Fidelity under Ground-Truth Graphs` 改为 `Structure Recovery under Ground-Truth Graphs` 或类似标题。
7. 拆分 privacy/fidelity 段落，避免 Bayesian Sampler 在定义前承担关键解释。
8. 在 Method 中补最小可复现摘要和 `Why a DAG` 简述。
9. 统一非因果 dependency graph 语言，移除一般方法/prompt 中的 causal overclaim。
10. 修 ablation 表和 downstream sensitivity 表的 booktabs/no vertical lines。
11. 处理主文宽表压缩、caption takeaway 和关键 float 位置。

### P2：一致性、可读性和技术排版

1. 建立术语表：`dependency graph (DAG)`、`generation plan`、`association scores`、`graph induction`、正式指标名和简称。
2. 建立 LaTeX 宏：`\method`、`\cllm` 等，统一 StructSynth、CLLM、bnlearn、Peter--Clark 格式。
3. 统一数学符号：矩阵/向量/集合粗体或 calligraphic 风格、dataset 下标、prompt 符号、Pearson `r` 与列联表维度。
4. 拆长句，尤其是 Introduction、Method、Experiments ablation list 和 Appendix 机制解释。
5. 将强动词和宣传化词汇降调：`confirms`、`conclusively demonstrating`、`powerful evidence`、`wins`、`outsized returns`、`synergy is vital`。
6. 修复被动语态、`This/These` 指代、平行结构和局部语法硬伤。
7. 拆分 datasets 段落，单独介绍真实数据集与 bnlearn structure benchmark。
8. 处理 `experiments.tex:155` 单句段落。
9. 补全图表矢量化与子图标签，尤其 `collage_3x2.png`。
10. 整理附录导航、长综述段落、prompt box 环境、label 约定。

### P3：最终 polish

1. `Related Works` -> `Related Work`；`Experimental Setups` -> `Experimental Setup`。
2. `Rational:` -> `Rationale:`。
3. `post LLM knowledge cutoff` -> `after the LLM knowledge cutoff` 或 `post-LLM-knowledge-cutoff datasets`。
4. 首次展开 `BFS`。
5. 修 `perform notably weaker`、Oxford comma、时态小漂移。
6. 替换重复词：`most pronounced`、`substantial(ly)`、`state-of-the-art downstream utility`。
7. 清理 orphan labels、散落 `\vspace` / `\hspace`、低信息 `utilize` / filler。

## 8. 推荐执行节奏

### 第一轮：合规和编译风险

先处理匿名、ethics/checklist、citation、bib、公式编号。这一轮不需要大改正文，但能消除最容易被格式或提交系统卡住的问题。

### 第二轮：摘要、引言、方法和实验主线

重写 abstract 和 contribution block，移动结果表与 pipeline 图，拆 privacy/fidelity 段落，补 Method 最小可复现信息和 DAG rationale。这一轮决定论文是否像一个完整故事。

### 第三轮：表格、图形和附录

统一 booktabs、caption、float 位置、PNG/子图、宽表压缩和附录导航。完成后做第一次 PDF 视觉检查。

### 第四轮：术语、数学和语言 polish

统一术语/宏/数学符号，拆长句，降调强 claim，修语法和词形。最后再编译一次，检查 citation、ref、overfull、页数和图表可读性。

## 9. 最终建议

如果只采用一份清单，建议以 `reports_codex` 作为总框架，因为它覆盖了匿名、裸 `\cite`、章节错位和最终编译等提交级风险；同时把 `Audit/reports` 的具体条目作为执行细则，因为它列出了许多可直接修改的局部问题。

最稳妥的做法是：用本交叉报告中的 P0/P1 作为主修订路线，用 `Audit/reports` 的 P2/P3 细项做最终全文扫尾。
