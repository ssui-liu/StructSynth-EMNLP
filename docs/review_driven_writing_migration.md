# KDD Review → TKDD 写作与组织层面迁移指南

> **目的**：从 KDD 四位审稿人（hziw, f5xi, 6JGG, ep8Q）的反馈中，提取所有**写作、论文结构、论证逻辑和呈现方式**层面的改进点，指导 TKDD 期刊版本的修订。  
> **范围**：仅覆盖写作与组织层面，不包含新增实验的具体设计。

---

## 一、审稿人评分中的写作/呈现信号

| 审稿人 | Presentation 得分 | 关键写作信号 |
|:---|:---|:---|
| hziw | 3: Moderate | 批评"工程性强但缺乏理论深度"，暗示论证层次不够 |
| f5xi | 3: Moderate | DAG 假设"未充分 justify"，核心设计选择的解释不足 |
| **6JGG** | **2: Low** | **最低分**，措辞暗示论文表达未能传达其真正贡献 |
| ep8Q | 3: Moderate | 批评"helpful but insufficient"，信息在附录中而非正文 |

> [!IMPORTANT]
> 6JGG 的 Presentation=2 是四人中最低。其批评（"only combines with minor tweaks"）部分源于论文未能清晰传达各组件的**非平凡创新**。写作层面的改进有望同时提升 Presentation 和 Novelty 评分。

---

## 二、核心写作问题与迁移建议

### 2.1 新颖性论证不足 — "创新点被埋没"

**问题来源**：hziw W1、6JGG W1、f5xi（Novelty=2 连带）

**审稿人共识**：三位审稿人认为论文在新颖性表述上不够有力，核心表现为：
- 未明确区分 StructSynth 与 prior "structure learning + generation" 框架的**本质差异**
- Hybrid discovery、Reasoned cycle resolution 等技术创新被轻描淡写
- 与最相近工作 GraDe 的区别（硬约束 vs 软约束）未被突出

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **Introduction 新增 "Key Insight" 段落**：在贡献点列表前，用 1-2 段清晰阐述为什么现有三类范式（DGM/Structure-Aware/LLM-based）都不能解决低数据下的结构与生成协同问题 | `introduction.tex` | 🔴 高 |
| 2 | **贡献点按技术深度重新组织**：当前三个贡献点偏向"做了什么"，需改写为"解决了什么问题 + 如何解决 + 效果"的三段式 | `introduction.tex` | 🔴 高 |
| 3 | **Method 节为每个组件添加 "Design Rationale" 段落**：在 Hybrid Discovery、Cycle Resolution、Topological Generation 三个子节开头，各用一段解释**为什么这样设计**（而非仅描述"是什么"） | `method.tex` | 🔴 高 |
| 4 | **新增 "Comparison with Closest Work" 表格**：在 Related Work 或 Method 末尾用结构化表格对比 StructSynth vs GraDe vs DECAF vs BN，维度包括：结构发现方式、约束类型（硬/软）、生成策略、低数据适应性 | `related_work.tex` 或 `method.tex` | 🟡 中 |
| 5 | **Ablation 部分加入叙事性总结段落**：Table 3 后用一段文字总结"如果各组件只是 minor tweaks，替换后不应导致 1.0-4.4 pts 的退化"，直接回应"模块拼接"的质疑 | `experiments.tex` | 🟡 中 |

---

### 2.2 DAG 假设的合理性论证缺失

**问题来源**：f5xi W1（核心批评）

**原文**：*"The formulation of inter-column dependency as a DAG is not sufficiently justified... feature dependencies are often better viewed as associative rather than inherently directional"*

**问题本质**：论文选择 DAG 作为依赖结构的建模形式，但仅在脚注中给出了 "generative blueprint" 的定位声明，正文未充分解释为什么 DAG（而非无向图）是生成任务的正确选择。

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **将脚注内容升级为正文段落**：将 `introduction.tex:47` 的 "generative blueprint" 脚注扩写为 Method 节的独立段落 | `method.tex` 开头 | 🔴 高 |
| 2 | **新增 "Why DAG?" 论证**：（a）autoregressive 生成本质上需要方向性和顺序；（b）无向图无法直接定义条件化顺序；（c）DAG 的无环性是避免循环依赖的数学前提；（d）与 BN 文献传统的一致性 | `method.tex` | 🔴 高 |
| 3 | **明确声明**：DAG 中的边是 **functional dependency for generation**，不是 causal claim | `method.tex` | 🔴 高 |

---

### 2.3 低数据动机论证薄弱

