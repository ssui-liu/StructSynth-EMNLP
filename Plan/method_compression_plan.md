# Method 保守压缩改进计划

> 目标：将 Method 正文（不含 Table 1）从当前 ~1312 词 / ~2.3 页压缩到 ~900-1000 词 / ~1.6-1.8 页，保留核心形式化表达力，削减冗余和中间变量定义。
> 修改文件：`Latex-EMNLP/sections/method.tex`
> 压缩策略：保守——保留叙事骨架和核心公式，只削减明确冗余

---

## 一、当前结构量化诊断

### 1.1 整体指标

| 指标 | 当前值 |
|---|---|
| 总词数（不含 Table 1） | 1312 |
| 公式数 | 6（Eq.1-6） |
| subsection 数 | 3（Problem Definition / Dependency Structure Discovery / Structure-Guided Synthesis） |
| subsubsection 数 | 7 |
| 预估页数（含 Table 1 浮动体） | ~2.3 页 |

### 1.2 各部分词数

| 部分 | 原文位置 | 词数 | 公式 | 问题诊断 |
|---|---|---:|---|---|
| §3 开头段 + §3.1 Problem Definition | L1-9 | 219 | — | Problem Definition 过长（~170 词），形式化了 D_train、A、X、f_LLM、D_aug、D_test 等平凡符号；§3 开头段与 §3.2 开头段有两阶段描述重复 |
| §3.2 开头段（Discovery 总述） | L11-13 | 115 | — | 与 §3 开头段重复讲"两阶段"和 BFS 设计动机 |
| §3.2.1 Graph Initialization | L15-20 | 116 | Eq.(1) | 基本合理，但 L20 的 BFS 队列初始化描述略冗余 |
| §3.2.2 Expansion & Link Generation | L22-37 | 258 | Eq.(2)(3) | **最大压缩来源之一**。Eq.(3) 只是从 P_i 拆出 E_prop 和 V_new 两个中间集合，无独立技术贡献。Association scores 的三种度量在正文展开，应指向 Appendix |
| §3.2.3 Cycle Resolution | L39-50 | 254 | Eq.(4) | **最大压缩来源之二**。L43 的举例 "(e.g., {(A→B, r_ab), ...})" 占篇幅但不增信息。Eq.(4) 中 E_pruned 的集合推导式可简化为文字 |
| §3.2.4 Continuation of BFS | L53-55 | 78 | — | **完全冗余**。"继续直到队列空"是 BFS 的默认行为，可合并到 §3.2.2 或 §3.2.3 末尾一句 |
| §3.3 开头 + §3.3.1 Graph-Based Values | L99-113 | ~140 | Eq.(5) | 基本合理，但 projection operator Π 的形式化定义可用文字替代 |
| §3.3.2 Independent Values | L115-121 | ~70 | Eq.(6) | 可保留，但 Eq.(6) 价值较低，可考虑用文字替代 |
| §3.3.3 Final Assembly | L123-125 | ~54 | — | **完全冗余**。"拼接两部分"是平凡操作，合并到 §3.3.2 末尾一句即可 |

---

## 二、压缩操作清单

每个操作项标注：操作编号、改动类型、预估节省词数、涉及的公式/段落、具体做法、审计检查点。

### OP-1：压缩 Problem Definition

| 属性 | 值 |
|---|---|
| **改动类型** | 重写 |
| **位置** | L5-9（§3.1 Problem Definition） |
| **预估节省** | ~100 词（从 ~170 词压到 ~70 词） |

**具体做法**：

将当前 ~170 词的形式化定义压缩为一个紧凑段落，保留核心符号 $\mathcal{D}_{\mathtt{train}}$、$n \le 100$、$\mathbf{A}$、$f_{\mathtt{LLM}}$、$\mathcal{D}_{\mathtt{synth}}$，但删除 $\mathbf{X}_{\mathtt{train}} = \{\mathbf{x}_1, \ldots, \mathbf{x}_n\}$ 的逐一展开、$\mathcal{D}_{\mathtt{aug}}$ 的形式化定义、以及 "exhibits superior performance on a held-out test set" 等冗余表述。

