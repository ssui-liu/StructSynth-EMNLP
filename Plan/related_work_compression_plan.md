# Related Work 压缩改进计划

> 目标：将正文 Related Work 从当前 ~1.5 页压缩到 ~0.7-0.8 页，重组为 "closest work only" 结构，消除与 Introduction 的重复；同时在 Appendix 新增 Extended Related Work，承接正文移出的详细内容。
> 修改文件：`Latex-EMNLP/sections/related_work.tex`、`Latex-EMNLP/sections/appendix.tex`

---

## 一、当前结构诊断

当前 Related Work 为两小节结构：

| 小节 | 内容 | 行数 | 问题 |
|---|---|---:|---|
| §2.1 Conventional（L12-17） | 早期方法（SMOTE、Copulas）→ DGMs（TVAE、CTGAN、Normalizing Flow、TabDDPM、TabSyn）→ Structure-Aware（BN、PrivBayes、DECAF、GOGGLE） | ~18行 | **最大问题**：(1) SMOTE/Copula/TVAE/CTGAN/TabDDPM/TabSyn 等与 StructSynth 关系较远，逐一展开浪费篇幅；(2) DGM 和 Structure-Aware 的缺陷描述与 Introduction 高度重复（"implicitly learn dependencies"、"challenges under limited data"） |
| §2.2 LLM-Based（L20-21） | GReaT、TAPTAP、AIGT → CLLM → TabGen-ICL → GraDe → 总结句 | ~12行 | 覆盖较全但 (1) fine-tuning 方法（GReaT/TAPTAP/AIGT）一句话即可带过；(2) 缺少 LLM-assisted dependency/graph discovery 这一与 StructSynth 最直接相关的线索；(3) 末尾总结句与 Introduction 新 P2 的方法缺口论述重复 |

**核心问题**：
1. **与 Introduction 重复严重**——DGM/Structure-Aware/LLM 三类方法的缺陷在 Introduction 已经讲过，Related Work 又重述一遍
2. **远近不分**——SMOTE、Copula、TVAE、CTGAN 等远端工作与 StructSynth 关系不大，却占了大量篇幅
3. **缺少最关键的对比线**——LLM-assisted graph/dependency discovery（如 LLM 用于因果发现、结构学习等）是 StructSynth 最直接的相关工作，当前完全缺失

---

## 二、整体策略：正文三段 + Appendix Extended Related Work

### 设计原则

正文三段必须**自成体系**：审稿人不翻 Appendix 也能完整理解 StructSynth 的定位。具体分工：

- **正文保留**：每类范式的一句定位 + 一句核心局限（只删展开，不删结论）
- **Appendix 扩展**：各方法的详细机制描述、更完整的引用覆盖、历史脉络

### 正文 vs Appendix 内容分工

| 正文保留 | Appendix 扩展 |
|---|---|
| DGM 一句定位 + 一句低数据局限 | 各 DGM 方法的详细机制（TVAE 的 VAE 架构、TabSyn 的 latent diffusion 等） |
| Structure-Aware 一句定位 + 一句图退化局限 | BN/PrivBayes 的隐私机制、DECAF 的 fairness 机制、GOGGLE 的 graph-VAE 细节 |
| CLLM / TabGen-ICL / GraDe 与 StructSynth 的差异对比 | Fine-tuning 方法（GReaT/TAPTAP/AIGT）的详细机制与对比 |
| LLM graph discovery 完整段落（新增，不拆分到 Appendix） | 早期方法（SMOTE/Copula）的历史脉络 |
| 每类方法的代表性引用 | 更完整的引用列表与分类讨论 |

---

## 三、正文目标结构：三段式（closest work only）

按审阅文档 §3.2 建议，重组为三个紧凑段落，不设子标题（或仅用 \paragraph 轻标题）。正文末尾加一句引导读者参阅 Appendix。

### 新段落 1：Tabular Synthesis in Low-Data Regimes（目标 ~4-5 行）

**核心定位**：
> 一句话带过 DGM 和 Structure-Aware 两类范式的核心思路与低数据瓶颈，建立 StructSynth 的研究背景。

**具体操作**：

