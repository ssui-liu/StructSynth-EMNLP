# 从旧演示代码迁移

本轮以 `47d8570` 为旧代码基线，在 `codex/structsynth-paper-refactor` 分支实施破坏式整理。
旧结果和原始 Adult 数据保留；旧实现从默认代码路径移除，避免同时维护两个语义不同的工作流。
论文文件与已有论文改动不属于本轮修改。

## 文件与入口映射

| 旧位置 | 新位置或入口 | 变化 |
|---|---|---|
| `data/utils.py` | `src/structsynth/data/` | 明确 task/schema，先 holdout 后 shot，保存来源行身份 |
| `structure_learning/` | `src/structsynth/structure/` | 单一图合同，统计证据与 LLM 诱导分开 |
| `data_generation/models/` | `generation/`、`llm/` | 稳定 row_id、全部已有条件、严格校验与可恢复批次 |
| `data_generation/evaluation/` | `evaluation/` | 统一协议与指标、缺失原因、多 seed 汇总 |
| `config/*.json`、旧 YAML | `configs/adult.yaml` | 统一 version-1 配置；未知字段显式报错 |
| 三个 `run_*.py` | 同名薄入口或 `structsynth` CLI | 新配置格式；不再有脚本内硬编码路径和默认数据集 |
| 冗长环境导出 `requirements.txt` | `pyproject.toml` + 可选 extras | 基础算法依赖、XGBoost 评估依赖、开发工具分开 |
| `.idea/` | 不再跟踪 | 本地 IDE 状态不属于研究代码 |

旧内部 Python import 不继续兼容。安装包之后从 `structsynth` 导入新 API。
这里的“旧内部”指 `47d8570` 中的 `data_generation` 和 `structure_learning` 包。
0.2.0 到 0.2.1 的进一步模块化保留 `structsynth` 已有公共导入，详见
[代码导航](../src/structsynth/README.md)和[模块化记录](MODULARIZATION.md)。
旧 JSON 图可以由 `DependencyGraph.from_dict(..., columns=...)` 显式读取，忽略旧缓存层级并重算；
新 CLI 不自动把历史图或 CSV 当成当前版本的已完成实验。旧实现若把所有列预填入图，
其节点语义无法从度数可靠恢复，应重新诱导。

## 会改变实验结果的调整

- 拓扑层按全部父节点计算，替代 BFS 最短距离；所有已生成列共同条件化。
- 图外列严格为 `A - V`，零度选中节点保留在图内；循环处理覆盖全部 elementary cycles。
- few-shot 语境示例与有限真实训练集分开；关联统计使用后者全部行。
- 默认下游协议改正为真实训练数据加合成数据。真实数据基线另存，不计入主方法效果。
- 两阶段默认温度统一为附录的 0.9；top_p=0.95、max_tokens=8000。模型端点不静默替换参数。
- 分类特征的未见类别不会仅因未在 few-shot 出现而被拒绝；显式域和分类目标仍闭域。
- Privacy 按论文默认使用未归一化数值 L1；最近邻并列采用均匀期望归属。
- Fidelity 数值项使用带符号 Pearson 之差；混合项共享真实参照分箱；默认参照为 train ∪ test。
- 批量规模间使用同一次生成的前缀。统计比较需要考虑这种配对关系。

这些变化修复旧实现与论文之间的偏差，但不是指标提升的证据。提示词、输出协议、
预处理和模型版本均可能影响结果；历史 `results/` 不能当成新实现的基准验收数值。

## 运行身份与恢复

每个 run 绑定实际 shot/seed、配置、原始数据和元信息内容、包源码及 Python/依赖版本。
命令中的 shots/seeds 选择范围单独保存；选择单 seed 不会创建一个新的同义实验。
更改配置、代码或依赖会创建新 run，而不是把旧检查点强行套到新实验。

`--resume` 校验完成产物和已完成阶段的请求日志。失败日志保存长度及前缀哈希水位，
允许中断后追加，不允许丢失已知请求记录。请求发出前写入 durable reservation；
请求完成前进程退出时，其用量保持 unknown。恢复不会免费重置请求或生成尝试预算。

生成支持批次/层检查点；图诱导目前只复用已完整完成的 graph 阶段。
图诱导中断时重新遍历，但沿用原账本预算，错误和 partial graph 供人工检查。
并发批次只在同一拓扑层执行。LLM 的 seed 只用于实验追踪，不保证远端确定性。

离线回放绑定源账本哈希；OpenAI-compatible 源日志还必须匹配当前两阶段模型配置。
回放保存原响应与原用量作为来源，新增 API 次数和 token 消耗为零，不与 live 运行混报。

## 检查与找回旧实现

在仓库根目录审查变更：

```bash
git diff --stat 47d8570 -- StructSynth-Code .github/workflows/structsynth.yml
git log --oneline -- StructSynth-Code .github/workflows/structsynth.yml
git show 47d8570:StructSynth-Code/run_data_generation.py
```

需要运行旧版时，可在新目录建立独立 detached worktree：

```bash
git worktree add --detach ../structsynth-before-refactor 47d8570
```

这些检查方式不覆盖当前工作区的论文改动。旧版依赖和旧流程缺陷仍按基线原样保留。
