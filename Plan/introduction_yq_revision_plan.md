# Introduction 改进计划（基于 YQ 意见）

> 目标：按 YQ 提出的五段式叙事框架重构 Introduction，从"所有方法都有问题"的 aggressive 叙事转为"逐层递进、公允评价、精准定位 novelty"的成熟叙事。
> 修改文件：`Latex-EMNLP/sections/introduction.tex`
> 参考文件：`yq_comments.md`

---

## 一、总体叙事对比

| 维度 | 当前版本（三段式） | YQ 方案（五段式） |
|---|---|---|
| **叙事策略** | "三类方法都 sidestep 问题" → 直接引出 StructSynth | 传统方法有 partial 优势 → LLM 补充语义先验但隐式编码 → graph-aware LLM 更进一步但未作 generation plan → 引出 StructSynth |
| **Novelty 定位** | Decouple discovery & synthesis（偏 pipeline 拼接感） | 把 dependency graph 当作 **prompt-level generation plan**（定位更精准） |
| **对 related work 态度** | 偏 aggressive（"sidestep, collapse, bypass"） | 更公允（"partial but important", "validate the importance"） |
| **方法命名** | Dependency Structure Discovery + Structure-Guided Synthesis（宽泛） | Evidence-Grounded Graph Induction + Graph-Planned Conditional Synthesis（更具辨识度） |

---

## 二、逐段分析

### P1：问题定位

#### 当前版本内容（L13-16）
```latex
Tabular data underpins high-stakes applications in healthcare, finance, and education,
valued for the dependency relationships it encodes among features---these inter-feature
dependencies are what enable ML models to learn meaningful decision boundaries.
In many such domains, data scarcity poses a fundamental challenge, and synthetic data
generation has emerged as a primary remedy.
Yet effective synthesis must go beyond augmenting volume: it must preserve the dependency
relationships inherent in the original data, since downstream models rely on these
relationships for generalization.
When available samples are severely limited, however, the very dependencies that
synthesis must preserve become difficult to discover reliably.
```

#### 存在的问题
1. **措辞过强**："must preserve the dependency relationships inherent" 和 "the very dependencies that synthesis must preserve become difficult to discover reliably" 过于绝对，暗示其他方法完全无法保持依赖，容易被 reviewer 挑战
2. **问题定义不够本质**：当前版本是"铺垫 → 引出困难"的渐进写法，但没有直接定义这个问题的本质是什么
3. **volume vs. dependency 的区分不够清晰**：只用了 "go beyond augmenting volume" 一句带过，没有充分阐明

#### YQ 的解决思路
- 开门见山定义：**"Low-data tabular synthesis is fundamentally a dependency-preservation problem"**
- 补充一句核心判断：**"Effective synthetic instances are useful only when they preserve the task-relevant relationships among attributes, not merely when they increase sample size"**
- 语气从"其他方法做不到"转为"这个问题的本质是什么"

#### 对 YQ 原文的修正
YQ 的 "fundamentally is a dependency-preservation problem" 同样过于绝对——表格合成在低数据下面临多维挑战（边际分布保真、隐私、混合类型、类别不平衡等），dependency preservation 是其中最关键但非唯一的问题。需要保留 YQ 的定义式开篇风格，但避免排他性表述。

此外，"most under-addressed" 也不准确——大量方法（BN、DECAF、GOGGLE、GraDe 等）都在处理依赖关系，不能说"没人做"。更准确的定位是：**在低数据场景下，依赖保持是最容易被破坏的**，因为依赖发现需要统计信号，而低数据下统计信号不可靠。

#### 改进方向
- 保留定义式开篇风格，但将核心表述从"没人做"改为"低数据下特别脆弱"：
  > "Low-data tabular synthesis poses several intertwined challenges; among them, **preserving inter-feature dependencies** is particularly fragile under sample scarcity — without faithful dependencies, additional samples add volume without predictive signal."
- "particularly fragile under scarcity" 比 "most under-addressed" 更准确：承认很多方法在做，但强调低数据下特别难做好
- 弱化 "must preserve" / "become difficult to discover reliably" 等绝对措辞
- 明确区分 volume augmentation 与 dependency preservation 的价值差异
- 保留 healthcare/finance/education 应用场景作为背景，但更简洁

