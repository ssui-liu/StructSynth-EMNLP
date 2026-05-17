# Reviewer 6JGG 审稿意见深度分析与评估

> **目标：** 结合论文原文，对 Reviewer 6JGG 的每条 Weakness 和 Question 进行逐一分析，评估其合理性，并为 rebuttal 提供论据和策略。

---

## 一、审稿人评分概览

| Criterion | Score | 评估 |
|---|---|---|
| Relevance | 3: Moderate | 偏低，与其他审稿人一致 |
| Novelty | **1: Poor** | **所有审稿人中最低分**，需重点反驳 |
| Technical Quality | **2: Low** | 核心拉分项 |
| Presentation | **2: Low** | 低于其他审稿人（均为 3），需关注 |
| Reproducibility | **1: Poor** | **所有审稿人中最低分**，需重点反驳 |
| Reviewer Confidence | 3: Moderate | 中等自信度，有说服空间 |

### 四位审稿人评分横向对比

| Criterion | hziw | f5xi | ep8Q | **6JGG** |
|---|---|---|---|---|
| Relevance | 3 | 3 | 4 | **3** |
| Novelty | 2 | 2 | 3 | **1** |
| Technical Quality | 2 | 2 | 2 | **2** |
| Presentation | 3 | 3 | 3 | **2** |
| Reproducibility | 2 | 2 | 2 | **1** |
| Reviewer Confidence | 3 | 3 | 3 | **3** |

**总体判断：** Reviewer 6JGG 是四位审稿人中 **最严厉的**，给出了两个 1 分（Poor），这是极端低分。但需注意：

1. **Confidence=3 (Moderate)** 说明审稿人对自己的判断并非高度自信，有力的反驳有较大改变评分的可能。
2. **6JGG 的 Strengths 段落表明其认可论文方向**——明确肯定了 decoupled framework 的价值、模型可解释性的提升、以及 privacy-fidelity trade-off 的改善。这意味着审稿人 **认可"做什么"但质疑"怎么做的够不够好"**。
3. **Novelty=1 和 Reproducibility=1 是极端评分**，即使反驳后仅提升到 2 分（Low），也意味着显著的相对改善。在中位数评分机制下，将极端低分拉升至合理范围对最终决定有重大影响。
4. 6JGG 的批评集中在 **三个截然不同的维度**：新颖性（W1）、数据可靠性（W2）、实验公平性（W3）。这需要 rebuttal 在不同层面进行针对性回应。

### 6JGG 的 Strengths 分析

6JGG 的 Strengths 段落提供了有价值的反驳基础：

> "This work introduces a decoupled framework that separates dependency discovery from data generation. This process not only mitigates the limitations of implicit structure learning and unstable pre-defined structures in low-data regimes, but also to some extent enhances model interpretability."

> "Furthermore, it achieves an improved privacy-fidelity trade-off by employing the dependency DAG as a structural regularizer to prevent training data memorization."

**关键洞察：** 6JGG 承认了框架的 **解释性价值** 和 **正则化效果**，这两点直接与 W2（数据可靠性）形成张力——如果 DAG 作为 structural regularizer 能有效防止 memorization（审稿人已承认），那生成数据的可靠性就比审稿人声称的要高。

---

## 二、逐条 Weakness 深度分析

### Weakness 1: 新颖性有限 — "现有技术的 minor tweaks 组合"

#### 审稿人原文

> The novelty is limited, where the discover-then-synthesize paradigm, LLM-based structure discovery and topological autoregressive synthesis are all existing in the literature. StructSynth only combines these with minor tweaks with no significant innovation.

#### 审稿人批评的核心逻辑

审稿人将 StructSynth 解构为三个已有组件：
1. Discover-then-synthesize 范式 → 已存在（Bayesian Network 即可视为该范式）
2. LLM-based structure discovery → 已存在（`jiralerspong2024efficient`, `ban2023causal` 等）
3. Topological autoregressive synthesis → 已存在（BN 的条件概率表生成即遵循拓扑序）

审稿人认为 StructSynth 只是将这三个组件"拼接"在一起，没有任何组件本身是新的。

#### 与其他审稿人的交叉分析

| 审稿人 | 批评 | 激进程度 |
|---|---|---|
| hziw | "limited fundamental novelty beyond module integration" | 中等 — 承认有集成价值 |
| f5xi | 未直接批评新颖性（低分源于技术质疑连带） | — |
| ep8Q | "Novel and well-motivated framework" | **正面评价** |
| **6JGG** | "only combines these with minor tweaks with no significant innovation" | **最激进** — 否认任何组件的创新性 |

**关键差异：** ep8Q 给出了 Novelty=3 并明确称框架为"novel"，与 6JGG 的 Novelty=1 形成鲜明对比。这种审稿人之间的分歧意味着 6JGG 的判断并非共识，反驳有据。

#### 论文中的反驳证据

**证据 1: 每个组件都有超越"minor tweak"的技术创新。**

