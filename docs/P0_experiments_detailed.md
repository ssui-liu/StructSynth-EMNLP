# P0 实验详细规格：最高优先级实验

> **定位**：这三项实验直接决定 TKDD 投稿的 Technical Quality 评分能否从 2 (Low) 提升到 3 (Moderate)。所有 4 位 KDD 审稿人均给出 TQ=2，这是论文最大的共同短板。

---

## 实验 1：多下游模型验证 (Multi-Downstream Evaluator)

### 1.1 实验目的

**核心目标**：验证 StructSynth 生成的合成数据对不同模型族的效用泛化性，排除"仅对 XGBoost 有效"的质疑。

**审稿人原文 (ep8Q W3)**：
> "Downstream utility is evaluated using only XGBoost. This is problematic for two reasons: (1) the quality of synthetic data may vary across model families. Patterns that help tree-based models may not help neural networks; (2) some baselines may perform relatively better under different downstream learners."

**审稿人建议 (ep8Q Q1)**：
> "How does performance change when the downstream model is not XGBoost? Specifically, have you tested with other models, e.g., TabPFNv2.5?"

### 1.2 合理性分析

| 维度 | 分析 |
|---|---|
| **审稿人要求的合理性** | ✅ 高度合理。单一模型评估是公认的评估局限。合成数据可能在 pairwise correlation 维度上对树模型更友好，但对需要平滑决策面的模型（如 MLP）效果可能不同 |
| **社区实践** | 虽然 CLLM/GReaT/TabDDPM 等前作也仅用 XGBoost，但 TKDD 作为期刊对评估深度的要求更高 |
| **必要性** | ✅ **必须完成**。ep8Q 是最友好的审稿人（Novelty=3, 唯一给"Novel"评价），补充此实验可将其 TQ 从 2 提升到 3，使其成为论文的强支持者 |
| **风险评估** | 低风险。StructSynth 的优势来自依赖结构保真（对所有模型族均有益），预期在多数模型上保持优势 |

### 1.3 实验设置

#### 下游模型选择

| 模型 | 类型 | 选择理由 | 超参数策略 |
|---|---|---|---|
| **LightGBM** | 树模型 (Boosting) | 排除 XGBoost 特异性优势；社区常用 | 默认参数 |
| **Random Forest** | 树模型 (Bagging) | 不同于 Boosting 的集成方式 | `n_estimators=100, max_depth=None` |
| **MLP (2-layer)** | 神经网络 | 验证跨模型族泛化（tree → neural） | `hidden_sizes=[128,64], lr=1e-3, epochs=100` |
| **Logistic Regression** | 线性模型 | 最简单的基线，测试合成数据对线性可分性的影响 | `C=1.0, max_iter=1000` |
| **TabPFNv2** | Foundation Model | 审稿人明确提及；前沿方法 | 默认推理设置 |

> [!IMPORTANT]
> TabPFNv2.5 需要检查可用性和兼容性。如不可用，至少完成前 4 个模型。

#### 数据集范围

- **完整覆盖**：所有 6 个 real-world 数据集 (Adult, Anxiety, Compas, Salary, Obesity, Churn)
- 如已新增数据集（实验 2），同步覆盖新增数据集

#### 评估指标

- 分类任务：AUC (与 Table 1 一致)
- 回归任务：R² (与 Table 1 一致)
- 每个模型 × 数据集 × 生成方法 组合重复 **10 次** (seed 42–51)，报告 mean ± std

#### 需评估的方法

与原 Table 1 一致的 12 个方法（11 baselines + StructSynth），确保完整可比性。

### 1.4 结果呈现

- **新建 Table**：格式与 Table 1 一致，但按下游模型分组
- 可选：汇总不同下游模型的 **Average Rank**，展示 StructSynth 跨模型的排名一致性
- 可选：绘制 **Radar Chart** 或 **Heatmap**，直观展示各生成方法在不同下游模型上的表现

### 1.5 预期结果与风险

| 预期 | 概率 | 应对 |
|---|---|---|
| StructSynth 在所有模型上保持 Rank 1 | 中高 | 理想结果，直接展示 |
| 在部分模型上 Rank 下降但仍在 Top-3 | 中 | 可接受，分析原因并在 Discussion 中讨论 |
| 在某模型上表现显著差于 baseline | 低 | 需深入分析原因，可能需要在 Limitations 中讨论 |

---

## 实验 2：增加数据集（含 Post-cutoff 数据集）

