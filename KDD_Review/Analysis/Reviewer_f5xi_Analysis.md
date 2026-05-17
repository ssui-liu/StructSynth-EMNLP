# Reviewer f5xi 审稿意见深度分析与评估

> **目标：** 结合论文原文，对 Reviewer f5xi 的 5 条 Weakness 进行逐一分析，评估其合理性，并为 rebuttal 提供论据和策略。

---

## 一、审稿人评分概览

| Criterion | Score | 评估 |
|---|---|---|
| Relevance | 3: Moderate | 偏低，与 hziw 一致 |
| Novelty | **2: Low** | 核心拉分项（但 f5xi 未直接质疑新颖性，该低分可能因技术质疑连带） |
| Technical Quality | **2: Low** | **核心拉分项**，f5xi 提出了 5 条具体技术质疑 |
| Presentation | 3: Moderate | 尚可 |
| Reproducibility | **2: Low** | 需补充代码承诺 |
| Reviewer Confidence | 3: Moderate | 中等自信度，有说服空间 |

### 与 Reviewer hziw 的评分对比

| Criterion | hziw | f5xi | 共同点 |
|---|---|---|---|
| Relevance | 3 | 3 | 均认为领域偏窄 |
| Novelty | 2 | 2 | 均给了低分 |
| Technical Quality | 2 | 2 | 均质疑技术深度 |
| Presentation | 3 | 3 | 均认为写作尚可 |
| Reproducibility | 2 | 2 | 均质疑可复现性 |

**关键差异：** 两位审稿人评分几乎一致，但 **质疑角度完全不同**。hziw 从宏观层面批评（新颖性不足、缺乏理论深度），而 f5xi 从微观层面质疑具体技术选择（DAG 假设、source node、统计保真度）。这意味着 **同一个 rebuttal 需要同时满足宏观和微观两个层面的反驳**。

**f5xi 的 Strengths 表明其认可论文方向：**
1. 问题定义清晰，动机有说服力
2. 两阶段设计直观，提高可解释性
3. 实验全面，fidelity-privacy trade-off 表现强

**结论：f5xi 认可"做什么"但质疑"怎么做"。** 反驳策略应聚焦于技术论证而非方向辩护。

---

## 二、逐条 Weakness 深度分析

### Weakness 1: DAG 假设的合理性 — 方向性 vs 关联性

#### 审稿人原文
> The formulation of inter-column dependency as a directed acyclic graph is not sufficiently justified. For tabular data, feature dependencies are often better viewed as associative rather than inherently directional, so the paper should better explain why a DAG is the right structural assumption here.

#### 审稿人批评的核心逻辑

审稿人认为：表格数据中的特征依赖通常是 **对称的/关联性的**（如 Age 和 Income 相关），而非 **方向性的**（Age → Income）。将关联关系强制编码为有向边是一种过强的假设，论文没有论证为什么这样做是合理的。

#### 论文中的反驳证据

**证据 1: 论文已明确声明 DAG 是功能性的而非本体论性的。**

Introduction 脚注（`introduction.tex:47`）：
> "Here, we use 'DAG' to denote a directed dependency graph: edges capture statistical/probabilistic dependencies inferred from limited observations and are used as a **generative blueprint**, not as a claim of ground-truth causality."

这一定位至关重要——DAG 不声称"X 导致 Y"，而是说"在我们的生成过程中，先观察 X 的值再生成 Y 的值"。

**证据 2: 方向性是生成阶段的功能需求，而非结构发现阶段的理论假设。**

Structure-Guided Synthesis（`methodology.tex:97-122`）中，DAG 的方向性用于确定 **topological ordering**：
- 节点被划分为拓扑层 $L_1, L_2, \ldots, L_m$
- 每层特征的生成以其父节点的已生成值为条件
- 公式：$\tilde{\mathbf{x}}_{j, L_i} = f_{\text{LLM}}(\pi_{\text{data\_gen}}(\tilde{\mathbf{x}}_{j, <i}, G_i, L_i, \mathcal{D}_{\text{few\_shot}}^i))$

即使底层依赖是对称的（如 Age ↔ Income），生成过程也 **必须** 选择一个方向——你不可能同时生成 Age 和 Income。DAG 提供的正是这个生成顺序。

**证据 3: 无向图无法直接用于 autoregressive 生成。**

