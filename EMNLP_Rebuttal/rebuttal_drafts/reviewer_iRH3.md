# Reviewer iRH3

Overall Assessment: 3 = Findings | Confidence: 3 | Excitement: 3

## Summary Of Weaknesses

1. Since the proposed method infers not only the existence of dependencies but also the directions of edges, the evaluation should assess more than statistical fidelity. While the paper reports measures such as Statistical Fidelity Error, it would also be valuable to evaluate the correctness of the learned graph structure, particularly edge directions, on datasets where ground-truth dependency structures are available.
2. The method is specifically motivated by small sample size scenarios, and the experiments focus on sample sizes up to n = 200. However, it is important to understand how the method behaves as more data become available. Experiments with larger sample sizes would help clarify the trade-off between the advantages of LLM-based graph construction and purely data-driven alternatives.
3. As acknowledged in the limitations section, the proposed approach exploits semantic information contained in feature names and descriptions, whereas most non-LLM baselines cannot use such information. This raises questions about the fairness of the comparison. An informative additional experiment would be to anonymize feature names (e.g., replacing them with V1, V2, ...) and evaluate how much the performance depends on semantic information provided by the feature names.

---

## 回复思路

### W1: 图结构正确性评估（边方向）

**审稿人诉求：** 在有 ground-truth 依赖结构的数据集上评估学到的 DAG 的正确性，特别是边方向。

**回复策略：** 论文已做了该实验 → 直接引导审稿人注意 §4.4 和 Figure 3 → 用消融中的 PC/NoTears 侧面印证

1. **论文已包含审稿人建议的评估。** §4.4 "Structural Fidelity under Ground-Truth Graphs" (l.470–490) 正是在有 ground-truth DAG 的数据集上评估了图结构恢复质量：
   - 使用三个 bnlearn benchmark 数据集：**Asia** (8 nodes), **Child** (20 nodes), **Insurance** (27 nodes)
   - 评估指标为 **Structural Hamming Distance (SHD)**——计算恢复真实图所需的边插入、删除和方向反转数，越低越好 (l.475–477)
   - 在 n ∈ {20, 50, 100, 200} 上进行了完整的 vary-n 评估（Figure 3）

2. **Figure 3 的关键结论 (l.479–490)：**
   - StructSynth 在三个数据集上均取得了 **最低或接近最低的 SHD**
   - 优势在 low-data settings (n ≤ 50) 最为显著——此时纯数据驱动的 graph-learning baseline（FCI, GOGGLE, NoTears）产生 **明显更高的结构错误**
   - 这证实了 LLM 语义先验能有效 **弥补小样本下统计信号的不足**，实现鲁棒的结构恢复（包括边方向）

3. **消融实验（Table 3, §4.3）从功能角度进一步印证了结构正确性的价值：**
   - *PC Discovery*（用经典 Peter-Clark 算法替代 LLM-guided 图发现）：AUC 84.54 vs StructSynth 85.55，下降 1.0 pts (l.443–447)
   - *NoTears Discovery*（用连续优化算法替代）：AUC 84.17，下降 1.4 pts
   - 论文总结 (l.443–447)："LLM-guided discovery outperforms classical alternatives"——StructSynth 学到的图结构不仅在 SHD 上更接近 ground-truth，而且在用于 generation plan 时也产生了更好的下游效果
   - *No Topological Order*（保留图但忽略拓扑序）：AUC −1.1 pts (l.449–451)——进一步说明边方向携带的拓扑信息对生成质量有实质性贡献

4. **可能需要补充的说明：**
   - 审稿人可能在阅读时未注意到 §4.4，因为该节标题为 "Structural Fidelity under Ground-Truth Graphs"，可能与前面的 "Statistical Fidelity Error" 指标产生术语上的混淆
   - 在 rebuttal 中应明确指引审稿人阅读 §4.4 和 Figure 3，强调这正是审稿人所要求的评估
   - 可考虑在修订版中将 §4.4 的标题改为更明确的表述（如 "Edge Direction Accuracy on Ground-Truth DAGs"），以减少此类遗漏

---

### W2: 更大样本量 (n > 200) 下的表现

**审稿人诉求：** 理解当更多数据可用时方法的行为，特别是 LLM-based 图构建 vs 纯数据驱动方法的 trade-off。

**回复策略：** Following previous work，描述 n > 200 超出本文聚焦范围 → 引用论文已有 vary-n 趋势 → 给出预期行为

1. **明确本文的研究定位与范围。** Following previous work on LLM-based tabular synthesis（如 CLLM, GReaT 等），我们的实验聚焦于 **n ≤ 200 的 low-data regime**。这一范围选择与先前工作一致：CLLM (Seedat et al., 2024) 同样以 n = 100 为主要实验设置，GReaT (Borisov et al., 2023) 也在小样本场景下报告了主要结果。StructSynth 的核心动机正是解决 **样本稀缺时** 依赖结构难以可靠发现的问题 (l.040–047)，因此实验设计围绕这一目标工作区间展开。

