# StructSynth Appendix 内容迁移与重构计划

> **目标**：将 KDD 草稿的 Appendix 中适合放入正文的内容迁移到 TKDD 版本的对应章节，同时保留真正属于附录的辅助材料，以符合期刊论文的完整性和深度要求。

---

## 一、Appendix 内容盘点

当前 `sections/appendix.tex` 共 737 行，包含以下 9 个独立内容块：

| # | Appendix 章节 | 行数 | 内容类型 | 当前状态 |
|:---|:---|:---|:---|:---|
| A1 | Extended Related Works | L3–13 | 文献综述扩展（传统结构学习 + LLM 结构学习） | 正文 Related Works 仅 26 行，极度精简 |
| A2 | Full Experimental Setups | L15–84 | 数据集表格 + Baselines 说明 + 超参数表 | 正文仅简要提及，细节全在附录 |
| A3 | Association Score Computation | L86–147 | 三种关联度量的数学定义 | 正文方法节引用但未展开 |
| A4 | Evaluation Metrics | L150–238 | 三个评估指标的完整数学定义 | 正文实验节引用但未展开 |
| A5 | Algorithms | L241–419 | 完整算法伪代码 (Algorithm 1) | 正文方法节引用但未包含 |
| A6 | Qualitative Graph Visualization | L246–252 | Adult 数据集上的图可视化对比 | 独立案例分析 |
| A7 | Structure Learning Examples | L306–328 | Asia 数据集上的结构发现对比图 | 正文 SHD 实验引用 |
| A8 | Token Usage Analysis | L332–339 | Token 消耗详细数据表 + 分析 | 正文效率分析节概括性引用 |
| A9 | Detailed Prompts | L347–732 | 6 个 Prompt 模板（tcolorbox 格式） | 正文方法节引用但未展示 |

---

## 二、迁移策略总览

根据内容性质，将附录内容分为三类处理：

```
┌─────────────────────────────────────────────────────────┐
│                    迁 移 策 略 矩 阵                      │
├──────────────────┬──────────────────────────────────────┤
│  🟢 整合进正文    │  A1, A2, A3, A4, A5, A8             │
│  🟡 部分迁移      │  A6, A7                              │
│  🔵 保留在附录    │  A9                                   │
└──────────────────┴──────────────────────────────────────┘
```

---

## 三、逐项迁移方案

### A1: Extended Related Works → `sections/related_work.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| Conventional Structure Learning (约 12 行) | 合并至 Related Works，新增 `\subsection{Structure Learning}` |
| LLM-based Structure Learning (约 10 行) | 合并至同一新增子节 |

**具体操作**：
- 在 `related_work.tex` 中添加 `\subsection{Structure Learning for Tabular Data}` 子节
- 包含两个 `\subsubsection`：Conventional Methods、LLM-based Methods
- 将附录文字直接迁移，微调措辞使其适配正文语境（去除"in our work"等附录式过渡语）
- 更新引用和交叉引用

**理由**：期刊论文的 Related Works 需要系统性覆盖。当前正文仅 26 行，过于精简。结构学习是本文核心贡献之一，必须在正文中充分讨论。

---

### A2: Full Experimental Setups → `sections/experiments.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| 数据集汇总表 (Table: Dataset Summary) | 迁入 `\subsubsection{Datasets}` 正文 |
| Baselines 详细说明 | 迁入 `\subsubsection{Baselines}` 正文并展开 |
| 超参数表 (Table: Hyperparameters) | 迁入 `\subsubsection{Implementation Details}` 正文 |

**具体操作**：
- 将 `Table: Dataset Summary` 从附录移至实验节 Datasets 部分，替代当前的纯文字描述
- 将 Baselines 详细实现说明（SynthCity 库、CuratedLLM 官方代码等）合并到正文 Baselines 子节
- 将超参数表移至 Implementation Details 中
- 删除附录中的对应内容和正文中的"see Appendix"交叉引用

**理由**：数据集特性、基线实现和超参数是可复现性的核心要素，期刊论文应在正文中完整呈现。

---