考虑一个无向依赖图 $\{A - B, B - C\}$：
- 无向图无法确定先生成 A 还是先生成 C
- DAG $\{A \to B, B \to C\}$ 明确了生成顺序：先 A，再 B（以 A 为条件），再 C（以 B 为条件）
- 即使选择 $C \to B \to A$（反向），只要是一致的，生成结果也是合理的
- **方向的选择不影响依赖关系是否被捕获，只影响生成的条件化顺序**

**证据 4: 这一做法在 Bayesian Network 和结构学习文献中是标准的。**

- Bayesian Network（Pearl, 1988）将 DAG 作为条件独立性的编码工具
- PC 算法、NoTears 等经典方法均使用 DAG 建模依赖关系
- DAG 不等同于 causality——这是 BN 文献中的基本共识
- StructSynth 遵循了这一传统，只是用 LLM 替代了传统的统计学习方法

**证据 5: 无环性的实际需求。**

如果允许环（有向环状图），生成阶段会出现循环依赖——A 依赖 B 的值，B 又依赖 A 的值，无法确定先生成谁。无环性是 **可执行生成蓝图** 的数学前提。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理**。论文确实没有在正文中充分解释为什么选择 DAG 而非无向图——脚注虽有说明但容易被忽略 |
| 审稿人可能忽略的点 | (1) 脚注中的 generative blueprint 声明; (2) autoregressive 生成本质上需要方向性; (3) DAG 在 BN 文献中的标准用法 |
| 反驳难度 | **中等**。需要重新框定 DAG 的角色，但逻辑上是清晰的 |
| 评分提升可能性 | 可提升 Technical Quality 从 2 到 3 |

#### Rebuttal 策略

**核心论点：** DAG 在 StructSynth 中的角色是 **pragmatic（功能性的）** 而非 **ontological（本体论性的）**。我们不声称特征间存在因果关系，而是需要一个无环的有向结构来定义 autoregressive 生成的条件化顺序。即使底层依赖是对称的，生成过程也必须选择一个方向——DAG 提供的正是这个生成蓝图。

**具体回应：**
1. **引用脚注**（`introduction.tex:47`），强调 generative blueprint 的定位
2. **解释功能需求**：autoregressive 生成需要 topological order，无环性是数学前提，方向性是条件化需求
3. **与 BN 传统对齐**：DAG 是 BN 文献中编码条件独立性的标准工具，不等同于 causality
4. **承认可改进**：论文可在未来工作中探索无向图 + 生成顺序启发式的替代方案

---

### Weakness 2: Source Node 识别的可靠性与适用性限制

#### 审稿人原文
> The proposed graph construction procedure seems to depend on identifying variables that are not influenced by others as starting points. It is unclear how the method would work when such source nodes do not exist or cannot be reliably identified, which may limit its applicability.

#### 审稿人批评的核心逻辑

BFS 结构发现需要一个起始点——source nodes（不被其他变量影响的特征）。如果：
- (a) 数据集中没有真正的 source node（所有变量互相关联）
- (b) LLM 无法可靠地识别 source node

则方法可能失败或产生不可靠的结构。

#### 论文中的反驳证据

**证据 1: Source node 识别是起点而非终点。**

BFS 机制的设计确保：
1. Source nodes 仅决定 **探索顺序**，而非最终结构
2. 每个被探索的节点会提出自己的后继节点（`methodology.tex:20-35`），逐步覆盖所有特征
3. Cycle resolution（`methodology.tex:37-48`）确保即使初始选择引入了环，也能被修正

即：**即使 source node 识别不完美，BFS 扩展 + cycle resolution 提供了自适应纠错机制。**

**证据 2: 实践中所有数据集均成功运行。**

论文在 9 个数据集上进行了实验（6 个 real-world + 3 个 benchmark）：
- Adult（15 features）, Anxiety（19 features）, Compas（8 features）
- Salary（18 features）, Obesity（15 features）, Churn（12 features）
- Asia（8 nodes）, Child（20 nodes）, Insurance（27 nodes）

所有数据集均成功识别了 source nodes 并完成了结构发现。特别是 Insurance（27 nodes）的成功说明方法在相对复杂的结构上也可行。

**证据 3: 大多数表格数据集具有自然的"根特征"。**

在论文使用的数据集中：
- Adult: Age, Sex, Country 等天然是根特征（不受其他变量影响）
- Anxiety: 年龄、性别等人口统计变量
- Asia (benchmark): asia（地区）、smoke（吸烟）是经典的根节点

