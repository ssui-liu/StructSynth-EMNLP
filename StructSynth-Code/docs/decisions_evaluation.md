# 数据与评估：协议与实现选择

本文依据论文的方法正文，以及附录的数据集、超参数和评估指标定义，说明数据边界与评价协议的实现选择。代码位于 [`data/`](../src/structsynth/data/) 和 [`evaluation/`](../src/structsynth/evaluation/)。

## 与论文逐项对齐

| 项目 | 论文位置 | 实现 |
|---|---|---|
| 数据边界 | Appendix `app:datasets`，原始数据先按 8:2 分割，再从训练池抽取 n 条 | `split_dataset` 先创建固定 holdout，再抽取 `shot` 条；剩余记录命名为 `unused`，不送入模型。改变 shot 不改变同一 seed 的 test。 |
| 重复实验 | Appendix `app:datasets`，42–51 共十个种子 | `seed` 由实验配置传入；数据层没有固定循环或全局 RNG 修改。主流程保存每个 seed 的结果。 |
| 稀缺训练集与 prompt 示例 | Method 开头的 `D_train` 与 `D_few_shot` 是不同集合 | `split_dataset` 生成完整的 n 条真实训练数据；`sample_examples` 再从其中抽取上下文示例，不能用 holdout 或 unused 补充。 |
| 下游默认协议 | Method 开头及 Appendix `app:metrics` | 默认 `augmentation`：XGBoost 仅拟合 `real_train + synthetic`，在真实 test 上评分。另提供明确标记的 `real_only`、`synthetic_only`。 |
| 下游参数 | Appendix `tab:hyperparameters` | XGBoost 的十项树参数逐项设置，包括 100 棵树、0.1 learning rate、depth 6；随机种子来自运行配置。`n_jobs=1` 是为确定性和资源约束作的工程选择，可覆盖。 |
| 主要效用指标 | Appendix `app:metrics` | 分类返回 AUC，回归返回 R²；附带分类 accuracy/macro-F1 或回归 MAE/RMSE。分类类别映射仅从拟合数据学习。 |
| Privacy 参考集 | Appendix `app:privacy_metric` | 每次按给定 seed 无放回下采样较大的真实 train/test，使二者参考样本数相等。这里的 train 是 n 条训练数据，不是完整 80% 训练池。 |
| Privacy 距离 | Appendix `app:privacy_metric` 公式 | 默认数值原始 L1 距离 + 分类 Hamming 距离，包含目标列；不擅自把论文默认改成标准化距离。返回 `privacy_risk`；兼容别名 `dcr` 表示同一概率，不是平均距离。 |
| 数值–数值 fidelity | Appendix `app:fidelity_metric` | `abs(rho_real - rho_synthetic)`，rho 保留正负号；与图发现使用 `abs(rho)` 的关联强度区分。该项可以达到 2，不能统一裁剪到 [0,1]。 |
| 分类–分类 fidelity | 同上 | 两列联合分布的 TVD；真实与合成的类别并集上补零，保留未知类别的概率质量。 |
| 混合 fidelity | 同上 | 数值列 q=10 分位分箱后计算联合 TVD；所有无序列对等权平均，包含目标列。 |

## 论文未明确的选择

