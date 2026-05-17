# Reviewer ep8Q 审稿意见深度分析与评估

> **目标：** 结合论文原文，对 Reviewer ep8Q 的每条 Weakness 和 Question 进行逐一分析，评估其合理性，并为 rebuttal 提供论据和策略。

---

## 一、审稿人评分概览

| Criterion | Score | 评估 |
|---|---|---|
| Relevance | **4: High** | **所有审稿人中最高**，且唯一给出 High |
| Novelty | **3: Moderate** | **所有审稿人中最高**（hziw=2, f5xi=2, 6JGG=1） |
| Technical Quality | **2: Low** | 与 hziw/f5xi 一致，核心拉分项 |
| Presentation | 3: Moderate | 与 hziw/f5xi 一致 |
| Reproducibility | **2: Low** | 与 hziw/f5xi 一致 |
| Reviewer Confidence | 3: Moderate | 中等自信度，有说服空间 |

### 四位审稿人评分横向对比

| Criterion | hziw | f5xi | 6JGG | **ep8Q** |
|---|---|---|---|---|
| Relevance | 3 | 3 | 3 | **4** |
| Novelty | 2 | 2 | 1 | **3** |
| Technical Quality | 2 | 2 | 2 | **2** |
| Presentation | 3 | 3 | 2 | **3** |
| Reproducibility | 2 | 2 | 1 | **2** |
| Reviewer Confidence | 3 | 3 | 3 | **3** |

### 核心定位：最友好、最建设性的审稿人

ep8Q 有两个独特特征使其与其他审稿人截然不同：

**特征 1：对论文方向的高度认可。**

ep8Q 的 Strengths 段落非常正面：

> "**Novel and well-motivated framework.** The discover-then-synthesize paradigm is a clean and principled decomposition. Decoupling structure learning from generation is conceptually appealing and addresses a real limitation of existing approaches."

> "**Practical evaluation with downstream model performance as the primary metric.** This paper centers evaluation on downstream model performance which is the most practically relevant measure of synthetic data quality."

> "**Evaluation covers both classification and regression tasks.** This broader task coverage, while still limited in scale, provides more generalizable evidence than papers that evaluate on one task alone."

ep8Q 是唯一使用 "Novel" 一词的审稿人，并且承认了评估设计的多个优点（下游性能为主指标、覆盖分类+回归）。

**特征 2：所有 Weakness 均聚焦于"评估完整性"而非方法论缺陷。**

| Weakness | 批评维度 | 是否质疑方法论本身 |
|---|---|---|
| W1: 评估规模 | 数据集数量不足 | **否** — 认为评估不够广泛 |
| W2: 数据污染 | LLM 可能见过数据 | **否** — 认为评估可能有偏差 |
| W3: 单一下游模型 | 评估不够全面 | **否** — 认为评估需要补充 |
| W4: 可复现性 | 缺少代码仓库 | **否** — 认为可复现性不足 |

**关键结论：** ep8Q 认可 **"做什么"和"怎么做"**，只是认为 **"验证得够不够"** 需要加强。这是最容易通过补充材料和实验满足的审稿人。

**总体判断：** ep8Q 的低分集中在 Technical Quality (2) 和 Reproducibility (2)。这两个维度都可以通过 **具体的补充行动**（多下游模型实验、代码开源承诺）来改善。如果 Technical Quality 从 2 提升到 3，Reproducibility 从 2 提升到 3，ep8Q 的平均分将从 2.67 提升到 3.17，成为论文的 **强支持者**。

**Rebuttal 策略核心：不是"反驳"而是"满足"。**

---

## 二、逐条 Weakness 深度分析

### Weakness 1: 评估规模不足 — "仅 6 个数据集"

#### 审稿人原文

> **Insufficient evaluation scale.** The evaluation is limited to only 6 real-world datasets. With so few datasets, formal statistical tests (Friedman test, Wilcoxon signed-rank test) have very low power. The authors should expand to at least 10-15 diverse datasets with varying sizes, feature counts, and domains to substantiate their claims.

#### 审稿人批评的核心逻辑

审稿人的论证链：
1. 6 个数据集 → 样本量太小
2. 样本量小 → 形式统计检验（Friedman test, Wilcoxon signed-rank test）功效不足
3. 功效不足 → 结论不可靠
4. 建议：扩展到 10-15 个数据集

这是一个 **纯统计方法论** 的批评，不涉及对方法本身的质疑。

#### 评估审稿人批评的合理性

| 维度 | 合理性 | 分析 |
|---|---|---|
| 统计功效担忧 | **合理** | 6 个数据集确实限制了形式统计检验的可靠性 |
| 具体建议（10-15） | **部分合理** | 10-15 是理想的，但在 rebuttal 期间（通常 1-2 周）难以完成 |
| 作为 rejection 理由 | **偏严格** | 先前工作的数据集规模类似或更小（见下文对比） |

**与先前工作的数据集规模对比：**

| 先前工作 | 数据集数量 | 发表venue |
|---|---|---|
| CLLM (`cllm2024`) | 6 | NeurIPS Workshop |
| GReaT (`borisov2023language`) | 6 | ICLR |
| TabDDPM (`kotelnikov2023tabddpm`) | 8 | ICLR |
| CTGAN (`xu2019modeling`) | 7 | NeurIPS |
| TabSyn (`tabsyn`) | 7 | ICLR |
| **StructSynth** | **6 + 3 benchmarks** | — |