审稿人担心的"所有变量互相关联、无根节点"的场景在实践中较少出现。

**证据 4: 即使无真正的 source node，方法也有退化策略。**

在最坏情况下（所有特征互相关联）：
- LLM 可以选择"最独立"的特征（关联分数最低的）作为起点
- 或者将所有特征同时作为初始节点（$Q \leftarrow V_{\text{all}}$），退化为 pairwise discovery
- Ablation 中 Pairwise Discovery（`experiments.tex:133`）的 AUC 为 85.25（vs. StructSynth 85.55），说明退化策略的性能损失很小

**证据 5: Source Node Prompt 的设计。**

`appendix.tex:482-525` 中的 prompt 设计：
- 不仅要求识别 source node，还要求 LLM 基于 feature descriptions 和 data 进行推理
- Prompt 提供了 all features 的描述和 few-shot data 作为上下文
- LLM 的语义理解能力使其能识别"在这个数据集中，哪些特征是基础性的"

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **理论上有理，但实践中影响有限**。"无 source node"是极端情况 |
| 审稿人可能忽略的点 | (1) BFS 扩展会覆盖所有节点; (2) cycle resolution 提供纠错; (3) 9 个数据集均成功; (4) 退化策略存在 |
| 反驳难度 | **中低**。有大量实证证据 |
| 评分提升可能性 | 可提升审稿人对方法适用性的信心 |

#### Rebuttal 策略

**核心论点：** Source node 识别是 BFS 的起点而非方法成功的瓶颈。BFS 扩展机制确保所有节点最终被探索，cycle resolution 提供自适应纠错，9 个数据集的实验验证了方法的广泛适用性。

**具体回应：**
1. **澄清 source node 的角色**：它仅决定探索顺序，不影响最终结构的完整性
2. **引用实验证据**：9 个数据集（包括 27-node Insurance）均成功运行
3. **解释纠错机制**：cycle resolution 和 BFS 迭代提供了多层保障
4. **讨论退化策略**：即使无真正的 source node，可选择"最独立"特征或所有特征作为起点，Pairwise Discovery ablation 证实退化策略的可行性（AUC 85.25 vs 85.55）

---

### Weakness 3: 统计保真度未达预期（核心难点）

#### 审稿人原文
> The method explicitly introduces dependency discovery and statistical signals to improve structural consistency, so one would expect stronger statistical fidelity than prior LLM-based methods such as GReaT and GraDe. However, the reported results do not clearly support this expectation, and the current explanation is not fully convincing.

#### 审稿人批评的核心逻辑

这是一个 **内部一致性** 的批评：
1. 论文声称：引入显式结构发现 → 改善结构一致性
2. 自然预期：Statistical Fidelity 应优于不使用显式结构的方法
3. 实际结果：StructSynth 的 Statistical Fidelity（avg rank 7.08）远不如 GReaT（avg rank 3.33）
4. 结论：论文的解释不令人信服

#### 关键数据对比

**Statistical Fidelity（越低越好）：**

| Method | Type | Adult | Anxiety | Compas | Salary | Obesity | Churn | **Avg** | **Rank** |
|---|---|---|---|---|---|---|---|---|---|
| NFlow | DGM | 50.68 | **43.50** | 60.62 | **52.38** | 58.85 | 53.98 | **53.34** | 4.50 |
| GReaT | LLM | 82.71 | **40.10** | **52.17** | 58.75 | **56.83** | **48.18** | **56.46** | **3.33** |
| GraDe | LLM | 84.30 | 42.59 | 53.82 | 55.85 | 57.44 | 53.66 | 57.94 | 4.17 |
| StructSynth | Ours | 57.60 | 57.86 | 57.23 | 64.64 | 61.14 | 58.63 | 59.52 | 7.08 |

StructSynth 在 Fidelity 上排名第 7/12，确实不是优势维度。

**但 Privacy Risk（越接近 0.5 越好）揭示了真相：**

| Method | Adult | Anxiety | Compas | Salary | Obesity | Churn | **Avg** | **Rank** |
|---|---|---|---|---|---|---|---|---|
| GReaT | 99.50 | 85.39 | 94.10 | 86.66 | 80.75 | 94.51 | **90.15** | 11.83 |
| GraDe | 97.51 | 61.14 | 75.11 | 65.99 | 59.30 | 69.07 | **71.35** | 9.50 |
| StructSynth | **49.97** | **44.74** | **62.37** | **50.13** | **49.80** | **48.67** | **50.95** | **1.33** |

