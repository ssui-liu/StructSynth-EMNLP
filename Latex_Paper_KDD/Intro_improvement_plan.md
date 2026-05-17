下面给出一个**按你提出的三点修改方向**（合并段落、扩展内容、引入 data mining / pattern / dependency 话语体系）重构后的 **Introduction 修改大纲**。大纲默认在正文中以 **Fig. 1**（你上传的示意图）作为“方法谱系 + 我们位置”的核心锚点来组织叙事。

---

## 0) 题目候选（弱化 LLM、强化数据性质/依赖结构）

优先贴近你给的方向（“Dependency Structure Discovery …”）：

1. **Dependency Structure Discovery for Tabular Data Synthesis in Low-Data Regimes**
2. **Structure Discovery for High-Fidelity Tabular Data Synthesis under Data Scarcity**
3. **Discover-then-Synthesize: Dependency-Aware Tabular Data Generation in Low-Data Settings**

（你们原题“Leveraging LLMs …”可以作为副标题或方法段落里再强调，以避免 intro 一上来“LLM 先行”。）

---

## 1) Intro 目标段落结构（建议 4 段 + 贡献列表）

你现在的 intro 分段偏细，可以**合并为 4 个大段落**：**问题—方法谱系/缺口—核心观点+RQ—方案概览+贡献**。你们论文现有动机要点（低数据、DGM 隐式学依赖失真、LLM 线性化忽略显式结构、两阶段 StructSynth）保持不变，但叙事更“聚合”。([arXiv][1])

---

## 2) Paragraph-by-paragraph 修改大纲（含每段应扩写的“内容抓手”）

### P1 — 背景与问题定义：把“表格数据”写成“依赖结构 + pattern”的对象

**目的**：用 data mining 语汇把问题抬高一层，不只是“数据少”，而是“结构/依赖难可靠挖掘”。

* 开场句式（建议）：

  * Tabular data 在医疗/金融/教育等领域广泛存在，但其价值来自**可解释的依赖关系与统计模式（dependencies / patterns）**；在低数据与隐私约束下，这些模式难以被可靠建模，从而限制下游 ML。([arXiv][1])
* 扩写抓手：

  * 强调“低数据场景”不仅样本少，还常见 **class imbalance、缺失值、离散/连续混合、长尾类别**，使得“pattern mining / dependency discovery”本身就更不稳定。
  * 引入“合成数据”的定位：不仅补量，更要补**结构信息**，否则对下游模型是“噪声增强”。

> 这一段建议合并你们目前 intro 的前两段，减少碎分段感。([arXiv][1])

---

### P2 — 方法谱系与缺口：用 Fig.1 做“对比地图”，明确三类路线各自的结构瓶颈

**目的**：把“DGM vs structure-aware vs LLM”变成一张结构化对照（Fig.1），并把缺口落在 **dependency structure discovery** 上。

* 叙事主线（建议按三块，但写成一个大段落）：

  1. **Deep generative models**（VAE/GAN/Diffusion）在数据充足时可隐式拟合分布，但在低数据下隐式学习的依赖模式会显著失真，导致低保真合成。([arXiv][1])
  2. **Structure-aware 生成**（Bayesian network/graph-inductive bias）理论上能更好保结构，但前提是能从数据中学到可靠的依赖图；低数据下这个前提崩塌。([arXiv][1])
  3. **LLM-based few-shot 生成**看似绕开数据稀缺，但线性化表格输入使其只能“在序列中诱导依赖”，难表达显式图结构，容易生成与真实结构不一致的 dependencies。([arXiv][1])

* **Fig.1 引用放置建议**：

  * 在本段中后部加一句：

    * “As summarized in **Fig.1**, existing paradigms either *implicitly* fit dependencies (data-hungry) or *induce* dependencies from linearized text (structure-blind), while explicit structure-aware synthesis is bottlenecked by unreliable graph discovery in low-data regimes.”
  * 这样 Fig.1 不只是“方法图”，而是 intro 的论证工具。

* 可以额外补一句“结构保真”为什么重要（为后文实验指标铺垫）：

  * 近期也有工作把 **structural fidelity** 作为评价核心维度，说明“会不会学到结构”本身就是 tabular generation 的关键痛点。([arXiv][2])

