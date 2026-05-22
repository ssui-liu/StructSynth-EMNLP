我看完当前 25 页版本后，整体判断是：**主线已经明显比之前成熟，尤其 generation plan 的叙事已经进到摘要、introduction 和 method 里了；但还没有完全 submit-ready。** 现在主要问题不是大逻辑，而是若干 **术语不一致、claim 过强、表格数值疑似错误、figure 内部旧标签未同步、appendix 与主文叙事冲突**。这些问题如果不修，会给 reviewer 很多“抓小辫子”的机会。

下面按优先级整理。

---

## 0. 最优先：标题还没改

当前 PDF 标题仍然是旧版：

> StructSynth: Dependency Structure Discovery for High-Fidelity Tabular Data Synthesis in Low-Data Regimes

但正文和摘要已经在往 “dependency graph as generation plan” 方向改。摘要里已经写了 graph determines generation order, conditioning context, and scope of each black-box LLM call，也引入了 **Evidence-Grounded Graph Induction** 和 **Graph-Planned Conditional Synthesis**。

建议最终标题直接改为：

> **StructSynth: Dependency Graphs as Generation Plans for Low-Data Tabular Synthesis with Language Models**

这个标题和当前摘要、introduction 第四段、method opening 的叙事是一致的。否则 reviewer 会觉得标题还停留在 “structure discovery paper”，但正文实际在卖 “graph-planned LLM synthesis”。

---

## 1. Main text 里最需要统一的术语

现在全篇同时出现了几套表述：

* **generation plan**
* **executable blueprint**
* **structural blueprint**
* **Structure-Guided Synthesis**
* **Graph-Planned Conditional Synthesis**
* **dependency adherence by construction**
* **dependency-faithful synthesis**

这些词有些可以保留，但不能混用得太随意。当前摘要和 method 中仍然有 “executable blueprint / enforce dependency adherence by construction” 这类偏强表述。

我建议统一成下面这套：

* 主概念：**dependency graph as a generation plan**
* 第一阶段：**Evidence-Grounded Graph Induction**
* 第二阶段：**Graph-Planned Conditional Synthesis**
* graph 的作用：**defines / specifies / determines an explicit conditioning schedule**
* 避免：**guarantee**, **true parents**, **causal path**, **executable blueprint** 频繁出现

具体替换建议：

> “serves as an executable blueprint”
> 改成
> **“is compiled into a generation plan”**

> “enforce dependency adherence by construction”
> 改成
> **“makes the planned conditioning structure explicit throughout generation”**

> “guarantees each feature is conditioned on its true parent nodes”
> 改成
> **“ensures that each feature is generated according to the parent set specified by the induced graph”**

这个修改很重要，因为你们已经在 footnote 里声明 DAG 不是 ground-truth causal claim。 如果后文又说 “true parents / guarantees / causal path”，会自相矛盾。

---

## 2. Abstract：整体方向对，但 claim 需要降一档

当前 abstract 的逻辑是好的：先讲低数据下 dependency fragile，再讲 existing methods，然后引出 graph as generation plan。问题主要有两个。

第一，句子：

> “none treats the graph as a generation plan that organizes the LLM’s generation process”

基本可以保留，但最好把 SPADA 的区别说得更精准。因为 SPADA 确实用 graph traversal 和 parent conditioning，只是没有让 LLM 自己作为每一步的 conditional generator。建议改成：

> **Recent graph-aware methods use dependency graphs as attention biases or as backbones for non-LLM samplers, but they do not use the graph as a prompt-level plan for organizing the LLM’s own generation process.**

这比 “attention masks or distribution priors” 更准确，也更自然地区分 GraDe / SPADA。

第二，abstract 里的：

> “to enforce dependency adherence by construction”

建议改。当前你们没有证明 LLM 一定遵守依赖，也没有在 main text 中显式写 parser / validator / regeneration loop。因此 “enforce by construction” 容易被认为过强。建议改成：

> **“making the conditioning structure explicit and verifiable throughout synthesis.”**

或者更短：