**问题来源**：hziw W2

**原文**：*"the method mainly relies on LLM reasoning without specific mechanisms for small-sample instability, and is equally applicable to large-data settings, weakening its core motivation"*

**问题本质**：论文声称聚焦低数据，但未明确论证**为什么 StructSynth 在低数据下特别有效**，以及**LLM 先验如何具体对抗小样本不稳定性**。

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **Introduction 增加 "Low-Data Challenge" 段落**：用 2-3 句明确阐述传统统计方法在 n < 100 时的失败模式（关联检验不稳定、结构发现不可靠） | `introduction.tex` | 🔴 高 |
| 2 | **Method 节显式标注低数据机制**：在对应位置标注三个机制：(a) LLM semantic prior 作为结构正则化器；(b) Statistical cues 作为弱监督（而非唯一决策依据）；(c) 解耦设计降低样本复杂度 | `method.tex` | 🟡 中 |
| 3 | **新增 "Why Low-Data Is Our Advantage Zone" 总结段落**：在 varying-n 实验结果后，用一段解释为什么 n≤50 时优势最显著、n 增大时差距缩小 | `experiments.tex` | 🟡 中 |

---

### 2.4 关键信息被"藏"在附录中

**问题来源**：6JGG W3（LLM 设置匹配信息在 Appendix 中）、ep8Q W4（prompt 有帮助但不够）、hziw W4（成本分析仅 3 行）、f5xi W5（计算开销未充分讨论）

**问题本质**：审稿人反复批评的内容，论文实际已有详细数据——但在附录中。正文的过度压缩导致审稿人无法发现已有证据。

> [!WARNING]
> 这是 KDD 会议风格的典型遗留问题：8 页限制迫使所有细节进入附录。TKDD 无页数限制，**必须将核心证据从附录迁移到正文**。

**TKDD 迁移建议**（与 `appendix_migration_plan.md` 协同）：

| 关键迁移内容 | 当前位置 | 目标位置 | 解决的审稿人批评 |
|:---|:---|:---|:---|
| CLLM LLM 设置匹配声明 + Table 2 超参数表 | Appendix A.2.2 | `experiments.tex` — Implementation Details | 6JGG W3 "LLM mismatch" |
| Token Usage 分析表 + input-dominant 分析 | Appendix A.8 | `experiments.tex` — Efficiency Analysis | hziw Q5, f5xi W5 |
| SHD 实验的图可视化（Adult + Asia） | Appendix A.6, A.7 | `experiments.tex` — Qualitative Analysis | f5xi W4, hziw Q3 |
| 评估指标数学定义 | Appendix A.4 | `experiments.tex` — Evaluation Metrics | 审稿人对指标合理性的质疑 |
| 算法伪代码 Algorithm 1 | Appendix A.5 | `method.tex` 末尾 | ep8Q W4, 6JGG Reproducibility=1 |
| 关联度量公式 | Appendix A.3 | `method.tex` — Statistical Association | f5xi "未达预期" |

---

### 2.5 Privacy 指标的合理性论证

**问题来源**：hziw W3

**原文**：*"The privacy metric based on nearest-neighbor matching is insufficiently justified and not compared with standard approaches (e.g., membership inference)"*

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **Evaluation Metrics 节展开 Privacy Risk 定义**：从 Appendix 迁入完整数学定义，添加 1-2 句解释该指标的**社区使用情况**（SDV, SynthCity 框架） | `experiments.tex` | 🔴 高 |
| 2 | **新增 "Relationship to MIA" 段落**：说明 NN Privacy Risk 与 Membership Inference Attack 衡量不同维度（record-level memorization vs model-level information leakage），二者是**互补而非替代** | `experiments.tex` | 🟡 中 |
| 3 | **审慎化 privacy 声明措辞**：全文检查，确保所有 privacy 相关表述为 "privacy-fidelity trade-off" 而非暗示绝对隐私保证 | 全文 | 🟡 中 |

---

### 2.6 Statistical Fidelity 结果的解释缺失

**问题来源**：f5xi W3（核心难点）

**原文**：*"one would expect stronger statistical fidelity than prior LLM-based methods... However, the reported results do not clearly support this expectation, and the current explanation is not fully convincing"*

