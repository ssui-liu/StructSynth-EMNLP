# Experiments 保守压缩改进计划

> 目标：将 Experiments 正文散文从当前 ~1894 词压缩到 ~1300-1450 词，保留 Table 2（Privacy/Fidelity per-dataset）在正文中。保留所有核心证据和浮动体的论证力，只削减冗余论述。
> 修改文件：`Latex-EMNLP/sections/experiments.tex`
> 压缩策略：保守——保留全部表格/图片在正文，只压缩散文部分的冗余表述和重复论点

---

## 一、当前结构量化诊断

### 1.1 整体指标

| 指标 | 当前值 |
|---|---|
| 总词数（含 LaTeX 表/图代码） | 2775 |
| 散文词数（不含表/图环境） | 1894 |
| subsection 数 | 6 |
| subsubsection 数 | 6 |
| 表格数 | 2（Table 2 Privacy/Fidelity + Table 3 Ablation） |
| 图片数 | 3（Figure 3 SHD + Figure 4 n-sweep + Figure 5 LLM-compare） |

注：Table 1（Downstream Performance）位于 `method.tex` 中作为浮动体，但在 §4.2.1 中引用。

### 1.2 各部分散文词数

| 部分 | 位置 | 词数 | 问题诊断 |
|---|---|---:|---|
| §4.1 Setup: Datasets | L3-4 | 106 | 基本合理，但 bnlearn 数据集描述可精简 |
| §4.1 Setup: Baselines | L7-8 | 42 | 已足够紧凑 |
| §4.1 Setup: Metrics | L10-19 | 184 | **主要压缩来源**。三个 metric 各用 3-4 行 itemize 展开，但 Appendix 已有完整定义。正文可压成紧凑段落 |
| §4.1 Setup: Impl Details | L21-23 | 66 | 基本合理 |
| §4.2.1 Downstream Perf | L89-90 | 150 | 末尾 "validates our core hypotheses..." 和 "strongly confirm..." 表述偏强，可精简 |
| §4.2.2 Privacy/Fidelity | L94-98 | 238 | **主要压缩来源**。Table 2 保留在正文，但两段讨论中逐 baseline 分析过于详细，可精简论述同时保留核心洞察 |
| §4.3 Ablation Study | L111-144 | 256 | 设置段（~113词）+ 结果段（~143词）。设置段列举 7 个 variant 较长但必要；结果段可精简 |
| §4.4 Structural Fidelity | L151-158 | 322 | **最大压缩来源**。逐数据集分析（Asia/Child/Insurance 各一段）过于细致，可压成一段概括 |
| §4.5 Influence of n | L161-180 | 199 | 分三维度（AUC/Fidelity/Privacy）逐一讨论，可合并为更紧凑的论述 |
| §4.6 Influence of LLM | L184-190 | 221 | 两段，第一段有模型列表重复（已在图中展示），可精简 |

### 1.3 关于 Table 2 的保留决策

Table 2（Privacy/Fidelity per-dataset）保留在正文，理由：
1. Privacy rank 1.33 是强卖点，per-dataset 细节增强说服力
2. 三维度评估（Utility + Privacy + Fidelity）完整性是论文优点
3. 移走可能被审稿人认为隐藏弱结果（fidelity rank 7.08），反而引起怀疑

因此本计划的页数节省完全来自散文压缩，不涉及浮动体迁移。

---

## 二、压缩操作清单

### OP-1：压缩 Evaluation Metrics

| 属性 | 值 |
|---|---|
| **改动类型** | 重写（itemize → 紧凑段落） |
| **位置** | L10-19（§4.1 Evaluation Metrics） |
| **预估节省** | ~100 词（从 ~184 词压到 ~80 词） |

**具体做法**：

当前三个 metric 用 `\begin{itemize}` 逐条展开，每条 3-4 行。Appendix~\ref{app:metrics} 已有完整定义。正文改为一个紧凑段落，每个 metric 用一句话概括：

> We evaluate synthetic data quality along three axes (detailed definitions in Appendix~\ref{app:metrics}): \textbf{Downstream Model Performance} (AUC for classification, $R^2$ for regression, trained on $\mathcal{D}_{\mathtt{aug}}$ and evaluated on $\mathcal{D}_{\mathtt{test}}$); \textbf{Statistical Fidelity} (mean pairwise correlation difference between real and synthetic data; lower is better); and \textbf{Privacy Risk} (fraction of synthetic nearest neighbors from training set; closer to 0.5 is better).