---

### P2：传统方法（Deep Generative + Structure-Aware）

#### 当前版本内容（L18-23）
```latex
As illustrated in Figure 1, existing generative approaches each sidestep, rather than
solve, this dependency discovery challenge.
Deep generative models merge structure discovery and generation into a single end-to-end
process, so that both collapse simultaneously when training samples are scarce.
Structure-aware methods isolate graph learning as a prerequisite, yet rely on purely
statistical algorithms whose outputs become unreliable under scarcity.
Large Language Models bypass explicit structure altogether, encoding inter-feature
dependencies only implicitly through linearized text.
In short, these approaches either couple structure discovery with generation or bypass
structure discovery entirely.
```

#### 存在的问题
1. **三类方法并列过于 aggressive**：用 "sidestep" 统摄三类，暗示所有现有工作都是在回避问题，审稿人可能觉得 unfair
2. **没有承认传统方法的价值**：当前版本只指出缺陷，没有指出每类方法的贡献和优势，缺乏学术公允性
3. **DGM / Structure-Aware / LLM 混在一起**：三类方法的性质差异很大（非 LLM vs. LLM），放在同一段讨论层次不清
4. **没有为后面引出 LLM 做铺垫**：直接并列导致无法自然过渡到 "LLM 提供了什么新的可能性"

#### YQ 的解决思路
- **拆分为独立段落**，先单独讨论非 LLM 的传统方法
- 核心表述："Conventional tabular generators offer **two important but partial** ways of handling dependencies"
  - Deep generative models：通过分布拟合隐式学习依赖，**但需要足够数据**
  - Structure-aware methods：通过图模型显式建模依赖，**但依赖图的质量**
- 关键：**不是要"打死"传统方法**，而是指出它们各有半个解决方案，为 LLM 的引入做铺垫

#### 改进方向
- 将传统方法（DGM + Structure-Aware）单独成段，与 LLM 方法分离
- 承认每类方法的价值和贡献（"important but partial"），语气公允
- 指出两类方法的互补性：一个学隐式依赖但需要数据量，一个用显式结构但需要图质量
- 这种"各有 partial 优势"的写法为后面引出 LLM 的 "complementary advantage" 做了自然铺垫

---

### P3：LLM 方法的优势与局限

#### 当前版本内容
当前版本中 LLM 只有一句：
```latex
Large Language Models (LLMs) bypass explicit structure altogether, encoding inter-feature
dependencies only implicitly through linearized text rather than exploiting the graphical
nature of tabular data.
```

#### 存在的问题
1. **篇幅严重不足**：LLM 作为本文的核心技术载体，在 intro 中只有一句话描述，与其重要性不匹配
2. **只讲缺点不讲优势**：没有说明 LLM 带来了什么新能力（语义先验），直接说 "bypass explicit structure"
3. **flat textualization 的问题没展开**：只说了 "implicitly through linearized text"，但没有阐明这种隐式编码具体丢失了什么、为什么不够好
4. **缺乏与前一段的逻辑连接**：LLM 应该是对传统方法局限性的一种回应，但当前版本没有建立这种关系

#### YQ 的解决思路
- LLM 方法独立成段，先讲优势再讲局限
- 优势："LLM-based synthesizers provide a **complementary advantage**: they can exploit attribute names, descriptions, and in-context examples as **semantic priors**"
- 局限：most LLM methods 通过 "flat textualization of attribute-value assignments" 编码依赖 → 主要论述这种 **implicit dependency 编码的问题**

#### 改进方向
- LLM 方法单独成段，与传统方法分离
- 先承认 LLM 的语义先验优势（attribute names, descriptions, in-context examples）
- 再具体论述 flat textualization 的问题：将结构化的多维依赖关系压平为线性文本序列，丢失了显式的条件独立性/依赖方向信息
- 与 P2 形成逻辑递进：传统方法有 partial 优势 → LLM 提供了 complementary advantage → 但 LLM 自身也有局限

---

### P4：Graph-Aware 生成方法（当前版本缺失，YQ 建议新增）

#### 当前版本内容
**无。** 当前版本从 "三类方法都不行" 直接跳到 StructSynth 的 decoupling 动机，中间缺少对 graph-aware methods 的讨论。

