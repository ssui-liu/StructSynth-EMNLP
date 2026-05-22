# StructSynth EMNLP 写作审计报告：Level 0-1 全局叙事与章节结构

## 范围

本报告仅审计 Writing Checklist 的 Level 0（Global Narrative & Story Arc）与 Level 1（Section-Level Structure & Function）。关注点包括：全局故事线、主张与证据的对应、读者预期管理，以及 abstract、introduction、related work、method、experiments、conclusion、limitations、appendix 的章节功能。审计依据限于 `Audit/writing_checklist.md` 与 `Latex-EMNLP/**`。

## 检查项简要结论

| 检查项 | 结论 |
|---|---|
| 0.1 One-sentence message | 基本通过。核心信息清楚：用依赖图作为 LLM 表格合成的 generation plan。但个别章节/材料没有完全服务于这条主线，例如主结果表放在 method 源文件中，附录有一些 causal 语言会偏离“dependency blueprint”的定位。 |
| 0.2 Narrative arc | 大体通过。Introduction 从低数据表格合成问题推进到依赖保持缺口，再自然引出 StructSynth；实验也覆盖 utility、privacy、fidelity、ablation 与 structure recovery。主要不足是部分“低数据/隐私/保真度”结论需要更精确地回扣证据。 |
| 0.3 Claim-Evidence alignment | 部分通过。贡献 1 与方法相连，贡献 2 与实验相连；但 abstract/introduction 中的 “state-of-the-art privacy preservation”“competitive statistical fidelity”“especially in low-data scenarios” 需要更细的证据限定。 |
| 0.4 Reader expectation management | 需要加强。Introduction 没有明确预告后续实验模块，读者到 experiments 才看到 ground-truth DAG、样本量 sweep、不同 LLM backend、下游模型敏感性等分析。 |
| 1.1 Abstract | 结构基本完整，但不完全达标。背景、问题、方法、意义都有；缺少具体量化结果，且 “LLM” 首次出现未展开。 |
| 1.2 Introduction | 较强。开头动机可读，gap 明确，方法名和两阶段设计清楚。弱点是 scope/非 scope 不够明确，贡献列表只有两条且偏宽，没有路线图。 |
| 1.3 Related Work | 基本通过。按主题组织，覆盖低数据表格合成、LLM 表格生成、LLM-assisted dependency discovery，也有近期工作。问题是 pipeline figure 放在 Related Work 中，章节功能上更像 Method/Introduction；部分段落定位句还可以更明确。 |
| 1.4 Method | 部分通过。开头有高层概览，两阶段结构清楚，设计理由存在。主要问题是 method 源文件夹入实验主结果表，且可复现细节大量依赖附录。 |
| 1.5 Experiments | 基本通过。setup 覆盖数据集、baselines、metrics、实现细节；结果解释较充分，ablation 有明确功能。但部分实验未在引言中预告，统计显著性未报告，privacy/fidelity 叙述需要更谨慎。 |
| 1.6 Conclusion | 基本通过。没有引入新技术或新结果，能回到 generation-plan 核心思想。但结尾主要停留在方法方向，尚未充分回扣 healthcare/finance/education 等真实场景问题。 |
| 1.7 Limitations | 基本通过。限制具体且不自毁贡献，覆盖语义先验、DAG 假设、API 依赖。可补充数据集范围、隐私指标范围、结构发现可重复性等限制。 |
| 1.8 Appendix | 内容丰富但需要分层。附录包含扩展 related work、DAG 理由、算法、实验细节、prompt、扩展讨论等；多数主文有引用，但一些对主叙事很关键的解释被放得过深，且 causal wording 与主文的“非因果 DAG”定位有张力。 |

## 主要优点

1. 全局主张清楚且有记忆点。标题与正文共同强调 “dependency graph as a generation plan”，Introduction 第 24-31 行把 gap、research question、two-stage response 连成一条自然的故事线。

2. Introduction 的 broad-to-narrow 推进有效。第 13-15 行先建立低数据表格合成中的依赖保持问题，第 17-25 行比较 deep generative、structure-aware、LLM、graph-aware 方法的不足，第 26-31 行再引出 StructSynth。

3. 方法结构与贡献高度对应。Introduction 第 34 行的两个阶段，在 Method 第 6-8 行和第 10、87 行分别展开为 Evidence-Grounded Graph Induction 与 Graph-Planned Conditional Synthesis。

4. 实验章节覆盖了主要主张。Experiments 第 4、8、11、15 行建立 datasets、baselines、metrics、implementation；第 84、90、136、161、166、172 行分别支撑 utility、privacy/fidelity、ablation、structure recovery、data efficiency、LLM generalizability。

5. Limitations 写得较具体。`LLM semantic prior`、`DAG assumption`、`LLM API dependence` 三个段落分别对应 schema 语义、结构假设、成本与可复现性风险，见 `Latex-EMNLP/sections/limitations.tex:3-14`。

## 问题按严重程度排序

### 高严重度 1：章节功能边界被结果表和 pipeline figure 打乱