**审计检查点**：
- [ ] 三个 metric 名称保留（Downstream Model Performance / Statistical Fidelity / Privacy Risk）
- [ ] 每个 metric 的方向性说明保留（AUC/R² ↑，Fidelity ↓，Privacy → 0.5）
- [ ] Appendix~\ref{app:metrics} 引用保留
- [ ] itemize 环境已删除
- [ ] 词数 ≤ 85

---

### OP-2：压缩 Privacy/Fidelity 讨论（保留 Table 2）

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L94-98（§4.2.2） |
| **预估节省** | ~100 词（从 ~238 词压到 ~140 词） |

**具体做法**：

Table 2 保留在正文，但两段讨论中逐 baseline 的对比分析过于详细。压缩策略：

1. **合并两段为一段**：当前第一段分析各 baseline 的 fidelity-privacy trade-off，第二段讲 StructSynth 的优势。合并后一段即可
2. **删除逐 baseline 分析**：当前逐一分析 GraDe（"attention-based generation tends toward data memorization"）、NFlow/CTGAN（"exhibit mediocre privacy and poor downstream utility"）、CLLM（"strong privacy but lower statistical fidelity"）。压缩为：用 GReaT 作为唯一具体例子点明 fidelity-privacy tension（fidelity rank 3.33 但 privacy risk 90.15%），其余 baseline 不逐一展开
3. **保留核心数据点**：StructSynth privacy rank 1.33, fidelity rank 7.08；与 CLLM 对比（privacy 1.33 vs 3.33）
4. **修正 overclaim**："superior privacy-fidelity trade-off" → "best privacy preservation with competitive fidelity"

**审计检查点**：
- [ ] Table 2 引用（tab:results_comparison_merged）保留
- [ ] StructSynth 的 privacy rank (1.33) 和 fidelity rank (7.08) 在文中出现
- [ ] GReaT 的 memorization 例子保留（作为 fidelity-privacy tension 的具体证据）
- [ ] "superior privacy-fidelity trade-off" 不出现
- [ ] NFlow/CTGAN/GraDe 的逐一分析已删除
- [ ] 词数 ≤ 145

---

### OP-3：精简 Downstream Model Performance 讨论

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L89-90（§4.2.1） |
| **预估节省** | ~50 词（从 ~150 词压到 ~100 词） |

**具体做法**：

1. 删除末尾过强论述："These findings strongly confirm that \textsf{StructSynth}'s decoupled design..." — 与 Introduction/Method 重复
2. 删除 "validates our core hypotheses: implicit learning is unreliable with sparse data, and generative performance is crippled if the initial structure discovery fails" — 过于 self-referential
3. 保留核心数据点：rank 1.00、avg score 75.01 vs CLLM 73.36 vs D_train 71.54
4. 保留一句简短的 insight（结构化指导的增益）

**审计检查点**：
- [ ] Table 1 引用保留
- [ ] 核心数据点（rank 1.00、75.01、73.36、71.54）保留
- [ ] "validates our core hypotheses" 删除
- [ ] "strongly confirm" 删除
- [ ] 词数 ≤ 105

---

### OP-4：压缩 Structural Fidelity 讨论

| 属性 | 值 |
|---|---|
| **改动类型** | 大幅重写 |
| **位置** | L151-158（§4.4） |
| **预估节省** | ~200 词（从 ~322 词压到 ~120 词） |

**具体做法**：

当前逐数据集分析（Asia 一段、Child 一段、Insurance 一段），每段解释为什么 StructSynth 在该数据集上表现好。这种逐数据集展开对 EMNLP 8 页限制来说过于奢侈。

压缩为两段：
1. **实验设置**（~30 词）：bnlearn 三个数据集 + SHD metric + 引用 Figure
2. **总结性结论**（~90 词）：StructSynth 在所有数据集和样本量下一致优于 baseline；LLM 先验在低数据（n≤50）时优势最大；传统方法（FCI/GOGGLE/NoTears）误差显著更高。Appendix 引用保留。

**删除内容**：
- Asia "maintains an SHD near 1, whereas baselines fluctuate..." 的详细叙述
- Child "errors in early discovery stages can cascade" 的机制分析
- Insurance "prioritizing the discovery of a stable structural blueprint" 的归因
- "validates the first stage of our framework" — self-referential
- "crucial for ensuring the subsequent generation follows valid causal pathways" — causal language

**审计检查点**：
- [ ] Figure~\ref{fig:shd} 引用保留
- [ ] SHD metric 的含义简要说明保留
- [ ] 三个数据集名称（Asia/Child/Insurance）出现
- [ ] Appendix~\ref{app:qualitative_graph_analysis} 引用保留
- [ ] 无 "causal pathway" 表述
- [ ] 词数 ≤ 125

---