**Downstream Performance（越高越好）：**

| Method | Avg Score | Rank |
|---|---|---|
| StructSynth | **75.01** | **1.00** |
| CLLM | 73.36 | 2.67 |
| GReaT | 69.25 | 6.00 |
| GraDe | 62.73 | 7.33 |

#### 深层分析

**为什么 GReaT 有更高的 Statistical Fidelity？**

GReaT 是 fine-tuning 方法——它直接在训练数据上微调 GPT-2，学习数据的 token-level 分布。这意味着：
- GReaT **记忆了训练数据的精确统计特性**（pairwise correlations）
- 但这种记忆导致了严重的 privacy 泄露（Privacy Risk 90.15%）
- GReaT 本质上是在"过拟合统计量"，而非"理解依赖结构"

**为什么 StructSynth 的 Statistical Fidelity 较低？**

StructSynth 使用 **prompt-based generation**（不 fine-tune）：
- LLM 不直接记忆训练数据的统计量
- 结构蓝图作为正则化器，引导 LLM 遵循依赖关系而非复制具体数值
- 这导致了 pairwise correlation 的近似但不精确的复现
- 但换来了最佳的 privacy 保护和最高的 downstream utility

**关键洞察：Statistical Fidelity 衡量的是 pairwise correlation，而非 conditional dependency。**

论文的 Statistical Fidelity metric 定义为（`appendix.tex:203-236`）：
$$\text{StatisticalFidelity} = \frac{1}{\binom{K}{2}} \sum_{1 \le i < j \le K} \Delta(C_i, C_j)$$

这衡量的是 **所有特征对** 的统计相似度，包括：
- DAG 中编码的父子依赖（StructSynth 优化的目标）
- DAG 中未编码的间接/虚假关联（StructSynth 有意忽略的）

StructSynth 的 DAG 只编码了 **最重要的依赖路径**，而非所有可能的 pairwise correlation。如果两个特征在 DAG 中不直接相连但统计相关（因为共同原因），StructSynth 不会强制复现这种间接关联——这是设计选择，不是缺陷。

**Ablation 的佐证：**

| Method | AUC | Fidelity | Privacy |
|---|---|---|---|
| StructSynth | **85.55** | 57.96 | 49.97 |
| Bayesian Sampler | 81.17 | **48.86** | 50.02 |
| No Structure (CLLM) | 83.95 | 60.67 | 49.45 |

Bayesian Sampler 的 Fidelity 最佳（48.86）但 AUC 最低（81.17），说明 **Fidelity 和 Utility 之间不是简单的正相关**。更高的 pairwise correlation 复现度并不一定带来更好的下游性能。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **高度合理**。这是 f5xi 最尖锐的批评，论文确实没有正面回答这个问题 |
| 审稿人可能忽略的点 | (1) GReaT 的高 fidelity 来自 memorization; (2) Fidelity metric 衡量的是 pairwise correlation 而非 conditional dependency; (3) Fidelity ≠ Utility |
| 反驳难度 | **中高**。需要精细论证，不能简单否认 |
| 评分提升可能性 | 如果论证得当，可显著提升 Technical Quality |

#### Rebuttal 策略

**核心论点：** StructSynth 优化的不是 pairwise statistical fidelity，而是 **conditional dependency fidelity + privacy preservation**。GReaT 的高 pairwise fidelity 来自 fine-tuning 导致的训练数据 memorization（Privacy Risk 90.15%），而 StructSynth 通过结构蓝图作为正则化器，在不记忆训练数据的前提下实现了最佳下游性能。

**具体回应（四步论证）：**

1. **承认观察的准确性**：是的，StructSynth 的 pairwise fidelity 不是最优的。

2. **揭示 GReaT/GraDe 高 fidelity 的真实原因**：
   - GReaT: fine-tuning → 记忆训练数据 → Privacy Risk 90.15%（几乎每条合成数据的最近邻都在训练集中）
   - GraDe: attention-based → 部分 memorization → Privacy Risk 71.35%
   - 对比：StructSynth Privacy Risk 50.95%（几乎无 memorization）
   - **结论：GReaT/GraDe 的高 fidelity 来自 memorization，不是来自更好的结构理解**