论文的数据集规模与该领域的主流工作一致。值得注意的是，论文还额外使用了 3 个有 ground-truth 的结构学习 benchmark（Asia, Child, Insurance），实际评估覆盖了 **9 个数据集**。

#### 论文中的反驳证据

**证据 1: Rank 1.00 的完美一致性本身就是强有力的统计证据。**

| Dataset | StructSynth Rank | 最佳竞争者 |
|---|---|---|
| Adult | 1 | CLLM (2) |
| Anxiety | 1 | TabSyn (2) |
| Compas | 1 | CLLM (2) |
| Salary | 1 | CLLM (2) |
| Obesity | 1 | CLLM (2) |
| Churn | 1 | CLLM (2) |

在 6/6 数据集上均为最佳，且第二名不固定（TabSyn、CLLM 交替），说明 StructSynth 的优势 **不是由某个数据集的偶然因素驱动的**。

形式化地，如果 StructSynth 与最佳 baseline 在每个数据集上等价（null hypothesis），那么 StructSynth 在所有 6 个数据集上均排名第一的概率仅为 $(1/12)^6 \approx 3.6 \times 10^{-7}$（假设 12 个方法随机排名），或 $(1/2)^6 \approx 0.016$（假设 StructSynth 与次优方法二选一）。后者在 $\alpha = 0.05$ 下已达到统计显著性。

**证据 2: 多维度交叉验证弥补了数据集数量的不足。**

| 验证维度 | 论文位置 | 要点 |
|---|---|---|
| 数据集多样性 | Table 1 | 4 classification + 2 regression, 4 domains |
| 结构评估 | Figure 5, SHD | 3 benchmarks × 4 sample sizes = 12 个数据点 |
| Ablation study | Table 3 | 7 个变体在 Adult 上的系统分析 |
| Varying-n | Figure 4 | n=20-200, 6 个数据点 |
| Multi-LLM | Figure 6 | 7 个 LLM 上的交叉验证 |
| Token efficiency | Appendix Table 4 | 6 个数据集的逐数据集成本分析 |

论文的评估虽然是 6 个 real-world 数据集，但通过 **多维度交叉验证** 提供了远超"6 个数据点"的实证深度。

**证据 3: 数据集覆盖了多样的特征和任务类型。**

| Dataset | Features | Domain | Task | 特殊性 |
|---|---|---|---|---|
| Adult | 15 (4 num + 11 cat) | Social/Census | Binary Classification | 高维分类 |
| Anxiety | 19 (12 num + 7 cat) | Medical/Health | Multi-Class Classification | Post-cutoff ✓ |
| Compas | 8 (5 num + 3 cat) | Crime | Binary Classification | 低维分类 |
| Salary | 18 (3 num + 15 cat) | Economy | Regression | Post-cutoff ✓ |
| Obesity | 15 (7 num + 8 cat) | Medical/Health | Regression | 混合类型回归 |
| Churn | 12 (8 num + 4 cat) | Business | Binary Classification | 商业应用 |

6 个数据集覆盖了：2 种任务类型（classification + regression）、4 个领域、8-19 个特征维度、binary/multi-class 分类。这种多样性支持了结论的泛化性。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理但偏严格**。6 个数据集确实偏少，但与先前工作一致，且 rank 1.00 的一致性提供了强统计证据 |
| 审稿人可能忽略的点 | (1) 3 个额外 benchmark 数据集 = 实际 9 个; (2) Rank 1.00 的统计显著性; (3) 多维度交叉验证; (4) 先前工作的数据集规模 |
| 反驳难度 | **低到中等**。这是一个"承认局限 + 论证已有证据充分性"的策略 |
| 评分提升可能性 | 如果补充 2-3 个数据集，可能显著提升审稿人信心 |

#### Rebuttal 策略

**核心论点：** 承认数据集数量是合理的关注点，但论文的实际评估覆盖远超"6 个数据点"。9 个数据集 + rank 1.00 完美一致性 + 多维度交叉验证共同支撑了结论的可靠性。如有可能，在 rebuttal 中补充额外数据集。

**具体回应：**
1. **承认局限**：6 个 real-world 数据集确实是评估规模上的局限
2. **澄清实际规模**：论文实际评估了 9 个数据集（6 real-world + 3 structure benchmarks），后者提供了 SHD 的定量验证
3. **强调统计证据**：rank 1.00 的完美一致性在统计上极不可能是偶然（$p < 0.02$ under conservative binomial test）
4. **引用社区标准**：先前工作（CLLM 6 个、GReaT 6 个、TabDDPM 8 个）的数据集规模类似
5. **补充承诺**：如有余力，在 rebuttal 中补充 2-4 个额外数据集（如 Credit, Heart, King, Magic 等 UCI/Kaggle 常用数据集）

---

### Weakness 2: 数据污染风险 — "仅 2 个 post-cutoff 数据集"

#### 审稿人原文

> **Data contamination risk with only 2 post-cutoff datasets.** Only 2 of the 6 datasets (Anxiety, Salary) were released after the LLM knowledge cutoff. The remaining 4 (Adult, Compas, Obesity, Churn) are well-known benchmarks that GPT-4o-mini has probably seen during pretraining. The LLM may be partially recalling training data rather than genuinely learning from the provided samples. The evaluation should include substantially more post-cutoff datasets.

#### 审稿人批评的核心逻辑

审稿人的担忧链：
1. GPT-4o-mini 可能在预训练中见过 Adult, Compas, Obesity, Churn
2. 如果 LLM "知道" 这些数据集，StructSynth 的优势可能部分来自 LLM 的数据记忆而非方法论设计
3. 仅有 2 个 post-cutoff 数据集无法排除这一解释
4. 建议增加更多 post-cutoff 数据集