#### 存在的问题
1. **Novelty 定位不精准**：不讨论 graph-aware 生成方法（如 GraDe、SPADA），读者无法理解 StructSynth 相比这些方法的独特之处
2. **跳跃过大**：从"LLM 隐式编码依赖有问题"直接跳到"我们 decouple"，中间缺少"已经有人尝试显式化依赖，但方式不同"的过渡
3. **容易被审稿人质疑**：如果不在 intro 中明确区分与 GraDe/SPADA 的差异，审稿人可能认为 StructSynth 只是又一个 graph-aware method

#### YQ 的解决思路
这是 **YQ 方案中最关键的新增段落**，逻辑链如下：

1. **引出**：A natural response is to make dependencies explicit; however, the key challenge lies in **what role the dependency plays in generation**
2. **点名/泛称**相关方法：
   - GraDe 将依赖融入 attention mechanism
   - SPADA 通过 conditional normalizing flow 实现高效采样
   - 也可以泛称 "recent graph-aware methods"（不点名）
   - 补充：这些方法未针对 low-data 场景设计
3. **关键转折**："These designs validate the importance of sparse dependency structure, but they **do not treat the graph as a generation plan** that organizes the LLM's own generation process"
4. **提出 Research Question**：*"Can a dependency graph determine the generation order, conditioning context, and scope of each black-box LLM call?"*

#### 对 YQ 原文的修正：SPADA 分类问题
YQ 将 SPADA 与 GraDe 并列为 "graph-aware LLM 方法"，但 SPADA **不使用 LLM 做生成**——它用 dependency graph 指导 normalizing flow / KDE 等统计模型采样（见 related work: "replacing LLM-based generation with lightweight statistical estimators"）。因此 P4 的段落标题不能叫 "graph-aware LLM methods"，应改为 **"graph-aware generation methods"**，这样可以同时涵盖：

| 方法 | 用图 | 生成器 | 图的角色 |
|---|---|---|---|
| GraDe | 是 | LLM（fine-tune） | attention mask（模型内部机制） |
| SPADA | 是 | 统计模型（flow/KDE） | 条件分布拟合的结构指引 |
| StructSynth | 是 | LLM（black-box prompt） | generation plan（决定 prompt 构建和调用调度） |

核心论点不变：这些方法验证了图的价值，但没有把图当作 generation plan。

#### 对 "prompt-level plan" 措辞的精确化
DAG 本身并不出现在 prompt 文本里，而是决定了 prompt 如何被构建和调度。在首次使用时需要澄清：
> "the graph serves as a generation plan that determines how prompts are constructed and sequenced"

避免审稿人误以为 DAG 被序列化塞进了 prompt text。后续使用 "generation plan" 即可（不必每次都带 "prompt-level"）。

#### 改进方向
- 新增完整段落，讨论 **graph-aware generation methods**（非仅 LLM methods）
- 承认这些方法验证了稀疏依赖结构的重要性（公允评价）
- 精准区分 StructSynth 的 novelty：**不是第一个用图的，而是第一个把图当作 generation plan 来组织 LLM 调用的**
  - GraDe：图 → attention mask（模型内部机制）
  - SPADA：图 → flow/KDE 拟合指引（统计模型，非 LLM）
  - StructSynth：图 → generation order + conditioning context + LLM call scope（组织 prompt 构建和调用调度）
- 用 research question 的形式明确引出核心贡献点，增强叙事张力
- 注明这些方法未针对 low-data 场景设计（GraDe 需 fine-tuning，SPADA 需足够数据拟合条件分布）

---

### P5：方法介绍 + 贡献

#### 当前版本内容（L25-34）

```latex
Decoupling yields two key advantages: ...
These requirements lead directly to StructSynth, a two-stage framework...
In the Dependency Structure Discovery stage, ...
In the Structure-Guided Synthesis stage, ...
Our contributions are:
- We identify dependency structure discovery as the primary bottleneck...
- We propose StructSynth, a discover-then-synthesize framework...
- Extensive experiments across six datasets...
```

#### 存在的问题