| 组件 | 已有工作 | StructSynth 的创新 | 创新性质 |
|---|---|---|---|
| Discover-then-synthesize | BN, DECAF | **解耦设计 + 低数据优化**：传统方法需要同时学习结构和分布，StructSynth 将二者分离以降低样本复杂度 | 范式优化 |
| Structure Discovery | LLM pairwise (Kiciman et al.), LLM BFS (Jiralerspong et al.) | **Hybrid discovery (LLM + statistical cues) + Reasoned cycle resolution**：统计信号作为弱监督引导 LLM，cycle resolution 基于文本 rationale 推理选择最弱边 | **技术创新** |
| Topological Generation | BN conditional probability tables | **LLM-based parent-conditioned generation with topological layering**：用 LLM 替代条件概率表，每个特征的生成显式以其 DAG 父节点为条件（硬约束 by construction） | **技术创新** |

**证据 2: Hybrid Discovery 的非平凡性（`methodology.tex:20-35`）。**

LLM-based structure discovery 的已有工作主要分为三类（`appendix.tex:11-14`）：
- Pairwise querying：O(K²) 复杂度，不适合多特征数据集
- BFS traversal：如 Jiralerspong et al.，但纯依赖 LLM 推理，无数据驱动信号
- Iterative supervision loop：传统算法提出 → LLM 验证

StructSynth 的 hybrid approach 不同于以上任何一种：
- **在 BFS 过程中实时注入统计关联信号**（Pearson's R, Cramér's V, Correlation Ratio）
- 统计信号作为 **弱监督**（而非唯一决策依据）辅助 LLM 推理
- Ablation 证实：移除统计信号后 AUC -1.5 pts（`experiments.tex:145`，No-Correlation Score: 84.06 vs. 85.55），说明统计信号的非冗余贡献

这不是"minor tweak"——这是一个新的 **信号融合机制**，将数据驱动的统计证据与 LLM 的语义先验在 prompt 层面进行了有机整合。

**证据 3: Reasoned Cycle Resolution 是全新的图约束维护范式（`methodology.tex:37-48`）。**

传统的无环性维护方法：
- PC 算法：基于条件独立性测试逐步删边，无法利用语义信息
- NoTears：连续优化中用矩阵指数/迹惩罚近似无环性，纯数值方法
- GES：面向 Markov 等价类的贪心搜索

StructSynth 的 cycle resolution：
- 当候选边引入环时，LLM 接收环中 **每条边的文本 rationale**（如"Higher Education is strongly correlated with and typically precedes higher Income"）
- LLM 分析这些 rationale 之间的 **逻辑矛盾**，推理选择最弱的边移除
- 这是一种 **reasoning-driven** 而非 **heuristic-driven** 的图约束维护

**证据 4: Ablation 量化了每个组件的非冗余贡献。**

| 变体 | AUC | Δ vs. StructSynth | 被替换的组件 |
|---|---|---|---|
| StructSynth (Full) | **85.55** | — | — |
| PC Discovery | 84.54 | -1.01 | Hybrid discovery → 纯统计 |
| NoTears Discovery | 84.17 | -1.38 | Hybrid discovery → 连续优化 |
| No-Correlation Score | 84.06 | -1.49 | Hybrid discovery → 纯 LLM |
| Pairwise Discovery | 85.25 | -0.30 | BFS → Pairwise |
| No Topological Order | 84.41 | -1.14 | Topological generation → 无序生成 |
| No Structure (=CLLM) | 83.95 | -1.60 | 完整框架 → 纯 LLM |
| Bayesian Sampler | 81.17 | -4.38 | LLM generator → 传统采样器 |

如果只是"minor tweaks"的组合，替换任何组件不应导致如此显著的性能差异。更关键的是：
- 移除统计信号（-1.5）和移除拓扑序（-1.1）的退化幅度证明了这两个"tweaks"各自有实质性的功能贡献
- Bayesian Sampler 的 -4.4 退化证明 LLM 与结构的 **协同效应** 远超简单组合

**证据 5: 与最相近工作 GraDe 的本质区别。**

GraDe（`related_works.tex:21`）将学习到的稀疏依赖图注入 attention 机制。这是一种 **软约束**——模型仍然可以在 attention weights 中偏离依赖结构。StructSynth 的拓扑序生成是 **硬约束**——生成过程 **按构造** 遵守依赖关系（by construction）。这是方法论层面的根本差异。

具体而言：
- GraDe: $P(\text{output} \mid \text{graph})$ — graph 影响 attention weights，但不强制条件化顺序
- StructSynth: $P(X_{L_i} \mid X_{L_{<i}}, G)$ — graph 确定条件化的拓扑层和父节点，每个特征的生成 **必须** 以其父节点已生成的值为条件

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理**。范式和各组件确实各有前身，审稿人的解构分析有一定道理。但"minor tweaks"的定性是过度的 |
| 审稿人可能忽略的点 | (1) Hybrid discovery 的信号融合机制创新; (2) Reasoned cycle resolution 的推理驱动范式; (3) 硬约束 vs 软约束的本质区别; (4) Ablation 量化的非冗余贡献; (5) Reviewer ep8Q 对新颖性的正面评价 |
| 反驳难度 | **中等偏高**。6JGG 的批评非常激进，需要精准论证"不是 minor tweaks"而不否认组件的前身 |
| 评分提升可能性 | Novelty 有望从 1 提升到 2-3。ep8Q 的 Novelty=3 提供了锚点 |