Method 源文件在 graph induction 与 graph-planned synthesis 之间插入了主实验结果表：`Latex-EMNLP/sections/method.tex:44-85` 定义 `tab:results_comparison_performance`，但该表在 experiments 中才被解释和引用（`Latex-EMNLP/sections/experiments.tex:82-84`）。这会破坏 Section-Level Function：读者还没读完方法，就在源码结构上进入结果证据，且 Graph-Planned Conditional Synthesis 被推迟到第 87 行。

Related Work 也承担了不属于自己的功能：`Latex-EMNLP/sections/related_work.tex:4-8` 放置了 `pipeline.png`，caption 直接概述 StructSynth 框架。pipeline figure 是方法总览，放在 Related Work 开头会让读者误以为相关工作节已经进入方法说明。

建议：将 `tab:results_comparison_performance` 移到 `experiments.tex` 的 Main Results 前后；将 `fig:pipeline` 移到 Method 开头或 Introduction 末尾。Related Work 保持纯粹的文献定位功能。

### 高严重度 2：部分强结论与证据之间需要更精确的限定

Abstract 声称 StructSynth “achieves state-of-the-art downstream utility and privacy preservation while maintaining competitive statistical fidelity, especially in low-data scenarios”（`Latex-EMNLP/sections/abstract.tex:3`），Introduction 贡献列表也重复了这一点（`Latex-EMNLP/sections/introduction.tex:35`）。证据基本存在，但表述需要更精确：

- Downstream utility 很强：`Latex-EMNLP/sections/method.tex:80` 给出 StructSynth 平均 75.01、Avg. Rank 1.00，Experiments 第 84 行解释了这一点。
- Privacy preservation 的“最佳”主要依赖平均排名：`Latex-EMNLP/sections/experiments.tex:54` StructSynth Avg. Rank 1.50，但同表第 51 行 CLLM 的平均 privacy score 为 50.51，按“closer to 0.5 is better”（第 37 行）直观看反而更接近 50。需要解释为什么排名优先于平均值，或改成 “best average privacy rank”。
- Statistical fidelity 并不显著领先：`Latex-EMNLP/sections/experiments.tex:75` 显示 StructSynth fidelity Avg. Rank 7.92。第 90 行已经解释 pairwise fidelity 与 conditional dependency 的张力，但 abstract/contribution 中的 “competitive” 对读者来说仍偏笼统。
- “especially in low-data scenarios” 的跨数据集主结果固定为 `n=100`（`Latex-EMNLP/sections/experiments.tex:15`），样本量变化实验只在 Adult 上进行（`Latex-EMNLP/sections/experiments.tex:164-166`）。应避免暗示所有数据集都做了样本量 sweep。

建议：把 abstract 与 contribution 中的结果句改为更可证伪的版本，例如：“On six datasets at n=100, StructSynth ranks first in downstream utility and average privacy rank; on Adult, the advantage is largest for n<=50, while pairwise fidelity remains mid-ranked because it optimizes conditional rather than pairwise dependencies.”

### 高严重度 3：Introduction 没有充分管理后续实验预期

Introduction 第 32-35 行只列出两个贡献，没有说明后续将出现哪些验证模块。读者到 Experiments 才会遇到若干未预告内容：ground-truth DAG/SHD 评估（`Latex-EMNLP/sections/experiments.tex:157-161`）、训练样本量影响（`Latex-EMNLP/sections/experiments.tex:164-166`）、不同 LLM backend（`Latex-EMNLP/sections/experiments.tex:170-172`）、下游模型敏感性放在附录（`Latex-EMNLP/sections/experiments.tex:155`）。

这不是实验本身的问题，而是 reader expectation management 的问题：引言承诺的是 “six datasets + ablations”，但后文实际证据地图更丰富。缺少 roadmap 会让一些实验显得像“额外堆叠”，而不是服务于同一个故事 arc。

建议：在贡献列表后加 2-3 句路线图，明确 “we evaluate utility/privacy/fidelity on six datasets, isolate both stages by ablation, test structure recovery on bnlearn DAGs, and analyze robustness across sample size, downstream learners, and LLM backends.”

### 中高严重度 4：Method 对附录依赖过重，主文可复现性不足

Method 开头给出两阶段总览（`Latex-EMNLP/sections/method.tex:6-8`），但若读者只看主文，仍难完整复现关键机制。第 8 行把完整 prompt templates 和 algorithm 放到附录，第 29 行把 association scores 放到附录；DAG 选择的关键理由也在 Appendix 的 `Why a DAG?`（`Latex-EMNLP/sections/appendix.tex:31-46`）。

附录承载补充细节是合理的，但目前若不看附录，读者无法清楚知道 association score 的类型选择、LLM 输出格式约束、cycle resolution 的具体输入/输出边界、生成失败或无效值如何处理。这会影响 Method 的 Section-Level Function。

建议：主文保留紧凑但完整的“minimum reproducible method”：在 Method 中用一小段或小表列出三类 association scores、四个 prompt 的输入/输出、cycle resolution 的决策规则、invalid generation handling；附录再放完整模板。