3. **重新框定目标**：
   - StructSynth 的目标不是精确复现所有 pairwise correlations
   - 而是捕获 **DAG 编码的依赖关系** 并保持隐私安全
   - 这正是 downstream utility 所衡量的（StructSynth rank 1.00 vs GReaT rank 6.00）

4. **补充 conditional dependency 分析**（如有余力）：
   - 可以在 rebuttal 中计算 DAG 中编码的父子对的 correlation fidelity
   - 预期：StructSynth 在 conditional dependency fidelity 上应显著优于 baseline
   - 这将直接回应审稿人的期望："引入了结构发现 → 结构一致性应更好"

---

### Weakness 4: 结构错误的传播

#### 审稿人原文
> This also raises a broader concern that errors in the discovered dependency structure may propagate to the generation stage. Since the whole framework relies on the quality of the inferred structure, the paper should provide more discussion on how robust the method is when the discovered graph is imperfect.

#### 论文中的反驳证据

**证据 1: SHD 实验直接量化了结构发现质量。**

Figure 5（`experiments.tex:152-159`）在三个有 ground-truth DAG 的 benchmark 上：

| Dataset | Nodes | StructSynth SHD | Baseline 对比 |
|---|---|---|---|
| Asia | 8 | ≈1（几乎完美） | FCI/NoTears/GOGGLE 均显著更高 |
| Child | 20 | 低 SHD，避免级联错误 | GraDe 产生密集错误图 |
| Insurance | 27 | 低 SHD，中等规模网络表现优异 | DGM baselines 过拟合 |

SHD 实验在 n=20, 50, 100, 200 四个样本量上进行了测试，StructSynth 在所有设置下均保持最低或接近最低的 SHD。

**证据 2: Ablation 量化了结构不完美时的 graceful degradation。**

| 替代结构 | 与 StructSynth 的结构差异 | AUC 影响 | 解读 |
|---|---|---|---|
| PC Discovery | 不同发现算法 → 不同结构 | -1.0 pts | 中等容错 |
| NoTears Discovery | 不同发现算法 → 不同结构 | -1.4 pts | 中等容错 |
| No Topological Order | 结构正确但生成顺序错误 | -1.1 pts | 顺序容错 |
| No Structure | 完全无结构 | -1.6 pts | 结构有价值但不致命 |

关键发现：**即使替换为完全不同的结构发现算法（PC/NoTears），性能退化仅为 1.0-1.4 AUC pts**，远小于移除 LLM 的退化（-4.4 pts）。这说明：
- 结构是重要的（No Structure -1.6）
- 但结构不需要完美（PC/NoTears -1.0/-1.4）
- **LLM 的生成能力可以部分弥补结构误差**

**证据 3: Re-discovered Graph 反向验证了结构保真。**

Appendix Figure 8（`appendix.tex:247-253`）展示了：
- (a) Reference graph（PC algorithm + domain expertise）
- (b) StructSynth LLM-discovered graph
- (c) 从 StructSynth 合成数据中 re-discovered graph

(b) 和 (a) 的高度一致性证明了结构发现的质量；(c) 和 (a) 的高度一致性证明了 **合成数据确实编码了发现的依赖结构**。

**证据 4: Asia 数据集的结构对比可视化。**

Appendix Figure 9（`appendix.tex:307-329`）详细展示了各方法在 Asia 上的结构：
- StructSynth：成功恢复 V-structure at dysp 和 smoke→lung 链
- GraDe：过度密集，大量虚假边
- GOGGLE：边反转（lung→smoke），遗漏关键连接
- NoTears：稀疏且碎片化，遗漏核心关系
- FCI：多边未定向

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理但论文已有大量证据**。审稿人可能没有注意到 SHD 实验和 ablation 分析 |
| 审稿人可能忽略的点 | (1) Section 4.4 的 SHD 实验; (2) Table 3 的 ablation; (3) Appendix 的 graph 可视化 |
| 反驳难度 | **低**。直接引用已有证据 |
| 评分提升可能性 | 可提升 Technical Quality |

#### Rebuttal 策略

**核心论点：** 论文已从三个层面提供了结构可靠性的证据：(1) SHD 定量评估（3 benchmarks, 4 sample sizes）; (2) Ablation 容错性分析（1.0-1.4 pts graceful degradation）; (3) Graph 可视化定性验证。即使结构不完美，框架展现出良好的容错性。

