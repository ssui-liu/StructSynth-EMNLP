# 图诱导、关联证据与生成顺序：实现决策

本轮依据 `Latex-EMNLP/sections/method.tex` 的 Evidence-Grounded Graph Induction / Graph-Planned Conditional Synthesis，以及 `sections/appendix.tex` 的 Association Scores、Algorithm 1 和三个图诱导提示词模板。以下解释与边界处理是便于检查的实现决策，不是新增实验结论。

| 论文要求或未规定处 | 本轮实现 | 检查位置 |
| --- | --- | --- |
| `V ⊆ A`；图初始化仅选入 source nodes | 图对象分别保存完整 `columns=A` 和显式 `nodes=V`。BFS 仅加入 source 和实际被提议发现的节点。 | `graph.py`, `discovery.py` |
| `A_iso = A \\ V` | 被选择但零度的节点仍在图内生成；未被选入的列才在最后补全。删边不删节点。 | `DependencyGraph.isolated_columns` |
| 拓扑层规定父节点必须先生成 | 使用确定性的 Kahn 拓扑代次，等价于根深度为 0、`depth(v)=1+max(depth(parent))`。发现 BFS 的最短距离不用于生成分层。 | `DependencyGraph.layers` |
| 局部结构为 `G[L ∪ parents(L)]` | 保留该节点集合内的全部边，包括父节点之间的边。父列及同层节点按数据列顺序排序。 | `DependencyGraph.local_subgraph` |
| source/link 提示词包含 few-shot examples | 两类请求都直接提供实际示例行，不使用会舍入小数的默认 DataFrame JSON 导出；调用方传入的示例必须按行值、JSON 类型及出现重数构成训练数据子集。未指定示例时取训练数据前至多 10 行；正式实验应显式保存、传入采样子集。 | `_prepare_examples`, `discover_structure` |
| 每次 link 请求使用当前图、关联及语义先验 | 请求包含全部候选字段/描述、已经验证的当前图、源节点与其余全部列的关联证据，以及固定 few-shot examples。目标列不特殊排除。 | `discover_structure` |
| 统计关联来自 `D_train` | 关联矩阵使用整个传入训练集，并对无向属性对只计算一次缓存。测试集、待生成数据均不参与。 | `association_evidence` |
| continuous-continuous 为归一化关联强度 | 使用绝对 Pearson `|r|`，保留负相关的强度；数值缩放避免有限大数溢出。 | `association_score` |
| categorical-categorical 使用论文偏差校正 Cramér V | 先计算未做 Yates 修正的 Pearson χ²，再逐项实现附录的 φ²、r、k 偏差修正。 | `association_score` |
| mixed 使用 correlation ratio η | 按类别均值的加权方差与总方差之比开方；类别始终承担分组角色，与输入列顺序无关。 | `association_score` |
| 论文未详细规定缺失值或退化统计量 | 每对独立排除缺失和连续列非有限值。样本不足、公式因常量导致零分母、偏差校正分母非正时，数值为 0，同时提供 `defined=false`、原因与有效样本数；提示词明确不能把 undefined 当作已测得的独立。η 在类别只有一个但连续列有方差时，仍按公式返回有效的 0。 | `AssociationScore` |
| 类别型字段可能用整数编码 | `DatasetSpec.categorical_columns` 与 boolean 声明优先于 dtype；分类任务目标总是作为类别型处理。独立使用关联工具且未传声明时才自动推断非数值/布尔列。 | `categorical_features` |
| 每轮候选边上检测所有 elementary cycles | 先批量纳入本轮有效提议，在完整候选图上枚举所有简单有向环，按列顺序规范化和排序；不是只检查某条最短路径。 | `discover_structure` |
| 每个环由 LLM 选择一条最弱边，取删除集合的并 | 严格校验返回边确实属于被询问的那个环且方向正确；即使前一次删边已打断另一个环，仍按论文伪代码对原始环集合逐环询问，然后取删除边并集。每次选择后记录全图是否仍有环，结束时再次验证整个 DAG。 | `cycle_edge_pruned` events |
| 论文未规定 cycle explosion | 默认单次扩展上限 1000 个环，可配置；超限立即失败，保留上一个有效 DAG，不接受部分修剪结果。最多扩展每个选中属性一次，内容重试也有上限。 | `max_cycles`, `DiscoveryError` |
| 论文未规定 malformed LLM responses | 整份响应必须通过校验后才修改图。不存在的属性、self edge、重复目标、空理由、错误删边、额外字段会提供错误反馈并重试；超过次数显式失败，不静默当作无依赖。Provider 网络重试与 token 记账由共享客户端完成；预算、配置、网络重试耗尽直接中止，但保留 `events` 与 `partial_graph` 到原异常类型。 | `ask`, `DiscoveryError.events` |
| 空 source 列表的含义未规定 | 允许模型明确返回空列表，此时 `V=∅`、所有列在 completion 生成；事件中记录。若模型输出格式错误或未知节点则重试/失败，不能与有效空列表混同。 | `validate_sources` |
| source 是否必须永久无入边未规定 | 将 source 视为初始化候选；后续 BFS 可以为它发现父节点，最终顺序由完成的 DAG 决定。不会额外强迫初始 roots 保持入度为零。 | `test_all_overlapping_cycles_are_resolved_with_each_new_edge_in_prompt` |
| 旧 artifact 的节点范围与层级不可靠 | 新版本要求显式 `nodes`。加载旧格式时保留其中显式 V，不按 degree 猜测意图；忽略旧 `hierarchical_structure`/持久化 layers 并重算。缺少完整列 schema 时要求调用方给出。若旧流程预填充了全部列，需重新运行 discovery 才能恢复论文的选择语义。 | `DependencyGraph.from_dict` |

图版本为 `schema_version=1`。这是生成用依赖计划，不是因果识别结果；新提示词避免把无向关联或边方向描述成已识别的因果关系。

回归测试覆盖长短路径同时存在时的错误 BFS 分层、零度选中节点、局部诱导子图、旧层级损坏、关联公式及退化输入、few-shot 子集约束、多个共享路径环、非法删边、重复/自环提议、空 source、重试/环数量上限及不可重试预算错误。此阶段仅使用离线脚本化响应，未调用真实付费模型，也未据此宣称恢复论文实验指标。