1. **阶段命名过于宽泛**："Dependency Structure Discovery" 和 "Structure-Guided Synthesis" 听起来像通用术语，缺乏辨识度
2. **Novelty 定位偏 pipeline 拼接**：当前强调 "decouple discovery and synthesis"，给人感觉只是把两个已有步骤分开做（A+B 问题）。"Decouple" 这个词本身暗示"拆开两步"，审稿人立刻联想到 pipeline 拼接，核心 intellectual contribution 被架构描述淹没
3. **没有回应 P4 的 research question**：当前版本缺少 P4，所以方法引出也缺少对应的 hook

#### YQ 的解决思路

- 方法引出要回应 P4 的 research question："We answer this question by instantiating StructSynth, a framework that **treats a dependency graph as a generation plan** for black-box LLM synthesis"
- 阶段重命名：
  - Stage 1：**Evidence-Grounded Graph Induction**（强调 LLM + 统计证据融合）
  - Stage 2：**Graph-Planned Conditional Synthesis**（强调图作为 plan 的独特性）

#### Decouple 的角色重新定位

"Decouple" 不作为 novelty claim（避免 A+B 感），而是作为 **design rationale**：

- **核心 novelty = graph as generation plan**（单一统一概念）→ 出现在贡献列表中
- **Decouple = 实现这一概念的合理架构选择** → 出现在方法描述中，作为解释而非贡献
- 叙事逻辑：要把图当 generation plan，需要先可靠地发现图 → 自然引出两阶段设计

具体表述方式：不说 "we decouple discovery and synthesis"，而说：

> To use a dependency graph as a generation plan, two requirements must be met: the graph must be reliably discovered from limited samples, and the graph must organize the LLM's generation process. Separating the two stages allows each to leverage complementary signals.

这样两阶段是核心概念的**必然推论**，而非两个独立技术的拼接。

#### 改进方向

- 用 "We answer this question by..." 回应 P4 的 research question，形成完整的问题-回答闭环
- 采用新命名：Evidence-Grounded Graph Induction + Graph-Planned Conditional Synthesis
- Novelty 叙事以 "graph as generation plan" 为核心，decouple 降级为 design rationale
- 贡献列表草案（基于新的 novelty 定位）：
  1. **框架贡献**：We propose to treat a dependency graph as a generation plan that determines the generation order, conditioning context, and scope of each LLM call for tabular synthesis. We instantiate this idea in StructSynth, where (a) Evidence-Grounded Graph Induction fuses LLM semantic priors with statistical association cues to discover reliable structures from limited samples, and (b) Graph-Planned Conditional Synthesis enforces the discovered topology as an executable blueprint for layer-wise generation.
  2. **实验贡献**：Experiments across six datasets demonstrate state-of-the-art downstream utility and privacy preservation while maintaining competitive statistical fidelity. Ablations confirm that both stages contribute independently, validating the generation-plan design.
- 贡献措辞继续保持对实验结果的准确表述（避免 overclaim，参见 R5.4-R5.8）

---

## 三、新旧结构对照

### 当前结构（三段式）

```
P1: 表格数据重要 → 依赖关系重要 → 低数据困难
P2: DGM/Structure-Aware/LLM 三类并列 → 都 sidestep → decouple 动机
P3: StructSynth 两阶段 + 3条贡献
```

### YQ 方案结构（五段式，含修正）

```
P1: 低数据合成中依赖保持 particularly fragile（定义式开篇，非排他性）
P2: 传统方法各有 partial 优势（DGM: 隐式+需数据, Structure-Aware: 显式+需图质量）
P3: LLM 提供语义先验优势，但 flat textualization 不显式编码依赖结构
P4: Graph-aware 生成方法（含非 LLM）显式化依赖但未当 generation plan → RQ
P5: StructSynth 回应 RQ，graph as generation plan + 两阶段是其自然推论 + 贡献
```

---

## 四、关键改写要点清单