### OP-5：压缩 Influence of Training Sample Size

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L161-180（§4.5） |
| **预估节省** | ~80 词（从 ~199 词压到 ~120 词） |

**具体做法**：

当前分三段分别讨论 AUC、Statistical Fidelity、Privacy deviation。合并为一段紧凑论述：
1. 总结：StructSynth 在 n=20 到 n=200 全范围一致优于 baseline
2. 关键洞察：低数据（n≤50）时优势最大
3. 三维度压成一句："maintains high AUC, low fidelity error, and near-0.5 privacy score across all sample sizes"
4. 删除 "Pareto-like behavior" 等修辞性表述

**审计检查点**：
- [ ] Figure~\ref{fig:influence_n} 引用保留
- [ ] n 范围（20 到 200）提及
- [ ] 三维度（AUC/Fidelity/Privacy）在同一段中覆盖
- [ ] "Pareto-like behavior" 删除
- [ ] 词数 ≤ 125

---

### OP-6：压缩 Influence of Different Language Models

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L184-190（§4.6） |
| **预估节省** | ~100 词（从 ~221 词压到 ~120 词） |

**具体做法**：

1. **删除模型列表重复**：当前第一段列出 "Qwen-2.5, Llama-4, DeepSeek series, GPT-4o series" + 各 citation。这些信息在图中已完全展示，正文只需 "a diverse set of open-source and proprietary LLMs"
2. **压缩 DeepSeek R1 设置说明**："due to the high inference cost of DeepSeek R1, its evaluation is limited to 100 synthetic samples" — 移到 caption 或 footnote
3. **删除修辞性表述**："This overall pattern confirms that our framework offers a fundamental advantage, effectively elevating the performance ceiling regardless of the base LLM's initial capabilities" — 过强
4. **保留核心结论**：StructSynth 在所有测试的 LLM 上一致优于 CLLM；结构化指导对中等能力模型增益最大
5. **token overhead 句保留**

**审计检查点**：
- [ ] Figure~\ref{fig:llm_compare} 引用保留
- [ ] 不再在正文中逐一列举 LLM 名称及 citation
- [ ] Appendix~\ref{sec:token_usage} token 分析引用保留
- [ ] "fundamental advantage" / "elevating the performance ceiling" 删除
- [ ] 词数 ≤ 125

---

### OP-7：精简 Ablation Study 结果讨论

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L144（结果讨论段） |
| **预估节省** | ~40 词（从 ~143 词压到 ~100 词） |

**具体做法**：

结果段当前分三个 bold 要点展开。结构清晰但可以更紧凑：
1. 保留三个核心 insight 但各压缩 1-2 句
2. 删除 "Additionally, removing statistical prompts..." — 已在第一个要点隐含
3. "correct causal ordering" → "correct topological ordering"（P0 修正）

**审计检查点**：
- [ ] Table~\ref{tab:ablation_study} 引用保留
- [ ] 三个核心 insight 保留（LLM > classical, structure matters, synergy is vital）
- [ ] 关键数值（1.0-1.4 pts, 1.6 pts, 1.1 pts, -4.4 pts）保留
- [ ] "causal ordering" 替换为 "topological ordering"
- [ ] 词数 ≤ 105

---

## 三、P0 级内容修正（须同步完成）

| 问题 | 位置 | 修改 | 审计检查点 |
|---|---|---|---|
| "superior privacy-fidelity trade-off" overclaim | §4.2.2 末尾 | 改为 "best downstream utility and privacy preservation, with competitive statistical fidelity" | [ ] overclaim 表述不出现 |
| "validates our core hypotheses" self-referential | §4.2.1 | 删除 | [ ] 不出现 |
| "strongly confirm" 过强 | §4.2.1 | 删除 | [ ] 不出现 |
| "correct causal ordering" | §4.3 | → "correct topological ordering" | [ ] "causal ordering" 不出现 |
| "valid causal pathways" | §4.4 | 删除或改为 "valid dependency pathways" | [ ] "causal pathways" 不出现 |
| "consistently outperforms all baselines" 过强 | §4.2.1 | → "achieves the best mean performance on all six datasets" 或类似表述 | [ ] "consistently outperforms all" 不出现 |

---

## 四、不在本计划范围内的项目

以下为审阅文档建议的实验补强，属于独立任务：
1. **多数据集 n-sweep / LLM-backbone 实验**（需要跑实验）
2. **Downstream model sensitivity**（加 Logistic/RF/MLP，需跑实验）
3. **Anonymized-schema ablation**（需跑实验）
4. **显著性检验**（需统计计算）
5. **Table 1 减少小数位**（排版优化，非压缩）
6. **Figure 4/5 合并为一个两栏小图**（排版优化，可选）

