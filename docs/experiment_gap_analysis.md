# StructSynth TKDD 实验补充计划：基于 KDD Review 的差距分析

> **目标**：系统梳理 KDD 四位审稿人对实验的质疑，结合 TKDD 期刊对实验深度和广度的更高要求，生成一份按优先级排序的实验补充计划。

---

## 优先级排序逻辑

综合考虑以下三个因素进行排序：
1. **审稿人共识度**：多位审稿人提出 > 单一审稿人提出
2. **对 Technical Quality 评分的影响**：所有审稿人均给出 TQ=2 (Low)，这是最大的共同短板
3. **TKDD 期刊标准**：期刊比会议要求更全面的实验验证和更深入的分析

---

## 🔴 P0：最高优先级（直接影响 Accept/Reject）

### 实验 1：多下游模型验证
- **触发来源**：Reviewer ep8Q W3 & Q1（独家且明确要求）
- **问题**：当前仅使用 XGBoost 评估下游性能，无法证明合成数据对不同模型族的泛化效用
- **具体方案**：
  - 下游模型列表：**LightGBM, Random Forest, MLP (2-layer), Logistic Regression**
  - 如可获得：增加 **TabPFNv2.5**（审稿人明确提及）
  - 在所有 6 个 real-world 数据集上运行
  - 报告格式与 Table 1 一致（AUC / R²）
- **工作量估计**：2–3 天
- **预期收益**：
  - ep8Q: Technical Quality 2→3（关键提升）
  - 所有审稿人：增强实验可信度

---

### 实验 2：增加数据集（含 post-cutoff 数据集）
- **触发来源**：
  - ep8Q W1（评估规模不足，建议 10-15 个数据集）
  - ep8Q W2（data contamination，仅 2 个 post-cutoff 数据集）
  - 6JGG W2（LLM 先验偏差影响数据可靠性）
- **问题**：6 个 real-world 数据集偏少，且 4 个为 LLM 预训练可能见过的知名数据集
- **具体方案**：
  - **新增 4–6 个数据集**，目标达到 10-12 个 real-world 数据集
  - **至少 2–3 个为 post-cutoff 数据集**（2024 年后发布），例如：
    - 来自 Kaggle 近期竞赛的表格数据集
    - 来自最新医学/金融/社科领域的小规模数据集
  - **多样化维度**：覆盖更多领域、不同特征数量（含 30+ features 的数据集）、不同类型（纯数值、纯分类、混合）
  - 建议候选数据集：
    - UCI: Credit (pre), Heart (pre), Magic (pre)
    - Post-cutoff: 需要调研 2024 年后发布的合适数据集
- **工作量估计**：3–5 天（含数据处理 + 全部 baseline 重跑）
- **预期收益**：
  - 大幅增强泛化性论证
  - 缓解 data contamination 质疑
  - 满足 TKDD 期刊对广度的要求

---

### 实验 3：统计显著性检验
- **触发来源**：
  - ep8Q W1（提到 Friedman test, Wilcoxon signed-rank test 功效不足）
  - TKDD 期刊标准（期刊论文要求形式统计检验）
- **问题**：主要结果表无统计显著性检验
- **具体方案**：
  - 对 Table 1 的主要结果添加 **Friedman test + Nemenyi post-hoc test**
  - 或使用 **Wilcoxon signed-rank test**（pairwise StructSynth vs. each baseline）
  - 报告 p-values，并注明显著性水平（\*, \*\*, \*\*\*）
  - 对多下游模型的结果同样添加统计检验
  - 多次运行取均值 + 标准差（如尚未做的话）
- **工作量估计**：1–2 天（依赖实验 1 和 2 完成后的数据）
- **预期收益**：
  - 直接回应 ep8Q 对统计功效的质疑
  - TKDD 基本要求

---

## 🟡 P1：高优先级（显著提升论文质量）

### 实验 4：Membership Inference Attack (MIA) 隐私评估
- **触发来源**：
  - Reviewer hziw W3 & Q4（明确要求与 MIA 比较）
- **问题**：仅使用 NN Privacy Risk，审稿人认为不够充分
- **具体方案**：
  - 实现标准 MIA 攻击（如 Logistic Regression / Shadow Model Attack）
  - 评估所有方法的 MIA 成功率
  - 报告 AUROC of MIA classifier
  - 与 NN Privacy Risk 结果进行对比分析