**具体回应：**
1. **引用 SHD 实验**：三个 benchmarks 上的一致优势，特别是 Asia 的 SHD≈1
2. **引用 ablation 数据**：PC/NoTears 替换仅导致 1.0-1.4 pts 退化
3. **引用 graph 可视化**：LLM-discovered graph 与 reference graph 高度一致
4. **强调 graceful degradation**：结构是 blueprint 而非生死攸关的瓶颈，LLM 的生成能力提供了容错缓冲

---

### Weakness 5: 重复 LLM 调用的计算开销

#### 审稿人原文
> The approach appears to require repeated LLM calls during structured generation, which could introduce substantial computational overhead. The paper would be stronger if it discussed inference cost, runtime, and scalability more explicitly, especially for tables with many columns.

#### 论文中的反驳证据

**证据 1: 详细的 Token Usage 分析（Appendix Table 4, `appendix.tex:255-305`）。**

| 指标 | CLLM | StructSynth | 差异 |
|---|---|---|---|
| Avg Total Tokens | 219.8K | 287.9K | +68.1K (**+31.0%**) |
| Avg Input Tokens | 114.1K | 179.2K | +65.1K (+57.1%) |
| Avg Output Tokens | 105.8K | 108.7K | +2.9K (+2.7%) |
| Graph Stage Tokens | — | 58.8K | 一次性结构发现成本 |

**证据 2: Overhead 的特性分析。**

- **Input-dominant**：Input +57%, Output 仅 +3%
- 在主流 LLM 定价中（如 GPT-4o-mini: input $0.15/M, output $0.60/M），output token 4x 贵于 input
- 因此 **实际货币成本增幅远低于 31%**
- 粗略估算：货币成本增幅约 +15-20%

**证据 3: BFS 策略的高效性。**

- 结构发现阶段使用 BFS 而非 pairwise comparison
- BFS 的 LLM 调用次数为 **O(K)**（K=特征数），而非 O(K²)
- Pairwise Discovery ablation（`experiments.tex:133`）：
  - Pairwise: AUC 85.25, 使用更多 token
  - BFS (StructSynth): AUC 85.55, 使用更少 token
  - **BFS 不仅更高效，性能也更好**

**证据 4: 多列场景的可扩展性验证。**

- Insurance benchmark：27 nodes（相对复杂的结构）
- StructSynth 在 Insurance 上仍保持低 SHD，说明方法在多列场景下可行
- Salary 数据集：18 features，token overhead 仅 +23.1%（所有数据集中最低之一）

**证据 5: 多 LLM 泛化性实验。**

Figure 6（`experiments.tex:194-198`）展示了在 7 个不同 LLM 上的一致优势，包括：
- 开源模型：Qwen-2.5, Llama-4, DeepSeek
- 闭源模型：GPT-4o 系列
- 说明方法不限于昂贵的大模型，可以使用成本更低的模型

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理但论文已有详细分析**（主要在 Appendix 中，正文仅 3 行） |
| 审稿人可能忽略的点 | (1) Appendix Table 4 的详细 token 分析; (2) BFS vs Pairwise 的效率对比; (3) 多 LLM 泛化性 |
| 反驳难度 | **低**。直接引用 Appendix 数据 |
| 评分提升可能性 | 可缓解审稿人对实用性的担忧 |

#### Rebuttal 策略

**核心论点：** 论文已在 Appendix 中提供了逐数据集、input/output 分离的 token 级成本分析。+31% 的 token 开销以 input token 为主，实际货币成本增幅约 15-20%。BFS 策略确保 O(K) 的调用复杂度，Insurance（27 nodes）实验验证了多列场景的可扩展性。

**具体回应：**
1. **引用 token 分析**：+31% overhead, input-dominant, 实际货币成本 ~+15-20%
2. **强调 BFS 效率**：O(K) 调用次数，优于 pairwise 的 O(K²)
3. **引用 Insurance 实验**：27 nodes 成功运行
4. **引用多 LLM 实验**：方法在低成本开源模型上同样有效

---

## 三、总体评估与建议

### Weakness 严重程度排序

