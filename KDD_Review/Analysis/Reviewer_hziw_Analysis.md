# Reviewer hziw 审稿意见深度分析与评估

> **目标：** 结合论文原文，对 Reviewer hziw 的每条 Weakness 和 Question 进行逐一分析，评估其合理性，并为 rebuttal 提供论据和策略。

---

## 一、审稿人评分概览

| Criterion | Score | 评估 |
|---|---|---|
| Relevance | 3: Moderate | 偏低，但提升空间有限（取决于 KDD 社区对 tabular synthesis 的兴趣） |
| Novelty | **2: Low** | **核心拉分项**，需重点反驳 |
| Technical Quality | **2: Low** | **核心拉分项**，需重点反驳 |
| Presentation | 3: Moderate | 尚可，非主要问题 |
| Reproducibility | **2: Low** | 需在 rebuttal 中补充代码/细节承诺 |
| Reviewer Confidence | 3: Moderate | 审稿人自信度中等，说明其判断有一定弹性 |

**总体判断：** Reviewer hziw 的评分偏低但集中在 Novelty 和 Technical Quality 上。这两个维度是 rebuttal 的核心战场。Presentation 和 Reproducibility 的低分可以通过补充材料改善。审稿人 Confidence 为 3（中等），意味着有力的反驳有可能改变其评分。

---

## 二、逐条 Weakness 深度分析

### Weakness 1: 新颖性不足 — "模块整合而非基础创新"

#### 审稿人原文
> Although the paper proposes a two-stage "structure discovery + data generation" framework, similar paradigms already exist, and the overall pipeline shows limited fundamental novelty beyond module integration.

#### 论文中的反驳证据

**证据 1: 并非简单整合，而是针对现有范式的结构性缺陷提出了新的解决方案。**

论文 `introduction.tex:24-39` 明确分析了三类现有范式各自的结构性瓶颈：

| 范式 | 代表方法 | 核心缺陷 |
|---|---|---|
| Deep Generative Models (DGMs) | TVAE, CTGAN, TabDDPM | 隐式学习依赖关系，在低数据下严重退化 |
| Structure-Aware Methods | BN, DECAF, GOGGLE | 依赖准确的结构图，但图发现在数据稀缺时不稳定 |
| LLM-based Methods | GReaT, CLLM, GraDe | 从线性化文本中隐式推断依赖，忽略显式结构 |

StructSynth 的核心创新在于识别了这三类范式的共同盲点——**无法在数据稀缺时同时实现可靠的结构发现和高质量的生成**——并提出了一个系统性的解决方案。

**证据 2: 技术创新体现在三个具体层面，而非简单的模块拼接。**

1. **Hybrid Discovery 机制**（`methodology.tex:20-35`）：将 LLM 的语义先验与统计关联信号（Pearson's R, Cramér's V, Correlation Ratio）相结合。这不同于：
   - 纯统计方法（PC, NoTears）——依赖大量样本的统计检验
   - 纯 LLM 方法——缺乏数据驱动的实证基础
   - Ablation 证实：移除统计信号后 AUC 下降 1.5 pts（`experiments.tex:145`，No-Correlation Score: 84.06 vs. 85.55）

2. **Reasoned Cycle Resolution**（`methodology.tex:37-48`）：当候选边集引入环时，LLM 基于每条边的文本 rationale 进行冲突分析和剪枝。这是一个新颖的、推理驱动的图约束机制，而非简单的启发式去环。传统方法通常：
   - 直接丢弃后添加的边（贪心策略）
   - 使用评分函数选择（无法利用语义信息）

3. **Structure-Conditioned Generation with Topological Layering**（`methodology.tex:97-122`）：
   - 将 DAG 节点划分为拓扑层，按层生成，每层特征以其父节点值为条件
   - Ablation 证实：移除拓扑序（No Topological Order）AUC 下降 1.1 pts；移除整个结构（No Structure）下降 1.6 pts
   - 这不是简单的 autoregressive generation，而是 **结构约束的、按依赖层级逐步展开的条件生成**

**证据 3: Ablation study 验证了各组件的非冗余贡献。**