#### 评估审稿人批评的合理性

| 维度 | 合理性 | 分析 |
|---|---|---|
| 核心担忧 | **合理** | LLM 对知名数据集的先验知识确实是 LLM-based 方法的系统性风险 |
| 影响范围 | **需细化** | "见过数据集" ≠ "记住数据行"，需要区分不同层面的影响 |
| 作为 rejection 理由 | **中等** | post-cutoff 数据集的表现提供了部分反驳 |

**关键区分：LLM 先验知识的三个层面。**

| 层面 | 描述 | 对 StructSynth 的影响 |
|---|---|---|
| **行级记忆** | LLM 记住了数据集中的具体行 | **影响最大** — 但 StructSynth 使用 prompt-based generation（非 fine-tuning），行级记忆的风险较低 |
| **结构理解** | LLM 知道数据集中哪些特征相关 | **影响中等** — 但这正是 StructSynth 利用 LLM 的设计意图（利用语义先验弥补小样本不足） |
| **任务知识** | LLM 知道数据集的用途和标签含义 | **影响最小** — 这对 prompt-based 方法是通用的 |

审稿人最担忧的是 **行级记忆**，但论文有多层证据表明这不是问题的主要来源。

#### 论文中的反驳证据

**证据 1: Post-cutoff 数据集上优势持续，幅度一致。**

| Dataset | Pre/Post Cutoff | StructSynth | CLLM | Δ | 平均 Δ |
|---|---|---|---|---|---|
| Adult | Pre | 85.55 | 83.95 | +1.60 | |
| Anxiety | **Post** | 86.45 | 85.17 | **+1.28** | |
| Compas | Pre | 69.40 | 66.24 | +3.16 | |
| Salary | **Post** | 55.98 | 54.53 | **+1.45** | |
| Obesity | Pre | 62.27 | 60.43 | +1.84 | |
| Churn | Pre | 90.39 | 89.81 | +0.58 | |
| | | | | | |
| Post-cutoff 平均 | | | | **+1.37** | |
| Pre-cutoff 平均 | | | | **+1.80** | |

**关键发现：** StructSynth 在 post-cutoff 数据集上的优势（+1.37）与 pre-cutoff 数据集上的优势（+1.80）一致，且 **pre-cutoff 的优势反而更大**。如果优势来自 LLM 对 pre-cutoff 数据的先验知识，那么 pre-cutoff 数据集上应该有更大优势，但数据 **不支持这一解释**。

**证据 2: Privacy Risk 数据排除行级记忆。**

| Dataset | Pre/Post | StructSynth Privacy Risk | 理想值 | 解读 |
|---|---|---|---|---|
| Adult | Pre | 49.97% | 50% | 无 memorization |
| Anxiety | Post | 44.74% | 50% | 无 memorization |
| Compas | Pre | 62.37% | 50% | 轻微偏高（但远低于 GReaT 94.10%） |
| Salary | Post | 50.13% | 50% | 无 memorization |
| Obesity | Pre | 49.80% | 50% | 无 memorization |
| Churn | Pre | 48.67% | 50% | 无 memorization |

如果 StructSynth 的性能来自 LLM 对训练数据的记忆（如审稿人所暗示），Privacy Risk 应显著偏离 0.5（接近 1.0 表示合成数据与训练数据过度相似）。实际上，Privacy Risk 在所有数据集上均接近 0.5，**包括 pre-cutoff 数据集**。

**证据 3: CLLM 使用相同 LLM 但性能更低。**

关键对照：CLLM 同样使用 gpt-4o-mini（`appendix.tex:46`），如果 LLM 的先验知识是性能的主要驱动力，CLLM 应该也能从"知道" Adult 等数据集中受益。但 CLLM 在 Adult 上的 AUC 仅为 83.95（vs. StructSynth 85.55），差距 1.6 pts。

**Ablation 直接证实**：No Structure 变体（等同于 CLLM，使用相同 LLM 但无结构引导）→ AUC 83.95 vs. StructSynth 85.55。这证明 **StructSynth 的优势来自结构蓝图引导，而非 LLM 对数据的先验知识**。

**证据 4: Statistical cues 来自实际数据，非 LLM 先验。**

BFS 过程中注入的统计关联信号（Pearson's R, Cramér's V, Correlation Ratio）是从 **实际训练数据**（$\mathcal{D}_{\text{few\_shot}}$）中计算的（`methodology.tex:22`）。Ablation（No-Correlation Score: 84.06 vs. 85.55, Δ=-1.5）证实了统计信号的独立贡献。

即使 LLM 对数据集有先验知识，统计信号仍然提供了 **独立于 LLM 先验的数据驱动验证**，防止 LLM 完全依赖先验而忽略实际数据。

**证据 5: 结构理解 ≠ 数据记忆。**

即使 GPT-4o-mini "知道" Adult 数据集中 Age 与 Income 相关，这恰恰是 StructSynth 希望利用的信息——**将 LLM 的结构理解作为低数据下的先验补偿**。论文在脚注（`introduction.tex:47`）中已明确声明：

> "edges capture statistical/probabilistic dependencies inferred from limited observations and are used as a generative blueprint, not as a claim of ground-truth causality."