| # | 改写要点 | 优先级 | 说明 |
|---|---|---|---|
| 1 | P1 改为定义式开篇 | 高 | "particularly fragile under scarcity"（非 "fundamentally is" 或 "most under-addressed"） |
| 2 | 拆分传统方法与 LLM 方法 | 高 | 当前混在一段，YQ 要求分为 P2（传统）+ P3（LLM） |
| 3 | 新增 P4：graph-aware **生成方法**段 | 高 | 涵盖 GraDe（LLM fine-tune）和 SPADA（统计模型），注意 SPADA 不是 LLM 方法 |
| 4 | Novelty = "graph as generation plan"；decouple 降级为 design rationale | 高 | 避免 A+B pipeline 拼接感，两阶段是核心概念的自然推论 |
| 5 | 阶段重命名 | 中 | Evidence-Grounded Graph Induction + Graph-Planned Conditional Synthesis |
| 6 | 弱化 aggressive 措辞 | 中 | "sidestep/collapse/bypass" → "partial/important but..." |
| 7 | 展开 flat textualization 的问题 | 中 | 用 "does not explicitly encode" 而非 "loses"，承认 LLM 可能隐式捕获部分依赖 |
| 8 | 添加 Research Question | 中 | "Can a dependency graph determine the generation order..." |
| 9 | 贡献列表调整 | 中 | 2 条：框架贡献（graph as generation plan）+ 实验贡献 |
| 10 | Figure 1 caption 改写（方案 A：只改 caption，不改图） | 中 | 图的三 panel 结构保持不变；caption 对齐新叙事，补充 graph-aware 方法的文字桥接（见下方 caption 草案） |
| 11 | "generation plan" 首次使用时澄清 | 中 | 图不是 prompt 文本的一部分，而是决定 prompt 如何构建和调度 |

---

## 五、页面篇幅预估

YQ 方案从三段扩展为五段，但每段可以写得很紧凑：

| 段落 | 预估行数 | 说明 |
|---|---|---|
| P1 | 4-5 行 | 定义式开篇 + volume vs. dependency 区分 |
| P2 | 4-5 行 | 两类传统方法各 2 句 |
| P3 | 5-6 行 | LLM 优势 + flat textualization 问题（需展开，比原估偏紧） |
| P4 | 7-9 行 | Graph-aware 生成方法（GraDe+SPADA）+ 转折 + RQ（全新段落，内容较多） |
| P5 | 12-15 行 | 方法概述 + generation plan 澄清 + 2 条贡献 |
| **合计** | **32-40 行** | 约 1.3-1.6 页（不含 Figure 1） |

相比当前版本（~30行正文），YQ 方案总行数略多，但信息密度更高、叙事层次更清晰。如果超出页面限制，优先压缩 P1 和 P2（这两段可以非常紧凑）。

---

## 六、Figure 1 Caption 改写（方案 A：只改 caption，不改图）

图的三 panel 结构（Conventional Methods / LLMs / StructSynth）保持不变，只改写 caption 文字对齐新叙事。

### 当前 caption

> **Tabular synthesis paradigms under data scarcity.** Existing approaches handle dependencies implicitly, from pre-learned graphs, or through serialized text. StructSynth explicitly discovers an executable dependency topology and uses it as a generation blueprint.

### 存在的问题

1. 三分法（implicitly / pre-learned graphs / serialized text）对应旧 intro 的三类并列，与新五段叙事的分类维度不匹配
2. 没有提及 graph-aware 生成方法（GraDe/SPADA）——新 intro P4 的核心论证对象在图中完全不可见
3. "executable dependency topology" 和 "generation blueprint" 接近新叙事的 "generation plan"，但没有点明与 graph-aware 方法的区别（attention mask / flow guidance vs. generation plan）

### Caption 草案

> **Tabular synthesis paradigms under data scarcity.** Conventional methods learn dependencies implicitly via distribution fitting or from pre-learned graphs; LLM-based methods encode them through serialized text. Recent graph-aware approaches (not shown) incorporate dependency structure as attention masks or distribution priors, but do not use it to organize the generation process. StructSynth discovers a dependency graph and treats it as a generation plan that determines the order, conditioning context, and scope of each LLM call.

### 草案要点

- 前两句对应图中的两个已有 panel（Conventional / LLM）
- 第三句用括号 "(not shown)" 桥接 P4 的 graph-aware 方法，解释为什么图中没有它们的 panel
- 最后一句定位 StructSynth 的 novelty = generation plan，并具体化为 order + conditioning context + scope

---

## 七、事实核查 Rubrics（改进版写完后逐条核查）

以下 rubrics 用于在改进版本写完后逐条核查，确保每个段落的事实性声明都有论文内容或文献支撑。每条标注核查来源和判定标准。