#### Rebuttal 策略

**核心论点：** 新颖性不在于各组件的前身是否存在，而在于 **组件内部的非平凡技术创新** 和 **跨组件的协同设计**。Hybrid discovery 的信号融合、reasoned cycle resolution 的推理驱动范式、以及拓扑序硬约束生成，每一个都有超越"minor tweak"的技术贡献，Ablation 证实了它们的非冗余性。

**具体回应：**
1. **不否认前身的存在**，而是强调每个组件内部的创新深度
2. **用 ablation 数据作为核心论据**：如果只是 minor tweaks，替换后不应导致 1.0-4.4 pts 的退化
3. **与 GraDe 明确区分**：硬结构约束 (by construction) vs 软 attention 引导
4. **提出 reasoned cycle resolution 作为新的图约束维护范式**：区别于传统的数值优化和启发式搜索
5. **引用 ep8Q 的正面评价**："Novel and well-motivated framework" — 说明新颖性判断存在审稿人间的分歧

---

### Weakness 2: 生成数据不可靠 — "LLM 先验知识影响大，与 LLM 方法无本质区别"

#### 审稿人原文

> The generated data is unreliable. The dependency DAG of features and the generation are all dependent on the LLM where the prior knowledge the LLM has will greatly affects the quality of the generated data. Since each large model has areas of strength and weakness, should different large models be used for table generation tasks in different domains? It has no fundamental difference with the methods with LLM.

#### 审稿人批评的核心逻辑

审稿人提出了两个关联的质疑：
1. **LLM 先验偏差**：结构发现和生成完全依赖 LLM，LLM 的领域知识偏差会直接影响 DAG 质量和生成数据质量
2. **与纯 LLM 方法无本质区别**：既然都依赖 LLM，StructSynth 与 CLLM 等方法有什么根本不同？

审稿人还提出了一个暗示性问题：不同领域的表格数据任务是否需要选择不同的 LLM？这隐含了对方法通用性的质疑。

#### 论文中的反驳证据

**证据 1: Multi-LLM 泛化性实验直接反驳了"LLM 偏差"质疑（`experiments.tex:194-198`，Figure 6）。**

论文在 7 个不同的 LLM 上测试了 StructSynth vs. CLLM：

| LLM 类型 | 模型 | StructSynth vs CLLM 的优势 |
|---|---|---|
| 开源 (小) | Qwen-2.5 系列 | 一致优势 |
| 开源 (中) | Llama-4 Maverick | 最大优势 (+0.028 AUC) |
| 开源 (大) | DeepSeek 系列 | 一致优势 |
| 闭源 | GPT-4o 系列 | 一致优势 |

**关键发现：**
- StructSynth 在 **每一个测试的 LLM** 上都优于 CLLM
- 优势最大的是 Maverick（中等能力模型），说明结构引导对能力较弱的 LLM 帮助最大
- 即使是最强的 GPT-4o，StructSynth 仍提供可衡量的改进

这直接反驳了审稿人的两个论点：
- 如果 LLM 的领域偏差是致命的，那 StructSynth 不应在 7 个不同架构的模型上一致有效
- 如果 StructSynth 与 CLLM"无本质区别"，那结构引导不应在所有模型上都带来改进

**证据 2: 统计信号作为数据驱动的偏差矫正机制。**

LLM 的先验知识不是无约束的——BFS 过程中，LLM 在提出每条边时都接收了 **统计关联信号** $\mathcal{S}(A_i)$（`methodology.tex:22-27`）：

$$P_i = f_{\text{LLM}}(\pi_{\text{generate}}(A_i, G_t, \mathcal{S}(A_i), \mathcal{D}_{\text{few\_shot}}))$$

统计信号来自 **实际数据**（Pearson's R, Cramér's V, Correlation Ratio），提供了独立于 LLM 先验的实证证据。Ablation（No-Correlation Score: 84.06 vs. 85.55, Δ=-1.5）证实了统计信号的非冗余贡献。

这意味着：**即使 LLM 对某个领域有偏差，统计信号会提供数据驱动的矫正**。

**证据 3: Post-cutoff 数据集表现说明不仅依赖 LLM 先验。**

论文使用了 2 个 LLM 知识截止日期后发布的数据集（`appendix.tex:27-28`）：
- Anxiety（医疗/健康领域，post-cutoff ✓）
- Salary（经济领域，post-cutoff ✓）

StructSynth 在这两个数据集上的表现：