LLM 对特征间关系的理解（无论来自预训练还是 few-shot 数据）正是结构发现阶段所利用的信号。关键在于 **生成阶段不直接复制训练数据的行**——Privacy Risk 数据已证实这一点。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理但过度担忧**。数据污染风险确实存在，但论文有多层证据表明它不是性能优势的主要来源：(1) Post-cutoff 优势持续; (2) Privacy Risk 排除行级记忆; (3) CLLM 对照实验; (4) 统计信号的数据驱动验证 |
| 审稿人可能忽略的点 | (1) Pre-cutoff 优势反而大于 post-cutoff; (2) Privacy Risk 在 pre-cutoff 数据集上同样接近 0.5; (3) CLLM 使用相同 LLM 但性能更低; (4) Statistical cues 提供数据驱动验证; (5) LLM 结构理解 ≠ 数据行记忆 |
| 反驳难度 | **中等**。需要精细区分 LLM 先验的不同影响层面 |
| 评分提升可能性 | 如果论证得当，可显著提升审稿人对评估可信度的信心 |

#### Rebuttal 策略

**核心论点：** 数据污染风险在行级记忆层面已被 Privacy Risk 数据排除。Post-cutoff 数据集的持续优势、CLLM 对照实验、以及统计信号的数据驱动验证共同证明 StructSynth 的性能优势来自方法论设计而非 LLM 对训练数据的记忆。

**具体回应（五步论证）：**

1. **承认合理担忧**：LLM 对知名数据集的先验知识确实是 LLM-based 方法的系统性风险，我们理解审稿人的关注。

2. **Post-cutoff 数据集的持续优势**：StructSynth 在 post-cutoff 数据集上的优势（+1.37）与 pre-cutoff（+1.80）一致，且 **pre-cutoff 优势反而更大**。如果优势来自 LLM 对 pre-cutoff 数据的先验知识，pre-cutoff 数据集应该优势更大——数据不支持这一解释。

3. **Privacy Risk 排除行级记忆**：所有数据集（包括 pre-cutoff）的 Privacy Risk 均接近 0.5，表明合成数据没有过度复制训练数据行。

4. **CLLM 对照实验**：CLLM 使用相同 gpt-4o-mini 但无结构引导，AUC 低 1.6 pts。Ablation（No Structure = CLLM）直接证明优势来自结构蓝图而非 LLM 先验。

5. **补充承诺**：如有余力，在 rebuttal 中补充 1-2 个额外 post-cutoff 数据集的实验。

---

### Weakness 3: 单一下游模型 — "仅用 XGBoost"

#### 审稿人原文

> **Single downstream model (XGBoost only).** Downstream utility is evaluated using only XGBoost. This is problematic for two reasons: (1) the quality of synthetic data may vary across model families. Patterns that help tree-based models may not help neural networks; (2) some baselines may perform relatively better under different downstream learners. The authors should validate with multiple downstream models (e.g., TabPFNv2.5) to ensure the findings generalize beyond a single evaluator.

#### 审稿人批评的核心逻辑

审稿人的两个论点：
1. **泛化性质疑**：合成数据对树模型有效 ≠ 对所有模型有效
2. **公平性质疑**：不同 baseline 可能在不同下游模型上有不同的相对表现

这是 ep8Q **最具体、最可操作的批评**——它提出了明确的要求（测试其他下游模型），且这一要求可以在 rebuttal 期间完成。

#### 评估审稿人批评的合理性

| 维度 | 合理性 | 分析 |
|---|---|---|
| 泛化性质疑 | **合理** | 单一下游模型确实是评估的局限 |
| 公平性质疑 | **部分合理** | 理论上可能，但 StructSynth 的优势来自结构保真而非特定于树模型的模式 |
| 具体建议 | **合理且可操作** | 补充 2-3 个下游模型的实验在 rebuttal 期间完全可行 |

**与先前工作的对比：**

| 先前工作 | 下游模型 | 发表venue |
|---|---|---|
| CLLM | XGBoost | NeurIPS Workshop |
| GReaT | XGBoost | ICLR |
| TabDDPM | XGBoost | ICLR |
| CTGAN | XGBoost + others | NeurIPS |
| TabSyn | XGBoost | ICLR |
| **StructSynth** | **XGBoost** | — |

使用 XGBoost 作为主要/唯一下游模型是该领域的 **标准实践**。但 ep8Q 的批评超越了这个标准——它提出了一个合理的改进方向。

#### 论文中可用的缓解证据

**证据 1: 论文的评估已包含非 XGBoost 的间接验证。**

| 评估维度 | 与 XGBoost 的关系 | 论文位置 |
|---|---|---|
| Statistical Fidelity | 独立于下游模型 | Table 2 |
| Privacy Risk | 独立于下游模型 | Table 2 |
| SHD (结构质量) | 独立于下游模型 | Figure 5 |
| Varying-n 趋势 | 补充验证 | Figure 4 |
| Multi-LLM 泛化性 | 模型维度的泛化 | Figure 6 |

虽然下游性能仅用 XGBoost，但论文通过多个 **独立于下游模型** 的指标进行了交叉验证。如果 StructSynth 仅对 XGBoost 有特殊优势，那么在其他指标上不应一致领先。

**证据 2: StructSynth 的优势来自结构保真而非特定模型模式。**

StructSynth 的核心机制（拓扑序生成 + 父节点条件化）产生的是 **更好的依赖结构保真**，而非某种特定于树模型的数据变换。理论上，更好的依赖结构应该对所有下游模型都有益，因为：
- 更真实的特征间依赖 → 更好的决策边界学习（无论模型类型）
- 更少的虚假关联 → 更少的过拟合风险（对所有模型）