| 变体 | AUC | Δ vs. StructSynth |
|---|---|---|
| StructSynth (Full) | **85.55** | — |
| PC Discovery | 84.54 | -1.01 |
| NoTears Discovery | 84.17 | -1.38 |
| No-Correlation Score | 84.06 | -1.49 |
| No Topological Order | 84.41 | -1.14 |
| No Structure (= CLLM) | 83.95 | -1.60 |
| Bayesian Sampler | 81.17 | -4.38 |

如果只是"模块整合"，替换任一模块不应导致如此显著的性能差异。每个组件的独立贡献被量化验证。

**证据 4: 与最相近的工作 GraDe 的本质区别。**

GraDe（`related_works.tex:21`）将学习到的稀疏依赖图注入 attention 机制，这是一种 **软约束**——模型仍然可以偏离依赖结构。StructSynth 的拓扑序生成是 **硬约束**——生成过程按构造遵守依赖关系（by construction）。这是方法论层面的根本差异。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理**。discover-then-synthesize 范式确实不新（Bayesian Network 即可视为该范式），审稿人的批评有据可依 |
| 审稿人可能忽略的点 | (1) Hybrid discovery 的创新性; (2) Reasoned cycle resolution 的新颖性; (3) 硬约束 vs 软约束的本质区别 |
| 反驳难度 | **中等**。需要在"范式不新"和"具体技术有创新"之间找到平衡 |
| 评分提升可能性 | Novelty 有望从 2 提升到 3 |

#### Rebuttal 策略

**核心论点：** 新颖性不在于"discover-then-synthesize"范式本身，而在于 **如何** 在低数据条件下可靠地实现每个阶段，以及两个阶段之间的协同设计。

**具体回应：**
1. 明确列出三个技术创新点（hybrid discovery, reasoned cycle resolution, topological generation），并分别与最相近的 prior work 对比
2. 用 ablation 数据说明每个创新点的独立贡献（非冗余）
3. 强调 StructSynth 与 GraDe 的根本区别：硬结构约束 vs 软 attention 引导

---

### Weakness 2: 低数据场景适用性缺乏专项机制

#### 审稿人原文
> While targeting low-data scenarios, the method mainly relies on LLM reasoning without specific mechanisms for small-sample instability, and is equally applicable to large-data settings, weakening its core motivation.

#### 论文中的反驳证据

**证据 1: LLM prior knowledge 本身就是一种对抗小样本不稳定性的机制。**

论文的核心洞察是（`introduction.tex:34-39`）：当样本量有限时，纯统计方法（如 PC 算法）的关联检验变得不可靠，但 LLM 的语义先验可以弥补这一缺陷。这不是"没有机制"，而是 **将 LLM 的领域知识作为小样本下的结构化正则化器**。

SHD 实验（`experiments.tex:152-159`）直接证实了这一点：

| 数据集 | StructSynth 的优势 |
|---|---|
| Asia (8 nodes) | 在 n=20 时 SHD≈1，而传统方法大幅波动 |
| Child (20 nodes) | 在低样本下避免了误差级联，而 GraDe 等方法产生密集错误图 |
| Insurance (27 nodes) | 通过优先发现稳定的"结构蓝图"避免了过拟合 |

**证据 2: Varying-n 实验展示了低数据下的独特优势。**

Figure 4（`experiments.tex:162-181`）在 Adult 数据集上测试了 n=20 到 200：

- **AUC**：StructSynth 在 n≤50 时优势最显著，BN 和 GOGGLE 需要显著更多样本才能竞争
- **Statistical Fidelity**：StructSynth 在所有样本量下保持稳定的低分数，而 baseline 常出现 fidelity 与 AUC 不同步改善的问题
- **Privacy**：StructSynth 的 Δ=|PrivacyRisk-0.5| 在所有 n 下接近零，展现了稳定的隐私-保真权衡

这表明方法 **确实在低数据下最为有效**，虽然它也适用于更大样本量。

**证据 3: Ablation 证实了低数据下各组件的特殊价值。**

- PC Discovery（纯统计方法）在 n=100 时 AUC 已落后 1.0 pts（`experiments.tex:130`），在更低样本量下差距只会更大
- No-Correlation Score 变体证实了统计信号作为弱监督的价值（`experiments.tex:145`："removing statistical prompts degrades performance, highlighting their value as weak supervision"）