**目标行文**（参考模板）：
> Given a small tabular dataset $\mathcal{D}_{\mathtt{train}} = (\mathbf{X}_{\mathtt{train}}, \mathbf{A})$ with $n \le 100$ instances and $K$ attributes, our goal is to use an LLM-based generator $f_{\mathtt{LLM}}$ to produce a synthetic dataset $\mathcal{D}_{\mathtt{synth}}$ that, when combined with $\mathcal{D}_{\mathtt{train}}$, improves downstream model performance. We adopt the DAG formulation for its functional role in defining a generative ordering; Appendix~\ref{sec:why_dag} provides a detailed justification.

**审计检查点**：
- [ ] §3.1 词数 ≤ 80
- [ ] 保留符号：$\mathcal{D}_{\mathtt{train}}$、$\mathbf{A}$、$n \le 100$、$K$、$f_{\mathtt{LLM}}$、$\mathcal{D}_{\mathtt{synth}}$
- [ ] DAG justification 的 Appendix 引用保留
- [ ] $\mathcal{D}_{\mathtt{aug}}$ 和 $\mathcal{D}_{\mathtt{test}}$ 的形式化定义已删除（这些在 Experiments 中再引入更自然）

---

### OP-2：合并 §3 开头段与 §3.2 开头段

| 属性 | 值 |
|---|---|
| **改动类型** | 合并 + 精简 |
| **位置** | L1-3（§3 开头段）+ L11-13（§3.2 开头段） |
| **预估节省** | ~70 词（从 ~165 词合并压到 ~95 词） |

**具体做法**：

当前两段都在讲"两阶段"和"BFS + LLM + statistical cues"。将 §3 开头段保留为唯一的方法总述，吸收 §3.2 开头段中的设计动机（(a) LLM semantic prior, (b) statistical association scores, (c) decoupling），然后 §3.2 直接从 DAG 定义 $G=(V,E)$ 开始，不再重复总述。

**审计检查点**：
- [ ] §3 开头段包含：两阶段名称、Figure 引用、Appendix 脚注、三点设计动机 (a)(b)(c)
- [ ] §3.2 首句直接引入 $G=(V,E)$ 定义，不重复 "two stages" 或 "BFS-guided"
- [ ] 合并后总述段词数 ≤ 100
- [ ] Appendix 脚注（prompt templates + algorithm）保留

---

### OP-3：精简 §3.2.1 Graph Initialization

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L15-20 |
| **预估节省** | ~30 词（从 ~116 词压到 ~85 词） |

**具体做法**：

- 保留 Eq.(1) 不变
- 删除 L20 中 BFS 队列和 V_visited 初始化的冗余描述（"To manage the discovery process, a queue Q for the Breadth-First Search (BFS) is initialized with these source nodes, i.e., Q ← V_source, and a set for tracking explored attributes, V_visited, is initialized as empty."）——这些是标准 BFS 实现细节，算法伪代码已在 Appendix 中
- 用一句替代："The graph is initialized as $G_0 = (V_{\mathtt{source}}, \emptyset)$ and expanded via BFS from these source nodes."

**审计检查点**：
- [ ] Eq.(1) 完整保留
- [ ] "source nodes" 概念清晰定义
- [ ] $G_0 = (V_{\mathtt{source}}, \emptyset)$ 保留
- [ ] BFS 队列初始化细节已删除
- [ ] 词数 ≤ 90

---

### OP-4：压缩 §3.2.2 Expansion & Link Generation + 删除 Eq.(3)

| 属性 | 值 |
|---|---|
| **改动类型** | 重写 + 公式删除 |
| **位置** | L22-37 |
| **预估节省** | ~100 词（从 ~258 词压到 ~155 词） |

**具体做法**：

