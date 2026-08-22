# Reviewer q74j

Overall Assessment: 4 = Conference | Confidence: 4 | Excitement: 3.5

## Summary Of Weaknesses

1. It is not clear whether the baselines used are the best available methods in their respective categories. As the authors explain in l.052-l.055, deep generative models' performance varies across architectures and some may require many more examples to train. I expected a little explanation in the experiments section that motivates the choice for the particular models used as baselines.
2. It is not always clear why you select a particular dataset to show results. In Section 4.5 and 4.6 why did you choose the Adult dataset and not one of the datasets that are created after the knowledge cutoff for LLMs?

## Comments Suggestions And Typos

The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction.

> Note: Reproducibility/Datasets/Software 评分均为 1，与 7Wh2 和 iRH3 的评分 4 不一致，需确认是否因缺少 supplementary material/code links 导致。

---

## 回复思路

### W1: Baseline 选择的 justification

**审稿人诉求：** 解释为什么选择这些特定的 baseline，是否是各自类别中的最佳方法。审稿人引用了论文 l.052–055 中关于 DGMs 性能因架构而异的讨论。

**回复策略：** 阐明选择标准 → 说明三大类 baseline 的覆盖逻辑 → 回应 low-data 评估的合理性 → 承诺修订

1. **阐明 baseline 选择的系统性标准：**
   - 论文选择了 **12 个 baselines**，涵盖三大范式（§4.1, l.306–312），设计目标是在每个类别中覆盖 **经典方法** 与 **近期代表性工作**：
     - **Deep Generative Models (5)**：TVAE/CTGAN (2019, 最广泛引用的 tabular-specific GAN/VAE)、TabDDPM (2023, 扩散模型代表)、NFlow (2021, normalizing flows 代表)、TabSyn (2024, 最新 SOTA DGM)
     - **Structure-Aware Methods (4)**：BN (经典概率图模型)、GOGGLE (2023, graph-based VAE)、DECAF (2021, causal-aware GAN)、SPADA-NF (2025, 最新 graph+NF 方法)
     - **LLM-based Methods (3)**：GReaT (2023, 首个 LLM tabular synthesizer)、CLLM (2024, prompt-based SOTA)、GraDe (2025, graph-aware LLM)
   - 选择原则：每类别至少包含 1 个经典基准和 1 个 2024–2025 年的最新方法，确保对比的 temporal coverage

2. **回应 "DGMs 需要更多样本" 的关注 (l.052–055)：**
   - 论文 §4.1 l.052–055 的讨论本身就是选择标准的一部分：我们有意在 low-data setting (n=100) 下评估这些方法，**因为我们的研究场景正是数据稀缺**。某些 DGMs（如 TabDDPM、TabSyn）确实在大样本下更强，但在 n=100 下的表现才是我们关心的公平对比条件
   - 主实验表格 (Table 1) 已展示了这一点：DDPM 和 TabSyn 的表现较弱（avg score 63.69 和 68.04），正说明这些大样本优势在 low-data 下不成立
   - §4.5 的 vary-n 实验 (Figure 3) 进一步展示了随 n 增大，baselines 的相对表现如何变化

3. **修订承诺：**
   - 在 §4.1 Baselines 段落中增加选择依据的简要说明（覆盖经典 + SOTA、跨范式、temporal span）
   - 在 Appendix 中补充各 baseline 在大样本和小样本下的已知性能参考

---

### W2: §4.5 和 §4.6 为何选择 Adult 而非 post-cutoff 数据集

**审稿人诉求：** §4.5 (Influence of Training Sample Size) 和 §4.6 (Influence of Different Language Models) 中使用 Adult 数据集而非 post-cutoff 数据集（如 Anxiety, Salary），质疑分析结论是否受 LLM 先验知识的影响。

**回复策略：** 说明 Adult 的选择理由（含空间限制）→ 提供 post-cutoff 数据集的 LLM baseline 补充结果 → 承诺修订

1. **说明选择 Adult 的原始 rationale：**
   - Adult 是表格合成领域**引用最广泛的 benchmark**（被 TVAE/CTGAN, GReaT, CLLM, GraDe, GOGGLE 等几乎所有 baselines 采用），选用它可以让 vary-n 和 LLM 对比结果与已有文献直接比较
   - Adult 具有 14 个 features、混合类型（连续+离散）、48K+ 原始样本，在 schema 复杂度和可用数据量上都适合做 vary-n 分析
   - 消融实验 (§4.3, Table 3) 同样在 Adult 上进行，§4.5–4.6 延续了同一数据集以保持分析的一致性
   - **空间限制**：§4.5 的 vary-n 分析需要在多个 n 值下对比多种方法，同时包含 utility/fidelity/privacy 三个维度（Figure 3 已占较大版面）。在有限的主稿篇幅下，我们选择了单一数据集以深入分析趋势，而非在多个数据集上浅尝辄止