### A3: Association Score Computation → `sections/method.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| Pearson's R 公式 | 迁入方法节关联度量段落 |
| Correlation Ratio 公式 | 同上 |
| Cramér's V 公式（含偏差校正） | 同上 |

**具体操作**：
- 在 `method.tex` 的 `\subsubsection{Expansion and Reasoned Link Generation}` 后新增 `\subsubsection{Statistical Association Measures}`
- 将三个公式及说明迁入，保持原有数学符号体系
- 删除正文中的 `(see Appendix~\ref{app:association_scores} for detailed formulas)` 引用
- 附录的 Adult 图可视化（Figure: Structure）也在此节附近，见 A6 处理

**理由**：关联度量是方法论的核心组成部分，期刊无页数限制，应完整展示。

---

### A4: Evaluation Metrics → `sections/experiments.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| Downstream Model Performance 定义 | 展开至 `\subsubsection{Evaluation Metrics}` |
| Privacy Risk Assessment 数学定义 | 同上 |
| Statistical Fidelity 数学定义 | 同上 |

**具体操作**：
- 在 `experiments.tex` 的 `\subsubsection{Evaluation Metrics}` 中，将当前简短的三条 itemize 分别展开为独立的 `\paragraph` 或 `\subsubsection`
- 包含完整的数学定义（公式）、评估流程和解释
- 删除"detailed definitions provided in Appendix section"的引用

**理由**：评估指标的数学定义是实验方法论的重要组成，期刊读者期望在正文中看到完整定义。

---

### A5: Algorithm → `sections/method.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| Algorithm 1: StructSynth 完整伪代码 | 迁入方法节末尾或合适位置 |

**具体操作**：
- 将 `Algorithm 1` (约 65 行伪代码) 从附录迁入 `method.tex`
- 建议放置在方法节末尾（`\subsection{Structure-Guided Synthesis}` 之后），作为完整算法的汇总总结
- 删除方法节开头脚注中的"See Appendix for ... complete algorithmic procedures (Section \ref{app:algorithm})"引用

**理由**：算法伪代码是方法描述的核心内容，期刊论文应在正文中完整展示。

---

### A6: Qualitative Graph Visualization → `sections/experiments.tex`

**策略：🟡 部分迁移**

| 内容 | 操作 |
|:---|:---|
| Adult 数据集图可视化对比 (Figure: Structure) | 迁入实验节 |
| 文字分析 | 迁入实验节 |

**具体操作**：
- 将 Figure (Reference Graph / LLM-Discovered / Re-discovered) 和分析文字迁入实验节
- 建议放置在 `\subsection{Structural Fidelity under Ground-Truth Graphs}` 后，作为定性分析的补充
- 可创建新的 `\subsection{Qualitative Analysis of Discovered Structures}` 

**理由**：图可视化是对定量 SHD 分析的有力补充，期刊正文可容纳这类定性分析。

---

### A7: Structure Learning Examples → `sections/experiments.tex`

**策略：🟡 部分迁移**

| 内容 | 操作 |
|:---|:---|
| Asia 数据集结构发现对比图 (Figure: collage) | 迁入实验节 |
| 基线方法结构错误的详细分析 | 迁入实验节 |

**具体操作**：
- 将图和分析迁入实验节的 `Structural Fidelity` 部分
- 与 A6 合并为一个 `\subsection{Qualitative Analysis}` 或分别作为 case study
- 更新 `experiments.tex` 中对 `Appendix~\ref{app:struct_examples}` 的引用

**理由**：结构发现可视化示例为定量 SHD 结果提供具体证据，适合期刊正文。

---

### A8: Token Usage Analysis → `sections/experiments.tex`

**策略：🟢 整合进正文**

| 内容 | 操作 |
|:---|:---|
| Token 消耗详细表 (Table: token_usage) | 迁入效率分析子节 |
| Token 分析文字 (input-dominant overhead 分析) | 迁入效率分析子节 |

**具体操作**：
- 将表格和分析段落迁入 `\subsection{Efficiency Analysis}` 正文
- 当前正文仅有 2 行概括，迁移后将成为完整的效率分析章节
- 删除"(Appendix~\ref{sec:token_usage})"引用