1. **Association scores**：将三种度量名称（Pearson's R / Correlation Ratio / Cramér's V）从正文展开改为一句概括 + Appendix 引用。当前原文："These scores are calculated using dependency measures specific to the data types of each attribute pair: \textit{Pearson's R} for continuous-continuous pairs, \textit{Correlation Ratio} for categorical-continuous pairs, and \textit{Cramér's V} for categorical-categorical pairs" → 压缩为 "using type-appropriate measures (Appendix~\ref{app:association_scores})"

2. **保留 Eq.(2)** — 这是 Stage 1 的核心操作

3. **删除 Eq.(3)** — E_prop 和 V_new 的集合定义只是从 P_i 中拆出两个中间变量，用一句文字替代："From $P_i$, new edges and previously unseen nodes are extracted and added to the graph and BFS queue, respectively."

4. **删除 L37 末尾冗余句**："These new nodes are then added to the queue Q for subsequent exploration, ensuring the continued expansion of the graph." — 与替代句重复

**审计检查点**：
- [ ] Eq.(2) 完整保留
- [ ] Eq.(3) 已删除
- [ ] Association scores 的三种度量名称不再出现在正文（只在 Appendix）
- [ ] Appendix~\ref{app:association_scores} 引用保留
- [ ] P_i 的 successor-rationale pairs 含义仍清晰
- [ ] 词数 ≤ 160

---

### OP-5：压缩 §3.2.3 Cycle Resolution + 简化 Eq.(4)

| 属性 | 值 |
|---|---|
| **改动类型** | 重写 + 公式简化 |
| **位置** | L39-50 |
| **预估节省** | ~100 词（从 ~254 词压到 ~150 词） |

**具体做法**：

1. **删除举例**：L43 中 "(e.g., \{ (A \to B, r_{ab}), (B \to C, r_{bc}), (C \to A, r_{ca}) \})" 占 ~20 词但不增信息，删除

2. **简化 Eq.(4)**：当前 Eq.(4) 是两行 aligned 公式，分别定义 E_pruned（集合推导式）和 G_{t+1}（图更新）。保守方案：将 E_pruned 行改为文字描述，只保留 G_{t+1} 更新公式为单行 equation：
   ```
   G_{t+1} = (V_t \cup V_{\mathtt{new},t},\ E_{\mathtt{candidate}} \setminus E_{\mathtt{pruned}})
   ```
   其中 E_pruned 由前文文字说明："For each detected cycle, the LLM identifies and removes the least justified edge; the union of all removed edges forms $E_{\mathtt{pruned}}$."

3. **压缩描述性文字**：当前段落中 "the framework initiates a reasoned resolution process"、"The prompt's input, ψ, provides the model with the complete logical contradiction, including the rationales for both newly proposed and previously established edges" 等冗余描述压缩

4. **删除末尾总结句**："This general mechanism ensures the graph remains acyclic and empowers the model to revise its structure based on new, more confident evidence." — 信息已由前文覆盖

**审计检查点**：
- [ ] Eq.(4) 简化为单行（只保留 G_{t+1} 更新）
- [ ] 举例 "(e.g., ...)" 已删除
- [ ] Cycle detection → LLM resolution → edge pruning 的三步逻辑仍清晰
- [ ] π_resolve prompt 引用保留
- [ ] 末尾总结句已删除
- [ ] 词数 ≤ 155

---

### OP-6：删除 §3.2.4 Continuation of BFS

| 属性 | 值 |
|---|---|
| **改动类型** | 整段删除 |
| **位置** | L53-55 |
| **预估节省** | ~78 词 |

**具体做法**：

删除整个 §3.2.4 subsubsection。BFS "继续直到队列空" 是默认行为，在 OP-5 末尾加一句收尾即可："This expansion-resolution cycle continues until the BFS queue is empty, yielding the final DAG $G$."

**审计检查点**：
- [ ] §3.2.4 "Continuation of BFS" subsubsection 不存在
- [ ] §3.2.3 末尾有 BFS 终止条件的一句说明
- [ ] "final DAG $G$" 或等价表述出现在 Stage 1 末尾

---

### OP-7：精简 §3.3.1 Generating Graph-Based Values

