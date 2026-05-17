# StructSynth 论文审阅优化核心整理

> 基于 `StructSynth 论文审阅优化.pdf` 与 `StructSynth-论文审阅优化-20260518003744/StructSynth-论文审阅优化.md` 整理。本文已移除导出噪声、重复标记、页眉页脚与无关链接，保留面向 EMNLP 投稿修改最关键的内容。

## 1. 总体判断

StructSynth 的想法有潜力，但当前主要风险不在于结果不够好，而在于：

1. 正文明显超出 EMNLP 8 页限制，Introduction、Related Work、Methodology、Experiments 都需要压缩。
2. 贡献容易被审稿人理解为 prompt engineering + BFS graph discovery + autoregressive generation 的 pipeline 拼接，而不是足够清晰的 NLP 方法创新。
3. 实验公平性、鲁棒性和可复现性证据还不够集中，尤其是 LLM backbone、样本规模、下游模型、schema semantics 依赖等问题。
4. 部分 claim 偏强，例如 `best privacy-fidelity trade-off` 与当前统计保真度结果并不完全一致。

建议将论文主张从“提出一个强新图学习算法”调整为：

> StructSynth contributes an executable dependency-blueprint paradigm for low-data tabular synthesis: it converts schema semantics, weak statistical evidence, and LLM reasoning into an explicit global dependency topology, and uses this topology as a generation-time control interface.

核心卖点应从 `LLM + BFS + DAG` 转向：

> global executable dependency topology for controlled LLM tabular generation

这比“LLM 帮助发现图，再按图生成表格”更适合 EMNLP 论文定位。

## 2. P0：必须优先修改的问题

| 问题 | 修改方向 | 影响 |
|---|---|---|
| 技术贡献可能被认为偏 applied / data mining | 在 Introduction 末尾明确与 CLLM、TabGen-ICL、GraDe 的差异：它们主要做 in-context generation 或局部/隐式依赖建模，而 StructSynth 输出可执行的全局拓扑蓝图 | 高 |
| Prompt-based BFS 新意不足 | 降低“BFS 是核心贡献”的权重，强调 `LLM prior + statistical cues + executable graph as control interface` | 高 |
| `guarantees fidelity` 表述过强 | 改为 `guarantees adherence to the discovered graph`，避免暗示发现图等于真实结构 | 高 |
| `best privacy-fidelity trade-off` 与 Table 2 不完全一致 | 改为 `best downstream utility and privacy preservation, while maintaining competitive structural/statistical fidelity` | 高 |
| Table 2 可能存在数值错误 | 重点核对 BN 的 Statistical Fidelity 行，该行看起来可能误用了 Table 1 的 downstream performance 数值 | 高 |
| DAG 容易被误读为 causal graph | 全文用 `dependency pathway`、`structural dependency` 替换不必要的 `causal mechanism/pathway` | 高 |

特别注意：论文正文与 Appendix H.2 都显示 StructSynth 的 Statistical Fidelity 是 competitive，而不是 best；平均 rank 约为 7.08。因此 Abstract 和 Conclusion 中不能宣称其拥有最佳 fidelity。

推荐替代表述：

> StructSynth achieves the best downstream utility and privacy preservation, while maintaining competitive structural/statistical fidelity.

## 3. P0：正文压缩到 8 页

目标至少压缩 2.5 页，建议争取压缩 2.8-3.8 页。

| 部分 | 当前状态 | 建议目标 | 可节省 |
|---|---:|---:|---:|
| Abstract + Introduction + Figure 1 | 约 2.5-3 页 | 1.5 页以内 | 0.8-1.0 页 |
| Related Work | 约 1 页以上 | 0.5 页 | 0.4-0.6 页 |
| Methodology + Figure 2 | 约 2.3 页 | 1.4-1.6 页 | 0.6-0.9 页 |
| Experiments + Tables/Figures | 约 4.5 页 | 3.0-3.3 页 | 1.0-1.3 页 |
| Conclusion + Limitations | 约 0.7 页 | 0.3-0.4 页 | 0.3 页 |

### 3.1 Introduction

当前四段式 Introduction 冗余较多。P1 已经讲 tabular data 重要性、依赖关系与 low-data failure modes；P2 又从 DGM、structure-aware methods、LLM 三类方法重新讲 dependency handling，建议合并为三段。

**P1：问题 + 低数据困难**