**证据 4: 关于"同样适用于大数据场景"的反驳。**

审稿人认为方法的通用性削弱了低数据动机，但这一逻辑有缺陷：
- 一个方法可以在低数据场景下特别有效，同时在大数据下也有竞争力——这恰恰说明方法的鲁棒性
- 论文的核心贡献是解决低数据下的结构发现问题，而非故意限制方法的适用范围
- Figure 4 的趋势实际上显示，随着 n 增大，StructSynth 与 baseline 的差距缩小（因为更多数据让所有方法受益），说明 **低数据确实是 StructSynth 的优势区间**

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理**。论文确实没有显式的"小样本正则化"模块（如 sample weighting, bootstrapping 等），但 LLM prior 本身起到了这一作用 |
| 审稿人可能忽略的点 | (1) LLM prior 作为 implicit regularizer 的角色; (2) SHD/varying-n 实验中低数据下的显著优势; (3) 方法通用性≠低数据动机无效 |
| 反驳难度 | **中低**。论文有充分的实验证据支持低数据优势 |
| 评分提升可能性 | Technical Quality 有望从 2 提升到 3 |

#### Rebuttal 策略

**核心论点：** LLM 的语义先验 + 统计弱监督 = 低数据场景下的结构化正则化器。方法在低数据下的优势已被 SHD 实验和 varying-n 实验量化验证。

**具体回应：**
1. 指出审稿人将"专项机制"狭义地理解为显式正则化模块，而忽视了 LLM prior 本身的正则化效应
2. 用 Figure 5 (SHD) 和 Figure 4 (varying-n) 数据说明 low-data advantage
3. 强调方法通用性是优点而非缺点，但核心贡献在于低数据场景

---

### Weakness 3: 隐私评估指标合理性

#### 审稿人原文
> The privacy metric based on nearest-neighbor matching is insufficiently justified and not compared with standard approaches (e.g., membership inference), limiting the credibility of the privacy claims.

#### 论文中的反驳证据

**证据 1: Nearest-Neighbor Privacy Risk 有明确的理论依据和社区使用。**

- 论文引用了 `van2023membership`（`experiments.tex:17`）作为该指标的理论基础
- 该指标在合成数据社区被广泛采用，包括 SDV、SynthCity 等主流合成数据框架
- Appendix（`appendix.tex:176-201`）提供了完整的数学定义：
  - 对每个合成样本 $\tilde{x}$，找到其在所有真实数据（train ∪ test）中的最近邻
  - Privacy Risk = 最近邻落在训练集的比例
  - 理想值 0.5 表示合成数据与训练集和测试集等距

**证据 2: 该指标衡量的是与 MIA 互补的隐私维度。**

| 指标 | 衡量内容 | 与 memorization 的关系 |
|---|---|---|
| NN Privacy Risk | 合成数据是否过度复制训练样本 | 直接衡量 record-level memorization |
| Membership Inference | 能否判断某条记录是否在训练集中 | 衡量 model-level 信息泄露 |

两者不是替代关系，而是互补关系。NN Privacy Risk 关注的是 **合成数据的保真度来源**——高保真是因为学到了分布，还是因为记住了训练样本？

**证据 3: 实验结果具有判别力。**

- GReaT: Privacy Risk 99.50% (Adult) → 严重 memorization
- CLLM: 49.45% (Adult) → 几乎无 memorization
- StructSynth: 49.97% (Adult) → 同样几乎无 memorization

如果指标没有判别力，就不会出现 GReaT 99.5% vs. CLLM 49.5% 的巨大差异。

**证据 4: 论文的隐私声明是审慎的。**

论文声称的是 **"best privacy-fidelity trade-off"**（`introduction.tex:53`），而非绝对的隐私保证。隐私评估的目的是展示 StructSynth 在不牺牲 fidelity 的情况下不会加剧 memorization，这一目标已被实验充分支持。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **部分合理**。MIA 确实是隐私评估的重要补充，但 NN Privacy Risk 并非不合理 |
| 审稿人可能忽略的点 | (1) 该指标的社区认可度和理论依据; (2) NN Privacy 和 MIA 的互补关系; (3) 实验结果的判别力 |
| 反驳难度 | **低**。这是一个较容易反驳的点，因为有充分的理论和实践依据 |
| 评分提升可能性 | 可提升审稿人对 Technical Quality 的信心 |