| 排序 | Weakness | 严重程度 | 反驳难度 | Rebuttal 优先级 | 理由 |
|---|---|---|---|---|---|
| 1 | W5: 计算开销 | **低** | **低** | **最高** | 论文已有详细分析，直接引用即可快速得分 |
| 2 | W4: 结构错误传播 | **低-中** | **低** | **高** | SHD + ablation + 可视化，证据充分 |
| 3 | W2: Source node 可靠性 | 中 | **中低** | **高** | 9 个数据集验证 + BFS 纠错机制 |
| 4 | W1: DAG 假设合理性 | 中 | **中等** | **高** | 需要重新框定，但逻辑清晰 |
| 5 | W3: 统计保真度落差 | **高** | **中高** | **最高** | 最尖锐的批评，需要精细四步论证 |

### Rebuttal 整体策略

**第一阶段（快速得分）：** 先回应 W4 和 W5——直接引用论文中已有的 SHD 实验、ablation 和 token usage 分析。这能快速建立论文的技术深度，为后续更难的论证奠定基础。

**第二阶段（核心论证）：** 重点回应 W3——这是 f5xi 最独特的批评，也是最能改变评分的。四步论证：承认观察 → 揭示 GReaT memorization → 重新框定目标 → 补充 conditional dependency 分析。

**第三阶段（方法论澄清）：** 回应 W1 和 W2——澄清 DAG 的功能性角色和 source node 的纠错机制。

### 评分提升预期

| Criterion | 当前 | 预期提升 | 条件 |
|---|---|---|---|
| Novelty | 2 | 2→3 | f5xi 未直接质疑新颖性，如果技术质疑被有效回应可能连带提升 |
| Technical Quality | 2 | 2→3 | 需要成功回应 W3（统计保真度）和 W1（DAG 假设） |
| Reproducibility | 2 | 2→3 | 承诺代码开源 |
| Presentation | 3 | 维持 | — |
| Relevance | 3 | 维持 | — |

---

## 四、Rebuttal 要点总结（Bullet Points）

### 针对 DAG 假设（W1）
- DAG 在 StructSynth 中是 **generative blueprint** 而非 causality 声明（论文脚注已有说明）
- 方向性是 autoregressive 生成的功能需求：必须确定先生成哪个特征
- 无环性是可执行生成蓝图的数学前提（避免循环依赖）
- 与 Bayesian Network 文献的 DAG 用法一致：编码条件独立性，不等同于因果

### 针对 Source Node 可靠性（W2）
- Source node 仅决定 BFS 的探索起点，不影响最终结构的完整性
- BFS 扩展确保所有节点最终被探索，cycle resolution 提供自适应纠错
- 9 个数据集（6 real-world + 3 benchmark，最大 27 nodes）均成功运行
- 退化策略存在：Pairwise Discovery ablation 证实无 source node 策略的可行性（AUC 85.25 vs 85.55）

### 针对统计保真度（W3）— 核心回应
- **承认 pairwise fidelity 不是最优维度**
- **揭示 GReaT/GraDe 高 fidelity 的代价**：GReaT Privacy Risk 90.15%（严重 memorization），GraDe 71.35%
- **StructSynth 的结构蓝图 = 正则化器**：在不记忆训练数据的前提下捕获核心依赖
- **Fidelity ≠ Utility**：Bayesian Sampler fidelity 最佳（48.86）但 AUC 最低（81.17）
- **StructSynth 的核心优势**：Downstream Utility rank 1.00 + Privacy rank 1.33
- **未来可补充**：Conditional dependency fidelity（DAG 编码的父子对的 correlation fidelity）

### 针对结构错误传播（W4）
- SHD 实验（3 benchmarks × 4 sample sizes）直接量化了结构质量
- Ablation：替代发现算法仅导致 1.0-1.4 AUC 退化（graceful degradation）
- Graph 可视化：LLM-discovered graph 与 reference graph 高度一致
- Re-discovered graph：从合成数据中反向验证了结构保真

### 针对计算开销（W5）
- +31% token overhead，以 input token 为主（+57% input, +3% output）
- 实际货币成本增幅约 15-20%（output token 通常 3-5x 贵于 input）
- Graph stage 平均仅 58.8K tokens（一次性结构发现成本）
- BFS 复杂度 O(K)，Insurance（27 nodes）验证了多列可扩展性
- 7 个 LLM 上均有效，不限于昂贵模型

### 针对可复现性
- Appendix 提供了 5 个完整的 prompt templates
- Appendix 提供了完整的 Algorithm 1 伪代码
- 承诺论文接收后开源代码和完整实现
- Hyperparameter 详细配置已提供（Appendix Table 2）