保留主线：

> low-data tabular synthesis must preserve feature dependencies

删除高 stakes 领域的长铺垫，只保留 healthcare / finance / education 的一句例子。

**P2：现有方法缺口**

将 DGM、structure-aware、LLM 各压缩成一句：

> DGMs learn dependencies implicitly and become data-hungry; structure-aware methods require reliable graph discovery, which collapses under low data; prompt-based LLMs exploit semantic priors but induce dependencies only through serialized text.

不要在 Introduction 中展开 TVAE、GAN、Diffusion、DECAF、GOGGLE 等细节，这些移到 Related Work 或 Appendix。

**P3：方法 + 贡献**

RQ1/RQ2 段可删除或压成一句，因为后文已经解释 StructSynth 的两个阶段。贡献 bullet 从 3 条压成 2 条：

1. A discover-then-synthesize framework that turns LLM/statistical evidence into an executable dependency topology.
2. Empirical evidence across utility, privacy, structural recovery, robustness to sample size and LLM backbones.

Figure 1 建议移到 Appendix 或与 Figure 2 合并。8 页限制下，Figure 2 的信息密度更高。

### 3.2 Related Work

Related Work 应压成 closest work only，避免与 Introduction 重复。

正文只保留三小段：

1. **Tabular synthesis in low-data regimes**：一句带过 DGM / structure-aware 方法。
2. **LLM-based tabular generation**：重点对比 GReaT、CLLM、TabGen-ICL。
3. **LLM-assisted dependency / graph discovery**：放入与 StructSynth 最相关的 BFS / LLM graph discovery 工作，并指出它们没有把图作为 tabular generation blueprint。

SMOTE、Copula、TVAE、CTGAN、TabDDPM、TabSyn 等细节移到 Appendix 或实验 baseline 说明。

### 3.3 Methodology

正文 Method 不应重复 Appendix 中的完整算法和 prompt。Problem Definition 可压成一个短段：

> Given n <= 100 labeled tabular records with schema A, our goal is to generate s synthetic records that improve downstream performance when combined with the original training set.

公式 (1)-(6) 多数只是文字流程形式化，不构成理论贡献。建议将 `E_prop`、`V_new`、`E_pruned`、projection operator 等细节移到 Appendix。

正文保留三步机制即可：

1. **Source node initialization**：LLM identifies likely root/source attributes.
2. **BFS expansion with statistical cues**：association scores guide LLM link proposals.
3. **Topological generation**：generate layer by layer, conditioning on parents.

Method 正文控制在 1.5 页以内。

### 3.4 Experiments

正文实验只保留四类核心证据：

1. **Utility main table**：Table 1 保留，但减少小数位，必要时缩短 method list。
2. **Ablation table**：Table 3 证明结构发现、统计 cue、topological order 的作用。
3. **Structural recovery figure**：Figure 3 证明 DAG discovery 不是装饰。
4. **Robustness summary**：将 n-sweep 和 LLM-backbone 结果压成一个小表或两栏小图，完整图放 Appendix。

Table 2 的 per-dataset privacy/fidelity 结果建议移到 Appendix。正文只放 compact summary，例如：

| Method | Utility avg. rank | Privacy avg. rank | Fidelity avg. rank |
|---|---:|---:|---:|
| CLLM | 2.67 | 3.33 | 8.50 |
| StructSynth | 1.00 | 1.33 | 7.08 |
| Best non-LLM | 待补 | 待补 | 待补 |

这样可以节省接近一页，同时避免过度解读 fidelity。

## 4. P0：实验补强

当前主实验设置为 `gpt-4o-mini`、`n=100`、`s=1000`、XGBoost。论文已有 Adult 上的 n-sweep 和多 LLM backbone 实验，但只在一个数据集上展示，不足以完全说服审稿人。

建议补充最小实验集合：