> **“making dependency conditioning explicit throughout synthesis.”**

---

## 3. Introduction：逻辑已经基本成立，但第 3–4 段还要微调

### 3.1 第一段：仍然有一点旧版强 claim

当前第一段仍然写：

> “preserving inter-feature dependencies is particularly fragile under sample scarcity”
> “Without faithful dependencies, additional synthetic samples add volume without adding predictive signal”

这个方向没问题，但 “without faithful dependencies” 稍强。建议改成更稳的 problem framing：

> **Low-data tabular synthesis is fundamentally a dependency-preservation problem: synthetic instances are useful only when they preserve task-relevant relationships among attributes, rather than merely increasing sample size.**

这样既保留核心观点，又避免承诺保留所有 dependencies。

---

### 3.2 第二段：conventional methods 写得比之前好，但可以更平衡

当前第二段把 existing methods 分成 deep generative models、structure-aware methods、LLM methods 三类，逻辑是好的。 但建议稍微弱化：

> “many requiring substantially more samples to converge reliably”

这句话可以保留，但如果 reviewer 熟悉 TabSyn / CTGAN 等方法，可能会认为表述略泛。可以改成：

> **“their reliability depends heavily on having enough samples to estimate the joint distribution.”**

同时，“Structure-aware methods make dependencies explicit through graphical models…” 这句很好，建议保留。

---

### 3.3 第四段：GraDe / SPADA 的 role taxonomy 还需要更精准

当前 introduction 写：

> GraDe injects graph into Transformer attention mask, while SPADA uses the graph to guide normalizing flows. However, neither treats the graph as a generation plan... both use it as an internal prior rather than determining what to generate, in what order, and with which context—and both require model fine-tuning or sufficient samples.

这里有两个问题。

**第一，“both use it as an internal prior” 对 SPADA 不准确。** SPADA 更像是把 graph 作为 **external sampler backbone**，不是 internal prior。

**第二，“both require model fine-tuning or sufficient samples” 把两个方法的限制揉在一起了。** GraDe 更接近 fine-tuning / attention modification；SPADA 更接近依赖 KDE / normalizing flow 的条件分布拟合。建议拆开但不要展开太多。

推荐替换成：

> **Recent graph-aware methods take important steps toward explicit dependency modeling. Some use dependency graphs as internal modeling biases, such as attention modulation, while others use LLM-induced graphs as backbones for efficient non-LLM samplers. These designs validate the importance of sparse dependency structure, but they do not treat the graph as a prompt-level plan that organizes the LLM’s own generation process. This leaves open a different interface: can a dependency graph determine the generation order, conditioning context, and scope of each black-box LLM call?**

这样不用在 intro 里长篇讨论 GraDe / SPADA，但 reviewer 能看出你们知道这两类 work 的区别。

---

### 3.4 第五段：当前 “Separating discovery from synthesis...” 有 A+B 风险

当前第五段说：

> “Separating discovery from synthesis allows each stage to leverage complementary signals...”

这句话逻辑没错，但容易把论文重新拉回 “decouple discovery and synthesis” 的旧叙事。建议强调 **graph-to-prompt compilation**：

> **We answer this question with StructSynth, a prompt-level framework that treats a dependency graph as a generation plan for black-box LLM synthesis. StructSynth contains two coupled stages: Evidence-Grounded Graph Induction and Graph-Planned Conditional Synthesis. The first stage induces a sparse acyclic graph from limited observations by combining LLM semantic priors with type-aware association evidence. The second stage compiles the induced graph into topological conditional prompts: topological layers determine when attributes are generated, parent sets determine the conditioning context, and local subgraphs determine the scope of each prompt. Thus, StructSynth does not append a graph to a generic LLM prompt; it uses the graph to factorize LLM synthesis into graph-local conditional generation steps.**

这段比当前版本更能解释为什么不是简单 A+B。

---

## 4. Method section：notation 和 claim 需要重点修

### 4.1 Method opening 需要把 “plan” 定义得更形式化