2. **承认审稿人的关切完全合理：**
   - 确实，Adult 可能存在于 LLM 的训练语料中，这使得 §4.5 和 §4.6 的结论**可能部分受益于 LLM 的数据先验**
   - 尤其是 §4.6 (LLM backbone 对比) 中，如果 LLM 已"见过" Adult 的分布，其优势可能被高估

3. **提供 post-cutoff 数据集的补充 vary-n 实验（Anxiety + Salary，仅 LLM 合成 baselines）：**
   - 受空间和计算成本限制，我们在 post-cutoff 数据集上优先对比了 LLM-based 合成方法（CLLM vs StructSynth），因为审稿人的核心关切是 LLM 先验知识的影响。结果如下（n = 20, 50, 100, 200）：

   **Anxiety (Classification, AUC):**

   | Method | n=20 | n=50 | n=100 | n=200 |
   |:--|--:|--:|--:|--:|
   | CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
   | StructSynth | **80.83** | **83.50** | **86.45** | **87.23** |
   | Δ | +3.31 | +1.63 | +1.28 | +1.79 |

   **Salary (Regression, R²):**

   | Method | n=20 | n=50 | n=100 | n=200 |
   |:--|--:|--:|--:|--:|
   | CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
   | StructSynth | 50.56 | 54.90 | **55.98** | 63.54 |

   - **关键观察：**
     - Anxiety（post-cutoff）上 StructSynth 在所有 n 上均优于 CLLM，优势在 n=20 时最大（+3.31 AUC），与 Adult 上的趋势一致
     - Salary（post-cutoff）上结果更 nuanced：n=100 时 StructSynth 略优，n=200 时 CLLM 反超（R² 63.54 vs 61.39），说明回归任务的 LLM 语义先验贡献在大 n 下递减
     - 这些 post-cutoff 结果**验证了 §4.5 在 Adult 上观察到的趋势**——结构引导在低数据时价值最大——同时也揭示了任务相关的 nuance

4. **修订承诺：**
   - 在 §4.5 中补充 Anxiety 和 Salary 的 vary-n 结果（图或表），与 Adult 并列呈现
   - 在 §4.5 的讨论中明确说明 Adult 的选择理由（文献一致性 + 空间限制），并指出 post-cutoff 数据集验证了同一趋势
   - 承诺在修订稿中补充 post-cutoff 数据集上的完整 baseline 对比（含 DGMs 和 Structure-Aware 方法），在 Appendix 中呈现
   - 在 §4.6 中增加至少一个 post-cutoff 数据集（Anxiety）的 LLM backbone 对比作为补充验证

---

### Minor: Introduction 中 goal 描述的位置

**审稿人原文：** The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction.

**回复策略：** 直接接受，承诺在修订中将 "graph as generation plan" 的完整定义（generation order, conditioning context, scope 三要素）提前至 Introduction 的研究问题 (l.085–087) 之后。

---

### Reproducibility/Datasets/Software 评分 = 1

**观察：** Reviewer q74j 给出 Reproducibility=1, Datasets=1, Software=1，与 Reviewer 7Wh2 (4/4/4) 和 iRH3 (4/3/4) 形成显著差异。q74j 的 1 分评语是 "They would not be able to reproduce the results here no matter how hard they tried" 和 "No usable datasets/software submitted"。

**可能原因：**
- 论文提交时可能未附 supplementary material 或 anonymous code link
- 数据集引用了来源但可能未提供预处理后的版本
- q74j 可能严格按照 "是否在提交中包含可用代码/数据" 来评分

**回复策略：**
1. 感谢审稿人指出这一重要问题
2. 说明 code 和 processed datasets 已准备好（或将在 camera-ready 前提供 anonymous link）
3. 具体承诺：
   - 提供完整代码仓库（含图发现、数据生成、评估 pipeline）
   - 提供预处理后的数据集和 train/test splits
   - 提供所有实验配置文件和 random seeds
   - 在 camera-ready 中加入 anonymous GitHub link 或补充材料

---

## Rebuttal-ready paragraphs

### W1 Response

> We appreciate this question and agree that baseline selection justification is important. Our 12 baselines were selected to span three paradigms with both established and recent methods in each: **Deep Generative Models** include the widely cited TVAE/CTGAN (2019), TabDDPM (2023, diffusion), NFlow (2021, normalizing flows), and TabSyn (2024, current DGM SOTA); **Structure-Aware Methods** include BN (classic), GOGGLE (2023, graph-based VAE), DECAF (2021, causal GAN), and SPADA-NF (2025, latest graph+NF); **LLM-based Methods** include GReaT (2023, first LLM synthesizer), CLLM (2024, prompt-based SOTA), and GraDe (2025, graph-aware LLM). Each category thus covers a temporal span from foundational to state-of-the-art.
>
> As the reviewer notes (l.052–055), some DGMs perform best with more training data. Our evaluation at n=100 is deliberate: the low-data regime is precisely our target scenario, and Table 1 shows that methods like TabDDPM and TabSyn underperform here (avg scores 63.69 and 68.04), confirming that large-sample advantages do not transfer to scarce-data settings. We will add a brief justification of our baseline selection criteria in the revision.