#### Rebuttal 策略

**核心论点：** NN Privacy Risk 是合成数据社区的标准指标，与 MIA 衡量不同维度的隐私风险。论文的隐私声明是审慎的 trade-off claim，而非绝对保证。

**具体回应：**
1. 说明该指标的社区使用情况（SDV, SynthCity, 多篇 NeurIPS/ICML 论文）
2. 解释 NN Privacy Risk 和 MIA 的互补关系，承认 MIA 是有价值的有力补充
3. 如有余力，可在 rebuttal 期间补充 MIA 实验（这是审稿人明确要求的）
4. 强调论文的 claim 是 trade-off 而非绝对隐私保证

---

### Weakness 4: 工程性强但缺乏理论深度

#### 审稿人原文
> The work is strong in engineering and experimentation but lacks novelty, structural reliability analysis, cost evaluation, and theoretical depth, making it more of a system integration than a fundamentally new contribution.

> **注：** 这条 weakness 是对前三条的总结性批评，审稿人列举了四个缺失：(1) novelty, (2) structural reliability analysis, (3) cost evaluation, (4) theoretical depth。

#### 逐点反驳

**（1）Novelty** — 已在 Weakness 1 中详述，此处不重复。

**（2）Structural Reliability Analysis — 论文已有，审稿人可能忽略了。**

| 分析内容 | 论文位置 | 要点 |
|---|---|---|
| SHD 实验 | `experiments.tex:152-159`, Figure 5 | 三个 benchmark 数据集 (Asia/Child/Insurance) 上的结构恢复精度，跨 n=20-200 |
| Adult Graph 可视化 | `appendix.tex:247-253`, Figure 8 | LLM-discovered graph vs. reference graph vs. re-discovered graph 的定性对比 |
| Asia 结构对比 | `appendix.tex:307-329`, Figure 9 | StructSynth vs. GraDe/GOGGLE/NoTears/FCI 的可视化对比 |
| Ablation: 替代发现算法 | `experiments.tex:130-131` | PC Discovery, NoTears Discovery 的退化量化 |

论文已经从 **定量**（SHD）、**定性**（graph visualization）和 **因果**（ablation with alternative discovery）三个角度分析了结构可靠性。审稿人可能没有注意到这些内容。

**（3）Cost Evaluation — 论文已有详细分析。**

| 分析内容 | 论文位置 | 要点 |
|---|---|---|
| Token Usage 分析 | `experiments.tex:200-201`, `appendix.tex:333-340`, Table 4 | 平均 +31% overhead (range: +19%~+42%) |
| Input/Output 分解 | Appendix Table 4 | Input +57%, Output +3%，实际货币成本低于 raw token 增加 |
| 逐数据集分析 | Appendix Table 4 | 六个数据集的详细 token 分解 |

论文已经提供了逐数据集、input/output 分离的 token 级成本分析，并讨论了实际货币成本的启示。审稿人的批评可能源于正文中的简短表述（仅 3 行），而忽略了 Appendix 中的完整分析。

**（4）Theoretical Depth — 确实是论文的薄弱环节。**

论文缺少以下理论分析：
- DAG 质量对下游性能的理论 bound
- Error propagation 的 formal analysis（从结构发现到数据生成）
- 为什么 LLM + statistical cues 的 hybrid 方法在低数据下更优的理论解释

但需要指出的是：
- 这类理论分析在 LLM-based 方法论文中普遍缺失（包括 CLLM、GReaT 等先前工作也没有）
- 论文通过大量的实证分析（ablation, SHD, varying-n, multi-LLM）部分弥补了理论缺失
- Empirical systems paper 在 KDD 中是可接受的发表类型

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **审稿人声称缺少 structural reliability analysis 和 cost evaluation 是不准确的**——论文已包含这些内容。Theoretical depth 的批评有部分道理 |
| 审稿人可能忽略的点 | (1) Section 4.4 和 Appendix 的 SHD 分析; (2) Appendix 的 token usage 分析; (3) 正文空间限制导致成本分析被压缩到 3 行 |
| 反驳难度 | **低到中等**。structural reliability 和 cost evaluation 可以直接指出论文中的已有内容 |
| 评分提升可能性 | Reproducibility 和 Technical Quality 都有提升空间 |

