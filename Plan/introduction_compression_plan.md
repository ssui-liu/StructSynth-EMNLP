# Introduction 压缩改进计划

> 目标：将 Introduction 从当前 ~2.5 页（含 Figure 1）压缩到 ~1.2-1.5 页，同时修正审阅文档指出的内容问题。
> 修改文件：`Latex-EMNLP/sections/introduction.tex`

---

## 一、当前结构诊断

当前 Introduction 为四段式 + Figure 1 + 3 条贡献，结构如下：

| 段落 | 内容 | 行数 | 问题 |
|---|---|---:|---|
| P1（L14-23） | 表格数据重要性 → 依赖关系 → 低数据三重失效模式 → 合成数据价值 | ~10行 | 铺垫过长；三重失效模式展开过细（statistical instability / structure learning collapse / generative overfitting 各自解释）；额外提到 class imbalance、missing values 等次要因素 |
| P2（L25-28） | DGM / Structure-Aware / LLM 三类方法详述 + 各自缺陷 | ~15行 | 最大的冗余来源。每类方法 3-5 句展开，引用了 TVAE、GAN、Diffusion、BN、DECAF、GOGGLE、CLLM 等具体方法名。与 P1 的依赖关系叙事有重复，且这些细节应属于 Related Work |
| P3（L33-41） | discover-then-synthesize 动机 + RQ1/RQ2 + 挑战描述 | ~8行 | RQ1/RQ2 与后文 Method 重复，单独成段拉长了篇幅 |
| P4（L44-55） | StructSynth 方法概述 + 3 条贡献 | ~12行 | 方法概述与 P3 有部分重复；贡献第3条 "best privacy-fidelity trade-off" overclaim 需修正 |
| Figure 1 | teaser 图 + 长 caption（Top/Middle/Bottom 描述） | 占 ~0.5页 | 图的 Top/Middle/Bottom caption 与 P2 正文高度重复；图本身标注已足够自解释 |

**核心问题**：P1 讲依赖关系+低数据困难，P2 又从三类方法角度重新讲依赖处理，叙事线有两轮循环。加上 P3 的 RQ 段和 Figure 1 的长 caption，导致进入方法之前花了过多篇幅。

---

## 二、目标结构：三段式

按审阅文档 §3.1 建议，将四段合并为三段，并处理 Figure 1。

### 新 P1：问题 + 低数据困难（目标 ~8-10 行）

**保留的核心主线**：
> Low-data tabular synthesis must preserve feature dependencies; discovering these dependencies reliably from limited samples is the fundamental bottleneck.

**具体操作**：

| 操作 | 原文位置 | 说明 |
|---|---|---|
| 保留 | L17 前半 | 表格数据承载依赖关系这一核心论点 |
| 大幅压缩 | L17-18 | healthcare/finance/education 只保留一句带过，删除 "foundational abstraction for modern data analytics" 等泛泛表述 |
| 压缩为一句 | L20 三重失效模式 | 当前 (i)(ii)(iii) 各有详细展开，压缩为一句概括：limited samples destabilize dependency discovery (spurious correlations), collapse structure learning, and cause generative overfitting |
| 删除 | L21 | "class imbalance, missing values, mixed types, long-tail" 这些次要因素在 Introduction 中不必提 |
| 压缩 | L22 | "resulting paradox" 句可删或压成半句 |
| 保留核心 | L23 | 合成数据的价值在于保留依赖关系，但措辞压缩 |

### 新 P2：现有方法缺口 + StructSynth 引出（目标 ~8-10 行）

**保留的核心主线**：
> Three paradigms exist but each has a structural bottleneck under data scarcity; we propose StructSynth as a discover-then-synthesize alternative.

**具体操作**：

| 操作 | 原文位置 | 说明 |
|---|---|---|
| 三类方法各压成一句 | P2 全段 | DGMs: learn implicitly, data-hungry → 一句。Structure-aware: need reliable graph, collapses under scarcity → 一句。LLMs: induce from serialized text, structure-blind → 一句 |
| 删除所有具体方法名 | P2 | TVAE、GAN、Diffusion、BN、DECAF、GOGGLE 等全部移到 Related Work；此处只说 "deep generative models"、"structure-aware methods"、"LLMs" |
| 删除 | P2 末尾总结句 | "In conclusion, existing paradigms either..." 与三句描述重复 |
| 合并 | P3 的动机句 | 将 "These observations motivate a discover-then-synthesize paradigm" 接在方法缺口后面，作为自然过渡 |
| 删除 | P3 的 RQ1/RQ2 | 两个 research question 与后文 Method 重复，删除或压成一句隐含表述 |
| 删除 | P3 的 "Addressing these questions poses significant challenges..." | 与 P1 的低数据困难叙述重复 |
| 引出 StructSynth | P4 L45 | 保留一句方法引出，但去掉 "as illustrated in the lower panel of Figure~\ref{fig:teaser}" 等指代（如果 Figure 1 移走的话） |

