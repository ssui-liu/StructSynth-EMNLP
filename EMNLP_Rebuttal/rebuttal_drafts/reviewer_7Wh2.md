# Reviewer 7Wh2

Overall Assessment: 2 = Resubmit next cycle | Confidence: 5 | Excitement: 1.5

---

## 回复思路

### W1: 与 PAFT 的关系及新颖性

**审稿人原文:** My main concern with this paper is that it is quite close to the paper by S. Xu et al. "Why LLMs Are Bad at Synthetic Table Generation and what to do about it" (https://arxiv.org/abs/2406.14541). This paper argues that LLM tabular generation fails because autoregressive generation imposes an order over columns, and that random feature-order fine-tuning will violate functional dependencies. It proposes injecting knowledge of functional relationships. Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data. As a result, the novelty here is limited and further the experimental results need to be contrasted with this above paper and their PAFT algorithm (in fact they seem to use the same dataset(s) as well).

**回复策略:** 承认引用遗漏并收缩贡献边界 → 精确三方机制区分 → 以 GraDe 作为已有同类方法覆盖的补充说明 → PAFT 直接对比 → 修订承诺

---

#### 1. 承认遗漏，并收缩贡献边界

- 承认应该引用和讨论 PAFT，修订中补充。
- 不强调 PAFT 的发表层级，也不使用未经充分时间线证据支持的“独立、同期开发”作为回应理由；这些信息不能消解 related-work omission。
- **贡献声明收缩**：不再隐含"首次将依赖结构用于 LLM 表格生成"。改为承认 PAFT、GraDe 和 StructSynth 共享"显式依赖结构有益于自回归表格合成"的核心洞察，但走了不同路径。

建议开头表述：

> We thank the reviewer for highlighting PAFT (Xu et al., 2024). We should have cited and discussed this highly relevant work. PAFT and StructSynth share the insight that autoregressive tabular synthesis benefits from explicit dependency structure, but operationalize it through different paradigms. We will revise our contribution statement accordingly and clarify that our novelty lies not in being the first structure-aware approach, but in using a directed dependency graph as an inference-time generation plan in a low-data, black-box setting.

---

#### 2. 精确机制区分（三方对比表）

从论文已有框架出发（§1, l.071–083; §3.2, l.281–297），但不再把 StructSynth 定位为"唯一结构感知方法"，而是在 PAFT–GraDe–StructSynth 谱系内精确定位。

| 维度 | PAFT | GraDe | StructSynth |
|---|---|---|---|
| 结构先验 | HyFD 等发现的 exact FD | HyFD/TANE 的 FD | LLM + 统计信号发现的有向依赖图 |
| 注入方式 | 编译为固定拓扑 permutation | dynamic attention graph + FD loss | 父节点条件提示 + 分层生成 (Eq.4, l.296) |
| 列顺序 | 全局固定 | 随机（per-row shuffle） | DAG 拓扑层 |
| 是否微调 | LoRA / DistilGPT-2 | GPT-2 full fine-tuning | 无需微调，black-box inference-time |
| 运行条件 | 需要足够样本做 fine-tuning | 同上 | 面向 low-data（100 行级），zero parameter update |
| 结构作用方式 | 隐式（编译进训练顺序后消失） | 半显式（attention mask + loss 正则化） | 显式（每步生成由父节点集和拓扑层控制） |

核心区分：三者在**结构类型**（exact FD vs 更一般的有向依赖图）、**注入时机**（训练时 vs 推理时）和**运行条件**（需微调 vs 无需微调）上并不相同。StructSynth 的贡献聚焦于“将有向依赖图用作 inference-time generation plan”——面向 low-data、black-box LLM、zero-parameter-update 的生成设置。这里应强调问题设定和结构使用方式的差异，而不是声称其他范式“不可替代”。

建议表述：

> The core architectural distinction is that PAFT compiles discovered functional dependencies into a global feature permutation for LoRA fine-tuning (DistilGPT2), whereas GraDe injects FD supervision through a dynamic sparse attention graph and an FD-alignment objective during GPT-2 fine-tuning. StructSynth instead uses a directed dependency graph as an inference-time generation plan (§3.2, l.281–297): topological layers determine generation order, parent-node sets determine conditioning context, and local subgraphs determine prompt scope (Eq. 4). Thus, our contribution concerns how dependency structure is explicitly executed at generation time in a black-box, zero-parameter-update setting, rather than the broader idea of structure-aware tabular synthesis itself.

---

#### 3. GraDe 作为补充性定位证据

**论点**：原实验已包含 GraDe（Table 1, l.294），它明确继承 PAFT 的诊断（随机列序破坏 FD），使用同类 FD 提取工具（HyFD/TANE），属于 FD-guided, fine-tuned LLM generator 家族。因此，实验设计并非完全没有覆盖 structure-aware LLM generator；但 GraDe 只能说明我们考虑过这一方法家族，不能替代对 PAFT 的直接讨论和比较。

**数据支撑**：同条件下（100-shot, 10 seeds, 1000 synthetic rows, 统一 XGBoost 评估），StructSynth 在六个数据集上均优于 GraDe（avg 75.01 vs 51.05, avg rank 1.00 vs 7.33）。

建议表述：

> We agree that PAFT is highly relevant. Our submitted evaluation already includes GraDe (Table 1), a structure-aware LLM generator that builds on the diagnosis that random feature orders may violate functional dependencies. Both PAFT and GraDe use externally extracted functional dependencies, although they inject them differently: PAFT converts them into a fixed topological permutation, whereas GraDe uses a learned sparse attention graph and an FD-alignment objective. Under the same 100-shot splits, ten seeds, 1,000 generated samples, and evaluation pipeline, StructSynth outperforms GraDe on all six datasets (avg. 75.01 vs. 51.05). This comparison shows that our evaluation already covers a representative FD-guided, fine-tuned generator, but it does not substitute for a direct comparison with PAFT. We will therefore add both an explicit discussion and a direct PAFT comparison.

**限定**：

- **不做传递推断**：不声称 "StructSynth > GraDe > PAFT"。GraDe 论文虽引用并讨论 PAFT，但自身也未将 PAFT 作为实验 baseline，因此不能做传递链。
- **附录硬伤必须修正**：§A.2 Baselines (l.596–598) 称"除 CuratedLLM 外都使用 SynthCity implementation"，但 GraDe 实际使用官方代码（含 HyFD/TANE FD 提取、dynamic graph attention、FD regularization loss）。如果审稿人核查 GraDe 的实现细节，此错误会直接削弱该论点的可信度。修订中必须改正为：

  > For GraDe, we used the authors' official implementation, which includes HyFD-based functional dependency extraction and dynamic graph attention. For CuratedLLM, we used the official source code provided by the authors. All remaining baselines use the SynthCity library with default hyperparameters.

---

#### 4. PAFT 直接对比（以 2×2 形式呈现的 component-transfer comparison）

在 GraDe 补充定位的基础上，加入 PAFT 的直接结果，并将 generator × structural source 的四种组合以 2×2 形式紧凑呈现。表格以 generator 为主分组，便于在同一生成机制内比较不同结构来源；但由于各 cell 并非严格匹配的受控条件，不将其表述为 factorial ablation，也不据此识别 structural source 或 generator 的独立因果效应。

> 100 real rows → 1,000 synthetic rows，统一 XGBoost 评估；所有指标均为跨数据集平均值。AUC/R² 越高越好，fidelity error 和 DCR deviation 越低越好，其中 DCR deviation = \|DCR−0.50\|。

| Generator | Structural source | Avg. AUC ↑ | Avg. R² ↑ | Avg. fidelity error ↓ | Avg. DCR deviation ↓ |
|:--|:--|--:|--:|--:|--:|
| PAFT | PAFT FD graph | 0.752 | 0.360 | 0.537 | 0.154 |
| PAFT | StructSynth dependency graph | 0.782 | 0.404 | 0.540 | 0.150 |
| StructSynth | PAFT FD graph | 0.808 | 0.550 | 0.580 | 0.053 |
| StructSynth | StructSynth dependency graph | 0.830 | 0.591 | 0.595 | 0.032 |

**核心结论（弱化解释）**：在当前汇总结果中，采用 StructSynth graph 的两组组合具有更高的平均 AUC（+0.030 / +0.022），采用 StructSynth generator 的两组组合也具有更高的平均 AUC（+0.056 / +0.048）和更低的 |DCR−0.50|。这些结果说明两类 graph representation 可以被不同 generator 使用，并为组件兼容性和机制差异提供初步证据。由于实验条件并非严格匹配，不使用“独立贡献”“正交组件”或“贡献叠加”等措辞，也不把行列差值解释为受控 effect size。

**必须主动披露的 caveats**（不能包装成完全同条件的官方复现）：

- graph-order 实验只有 5 seeds，PAFT full 是 10 seeds——seed 数不对齐
- `local_fd` 是对缺失 HyFD 步骤的近似（runner 脚本 `run_structsynth_paft.py:60` 已注明），非完全官方 PAFT 复现
- PAFT 用 DistilGPT2，StructSynth 用 black-box LLM——这是两种方法设计设定的一部分，但也意味着该表不能进行严格的单因素归因
- 定位为**组件兼容性和机制差异的初步证据**，而非严格的 factorial ablation 或全面性能排序

建议表述：

> To directly compare with PAFT, we conducted a component-transfer comparison (100 real rows, 1,000 synthetic rows, unified XGBoost evaluation) and present the four graph–generator combinations in a compact 2×2 format. We note several methodological caveats: (1) our PAFT reproduction uses a local FD approximation rather than the full HyFD pipeline; (2) seed counts differ across conditions (5–10); and (3) PAFT uses fine-tuned DistilGPT2 while StructSynth uses a black-box LLM. Accordingly, the 2×2 layout is descriptive rather than a controlled factorial design. We interpret the results as preliminary evidence that the graph representations are usable across the two generation mechanisms, not as estimates of independent component effects or a definitive ranking of the two methods.

---

#### 5. 下游表现与消融仅作为间接辅助证据

前述机制区分、GraDe 比较和 PAFT 直接对比主要用于说明方法定位，而不能直接证明生成数据忠实保持了依赖结构。对于“结构是否被保持”这一问题，当前论文只能提供以下辅助性、间接证据：

**方向 A：下游 utility 的跨数据集一致性优势**

StructSynth 在 Table 1 中六个数据集上全部排名第一（avg rank 1.00, avg score 75.01），覆盖分类和回归任务、不同特征数和领域。这说明生成数据保留了对下游预测有用的统计信号，可视为与结构利用有效性相一致的间接证据；但 utility 也可能受边缘分布、模型能力等因素影响，因此不能单独证明依赖结构被忠实保持。

**方向 B：消融实验中的结构剥离效应**

Table 3 报告了移除或替换相关设计后下游表现的变化：
- 去掉图（No Structure ≈ CLLM）：AUC −1.6 pts
- 保留图但忽略拓扑序：AUC −1.1 pts
- 保留图但换掉 LLM generator：AUC −4.4 pts

这些结果表明图、拓扑执行顺序和生成器设计都与下游性能相关。其中 “No Topological Order” 在保留图的同时改变执行顺序，为拓扑执行的实际作用提供了较有针对性的证据；但该消融衡量的是对下游 AUC 的贡献，不应进一步表述为对结构保真度或生成质量的严格因果证明。

**方向 C：论文已有的定性结构对比**

§4.5 (l.469–474) 在 Adult 上展示了三张图的对比：reference graph（PC on full data + 领域修正）vs LLM-discovered graph vs re-discovered from synthetic data。合成数据上重新发现的图与 reference graph 的定性相似，为部分核心依赖路径可能得到保留提供了案例证据；由于这里只涉及单个数据集和定性比较，不将其描述为普遍性的“确认”。

**局限性的诚实声明**：以上均为间接证据，不等同于直接的 FD violation rate 或 conditional fidelity 量化。我们将在修订中讨论更直接的结构保真度指标作为 future work 方向。

建议表述：

> We agree that downstream utility is only an indirect measure of structural preservation. StructSynth's consistent rank-1 performance across six datasets indicates that the generated data preserve statistical signals useful for both classification and regression, but does not by itself establish faithful dependency preservation. Our ablation study (Table 3) offers complementary evidence about the proposed mechanism: removing the graph (−1.6 AUC), ignoring topological order (−1.1 AUC), or replacing the LLM generator (−4.4 AUC) each reduces downstream performance. In addition, the Adult case study in §4.5 shows qualitative similarity between dependency pathways rediscovered from synthetic data and the reference graph. We will present these results as supporting rather than conclusive evidence, and explicitly identify direct structural metrics, such as FD violation rates and conditional-distribution fidelity, as an important direction for future evaluation.

---

#### 6. 修订承诺

1. Introduction / Related Work 中引用 PAFT，明确 PAFT–GraDe–StructSynth 三者的技术谱系定位
2. 贡献声明收缩，聚焦 "directed dependency graph as an inference-time generation plan in low-data regimes"，不再隐含"首次结构感知"
3. 加入 PAFT direct baseline 和以 2×2 形式呈现的 component-transfer comparison（明确其并非严格 factorial design，并披露方法论 caveats）
4. 修正附录 §A.2 关于 GraDe 实现的错误描述（官方代码，非 SynthCity）
5. 将 backbone / post-cutoff 实验降为辅助证据，不作为面对结构感知批评的主线
6. 在 future work 中讨论更直接的结构保真度指标（FD violation rate, conditional fidelity）

---

#### 论文已有消融证据的辅助作用

Table 3 (§4.3, l.422–463) 的消融结果表明**图、拓扑执行与 LLM 生成器**分别是当前设计中与性能相关的组成部分，而收益并非仅来自“使用了 DAG”这一标签：

- *No Structure*（去掉图 ≈ CLLM，l.442）：AUC −1.6 pts
- *No Topological Order*（保留图但忽略拓扑序，l.441）：AUC −1.1 pts
- *Bayesian Sampler*（保留图但换掉 LLM generator，l.443）：AUC −4.4 pts

较稳妥的 insight 是：LLM-guided discovery 在当前设置下优于所比较的 classical alternatives；仅有图而没有拓扑执行并不足以获得完整收益；生成器选择也与最终表现相关。StructSynth 将依赖 *discovered and explicitly executed*，而非仅通过 column permutation 间接编码。这里不进一步声称 graph–LLM 存在已被严格识别的因果协同效应。

这些消融在回复中仅作为**辅助证据**使用，说明 StructSynth 的 generation plan 各设计选择与下游表现相关，而不将其解释为结构保真度或独立因果效应的直接证明。

---

### W2: Privacy 评估不充分

**审稿人原文:** Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution.

**回复策略:** 从论文已有分析出发承认边界 → 说明 generation plan 的正则化机制 → 缩窄表述

1. **论文已有的分析基础（§4.2 "Privacy Preservation and Statistical Fidelity Error", l.451–456）：**
   - Table 2 揭示了 fidelity 与 privacy 之间的**根本张力**："high statistical accuracy often results from data memorization"
   - StructSynth 在所有方法中 privacy rank **最优 (1.33)**，同时保持 fidelity rank 5.33（Table 2; l.456）
   - 论文将此归因于 decoupled framework 的**正则化效应**："uses an explicit structural blueprint as a regularizer to guide the LLM"

2. **承认边界：**
   - Privacy Risk (DCR) 是经验性最近邻诊断指标，不构成 differential privacy 等 formal guarantee
   - 论文 Ethical Considerations 已声明："StructSynth is not a formal privacy mechanism"
   - 正则化效应是架构层面的观察，并非有意设计的隐私机制，也未做因果验证

3. **修订承诺：**
   - 将 "privacy preservation" 替换为 "empirical privacy behavior" 或 "privacy-risk evaluation"
   - 明确 DCR 的定义和局限
   - 将 formal privacy guarantee 缺失列为 limitation
   - 讨论 membership-inference evaluation 和 formal privacy 机制集成作为 future work

---

### W3: Statistical fidelity 表现一般

**审稿人原文:** The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results).