### 中高严重度 5：DAG 的“非因果依赖图”定位与局部 causal wording 不一致

主文试图避免因果过度声明：Introduction 第 30 行脚注明确 DAG 不是 ground-truth causal claim；Appendix 第 37 行和第 479-481 行也说 DAG 是 generative blueprint，不支持 causal intervention/counterfactual reasoning。

但附录和 prompt 语言又多次使用因果语义：`source node is ... not caused by any other variable`（`Latex-EMNLP/sections/appendix.tex:569`）、`direct successors (effects)`（第 616 行）、`direct effects`（第 650 行）、`true parent nodes`（第 456 行）、`valid causal path`（第 331 行）。这些表述会让审稿人追问：如果不是 causal graph，为什么 prompt 要求 LLM 判断 cause/effect？

建议：统一术语为 “dependency parent/child”“generation predecessor/successor”“conditioning parent”，避免 “caused/effects/true parent/causal path”。若必须使用 causal benchmark，明确写成 “causal DAGs are used as proxy ground-truth dependency structures only for evaluation convenience.”

### 中等严重度 6：Related Work 的定位句还可更鲜明

Related Work 按主题组织良好，但第 11-20 行的前两个段落主要综述 prior methods，真正的“我们与这些工作的区别”分散在句中。第 22-24 行对 LLM-assisted dependency discovery 的定位更清楚：“do not connect the discovered structure to downstream data generation process”。第一、二段也应以类似句式收束，明确 “StructSynth differs by using a discovered graph as an executable LLM generation plan under low-data constraints.”

建议：每个 paragraph 最后一两句固定回答同一个问题：这些工作解决了什么、还缺什么、StructSynth 在哪里切入。这样 Related Work 会更像论证，而不是压缩版文献清单。

### 中等严重度 7：Conclusion 回扣现实问题不够充分

Conclusion 第 3-5 行准确总结了 generation-plan idea 和实验结果，但结尾停在 “explicit structural guidance is a promising direction”。Introduction 第 13 行以 healthcare、finance、education 等真实场景启动问题，Conclusion 没有回到这些场景，也没有说明低数据表格合成的实际收益边界。

建议：最后补一句面向真实任务的 impact，例如强调在无法大规模收集敏感表格数据时，显式依赖蓝图可以提高可用性并降低记忆风险；同时避免泛化到所有表格数据问题。

### 中等严重度 8：Abstract 缺少量化结果且有未定义缩写

Abstract 的故事顺序基本完整，但没有任何具体数值结果；而 checklist 明确要求至少一个 concrete quantitative result。`LLM` 在 `Latex-EMNLP/sections/abstract.tex:3` 首次出现时未展开，`DAG` 则有展开。

建议：在 abstract 最后一句加入 1-2 个最关键数字，并首次写出 “large language model (LLM)”。例如用平均分/平均排名表达 utility 与 privacy，同时谨慎描述 fidelity。

## 可执行修订建议

1. 重排章节材料：把 `tab:results_comparison_performance` 从 Method 移到 Experiments；把 `fig:pipeline` 从 Related Work 移到 Method 开头。

2. 改写 abstract 结果句：加入具体数字，并把 “state-of-the-art privacy preservation” 改成 “best average privacy rank” 或解释 score/rank 的判定逻辑；把 “competitive statistical fidelity” 改成 “mid-ranked pairwise fidelity, explained by a conditional-dependency objective” 或类似更诚实的表达。

3. 扩展 Introduction 贡献列表：从两条扩成三到四条，分别对应 idea/method、main empirical result、ablation/structure recovery、robustness/low-data analysis；贡献后加简短 roadmap。

4. 在 Method 中加入最小可复现摘要：一小表列出 stage、input、operation、output、appendix pointer；正文保留足够信息让读者不依赖附录也能理解算法边界。

5. 统一 DAG 术语：全稿把 “caused/effects/true parent/causal path” 替换为 dependency 或 conditioning 语言；在使用 bnlearn causal DAG 评估时明确这是 proxy evaluation。

6. 强化 Related Work 段尾 positioning：每个主题段都以 “what remains missing for low-data LLM synthesis” 结束，并把 StructSynth 的差异压成一句。

7. 调整 Experiments 的叙事顺序：先 main results，再解释 privacy-fidelity tension，再 ablation 验证两阶段，再 structure recovery，最后 robustness/sensitivity。每个小节开头说明它验证 Introduction 中哪一个 claim。

8. 给 Conclusion 增加现实场景闭环：从 generation-plan idea 回到低数据、敏感领域表格合成的可用性与隐私风险，同时承接 Limitations 中的 schema semantics、DAG assumption、API dependence。

9. 给 Appendix 加一个开头导航表：列出每个附录小节对应主文位置与功能，标明哪些是补充细节、哪些是额外分析，避免关键论证被埋在附录深处。

## 独立性说明

本次审计未访问、读取、列出、检索或打开 `Audit/reports` 及其内部任何文件；也未读取 `Audit/reports_codex` 中的其他 Codex 报告。仅创建/更新了本指定报告文件。
