# Conclusion + Limitations 改写计划

> 修改文件：`Latex-EMNLP/sections/conclusion.tex`、`Latex-EMNLP/sections/limitations.tex`

---

## 一、ARR 2026 对 Limitations 的要求

根据 ARR/EMNLP 2026 官方要求（来源：aclrollingreview.org/cfp, 2026.emnlp.org/calls/main_conference_papers/）：

- **必须**有独立的 `\section*{Limitations}`，不可放在 Conclusion 内，**缺失将 desk reject**
- 位置：正文之后、References 之前（当前论文已正确放置）
- **不计入**页数限制
- **应包含**：方法论上的注意事项、泛化性未覆盖的方向、实际限制（计算成本等）
- **不可包含**：新方法、新分析、新实验结果（不可借此偷加正文内容）
- 无明确长度要求，但应实质性讨论，不宜过短敷衍

---

## 二、Conclusion 改写（`conclusion.tex`）

### 2.1 当前问题

| 段落 | 内容 | 问题 |
|---|---|---|
| P1（方法回顾） | 重新解释 discover-then-synthesize、DAG 构建、拓扑排序生成 | **过度复述方法**：BFS、statistical cues、topological layering 等细节与 Abstract/Method 高度重复 |
| P2（实验总结） | 列出 rank 1.00、+1.65 AUC、rank 1.50、20 samples、7 LLMs | **数字堆砌**：结论应提炼高层 takeaway 而非复读指标 |

**缺失**：无 broader takeaway（读完论文后读者应带走的核心信息）

### 2.2 目标结构：单段，~5-7 行

EMNLP 风格 Conclusion（Limitations 已独立成 section，Conclusion 不再承担此职责）：

1. **1-2 句总结贡献**：点出核心 insight（解耦）+ 方法名称，不复述细节
2. **1-2 句高层结果**：定性语言（SOTA utility, strong privacy, competitive fidelity），不列数字
3. **1-2 句 broader takeaway / future outlook**：提炼对领域的启示，而非重复 limitation

### 2.3 改写策略

**保留**：
- StructSynth 名称 + discover-then-synthesize 范式（一句话）
- 核心 insight：解耦结构发现与数据生成降低了对样本量的需求
- 高层结论：SOTA downstream utility + privacy + 跨 LLM 泛化

**删除**：
- DAG 构建的具体过程（BFS、statistical cues、cycle resolution）
- 拓扑排序生成的细节（autoregressive、layering、conditioning on parents）
- 所有具体数字（rank 1.00、+1.65 AUC、rank 1.50、20 samples、7 architectures）

**新增**：
- Broader takeaway：decoupling 范式对低数据合成领域的普适意义（不限于本方法）

---

## 三、Limitations 改写（`limitations.tex`）

### 3.1 当前内容诊断

当前 Limitations 为单段 ~4 行，覆盖四个点：

| 点 | 内容 | 评价 |
|---|---|---|
| 1. LLM 依赖 feature name 质量 | opaque/specialized schemas 削弱发现 | ✅ 有效，但可展开 |
| 2. 维度限制 | $K \in [8, 19]$，高维需 hierarchical discovery | ✅ 有效 |
| 3. DAG 不可表达环路 | cyclic/bidirectional dependencies | ✅ 有效 |
| 4. 商业 API 依赖 | cost + reproducibility | ✅ 有效，但已有 token usage appendix 部分缓解 |

**问题**：四个点挤在一句式段落中，读起来像 bullet list 的压缩版，缺乏展开和 nuance。ARR 审稿人可能认为过于敷衍。

### 3.2 改写目标

将三个点扩展为有结构的讨论，每点 1-2 句，总长 ~8-12 行。补充审稿人可能质疑的角度：

### 3.3 改写方案

**L1：LLM 语义先验的适用边界**（~2-3 句）
- 现有：opaque schemas 削弱发现
- 展开：StructSynth 的结构发现质量取决于 LLM 对 feature name 和 domain 的语义理解。当 feature name 为编码（如 V1, V2）或高度专业术语（如基因组位点编号）时，LLM 先验质量下降。虽然统计信号可部分补偿，但在完全匿名化的 schema 下，结构发现可能退化为纯统计方法。

**L2：DAG 假设的局限**（~2 句）
- 现有：cannot express cyclic/bidirectional
- 展开：DAG 形式化排除了双向或循环依赖。对于存在真实反馈环路的数据（如经济指标间的互因关系），当前框架需要将环路近似为单向边，可能损失部分依赖信息。

**L3：LLM API 依赖与可复现性**（~2 句）
- 现有：commercial API cost + reproducibility
- 展开：依赖商业 LLM API 引入成本和可复现性问题。虽然 Appendix 报告了较低的 token 开销，且跨多个 LLM 的实验验证了框架对具体模型选择的鲁棒性，但 API 版本更新仍可能影响结果的精确复现。

---

## 四、执行步骤

1. 起草新 Conclusion（英文），与 Abstract 对比确保措辞差异化
2. 起草新 Limitations（英文），逐点展开
3. 确认 Conclusion ≤ 7 行、Limitations ~10-14 行
4. 替换两个文件内容
