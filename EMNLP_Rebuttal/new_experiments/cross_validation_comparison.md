# StructSynth × PAFT 双向交叉实验

> 统一数据规模：`n_train=100`，`n_synth=1000`。StructSynth 论文基线来自 Table 1–2（gpt-4o-mini，10 seeds）；PAFT full/graph-orders 来自三变体评估（DistilGPT2，10/5 seeds）；StructSynth + PAFT-FD prior 来自 DeepSeek V4 Flash 实验（seeds 42–46，共 5 seeds）。
>
> **重要口径**：四行 downstream utility 均使用 StructSynth-aligned XGBoost evaluator，因而消除了原先 Logistic/Linear 与 XGBoost 的 learner 混淆。方向 A 严格匹配 seeds 42–46；方向 B 仍因 generator、图先验与 seed 数不同而属于跨配置参照，而非受控消融。
>
> PAFT anonymous-header variant 不涉及 StructSynth/PAFT 结构组件迁移，因此保留在三变体结果目录中，不纳入本交叉实验主表。

## 0. 完整 2×2 设计

两个实验因素分别是图来源（PAFT FD 图或 StructSynth 图）与生成机制（PAFT 训练时排列或 StructSynth 推理时图执行）。每格依次报告 `Avg. AUC / Avg. R² / fidelity error / mean |DCR−0.50|`。

| 图来源 | PAFT generation mechanism | StructSynth generation mechanism |
|---|---|---|
| **PAFT FD graph** | **PAFT full**<br>0.7521 / 0.4039 / **0.5374** / 0.1535<br>10 seeds；DistilGPT2 | **StructSynth + PAFT-FD prior**<br>0.8280 / 0.5697 / 0.5798 / 0.0534<br>5 seeds；DeepSeek V4 Flash |
| **StructSynth graph** | **PAFT + StructSynth graph orders**<br>0.7818 / 0.3596 / 0.5400 / 0.1497<br>5 seeds；DistilGPT2 | **StructSynth full**<br>**0.8295** / **0.5913** / 0.5952 / **0.0322**<br>10 seeds；gpt-4o-mini |

这四格构成完整的**跨系统 2×2 矩阵**，但不是严格受控的 factorial ablation：右列两格的黑盒 generator 不同，两个迁移格只有 5 seeds。它能够支持“图来源与生成机制可分离、可交叉组合”，但不能估计图来源、生成机制及其交互项的净因果效应。

## 1. Downstream utility

| Method | 方向 | Generator | Learner | Seeds | Adult AUC↑ | Anxiety AUC↑ | Compas AUC↑ | Churn AUC↑ | Avg. AUC↑ | Salary R²↑ | Obesity R²↑ | Avg. R²↑ |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| StructSynth（论文） | — | gpt-4o-mini | XGBoost | 10 | 0.8555 | 0.8645 | 0.6940 | 0.9039 | 0.8295 | 0.5598 | 0.6227 | 0.5913 |
| PAFT full | — | DistilGPT2 | XGBoost | 10 | 0.7870 | 0.7217 | 0.6007 | 0.8988 | 0.7521 | 0.4476 | 0.3601 | 0.4039 |
| PAFT + SS graph orders | SS→PAFT | DistilGPT2 | XGBoost | 5 | 0.8170 | 0.8386 | 0.5868 | 0.8849 | 0.7818 | 0.3582 | 0.3609 | 0.3596 |
| StructSynth + PAFT-FD prior | PAFT→SS | DeepSeek V4 Flash | XGBoost | 5 | 0.8504 | 0.8671 | 0.7094 | 0.8848 | 0.8280 | 0.5287 | 0.6108 | 0.5697 |

在统一 XGBoost evaluator 后，StructSynth 论文结果相对 PAFT full 的 Avg. AUC 为 0.8295 vs 0.7521，Avg. R² 为 0.5913 vs 0.4039。该比较使用各方法的原始 generator 配置，因此反映完整系统在 low-data setting 下的结果；它不隔离 generator 容量或训练方式的贡献。PAFT 的 fidelity 更好，而 StructSynth 的 DCR 更接近 0.50，显示两者存在明确的 fidelity–utility–privacy trade-off。

### 方向 A：StructSynth-derived graph ordering → PAFT

本节只比较共同的 seeds 42–46。表中为 mean ± population std，Δ = graph orders − PAFT full。