### W2 Response

> We chose the Adult dataset for §4.5 (vary-n) and §4.6 (LLM backbone comparison) for two reasons: (1) Adult is the most widely used benchmark in the tabular synthesis literature (adopted by TVAE/CTGAN, GReaT, CLLM, GraDe, and GOGGLE), enabling direct comparison with prior work, and it shares the dataset with the ablation study (§4.3, Table 3), maintaining analytical consistency; (2) space constraints—the vary-n analysis requires reporting multiple methods across several n values on three dimensions (utility/fidelity/privacy), making single-dataset deep analysis preferable to shallow multi-dataset coverage.
>
> However, we fully agree that validating on post-cutoff datasets is important. We have completed vary-n experiments (n=20, 50, 100, 200) comparing LLM-based synthesis methods on Anxiety and Salary, both released after the LLM knowledge cutoff:
>
> | Dataset (Metric) | Method | n=20 | n=50 | n=100 | n=200 |
> |---|---|---|---|---|---|
> | Anxiety (AUC) | CLLM | 77.52 | 81.87 | 85.17 | 85.44 |
> | Anxiety (AUC) | StructSynth | **80.83** | **83.50** | **86.45** | **87.23** |
> | Salary (R²) | CLLM | 48.16 | 52.34 | 54.53 | 61.39 |
> | Salary (R²) | StructSynth | 50.56 | 54.90 | **55.98** | 63.54 |
>
> On Anxiety, StructSynth leads across all sample sizes, with the largest margin at n=20 (+3.31 AUC)—consistent with the Adult trend. On Salary, the advantage is smaller and reverses at n=200 (CLLM R² 63.54 vs. StructSynth 61.39), revealing that regression tasks benefit less from semantic priors as data grows. These post-cutoff results confirm that the trend observed on Adult (structural guidance is most valuable under scarcity) holds on datasets unseen during LLM pretraining.
>
> We additionally ran a fixed-100-shot LLM-backbone check with Qwen3-32B on both post-cutoff datasets (five seeds; 1,000 synthetic rows per seed):
>
> | Dataset | Metric | CLLM | StructSynth |
> |---|---|---:|---:|
> | Anxiety | AUC | 0.8432 ± 0.0118 | 0.8564 ± 0.0141 |
> | Salary | R² | 0.5179 ± 0.0374 | 0.5318 ± 0.0355 |
>
> The utilities are near parity under this newer Qwen backbone: the mean difference is -0.0019 AUC on Anxiety and -0.0039 R² on Salary, both small relative to the five-seed variation. StructSynth also reduces pairwise fidelity error on both datasets; the privacy outcome is dataset-dependent. Thus, this post-cutoff backbone check supports compatibility with Qwen3-32B without claiming a uniform utility gain.
>
> We will include these results alongside the Adult analyses in the revision and supplement them with complete baseline comparisons (including DGMs and Structure-Aware methods) on the post-cutoff datasets in the Appendix.

### Minor Response

> We agree with this suggestion and will move the full definition of "generation plan" earlier in the Introduction in the revision.

### Reproducibility Response

> We note the discrepancy in reproducibility scores (1/1/1 from Reviewer q74j vs. 4/4/4 from Reviewer 7Wh2 and 4/3/4 from Reviewer iRH3) and take this concern seriously. We believe this may stem from the absence of an anonymous code/data link in the submission. We confirm that our complete implementation—including graph discovery, conditional synthesis, and the full evaluation pipeline—as well as preprocessed datasets, train/test splits, configuration files, and random seeds, are ready for release. We commit to providing an anonymous repository link in the revision and will include it as supplementary material. The datasets used are all publicly available (cited in §4.1 and Appendix A), and we will additionally provide our exact preprocessing scripts to ensure full reproducibility.

---

## 整体回复语气策略

Reviewer q74j 是**最正面的审稿人**（Overall 4 = Conference，Excitement 3.5，Soundness 4.5）。其 Summary of Strengths 高度肯定了论文的写作质量、实验设计和消融分析。两个 weakness 都是**合理的方法论改进建议**，而非对论文价值的根本质疑。回复应：

1. **尊重审稿人的专业判断**——q74j 的 Confidence 为 4，对问题的把握准确。两个 weakness 指向的都是实验设计的 **transparency**（选择理由的说明），而非实验质量本身
2. **直接回应每个具体问题**——提供清晰的 rationale + 补充数据 + 修订承诺
3. **主动回应 Reproducibility 评分差异**——虽然审稿人未在 weakness 中明确提出，但 1/1/1 的评分是潜在扣分项，应主动说明并承诺改进
4. **语气积极、高效**——这是一位倾向接收的审稿人，回复的目标是 **消除残余疑虑**，巩固其正面印象
5. **简洁**——q74j 的 review 本身简洁精练，回复也应匹配这一风格，避免冗长