#### Rebuttal 策略

**核心论点：** 审稿人列举的 (2) structural reliability 和 (3) cost evaluation 在论文中已有详细分析（主要在 Appendix），我们将在 rebuttal 中明确引用这些内容。

**具体回应：**
1. **Structural Reliability：** 直接引用 SHD 实验、Adult graph visualization、Asia 结构对比
2. **Cost Evaluation：** 引用 Appendix Table 4 的 token 分析，强调 +31% overhead 的 input-dominant 特性
3. **Theoretical Depth：** 坦诚承认 formal 理论分析的缺失，但指出这在 LLM-based 方法论文中的普遍性，并强调论文的实证严谨性
4. 如有余力，可在 rebuttal 中补充简单的 error propagation 分析（如：当 SHD 增加 k 条边错误时，AUC 的近似变化率）

---

## 三、逐条 Question 回应框架

### Q1: 与先前 structure learning + generation 框架的区别

**审稿人原文：** Please clearly distinguish your method from prior "structure learning + generation" frameworks and highlight any fundamentally new contributions beyond LLM-based implementation.

#### 回应框架

从三个技术维度与先前工作进行对比：

| 维度 | 先前工作 | StructSynth |
|---|---|---|
| **结构发现** | Bayesian Network: 纯统计估计; DECAF/GOGGLE: 端到端学习（data-hungry） | LLM-guided BFS + statistical cues hybrid，利用语义先验弥补样本不足 |
| **图约束维护** | PC/NoTears: 面向 Markov 等价类的搜索，或无环性通过连续优化保证 | Reasoned cycle resolution: LLM 分析环中每条边的 rationale，推理选择最弱边移除 |
| **生成策略** | BN: 条件概率表; DECAF: GAN + causal adjacency; GraDe: attention mask（软约束） | Topological layering + parent-conditioned generation（硬约束：by construction） |

#### 关键支撑证据
- Ablation: PC Discovery (-1.0), NoTears (-1.4), No-Correlation (-1.5), No Topological Order (-1.1)
- SHD 实验：在 Asia 上 SHD≈1（n=100），远优于 NoTears (SHD>5) 和 FCI（多边未定向）

---

### Q2: 低数据场景的专项机制

**审稿人原文：** What specific mechanisms make the approach particularly suitable for low-data regimes, rather than being generally applicable to any data scale?

#### 回应框架

三个机制使方法特别适合低数据场景：

1. **LLM Semantic Prior as Structure Regularizer**
   - 当 n 极小时，统计关联检验不稳定（高方差），LLM 的领域知识提供了独立于样本量的先验信息
   - SHD 实验：n=20 时 StructSynth 仍保持 SHD≈1（Asia），传统方法大幅退化

2. **Statistical Cues as Weak Supervision**
   - 统计信号（Pearson's R, Cramér's V）在小样本下噪声较大，但作为 LLM 的辅助输入（而非唯一决策依据）提供了数据驱动的弱监督
   - Ablation: 移除统计信号后 AUC -1.5，说明即使噪声较大，统计信号仍有价值

3. **Decoupled Design Reduces Sample Complexity**
   - 传统方法（DGMs）需要同时学习依赖结构和数据分布，样本复杂度高
   - StructSynth 将两个任务解耦，结构发现阶段只需发现拓扑关系（不需要精确估计条件概率），生成阶段则利用 LLM 的分布学习能力

#### 关键支撑证据
- Figure 4: n≤50 时 StructSynth 优势最显著，n 增大时与 baseline 差距缩小
- Figure 5: SHD 在 n=20~200 区间稳定优于所有 baseline
- Ablation: 传统发现算法（PC, NoTears）在 n=100 时已显著退化

---

### Q3: DAG 错误对下游的影响

**审稿人原文：** How robust is the LLM-guided structure discovery under small samples, and how do errors in the learned DAG affect downstream generation quality?

#### 回应框架