---

### P3 — 核心观点 + Research Questions：把问题收束成“Discover-then-Synthesize”的 data mining 视角

**目的**：把你们现有的两条 RQ（结构怎么学、LLM 怎么用）扩展成更强的“先挖依赖、再控生成”的框架陈述。

* 建议写法：

  * 把 tabular synthesis 明确为一个 data mining pipeline：

    1. **Dependency/structure discovery**（从少量样本中挖掘稳定依赖/模式）
    2. **Structure-conditioned generation**（在显式结构约束下生成，避免 spurious patterns）
* RQ 的表达建议更“dependency-centric”：

  * RQ1：低数据下如何更可靠地做 dependency structure discovery（减少偶然相关、提升可解释性与稳定性）？([arXiv][1])
  * RQ2：如何让生成过程显式遵循该结构（而非仅从线性序列“诱导”）以提升 structural fidelity 与 downstream utility？([arXiv][1])
* 关键词注入（建议在本段自然出现，而非堆砌）：

  * dependency discovery / pattern mining / relational structure / structural fidelity / structure-conditioned synthesis / spurious dependency

---

### P4 — 方法概览（Fig.1 再次锚定）+ 贡献与结论句

**目的**：用一段话清晰交代 StructSynth 的两阶段，并把“by construction 保结构”说透；然后用更有信息密度的贡献列表收尾。

* 开段直接 Ref Fig.1（建议固定句式）：

  * “**As illustrated in Fig.1**, we propose StructSynth, a decoupled two-stage framework: (i) **Dependency Structure Discovery**, and (ii) **Structure-Guided Synthesis**.”([arXiv][1])
* 两阶段各用 1–2 句、但信息更具体（比现在“点到为止”更展开一点）：

  1. Discovery：强调“LLM + statistical cues + search/consistency”，点到 BFS / cycle resolution / rationale 等“可靠性机制”，但不深入算法细节（intro 适度）。([arXiv][3])
  2. Synthesis：强调“topological layering / parent-conditioned autoregressive generation”，突出“结构约束进入生成过程”，不是后处理。([arXiv][3])
* 贡献列表（建议从“方法 + 机制 + 结果/指标”三点写得更有抓手）：

  * **(i)** 提出一个面向低数据的 dependency structure discovery + synthesis 解耦框架（discover-then-synthesize）。([arXiv][1])
  * **(ii)** 以显式结构作为 generation blueprint，使合成数据在生成时即满足 dependency constraints，从机制上提升 structural fidelity。([arXiv][1])
  * **(iii)** 实验证明在低数据场景取得更好的 structural integrity 与 downstream utility，并能更好权衡 privacy 与 statistical fidelity。([arXiv][4])

---

## 3) 建议你在 Intro 里“显式加入”的词汇槽位

为了符合你说的“多扯 data mining / pattern / dependency”，建议固定在以下位置自然出现：

* P1：pattern / dependency / data mining（把表格数据定义成“依赖结构承载体”）
* P2：implicit dependency learning（DGM）/ induced dependencies（LLM）/ explicit dependency graph（structure-aware）
* P3：dependency structure discovery / spurious dependencies / structural fidelity
* P4：structure-conditioned generation / blueprint / by construction

---

如果你愿意再进一步把这个大纲落成“可直接替换你们现有 Introduction 的英文段落草稿”（按 4 段结构写完整文本，并给出 Fig.1 引用的推荐句子与位置），我也可以基于上述大纲直接生成一版可用的 intro 初稿。

[1]: https://arxiv.org/html/2508.02601v1 "StructSynth: Leveraging LLMs for Structure-Aware Tabular Data Synthesis in Low-Data Regimes"
[2]: https://arxiv.org/abs/2503.09453?utm_source=chatgpt.com "How Well Does Your Tabular Generator Learn the Structure of Tabular Data?"
[3]: https://arxiv.org/pdf/2508.02601 "StructSynth: Leveraging LLMs for Structure-Aware Tabular Data Synthesis in Low-Data Regimes"
[4]: https://arxiv.org/abs/2508.02601?utm_source=chatgpt.com "StructSynth: Leveraging LLMs for Structure-Aware Tabular Data Synthesis in Low-Data Regimes"