| 属性 | 值 |
|---|---|
| **改动类型** | 行文收紧 |
| **位置** | L104-113 |
| **预估节省** | ~30 词（从 ~140 词压到 ~110 词） |

**具体做法**：

1. **删除 projection operator 形式化定义**：当前 "$\mathcal{D}_{\mathtt{few\_shot}}^i = \Pi_{L_i \cup \Gamma^{-}(L_i)}(\mathcal{D}_{\mathtt{few\_shot}})$, where $\Pi$ denotes the projection operator onto specified columns" → 替换为 "along with the corresponding columns from the few-shot examples"

2. **保留 Eq.(5)** — 这是整个方法的关键等式，描述拓扑层条件生成

3. **保留拓扑层概念** $\mathcal{L} = (L_1, \dots, L_m)$ 和 parent nodes $\Gamma^{-}(L_i)$ 的定义

**审计检查点**：
- [ ] Eq.(5) 完整保留
- [ ] 拓扑层 $\mathcal{L}$ 和 parent nodes $\Gamma^{-}$ 定义保留
- [ ] Projection operator $\Pi$ 的形式化定义已删除
- [ ] 词数 ≤ 115

---

### OP-8：合并 §3.3.2 + §3.3.3，保留 Eq.(6)

| 属性 | 值 |
|---|---|
| **改动类型** | 合并两个 subsubsection |
| **位置** | L115-125 |
| **预估节省** | ~40 词（从 ~124 词压到 ~85 词） |

**具体做法**：

1. 将 §3.3.3 Final Assembly 的内容（"concatenating graph-dependent and independent values → repeat s times → D_synth"）合并到 §3.3.2 末尾，作为 1-2 句收尾
2. 删除 §3.3.3 的 subsubsection 标题
3. §3.3.2 标题改为 "Generating Independent Values and Final Assembly" 或直接改为 "Completing Synthesis"
4. 保留 Eq.(6)，紧凑表述
5. 删除 projection operator 形式化（同 OP-7 策略）："$\mathcal{D}_{\mathtt{few\_shot}}^{\mathtt{iso}} = \Pi_{A_{\mathtt{iso}}}(\mathcal{D}_{\mathtt{few\_shot}})$" → 删除或简化

**审计检查点**：
- [ ] §3.3.3 "Final Assembly" subsubsection 不存在
- [ ] Eq.(6) 保留
- [ ] $\mathcal{D}_{\mathtt{synth}}$ 最终定义出现在合并后的段落末尾
- [ ] 生成 $s$ 次得到 $\mathbf{X}_{\mathtt{synth}}$ 的说明保留
- [ ] 词数 ≤ 90

---

## 三、公式保留/删除/简化汇总

| 公式 | 内容 | 操作 | 理由 |
|---|---|---|---|
| Eq.(1) | $V_{\mathtt{source}} = f_{\mathtt{LLM}}(\pi_{\mathtt{source}}(\mathcal{D}_{\mathtt{few\_shot}}))$ | **保留** | Stage 1 入口，简洁 |
| Eq.(2) | $P_i = f_{\mathtt{LLM}}(\pi_{\mathtt{generate}}(A_i, G_t, \mathcal{S}(A_i), \mathcal{D}_{\mathtt{few\_shot}}))$ | **保留** | Stage 1 核心操作 |
| Eq.(3) | $E_{\mathtt{prop},t}$ 和 $V_{\mathtt{new},t}$ 集合定义 | **删除→文字** | 中间变量，无独立技术贡献 |
| Eq.(4) | $E_{\mathtt{pruned}}$ + $G_{t+1}$ 更新 | **简化** | 删除 $E_{\mathtt{pruned}}$ 集合推导，只保留 $G_{t+1}$ 更新单行 |
| Eq.(5) | 拓扑层条件生成 | **保留** | 整个方法的关键等式 |
| Eq.(6) | 孤立属性生成 | **保留** | 完整性需要，与 Eq.(5) 配对 |

压缩后正文公式：4 个完整 + 1 个简化 = **4-5 个公式**（从 6 个减少）。

