# StructSynth 论文对齐重构记录

本文记录截至 `9cb138c` 的 0.2.0 重构。后续按用户要求进行的 0.2.1 目录模块化，
见[模块化记录](MODULARIZATION.md)和[代码导航](../../StructSynth-Code/src/structsynth/README.md)。

本次重构把论文中的两阶段方法落实为可安装、可测试、可追踪的研究代码。用户于 2026 年 10 月 4 日授权基于 Git 的破坏式优化和多 agent 开发，并授权按论文与工程判断处理不确定项。本文记录实现范围、复核入口和验证证据。

## 基线与范围

- 开发分支：`codex/structsynth-paper-refactor`。
- 代码基线：`47d8570`，该提交下 `StructSynth-Code/` 在开始重构时无本地改动；可通过 Git 恢复旧代码。
- 论文依据：工作区 `Latex-EMNLP/sections/method.tex`、`appendix.tex`、`experiments.tex`，与 `Latex-arXiv` 方法正文交叉核对。工作区中未提交的论文改动保留原状；论文来源指纹见 `paper_sources.json`。
- 实施范围：`StructSynth-Code/` 与 `.github/workflows/structsynth.yml`；论文、审稿记录和已有实验结果不作为本次代码提交的修改对象。
- 目标是与方法定义一致的可运行实现。没有重跑原论文全部实验，因此不能宣称恢复或提升了论文报告的指标。

## 迭代顺序与验收

本轮五步均已完成。原 37 个生产 Python 文件、6542 行，收拢为 16 个包模块加 3 个薄入口，
共 3649 行；测试和决策文档单独维护。完整验收为 321 项测试、十 seed Adult 离线流程和独立 wheel 运行。

1. 固定论文语义和共享接口。明确 selected graph nodes、图外属性、全部已生成条件、拓扑层次、augmentation 协议。
2. 重写图学习、生成和评估核心。用针对既有错误的反例验证，覆盖多路径 DAG、循环、部分响应、重试、类别边界和测试集隔离。
3. 集成统一 CLI、配置、请求账本、原子产物、运行标识和检查点。验证配置相对路径与重复运行行为。
4. 用离线模型替身跑通完整流程；安装包后验证入口、构建、依赖和测试。离线替身结果仅证明工程链路，不作为生成质量证据。
5. 第二轮交叉审查故障恢复和论文一致性，修复后按阶段提交，记录剩余研究验证工作。

## 需要作者重点复核的解释

| 问题 | 本次选择 | 依据或性质 |
|---|---|---|
| DAG 是否声称真实因果关系 | 公共接口和提示词使用 dependency graph | 论文明确其用途是生成计划 |
| 生成条件范围 | 全部已生成字段，配合当前层及其父节点的诱导子图 | 方法正文公式中的 x 小于 i；优先于旧代码仅传直接父列 |
| 图外字段 | A 减 V，最后统一补全；被选入 V 的零度节点仍是根节点 | 方法与算法中的集合定义 |
| 环处理 | 一轮候选边加入后检查所有 elementary cycles；删边必须来自当前冲突且最终仍需 DAG 验证 | 论文算法；超出可计算规模显式失败 |
| 默认超参数 | 两阶段均采用附录 LLM 参数；独立配置允许改动并留痕 | 旧配置与论文参数不同，选择论文 |
| 隐私距离 | 默认原始数值 L1 加类别 Hamming，不擅自归一化 | 附录明确公式 |
| 隐私最近邻并列 | 对并列最近邻的训练归属取均匀期望 | 论文未指定，工程解释；避免数据拼接顺序造成偏置 |
| 混合 fidelity 分箱 | 用真实参照数据的共同分位点映射两组数据 | 论文未指定分箱边界来源，工程解释 |
| 预处理 | 训练侧拟合，测试侧仅转换 | 避免旧实现根据测试类别改变训练数据 |
| LLM 框架 | 用小型 OpenAI-compatible JSON 边界替代重复 LangChain 包装 | 工程替换，非方法创新；不保证新旧提示词产生相同样本 |
| 样本规模间关系 | 每个 seed 生成最大规模，再用前缀评价不同规模 | 减少重复请求；论文未规定必须独立生成，需作为配对结果分析 |
| 运行前本地基线 | 在任何 LLM 请求前拟合 real-only 预测模型并保存指标 | 检查依赖、模型参数和数据可用性；主实验仍使用配置中的协议 |
| 多 seed 汇总 | 相同协议、源码、环境、数据和模型才合并；输出有效数和缺失原因 | 避免把重复 seed 或离线结果当独立真实模型证据 |

各模块的详细决定与边界条件见公开代码目录中的[图诱导](../../StructSynth-Code/docs/decisions_graph.md)、
[生成](../../StructSynth-Code/docs/decisions_generation.md)和[评估](../../StructSynth-Code/docs/decisions_evaluation.md)。
迁移与旧代码检查见 `MIGRATION.md`；本轮实测证据、剩余研究验证边界见 `VALIDATION.md`。

## 外部接口依据

请求字段与 JSON 响应模式按 [OpenAI Chat Completions API 文档](https://developers.openai.com/api/reference/resources/chat)核对。包结构采用 [Python Packaging 的 pyproject.toml 指南](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)。兼容端点必须自行支持所配置的模型和字段；代码不会静默丢弃不支持的参数或替换模型。