| 数据集 | StructSynth | CLLM | 差异 |
|---|---|---|---|
| Anxiety (AUC) | **86.45** | 85.17 | +1.28 |
| Salary (R²) | **55.98** | 54.53 | +1.45 |

如果 StructSynth 的性能完全来自 LLM 对数据的先验知识（如审稿人所暗示），那在 post-cutoff 数据集上，LLM 不可能"记住"数据，StructSynth 的优势应该消失。但实验显示优势依然存在且与平均优势（+1.65）一致。

这说明 **StructSynth 的优势来自方法论设计（结构蓝图引导），而非 LLM 的数据记忆**。

**证据 4: StructSynth 与 CLLM 有本质区别——ablation 直接证实。**

| 方面 | CLLM | StructSynth | 区别 |
|---|---|---|---|
| 结构建模 | 无显式结构 | DAG 蓝图 | 有 vs 无 |
| 生成策略 | 所有特征一起生成 | 按拓扑层逐步条件生成 | 无约束 vs 硬约束 |
| 统计信号 | 不使用 | BFS 中注入 | 无 vs 有 |
| Privacy 效果 | rank 3.33 | rank **1.33** | DAG 作为正则化器 |

Ablation: No Structure (=CLLM) → AUC 从 85.55 降至 83.95（-1.6 pts），这不是"无本质区别"。

**证据 5: DAG 作为 structural regularizer 的正则化效应。**

审稿人在 Strengths 中已承认：
> "it achieves an improved privacy-fidelity trade-off by employing the dependency DAG as a structural regularizer to prevent training data memorization."

如果 DAG 能有效防止 memorization（审稿人已认可），那它就不是简单的"传递 LLM 偏差"——它在 **约束和引导 LLM 的生成过程**，使其不偏向记忆训练数据而是遵循依赖结构。

| 方法 | Privacy Risk (Adult) | 解读 |
|---|---|---|
| GReaT | 99.50% | 严重 memorization |
| CLLM | 49.45% | 几乎无 memorization |
| StructSynth | **49.97%** | 几乎无 memorization + 更高 utility |

StructSynth 在保持与 CLLM 相同水平隐私保护的同时，AUC 提升了 1.6 pts。DAG 的正则化效应没有损害隐私，同时提升了数据效用。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理但过度概括**。LLM 先验确实会影响结构发现，但论文已通过多种机制缓解这一问题（统计信号、Multi-LLM 泛化性、post-cutoff 数据集验证）。"无本质区别"的论断与 ablation 数据直接矛盾 |
| 审稿人可能忽略的点 | (1) Figure 6 的 Multi-LLM 泛化性实验; (2) Post-cutoff 数据集的持续优势; (3) 统计信号的数据驱动矫正; (4) Ablation No Structure = CLLM 的 -1.6 pts 退化; (5) 6JGG 自己在 Strengths 中承认的 DAG 正则化效应 |
| 反驳难度 | **中等**。论文有充分的实验证据，但需要整合多个维度的论据 |
| 评分提升可能性 | Technical Quality 有望从 2 提升到 3 |

#### Rebuttal 策略

**核心论点：** StructSynth 与纯 LLM 方法有本质区别：(1) 显式结构蓝图引导（硬约束 by construction），(2) 统计信号的数据驱动矫正，(3) DAG 作为正则化器防止 memorization。Multi-LLM 泛化性实验（7 个模型一致优势）和 post-cutoff 数据集的持续表现证明方法不依赖特定 LLM 的先验知识。

**具体回应（四步论证）：**

1. **承认 LLM 的角色但重新框定**：LLM 在 StructSynth 中不是"无约束的生成器"，而是被 DAG 蓝图和统计信号双重约束的受引导生成器。

2. **Multi-LLM 实验作为核心反驳**：在 7 个不同架构的 LLM 上一致优于 CLLM，证明方法的优势来自框架设计而非特定 LLM 的先验。

3. **Post-cutoff 数据集的验证**：在 LLM 不可能见过数据的数据集上优势依然存在，排除了"LLM 记忆数据"的解释。

4. **Ablation 量化本质区别**：No Structure (=CLLM) 导致 -1.6 pts AUC 退化，这不是"无本质区别"。

**额外回应"不同领域选择不同 LLM"：**
- Multi-LLM 实验表明结构引导在所有测试模型上都有效，包括通用模型
- 统计信号来自数据本身（与领域无关的关联度量），能自适应不同领域
- 论文不排除在特定领域使用专门 LLM 可进一步提升，但通用 LLM 已足够有效

---

### Weakness 3: 实验设计缺陷 — "默认超参数 + LLM 设置不匹配"

#### 审稿人原文

> There are some flaws with experimental design. This paper uses default hyperparameters for baselines and mismatches LLM settings for LLM-based baselines, which will lead to unfair comparisons.

#### 审稿人批评的核心逻辑

审稿人提出了两个独立的实验公平性质疑：