**结构发现的鲁棒性（定量）：**
- SHD 实验（`experiments.tex:152-159`）：在三个有 ground-truth 的 benchmark 上，StructSynth 在 n=100 时 SHD 远低于所有 baseline
- Asia 数据集：SHD≈1（几乎完美恢复），而 NoTears/GOGGLE/FCI 均显著高于此

**DAG 错误的容错性（ablation 证据）：**

| 结构替代方案 | SHD 差异 | AUC 影响 | 容错性判断 |
|---|---|---|---|
| PC Discovery | SHD 更高 | -1.0 pts | **中等容错**：结构精度下降有限影响 AUC |
| NoTears Discovery | SHD 更高 | -1.4 pts | **中等容错**：同上 |
| No Topological Order | 结构正确但生成顺序错误 | -1.1 pts | **顺序重要但不致命** |
| No Structure | 完全无结构 | -1.6 pts | **结构有价值但不主导** |

**关键洞察：** 即使结构发现不完美（如 PC/NoTears），性能退化也仅 1.0-1.4 pts，说明框架具有 **graceful degradation** 特性——结构是一个有用的 blueprint 而非生死攸关的瓶颈。LLM 的生成能力可以在一定程度上弥补结构误差。

**Re-discovered Graph 证据（`appendix.tex:247-253`）：**
- 从 StructSynth 生成的合成数据中重新发现的图与 reference graph 高度一致
- 这从另一个角度证明了结构保真性

---

### Q4: 隐私指标合理性

**审稿人原文：** Can the authors better justify the chosen privacy metric and compare it with standard evaluations?

#### 回应框架

详见 Weakness 3 分析。额外补充：

**该指标与先前工作的使用一致性：**
- 论文遵循了 CLLM（`cllm2024`）和其他合成数据论文的评估范式
- 使用相同指标确保了与 baseline 的公平比较
- 在 Appendix 中提供了完整的数学定义（`appendix.tex:176-201`），包括 distance function 的定义（L1 + Hamming）和 downsampling 策略

**Rebuttal 行动项：**
- 承认 MIA 是有价值的补充评估
- 可在 rebuttal 期间快速补充一个 MIA 实验（如使用 logistic regression membership inference attack）

---

### Q5: 计算成本 vs 性能

**审稿人原文：** Can the authors provide a clearer analysis of computational cost (e.g., token usage, runtime) versus performance gains, especially for practical deployment?

#### 回应框架

**成本分析（来自 Appendix Table 4，`appendix.tex:255-305`）：**

| 指标 | CLLM | StructSynth | 差异 |
|---|---|---|---|
| 平均 Total Tokens | 219.8K | 287.9K | +68.1K (+31.0%) |
| 平均 Input Tokens | 114.1K | 179.2K | +65.1K (+57.1%) |
| 平均 Output Tokens | 105.8K | 108.7K | +2.9K (+2.7%) |
| Graph Stage Tokens | — | 58.8K | 额外结构发现成本 |

**关键见解：** Overhead 以 input token 为主（+57.1%），而 output token 几乎不变（+2.7%）。在主流 LLM 定价中，output token 通常比 input token 贵 3-5 倍，因此实际货币成本增加远低于 31%。

**性能收益：**

| 指标 | CLLM | StructSynth | 提升 |
|---|---|---|---|
| Average Score | 73.36 | 75.01 | +1.65 |
| Average Rank | 2.67 | **1.00** | 完美排名 |
| Privacy Rank | 3.33 | **1.33** | 隐私更优 |

**成本-性能比：** 以约 31% 的 token 增加换取 1.65 pts 的平均性能提升和从排名 2.67 到 1.00 的跃升，在实践中是合理的。

**可扩展性分析：**
- Graph discovery 阶段的 BFS 复杂度为 O(K) 次查询（K=特征数），而非 O(K²)（pairwise）
- 对于 Adult（15 features），graph discovery 仅需 ~58.8K tokens
- 论文已提供了 Pairwise Discovery ablation（`experiments.tex:133`），证实 BFS 是高效的

---

## 四、总体评估与建议

### Weakness 严重程度排序