**问题本质**：StructSynth 引入了结构发现，但 Statistical Fidelity（pairwise correlation 匹配度）不如 GReaT。论文未解释这一看似矛盾的结果。

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **新增 "Understanding the Fidelity-Privacy Trade-off" 段落**：解释 GReaT 的高 fidelity 来自 fine-tuning 导致的 memorization（Privacy Risk 90.15%），StructSynth 的结构蓝图作为正则化器，有意牺牲 pairwise fidelity 换取 privacy 保护 | `experiments.tex` | 🔴 高 |
| 2 | **重新框定 Statistical Fidelity 的角色**：说明该指标衡量的是 pairwise correlation（所有特征对），而非 conditional dependency（DAG 编码的依赖关系）。StructSynth 优化后者，不直接优化前者 | `experiments.tex` | 🔴 高 |
| 3 | **用 Bayesian Sampler 数据佐证**：Bayesian Sampler fidelity 最佳（48.86）但 AUC 最低（81.17），说明 Fidelity ≠ Utility | `experiments.tex` | 🟡 中 |

---

### 2.7 与纯 LLM 方法的本质区别论证

**问题来源**：6JGG W2, Q1（最核心质疑之一）

**原文**：*"It has no fundamental difference with the methods with LLM"*

**问题本质**：论文未在正文中用足够的篇幅和清晰度论证 StructSynth 与 CLLM 等纯 LLM 方法的**质变**（而非量变）。

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **Method 或 Discussion 新增 "Structure-Blind vs Structure-Aware Generation" 对比段**：用三个维度对比——(a) 结构建模（无 vs 显式 DAG）；(b) 生成策略（无约束 vs 拓扑硬约束）；(c) 正则化效应（无 vs DAG 正则化器） | `method.tex` 或新增 `discussion.tex` | 🔴 高 |
| 2 | **Ablation 结果的叙事强化**：在 No Structure (=CLLM) 变体结果旁，明确标注"这等价于在相同 LLM 设置下移除所有结构引导"，使读者立即理解 -1.6 pts 的含义 | `experiments.tex` | 🟡 中 |

---

### 2.8 Source Node 假设的可用性讨论

**问题来源**：f5xi W2

**原文**：*"It is unclear how the method would work when such source nodes do not exist or cannot be reliably identified"*

**TKDD 迁移建议**：

| # | 具体行动 | 位置 | 优先级 |
|:---|:---|:---|:---|
| 1 | **Method 添加 "Source Node Identification" 讨论段落**：解释 source node 仅决定 BFS 起点而非最终结构，BFS 扩展 + cycle resolution 提供纠错 | `method.tex` | 🟡 中 |
| 2 | **讨论退化策略**：当无明确 source node 时可选择"最独立"特征或退化为 pairwise discovery（Ablation: AUC 85.25 vs 85.55） | `method.tex` 或 `discussion.tex` | 🟡 中 |

---

## 三、论文结构层面的迁移建议

### 3.1 新增章节

| 新增章节 | 内容要点 | 理由 |
|:---|:---|:---|
| **Discussion** | ① 优势场景与局限场景分析；② 结构发现质量与下游性能的关系讨论；③ 与因果推断方法的区别声明；④ Fidelity-Privacy trade-off 的深入解释 | hziw W4 "缺乏理论深度"、f5xi W3 "统计保真度落差"、6JGG Q1 "本质区别" |
| **Limitations** | ① LLM 先验偏差的局限；② 高维场景（50+ features）的可扩展性；③ DAG 假设不支持环形依赖；④ API 调用成本 | 期刊审稿人高度关注(hziw W2, ep8Q Q2, f5xi W5) |
| **Complexity Analysis** | BFS O(K) vs Pairwise O(K²) 的形式化分析 | hziw W4 "缺乏理论深度"、f5xi W5 "计算开销" |

### 3.2 现有章节扩展

| 章节 | 扩展方向 | 理由 |
|:---|:---|:---|
| **Related Work** | 新增 Structure Learning 子节（传统方法 + LLM-based 方法），系统化对比 | hziw Q1: "clearly distinguish from prior frameworks" |
| **Conclusion** | 从 3 行扩至 8-15 行，含贡献回顾 + 关键发现 + Future Work | 期刊标准 |
| **Introduction** | 末尾添加论文组织说明段落 | 期刊标准做法 |

---

## 四、写作风格迁移要点

### 4.1 从"描述做了什么"到"论证为什么这样做"

**KDD 风格（当前）**：
> "We employ BFS traversal to discover dependency structures, injecting statistical association scores into each step."

**TKDD 风格（目标）**：
> "A key design choice in StructSynth is the use of BFS traversal over pairwise querying. While pairwise approaches require O(K²) LLM calls, BFS reduces this to O(K) while maintaining comparable accuracy (Ablation: AUC 85.25 vs 85.55). More importantly, BFS naturally reveals the hierarchical layer structure needed for topological generation, making the two stages synergistic."