| 风险 | 当前证据 | 建议补充 | 影响 |
|---|---|---|---|
| LLM backbone 单一 | Figure 5 只在 Adult 上比较多种 LLM | 至少在 Adult + Anxiety/Salary + Churn 三个数据集上跑 GPT-4o-mini、一个开源模型、一个强闭源模型 | 高 |
| n=100 单一规模 | Figure 4 只在 Adult 上做 n in {20, 50, 100, 200} | 在一个 classification、一个 regression、一个 post-cutoff dataset 上做 n-sweep | 高 |
| 下游评估器单一 | 只用 XGBoost | 加 Logistic / Linear model、Random Forest、MLP；回归任务加 Ridge / RF / XGB | 高 |
| s=1000 固定 | 当前固定生成 1000 samples | 加 s in {100, 500, 1000, 2000}，报告 utility/privacy 曲线 | 中 |
| temperature=0.9 固定 | 当前只给超参表 | 加 temperature in {0.2, 0.7, 0.9, 1.1}，或至少讨论敏感性 | 中 |

最关键的是 downstream model sensitivity。如果只用 XGBoost，审稿人会怀疑 synthetic data augmentation 是否只对 tree-based learner 有效。

## 5. P0：Baseline 公平性

StructSynth 和 CLLM 使用 LLM external semantic prior 与 in-context learning，而 DGM / structure-aware baselines 只从 100 条样本中训练。论文需要明确这不是完全同条件比较，而是比较 low-data setting 下可用方法的实际效果。

建议：

1. 将 baselines 分组汇报：
   - **No-external-prior methods**：TVAE、CTGAN、TabDDPM、TabSyn、BN、GOGGLE、DECAF。
   - **LLM-prior methods**：GReaT、CLLM、GraDe、StructSynth。
2. 主结论重点强调 StructSynth 相比 CLLM / GraDe 的改进，因为这是更公平的对比。
3. 增加 anonymized-schema control：将列名替换为 `X1, X2, ...` 或随机打乱 column names，再运行 StructSynth / CLLM。
4. 至少对 CTGAN、TabDDPM、TabSyn、BN / GOGGLE 做少量 hyperparameter search；若做不到，应说明 n=100 下 validation data 不足，因此采用官方默认配置，并作为 limitation。
5. 正文简短提到 token/cost-budget fairness。Appendix G 已报告 StructSynth 比 CLLM 多约 31% token overhead，应避免审稿人认为性能提升只是来自更多 prompt budget。

## 6. P1：DAG 假设与 Cycle Resolution

论文已说明 DAG 是 generative blueprint，不是 causal claim；Appendix B 也解释了为什么需要方向性和无环性。但正文中仍需减少 causal 语言，并补强 cycle resolution 的实证依据。

| 问题 | 修改建议 | 影响 |
|---|---|---|
| DAG 被误读为 causal graph | 全文将 `causal pathway/mechanism` 改为 `dependency pathway/structural dependency`，除非讨论 bnlearn ground-truth causal DAG | 高 |
| Cycle resolution 由 LLM 判断，可能主观 | 增加小表：平均 cycle 数、每次移除边类型、resolution 后 SHD/utility 变化 | 中高 |
| 缺少 cycle resolution 消融 | 加 `Score-based Cycle Resolution`：移除 association score 最低的边，并与 LLM-based resolution 对比 | 中高 |
| DAG 不适合双向依赖 | 在 Limitations 中提出 SCC condensation、iterative conditional generation、undirected dependency blocks 等未来方向 | 中 |

Method 中 cycle resolution 的描述可以压缩，把空间留给 ablation 或实证 justification。

## 7. P1：结构发现评估的记忆污染风险

结构发现质量用 Asia、Child、Insurance 三个 bnlearn benchmark，并报告 SHD。但这些网络非常经典，变量名如 `smoke`、`lung`、`bronc`、`dysp` 具有强语义，LLM 可能在预训练中见过类似结构。

建议补充 schema anonymization / random renaming 实验：

| 设置 | 示例 |
|---|---|
| 原始变量名 | `smoke`, `lung`, `bronc`, `dysp` |
| 匿名变量名 | `X1`, `X2`, `X3`, `X4` |
| 语义扰动变量名 | random unrelated names |

报告指标：

1. SHD
2. Edge precision / recall
3. Orientation accuracy

若 StructSynth 在匿名设置下仍优于 FCI / GOGGLE / NoTears，说明 statistical cue + BFS 机制确实有效；若性能下降，也可诚实说明方法依赖 schema semantics，这与 low-data LLM prior 的论文主张一致。

## 8. P1：可复现性

Appendix I 已给出 prompt templates，Appendix E.3 给出 temperature、top_p、max_tokens、XGBoost 参数，但对 LLM-based 方法仍不够。

建议补充：