1. **默认超参数问题**：非 LLM baselines 使用 SynthCity 库的默认配置，可能低估了 baseline 的性能
2. **LLM 设置不匹配**：LLM-based baselines（GReaT, CLLM, GraDe）的 LLM 配置可能与 StructSynth 不一致，导致不公平的比较

#### 这是 6JGG 最独特的批评

四位审稿人中，只有 6JGG 提出了实验公平性的问题。这一批评如果成立，将直接质疑所有实验结论的可信度，影响最为严重。

#### 逐点深度分析

##### 质疑 1: 默认超参数是否公平？

**论文的实验设置（`appendix.tex:44-46`）：**

> "For all baseline methods, with the exception of CuratedLLM, we utilize the implementations provided in the SynthCity library. These models were run using their default hyperparameter configurations to ensure a standardized comparison."

**评估：**

| 维度 | 分析 |
|---|---|
| 社区惯例 | 使用库默认配置是合成数据领域的 **标准实践**。CLLM（`cllm2024`）、TabDDPM（`kotelnikov2023tabddpm`）、TabSyn（`tabsyn`）等先前工作均采用类似方法 |
| 公平性论证 | 默认配置通常是作者推荐的参数，经过了充分的调优。使用默认配置避免了 "cherry-picking baselines" 的反面批评 |
| SynthCity 库的权威性 | SynthCity（`qian2023synthcity`）是 NeurIPS 2023 发表的合成数据基准框架，其默认配置经过社区验证 |
| 潜在风险 | 审稿人的担忧有一定道理——默认配置可能不适合低数据场景（n=100），因为默认参数可能针对较大数据集调优 |

**反驳策略：**
- 强调使用 SynthCity 库和默认配置是标准实践
- 指出 StructSynth 的优势幅度较大（avg rank 1.00，远超第二名 CLLM 的 2.67），不太可能完全由超参数解释
- 可在 rebuttal 中对关键 baseline（如 TabSyn, CTGAN）进行简单的超参数调优实验作为补充验证

##### 质疑 2: LLM 设置是否匹配？

**这是 6JGG 批评中最关键的一点，也是论文有直接反驳证据的一点。**

**论文对 CLLM 的明确声明（`appendix.tex:46`）：**

> "For CuratedLLM, we used the official source code provided by the authors, adapting it to our experimental setup. To ensure a fair comparison, **it was configured with the same Large Language Model (LLM) settings as our proposed StructSynth**, with detailed parameters provided in Table 2."

**详细参数对比（`appendix.tex:63-67`，Table 2）：**

| Hyperparameter | Value |
|---|---|
| LLM backbone | gpt-4o-mini |
| temperature | 0.9 |
| top_p | 0.95 |
| frequency_penalty | 0 |
| presence_penalty | 0 |
| max_tokens | 8000 |

这些参数同时适用于 StructSynth 和 CLLM。6JGG 声称的"LLM settings mismatch"对 CLLM 是 **不成立的**。

**对 GReaT 的分析：**

GReaT（`related_works.tex:21`）是一个 **fine-tuning 方法**：
- 使用 GPT-2 作为 backbone，通过 fine-tuning 学习数据分布
- 生成时 autoregressively 生成 token 序列
- 不使用 prompt-based generation，因此 **不适用** "LLM settings" 的概念
- GReaT 的 GPT-2 是其方法论的核心组件（fine-tuning 需要可训练的模型），不能替换为 gpt-4o-mini（不可 fine-tune）
- 使用 GReaT 的默认 GPT-2 配置是唯一合理的实验设置

**对 GraDe 的分析：**

GraDe（`related_works.tex:21`）将外部提取的功能依赖注入 attention 机制：
- 使用可训练的 Transformer 模型
- 依赖 externally extracted functional dependencies 作为图结构的来源
- 不是一个 prompt-based LLM 方法，**不涉及 LLM API 调用**
- 因此不存在 "LLM settings mismatch" 的问题

**三位 LLM-based baselines 的 LLM 使用情况总结：**

| Method | LLM 使用方式 | 是否使用 gpt-4o-mini | Mismatch? |
|---|---|---|---|
| GReaT | Fine-tune GPT-2 | 否（使用 GPT-2） | **不适用** — fine-tuning 方法无法使用 API 模型 |
| CLLM | Prompt-based generation | **是** — 与 StructSynth 完全相同 | **无 mismatch** |
| GraDe | 可训练 Transformer + functional dependencies | 否（使用自有模型） | **不适用** — 非 LLM API 方法 |