当前 method 说 DAG naturally encodes generation order，topological sort yields the synthesis sequence，parents define conditioning set。 这很好，但还可以更 submit-ready。建议加入一句：

> **Given an induced graph (G), we compile it into a generation plan (\Pi_G=(\mathcal{L}, \mathrm{Pa}, \mathcal{G}*{\mathrm{local}})), where (\mathcal{L}) denotes topological layers, (\mathrm{Pa}) denotes parent conditioning sets, and (\mathcal{G}*{\mathrm{local}}) denotes the local subgraph included in each prompt.**

这会让 “generation plan” 不只是 metaphor，而是一个明确对象。

---

### 4.2 Source node 的表述仍然偏 causal

当前 3.1.1 写：

> “source nodes—attributes not influenced by any others”

建议改成：

> **“root attributes in the generation plan—attributes that are generated without conditioning on other attributes.”**

不要写 “not influenced by”，因为这会被理解成 causal influence。Appendix prompt 里也有类似问题，后面单独说。

---

### 4.3 (G_t=(V_t,E_t)) 没有显式定义

3.1.2 和 3.1.3 里使用了 (G_t)、(V_t)、(E_t)、(E_{\text{prop},t})、(V_{\text{new},t})，但主文没有在第一次出现时完整定义。当前 Eq. 3 直接写 (G_{t+1}=(V_t\cup V_{\text{new},t}, ...))。

建议在 3.1.2 开头加：

> **At iteration (t), let (G_t=(V_t,E_t)) be the current graph. The LLM proposals are parsed into a candidate edge set (E_{\mathrm{prop},t}) and a set of newly discovered attributes (V_{\mathrm{new},t}).**

这个是 notation 规范性问题，建议一定加。

---

### 4.4 Association score 的范围需要说清楚

当前 main text 写 (S(A_i)\in \mathbb{R}^{K-1})，并说使用 Cramér’s V 和 Pearson’s (r)。 Appendix prompt example 又写 association scores are “scaled 0 to 1”。这两者不完全一致，因为 Pearson’s (r\in[-1,1])。

建议明确：

> **We feed the LLM normalized association strengths (S(A_i)\in[0,1]^{K-1}), using (|r|) for continuous-continuous pairs and type-appropriate normalized association measures for other pairs.**

如果你们确实保留 Pearson 的 sign，也要说明 sign 是否进入 prompt。否则 reviewer 会问：LLM 看到的是 signed correlation 还是 dependency strength？

---

### 4.5 Graph-Planned Conditional Synthesis 的公式与文字有轻微不一致

当前文字说 each feature is conditioned on its parent nodes，但公式用的是 (\tilde{x}_{j,<i})，即所有 preceding layers。

这会产生一个小矛盾：

* 如果实际只条件在 parent values 上，公式应该写 (\tilde{x}_{j,\Gamma^-(L_i)})。
* 如果实际输入了所有 preceding generated values，那就不能说 “conditioned on its parents” 这么窄。

建议二选一。

更契合你们 claim 的写法是：

> [
> \tilde{x}_{j,L_i}
> =================
>
> f_{\mathrm{LLM}}\left(
> \pi_{\mathrm{data}}\left(
> \tilde{x}*{j,\Gamma^-(L_i)}, G_i, L_i, D^i*{\mathrm{few}}
> \right)
> \right).
> ]

这样 “parent-conditioned generation” 更干净。

如果 implementation 里确实给了 all previous values，那就把文字改成：

> **“conditioned on previously generated values, with the local subgraph specifying the parent dependencies to preserve.”**

---

### 4.6 (D_{\text{few_shot}}) 的大小和选择策略不够清楚

主文说使用 small subset (D_{\text{few_shot}}\subseteq D_{\text{train}})，但没有说明它是全部 100 个样本，还是从 100 个中抽取若干 few-shot examples。 实验部分说 (n=100)，生成 1000 synthetic samples。

建议明确一句：

> **Unless otherwise stated, (D_{\mathrm{few}}) is sampled uniformly from (D_{\mathrm{train}}) with size (m=\dots).**