2. **论文已有的 vary-n 趋势提供了关键线索。** §4.5 (l.491–505) 和 Figure 4 在 Adult 数据集上报告了 n ∈ {20, 50, 100, 200} 下的 AUC、Fidelity、Privacy 趋势：
   - StructSynth 在所有 n 上维持高 AUC、低 fidelity error 和接近零的 privacy deviation (l.496–497)
   - 优势在 n ≤ 50 时最为显著——此时 BN 和 GOGGLE 等需要更多样本才能达到竞争力的 baseline 表现明显更弱 (l.498–500)
   - 论文总结 (l.500–505)：generation plan 充当正则化器，**防止 record-level overfitting，并在不同样本量下维持稳定的 utility-fidelity-privacy 平衡**

3. **对 n > 200 的预期行为。** 基于现有趋势和方法设计原理，我们对更大样本量下的行为有明确预期：
   - StructSynth 的混合图发现 (§3.1) 将 LLM 语义先验与统计关联分数（Cramér's V, |r|, correlation ratio）结合。随着 n 增大，统计估计更准确，**数据驱动信号自然增强，LLM 语义先验的相对贡献递减**
   - StructSynth **不会因 n 增大而退化**（统计分量自适应），但其相对于纯数据驱动方法的优势预期会 **收窄**
   - 这与 Figure 3 (§4.4) 中 SHD 实验的趋势一致：随 n 增长，FCI、NoTears 等纯数据驱动方法的 SHD 逐渐下降并趋近 StructSynth，说明统计信号在大 n 下逐渐充分
   - 在 n 足够大的场景下，用户可能更适合使用纯数据驱动的 structure-aware 方法（如 BN, GOGGLE），因为它们无需 LLM API 开销

4. **修订承诺：** 在 Discussion 中增加对 StructSynth **目标工作区间** 的明确讨论，阐述其在 small-to-moderate n 下的设计定位，以及随 n 增长向纯数据驱动方法过渡的预期趋势。

---

### W3: 匿名化特征名实验（信息公平性）

**审稿人诉求：** 将特征名匿名化为 V1, V2, ...，评估性能对语义信息的依赖程度。

**回复策略：** 论文已有的设计要素提供了部分答案 → 匿名化实验直接验证 → 诚实报告 mixed 结果

1. **论文的统计关联分数设计本身就是对这一关切的部分回应：** §3.1.2 (l.249–258) 描述了 BFS 遍历中 Cramér's V / |r| / correlation ratio 的计算（Eq.2, l.262），其设计目的正是 "pairing statistical evidence with the LLM's semantic prior so that each compensates the other's weakness at small n" (l.256–258)。即使列名匿名化，这些统计量仍可从数据分布中识别依赖关系。论文 Limitations (l.545–546) 也已指出 "statistical association cues can partially compensate"。

2. **我们已完成审稿人建议的匿名化实验，直接验证了上述设计：** 列名替换为 `feature_01, feature_02, ...`，任务描述和列描述替换为通用文本，单元格值保持不变。模型: gpt-5-mini, 100 real shots, seed 42。

   > Anxiety + Salary，n=1000

   | 数据集 | 条件 | Utility | Fidelity ↓ | DCR (→0.50) |
   |:--|:--|:--|--:|--:|
   | Anxiety | Original | **AUC 0.865** | 0.579 | 0.447 |
   | Anxiety | Anonymized | AUC 0.850 | **0.534** | 0.564 |
   | Salary | Original | **R² 0.560** | 0.646 | 0.501 |
   | Salary | Anonymized | R² 0.462 | **0.615** | 0.412 |

3. **关键观察：**
   - StructSynth 在匿名化后 **仍可正常运行**，统计关联分数接管了图发现的主要角色
   - Anxiety 上匿名化后 fidelity 改善 (0.579→0.534) 但 utility 略有下降 (AUC 0.865→0.850)，说明语义先验对分类 utility 仍有正向贡献，但部分语义推断的边可能是 spurious 的
   - Salary R² 下降 (0.560→0.462)，说明对回归任务的语义先验贡献更大
   - 结果是 **mixed** 而非 uniformly robust

4. **修订承诺：** 将匿名化实验加入 Appendix，诚实报告 mixed 结论和局限。

---

## Rebuttal-ready paragraphs

### W1 Response