**结论：** 6JGG 的 "LLM settings mismatch" 批评 **在三个 LLM-based baseline 上均不成立**：
- CLLM：完全相同的 LLM 设置（论文已明确声明）
- GReaT：fine-tuning 方法，方法论上不适用相同的 LLM 设置
- GraDe：attention injection 方法，不涉及 LLM API 调用

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **质疑 1（默认超参数）部分合理**，但属于标准实践；**质疑 2（LLM mismatch）不成立**，论文已有直接反驳证据 |
| 审稿人可能忽略的点 | (1) Appendix 中 CLLM LLM 设置完全匹配的明确声明; (2) GReaT 是 fine-tuning 方法，不适用相同 LLM 设置; (3) GraDe 非 LLM API 方法; (4) SynthCity 默认配置是社区标准 |
| 反驳难度 | **低到中等**。质疑 2 有直接反驳证据；质疑 1 需要更细致的论证 |
| 评分提升可能性 | Reproducibility 有望从 1 提升到 2-3（直接反驳了不公平比较的指控） |

#### Rebuttal 策略

**核心论点：** 实验设计是公平的。(1) CLLM 使用了与 StructSynth 完全相同的 LLM 设置（Appendix 已明确声明）；(2) GReaT 和 GraDe 的方法论本质决定了它们不能/不需要使用相同的 LLM 设置；(3) 非 LLM baselines 使用 SynthCity 库默认配置是社区标准实践。

**具体回应（逐条反驳）：**

1. **LLM 设置匹配（对质疑 2 的直接反驳）：**
   - **CLLM**：引用 Appendix Section A.2.2 原文，CLLM 配置了与 StructSynth 完全相同的 LLM 设置（gpt-4o-mini, temperature=0.9, top_p=0.95 等）。Table 2 提供了完整的参数列表。
   - **GReaT**：解释这是一个 GPT-2 fine-tuning 方法。Fine-tuning 需要可训练的开源模型（GPT-2），不能使用 API 模型（gpt-4o-mini 不可 fine-tune）。使用 GPT-2 是方法论上的必要选择，不是设置不匹配。
   - **GraDe**：解释这是一个使用可训练 Transformer 的 attention injection 方法，将外部功能依赖注入 attention mask。它不使用 LLM API，因此不存在 LLM 设置匹配的问题。

2. **默认超参数（对质疑 1 的论证）：**
   - 强调使用 SynthCity 库（NeurIPS 2023）是合成数据评估的社区标准
   - 列举使用相同方法的先前工作（CLLM, TabDDPM, TabSyn 等）
   - 指出 StructSynth 的优势幅度（avg rank 1.00，远超第二名 2.67）不太可能完全由超参数解释
   - 如有余力，可对 TabSyn 和 CTGAN 进行简单的 grid search 补充验证

3. **额外公平性论证：**
   - StructSynth 也未针对各数据集进行超参数调优——所有数据集使用相同的 prompt templates 和参数
   - 消融实验（Table 3）在同一数据集上控制变量，公平性有保障

---

## 三、逐条 Question 回应框架

### Q1: StructSynth 与传统 LLM 生成方法的本质区别

**审稿人原文：** I wonder what's the fundamental difference between traditional LLM generation method and StructSynth

#### 回应框架

从三个维度论证本质区别：

| 维度 | 传统 LLM 方法（以 CLLM 为代表） | StructSynth |
|---|---|---|
| **结构建模** | 无显式结构——依赖 LLM 从 few-shot 数据中隐式学习特征间关系 | 显式构建 DAG——结构发现阶段独立于生成，提供可解释的依赖拓扑 |
| **生成策略** | 所有特征在一次 LLM 调用中生成，无约束的 autoregressive generation | 按拓扑层逐步生成，每层特征 **必须** 以其 DAG 父节点已生成值为条件（硬约束） |
| **正则化效应** | 无结构正则化——LLM 可能偏向 memorization 或偏离依赖关系 | DAG 作为 structural regularizer（审稿人在 Strengths 中已承认），同时防止 memorization 并保证依赖遵守 |

**量化证据：**

| 对比维度 | CLLM | StructSynth | 差异 |
|---|---|---|---|
| AUC (avg) | 73.36 | **75.01** | +1.65 |
| Privacy Rank | 3.33 | **1.33** | +2.00 |
| Ablation: No Structure | — | -1.6 pts | 结构引导的量化贡献 |

**核心论点：** 传统 LLM 方法是"结构盲"的（structure-blind）——它们只能从线性化的文本序列中隐式推断依赖关系。StructSynth 是"结构感知"的（structure-aware）——它首先显式发现依赖结构，然后 **强制** 生成过程遵循这一结构。这不是量变，而是质变。

---

### Q2: 如何确保 dependency DAG 的合理性

**审稿人原文：** ...and how ensure the dependency DAG of features is reasonable?

#### 回应框架

**第一层：定量验证（Ground-truth benchmarks）**

SHD 实验（`experiments.tex:152-159`，Figure 5）在三个有 ground-truth DAG 的 benchmark 上：

| Dataset | Nodes | StructSynth SHD | 优势 |
|---|---|---|---|
| Asia | 8 | ≈1（几乎完美恢复） | FCI/NoTears/GOGGLE 均显著更高 |
| Child | 20 | 低 SHD，避免级联错误 | GraDe 产生密集错误图 |
| Insurance | 27 | 低 SHD，中等规模网络优异 | DGM baselines 过拟合 |