### 2.1 实验目的

**核心目标**：扩大评估规模以增强结论的泛化性，同时增加 post-cutoff 数据集以缓解 data contamination 质疑。

**审稿人原文 (ep8Q W1)**：
> "The evaluation is limited to only 6 real-world datasets. With so few datasets, formal statistical tests (Friedman test, Wilcoxon signed-rank test) have very low power. The authors should expand to at least 10-15 diverse datasets."

**审稿人原文 (ep8Q W2)**：
> "Only 2 of the 6 datasets (Anxiety, Salary) were released after the LLM knowledge cutoff. The remaining 4 are well-known benchmarks that GPT-4o-mini has probably seen during pretraining."

**审稿人原文 (6JGG W2)**：
> "The prior knowledge the LLM has will greatly affects the quality of the generated data."

### 2.2 合理性分析

| 维度 | 分析 |
|---|---|
| **数据集数量** | 当前 6 个 real-world 数据集与先前工作一致（CLLM 6 个, GReaT 6 个, TabDDPM 8 个），但 TKDD 期刊对广度的要求更高。目标 **10-12 个**是合理的 |
| **Post-cutoff 必要性** | ✅ GPT-4o-mini 的 knowledge cutoff 约为 2023 年 10 月。Adult/Compas/Obesity/Churn 均为经典数据集，LLM 在预训练中极可能见过。增加 post-cutoff 数据集可直接排除 data contamination 解释 |
| **多样性必要性** | ✅ 当前数据集特征数为 8-19，缺乏高维数据集（30+ features）的测试，也缺乏纯数值或纯分类的数据集 |

### 2.3 实验设置

#### 候选数据集筛选标准

1. **Post-cutoff（强烈优先）**：2024 年后在 Kaggle/UCI/OpenML 上发布
2. **多样化**：覆盖未有的领域（如环境、教育、制造等）
3. **特征数量多样化**：含 1-2 个 30+ features 的数据集
4. **适合低数据场景**：总样本量 ≥500（以便在 n=100 采样后仍有足够的测试集）
5. **任务类型平衡**：保持分类/回归的合理比例

#### 候选数据集建议

| 数据集 | 来源 | 特征数 | 类型 | 领域 | Post-cutoff | 备注 |
|---|---|---|---|---|---|---|
| **Diabetes 130** | UCI | 50+ | 混合 | 医疗 | ❌ | 高维测试 |
| **Bank Marketing** | UCI | 17 | 混合 | 金融 | ❌ | 经典金融 |
| **Credit Card Default** | UCI | 24 | 混合 | 金融 | ❌ | 中维金融 |
| **Kaggle 2024 近期竞赛 A** | Kaggle | TBD | TBD | TBD | ✅ | 需调研 |
| **Kaggle 2024 近期竞赛 B** | Kaggle | TBD | TBD | TBD | ✅ | 需调研 |
| **Kaggle 2024 近期竞赛 C** | Kaggle | TBD | TBD | TBD | ✅ | 需调研 |

> [!WARNING]
> Post-cutoff 数据集需要仔细确认发布日期。GPT-4o-mini 的训练数据截止日期约为 2023-10，因此 **2024 年 1 月之后** 首次发布的数据集才算安全。注意，即使 Kaggle 上标记为 2024 发布，底层数据可能更早存在。需检查数据来源说明。

#### 每个新数据集的处理流程

1. 下载并预处理（处理缺失值、编码分类变量）
2. 与现有数据集保持一致的划分策略（8:2 split, n=100 subsample × 10 seeds）
3. 对所有 12 个方法（11 baselines + StructSynth）运行生成 + 评估
4. 报告 AUC/R², Statistical Fidelity, Privacy Risk

### 2.4 结果呈现

- 扩展 Table 1 和 Table 2（or 作为新表呈现）
- 重新计算 Average Score 和 Average Rank（包含新数据集）
- 分别报告 pre-cutoff 和 post-cutoff 数据集的平均性能差异

### 2.5 预期结果与风险

| 预期 | 概率 | 应对 |
|---|---|---|
| StructSynth 在新数据集上保持优势 | 中高 | 大幅增强泛化论证 |
| 在高维数据集上优势减弱 | 中 | 可在 Discussion 中讨论可扩展性限制 |
| 在 post-cutoff 数据集上优势 ≥ pre-cutoff 平均 | 中 | 直接反驳 data contamination |
| 在某些数据集上表现不佳 | 低-中 | 在 Error/Failure Case 分析中讨论 |