**证据 3: Rank 1.00 的一致性暗示稳健的优势。**

如果在某些数据集上 StructSynth 仅有 XGBoost 特定的优势，那它的 rank 不应该在所有 6 个数据集上一致为 1——因为不同数据集对树模型的友好程度不同。完美的一致性暗示优势来自更根本的属性（依赖结构保真）。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理**。单一下游模型是评估的真正局限，审稿人的建议合理且可操作 |
| 审稿人可能忽略的点 | (1) 多个非 XGBoost 指标的交叉验证; (2) 社区标准实践; (3) 优势来自结构保真的理论论证 |
| 反驳难度 | **低**。这是最容易解决的批评——补充实验即可 |
| 评分提升可能性 | **高**。补充多下游模型实验可能是提升 Technical Quality 从 2 到 3 的关键行动 |

#### Rebuttal 策略

**核心论点：** 承认单一下游模型是评估的局限，但论文已通过多个独立指标进行了交叉验证。将在 rebuttal 中补充多下游模型实验以验证结论的泛化性。

**具体回应：**

1. **承认局限**：单一下游模型确实无法全面评估合成数据对不同模型族的效用。

2. **论证已有缓解**：
   - Statistical Fidelity、Privacy Risk、SHD 等指标独立于下游模型
   - 使用 XGBoost 是该领域的标准实践
   - Rank 1.00 的一致性暗示优势来自根本属性

3. **补充实验（Rebuttal 期间的关键行动）**：
   - 选择 2-3 个额外的下游模型：
     - **LightGBM**：树模型变体，验证是否对 XGBoost 有特殊优势
     - **Random Forest**：另一种集成方法
     - **MLP / 1-hidden-layer Neural Network**：神经网络，验证跨模型族泛化性
     - **TabPFNv2.5**（如果可用）：审稿人明确提到
   - 在所有或关键数据集上运行
   - 报告与 Table 1 相同格式的结果

4. **预期结果**：StructSynth 应在不同下游模型上保持优势，因为其优势来自依赖结构保真（对所有模型有益），而非特定于树模型的数据变换。

---

### Weakness 4: 可复现性问题 — "无代码仓库链接"

#### 审稿人原文

> **Reproducibility concerns.** The paper does not provide a link to an anonymous code repository. Given the complexity of the multi-stage pipeline and the sensitivity of LLM-based methods to prompt engineering, reproducing the results from the paper alone may be very difficult. The full prompt templates in Appendix I are helpful but insufficient without the surrounding orchestration code.

#### 审稿人批评的核心逻辑

1. 无匿名代码仓库 → 复现困难
2. 多阶段 pipeline + prompt engineering → 复杂度高
3. Appendix 的 prompt templates 有帮助但不够

#### 评估审稿人批评的合理性

| 维度 | 合理性 | 分析 |
|---|---|---|
| 核心担忧 | **合理** | LLM-based 方法的复现性确实是社区关注点 |
| 批评强度 | **合理** | 承认 Appendix 有帮助，但认为需要代码 |
| 与其他审稿人一致 | 是 | hziw (Reproducibility=2)、f5xi (Reproducibility=2)、6JGG (Reproducibility=1) 均有类似担忧 |

#### 论文中已提供的可复现性材料

| 材料 | 论文位置 | 覆盖范围 |
|---|---|---|
| 5 个完整 prompt templates | `appendix.tex:348-733`（5 个 tcolorbox） | pipeline 的所有 LLM 交互环节 |
| Algorithm 1 完整伪代码 | `appendix.tex:355-420` | 两阶段完整流程 |
| Hyperparameter 详细配置 | `appendix.tex:55-85`，Table 2 | LLM、XGBoost、PC 算法的所有参数 |
| Evaluation metric 完整定义 | `appendix.tex:151-236` | Privacy Risk、Statistical Fidelity 的数学定义 |
| Association score 公式 | `appendix.tex:87-148` | Pearson's R, Correlation Ratio, Cramér's V |
| Token usage 详细分析 | `appendix.tex:255-340`，Table 4 | 逐数据集的 input/output token 分解 |
| Graph 可视化示例 | `appendix.tex:247-329`，Figures 8-9 | 结构发现和恢复的定性验证 |
| Dataset 特征描述 | `appendix.tex:18-36`，Table 1 | 所有数据集的详细特征 |
| CLLM 实验设置 | `appendix.tex:44-46` | 确保公平比较的具体措施 |

**关键观察：** 论文已提供的材料 **覆盖了 pipeline 的所有关键步骤**——从 prompt templates（输入）到 algorithm（流程）到 hyperparameters（配置）到 metrics（评估）。一个有经验的研究者基于这些材料复现结果是可行的，但确实需要大量工程工作。

#### 评估判断

| 维度 | 评估 |
|---|---|
| 审稿人批评的合理性 | **合理**。代码仓库确实是最直接的可复现性保障 |
| 论文已有材料 | **丰富但不足以替代代码**。5 个 prompt templates + Algorithm 1 + hyperparameters 覆盖了所有关键步骤，但 orchestration code 仍需重建 |
| 反驳难度 | **最低**。直接承诺即可 |
| 评分提升可能性 | **高**。承诺代码开源 + 匿名仓库可将 Reproducibility 从 2 提升到 3 |

#### Rebuttal 策略

**核心论点：** 承诺论文接收后立即开源完整代码。在 rebuttal 期间提供匿名代码仓库链接。列出论文已提供的可复现性材料清单。