1. **分类抽样**：论文写随机划分，没有明确分层。保留旧代码意图，holdout 按类别分层；n 条训练样本按原训练池比例分配，但保证每类至少一条。分配使用带容量约束的确定性配额；如果 n 小于类别数或 holdout 无法覆盖类别，直接报错。回归不分层，不再通过 dataset/target 名称猜测任务。
2. **prompt 类别平衡**：论文没有规定平衡算法。默认分类 prompt 按类别尽量等额，无放回抽样；少数类不足时把配额给其他类；回归均匀抽样。该选择只作用于上下文示例，不重采样完整 n 条训练数据。所有随机性使用局部 Generator。
3. **类别与字段元信息**：初始 CSV dtype 仅用于描述字段存储类型；`infer_training_schema` 在拆分后只为分类 target 推断闭合类别域，整数 dtype、nullable 同样只从训练数据补充。普通分类特征仅在 metadata 显式给出 `categories` 时闭域；有限训练集不保证观察到全部真实特征类别，自动闭域会限制论文依赖的语义先验。观察到的特征类别单独记录在 `training_metadata.observed_categories`，不是生成硬约束。整数推断不依赖“小样本碰巧全为整数”，数值 min/max 只保存为描述统计，不作为生成的硬范围。
4. **多分类 AUC**：论文只写 AUC，未指定聚合；选择 macro one-vs-rest，并在返回值中标为 `macro_ovr`。test 缺少拟合类别、出现新目标类别、模型没有概率输出时，AUC 返回 `null` 和原因，不补造测试样本或扩大训练词表。test 目标常量或不足两条时 R² 同样返回 `null`。
5. **下游预处理**：论文未写编码和缺失策略。数值缺失用模型拟合数据中的中位数填充；全部缺失的训练特征固定填 0。类别使用训练集拟合 one-hot；新测试类别变为全零块。缺失类别本身作为一个显式类别。augmentation 时拟合数据包括真实训练样本与合成样本，这是协议的一部分；任何 test 信息均不参与拟合。
6. **Privacy 距离缩放**：论文公式没有缩放，所以默认 `none`。增加显式 `train_range` 作为敏感性分析：仅从有限真实训练集计算各数值列的 range；零 range 使用 1。此模式改变度量定义，必须与默认分开报告；每次输出记录 scaling 名称与实际 scale。
7. **Privacy 并列最近邻**：原实现 `argmin` 因 train 排在前面而把所有并列判给 train。论文 argmin 没有定义并列处理。新实现均匀选择所有最近记录的期望归属概率，保留重复记录的重数。例如 train 有两条距离为 0、test 有一条距离为 0，贡献为 2/3；两组同样最近记录数时为 1/2。浮点并列阈值为 rtol=atol=1e-12，并写入结果。等大小参考集消除样本数偏差，但有限数据集上的 0.5 并非确定性保证。
8. **Fidelity 的真实参考集**：论文在 Privacy 中把 `D_real` 定义为有限 train ∪ test，随后 fidelity 延用同一符号；旧代码却仅使用 test。新默认由主流程明确选择 `train_test` 并记入报告，也允许单独 train/test。这里只把真实参考数据用于评价，不会影响生成或下游预处理。
9. **混合 fidelity 的分箱边界**：论文没有说明两个数据集是否共享边界。旧代码各自 qcut 后直接比较区间字符串；即便分布相近，只要边界小幅移动就会错误成为不同类别。新实现仅从指定 real reference 学习边界，同一边界应用于合成集，最外侧区间延伸至无穷以保留越界合成记录的质量。边界写入结果，可审查。
10. **常量列与缺失数值**：常量或不足两条记录的 Pearson 未定义，采用零关联约定并列出受影响的列对；混合列若真实数值为常量，退回精确数值类别以保留合成值漂移。Privacy/fidelity 的论文公式没有规定缺失数值处理，因此遇到 NaN/Inf 明确失败，避免把未知处理伪装为论文指标；分类缺失按显式类别比较。只有一列时 fidelity 返回 `null`，不返回虚假的完美零分。

## 输入兼容与实现细节

- `load_dataset` 接收显式 CSV 和 metadata 路径，兼容 `label_column` / `description` 旧键和 dataset-name 包裹格式。必须明确 `task_type`，不根据名称猜回归。
- 显式声明的文本类别列按字符串读取，保留 `001` 等类别身份；显式数值或布尔类别域仍保留相应类型。CSV 的空白或重复表头在交给 pandas 前拒绝，避免 pandas 将复制的 target 自动改名为 `target.1` 后当作普通特征。
- Adult 的国家、资本收益/亏损、婚姻状态简化，以及 Anxiety 的三分类阈值保留为明确指定的 `cleaning` 模式；默认 `none`，不会偷偷改变原始研究对象。选择这些历史转换应在运行配置中保留。
- `split.metadata` 保存处理后全表 SHA256、实际 seed、各 split 的来源行位置和 train-only 描述；源码行位置指处理后表中的位置，清洗会改变它与原 CSV 行号的对应。
- 不去重真实或合成记录；论文未定义去重，重复比例也属于生成行为。测试边界按来源行互斥，值完全相同的不同真实记录仍可能进入不同 split。
- XGBoost 不可用时明确报错。另有显式的 random forest、logistic classification、ridge regression、MLP classification/regression 模型供附录或调试使用；不会自动用它们替代论文默认。MLP 按附录设定 `hidden_layer_sizes=(100,)`、`max_iter=500`，随机种子来自运行配置。
- Ridge 使用 dense SVD 求解相同的 L2 目标，避开旧版 sklearn 对新版 SciPy 已删除 `sym_pos` 参数的依赖；该选择不改变 alpha=1.0 的目标函数。
- Privacy 按合成数据 chunk 和逐列累加计算距离，避免一次构建“合成行 × 真实行 × 列”的三维数组；数学定义保持一致。
- 各指标返回原始量纲的数值，不在底层统一乘 100。只有展示层适合把 AUC/Privacy 等概率转为百分比。

