# EMNLP 论文内容重组计划：从期刊组织回归会议组织

> **背景**：当前 TKDD 版本从 KDD 会议版迁移而来后，将大量 appendix 内容提升至正文、扩展了分析段落、新增了 Discussion/Limitations 等章节，形成了典型的期刊论文组织方式。EMNLP 作为会议论文 (Long Paper, **8 页正文** + 无限 references + appendix)，需要将内容重新压缩回会议格式。  
> **目标**：在保持核心贡献与关键实验结果完整的前提下，将正文控制在 8 页以内，将非核心内容移至 appendix。  
> **参考基准**：以 KDD 会议版 (`Latex_Paper_KDD/sections/`) 为组织蓝本，结合 TKDD 版新增的有价值内容。  
> **范围**：聚焦内容在各区域 (正文/appendix) 之间的重新分配，不修改具体研究内容。

---

## 一、现状分析：TKDD 版内容规模 vs EMNLP 页面预算

### 1.1 页面估算 (ACL 双栏格式，~110 行/页)

| 章节 | 估算页数 | 说明 |
|:---|:---|:---|
| Abstract | 0.15 | ~120 词 |
| Introduction | 1.1 | 含 Figure 1 |
| Related Work | 0.85 | 含 pipeline `figure*` |
| Methodology | 3.2 | 含 Table 1, Algorithm 1, 6 个公式, 关联度量子节 |
| Experiments | 5.5 | 含 6 个 table/figure + 大量分析文字 |
| Discussion | 0.6 | 新增章节 |
| Limitations | 0.25 | 新增章节 |
| Conclusion | 0.2 | 扩展版 |
| **合计** | **~11.85** | **超出 EMNLP 限制约 3.85 页** |

### 1.2 TKDD 版本的三类"期刊化"膨胀

| 膨胀类型 | 说明 | 占比 |
|:---|:---|:---|
| **A. Appendix→正文提升** | 8 个 appendix 节被移入正文 (数据集表、超参表、评估指标公式、关联度量公式、算法伪代码、定性图可视化、Token 分析、Structure Learning 相关工作) | ~60% |
| **B. 分析段落扩展** | 隐私/保真度"启发式差异"分析、消融"定性非定量"论证、"为何低数据区是优势区"段落、Design Rationale 段落 | ~25% |
| **C. 全新章节** | Discussion (4 小节 ~800 词)、Limitations (4 段)、扩展 Conclusion (具体指标 + 未来工作) | ~15% |

---

## 二、核心重组策略

### 2.1 总体原则

```
正文 (≤8 页): 核心贡献 + 关键实验结果 + 精炼分析
Appendix (无限): 技术细节 + 扩展分析 + 定性可视化 + 完整证明/论证
```

### 2.2 内容去向决策矩阵