---

## 四、结构变化汇总

| 改前 | 改后 | 说明 |
|---|---|---|
| §3 开头段 + §3.2 开头段（两段分离） | §3 开头段（合并，含设计动机） | OP-2 |
| §3.1 Problem Definition（~170 词） | §3.1 Problem Definition（~70 词） | OP-1 |
| §3.2.1 Graph Initialization | §3.2.1 Graph Initialization（精简队列描述） | OP-3 |
| §3.2.2 Expansion & Link Generation（含 Eq.2+3） | §3.2.2 Expansion & Link Generation（保留 Eq.2，删 Eq.3） | OP-4 |
| §3.2.3 Cycle Resolution（含完整 Eq.4） | §3.2.3 Cycle Resolution（简化 Eq.4 + 吸收 BFS 终止句） | OP-5 + OP-6 |
| §3.2.4 Continuation of BFS | **删除** | OP-6 |
| §3.3.1 Generating Graph-Based Values | §3.3.1 Generating Graph-Based Values（删 Π 形式化） | OP-7 |
| §3.3.2 Generating Independent Values | §3.3.2 Completing Synthesis（合并 Final Assembly） | OP-8 |
| §3.3.3 Final Assembly | **删除**（合并到 §3.3.2） | OP-8 |

subsubsection 数：7 → **5**

---

## 五、预期效果

| 指标 | 改前 | 改后 | 变化 |
|---|---|---|---|
| 总词数（不含 Table 1） | 1312 | ~900-1000 | -312 到 -412 词（-24% 到 -31%） |
| 公式数 | 6 | 4-5 | -1 到 -2 |
| subsubsection 数 | 7 | 5 | -2 |
| 预估页数 | ~2.3 页 | ~1.6-1.8 页 | 节省 ~0.5-0.7 页 |
| 形式化完整性 | 完整（含中间变量） | 核心保留，中间变量改为文字 | 审稿人仍可从正文理解完整方法 |

### 各操作节省词数预估汇总

| 操作 | 节省词数 |
|---|---:|
| OP-1：压缩 Problem Definition | ~100 |
| OP-2：合并开头段 | ~70 |
| OP-3：精简 Graph Initialization | ~30 |
| OP-4：压缩 Expansion + 删 Eq.(3) | ~100 |
| OP-5：压缩 Cycle Resolution + 简化 Eq.(4) | ~100 |
| OP-6：删除 Continuation of BFS | ~78 |
| OP-7：精简 Graph-Based Values | ~30 |
| OP-8：合并 Independent Values + Final Assembly | ~40 |
| **合计** | **~548** |

注：部分操作会增加少量替代文字（收尾句、文字化描述），实际净节省约 **~350-420 词**。

---

## 六、P0 级内容修正（须同步完成）

这些修正来自审阅文档 §3.3 和 §6，在 Method 中涉及的部分：

| 问题 | 位置 | 修改 | 审计检查点 |
|---|---|---|---|
| "causal" 语言残留 | 全文检查 | 将 Method 中任何 `causal pathway/mechanism` 替换为 `dependency pathway/structural dependency` | [ ] Method 中不出现 "causal pathway" 或 "causal mechanism"（"causal" 仅在引用 bnlearn ground-truth 时可出现） |
| Cycle Resolution 描述中 "empowers the model" 过于拟人化 | L50 | 删除（OP-5 已覆盖） | [ ] 无拟人化表述 |

---

## 七、不在本计划范围内的项目

以下事项与 Method 压缩相关但属于独立任务，此处仅记录不执行：

1. **Table 1 位置调整** — Table 1 当前浮动在 Method §3.2.4 之后，是否移到 Experiments 是排版决策
2. **Figure 2 缩小** — 审阅文档建议缩小 pipeline 图，但这是独立的排版操作
3. **Appendix 中新增被移出的形式化内容** — Eq.(3) 和中间变量定义移到 Appendix，需要在 Appendix 的算法描述中确认覆盖（当前 Appendix~\ref{sec:algorithm} 已有完整伪代码，理论上已覆盖）