### 4.2 从"结果呈现"到"结果解读"

审稿人的一个共同不满是论文**只呈现了结果但未充分解读**。例如：

- Statistical Fidelity 排名第 7 但未解释为什么 → f5xi W3
- Privacy Risk 接近 0.5 但未论证其意义 → hziw W3
- Token overhead +31% 但未分析 cost-effectiveness → hziw Q5

**建议**：每个主要实验结果表/图后，添加 1-2 段 **"Analysis and Interpretation"**，解释结果的含义、可能原因和对方法设计的启示。

### 4.3 时态与语气

| 场景 | KDD 惯例 | TKDD 期刊惯例 |
|:---|:---|:---|
| 方法描述 | 混合使用 present/past | 一致使用 present tense |
| 实验结果 | "We achieved..." | "Table X shows that..." / "Results indicate..." |
| 指标声明 | 可能过度乐观 | 审慎表述，用 "trade-off" 而非绝对声明 |

---

## 五、逐审稿人写作层面迁移映射

| 审稿人 | 批评点 | 写作层面根因 | TKDD 改进 | 对应章节 |
|:---|:---|:---|:---|:---|
| **hziw** | W1: 新颖性不足 | 技术创新点未被清晰传达 | 重写贡献点 + 添加 design rationale | Introduction, Method |
| | W2: 低数据动机弱 | 未显式论证 LLM prior 的正则化效应 | 添加低数据机制讨论段落 | Introduction, Method |
| | W3: 隐私指标 | 指标合理性论证在 Appendix 中 | 迁移定义到正文 + 互补性讨论 | Experiments |
| | W4: 缺乏深度 | SHD/成本分析被压缩在附录 | 全部迁入正文 | Experiments |
| **f5xi** | W1: DAG 假设 | 仅脚注解释 | 升级为正文段落 | Method |
| | W2: Source Node | 未讨论边界情况 | 添加讨论段落 | Method/Discussion |
| | W3: Fidelity 落差 | 未解释看似矛盾的结果 | 添加 trade-off 解释段 | Experiments |
| | W4: 错误传播 | SHD 和 ablation 在附录中 | 迁移 + 添加 graceful degradation 讨论 | Experiments |
| | W5: 计算开销 | 正文仅 3 行 | 展开为完整效率分析节 | Experiments |
| **6JGG** | W1: Minor tweaks | 各组件创新深度未传达 | 重写 Method 各子节开头 | Method |
| | W2: 与 LLM 无区别 | 没有 structure-blind vs aware 对比 | 添加对比论证段 | Method/Discussion |
| | W3: LLM mismatch | 公平性声明在附录中 | 迁移到 Implementation Details | Experiments |
| | Presentation=2 | 整体论证力度不足 | 全文层面强化 "why" 而非 "what" | 全文 |
| **ep8Q** | W4: 可复现性 | Prompt 有帮助但缺代码 | 添加 Reproducibility Statement | Experiments |

---

## 六、优先级总结与执行清单

### 🔴 高优先级（直接影响核心评分维度：Novelty + Technical Quality + Presentation）

- [ ] 重写 Introduction 贡献点（从"做了什么"到"解决了什么 + 为什么 + 效果"）
- [ ] Method 节每个组件添加 Design Rationale 段落
- [ ] DAG 假设从脚注升级到正文段落 + "Why DAG?" 论证
- [ ] 将核心实验参数/指标定义/成本分析从附录迁入正文
- [ ] 新增 Statistical Fidelity 的 Fidelity-Privacy trade-off 解释段
- [ ] 新增 Structure-Blind vs Structure-Aware 对比论证
- [ ] 新增 Discussion 章节
- [ ] 新增 Limitations 章节

### 🟡 中优先级（显著提升论文深度与可信度）

- [ ] 新增 Closest Work 对比表格
- [ ] Ablation 叙事性总结段落
- [ ] 低数据机制的显式标注
- [ ] Privacy 指标与 MIA 的互补性讨论
- [ ] Source Node 假设讨论
- [ ] Complexity Analysis 子节
- [ ] Related Work 新增 Structure Learning 子节
- [ ] Conclusion 扩展（3 行 → 8-15 行）

### 🟢 低优先级（锦上添花）

- [ ] 全文时态统一（present tense for method, "Results show..." for experiments）
- [ ] "Paper Organization" 段落（Introduction 末尾）
- [ ] Reproducibility Statement
- [ ] 每个结果表/图后的 Analysis and Interpretation 段落