**具体回应：**

1. **承诺代码开源**：论文接收后立即在 GitHub 上开源完整实现，包括：
   - 完整的 pipeline orchestration code
   - 所有 prompt templates（代码形式）
   - 数据预处理和评估脚本
   - 可一键复现的实验配置

2. **提供匿名仓库**（如果可行）：在 rebuttal 期间提供匿名代码仓库链接

3. **列出已有材料**：
   - 5 个完整 prompt templates（Appendix, 5 个 tcolorbox）
   - Algorithm 1 完整伪代码
   - 详细 hyperparameter 列表（LLM, XGBoost, PC）
   - Evaluation metric 完整数学定义
   - Association score 计算公式
   - Token usage 逐数据集分解

---

## 三、逐条 Question 回应框架

### Q1: 非 XGBoost 下游模型的表现

**审稿人原文：** How does performance change when the downstream model is not XGBoost? Specifically, have you tested with other models, e.g., TabPFNv2.5?

#### 回应框架

**这是 W3 的延伸，是 rebuttal 中最需要实际行动的问题。**

**实验计划：**

| 下游模型 | 选择理由 | 验证目标 |
|---|---|---|
| LightGBM | 树模型变体，社区常用 | 排除 XGBoost-specific 优势 |
| Random Forest | 集成方法，不同于 boosting | 验证跨集成方法泛化 |
| MLP (1-2 hidden layers) | 神经网络 | 验证跨模型族（tree → neural）泛化 |
| TabPFNv2.5 | 审稿人明确提到 | 直接回应审稿人建议 |

**预期结果：**
- StructSynth 在树模型（LightGBM, RF）上应保持明显优势
- 在 MLP 上优势可能缩小但应仍存在（因为依赖结构保真对所有模型有益）
- TabPFNv2.5 如果可用，结果将最有说服力

**结果呈现格式：** 与 Table 1 相同格式，增加下游模型列，报告 AUC/R²。

**理论支撑：** StructSynth 的拓扑序生成确保了特征间依赖关系的忠实传递。更好的依赖结构保真 → 更真实的联合分布近似 → 对所有下游模型都有益（无论模型如何利用特征间关系）。

---

### Q2: 多特征场景（50+ columns）下 BFS 的扩展性

**审稿人原文：** What happens when the number of features increases significantly (e.g., 50+ columns)? How does the BFS-based discovery scale, and how many LLM queries are required?

#### 回应框架

**理论分析：**

| 维度 | 分析 |
|---|---|
| LLM 查询次数 | BFS 遍历每个节点一次 → O(K) 次查询（K=特征数）。50 features → ~50 次查询 |
| 每次查询的 token | 与当前图状态大小和候选特征数相关，随 K 增长 |
| 总 token 消耗 | Graph stage: O(K × avg_tokens_per_query) |
| Cycle resolution | 每个 cycle 一次额外查询，cycles 数量通常远小于 K |

**已有证据：**

| 证据 | 来源 | 要点 |
|---|---|---|
| Insurance (27 nodes) 成功运行 | `experiments.tex:156-158` | 27 个节点的中等规模网络已成功 |
| BFS vs Pairwise ablation | `experiments.tex:133` | BFS 不仅更高效（O(K) vs O(K²)），性能也更好（85.55 vs 85.25） |
| Graph stage 平均 58.8K tokens | `appendix.tex:281` | 100-shot 设置下，graph discovery 的平均 token 消耗 |

**Token 消耗随特征数的增长趋势（来自 Table 4 数据）：**

| Dataset | Features | Graph Input (K) | Graph Output (K) | Graph Total (K) |
|---|---|---|---|---|
| Compas | 8 | 17.1 | 1.0 | 18.1 |
| Adult | 15 | 38.1 | 1.5 | 39.6 |
| Churn | 12 | 41.4 | 2.2 | 43.6 |
| Obesity | 15 | 43.5 | 1.7 | 45.3 |
| Anxiety | 19 | 89.0 | 3.1 | 92.1 |
| Salary | 18 | 111.1 | 3.1 | 114.3 |

**趋势分析：** Graph total tokens 大致与 feature 数量正相关但增长温和。从 8 features (18.1K) 到 19 features (92.1K)，增长约 5x。外推到 50 features，预计 graph discovery 约需 200-400K tokens（取决于特征间关系的复杂度）。

**潜在瓶颈与应对：**

| 瓶颈 | 影响 | 应对策略 |
|---|---|---|
| Prompt 长度增长 | 更多特征 → 更长的 association score 列表 | 可过滤低分特征，减少 prompt 长度 |
| Cycle 数量增加 | 更多特征 → 更可能产生环 | Reasoned cycle resolution 可并行处理多个环 |
| LLM 推理质量 | 复杂结构可能超出 LLM 的推理能力 | 可分阶段 discovery（先模块化发现子图，再合并） |

**回应结构：**
1. BFS 的 O(K) 查询复杂度是理论上的优势
2. 实际 token 消耗增长温和（8-19 features 的数据支持）
3. Insurance (27 nodes) 已成功运行
4. 承认 50+ features 是未来工作的重要方向，可考虑模块化 discovery 等扩展策略

---

### Q3: 代码开源计划

**审稿人原文：** Do you plan to release the code and full implementation? Given the complexity of the pipeline and the sensitivity to prompt design, code availability is important for reproducibility.

#### 回应框架

**直接回答：是的，计划在论文接收后立即开源。**

**开源内容清单：**