---

## 八、实施顺序与 Git 提交计划

每个操作作为独立 commit，便于回档和审计：

| 步骤 | 操作 | Git commit message |
|---|---|---|
| 1 | OP-1：压缩 Problem Definition | `Method OP-1: Compress Problem Definition (~100 words saved)` |
| 2 | OP-2：合并 §3 开头段与 §3.2 开头段 | `Method OP-2: Merge section and subsection openers (~70 words saved)` |
| 3 | OP-3：精简 Graph Initialization | `Method OP-3: Tighten Graph Initialization (~30 words saved)` |
| 4 | OP-4：压缩 Expansion + 删 Eq.(3) | `Method OP-4: Compress Expansion, remove Eq.(3) (~100 words saved)` |
| 5 | OP-5 + OP-6：压缩 Cycle Resolution + 删 BFS Continuation | `Method OP-5+6: Compress Cycle Resolution, remove BFS Continuation (~178 words saved)` |
| 6 | OP-7：精简 Graph-Based Values | `Method OP-7: Tighten Graph-Based Values (~30 words saved)` |
| 7 | OP-8：合并 Independent Values + Final Assembly | `Method OP-8: Merge Independent Values and Final Assembly (~40 words saved)` |
| 8 | P0 修正：causal 语言检查 | `Method P0: Replace causal language with dependency language` |
| 9 | 审计：词数 + 公式数 + 结构检查 | 不产生 commit，仅输出报告 |

### 每步审计流程

每个 commit 后执行 subagent 审查，检查：
1. 该操作的所有审计检查点是否通过
2. 改动是否引入 LaTeX 语法错误
3. 改动是否意外删除了计划保留的内容

---

## 九、完整审计检查清单

最终验收时逐项核对：

### 结构审计
- [ ] subsection 数 = 3（Problem Definition / Dependency Structure Discovery / Structure-Guided Synthesis）
- [ ] subsubsection 数 = 5（Graph Initialization / Expansion & Link Generation / Cycle Resolution / Generating Graph-Based Values / Completing Synthesis）
- [ ] §3.2.4 "Continuation of BFS" 不存在
- [ ] §3.3.3 "Final Assembly" 不存在

### 公式审计
- [ ] Eq.(1) 完整保留：$V_{\mathtt{source}} = f_{\mathtt{LLM}}(\pi_{\mathtt{source}}(\mathcal{D}_{\mathtt{few\_shot}}))$
- [ ] Eq.(2) 完整保留：$P_i = f_{\mathtt{LLM}}(\pi_{\mathtt{generate}}(...))$
- [ ] 原 Eq.(3) 已删除（$E_{\mathtt{prop}}$ 和 $V_{\mathtt{new}}$ 的集合定义）
- [ ] 原 Eq.(4) 已简化为单行 $G_{t+1}$ 更新
- [ ] Eq.(5) 完整保留：拓扑层条件生成
- [ ] Eq.(6) 保留：孤立属性生成
- [ ] 正文公式总数 = 4 或 5

### 词数审计
- [ ] §3.1 Problem Definition ≤ 80 词
- [ ] §3 开头段（合并后）≤ 100 词
- [ ] §3.2.2 Expansion ≤ 160 词
- [ ] §3.2.3 Cycle Resolution ≤ 155 词
- [ ] 总词数（不含 Table 1）≤ 1000 词

### 内容审计
- [ ] 所有 Appendix 引用保留（\ref{app:prompts}, \ref{sec:algorithm}, \ref{sec:why_dag}, \ref{app:association_scores}）
- [ ] Figure~\ref{fig:pipeline} 引用保留
- [ ] Method 中无 "causal pathway" 或 "causal mechanism"
- [ ] Method 中无 "Recently" / "More recently" 时间副词
- [ ] 核心概念完整：source nodes → BFS expansion → statistical cues → LLM link proposal → cycle resolution → topological layers → parent conditioning → isolated attributes → final dataset