测试范围覆盖 n=20, 50, 100, 200 四个样本量。

**第二层：多重保障机制**

| 机制 | 位置 | 功能 |
|---|---|---|
| Statistical cues | `methodology.tex:22-27` | 数据驱动的弱监督，矫正 LLM 先验偏差 |
| LLM reasoning | `methodology.tex:24-27` | 语义先验弥补小样本统计不稳定 |
| Reasoned cycle resolution | `methodology.tex:37-48` | 基于逻辑推理确保无环性 |
| Few-shot grounding | `methodology.tex:14, 26` | 实际数据样本锚定 LLM 的推理 |

**第三层：下游验证**

- Ablation: 替代发现算法（PC: -1.0, NoTears: -1.4）证实 graceful degradation
- Re-discovered graph（`appendix.tex:247-253`，Figure 8）：从合成数据中反向恢复的图与 reference graph 高度一致
- Asia 结构可视化（`appendix.tex:307-329`，Figure 9）：StructSynth 成功恢复 V-structure 和关键因果链

---

## 四、总体评估与建议

### Weakness 严重程度排序

| 排序 | Weakness | 严重程度 | 反驳难度 | Rebuttal 优先级 | 理由 |
|---|---|---|---|---|---|
| 1 | W3: 实验设计不公平 | **中（但论文有直接反驳证据）** | **低** | **最高** | "LLM mismatch" 批评不成立，直接反驳可快速得分并动摇审稿人的整体判断 |
| 2 | W2: 数据不可靠/与 LLM 无区别 | **中高** | **中等** | **高** | Multi-LLM + post-cutoff + ablation 三重证据链 |
| 3 | W1: 新颖性不足 | **高** | **中等偏高** | **高** | 最难反驳但影响最大（Novelty=1） |

### Rebuttal 整体策略

**第一阶段（快速得分，动摇审稿人信心）：W3 — 实验公平性**

这是 6JGG 最独特的批评，也是最容易反驳的。直接引用 Appendix 中的明确声明，指出 CLLM 的 LLM 设置完全匹配，GReaT 和 GraDe 的方法论本质决定了不适用"LLM settings match"的概念。

**为什么优先反驳 W3：**
- 如果审稿人接受了"实验不公平"的前提，后续所有反驳都将被削弱
- W3 有最直接的反驳证据（Appendix 原文），可以最快建立可信度
- 成功反驳 W3 可以动摇审稿人对其他批评的信心（"如果我对实验设计的判断有误，其他判断是否也需要重新考虑？"）

**第二阶段（核心论证）：W2 — 数据可靠性与本质区别**

用三重证据链反驳"与 LLM 无本质区别"：
1. Multi-LLM 泛化性（7 个模型一致优势）→ 方法优势不依赖特定 LLM
2. Post-cutoff 数据集（优势持续）→ 优势来自设计而非数据记忆
3. Ablation（No Structure = CLLM, -1.6 pts）→ 结构引导有量化贡献

**第三阶段（深度论证）：W1 — 新颖性**

不否认组件前身，但强调：
1. Hybrid discovery 的信号融合创新（非 minor tweak）
2. Reasoned cycle resolution 的新范式
3. 硬约束 vs 软约束的本质区别
4. 引用 ep8Q 的正面评价作为锚点

### 评分提升预期

| Criterion | 当前 | 预期提升 | 条件 |
|---|---|---|---|
| Novelty | **1** | 1→2 | 需要成功论证具体技术创新（即使提升到 2 也是显著进步） |
| Technical Quality | 2 | 2→3 | 成功反驳 W2（数据可靠性）和 W3（实验公平性） |
| Presentation | 2 | 2→3 | 通过清晰的 rebuttal 展示论文的深度 |
| Reproducibility | **1** | 1→2 或 1→3 | 直接反驳"LLM mismatch"，承诺代码开源 |
| Relevance | 3 | 维持 | — |

**注意：** 6JGG 的 Novelty=1 和 Reproducibility=1 是极端低分。在 AC 决策中，极端分数往往被中位数调和，但将 1 分提升到 2 分对最终决策仍有重要影响——它消除了"有审稿人认为论文在关键维度上 Poor"的负面信号。

---

## 五、Rebuttal 要点总结（Bullet Points）

### 针对新颖性（W1, Novelty）
- 新颖性不在于范式本身，而在于三个组件内部的技术创新：(1) hybrid discovery 的 LLM + statistical cues 信号融合，(2) reasoning-driven cycle resolution（区别于传统数值优化），(3) topological hard-constrained generation（区别于 GraDe 的 soft attention guidance）
- Ablation 量化了每个组件的非冗余贡献：移除统计信号 -1.5, 移除拓扑序 -1.1, 移除结构 -1.6, 替换 LLM 为 Bayesian Sampler -4.4
- 与 GraDe 的本质区别：硬结构约束 (by construction) vs 软 attention 引导
- Reviewer ep8Q 给出 Novelty=3 并评价"Novel and well-motivated framework"，说明新颖性判断存在审稿人间的分歧

