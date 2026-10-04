# 0.2.1 模块化记录

本轮按用户要求，将 `src/structsynth` 从单层文件结构改为六个功能子包，方便阅读和维护。
基线为 `9cb138c`（0.2.0）；继续使用 `codex/structsynth-paper-refactor` 分支。
方法、指标、默认参数和模型请求协议保持原义，新增版本号为 0.2.1。

## 组织变化

| 原位置 | 新实现位置 | 拆分依据 |
|---|---|---|
| `data.py` | `data/loading.py`、`validation.py`、`metadata.py`、`sampling.py` | 文件读取、合同检查、训练元信息和抽样各自管理 |
| `associations.py`、`graph.py`、`discovery.py` | `structure/` | 集中论文第一阶段；提示词独立放在 `prompts.py` |
| `generation.py` | `generation/` | 主控、阶段计划、请求构造、校验、检查点、序列化和异常分开 |
| `llm.py` | `llm/` | 合同、HTTP 客户端、账本、解析和回放分开 |
| `evaluation.py`、`reporting.py` | `evaluation/` | 预处理、三个指标维度、公共表示和汇总分开 |
| `pipeline.py` | `pipeline/identity.py`、`evaluation.py`、`runner.py` | 实验身份、评价产物和阶段编排分开 |

保留共享的 `config.py`、`schema.py`、`artifacts.py`；命令入口和离线示例仍为 `cli.py`、`demo.py`。
生成主控从原单文件 581 行中抽出为 214 行，其余责任由显式参数的辅助函数承担，未使用 mixin
或把整个生成器传给工具函数。图诱导流程仍集中阅读，关联、图合同与提示词可以独立修改。

详细目录、推荐阅读顺序与“改什么就看哪里”见[包内代码导航](../../StructSynth-Code/src/structsynth/README.md)。
该导航随 wheel 一起分发。

## 兼容与实验身份

- `structsynth.data`、`generation`、`llm`、`evaluation`、`pipeline` 从文件变为同名包，
  `__init__.py` 显式导出原有公共类、函数和常量。
- 原 `structsynth.graph`、`associations`、`discovery`、`reporting` 保留静态兼容导出，
  与新位置引用同一对象。包内部使用规范实现路径；没有动态别名或第二份实现。
- 内部辅助函数的位置不属于稳定 API。原测试中基线拟合的 monkeypatch 挂载点随实现移到
  `structsynth.pipeline.evaluation.evaluate_downstream`，测试原意保持不变。
- 源码指纹现在递归读取所有 `.py`，按包内相对 POSIX 路径建立映射；子包中的同名文件不会
  覆盖彼此，安装位置、Markdown 文档和 `.pyc` 缓存不影响指纹。
- 生成器的 prompt/checkpoint version 均保持原值，等价输入的生成检查点仍可恢复。
  **整次实验的 run identity 还绑定源码，因此升级后会使用新的运行目录。** `--resume` 不会把
  0.2.0 整次实验当作新源码下的已完成实验；需要复用原响应时使用 `--replay-dir`。

本轮包源码指纹：

```text
b10916759b8810adcf4840a41d7c74b99e5fcb919c2b0f1d400c011da9ab6923
```

## 验证证据

- Python 3.11 项目环境：**323 passed**；Python 3.9 现有环境：**321 passed, 2 skipped**，
  跳过项仍仅为该环境未安装 XGBoost 的两个测试。
- Ruff 全部通过。新增两个回归测试保护递归源码身份和旧/新图与汇总 API 的对象一致性。
- 数据、评估、汇总、LLM、图和关联中的搬移定义通过 AST 等价比对。
- 生成器使用拆分前记录的黄金产物验证：完整请求及 key、检查点原始字节、生成数据及 dtype、
  首次执行与恢复事件一致；旧检查点可在不调用客户端的情况下恢复。
- 0.2.0 的完整离线日志由 0.2.1 回放：两阶段请求 key 集合一致，split、schema、graph、
  examples、train/test、synthetic、baseline 和 metrics 文件逐字节一致；新增 API 次数为零。
- wheel 与 sdist 构建成功。wheel 的 46 个 Python 文件与源码逐字节一致，并包含代码导航。
  从工作区外独立导入 wheel，六个子包、源码指纹、本地 XGBoost 完整 demo 和续跑均通过。

回放产物原位于工作区被 Git 忽略的目录（已在后续开源目录整理时清理）：
`runs/modularization-0.2.1/offline_demo/20_shot/seed_42/2b7d628bf777fc79/`。
这轮验证针对组织变化的兼容性，不构成新的模型质量或性能结论。