- **工作量估计**：2–3 天
- **预期收益**：
  - hziw: 直接满足审稿人要求
  - 增加隐私声明的可信度
  - NN Privacy Risk 与 MIA 的互补分析可作为新的讨论点

---

### 实验 5：参数敏感性分析 (Parameter Sensitivity)
- **触发来源**：
  - `tkdd_improvement_checklist.md` 中优先级（已列出）
  - hziw Q2（低数据场景机制）
  - TKDD 期刊标准
- **问题**：缺少对关键超参数的敏感性分析
- **具体方案**：
  1. **Few-shot 样本数 $k$ 的影响**：$k = 10, 20, 50, 100, 200, 500$
     - 在 2–3 个代表性数据集上测试
     - 绘制 AUC/R² vs. $k$ 曲线
  2. **LLM temperature 的影响**：$T = 0.3, 0.5, 0.7, 0.9, 1.0, 1.2$
     - 评估生成质量的稳定性
  3. **关联分数阈值的影响**：
     - 测试不同阈值对 DAG 结构（边数、SHD）和下游性能的影响
- **工作量估计**：3–4 天
- **预期收益**：
  - TKDD 期刊论文必备分析
  - 增强方法的可理解性和可操作性

---

### 实验 6：Error / Failure Case 分析
- **触发来源**：
  - `tkdd_improvement_checklist.md`
  - f5xi W3（统计保真度未达预期）& W4（结构错误传播）
  - hziw Q3（DAG 错误对下游质量的影响）
- **问题**：缺乏 StructSynth 失败场景的系统分析
- **具体方案**：
  1. **Conditional Dependency Fidelity 分析**：
     - 计算 DAG 中编码的父子对的 pairwise correlation fidelity
     - 与全局 Statistical Fidelity 对比，证实结构化方法 **在依赖关系维度** 上更优
  2. **错误传播量化**：
     - 人为注入 $k$ 条错误边（添加 / 删除 / 反转），观察下游性能退化曲线
     - 绘制 SHD vs. AUC 的关系图，量化 graceful degradation
  3. **失败场景识别**：
     - 找到 StructSynth 表现最差的数据集 / 数据子集
     - 分析失败原因（特征类型？依赖结构复杂度？数据分布特性？）
     - 讨论降级策略（回退到 CLLM / 手动指定结构等）
- **工作量估计**：3–4 天
- **预期收益**：
  - 直接回应 f5xi W3（统计保真度落差的深层解释）
  - 量化结构错误的容错性（当前仅有 ablation 证据）
  - TKDD 期刊对 robustness 的深度要求

---

### 实验 7：计算成本与可扩展性系统分析
- **触发来源**：
  - f5xi W5（重复 LLM 调用的计算开销）
  - hziw Q5（成本 vs 性能分析）
  - ep8Q Q2（50+ columns 下 BFS 扩展性）
- **问题**：当前成本分析在 Appendix 中仅有 token 分解，缺乏 runtime 和可扩展性实验
- **具体方案**：
  1. **Runtime 对比**：
     - 测量 StructSynth vs. 所有 baseline 的端到端运行时间
     - 分解为 structure discovery time + generation time
  2. **可扩展性测试**：
     - 在特征数量 $K = 8, 15, 20, 27, 40+$ 的数据集上测试
     - 绘制 LLM 查询次数 / token 消耗 / 运行时间 vs. $K$ 的曲线
     - 如可能，构造或找到 50+ features 的数据集进行测试
  3. **成本-性能 Pareto 图**：
     - X 轴：token 消耗 / 运行时间 / 货币成本
     - Y 轴：AUC / Score
     - 展示 StructSynth 在 Pareto 前沿的位置
- **工作量估计**：2–3 天
- **预期收益**：
  - 将 Appendix 中的简略分析扩展为正文中的系统化分析
  - 回应三位审稿人对成本 / 扩展性的质疑

---

## 🟢 P2：中优先级（锦上添花，提升深度）

### 实验 8：Conditional Dependency Fidelity 新指标
- **触发来源**：f5xi W3（统计保真度落差）& 自我改进
- **问题**：当前 Statistical Fidelity 衡量的是所有 pairwise correlation，而非 StructSynth 优化的 conditional dependency
- **具体方案**：
  - 定义新指标：**Conditional Dependency Fidelity**——仅计算 DAG 中父-子对的 correlation fidelity
  - 在所有数据集上计算此指标
  - 预期 StructSynth 在此指标上显著优于 baseline
  - 可作为论文的一个新贡献点