| Dataset | PAFT full（matched 5 seeds） | PAFT + SS graph orders | Δ | 数值方向 |
|---|---:|---:|---:|---|
| Adult AUC | 0.7910 ± 0.0239 | 0.8170 ± 0.0186 | +0.0260 | 提升 |
| Anxiety AUC | 0.7202 ± 0.0153 | 0.8386 ± 0.0238 | +0.1184 | 提升 |
| Compas AUC | 0.6113 ± 0.0668 | 0.5868 ± 0.0308 | -0.0245 | 下降 |
| Churn AUC | 0.8850 ± 0.0100 | 0.8849 ± 0.0262 | -0.0002 | 基本持平 |
| Obesity R² | 0.3415 ± 0.0617 | 0.3609 ± 0.0987 | +0.0194 | 提升 |
| Salary R² | 0.4149 ± 0.0754 | 0.3582 ± 0.0729 | -0.0566 | 下降 |

分类平均 AUC 从 0.7519 提升到 0.7818（Δ = +0.0299），回归平均 R² 从 0.3782 小幅降到 0.3596（Δ = -0.0186）。因此 graph ordering 的收益仍具有任务选择性：Anxiety 增益最大，Adult 也有提升，Churn 基本不变；Salary 的下降使其不能被表述为普遍改进。

相同 5 seeds 下，平均 fidelity error 从 0.5319 升至 0.5400（+0.0081，变差）；平均 DCR 从 0.6553 降至 0.6497，距理想值 0.50 缩小 0.0056。辅助指标同样呈混合结果。

### 方向 B：PAFT-FD prior → StructSynth

FD-prior 列为 5-seed mean ± population std；Δ = FD prior − StructSynth 论文均值。由于缺少相同 DeepSeek backbone、相同 seeds 下的 StructSynth 原始图基线，Δ 只描述数值差异。

| Dataset | StructSynth（论文） | SS + PAFT-FD prior | Δ | 数值方向 |
|---|---:|---:|---:|---|
| Adult AUC | 0.8555 | 0.8504 ± 0.0122 | -0.0051 | 基本持平 |
| Anxiety AUC | 0.8645 | 0.8671 ± 0.0086 | +0.0026 | 基本持平 |
| Compas AUC | 0.6940 | 0.7094 ± 0.0132 | +0.0154 | 提升 |
| Churn AUC | 0.9039 | 0.8848 ± 0.0094 | -0.0191 | 下降 |
| Obesity R² | 0.6227 | 0.6108 ± 0.0709 | -0.0119 | 基本持平 |
| Salary R² | 0.5598 | 0.5287 ± 0.0441 | -0.0311 | 下降 |

平均 AUC 为 0.8280，与论文基线 0.8295 相差 -0.0015；平均 R² 为 0.5697，与论文基线 0.5913 相差 -0.0215。虽然只有 2/6 个数据集数值提升，5-seed 结果仍表明 PAFT 发现的 FD 图可以接入 StructSynth，并在更换 generator 后维持接近论文结果的整体 utility。这是组件兼容性证据，不能解释为 FD prior 的净因果收益或模型无关性证明。

## 2. Statistical fidelity（相关性误差，越低越好）

FD-prior 的 fidelity 与下节 DCR 使用 PAFT 三变体相同的 shared evaluator 补算，因此这两类指标可以按定义直接比较。

| Method | Adult | Anxiety | Compas | Churn | Obesity | Salary | Avg. | Best on |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| StructSynth（论文） | 0.5760 | 0.5786 | 0.5723 | 0.5863 | 0.6114 | 0.6464 | 0.5952 | 0/6 |
| PAFT full | 0.5166 | **0.4296** | **0.5386** | 0.5472 | **0.5700** | 0.6222 | **0.5374** | 3/6 |
| PAFT + SS graph orders | 0.5030 | 0.4308 | 0.5563 | **0.5429** | 0.5764 | 0.6307 | 0.5400 | 1/6 |
| StructSynth + PAFT-FD prior | **0.4724** | 0.6207 | 0.5844 | 0.6546 | 0.6036 | **0.5435** | 0.5798 | 2/6 |

PAFT full 的总体 fidelity 最佳（0.5374）。FD-prior 混合方法在 Adult 和 Salary 上最佳，并将 StructSynth 的平均误差从 0.5952 降至 0.5798（-0.0154），但在 Anxiety、Compas 与 Churn 上退化，不能声称逐数据集全面改善。

## 3. Privacy（DCR / Prob(NN in Train)，越接近 0.50 越好）

跨数据集汇总采用 `mean |DCR−0.50|`，而不是 `|mean DCR−0.50|`，以避免正负偏差相互抵消。

| Method | Adult | Anxiety | Compas | Churn | Obesity | Salary | Avg. DCR | Mean &#124;DCR−0.50&#124;↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| StructSynth（论文） | **0.4997** | 0.4474 | 0.6237 | **0.4867** | **0.4980** | **0.5013** | 0.5095 | **0.0322** |
| PAFT full | 0.7635 | 0.6076 | 0.7531 | 0.6232 | 0.5708 | 0.6028 | 0.6535 | 0.1535 |
| PAFT + SS graph orders | 0.7388 | 0.5956 | 0.7408 | 0.6514 | 0.5732 | 0.5984 | 0.6497 | 0.1497 |
| StructSynth + PAFT-FD prior | 0.4408 | **0.4696** | **0.6214** | 0.4862 | 0.5588 | 0.5366 | 0.5189 | 0.0534 |