**回复策略:** 论文已有分析解释现象 → 联结 W1 的结构指标承诺 → 缓和表述

1. **论文已有的解释——fidelity 中等是设计的合理结果，而非缺陷：**
   - Statistical Fidelity Error 度量合成数据与真实数据之间的**成对相关性匹配度 (pairwise correlations)**，lower is better
   - StructSynth 的 DAG 编码的是**父子节点间的条件依赖 (conditional dependencies)**——后者才是驱动下游模型性能的结构
   - 反例：*Bayesian Sampler* 消融取得**最佳 fidelity (48.86)** 却有**最低 AUC (81.17)**（Table 3, l.443），确认 pairwise-correlation recovery 和 downstream utility 是根本不同的目标

2. **下游 utility 作为结构保持的侧面证据：**
   - Pairwise fidelity 度量的是边际相关性匹配，但驱动下游模型性能的是条件依赖结构
   - StructSynth 在六个数据集上一致排名第一（avg rank 1.00），而 Bayesian Sampler 取得最佳 fidelity 却有最低 AUC——说明 pairwise fidelity 中等恰恰是因为 StructSynth 优先保持了条件结构而非边际相关性
   - 消融中"No Topological Order"（保留图但忽略执行顺序）导致 AUC −1.1 pts，进一步说明结构的使用方式（而非仅存在性）对生成质量有因果影响