### 针对数据可靠性（W2, Data Reliability）
- **Multi-LLM 泛化性**（Figure 6）：7 个不同 LLM 上一致优于 CLLM，证明方法优势来自框架设计而非特定 LLM 先验
- **Post-cutoff 数据集**：Anxiety 和 Salary 均在 LLM 知识截止后发布，StructSynth 优势持续（+1.28, +1.45），排除了"LLM 记忆数据"的解释
- **统计信号的数据驱动矫正**：BFS 过程中注入 Pearson's R / Cramér's V / Correlation Ratio，提供独立于 LLM 先验的实证证据
- **Abllation 直接反驳"无本质区别"**：No Structure (=CLLM) 导致 AUC -1.6 pts
- **6JGG 自己在 Strengths 中承认**：DAG 作为 structural regularizer 防止 training data memorization

### 针对实验公平性（W3, Experimental Fairness）— 最优先反驳
- **CLLM 的 LLM 设置完全匹配**：Appendix Section A.2.2 明确声明"it was configured with the same Large Language Model (LLM) settings as our proposed StructSynth"。Table 2 提供了完整参数：gpt-4o-mini, temperature=0.9, top_p=0.95, frequency_penalty=0, presence_penalty=0, max_tokens=8000
- **GReaT 是 fine-tuning 方法**（使用 GPT-2）：Fine-tuning 需要可训练的开源模型，不能使用 API 模型（gpt-4o-mini 不可 fine-tune）。使用 GPT-2 是方法论上的必要选择
- **GraDe 是 attention injection 方法**（使用可训练 Transformer + 外部功能依赖）：不涉及 LLM API 调用，不存在 LLM 设置匹配的问题
- **非 LLM baselines 使用 SynthCity 默认配置**：这是合成数据评估的社区标准实践（SynthCity, NeurIPS 2023），CLLM/TabDDPM/TabSyn 等先前工作均采用相同方法
- **StructSynth 的优势幅度**：avg rank 1.00（远超第二名 CLLM 2.67），不太可能完全由超参数选择解释

### 针对可复现性（Reproducibility=1）
- Appendix 提供了 5 个完整的 prompt templates（`appendix.tex:348-733`，5 个 tcolorbox）
- Appendix 提供了完整的 Algorithm 1 伪代码（`appendix.tex:355-420`）
- Appendix 提供了详细的 hyperparameter 列表（`appendix.tex:55-85`，Table 2）
- Appendix 提供了完整的 evaluation metric 定义（`appendix.tex:151-236`）
- 承诺论文接收后开源代码和完整实现
- **LLM 设置完全透明**：所有参数已公开，不存在隐藏的配置优势

### 针对 DAG 合理性的回应（Q2）
- SHD 实验（3 benchmarks × 4 sample sizes）：Asia SHD≈1，Child/Insurance 一致优势
- Hybrid discovery 双保障：LLM 语义先验 + 统计信号弱监督
- Reasoned cycle resolution：基于逻辑推理的图约束维护
- Ablation：替代发现算法的 graceful degradation（PC -1.0, NoTears -1.4）
- Re-discovered graph 反向验证：合成数据中恢复的图与 reference 高度一致
- Asia 可视化：成功恢复 V-structure 和关键因果链

---

## 六、与其他审稿人的交叉分析与统筹策略

### 6JGG 的独特关注点

| 关注点 | 6JGG | 其他审稿人 |
|---|---|---|
| 实验公平性（超参数 + LLM 设置） | ✓（W3） | 无 |
| LLM 先验偏差对数据可靠性的影响 | ✓（W2） | 无（f5xi 提及了结构错误传播，但角度不同） |
| 与纯 LLM 方法的本质区别 | ✓（W2, Q1） | hziw Q1（但更侧重 structure learning + generation 框架的区别） |

### 可复用的论据

| 为 6JGG 准备的论据 | 可复用于其他审稿人 |
|---|---|
| Ablation 量化非冗余贡献 | hziw W1, f5xi W4, ep8Q general |
| Multi-LLM 泛化性实验 | ep8Q Q2（ scalability） |
| Post-cutoff 数据集的持续优势 | ep8Q W2（data contamination） |
| SHD 实验 + graph 可视化 | hziw W4, f5xi W4 |
| Token usage 分析 | hziw Q5, f5xi W5 |
| CLLM LLM 设置匹配声明 | ep8Q W4（reproducibility） |

### 统筹建议

在 rebuttal 中，建议将 6JGG 的 W3（实验公平性）放在第一个回应。原因：
1. 这是 6JGG 独有的关注点，必须直接回应
2. 直接反驳"LLM mismatch"可以快速建立实验的可信度
3. 一旦实验公平性被建立，W1 和 W2 的反驳将更有说服力
4. CLLM 设置匹配的证据同时回应了 ep8Q 的 reproducibility 质疑