或者：

> **In our experiments, (D_{\mathrm{few}}=D_{\mathrm{train}}) under the 100-shot setting.**

这是 reproducibility 必须项。

---

## 5. Results / tables：这里有几个 submit blocker

### 5.1 Table 2 的 BN statistical fidelity 行疑似复制错误

Table 2 里 BN 在 Statistical Fidelity 部分的数值看起来和 Table 1 的 downstream performance 数值完全一致，例如 Adult 82.68、Anxiety 82.77、Salary 46.33、Churn 88.85。这很像复制粘贴错误。Table 2 的正文讨论又依赖 fidelity / privacy trade-off，因此这个表必须核对。

这是 **submit blocker**。如果 reviewer 发现，会直接影响可信度。

---

### 5.2 Privacy metric 建议改成 Privacy Deviation 或明确 rank 计算方式

Table 2 中 Privacy Risk 的理想值是 0.5，但表格展示的是 raw privacy risk percentage。正文说 StructSynth has best privacy preservation，average rank 1.50。 这会让读者困惑：数值越低越好？越接近 50 越好？比如 44 和 56 到底谁更好？

建议二选一：

**方案 A：表格仍放 raw Privacy Risk，但 caption 写清楚：**

> **For Privacy Risk, ranks are computed by deviation from 0.5, i.e., (|\mathrm{PrivacyRisk}-0.5|); lower deviation indicates better privacy preservation.**

**方案 B：直接把表格改成 Privacy Deviation：**

> [
> \Delta_{\mathrm{privacy}}=|\mathrm{PrivacyRisk}-0.5|
> ]

然后 lower is better。这个最清楚。

---

### 5.3 Statistical Fidelity 这个名字容易误导

你们的 Statistical Fidelity 是 “pairwise difference / error”，lower is better。正文已经解释 lower is better，但表格标题叫 “Statistical Fidelity (%)”，容易让人直觉以为越高越好。

建议改名为：

> **Pairwise Fidelity Error**

或者至少：

> **Statistical Fidelity Error**

这样正文里也可以写：

> “StructSynth maintains competitive pairwise fidelity error.”

比 “competitive statistical fidelity” 更清楚。

---

### 5.4 Table 3 标题和数值要核对

Table 3 标题是：

> Ablation Study on Adult Datasets

应改为：

> **Ablation Study on the Adult Dataset**

另外 Table 3 中 StructSynth fidelity 是 57.96，而 Table 2 Adult statistical fidelity 中 StructSynth 是 57.60。两者是否来自不同实验设置？如果不是，应统一。Ablation 部分当前用 Table 3 来支持两阶段贡献。

---

### 5.5 “No-Correlation Score” 建议改成 “No-Association Scores”

因为你们不仅用了 Pearson correlation，还用了 Cramér’s V、correlation ratio 等 type-aware association measures。当前 ablation 叫 “No-Correlation Score”。

建议改成：

> **No-Association Scores**

这与 method 的 “statistical association cues” 更一致。

---

### 5.6 “GOGGLE, NoTears are score-based methods” 不准确

Structural Fidelity 部分写：

> “traditional constraint-based methods (FCI) and score-based methods (GOGGLE, NoTears)”

GOGGLE 不应被称为 score-based method。建议改成：

> **“constraint-based methods (FCI), differentiable graph-learning methods (GOGGLE), and continuous-optimization-based structure learners (NoTears)”**

或者更简单：

> **“baseline graph-learning methods such as FCI, GOGGLE, and NoTears”**

---

## 6. Figure / caption 一致性问题

### 6.1 Figure 1 需要同步新标题和新术语

Figure 1 caption 目前说 StructSynth discovers a dependency graph and treats it as a generation plan，方向对。 但 figure 内部图像仍有旧标签，例如 “Dependency Structure Discovery / Structure-Guided Synthesis”。建议全部改成：

* **Evidence-Grounded Graph Induction**
* **Graph-Planned Conditional Synthesis**

Figure caption 里的：

> “from pre-learned graphs”