3. **StructSynth 的三维 profile：**
   - Table 1：全部六个数据集下游 utility 排名第一，avg rank 1.00，avg score 75.01
   - Table 2：privacy rank 最优 1.33；fidelity rank 中等 5.33
   - 三者构成 **utility–fidelity–privacy trade-off**，而非某一维度的失败

4. **修订承诺：** 在 Abstract / Introduction / Conclusion 中将 "competitive statistical fidelity" 替换为更精确的表述，明确报告三维 trade-off，并阐明 pairwise fidelity 中等与条件结构保持之间的设计性取舍。

---

### W4: Opaque / anonymized schemas 的限制

**审稿人原文:** The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies).

**回复策略:** 论文已承认该限制 → 提供初步消融数据 → 诚实报告 mixed 结果 → 承认 PAFT 在此维度的优势

1. **论文 Limitations 已明确承认**（l.539–550）："When schemas are opaque [...] the semantic prior weakens considerably"; "a fully anonymized schema effectively reduces our hybrid discovery to a purely statistical method"。这一局限是 StructSynth 混合设计（semantic prior + statistical evidence）的固有边界。

2. **但统计关联分数提供了部分补偿：** §3.1.2 (l.249–258) 描述了 BFS 遍历中 Cramér's V / |r| / correlation ratio 的计算（Eq.2）。即使列名匿名化，这些统计量仍可从数据分布中识别依赖关系。匿名化实验验证了这一点：

   > Anxiety + Salary，gpt-5-mini，seed 42，n=1000

   | 数据集 | 条件 | Utility | Fidelity ↓ | DCR (→0.50) |
   |:--|:--|:--|--:|--:|
   | Anxiety | Original | **AUC 0.865** | 0.579 | 0.447 |
   | Anxiety | Anonymized | AUC 0.850 | **0.534** | 0.564 |
   | Salary | Original | **R² 0.560** | 0.646 | 0.501 |
   | Salary | Anonymized | R² 0.462 | **0.615** | 0.412 |