| 操作 | 原文位置 | 说明 |
|---|---|---|
| 移到 Appendix | L13 SMOTE/Copula 段 | 早期方法与本文方法无直接关系，移到 Appendix Extended Related Work |
| 大幅压缩 | L14-15 DGM 段 | 当前逐一列举 TVAE → CTGAN → NF → TabDDPM → TabSyn 并分别描述优点。压缩为一句：Deep generative models (VAEs, GANs, diffusion models) learn the joint distribution implicitly but are data-hungry and offer limited control over feature dependencies (cite 代表性 2-3 篇)。各方法的详细机制描述移到 Appendix |
| 大幅压缩 | L16-17 Structure-Aware 段 | 当前逐一介绍 BN/PrivBayes/DECAF/GOGGLE。压缩为一句：Structure-aware methods (BN-based, graph-VAEs) incorporate explicit dependency structures but rely on graphs learned from data, which degrade under scarcity (cite 代表性 2-3 篇)。各方法细节移到 Appendix |
| 删除 | DGM/Structure-Aware 缺陷的详细展开 | "limited interpretability and controllability"、"posing challenges especially under limited data scenarios" 等与 Introduction 重复的表述全部删除，正文只需一个简短的局限定位句 |
| 保留引用但移除描述 | TVAE、CTGAN、TabDDPM、TabSyn、PrivBayes、DECAF、GOGGLE | 正文作为 citation 保留（集中引用），详细描述移到 Appendix |

### 新段落 2：LLM-Based Tabular Generation（目标 ~6-8 行）

**核心定位**：
> 重点对比 StructSynth 与 LLM-based 方法的关系：fine-tuning vs prompting vs structure-guided，明确 StructSynth 的差异化定位。

**具体操作**：

| 操作 | 原文位置 | 说明 |
|---|---|---|
| 压缩为一句 | L21 fine-tuning 方法 | GReaT/TAPTAP/AIGT 当前各有提及。正文压缩为一句带过，详细对比移到 Appendix。正文：Fine-tuning approaches (GReaT, TAPTAP) serialize rows as text and fine-tune LLMs for autoregressive generation, but are computationally expensive and degrade under data scarcity |
| 保留并精简 | L21 CLLM | CLLM 是最直接的 prompt-based baseline，正文保留 1-2 句核心描述：CLLM uses curated in-context examples to guide generation without parameter updates, but treats columns independently without modeling inter-feature dependencies |
| 保留并精简 | L21 TabGen-ICL | 正文保留 1 句描述其 iterative distribution alignment 思路 |
| 重写对比 | L21 GraDe | GraDe 是结构相关的 LLM 方法，正文需重点对比，精简为 1-2 句，突出差异：GraDe injects a learned sparse dependency graph into Transformer attention, but the graph serves as an attention mask rather than an explicit generation blueprint, and requires model fine-tuning |
| 删除 | L21 末尾总结句 | "Nevertheless, while these methods induce or integrate dependencies implicitly or locally..." 与 Introduction 重复 |
| 新增差异总结 | 段末 | 加一句点明 StructSynth 的独特定位：Unlike these methods, StructSynth first discovers an interpretable global dependency topology and then uses it as an executable blueprint for structure-preserving generation, without any model fine-tuning |

### 新段落 3：LLM-Assisted Dependency / Graph Discovery（目标 ~4-5 行）

**核心定位**：
> 这是当前 Related Work 完全缺失但与 StructSynth Stage 1 最直接相关的线索——LLM 被用于因果/依赖关系发现。此段为新增内容，全部保留在正文，不拆分到 Appendix。

**具体操作**：

| 操作 | 说明 |
|---|---|
| 新增 | 介绍 LLM 用于因果发现/结构学习的代表性工作（如 LLM-based causal discovery、LLM for DAG learning 等） |
| 新增 | 指出这些工作的共同局限：(1) 主要面向因果推断而非数据生成；(2) 没有将发现的图作为 tabular generation 的控制接口 |
| 新增差异总结 | StructSynth bridges this gap by converting the discovered dependency topology into an executable generation blueprint—the graph is not an end in itself but a structural contract that governs layer-wise synthesis |

**需要补充的引用**（需调研确认）：
- LLM-based causal discovery 相关工作（如有）
- LLM for structure learning / graph discovery 相关工作
- 可以考虑：BFS/graph search + LLM 的组合方法

### 正文末尾引导句

在段落 3 结束后加一句引导：
> A more comprehensive discussion of related methods is provided in Appendix~\ref{sec:extended_related_work}.

---

## 四、Appendix Extended Related Work 结构设计

在 `appendix.tex` 中新增一节，承接正文移出的详细内容。结构如下：

### §X Extended Related Work

#### §X.1 Early and Statistical Methods

| 内容来源 | 说明 |
|---|---|
| 原 L13 SMOTE/Copula 段 | 保留完整描述，补充历史脉络：从统计方法到深度学习的过渡 |

#### §X.2 Deep Generative Models for Tabular Data

| 内容来源 | 说明 |
|---|---|
| 原 L14-15 DGM 段的详细描述 | TVAE 的 VAE 架构细节、CTGAN 的 training-by-sampling 机制、Normalizing Flow 的可逆变换、TabDDPM 的扩散过程、TabSyn 的 latent space diffusion |
| 可补充 | 各方法在低数据场景下的具体表现差异（如有实验数据支撑） |

#### §X.3 Structure-Aware Generative Methods