---

## 五、预期效果

| 指标 | 改前 | 改后 | 变化 |
|---|---|---|---|
| 散文词数 | 1894 | ~1300-1450 | -444 到 -594 词（-23% 到 -31%） |
| 正文表格 | 2 | 2（均保留） | 不变 |
| 正文图片 | 3 | 3 | 不变 |
| subsection 数 | 6 | 6 | 不变 |
| subsubsection 数 | 6 | 6 | 不变 |
| 预估页数节省 | — | ~0.5-0.8 页 | 纯散文压缩 |

### 各操作节省词数预估汇总

| 操作 | 节省词数 |
|---|---:|
| OP-1：压缩 Evaluation Metrics | ~100 |
| OP-2：压缩 Privacy/Fidelity 讨论（保留 Table 2） | ~100 |
| OP-3：精简 Downstream Perf 讨论 | ~50 |
| OP-4：压缩 Structural Fidelity 讨论 | ~200 |
| OP-5：压缩 Influence of n | ~80 |
| OP-6：压缩 Influence of LLM | ~100 |
| OP-7：精简 Ablation 结果讨论 | ~40 |
| **合计** | **~670** |

注：部分操作会增加少量替代文字，实际净节省约 **~450-600 词**。

---

## 六、实施顺序与 Git 提交计划

| 步骤 | 操作 | Git commit message |
|---|---|---|
| 1 | OP-1：压缩 Evaluation Metrics | `Experiments OP-1: Compress Evaluation Metrics to paragraph (~100 words saved)` |
| 2 | OP-2：压缩 §4.2.2 Privacy/Fidelity 讨论 | `Experiments OP-2: Tighten Privacy/Fidelity discussion, keep Table 2 (~100 words saved)` |
| 3 | OP-3：精简 §4.2.1 | `Experiments OP-3: Tighten Downstream Performance discussion (~50 words saved)` |
| 4 | OP-4：压缩 §4.4 Structural Fidelity | `Experiments OP-4: Compress Structural Fidelity discussion (~200 words saved)` |
| 5 | OP-5：压缩 §4.5 Influence of n | `Experiments OP-5: Compress Influence of n discussion (~80 words saved)` |
| 6 | OP-6：压缩 §4.6 Influence of LLM | `Experiments OP-6: Compress Influence of LLM discussion (~100 words saved)` |
| 7 | OP-7：精简 §4.3 Ablation 结果 | `Experiments OP-7: Tighten Ablation results discussion (~40 words saved)` |
| 8 | P0 修正：overclaim + causal 语言 | `Experiments P0: Fix overclaims and causal language` |
| 9 | 审计：词数 + 结构 + 内容检查 | 不产生 commit，仅输出报告 |

---

## 七、完整审计检查清单

### 结构审计
- [ ] subsection 数 = 6（不变）
- [ ] subsubsection 数 = 6（不变）
- [ ] Table 2 保留在 `experiments.tex` 中

### 浮动体审计
- [ ] Table 2（Privacy/Fidelity）保留在正文
- [ ] Table 3（Ablation）保留在正文
- [ ] Figure 3（SHD）保留在正文
- [ ] Figure 4（n-sweep）保留在正文
- [ ] Figure 5（LLM-compare）保留在正文

### 词数审计
- [ ] §4.1 Evaluation Metrics ≤ 85 词
- [ ] §4.2.1 Downstream Perf ≤ 105 词
- [ ] §4.2.2 Privacy/Fidelity ≤ 145 词
- [ ] §4.3 Ablation 结果讨论 ≤ 105 词
- [ ] §4.4 Structural Fidelity ≤ 125 词
- [ ] §4.5 Influence of n ≤ 125 词
- [ ] §4.6 Influence of LLM ≤ 125 词
- [ ] 总散文词数 ≤ 1450 词

### 内容审计
- [ ] 所有 Appendix 引用保留（app:datasets, app:baselines, app:metrics, app:hyperparameter, app:qualitative_graph_analysis, sec:token_usage）
- [ ] 所有表/图引用保留（tab:results_comparison_performance, tab:results_comparison_merged, tab:ablation_study, fig:shd, fig:influence_n, fig:llm_compare）
- [ ] "superior privacy-fidelity trade-off" overclaim 不出现
- [ ] "validates our core hypotheses" 不出现
- [ ] "strongly confirm" 不出现
- [ ] "consistently outperforms all baselines" 不出现
- [ ] "causal ordering" / "causal pathways" 不出现
- [ ] 四类核心证据保留：Utility 主表引用 + Privacy/Fidelity 表引用 + Ablation 表引用 + SHD 图引用 + Robustness（n-sweep + LLM）