| 排序 | Weakness | 严重程度 | 反驳难度 | Rebuttal 优先级 |
|---|---|---|---|---|
| 1 | W4: 缺少 structural reliability / cost evaluation（审稿人忽略了已有内容） | **低**（论文已有证据） | **低** | **最高** — 直接指出即可 |
| 2 | W3: 隐私指标合理性 | 中 | **低** | **高** — 容易反驳，可补充 MIA |
| 3 | W2: 低数据场景适用性 | 中 | **中低** | **高** — 有充分实验证据 |
| 4 | W1: 新颖性不足 | **高** | **中等** | **高** — 需要精心论证 |

### Rebuttal 优先级与策略

1. **首先回应 W4（最易反驳）：** 直接引用论文中已有的 SHD 实验、token usage 分析，指出审稿人可能忽略了 Section 4.4 和 Appendix 中的详细分析。这能快速建立论文的技术深度。

2. **其次回应 W3（次易反驳）：** 论证 NN Privacy Risk 的合理性和社区认可度，承认 MIA 的互补性，如有余力补充 MIA 实验。

3. **重点回应 W2（核心动机相关）：** 用 SHD + varying-n + ablation 的三重证据链论证低数据优势。重新框定"专项机制"的定义——LLM prior + statistical cues 本身就是对抗小样本不稳定性的机制。

4. **精心回应 W1（最难但最重要）：** 这是审稿人给出 Novelty 2: Low 的核心原因。需要：
   - 不否认范式不新，但强调具体技术创新
   - 用 ablation 量化每个创新点的非冗余贡献
   - 与最相近工作（GraDe, DECAF）明确区分硬约束 vs 软约束
   - 提出 reasoned cycle resolution 作为新的图约束维护范式

### 评分提升预期

| Criterion | 当前 | 预期提升 | 条件 |
|---|---|---|---|
| Novelty | 2 | 2→3 | 需要成功论证具体技术创新 |
| Technical Quality | 2 | 2→3 | 需要指出已有分析 + 补充 MIA |
| Reproducibility | 2 | 2→3 | 承诺代码开源 |
| Presentation | 3 | 维持 | — |
| Relevance | 3 | 维持 | — |

---

## 五、Rebuttal 要点总结（Bullet Points）

### 针对新颖性（Novelty）
- StructSynth 的创新不在范式而在技术实现：(1) hybrid discovery (LLM + stats), (2) reasoned cycle resolution, (3) topological hard-constrained generation
- Ablation 证实每个组件有独立贡献（1.0-4.4 AUC pts），非冗余拼接
- 与 GraDe 的本质区别：硬结构约束 (by construction) vs 软 attention 引导

### 针对低数据适用性（Low-Data Suitability）
- LLM semantic prior = 低数据下的结构化正则化器（无需额外样本即可提供领域知识）
- SHD 实验：n=20 时 SHD≈1 (Asia)，传统方法大幅退化
- Varying-n 实验：n≤50 时优势最显著，n 增大时差距缩小 → 低数据是优势区间
- Decoupled design 降低样本复杂度：结构发现只需拓扑关系，不需要精确概率估计

### 针对隐私指标（Privacy Metric）
- NN Privacy Risk 是合成数据社区的标准指标（SDV, SynthCity, van2023membership）
- 与 MIA 互补而非替代：NN 衡量 record-level memorization，MIA 衡量 model-level 信息泄露
- 实验结果具有判别力（GReaT 99.5% vs CLLM 49.5%）
- 论文声称的是 trade-off 而非绝对保证

### 针对结构可靠性和成本（Structural Reliability & Cost）
- **Structural Reliability 已有分析：** SHD (3 benchmarks) + graph visualization (Adult, Asia) + ablation (PC, NoTears)
- **Cost Evaluation 已有分析：** Appendix Table 4, 逐数据集 token 分解，+31% overhead (input-dominant)
- DAG 错误有 graceful degradation：替代发现算法仅导致 1.0-1.4 AUC 退化
- 承认 theoretical depth 是未来工作方向

### 针对可复现性（Reproducibility）
- Appendix 提供了完整的 prompt templates（5 个 prompt box）
- Appendix 提供了完整的算法伪代码（Algorithm 1）
- 承诺在论文接收后开源代码
- Hyperparameter 详细列表已提供（Appendix Table 2）