- **工作量估计**：1–2 天
- **预期收益**：
  - 化解 f5xi 最尖锐的批评（W3 统计保真度）
  - 为论文增加一个新的评估维度

---

### 实验 9：跨 LLM 的结构发现一致性
- **触发来源**：6JGG W2（不同 LLM 的先验偏差）
- **问题**：Multi-LLM 实验仅报告了下游性能，未分析不同 LLM 发现的结构是否一致
- **具体方案**：
  - 用 3–4 个不同 LLM 在相同数据集上发现 DAG
  - 比较发现的 DAG 的 SHD（互相之间 + 与 reference 的）
  - 分析哪些依赖关系是跨模型稳定的，哪些是模型特异的
- **工作量估计**：2–3 天
- **预期收益**：
  - 深入回应 6JGG 关于 LLM 偏差的质疑
  - 增强方法 robustness 论证

---

### 实验 10：消融实验扩展到更多数据集
- **触发来源**：当前 ablation 仅在 Adult 上进行
- **问题**：单数据集消融可能不够泛化
- **具体方案**：
  - 将 Table 3 的 7 个消融变体扩展到至少 3–4 个数据集
  - 报告每个变体在不同数据集上的 AUC
  - 检验各组件贡献的一致性
- **工作量估计**：2–3 天
- **预期收益**：
  - 增强消融结论的泛化性
  - TKDD 对实验深度的要求

---

## 总结：工作量与时间线估计

| 优先级 | 实验编号 | 实验内容 | 估计工作量 | 依赖关系 |
|---|---|---|---|---|
| 🔴 P0 | 1 | 多下游模型验证 | 2–3 天 | 无 |
| 🔴 P0 | 2 | 增加数据集 | 3–5 天 | 无 |
| 🔴 P0 | 3 | 统计显著性检验 | 1–2 天 | 依赖 1 & 2 完成 |
| 🟡 P1 | 4 | MIA 隐私评估 | 2–3 天 | 无 |
| 🟡 P1 | 5 | 参数敏感性分析 | 3–4 天 | 无 |
| 🟡 P1 | 6 | Error / Failure Case | 3–4 天 | 无 |
| 🟡 P1 | 7 | 计算成本与可扩展性 | 2–3 天 | 无 |
| 🟢 P2 | 8 | Conditional Dep Fidelity | 1–2 天 | 无 |
| 🟢 P2 | 9 | 跨 LLM 结构一致性 | 2–3 天 | 无 |
| 🟢 P2 | 10 | 消融扩展到多数据集 | 2–3 天 | 依赖 2 完成 |

> **P0 合计**：6–10 天 | **P1 合计**：10–14 天 | **P2 合计**：5–8 天 | **全部合计**：21–32 天

> [!IMPORTANT]
> 实验 1（多下游模型）和实验 2（增加数据集）可以并行进行。实验 3（统计检验）需等待前两者完成。P1 的 4 个实验之间无依赖，可并行推进。

---

## 与审稿人反馈的映射关系

| 实验 | hziw | f5xi | 6JGG | ep8Q |
|---|---|---|---|---|
| 1. 多下游模型 | | | | ✅ W3 Q1 |
| 2. 增加数据集 | | | ✅ W2 | ✅ W1 W2 |
| 3. 统计显著性 | | | | ✅ W1 |
| 4. MIA 隐私 | ✅ W3 Q4 | | | |
| 5. 参数敏感性 | ✅ Q2 | | | |
| 6. Error/Failure | ✅ Q3 | ✅ W3 W4 | | |
| 7. 计算成本 | ✅ Q5 | ✅ W5 | | ✅ Q2 |
| 8. Cond. Dep. Fidelity | | ✅ W3 | | |
| 9. 跨 LLM 结构 | | | ✅ W2 | |
| 10. 消融扩展 | | ✅ W4 | ✅ W1 | |

> [!TIP]
> 实验 1 和实验 4 的投资回报率最高——前者是唯一一位审稿人（ep8Q，最友好）的明确要求，后者是 hziw 的直接要求。优先完成这两项可以快速提升两位审稿人的评分。