1. 模型版本与调用日期，例如 `gpt-4o-mini` 的 exact API model string。
2. LLM 输出解析规则，包括 JSON schema、失败重试次数、非法边处理。
3. few-shot subset 选择策略：随机还是 curated，每个 seed 是否固定。
4. prompt 完整模板与变量填充示例，至少补一个真实 dataset 的完整 prompt 实例。
5. temperature sensitivity：结构发现阶段建议用较低 temperature，生成阶段可用较高 temperature，或至少做消融。
6. 代码与生成图缓存：结构图应保存，synthetic tables 应可复现或至少可重新采样。

正文只需一句：

> Full prompts, parsing rules, and model-version details are provided in Appendix.

## 9. P1：实验叙述降温

Table 1 显示 StructSynth 平均 rank 1.00、平均得分 75.01，超过 CLLM 的 73.36。但多个 dataset 上均值差距不大且标准差重叠，例如 Anxiety、Churn。

避免写：

> StructSynth consistently outperforms all baselines.

建议改为：

> StructSynth obtains the best mean performance on all six datasets, though the margin is small on some datasets; significance tests are reported in Appendix.

建议补充 paired bootstrap 或 Wilcoxon signed-rank test，至少比较：

1. StructSynth vs CLLM
2. StructSynth vs TabSyn
3. StructSynth vs Train-only

Privacy metric 目前只用 nearest-neighbor train/test fraction。接近 0.5 不一定说明隐私安全，也可能说明 synthetic data 离真实数据都远。建议在 Appendix 增加：

1. Exact duplicate rate
2. Distance to closest record, DCR
3. Membership inference attack AUC
4. Attribute disclosure risk

## 10. 建议的 8 页正文结构

| 页码 | 内容 | 处理方式 |
|---|---|---|
| Page 1-1.5 | Introduction | 删除 Figure 1 或移附录；三段式 intro；贡献两条 |
| Page 1.5-2 | Related Work | 只保留 closest work；常规 DGM 历史移附录 |
| Page 2-3.5 | Method | 保留 Figure 2 但缩小；正文只讲三步机制；公式和完整算法移附录 |
| Page 3.5-4 | Experimental Setup | 数据集、baselines、metrics 压缩成紧凑段落 + 小表 |
| Page 4-5 | Main Utility Results | Table 1 保留或简化；结果文字压缩 |
| Page 5-6 | Ablation + Structural Recovery | Table 3 + Figure 3，强调结构确实有用 |
| Page 6-7 | Robustness / Fairness | 用小表汇报 n-sweep、LLM-backbone、downstream-model sensitivity；完整图放 Appendix |
| Page 7-8 | Privacy/Fidelity Summary + Limitations + Conclusion | Table 2 移 Appendix；正文给 compact rank summary；Limitations 压缩但保留 DAG、schema semantics、LLM API 依赖 |

## 11. 最关键修改清单

### 必须改

1. 修正 Abstract 和 Conclusion 中 `best privacy-fidelity trade-off` 的过强表述。
2. 核对 Table 2，尤其 BN 的 Statistical Fidelity 行是否复制错误。
3. Introduction + Related Work 至少压掉 1.2 页。
4. Method 中大部分公式和形式化定义移到 Appendix。
5. 增加或前置 anonymized-schema ablation，证明方法不是简单依赖 LLM 记忆或语义常识。
6. 增加 downstream model sensitivity，避免只对 XGBoost 有效的质疑。
7. 正文明确 DAG 是 generation blueprint，不是 causal graph，并减少 causal 语言。
8. Table 2 per-dataset 结果移到 Appendix，用 compact privacy/fidelity summary 替代。

### 建议改

1. n-sweep 不只在 Adult 上做，至少再加一个 regression 和一个 post-cutoff dataset。
2. LLM backbone 不只在 Adult 上做，至少补 2-3 个代表数据集。
3. Cycle resolution 加 score-based baseline 消融。
4. 加显著性检验。
5. 补 temperature、s、prompt robustness sensitivity。

## 12. 一句话投稿策略

这篇论文的最佳投稿策略不是把 StructSynth 包装成全新的图学习算法，而是定位为一种 **LLM-controlled tabular synthesis framework**：核心贡献是把语言模型的 schema prior 转换为可执行、可解释、可控的依赖生成蓝图。当前最需要做的是压缩叙述、降低过强 claim、补公平性与鲁棒性实验。