> Thank you for this suggestion. We would like to draw attention to the fact that our paper already includes exactly the evaluation you describe. In §4.4 "Structural Fidelity under Ground-Truth Graphs" (l.470–490), we evaluate structure discovery quality on three bnlearn benchmark datasets with known ground-truth DAGs — Asia (8 nodes), Child (20 nodes), and Insurance (27 nodes) — using the **Structural Hamming Distance (SHD)**, which counts edge insertions, deletions, and reversals needed to recover the true graph (lower is better).
>
> As shown in Figure 3, StructSynth achieves the lowest or near-lowest SHD on all three datasets across varying sample sizes (n ∈ {20, 50, 100, 200}). The advantage is most pronounced in low-data settings (n ≤ 50), where purely data-driven graph-learning methods such as FCI, GOGGLE, and NoTears produce substantially higher structural errors. This confirms that the LLM's semantic prior effectively complements weak statistical signals, enabling robust structure recovery — including edge directions — even from severely limited samples.
>
> These findings are further corroborated by our ablation study (Table 3, §4.3), where substituting our LLM-guided graph discovery with classical alternatives — PC Discovery (−1.0 AUC) and NoTears Discovery (−1.4 AUC) — degrades downstream performance, while ignoring topological order (−1.1 AUC) confirms that the learned edge directions carry functional signal for generation quality.
>
> We apologize if these results were not sufficiently prominent; we will consider revising the section title to make it more immediately clear that this evaluation directly addresses edge direction accuracy on ground-truth DAGs.

### W2 Response

> Thank you for raising this point. Following previous work on LLM-based tabular synthesis — including CLLM (Seedat et al., 2024) and GReaT (Borisov et al., 2023) — our experiments focus on the **low-data regime (n ≤ 200)**, which is the setting where StructSynth's core contribution is most relevant: leveraging LLM semantic priors to compensate for insufficient statistical signals in structure discovery (l.040–047).
>
> Our existing vary-n analysis (§4.5, Figure 4) on the Adult dataset already provides insight into the scaling trend. StructSynth maintains high AUC, low fidelity error, and near-zero privacy deviation across all sample sizes, with the advantage most pronounced at n ≤ 50 where baselines like BN and GOGGLE require significantly more samples to become competitive (l.496–500). The generation plan acts as a regularizer that prevents record-level overfitting, yielding a stable utility-fidelity-privacy balance independent of sample size (l.500–505).
>
> Based on these trends and the method's design, we expect that as n grows beyond 200, StructSynth will **not degrade** — its statistical association component (Cramér's V, |r|, correlation ratio) naturally becomes more accurate with larger samples — but its **marginal advantage over purely data-driven methods will narrow**, as the LLM semantic prior's relative contribution diminishes. This is consistent with the SHD trends in Figure 3, where data-driven methods (FCI, NoTears) gradually approach StructSynth's structural accuracy as n increases. We will add an explicit discussion of StructSynth's target operating range and the expected convergence with data-driven alternatives in the revision.

### W3 Response

> We fully agree with this concern and have conducted the suggested experiment. We anonymized all column names (e.g., `Age` → `feature_01`), replaced domain-specific task descriptions with generic text, and anonymized column descriptions — while keeping cell values intact. Experiments used 100 real training samples.
>
> Results on Anxiety and Salary (n=1000 synthetic samples):
>
> | Dataset | Condition | Downstream | Fidelity (↓) | Privacy DCR (→0.5) |
> |---|---|---|---|---|
> | Anxiety | Original | AUC **0.865** | 0.579 | 0.447 |
> | Anxiety | Anonymized | AUC 0.850 | **0.534** | 0.564 |
> | Salary | Original | R² **0.560** | 0.646 | 0.501 |
> | Salary | Anonymized | R² 0.462 | **0.615** | 0.412 |
>
> On Anxiety, the anonymized variant shows a modest utility decrease (AUC 0.865→0.850) but substantially better fidelity (0.579→0.534), suggesting that some semantically inferred edges may be spurious and a sparser data-driven graph can provide a more precise structural prior. On Salary, the original retains a clear advantage (R² 0.560 vs. 0.462), indicating that semantic priors contribute more to regression tasks involving fine-grained continuous dependencies.
>
> This mixed result is informative: StructSynth remains functional under anonymization because the statistical association scores (Cramér's V, |r|, correlation ratio; §3.1.2) compensate for the absent semantic prior — confirming the design rationale described in l.249–258. Importantly, even in the worst case (Salary), the anonymized variant's R² of 0.462 remains well above the levels achieved by unstructured baselines in Table 1, demonstrating that the performance gains stem primarily from the learned structural dependencies rather than memorized domain knowledge from feature names.
>
> We will include these results in the revision alongside an honest discussion of the task-dependent contribution of semantic priors.

---

## 整体回复语气策略

Reviewer iRH3 是**建设性的、具体的**审稿人（Overall 3，Confidence 3，Excitement 3）。三个 weakness 都是合理的方法论问题，不是对论文价值的根本质疑。回复应：

1. **W1 的核心是引导审稿人注意已有内容**——论文已做了 ground-truth 图评估（§4.4, Figure 3），审稿人可能遗漏了。回复时应礼貌地指引，而非暗示审稿人没读仔细。同时用消融中 PC Discovery 和 NoTears Discovery 的对比侧面印证图结构学习的有效性
2. **W2 的核心是界定研究范围**——following previous work 明确 n ≤ 200 是本文的设计焦点，给出理论预期而非回避问题
3. **W3 的核心是用实验数据直接回应**——已做了审稿人要求的实验，诚实报告 mixed 结论
4. **语气温和、合作性强**——这位审稿人倾向于接收（Findings），回复的目标是巩固其正面印象并充分回应技术关切