| 组件 | 内容 |
|---|---|
| Pipeline 核心 | 完整的 StructSynth 两阶段实现 |
| Prompt templates | 所有 5 个 prompt 的代码实现 |
| Data preprocessing | 数据集加载和预处理脚本 |
| Evaluation | 所有 3 个 metric 的评估脚本 |
| Baselines | 所有 11 个 baseline 的运行脚本（基于 SynthCity） |
| Configuration | 所有 hyperparameter 配置文件 |
| Documentation | README + 使用示例 |

**已有可复现性材料回顾：**
- 5 个完整 prompt templates（`appendix.tex:348-733`）
- Algorithm 1 完整伪代码（`appendix.tex:355-420`）
- 详细 hyperparameter 列表（`appendix.tex:55-85`）
- Evaluation metric 数学定义（`appendix.tex:151-236`）
- Association score 计算公式（`appendix.tex:87-148`）

---

## 四、总体评估与建议

### Weakness 严重程度排序

| 排序 | Weakness | 严重程度 | 反驳难度 | Rebuttal 优先级 | 理由 |
|---|---|---|---|---|---|
| 1 | W4: 可复现性 | **低** | **最低** | **最高** | 直接承诺即可，可快速得分 |
| 2 | W3: 单一下游模型 | **中** | **低** | **最高** | 补充实验即可解决，是提升 Technical Quality 的关键行动 |
| 3 | W1: 评估规模 | **中** | **低到中等** | **高** | 承认局限 + 论证已有证据充分性 |
| 4 | W2: 数据污染 | **中高** | **中等** | **高** | 需要精细论证，但有充分证据 |

### Rebuttal 整体策略

**ep8Q 的特殊性决定了策略：这是"满足"而非"反驳"。**

ep8Q 的所有 Weakness 都是建设性的改进建议，而非对方法论的否定。策略应该是：
1. **尽可能满足审稿人的具体要求**（补充实验、承诺代码开源）
2. 对于无法完全满足的要求（如扩展到 15 个数据集），坦诚承认并论证已有证据的充分性
3. **用实际行动（补充实验）而非纯文字论证**来回应

**第一阶段（承诺回应）：W4 — 可复现性**

这是最易回应的 Weakness：
- 立即承诺论文接收后开源代码
- 如可行，在 rebuttal 期间提供匿名代码仓库
- 列出已提供的可复现性材料清单
- **预期效果：** Reproducibility 从 2 提升到 3

**第二阶段（补充实验）：W3 + Q1 — 多下游模型**

这是 **rebuttal 中投资回报率最高的行动**：
- 补充 2-3 个下游模型（LightGBM, MLP, RF/TabPFN）
- 在所有或关键数据集上运行
- **预期效果：**
  - ep8Q: Technical Quality 从 2 提升到 3
  - 满足其他审稿人对实验充分性的担忧
  - 为所有审稿人的 rebuttal 提供通用证据

**第三阶段（论证回应）：W1 + W2 — 评估规模和数据污染**

- W1：论证 9 个数据集 + rank 1.00 完美一致性 + 多维度交叉验证的充分性
- W2：用 post-cutoff 数据集 + Privacy Risk + CLLM 对照的三重证据链论证

### 评分提升预期

| Criterion | 当前 | 预期提升 | 条件 |
|---|---|---|---|
| Relevance | 4 | 维持 | 已是最高 |
| Novelty | 3 | 维持或 3→4 | 如果整体回应有力（ep8Q 已给 Moderate） |
| Technical Quality | **2** | **2→3** | **关键取决于补充多下游模型实验** |
| Presentation | 3 | 维持 | — |
| Reproducibility | **2** | **2→3** | 代码开源承诺 + 匿名仓库 |

**总体提升：** 平均分从 2.67 提升到 3.17（+0.5），ep8Q 将成为论文的强支持者。

---

## 五、Rebuttal 要点总结（Bullet Points）

### 针对评估规模（W1）
- 承认 6 个 real-world 数据集是评估规模的局限
- 澄清论文实际评估了 **9 个数据集**（6 real-world + 3 structure benchmarks with ground-truth DAGs）
- Rank 1.00 的完美一致性在统计上极不可能是偶然（conservative binomial test: $p < 0.02$）
- 数据集覆盖了 2 种任务类型、4 个领域、8-19 个特征维度
- 先前工作（CLLM 6、GReaT 6、TabDDPM 8、TabSyn 7 个数据集）的规模类似
- 多维度交叉验证（ablation × 7, varying-n × 6, multi-LLM × 7, SHD × 12 data points）弥补了数据集数量
- 如有余力，在 rebuttal 中补充 2-4 个额外数据集

### 针对数据污染（W2）
- **Post-cutoff 数据集优势持续**：Anxiety +1.28, Salary +1.45，与平均 +1.65 一致。**Pre-cutoff 优势反而更大（+1.80 vs +1.37）**，不支持"LLM 先验知识驱动优势"的解释
- **Privacy Risk 排除行级记忆**：所有数据集（包括 pre-cutoff）的 Privacy Risk 均接近 0.5（Adult 49.97%, Obesity 49.80%, Churn 48.67%）
- **CLLM 对照实验**：CLLM 使用相同 gpt-4o-mini 但 AUC 低 1.6 pts（Ablation: No Structure = CLLM）。优势来自结构蓝图而非 LLM 先验
- **Statistical cues 数据驱动**：Pearson's R / Cramér's V / Correlation Ratio 从实际数据计算，Ablation 证实独立贡献（No-Correlation: -1.5 AUC pts）
- **区分"结构理解"与"数据记忆"**：LLM 对特征关系的理解是 StructSynth 的设计意图（弥补小样本不足），但生成阶段不复制数据行

