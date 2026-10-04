# StructSynth 内部开发记录

这里保留论文对齐重构、模块化和本地验收记录，供作者检查；不属于
`StructSynth-Code/` 的公开代码目录，也不进入 wheel 或源码分发包。

- [论文对齐重构](REFACTOR_PLAN.md)
- [旧代码迁移](MIGRATION.md)
- [0.2.0 验证记录](VALIDATION.md)
- [0.2.1 模块化记录](MODULARIZATION.md)
- [核对论文的来源指纹](paper_sources.json)
- [原本地验证环境快照](constraints-tested-py311.txt)

方法定义与实现选择仍作为公开文档保留在
[`StructSynth-Code/docs/`](../../StructSynth-Code/docs/)，代码导航见
[`src/structsynth/README.md`](../../StructSynth-Code/src/structsynth/README.md)。

## 2026-10-04 开源目录整理

基线：`fbc839a`；分支：`codex/structsynth-paper-refactor`。
本轮按用户要求整理公开目录，包版本仍为 0.2.1。

| 原位置 | 处理 |
|---|---|
| 根目录三个 `run_*.py` | 移到 `scripts/`，仍委托统一 CLI；补充脚本使用说明 |
| `docs/REFACTOR_PLAN.md`、`MIGRATION.md`、`MODULARIZATION.md`、`VALIDATION.md`、`paper_sources.json` | 移到本目录，修正文档链接并标记已清理的历史产物 |
| `constraints-tested-py311.txt` | 随验证记录归档；它是特定 macOS / Python 环境快照，公开依赖仍由 `pyproject.toml` 定义 |
| `results/` | 删除旧演示图和生成表；它们不属于当前实现的可复现实验输出，历史内容保留在 Git |
| `runs/` | 清理 15 份已完成的离线 demo、bootstrap 验证及 replay 运行；删除前逐份核对 manifest 的状态与 backend |
| `dist/`、缓存、`src/structsynth.egg-info/`、`.DS_Store` | 删除生成文件；完善忽略规则 |
| `.venv/` | 保留本地开发环境，继续排除在 Git 和发布包之外 |

首次清理共移除 3,639 个生成或历史结果文件，约 66.66 MiB。
构建验证临时产生的元信息在验收后清理；新的验证输出和安装包均写到临时目录并自动移除。
README、CI 的 Ruff 路径和 `MANIFEST.in` 同步到 `scripts/`。
公开方法说明去除本地论文路径和开发过程叙述，保留方法选择与测试覆盖说明。

## 验证

- Python 3.11 项目环境：`pytest -q -p no:cacheprovider`，**323 passed**。
- `ruff check --no-cache src tests scripts` 与 `pip check` 通过。
- 三个脚本在项目根目录与外部工作目录的 `--help` 均可运行。
- 从外部工作目录依次执行三个脚本，以离线日志完成 split、discover、generate，
  再通过 CLI 执行 XGBoost 评估；生成 JSON 和指标与源 demo 逐字节一致，新增 API 请求为零。
- wheel 与 sdist 构建成功；sdist 包含三个脚本、配置、数据及公开方法说明，
  wheel 的 46 个 Python 文件与源码逐字节一致；两种分发包都不含内部记录或本地产物。
- 独立 agent 只读检查脚本引用、CI、打包配置及清理边界；本地文档链接检查通过。
- 包内 Python 源码未变，源码指纹仍为
  `b10916759b8810adcf4840a41d7c74b99e5fcb919c2b0f1d400c011da9ab6923`。

需要检查被删除的已跟踪历史结果时，可在仓库根目录使用：

```bash
git ls-tree -r --name-only fbc839a -- StructSynth-Code/results
git show fbc839a:StructSynth-Code/results/structure_graph/adult/gpt_4o_mini/graph.json
```

`runs/` 中的离线输出原本不受 Git 跟踪，清理后不能通过 Git 恢复。
旧验证记录保留历史执行结论；本次验证仅说明整理后的工程行为正确。

## 2026-10-04 安装与打包配置精简

基线：`f21b161`。根据用户对根目录四个配置文件的整理要求，保留两个职责明确的文件：

| 文件 | 处理与理由 |
|---|---|
| `pyproject.toml` | 保留在项目根目录，统一依赖、可选 extras、CLI、wheel 和开发工具配置；包发现仅限 `structsynth` 与子包，关闭隐式 namespace 扫描，显式打包代码导航 |
| `MANIFEST.in` | 保留在项目根目录，精简为源码分发包所需的脚本、配置、方法说明、测试和 Adult 输入；不再递归纳入整目录中的任意文件类型 |
| `requirements.txt` | 删除；原内容只是 `-e .[evaluation]`，不含独立依赖。原 `pip install -r requirements.txt` 改为 `python -m pip install -e '.[evaluation]'` |
| `env.example` | 删除；原文件只有环境变量 export 示例，现集中说明在 README。运行时仍从 `api_key_env` 指定的环境变量读取密钥 |

README 分别列出基础、论文评估和开发安装命令，注明 `.env` 不自动加载；删除无用的
`.gitignore` 示例文件例外。运行时依赖、模型参数、Python 下限和包版本保持不变。

构建依赖下限由 `setuptools>=61` 修正为 `>=64`，覆盖文档采用的 PEP 660 editable 安装。
官方 [setuptools 64.0.0 更新记录](https://setuptools.pypa.io/en/latest/history.html#v64-0-0)
说明该版本引入 editable hooks；[pip 21.3 更新记录](https://pip.pypa.io/en/stable/news/#v21-3)
说明前端支持。因此 README 在创建虚拟环境后先更新 pip。
保留 MANIFEST 的依据见 [setuptools 源码分发文件规则](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html)。

验证：323 项测试、Ruff 和依赖检查通过；wheel、sdist 与 editable 安装成功。
源码包包含全部公开资产，wheel 的 46 个 Python 文件与当前源码逐字节一致。
从临时 wheel 安装目录执行控制台入口、XGBoost 离线 demo 和续跑均通过；editable 导入
确认来自独立临时源码副本。构建下限调整后重新验证分发包与 editable 安装。
独立 agent 完成引用与构建兼容性复核；全部构建和安装检查使用临时目录，不产生项目内杂项。