### R0：全局核查项

| # | 核查项 | 判定标准 | 核查来源 |
|---|---|---|---|
| R0.1 | 无排他性措辞 | 不出现 "the only"、"no existing method"、"fundamentally is" 等将 dependency preservation 定义为唯一问题的表述 | 全文检索 |
| R0.2 | 无未定义缩写 | 首次出现的缩写必须有全称（DAG、LLM、BFS 等） | 全文检索 |
| R0.3 | 引用完整性 | 每个 `\cite{}` 的 key 在 `references.bib` 中存在 | `references.bib` |
| R0.4 | 阶段命名一致性 | 如果 intro 采用新命名（Evidence-Grounded Graph Induction / Graph-Planned Conditional Synthesis），检查 method section 和 Figure caption 是否同步更新，或有意保留旧名 | `method.tex`, `introduction.tex` Figure 1 caption |

### R1：P1（问题定位）核查

| # | 声明 | 判定标准 | 核查来源 |
|---|---|---|---|
| R1.1 | "preserving inter-feature dependencies is particularly fragile under scarcity" | 不出现 "fundamentally is"、"most under-addressed"、"the only" 等排他性表述；"particularly fragile" 表达低数据下特别难做好，而非没人做 | 措辞检查 |
| R1.2 | 表格数据在 healthcare/finance/education 的重要性 | 需有对应引用支撑 | 当前版本引用 `choi2017generating`(healthcare), `rundo2019machine`(finance), `luan2021review`(education)，均在 bib 中 |
| R1.3 | 依赖关系使 ML 模型学到有意义的决策边界 | 需有引用支撑 | 当前版本引用 `fonseca2023tabular`，在 bib 中 |
| R1.4 | 合成数据是应对数据稀缺的主要手段 | 需有引用支撑 | 当前版本引用 `borisov2022deep`，在 bib 中 |
| R1.5 | "without faithful dependencies, additional samples add volume without predictive signal" | 本文实验是否支撑？ | **支撑**：ablation 中 No Structure 变体（=CLLM，不用依赖图）AUC 83.95 vs. StructSynth 85.55（Table 5）；且 Bayesian Sampler 有最好 fidelity 但最差 AUC，说明 pairwise correlation 不等于有效依赖 |

### R2：P2（传统方法）核查

| # | 声明 | 判定标准 | 核查来源 |
|---|---|---|---|
| R2.1 | DGMs "通过分布拟合隐式学习依赖" | 需准确描述 DGM 的工作方式 | Related work (L12): "capture the joint distribution end-to-end" — 准确 |
| R2.2 | DGMs 在低数据下性能受限 | 需有实验或文献支撑，且措辞须留余地 | Related work (L12): "data-hungry"；DDPM AUC 63.68，NFlow 61.88 支撑此说。但 **TabSyn AUC 69.64（rank 4.00）是反例**——不能说"所有 DGM 都不行"。建议措辞："performance varies across architectures, with many requiring substantially more samples to converge reliably" |
| R2.3 | Structure-aware methods "通过图模型显式建模依赖" | 需准确描述 | Related work (L13): "incorporating explicit dependency graphs; Bayesian-network-based generators and graph-based VAEs" — 准确 |
| R2.4 | Structure-aware methods "依赖图质量" / "图在稀缺数据下不可靠" | 需有实验或文献支撑 | 引用 `chai2022data`（在 bib 中）；SHD 实验（Figure 3）显示传统方法在低样本下 SHD 显著高于 StructSynth；GOGGLE 在 Table 1 AUC 仅 67.98 |
| R2.5 | 用 "important but partial" 而非 "sidestep" | 措辞检查：不出现 "sidestep"、"fail"、"collapse" 等 aggressive 用词来统摄传统方法 | 措辞检查 |

### R3：P3（LLM 方法）核查