建议改成：

> **“through learned graphical structures”**

“pre-learned graphs” 听起来像外部给定 graph，不太准确。

---

### 6.2 Figure 2 image 内部标签和 caption 不一致

Figure 2 caption 已经用了新名字：

> Evidence-Grounded Graph Induction
> Graph-Planned Conditional Synthesis

但图内部大标题仍是：

> Dependency Structure Discovery
> Structure-Guided Synthesis

这需要改。Method 正文已经使用新 stage 名。

建议 Figure 2 内部统一为：

> **1. Evidence-Grounded Graph Induction**
> **2. Graph-Planned Conditional Synthesis**

另外 Figure 2 里 prompt box 仍写 (\pi_{\text{generation}})，而主文 equation 用的是 (\pi_{\text{generate}})。建议统一成一个，例如全篇用：

> (\pi_{\text{edge}})

或

> (\pi_{\text{generate}})

---

### 6.3 Figure 4 的 Train Only 曲线要确认

Figure 4 同时展示 AUC、Fidelity、Privacy (\Delta)。caption 中包含 Train Only baseline，但 Train Only 没有 synthetic data，因此 fidelity / privacy risk 对它是否定义需要确认。

如果 Train Only 只用于 AUC 面板，应在 caption 说明：

> **Train Only is shown only for the AUC panel.**

如果 figure 中在 fidelity/privacy 面板也画了 Train Only，需要去掉或解释计算方式。

---

### 6.4 Figure 5 caption 可以更简洁

当前：

> AUC Score on the Adult Dataset Using Various LLMs for StructSynth and CLLM

建议改成：

> **AUC on Adult across LLM backbones.**

正文已经说明比较 StructSynth 与 CLLM across open-source and proprietary LLMs。

---

## 7. Related Work 细节

### 7.1 Section title 建议用 “Related Work”

现在标题是：

> Related Works

ACL / EMNLP 风格通常用：

> **Related Work**

---

### 7.2 CLLM 的描述稍微降调

当前写：

> “CLLM ... treats each column independently without modeling inter-feature dependencies”

这个可能有点过强。建议改成：

> **“does not explicitly model inter-feature dependency structure.”**

这样不容易被 CLLM 作者或 reviewer 质疑。

---

### 7.3 SPADA 的描述应与 intro 保持一致

Related Work 里目前写 SPADA replaces LLM-based generation with KDE / normalizing flows，greatly accelerating sampling but relying on sufficient data to fit reliable conditional distributions。 这个表述是好的。Introduction 里也应该用同样的 role-based distinction：

> **SPADA: graph as external sampler backbone**
> **StructSynth: graph as prompt-level LLM generation plan**

不要在 intro 里写 “SPADA uses graph as internal prior”。

---

## 8. Conclusion：要和新 title 对齐

当前 conclusion 已经比旧版好，但仍然有一些 “dependency-faithful / blueprint / outsized returns” 的表达。 建议把第一句改成和标题完全一致：

> **We presented StructSynth, a framework built on one core idea: dependency graphs can serve as generation plans for low-data tabular synthesis with language models.**

然后删弱：

> “dependency-faithful synthesis”
> “outsized returns”

改成：

> **“graph-planned conditional synthesis”**
> **“consistent improvements in generation quality”**

---

## 9. Appendix 高风险问题

虽然 main text 是重点，但 appendix 里有几个问题会直接影响主文可信度。

### 9.1 Appendix C 仍有旧术语

Appendix C 写：

> “structure-guided synthesis stage”

应改成：

> **Graph-Planned Conditional Synthesis**

Appendix C Summary 里也可以把 “discover-then-synthesize paradigm” 改成：

> **graph-as-plan formulation**

---

### 9.2 Appendix G 有明显 typo：Captial

Figure 6 中多处写成：

> Captial Gain / Captial Loss

应改为：

> **Capital Gain / Capital Loss**

这是显眼 typo，必须修。

---

### 9.3 Appendix G.2 的 causal wording 与主文冲突

Appendix G.2 里大量使用：