| 内容来源 | 说明 |
|---|---|
| 原 L16-17 Structure-Aware 段的详细描述 | BN 的图结构学习、PrivBayes 的隐私保护机制、DECAF 的因果公平性、GOGGLE 的 graph-based VAE |
| 可补充 | 图学习方法在小样本下退化的具体机制分析 |

#### §X.4 LLM-Based Tabular Generation: Extended Discussion

| 内容来源 | 说明 |
|---|---|
| 原 L21 fine-tuning 方法的详细描述 | GReaT 的 row serialization + fine-tuning 细节、TAPTAP 的 table-pretraining 策略、AIGT 的增强生成 |
| 可补充 | 与 StructSynth 在计算开销、数据需求、结构保持方面的更详细对比表（可考虑加一个 comparison table） |

### Appendix 写作原则

1. **不是正文的简单复制粘贴**——Appendix 应比原正文更深入，补充正文无法展开的机制细节和对比分析
2. **保持与正文的引用一致性**——正文中集中引用的方法，在 Appendix 中提供详细描述
3. **可考虑增加对比表**——用表格形式总结各方法在 dependency handling / data requirement / generation control 等维度的对比

---

## 五、P0 级内容修正（必须同步完成）

| 问题 | 位置 | 修改 |
|---|---|---|
| 与 Introduction 重复的缺陷描述 | 正文各段末尾 | 全部删除。Related Work 只做客观描述 + 与 StructSynth 的差异对比，不重复 Introduction 已有的 "paradigm gap" 论述 |
| TabSyn 描述过长 | L15 | 正文压缩为 citation only 或最多半句；详细描述移到 Appendix §X.2 |
| GraDe 描述与 Introduction 定位冲突 | L21 | 正文需明确其图是 attention mask 而非 generation blueprint，与 StructSynth 区分 |
| "Recently" / "More recently" 过多 | 多处 | 时间副词（recently、more recently、very recently）出现 3+ 次，正文删除大部分，保留至多 1 个 |
| 注释掉的 footnote | L10 | `% \footnote{+yq+: shall we merge 2.1 and 2.2...}` 清理掉 |

---

## 六、需要额外调研的内容

新段落 3（LLM-Assisted Dependency/Graph Discovery）是当前完全缺失的内容，需要补充引用。调研方向：

1. **LLM for causal discovery**：如 LLM-based pairwise causal reasoning、LLM + PC/FCI algorithm
2. **LLM for structure learning**：如 LLM 辅助 DAG 搜索、LLM 作为变量关系先验
3. **Graph discovery + generation 的结合**：是否有工作将发现的图用于下游生成任务

如果调研后发现该方向文献较少，可以将段落 3 缩短为 2-3 句，强调 StructSynth 的新颖性。

---

## 七、预期效果

| 指标 | 改前 | 改后（正文） | 改后（Appendix） |
|---|---|---|---|
| 小节数 | 2 个小节（§2.1 Conventional + §2.2 LLM-Based） | 3 个段落（\paragraph 轻标题） | 4 个小节（§X.1-X.4） |
| 篇幅 | ~1.5 页 | ~0.7-0.8 页 | ~0.8-1.0 页 |
| 与 Introduction 重复度 | 高（DGM/Structure-Aware/LLM 缺陷各讲两遍） | 消除（只做客观对比，不重复 gap 论述） | 不适用 |
| 远端工作 | SMOTE、Copula 等占正文大量篇幅 | 正文只保留 closest work | Appendix 提供完整覆盖 |
| LLM graph discovery | 完全缺失 | 正文新增独立段落 | — |
| GraDe 对比 | 描述详细但未明确与 StructSynth 区分 | 精简 + 明确差异 | Appendix 提供详细对比 |
| 审稿人体验 | 正文冗长，重复感强 | 正文精炼自成体系，深度内容在 Appendix 可查 | 展示充分的文献调研 |

---

## 八、实施顺序

1. **调研**：补充 LLM-assisted dependency/graph discovery 的引用（正文段落 3 所需）
2. **清理注释**：删除 L10 的注释掉的 footnote
3. **重写正文段落 1**：Tabular Synthesis in Low-Data Regimes（压缩 DGM + Structure-Aware）
4. **重写正文段落 2**：LLM-Based Tabular Generation（精简 + 重点对比 CLLM/TabGen-ICL/GraDe）
5. **新写正文段落 3**：LLM-Assisted Dependency/Graph Discovery（补充缺失的对比线）
6. **添加正文引导句**：指向 Appendix Extended Related Work
7. **编写 Appendix Extended Related Work**：将正文移出的详细描述重新组织为 §X.1-X.4，适当补充深入分析
8. **检查引用完整性**：确保正文和 Appendix 中的 cite 覆盖所有相关工作
9. **检查与 Introduction 的互补性**：确认正文 Related Work 与 Introduction 无重复表述