| # | 声明 | 判定标准 | 核查来源 |
|---|---|---|---|
| R3.1 | LLM 能利用 attribute names、descriptions、in-context examples 作为语义先验 | 需准确描述 LLM tabular synthesis 的工作方式 | Related work (L17-18): GReaT "serialize rows as text"；CLLM "selects curated in-context examples" — 准确 |
| R3.2 | "complementary advantage" 的定位 | LLM 的优势应与 P2 中传统方法的局限互补 | 逻辑检查：传统方法在低数据下失效（数据不够 / 图不可靠） → LLM 用语义先验补偿统计信号不足 — 逻辑成立 |
| R3.3 | "flat textualization" 是多数 LLM 方法的主流做法 | 需有文献支撑 | GReaT: serialize rows as text（`borisov2023language`）；CLLM: linearized attribute-value pairs（`cllm2024`）；`liu2024rethinking` 讨论了 LLM 不利用 tabular 结构性 — 均在 bib 中 |
| R3.4 | flat textualization "丢失了显式依赖方向 / 条件独立性信息" | 是否过强？ | 需谨慎措辞：flat text 确实不编码显式的条件依赖方向，但 LLM 可能通过 attention 隐式捕获部分依赖。建议用 "does not explicitly encode" 而非 "loses" |
| R3.5 | 对 LLM 方法不能只讲缺点 | 措辞检查：必须先承认优势再讲局限 | 措辞检查 |

### R4：P4（Graph-Aware 生成方法）核查

| # | 声明 | 判定标准 | 核查来源 |
|---|---|---|---|
| R4.1 | GraDe "将依赖图融入 attention mechanism" | 需准确描述 GraDe 的实际做法 | Related work (L19): "injecting a learned sparse dependency graph into the Transformer attention mechanism, but the graph serves as an attention mask" — 准确；`zhang-etal-2025-features` 在 bib 中 |
| R4.2 | SPADA "通过 conditional normalizing flow 实现采样" | 需准确描述 SPADA 的实际做法 | Related work (L20): "replacing LLM-based generation with lightweight statistical estimators (KDE, normalizing flows)" — 准确；`yang2025doubling` 在 bib 中 |
| R4.3 | "这些方法未针对 low-data 场景设计" | 措辞用 "未针对...设计" 而非 "没有考虑"——它们不是不知道低数据问题，而是设计上不适合 | Related work: GraDe "requires model fine-tuning"（fine-tuning 在低数据下受限）；SPADA "relying on sufficient data to fit reliable conditional distributions" — 支撑成立 |
| R4.4 | "validate the importance of sparse dependency structure, but do not treat the graph as a generation plan" | GraDe/SPADA 是否确实未用图作 generation plan？ | GraDe 用图作 attention mask（模型内部机制）— 准确；SPADA 用图指导 flow 拟合（统计模型，非 LLM）— 准确。注意：不再使用 "prompt-level plan" 统称，首次使用需澄清"图决定 prompt 如何构建和调度" |
| R4.5 | Research Question 的合理性 | "Can a dependency graph determine the generation order, conditioning context, and scope of each black-box LLM call?" — 本文方法是否确实做到了这三点？ | **generation order**: topological layering（method 3.2.1）✓；**conditioning context**: parent conditioning（method 3.2.1, Eq.4）✓；**scope of each LLM call**: 按 layer 分次调用 LLM，每次只生成一层的 attributes（method 3.2.1）✓ |
| R4.6 | 不对 GraDe/SPADA 使用贬义措辞 | 措辞检查：应用 "validate importance" 等公允表述 | 措辞检查 |
| R4.7 | SPADA 不被归类为 LLM 方法 | 段落标题和行文中用 "graph-aware generation methods"（非 "graph-aware LLM methods"）；SPADA 的描述明确提及它用统计模型而非 LLM 生成 | 措辞检查 |
| R4.8 | "generation plan" 首次使用时有澄清 | 需明确图不是 prompt 文本的一部分，而是决定 prompt 如何构建和调度（generation order + conditioning context + scope of each LLM call） | 措辞检查 |

### R5：P5（方法介绍 + 贡献）核查