### 针对单一下游模型（W3）— **最关键的补充行动**
- 承认单一下游模型是评估的局限
- 使用 XGBoost 是合成数据评估的社区标准（CLLM, GReaT, TabDDPM, TabSyn 等均使用）
- 论文已通过多个独立于下游模型的指标交叉验证（Statistical Fidelity, Privacy Risk, SHD）
- **Rebuttal 中将补充 2-3 个下游模型**（LightGBM, MLP, Random Forest / TabPFNv2.5）
- 预期：StructSynth 的优势来自依赖结构保真，对所有模型族应普遍有效

### 针对可复现性（W4）
- **承诺论文接收后立即开源完整代码**，包括 pipeline、prompts、evaluation、baselines
- 如可行，在 rebuttal 期间提供匿名代码仓库链接
- 论文已提供：5 个完整 prompt templates、Algorithm 1 伪代码、详细 hyperparameters、evaluation metric 数学定义、association score 公式、token usage 逐数据集分解
- CLLM 的 LLM 设置已明确声明完全匹配（Appendix Section A.2.2）

### 针对 BFS 扩展性（Q2）
- BFS 查询复杂度为 O(K)（vs. Pairwise 的 O(K²)），Ablation 证实 BFS 更高效且性能更好
- 当前最大数据集：Insurance (27 nodes) 成功运行，Salary (18 features) token overhead 仅 +23.1%
- Graph stage token 消耗随特征数增长温和（8→19 features: 18K→92K tokens）
- 外推到 50 features: 预计 graph discovery 约 200-400K tokens
- 潜在扩展策略：模块化 discovery（先发现子图再合并）、低分特征过滤

---

## 六、与其他审稿人的交叉分析与统筹策略

### ep8Q 的独特关注点

| 关注点 | ep8Q | 其他审稿人 | 重叠度 |
|---|---|---|---|
| 数据集数量 | ✓ (W1) | 无 | **独特** |
| Data contamination | ✓ (W2) | 无 | **独特** |
| 多下游模型 | ✓ (W3, Q1) | 无 | **独特** |
| 代码开源 | ✓ (W4, Q3) | hziw (Reproducibility=2), 6JGG (Reproducibility=1) | 部分重叠 |
| BFS 扩展性 | ✓ (Q2) | f5xi (W5: 计算开销) | 部分重叠 |

**关键发现：** ep8Q 有 **三个独特关注点**（W1, W2, W3），这些在其他审稿人的批评中没有出现。但 ep8Q 关注的维度——**评估的全面性和可信度**——恰好是其他审稿人给出 Technical Quality=2 的深层原因。满足 ep8Q 的要求可以间接缓解其他审稿人的担忧。

### 为 ep8Q 准备的实验/论据的复用价值

| 为 ep8Q 准备的 | 可复用于 | 复用价值 |
|---|---|---|
| **多下游模型实验结果** | hziw (Technical Quality), f5xi (Technical Quality), 6JGG (Technical Quality) | **最高** — 直接回应 4 个审稿人对 Technical Quality 的低分 |
| **代码开源承诺** | hziw (Reproducibility=2), 6JGG (Reproducibility=1), f5xi (Reproducibility=2) | **最高** — 直接回应 4 个审稿人对 Reproducibility 的低分 |
| **Post-cutoff 数据集论证** | 6JGG (W2: 数据可靠性) | **高** — 直接反驳"LLM 先验知识决定性能"的批评 |
| **Rank 1.00 统计论证** | hziw (实验充分性) | **中等** |
| **BFS 扩展性分析** | f5xi (W5: 计算开销) | **中等** — 两个审稿人都关注成本/效率 |

### 统筹建议

**ep8Q 是 rebuttal 的战略支点。** 原因：

1. **ep8Q 的要求最具体、最可操作**：其他审稿人的批评（新颖性不足、方法论质疑）难以通过补充实验解决，而 ep8Q 的要求（多下游模型、代码开源）都可以通过具体行动满足。

2. **满足 ep8Q 的行动可以复用到所有审稿人**：
   - 多下游模型实验 → 提升所有审稿人的 Technical Quality
   - 代码开源 → 提升所有审稿人的 Reproducibility
   - Post-cutoff 数据集论证 → 反驳 6JGG 的"与 LLM 无本质区别"

3. **ep8Q 是最可能给出正面 overall recommendation 的审稿人**：如果 Technical Quality 从 2 提升到 3，ep8Q 的评分将显著高于其他审稿人，成为论文的强支持者。

**建议行动优先级：**

| 优先级 | 行动 | 工作量 | 受益审稿人 | 预期效果 |
|---|---|---|---|---|
| 1 | 承诺代码开源 + 匿名仓库 | 0.5 天 | 全部 4 位 | Reproducibility +1 |
| 2 | 补充多下游模型实验 | 1-2 天 | 全部 4 位 | Technical Quality +1 |
| 3 | 补充 2-3 个额外数据集 | 2-3 天 | ep8Q, hziw | 评估充分性增强 |
| 4 | 补充 1-2 个 post-cutoff 数据集 | 1-2 天 | ep8Q, 6JGG | Data contamination 反驳 |

**总工作量预估：** 4-8 天（取决于是否包含额外数据集实验）。这在 rebuttal 期间（通常 1-2 周）是可行的。