## 验证

`tests/test_data.py` 与 `tests/test_evaluation.py` 覆盖：先 holdout 后 shot、分类分层与稀有类失败、回归不误分层、容量受限的 prompt 平衡、无全局 RNG 污染、训练类别域不接触测试集、显式清洗、训练预处理对测试值变化不敏感、三种下游协议、未知目标与多分类 AUC、实际 XGBoost 分类/回归、小样本 ties 的精确期望、等大小 references、缩放单位不变性、Hamming 与 chunk 一致性、signed Pearson、联合 TVD 和混合共享分箱。

## 多 seed 汇总协议

`structsynth.evaluation.reporting.summarize_runs(run_dirs)` 仅读取各目录的 `manifest.json`、`metrics.json`、`usage.json`，返回结构化报告；`write_summary(run_dirs, output_dir)` 写出 `summary.json` 和 tidy `summary.csv`，返回 JSON 路径，不修改原始运行。

- **相容组**包含实际 dataset/shot/n_samples、下游协议与模型、输入 CSV/metadata 指纹、完整代码指纹、依赖版本、整个 backend 身份以及其余配置。`data.seeds`、`data.shots`、输出位置和数据文件位置不影响已固定输入内容的单次实验，因此从兼容性键中移除；实际 shot/seed 仍来自 manifest。保留 generation 的整体 `n_samples` 计划，避免把不同最大生成规模的前缀实验默认视为相同。live、offline-demo、以及源 ledger hash 不同的 replay 分开汇总。
- **统计单位是 seed**。重复传入同一路径先去重。同 seed 多份有效结果完全一致时只计一次；同 seed 有不同有效结果时，该 seed 的所有性能指标排除，并明确标记 `duplicate_seed_conflict`，不选择较好结果、最新结果或将它们当作多次独立实验。只有一份有效结果而其他副本未完成时，可使用该有效结果一次；副本状态仍列出。
- **平均与离散度**仅在有限有效数值上计算 mean 和 sample standard deviation（`ddof=1`）。少于两个有效 seed 时 sample std 为 `null`；没有有效值时 mean 也为 `null`。每项均输出 `valid_count`、`missing_count`、逐 seed 缺失原因。使用原始指标量纲，不隐式乘 100。
- **不伪装完整实验**：仅完成 evaluation 且 manifest 状态为 complete 的指标可参与；缺文件、未完成、指标未定义、与配置的协议/模型不一致、metrics 文件与 manifest 中 checksum 不符均保留为缺失。无法建立输入/代码/环境身份的目录列于顶层 `excluded_runs`，不猜测其所属实验组。计划 seed 从 `manifest.requested_grid.seeds`（兼容旧配置中的 seeds）读取；未提供的计划 seed 单列 `missing_expected_seeds`，不冒充已执行实验的缺失观测。
- **白名单性能指标**为下游 AUC/R²/accuracy/macro-F1/MAE/RMSE、Privacy risk 与两侧平均最近距离、总体 fidelity。行数、pair count、seed、分箱边界等不求性能均值；`dcr` 和 `pairwise_correlation_diff` 兼容别名不会被重复算作独立指标。
- **成本分开汇总**：`requests` 是 ledger 记录数，只有 `api_requests` 表示实际 provider 调用，`replayed_requests` 表示重放。未知 token 不填 0；`sum` 在任何 seed 成本未知时为 `null`，另给 `known_sum` 和有效计数。成本对应整个生成运行（含最大请求 n），在各 n 分组里重复展示，不能跨 n 组累加。若同 seed 副本成本不同，成本单独标记冲突。
- **审查限制**：聚合只验证 manifest 已登记的 metrics checksum，不重新训练、重新计算指标或检验原始数据；没有登记 checksum 的指标明确标为 `not_recorded`。报告的输入范围由调用者提供，不自动递归扫描，也不自动产生置信区间或显著性结论。

`tests/test_reporting.py` 检查跨 seed sample std、单 seed、缺失及损坏结果、重复路径/seed、配置/模型/协议/源码/依赖/输入/backend 分组、未知 token 与 API 调用计数、JSON/CSV 输出和原始运行不被修改。