3. **关键观察：**
   - StructSynth 在匿名化后**仍可正常运行**，统计关联分数接管图发现的主要角色
   - Anxiety：utility 略降 (0.865→0.850)，fidelity 改善 (0.579→0.534)，说明部分语义推断的边可能是 spurious
   - Salary：R² 下降较大 (0.560→0.462)，说明对回归任务的语义先验贡献更大
   - 结果是 **mixed** 而非 uniformly robust

4. **诚实承认 PAFT 在此维度的优势：** 审稿人指出 PAFT 的纯统计 FD discovery 可能对 opaque schemas 更不敏感，这是一个合理判断。这是 inference-time semantic prompting vs training-time statistical FD extraction 之间的真实 trade-off，我们将在修订中明确讨论。

5. **修订承诺：** 将 opaque/encoded schemas 明确列为 limitation 而非声称鲁棒；补充匿名化消融结果及其局限；讨论 PAFT 在此维度的互补优势。

---

## 修订摘要（按优先级）

| 优先级 | 事项 | 回应 |
|---|---|---|
| P0 | 引用 PAFT，在 Related Work 中定位 PAFT–GraDe–StructSynth 技术谱系 | W1 |
| P0 | 修正附录 §A.2 关于 GraDe 实现的错误描述（官方代码，非 SynthCity） | W1 |
| P1 | 贡献声明收缩，聚焦 "directed dependency graph as an inference-time generation plan" | W1 |
| P1 | 加入 PAFT direct baseline 和以 2×2 形式呈现的 component-transfer comparison，明确其并非严格 factorial design | W1 |
| P1 | 缩窄 privacy 语言，明确 DCR 非 formal guarantee | W2 |
| P2 | 明确报告 utility–fidelity–privacy 三维 trade-off，阐明 pairwise fidelity 与条件结构保持的设计性取舍 | W3 |
| P2 | 补充 schema anonymization 结果，诚实报告 mixed 结论和 PAFT 互补优势 | W4 |
| P2 | 将 backbone / post-cutoff 实验降为辅助证据 | 全局 |
| P2 | 在 future work 中讨论更直接的结构保真度指标（FD violation rate, conditional fidelity） | W1 |

## 全局注意事项

- **主要受众是 AC**，不是 7Wh2。目标是让 AC 看到技术批评已被实质性回应。
- **绝不在 rebuttal 中提及身份猜测或 COI。**
- **对 PAFT 的态度**：尊重其先行洞察，承认互补性，但精确划界。不过度恭维，不回避。
- 不使用 **"concurrent independent work"** 为引用遗漏辩护，也不强调 PAFT 的 **workshop** 发表层级；二者都无助于回答技术问题。
- 不从审稿人对某项相关工作的关注推断其身份或利益关系；只有在出现可核实、与评审政策直接相关的事实时，才考虑通过 Author–AC Discussion 客观报告。