---

## 实验 3：统计显著性检验

### 3.1 实验目的

**核心目标**：为主要实验结果添加形式化统计检验，证明 StructSynth 的优势具有统计显著性。

**审稿人原文 (ep8Q W1)**：
> "With so few datasets, formal statistical tests (Friedman test, Wilcoxon signed-rank test) have very low power."

**TKDD 期刊标准**：期刊论文应包含统计显著性检验来验证实验结论。

### 3.2 合理性分析

| 维度 | 分析 |
|---|---|
| **学术规范** | ✅ 统计检验是 ML 实验论文的基本要求，尤其在期刊中。Demšar (2006, JMLR) 的"Statistical Comparisons of Classifiers over Multiple Datasets"是标准参考 |
| **功效问题** | 审稿人正确指出 6 个数据集下 Friedman test 功效不足。但增加到 10+ 数据集后（实验 2 完成后），统计功效将显著提升 |
| **依赖关系** | ⚠️ 本实验应在实验 1 和实验 2 完成后进行，以最大化数据点数量 |

### 3.3 实验设置

#### 检验方法选择

| 检验方法 | 适用场景 | 在本文中的用途 |
|---|---|---|
| **Friedman test** | 多个方法在多个数据集上的全局比较 | 检验 12 个方法之间是否存在统计显著差异 |
| **Nemenyi post-hoc test** | Friedman 显著后的两两比较 | 确定 StructSynth 与哪些 baselines 显著不同 |
| **Wilcoxon signed-rank test** | 两个方法的 pairwise 比较 | StructSynth vs. 各关键 baseline 的 pairwise 显著性 |
| **Critical Difference (CD) diagram** | 可视化排名差异显著性 | 直观展示方法间的显著性关系（Demšar style） |

#### 检验层面

1. **主结果表 (Downstream Performance)**：
   - 对所有数据集的 AUC/R²进行 Friedman + Nemenyi
   - StructSynth vs. CLLM, GraDe, TabSyn 等关键 baselines 的 Wilcoxon
2. **隐私-保真度权衡**：
   - 对 Privacy Risk 的排名进行 Friedman
3. **多下游模型结果**（实验 1 完成后）：
   - 按下游模型分组进行 Friedman

#### 显著性水平

- 常规：$\alpha = 0.05$（标记为 *）
- 强显著：$\alpha = 0.01$（标记为 **）
- 高度显著：$\alpha = 0.001$（标记为 ***）

#### 多重检验校正

使用 Holm-Bonferroni 方法控制 FWER（Family-Wise Error Rate）。

### 3.4 结果呈现

1. **在 Table 1 中添加**：Friedman p-value 和各 pairwise Wilcoxon p-values
2. **新建 Critical Difference Diagram**：Demšar style CD 图，展示方法间排名的显著性分组
3. **正文中报告**：关键统计检验结果（如"StructSynth significantly outperforms CLLM ($p < 0.01$, Wilcoxon signed-rank test)"）

### 3.5 预期结果与风险

| 预期 | 概率 | 应对 |
|---|---|---|
| 在 10+ 数据集上 Friedman 显著($p < 0.05$) | 高（基于当前 rank 1.00） | 强有力的统计支持 |
| Nemenyi 分出 StructSynth 独立的显著性组 | 中高 | 最理想结果 |
| 部分 pairwise 检验不显著 | 中 | 可接受：强调效应量(effect size)和一致性方向 |
| 数据集不足，功效仍然不够 | 低（如果实验 2 完成） | 报告 effect size (Cliff's delta) 作为补充 |

---

## P0 实验间的依赖关系与执行顺序

```mermaid
graph LR
    E1[实验 1: 多下游模型] --> E3[实验 3: 统计检验]
    E2[实验 2: 增加数据集] --> E3
    E1 -.-> E2
    style E1 fill:#ff6b6b,color:#fff
    style E2 fill:#ff6b6b,color:#fff
    style E3 fill:#ff6b6b,color:#fff
```

**建议执行顺序**：
1. **第 1 周**：实验 1 和实验 2 **并行推进**（无硬依赖）
2. **第 2 周**：实验 2 完成后，在扩展数据集上运行实验 1 的多下游模型
3. **第 2-3 周**：汇总所有结果后执行实验 3 的统计检验

> [!TIP]
> 实验 1 的代码框架可以在等待实验 2 的数据集选择和处理时先行开发和调试。