| 内容 | KDD 版位置 | TKDD 版位置 | EMNLP 目标位置 | 理由 |
|:---|:---|:---|:---|:---|
| Abstract | 无 | 正文 | **正文** | 必须 |
| Introduction (简洁版) | 正文 | 正文 (扩展) | **正文** (用 KDD 版) | 更紧凑 |
| Pipeline figure | Related Work | Related Work | **正文 Related Work** | 核心框架图 |
| Related Work §2.1-2.2 | 正文 | 正文 | **正文** | 必须 |
| Related Work §2.3 Structure Learning | Appendix | 正文 | **Appendix A** | 非核心前置知识 |
| "Why a DAG?" 完整论证 | 无 | 正文 (28 行) | **Appendix B** 或 footnote | KDD 用 footnote 足够 |
| Design Rationale 段落 | 无 | 正文 (12 行) | **正文** (压缩至 2-3 句) | 有价值但过长 |
| 关联度量公式 (Pearson's R 等) | Appendix | 正文 | **Appendix C** | 技术细节 |
| Algorithm 1 伪代码 | Appendix | 正文 | **Appendix D** | 会议论文常规做法 |
| 数据集摘要表 | Appendix | 正文 | **Appendix E** | 细节 |
| 超参数表 | Appendix | 正文 | **Appendix E** | 细节 |
| 评估指标公式 | Appendix | 正文 | **正文** (简要描述) | 简化引用 |
| Table 1 (Performance) | Method | Method | **正文 Method 或 Experiments** | 核心结果 |
| Table 2 (Privacy+Fidelity) | Experiments | Experiments | **正文 Experiments** | 核心结果 |
| Table 3 (Ablation) | Experiments | Experiments | **正文 Experiments** | 核心结果 |
| Figure SHD | Experiments | Experiments | **正文 Experiments** | 核心结果 |
| Adult 定性图可视化 | Appendix | 正文 | **Appendix F** | 支撑性证据 |
| Asia 定性图可视化 | Appendix | 正文 | **Appendix F** | 支撑性证据 |
| Token 使用量表+分析 | Appendix | 正文 | **Appendix G** | 细节 |
| "为何低数据是优势区" | 无 | 正文 | **Appendix H** 或删除 | 非核心分析 |
| Discussion 全部 4 小节 | 无 | 正文 | **Appendix H** (压缩) | 有价值但非必要 |
| Limitations | 无 | 正文 | **Appendix I** | EMNLP 要求存在，可在正文末尾简述 |
| Conclusion (简洁版) | 正文 | 正文 (扩展) | **正文** (段落 1-2) | 保留核心数据，去掉未来工作 |

---

## 三、EMNLP 版章节规划

### 3.1 正文结构 (目标 ≤8 页)

```
\begin{abstract}                          (~0.15 页)
\section{Introduction}                    (~0.9 页)  [用 KDD 版本框架]
\section{Related Work}                    (~0.5 页)  [仅 §2.1 + §2.2]
  └ pipeline figure (figure*)
\section{Methodology}                     (~1.8 页)  [核心内容保留, 细节下沉]
  ├ Problem Definition
  ├ Dependency Structure Discovery (含压缩版 Design Rationale)
  ├ Structure-Guided Synthesis
  └ Table 1 (Performance Comparison)
\section{Experiments}                     (~3.8 页)
  ├ Experimental Setups (压缩版)
  ├ Main Results (Table 1 已在 Method 中则不重复; Table 2)
  ├ Ablation Study (Table 3)
  ├ Structural Fidelity (SHD Figure)
  ├ Influence of Training Sample Size
  └ Influence of Different LLMs
\section{Conclusion}                      (~0.15 页)
\section*{Limitations}                    (~0.2 页)  [EMNLP 要求, 可简化]
\bibliography{references}
                                          ─────────
                                          ~7.5 页
```

### 3.2 Appendix 结构

```
\appendix

\section{Structure Learning Background}           [原 TKDD Related Work §2.3]
\section{Structural Formulation: Why a DAG?}      [原 TKDD Method §2.2]
\section{Statistical Association Measures}         [原 TKDD Method §2.5]
\section{Complete Algorithm}                       [原 TKDD Method §2.6, Algorithm 1]
\section{Detailed Experimental Setup}              [数据集表, 超参数表, 完整评估指标]
\section{Qualitative Graph Analysis}               [Adult 三图 + Asia 六图]
\section{Efficiency Analysis}                      [Token 使用量表 + 分析]
\section{Extended Discussion}                      [原 TKDD Discussion, 压缩]
\section{Detailed Prompts for StructSynth}         [6 个 tcolorbox prompt 模板]
```

---

## 四、逐节迁移操作指南

### 4.1 Introduction

**操作**: 以 KDD 会议版为基础，选择性融入 TKDD 改进

| 操作 | 详情 |
|:---|:---|
| **使用 KDD 版主体** | KDD 版更紧凑 (55 行 vs TKDD 56 行) |
| **保留 TKDD 改进** | P1 的 "three compounding failure modes" 枚举有价值，可保留 (如果页数允许) |
| **DAG 说明回退为 footnote** | TKDD 用 `Section~\ref{sec:why_dag}` 交叉引用正文章节; EMNLP 版回退为 KDD 的 `\footnote{...not a claim of ground-truth causality...}` |
| **贡献点保持不变** | 三个贡献点两个版本一致 |

**Subagent 校验点**:
- [ ] 确认 footnote 中的 DAG 说明文字完整
- [ ] 确认 `\ref{fig:teaser}` 引用正确
- [ ] 对比 KDD/TKDD 两个 introduction 文字差异清单

### 4.2 Related Work

**操作**: 截断至 KDD 版范围

| 操作 | 详情 |
|:---|:---|
| **保留** | §2.1 Conventional Tabular Data Synthesis + §2.2 LLM-Based Synthesis |
| **移至 Appendix A** | §2.3 Structure Learning for Tabular Data (含 Conventional + LLM-based 两个 subsubsection) |
| **Pipeline figure** | 保持 `figure*` 在 Related Work 顶部 |

**迁移细节**:
- 将 TKDD `related_work.tex` 中 `\subsection{Structure Learning for Tabular Data}` 及其后的全部内容剪切
- 粘贴至 appendix 文件，作为 Appendix A
- 更新所有 `\ref{...}` 交叉引用

**Subagent 校验点**:
- [ ] 确认正文 Related Work 以 LLM-Based 小节结尾
- [ ] 确认 appendix 中 Structure Learning 内容完整
- [ ] 检查是否有正文其他位置引用了 §2.3 中的内容

### 4.3 Methodology

**操作**: 保留核心，大幅下沉细节

| 保留在正文 | 移至 Appendix |
|:---|:---|
| Problem Definition (原样) | §2.2 "Structural Formulation: Why a DAG?" → Appendix B |
| Dependency Structure Discovery (保留核心描述) | "Design Rationale for Low-Data Regimes" 段落 → 压缩至 2-3 句嵌入正文 |
| Structure-Guided Synthesis (原样) | §2.5 Statistical Association Measures → Appendix C |
| Table 1 (Performance) (保持在正文) | §2.6 Complete Algorithm → Appendix D |
| 所有数学公式 (Discovery + Synthesis) | |

**具体操作步骤**:

1. **"Why a DAG?" → Appendix B**
   - 剪切 TKDD `method.tex` 中从 `\subsection{Structural Formulation: Why a DAG?}` 到该节末尾的全部内容
   - 粘贴至 appendix 文件
   - 在 Problem Definition 后添加一句引用: "We adopt the DAG formulation for its functional role in defining a generative ordering; see Appendix B for a detailed justification."

2. **"Design Rationale" → 压缩**
   - TKDD 原文有 ~200 词阐述三个机制 (LLM prior, statistical cues, decoupled architecture)
   - 压缩为: "This design explicitly adapts to data-scarce settings by (a) leveraging the LLM's semantic prior as a structural regularizer, (b) using statistical association scores as weak supervision, and (c) decoupling structure discovery from generation to reduce per-stage sample complexity."
   - 完整版保留在 appendix 或删除

3. **Association Measures → Appendix C**
   - 剪切三个 subsubsection (Pearson's R, Correlation Ratio, Cramér's V) 及其公式
   - 在正文 Discovery 小节中改为: "We compute association scores using dependency measures specific to data types: Pearson's R (continuous-continuous), Correlation Ratio (categorical-continuous), and Cramér's V (categorical-categorical)~\cite{agresti2011categorical} (detailed in Appendix C)."

4. **Algorithm 1 → Appendix D**
   - 剪切 `\begin{algorithm*}...\end{algorithm*}`
   - 在正文 Structure-Guided Synthesis 后添加引用: "The complete algorithmic procedure is provided in Algorithm 1 (Appendix D)."

**Subagent 校验点**:
- [ ] 确认正文 Methodology 保留: Problem Definition + Discovery + Synthesis + Table 1
- [ ] 确认所有公式 (Discovery/Synthesis 核心公式) 仍在正文
- [ ] 确认 appendix B/C/D 内容完整无遗漏
- [ ] 确认 `\ref{sec:why_dag}`, `\ref{sec:association_scores}`, `\ref{sec:algorithm}` 引用更新

### 4.4 Experiments

**操作**: 最大幅度的重组 — 核心结果保留，细节与分析下沉

#### 4.4.1 Experimental Setups (压缩)

| 子节 | KDD 处理 | TKDD 处理 | EMNLP 操作 |
|:---|:---|:---|:---|
| Datasets | "详见 Appendix" | 完整表格 + 描述 | **KDD 方式**: 简要列举 + "详见 Appendix E" |
| Baselines | 简要列举 + "详见 Appendix" | 完整段落 | **KDD 方式**: 简要列举 + "详见 Appendix E" |
| Evaluation Metrics | 简要 itemize + "详见 Appendix" | 完整公式 + 定义 | **中间路线**: 简要描述 (保留 Statistical Fidelity 和 Privacy Risk 的 1-2 句定义)，公式移至 Appendix E |
| Implementation | 简要 + "详见 Appendix" | 完整段落 + 超参表 | **KDD 方式**: 简要 + "详见 Appendix E" |

**具体操作**:
- 用 KDD 版的 Setups 文字替代 TKDD 版的扩展文字
- 添加 "Appendix E provides full details" 类引用
- Evaluation Metrics: 保留 3 个 metric 的名称和一句话定义，公式下沉

#### 4.4.2 Main Results (保留但压缩分析)

| 结果 | 操作 |
|:---|:---|
| Table 1 (Performance) | **已在 Methodology 中**，不重复 (或移至 Experiments) |
| Table 2 (Privacy+Fidelity) | **保留在正文** |
| Performance 分析 | 使用 KDD 版简洁分析 (1 段) |
| Privacy/Fidelity 分析 | **使用 KDD 版** (2 段); 不用 TKDD 扩展版 "instructive discrepancy" 分析 |

#### 4.4.3 Ablation Study (保留但压缩分析)

| 操作 | 详情 |
|:---|:---|
| Table 3 | 保留在正文 |
| 分析文字 | **使用 KDD 版** (1 段, 3 个 insight)，不用 TKDD 的 3 段扩展版 |

#### 4.4.4 Structural Fidelity (SHD) — 保留

| 操作 | 详情 |
|:---|:---|
| Figure (SHD) | 保留在正文 |
| 分析 | **使用 KDD 版** (较紧凑)，Asia/Child/Insurance 各 1-2 句 |

#### 4.4.5 Qualitative Analysis → Appendix F

| 操作 | 详情 |
|:---|:---|
| Adult 三图可视化 | 移至 Appendix F |
| Asia 六图可视化 | 移至 Appendix F |
| 对应分析文字 | 移至 Appendix F |
| 正文替代 | 在 SHD 小节末尾添加一句: "Appendix F provides qualitative visualizations on the Adult and Asia datasets." |

#### 4.4.6 Influence of Training Sample Size — 保留

| 操作 | 详情 |
|:---|:---|
| Figure (vary_n) | 保留在正文 |
| 分析 | **使用 KDD 版** |
| "Why Low-Data Is Our Advantage Zone" 段落 | **删除** 或移至 Appendix H |

#### 4.4.7 Influence of Different LLMs — 保留

| 操作 | 详情 |
|:---|:---|
| Figure (llm_compare) | 保留在正文 |
| 分析 | **使用 KDD 版** |

#### 4.4.8 Efficiency Analysis → Appendix G

| 操作 | 详情 |
|:---|:---|
| Token 使用量表 | 移至 Appendix G |
| 3 段分析 | 移至 Appendix G |
| 正文替代 | 在 LLM comparison 后添加一句: "Appendix G provides a detailed token usage analysis showing that StructSynth incurs a modest +31\% overhead over CLLM." |

**Subagent 校验点**:
- [ ] 确认正文包含: Setups (压缩) + Main Results + Ablation + SHD + Sample Size + LLMs
- [ ] 确认正文图表: Table 2, Table 3, SHD Figure, vary_n Figure, llm_compare Figure
- [ ] 确认 appendix E/F/G 内容完整
- [ ] 对比正文实验部分与 KDD 版，确认无核心结果丢失

### 4.5 Discussion → Appendix H

| 操作 | 详情 |
|:---|:---|
| 全部 4 小节 | 移至 Appendix H "Extended Discussion" |
| 可选保留 | 在 Conclusion 中用 1-2 句概括核心 insight |

**TKDD Discussion 内容摘要** (用于 appendix 标题规划):
- H.1 Structure-Blind vs. Structure-Aware Generation
- H.2 Understanding the Fidelity-Privacy Trade-off
- H.3 When Does Structural Guidance Help Most?
- H.4 Relationship to Causal Inference

### 4.6 Limitations → Appendix I (或正文末尾极简版)

| 选项 | 说明 |
|:---|:---|
| **选项 A (推荐)** | 正文保留 `\section*{Limitations}`，内容压缩至 3-4 句 (点出 4 个方向: LLM 依赖、可扩展性、DAG 假设、API 成本) |
| **选项 B** | 完整移至 appendix，正文仅保留 `\section*{Limitations}` 标题 + 一句引用 |

**⚠️ EMNLP 要求**: 论文必须包含 Limitations 章节。无论选择哪个方案，正文中必须出现 `\section*{Limitations}`。

### 4.7 Conclusion

**操作**: 使用 KDD 版 + 融入 TKDD 的具体指标

```
Paragraph 1 (来自 KDD): 方法名、两阶段、核心结果概述
Paragraph 2 (来自 TKDD, 新增): 具体指标 (avg rank 1.00, +1.65 AUC, avg rank 1.33 privacy, 20-sample recovery, 7 LLM architectures)
不包含: 未来工作段落 (TKDD Paragraph 3)
```

**Subagent 校验点**:
- [ ] 确认 conclusion 包含核心定量指标
- [ ] 确认无未来工作段落

---

## 五、页数预算验证

### 5.1 重组后正文估算

| 章节 | 估算页数 | 内容 |
|:---|:---|:---|
| Abstract | 0.15 | 原样 |
| Introduction | 0.9 | KDD 版 + footnote DAG |
| Related Work | 0.5 | §2.1 + §2.2 + pipeline figure |
| Methodology | 1.8 | Problem Def + Discovery (压缩) + Synthesis + Table 1 |
| Experiments | 3.8 | Setups (压缩) + Results + Ablation + SHD + Sample Size + LLMs |
| Conclusion | 0.15 | 2 段 |
| Limitations | 0.2 | 简版 |
| **合计** | **~7.5** | **在 8 页限制内, 余量 ~0.5 页** |

### 5.2 关键浮动项

如果正文超过 8 页，按以下优先级继续削减:

| 优先级 | 削减项 | 预计节省 |
|:---|:---|:---|
| 1 | Design Rationale 段落完全删除 (仅保留 1 句) | ~0.1 页 |
| 2 | Table 1 (Performance) 移至 Experiments 或 Appendix | ~0.3 页 |
| 3 | Sample Size / LLM comparison 分析进一步压缩 | ~0.1 页 |
| 4 | Evaluation Metrics 完全移至 appendix (仅保留 metric 名称) | ~0.1 页 |
| 5 | Limitations 完全移至 appendix (仅保留标题 + 引用) | ~0.15 页 |

---

## 六、Subagent 任务分配

### Subagent 1: KDD vs TKDD 文字差异分析

**输入**: `Latex_Paper_KDD/sections/*.tex` vs `sections/*.tex`  
**任务**: 逐段比对两个版本，标记每处文字差异为以下类别之一:
- `IDENTICAL`: 完全相同
- `TKDD_EXPANDED`: TKDD 扩展了 KDD 的文字
- `TKDD_NEW`: TKDD 新增的段落/小节
- `TKDD_PROMOTED`: 从 KDD appendix 提升至 TKDD 正文的内容

**输出**: 逐文件差异清单，标注每处差异的行号和类别

### Subagent 2: Appendix 内容完整性校验

**输入**: 迁移后的 appendix 文件  
**任务**: 
- 确认 TKDD 版以下内容已完整出现在 appendix 中:
  - [ ] Structure Learning (PC, FCI, GES, FCMs, LLM-based)
  - [ ] Why a DAG? (4 个 paragraph)
  - [ ] Association Measures (Pearson's R, Correlation Ratio, Cramér's V 公式)
  - [ ] Algorithm 1 (完整伪代码)
  - [ ] Dataset 表 + Hyperparameter 表 + 完整 Metrics
  - [ ] Adult 三图 + Asia 六图 + 分析
  - [ ] Token 使用量表 + 分析
  - [ ] Discussion (4 小节)
  - [ ] 6 个 Prompt tcolorbox

**输出**: 完整性 checklist + 遗漏项列表

### Subagent 3: 正文交叉引用校验

**输入**: 编译后的 PDF + .log 文件  
**任务**:
- [ ] 确认所有 `\ref{}` 无 `??` 未解析引用
- [ ] 确认所有 `\cite{}` 正确显示
- [ ] 确认 Appendix A-I 的 section 编号连续
- [ ] 确认正文中引用 appendix 内容的语句指向正确编号

### Subagent 4: 页数与格式合规

**输入**: 编译后的 PDF  
**任务**:
- [ ] 统计正文页数 (不含 references 和 appendix)
- [ ] 确认 ≤ 8 页
- [ ] 确认 Limitations 章节存在
- [ ] 确认 Acknowledgments 在 review 模式下被隐藏
- [ ] 确认行号正确显示

---

## 七、执行时序

```
Phase 1: 内容拆分 (预计工作量最大)
  ├── Step 1: 复制 KDD 版 section 文件作为 EMNLP 正文基础
  ├── Step 2: 将 TKDD 版的新增/扩展内容标注并分类
  ├── Step 3: 按照第四节指南，将需要保留在正文的 TKDD 内容合并到 KDD 基础上
  └── Step 4: 将需要移至 appendix 的 TKDD 内容整理到 appendix 文件

Phase 2: 引用更新
  ├── Step 5: 更新正文中的交叉引用 (指向新的 appendix 编号)
  ├── Step 6: 更新 \label 命名 (避免与正文冲突)
  └── Step 7: 检查所有 \ref, \cite 命令

Phase 3: 编译验证
  ├── Step 8: 首次完整编译
  ├── Step 9: Subagent 1-4 并行执行校验
  └── Step 10: 根据校验结果修复问题

Phase 4: 微调
  ├── Step 11: 如超页，按第五节浮动项优先级削减
  └── Step 12: 最终编译确认
```

---

## 八、关键风险与注意事项

### 8.1 Table 1 的位置问题

TKDD 版将 Table 1 (Performance Comparison) 放在 `method.tex` 中，位于 Structure-Guided Synthesis 之前。KDD 版也是如此。对于 EMNLP:
- **选项 A (保持)**: Table 1 留在 Methodology，作为方法贡献的佐证
- **选项 B (迁移)**: Table 1 移至 Experiments Main Results，Methodology 更纯粹
- **建议**: 保持 KDD 版的位置 (选项 A)，但在页数紧张时可考虑选项 B 以释放 Methodology 空间

### 8.2 Pipeline Figure 的位置

Pipeline figure (`fig:pipeline`) 在 KDD/TKDD 版中位于 Related Work 顶部。对于 EMNLP 双栏格式:
- `figure*` 会跨双栏显示，可能占用较多空间
- 如果页数紧张，可考虑将此图移至 Methodology 顶部或 Appendix

### 8.3 引言中 DAG Footnote 的差异

KDD 版使用 `\footnote{Here, we use ``DAG'' to denote a directed dependency graph: edges capture statistical/probabilistic dependencies...}` 
TKDD 版改为交叉引用 `Section~\ref{sec:why_dag}`。
EMNLP 版应使用 KDD 的 footnote 方式，并在 appendix B 中保留完整论证。

### 8.4 实验分析的文字来源

本计划多处建议"使用 KDD 版分析"。实际操作时:
- KDD 版的实验分析已足够支撑核心论点
- TKDD 版的扩展分析 (如 "instructive discrepancy") 可在 appendix 的 Extended Discussion 中保留
- **不需要重写**，只需选择使用哪个版本

### 8.5 Label 命名一致性

TKDD 版引入了新的 label (如 `sec:why_dag`, `sec:synth`, `sec:association_scores`, `sec:algorithm`)。当这些内容移至 appendix 后:
- Label 应保持不变以避免引用断裂
- 或批量重命名并在所有引用处同步更新
- **建议**: 保持 label 不变，仅改变内容的物理位置