**关于引用 Figure 1 的处理**：
- 当前 P2 开头 "see Figure~\ref{fig:teaser}" 和 P4 "as illustrated in the lower panel of Figure~\ref{fig:teaser}" 需要根据 Figure 1 的最终处理方式调整
- 如果 Figure 1 保留在 Introduction：精简 caption，只保留 title 句，删除 Top/Middle/Bottom 描述
- 如果 Figure 1 移到 Appendix：删除所有 Figure 1 引用，可在方法缺口段末加 "(see Appendix Figure X for a visual taxonomy)"

### 新 P3：方法概述 + 贡献（目标 ~10-12 行）

**保留的核心主线**：
> StructSynth 的两阶段机制 + 2 条贡献。

**具体操作**：

| 操作 | 原文位置 | 说明 |
|---|---|---|
| 压缩 | P4 Stage 1 描述 | 当前 3 行描述 LLM-guided BFS + statistical cues + cycle resolution，压缩为 2 行。降低 BFS 的权重，强调 "LLM prior + statistical cues → executable dependency topology" |
| 压缩 | P4 Stage 2 描述 | 当前 3 行描述 topological layering + parent conditioning + design guarantee，压缩为 2 行 |
| 修正 | P4 脚注 | DAG 脚注保留但精简，明确 "dependency graph, not causal claim" |
| 修正表述 | P4 "guarantees...that the synthetic data strictly adheres to the discovered dependency structure" | 改为 "guarantees adherence to the discovered dependency graph"，避免暗示发现图=真实结构 |
| 贡献从 3 条压为 2 条 | P4 贡献列表 | 见下方详细说明 |

**贡献改写**：

当前 3 条：
1. discover-then-synthesize framework（框架贡献）
2. LLM-guided structure discovery + structure-conditioned generation（方法贡献）
3. state-of-the-art utility + best privacy-fidelity trade-off（实验贡献）→ **overclaim，需修正**

改为 2 条：
1. **框架+方法合并**：A discover-then-synthesize framework that converts LLM reasoning and statistical evidence into an executable global dependency topology, then uses it as a structural blueprint for controlled, layer-wise data generation.（强调 "executable topology as control interface"，对齐审阅文档的核心定位建议）
2. **实验**：Extensive experiments across six datasets demonstrating state-of-the-art downstream utility and privacy preservation, with competitive structural fidelity, and robustness to sample size and LLM backbones.（修正 overclaim，增加 robustness 维度）

---

## 三、Figure 1 处理方案

### 方案 A：保留 Figure 1，精简 caption（推荐，如果不需要极限压缩页数）

- 删除 caption 中的 Top/Middle/Bottom 逐段描述
- 只保留一句 title，例如：
  > **Tabular synthesis paradigms under data scarcity.** Existing approaches handle dependencies implicitly, from pre-learned graphs, or through serialized text. \textsf{StructSynth} explicitly discovers an executable dependency topology and uses it as a generation blueprint.
- 优化 Figure 1 title（结合之前讨论的分析）

### 方案 B：Figure 1 移到 Appendix（如果需要极限压缩）

- 可节省 ~0.4-0.5 页
- 删除正文中所有 Figure 1 引用
- 在 Appendix 中保留完整 caption

---

## 四、P0 级内容修正（必须同步完成）

这些修正来自审阅文档 §1-§2，在 Introduction 中涉及的部分：

| 问题 | 位置 | 修改 |
|---|---|---|
| "best privacy-fidelity trade-off" overclaim | 贡献第3条（L54） | → "best downstream utility and privacy preservation, while maintaining competitive structural fidelity" |
| "guarantees...strictly adheres to the discovered dependency structure" 过强 | P4 Stage 2（L49） | → "guarantees adherence to the discovered dependency graph" |
| 贡献被认为偏 applied/pipeline 拼接 | 贡献表述 | 强调 "executable dependency topology as generation-time control interface"，而非 "LLM + BFS + DAG" |
| DAG 被误读为 causal graph | P4 脚注（L48） | 脚注保留并精简，确保措辞为 "dependency graph"，非 "causal graph" |
| Introduction 未与 CLLM/GraDe 明确区分 | 新 P2 末尾 | 加一句差异点明：existing LLM methods do in-context generation or local dependency modeling, whereas StructSynth outputs a global executable topology |

---

## 五、预期效果

| 指标 | 改前 | 改后 |
|---|---|---|
| 段落数 | 4段 + Figure 1 长 caption | 3段 + Figure 1 短 caption（或移走） |
| Introduction 页数（含 Figure 1） | ~2.5 页 | ~1.2-1.5 页 |
| 贡献条数 | 3 条 | 2 条 |
| 具体方法名引用 | TVAE, GAN, Diffusion, BN, DECAF, GOGGLE, CLLM 等 | 全部移到 Related Work |
| Overclaim | "best privacy-fidelity trade-off" | 修正为准确表述 |
| 与 P2/Related Work 重复 | 严重 | 消除 |

---

## 六、实施顺序

1. 先决定 Figure 1 的处理方案（保留精简 vs 移到 Appendix）
2. 重写 P1：问题+低数据困难
3. 重写 P2：方法缺口+StructSynth 引出
4. 重写 P3：方法概述+2 条贡献
5. 处理 Figure 1 caption（精简或移走）
6. 检查所有 P0 级内容修正是否到位
7. 用 `texcount` 或手动统计确认压缩效果