| # | 声明 | 判定标准 | 核查来源 |
|---|---|---|---|
| R5.1 | "Evidence-Grounded Graph Induction" 命名准确性 | 方法是否确实融合了 evidence（LLM reasoning + statistical association）来归纳图？ | Method 3.1: LLM-guided BFS + association scores $\mathcal{S}(A_i)$（Eq.2）+ cycle resolution — "evidence-grounded" 成立 |
| R5.2 | "Graph-Planned Conditional Synthesis" 命名准确性 | 方法是否确实用图来"规划"条件生成？ | Method 3.2: topological layering → layer-wise conditional generation（Eq.4）→ 图决定生成顺序和条件 — "graph-planned" 成立 |
| R5.3 | DAG 脚注：声明不做因果宣称 | 必须保留 "dependency graph, not causal claim" 的脚注 | 当前版本已有脚注，检查是否在新版保留 |
| R5.4 | 贡献 - downstream utility SOTA | 是否所有 6 个数据集都 best？ | Table 1: StructSynth 6/6 datasets best, avg rank 1.00 — **准确** |
| R5.5 | 贡献 - privacy preservation | 是否可以声称 best？ | Table 2 (privacy): avg rank 1.50, 但 CLLM avg rank 3.50 也较好；StructSynth 在 4/6 datasets best — 可以说 "state-of-the-art" 但不能说 "best on all" |
| R5.6 | 贡献 - statistical fidelity | 是否 competitive？ | Table 2 (fidelity): avg rank 7.92, 不是最好（NFlow 5.00, GReaT 3.67）— 只能说 "competitive"，不能说 "strong" 或 "best" |
| R5.7 | 贡献 - "each stage contributes independently" | ablation 是否支撑？ | Table 5: No Structure (−1.6 AUC), No Topological Order (−1.1), PC/NoTears Discovery (−1.0~1.4), Bayesian Sampler (−4.4) — 两个阶段的变体都导致下降，**支撑成立** |
| R5.8 | 避免 overclaim | 不出现 "best privacy-fidelity trade-off"、"guarantees strict adherence" 等 | 措辞检查 |

### R-cross：跨段逻辑一致性核查

| # | 核查项 | 判定标准 |
|---|---|---|
| RC.1 | P1→P2 逻辑衔接 | P1 提出 dependency preservation 是核心挑战 → P2 讨论传统方法如何处理依赖（但各有局限）。P2 不能引入 P1 未提及的新问题维度 |
| RC.2 | P2→P3 逻辑衔接 | P2 指出传统方法各有 partial 优势 → P3 引出 LLM 作为 "complementary advantage"。P3 的优势描述应与 P2 的局限互补 |
| RC.3 | P3→P4 逻辑衔接 | P3 指出 LLM 的 flat textualization 问题 → P4 讨论 "显式化依赖" 的已有尝试。P4 不能重复 P3 已说的内容 |
| RC.4 | P4→P5 逻辑衔接 | P4 提出 RQ → P5 必须以 "We answer this question by..." 或等价形式回应。RQ 中提到的三个方面（generation order, conditioning context, scope）必须在 P5 中有对应 |
| RC.5 | Novelty 与 decouple 的角色区分 | 核心 novelty = "graph as generation plan"（出现在贡献列表中）；decouple = design rationale（出现在方法描述中，作为"为什么分两阶段"的解释，不作为独立贡献）。检查：贡献列表中不出现 "decouple" 作为核心卖点；方法描述中可以提 "separating the two stages allows..."，但定位为设计选择而非 novelty |
| RC.6 | 对 related work 态度一致性 | 5 段中对同一方法的评价不矛盾（如 P2 说传统方法 "important but partial"，P5 贡献中不能反过来说 "existing methods fail"） |

---

## 八、实施顺序

1. 重写 P1：定义式开篇，"particularly fragile under scarcity"
2. 重写 P2：传统方法的 partial 优势（从当前 P2 拆分；注意 DGM 措辞留余地，TabSyn 是反例）
3. 重写 P3：LLM 的语义先验优势 + flat textualization 局限（"does not explicitly encode"，非 "loses"）
4. 新写 P4：graph-aware **生成方法**（注意 SPADA 非 LLM）+ research question
5. 重写 P5：回应 RQ，graph as generation plan 为核心 novelty，decouple 为 design rationale，新命名 + 2 条贡献
6. 同步更新 Figure 1 caption：对齐新的 novelty 定位和分类维度
7. 检查 Related Work：对 GraDe/SPADA/CLLM 的描述口径是否与 intro 新叙事一致
8. 检查 Method section：阶段命名是否需要同步更新为新命名
9. 按 Rubrics 逐条核查