FD-prior 的平均 DCR 为 0.5189，`mean |DCR−0.50|` 为 0.0534，明显优于 PAFT full（0.1535）和 graph orders（0.1497），但仍不及 StructSynth（0.0322）。它在 Anxiety 和 Compas 上最接近 0.50；StructSynth 在其余四个数据集上更接近 0.50。稳妥结论是：PAFT-FD prior 没有破坏 StructSynth 的整体隐私特性，而非某一方法在全部数据集上“显著更安全”。

## 4. 综合结论

| 交叉方向 | Utility | Fidelity | Privacy | 可支持的结论 |
|---|---|---|---|---|
| SS→PAFT：graph orders | 3/6 提升；Avg. AUC +0.0299，Avg. R² -0.0186 | 匹配均值 +0.0081（变差） | DCR 距 0.50 缩小 0.0056 | 对分类任务有选择性帮助；回归略降 |
| PAFT→SS：FD prior | 2/6 提升；Avg. AUC -0.0015，Avg. R² -0.0215 | 相对 SS 平均误差 -0.0154 | Mean &#124;DCR−0.50&#124; = 0.0534 | 图先验可迁移到 SS，并大体保留 utility 与 privacy |

最稳健的双向结论是：**StructSynth 与 PAFT 的结构组件可以相互迁移，但迁移收益不是普遍单调的。** StructSynth-derived graph ordering 对 PAFT 的分类 utility 有选择性帮助；反向使用 PAFT-FD prior 时，StructSynth 维持接近论文结果的 utility、接近 0.50 的 DCR，并获得略低的平均 fidelity error。

不应使用“两个方向均显著提升”或直接比较四行 utility 高低的叙事。当前结果支持两种方法的结构信号具有兼容性，并在 utility、fidelity 与 privacy 之间呈现互补权衡。

## 5. Rebuttal-ready paragraph

> We evaluated all methods with the same XGBoost downstream protocol under the 100-shot, 1,000-sample setting. Under their original generation configurations, StructSynth achieved higher average classification AUC (0.8295 vs. 0.7521) and regression R² (0.5913 vs. 0.4039) than PAFT full, while PAFT retained better pairwise fidelity and StructSynth showed substantially lower DCR deviation from 0.50. We further conducted bidirectional component transfer. Within PAFT and using the same five seeds, StructSynth-derived graph ordering increased average classification AUC from 0.7519 to 0.7818, with the largest gain on Anxiety (+0.1184), while average regression R² changed from 0.3782 to 0.3596. In the reverse direction, feeding PAFT-discovered FD graphs into StructSynth yielded an average AUC of 0.8280 and average R² of 0.5697 over five seeds, close to the StructSynth paper results (0.8295 and 0.5913). These results do not imply uniform gains, but show that graph source and generation mechanism are separable: PAFT-derived dependencies can serve as priors for StructSynth, whereas StructSynth-derived ordering selectively improves PAFT classification. Because the reverse-direction comparison changes the generator backbone, we interpret it as compatibility evidence rather than a controlled ablation.

## 6. 限制与后续最小补充

- 方向 B 缺少同一 DeepSeek V4 Flash、同一 seeds 42–46 下的 StructSynth 原始图基线，无法分离 generator 与 FD-prior 的贡献。
- StructSynth 论文基线为 10 seeds，FD-prior 为 5 seeds；方向 B 不是逐 seed 配对比较。
- PAFT graph-orders 只有 5 seeds，且 Salary 方差很大；补齐 seeds 47–51 后再做配对统计检验更可靠。
- 当前未做多重比较校正后的显著性检验，“提升/下降”只表示数值方向。

## 7. 数据与复核路径

- PAFT 三变体汇总：`paft_three_variants_evaluation/evaluation_outputs/paft_overview.csv`
- PAFT 逐 seed 结果：`paft_three_variants_evaluation/evaluation_outputs/{dataset}/100_shot/{variant}/detailed_results.csv`
- FD-prior downstream：`paft_fd_prior_deepseek_v4_flash/results/metrics_summary.csv`
- FD-prior fidelity/privacy 逐 seed：`paft_fd_prior_deepseek_v4_flash/evaluation_outputs/fidelity_privacy_detailed.csv`
- FD-prior fidelity/privacy 汇总：`paft_fd_prior_deepseek_v4_flash/evaluation_outputs/fidelity_privacy_overview.csv`