**理由**：效率分析是审稿人关注的重点，期刊版本应完整展示。

---

### A9: Detailed Prompts → 保留在 `sections/appendix.tex`

**策略：🔵 保留在附录**

| 内容 | 操作 |
|:---|:---|
| Textualization Examples (Box 1) | 保留在附录 |
| 5 个 Prompt 模板 (π_source ~ π_data_gen_iso) | 保留在附录 |

**理由**：
- Prompt 模板属于实现细节，放在正文中会过度冗长且打断叙事流
- 正文方法节已对每个 prompt 的作用进行了充分描述
- 保留在附录作为可复现性的补充材料，是期刊论文的标准做法
- 保持正文对 Appendix prompts 的引用即可

---

## 四、迁移后的文件结构预览

### 正文章节预估篇幅变化

| 文件 | 当前行数 | 迁移后预估 | 变化 |
|:---|:---|:---|:---|
| `related_work.tex` | 26 行 | ~55 行 | +29 行（A1 整合） |
| `method.tex` | 125 行 | ~260 行 | +135 行（A3 + A5） |
| `experiments.tex` | 204 行 | ~420 行 | +216 行（A2 + A4 + A6 + A7 + A8） |
| `appendix.tex` | 737 行 | ~260 行 | -477 行（仅保留 A9 prompts） |

### 迁移后附录仅保留

```
appendix.tex
├── Detailed Prompts for StructSynth
│   ├── Box 1: Data Textualization Examples
│   ├── π_source: Source Nodes Initialization
│   ├── π_generation: Link Generation
│   ├── π_resolve: Cycle Resolution
│   ├── π_data_gen: Structure-Guided Synthesis
│   └── π_data_gen_iso: Independent Feature Synthesis
```

---

## 五、交叉引用更新清单

迁移内容后，需更新以下交叉引用：

| 位置 | 当前引用 | 更新为 |
|:---|:---|:---|
| `method.tex` L3 (脚注) | "See Appendix for full prompt templates... and complete algorithmic procedures" | 仅保留 prompt 引用，删除 algorithm 引用 |
| `method.tex` L22 | "see Appendix~\ref{app:association_scores} for detailed formulas" | 改为正文内 Section 引用 |
| `experiments.tex` L4 | "Full dataset details are provided in the Appendix section \ref{app:datasets}" | 删除，改为引用正文中的表格 |
| `experiments.tex` L8 | "implementation details in Appendix section A.2.2" | 删除，改为正文内引用 |
| `experiments.tex` L11 | "detailed definitions provided in Appendix section \ref{app:metrics}" | 删除，改为正文内引用 |
| `experiments.tex` L23 | "Full hyperparameter configurations are provided in Appendix section \ref{app:hyperparameter}" | 删除，改为引用正文表格 |
| `experiments.tex` L159 | "Appendix~\ref{app:struct_examples}" | 改为正文内 Section/Figure 引用 |
| `experiments.tex` L201 | "Appendix~\ref{sec:token_usage}" | 删除，改为正文内引用 |

---

## 六、迁移优先级与执行顺序

建议按以下顺序执行，避免交叉引用冲突：

| 优先级 | 步骤 | 内容 | 依赖 |
|:---|:---|:---|:---|
| 1️⃣ | A1 → Related Works | 文献综述扩展 | 无 |
| 2️⃣ | A3 → Method | 关联度量公式 | 无 |
| 3️⃣ | A5 → Method | 算法伪代码 | A3 完成后 |
| 4️⃣ | A2 → Experiments | 实验设置详情 | 无 |
| 5️⃣ | A4 → Experiments | 评估指标定义 | 无 |
| 6️⃣ | A8 → Experiments | Token 分析 | 无 |
| 7️⃣ | A6+A7 → Experiments | 定性可视化 | A4 完成后 |
| 8️⃣ | 清理 Appendix | 删除已迁移内容，保留 A9 | 以上全部完成 |
| 9️⃣ | 交叉引用更新 | 修复所有引用 | 以上全部完成 |