* causal mechanism
* smoke causes lung
* causal chain
* valid causal path
* direct causation

这些表述和主文 “DAG is not a ground-truth causal claim” 冲突。Appendix C 已经强调 DAG 是 generative blueprint, not causal claim。 Appendix G.2 应该改成：

> **ground-truth DAG structure**
> **directed dependency path**
> **topological path**
> **reference dependency graph**

如果要说 Asia 本身是 causal BN，可以写：

> **Although the Asia benchmark is defined by a causal Bayesian network, StructSynth uses it only as a reference directed dependency structure for SHD evaluation.**

这样不会和非因果定位冲突。

---

### 9.4 Appendix I.1 有 “true parent nodes” 强 claim

Appendix Extended Discussion 写：

> “guarantees each feature is conditioned on its true parent nodes”

这句话必须改。它不只是措辞问题，而是和非因果定位冲突。应改成：

> **“ensures that each feature is conditioned according to the parent set specified by the induced graph.”**

---

### 9.5 Prompt templates 仍然是 causal prompt

Appendix K prompt 里还有：

* “not caused by any other variable”
* “direct successors (effects)”
* “direct effects”
* “logical contradiction”

这些都容易让 reviewer 认为你们实际上在做 causal discovery，而不是 generation-plan induction。Appendix K 介绍了 prompt pipeline，包括 (\pi_{\text{source}}), (\pi_{\text{generation}}), (\pi_{\text{resolve}}), (\pi_{\text{data_gen}}), (\pi_{\text{iso}})。

建议改成：

> “source nodes” → **root attributes in the generation plan**
> “not caused by any other variable” → **generated without conditioning on other attributes**
> “direct effects” → **direct dependent attributes / successor attributes**
> “cause/effect” → **conditioning predecessor / dependent successor**
> “logical contradiction” → **cyclic dependency in the generation plan**

这会显著降低 causal-discovery reviewer 的攻击面。

---

### 9.6 Appendix D 缺引用

Appendix D 使用 Bergsma and Wicher (2013) 的 bias-corrected Cramér’s V。 但 references 里没有看到 Bergsma and Wicher。需要补 reference。

---

### 9.7 References 有一个明显格式问题

Reference 中出现：

> “Carlo Bifulco, and 1 others”

这个应改成：

> **“Carlo Bifulco, and others”**

或者列出完整作者。这个很容易被看出来。

---

## 10. 建议的最终 submit-ready checklist

我建议学生按下面顺序改：

1. **改 title** 为新标题。
2. **把 main text 所有旧 stage 名同步**：Dependency Structure Discovery → Evidence-Grounded Graph Induction；Structure-Guided Synthesis → Graph-Planned Conditional Synthesis。
3. **删除或弱化所有 guarantee / true parents / causal path / caused by / effects**。
4. **核对 Table 2，尤其 BN statistical fidelity 行**。
5. **把 Privacy Risk 的 ranking 规则写清楚，最好改成 Privacy Deviation**。
6. **统一 Statistical Fidelity 为 Statistical Fidelity Error / Pairwise Fidelity Error**。
7. **修 Figure 1、Figure 2 内部标签**，不仅是 caption。
8. **补 (D_{\text{few}}) 大小和选择策略**。
9. **在 method 中定义 (G_t=(V_t,E_t)), (E_{\text{prop},t}), (V_{\text{new},t})**。
10. **修 Appendix K prompts 的 causal wording**。
11. **修 Captial → Capital；Bergsma & Wicher reference；and 1 others**。
12. **统一 πgenerate / πgeneration / πdata_gen_iso 命名**。

整体而言，现在的论文已经有 submit-ready 的骨架；主要是要把 **generation plan** 这条主线贯彻到底。现在最危险的不是方法本身，而是局部文字仍然残留旧叙事：**structure discovery / executable blueprint / causal source-effect / guarantee**。把这些统一成 **graph induction / graph-planned conditional synthesis / prompt-level generation plan / explicit conditioning schedule** 后，稿子的完整度会明显提升。
