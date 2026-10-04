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

## 2026-10-04 README 与 camera-ready 论文对齐

基线：`5c67377`。依据用户指定的 `EMNLP26_StructSynth_Camera_Ready.pdf`（27 页）
重写公开 README；PDF SHA256 为
`d6cb7f0c4e9db57759ba83de4897d45481088eb29bb99e89e50f0f5b8ff4f07c`。
本次仅修改文档，源码与实验配置未调整。

- 第 1 页：使用当前论文标题和四位作者姓名。引用仅列标题、作者和 Manuscript，
  未根据文件名补造发表年份、录用状态、DOI 或 arXiv 编号。
- 第 4–5 页、Algorithm 1：突出依赖图作为生成计划，以及图诱导、拓扑层生成、
  全部已生成值作为条件、局部父节点子图和图外补全；补充 Mermaid 流程图。
- 第 5 页 Table 1：逐项核对六数据集的 real-only 与 StructSynth 均值、标准差和任务类型。
  明确分类 AUC、回归 R² 及该表乘 100 的展示方式。
- 第 7 页 Table 2：准确限定 14 个生成器中的效用平均排名 1.00、隐私排名 1.50、
  fidelity error 排名 9.50；隐私按偏离 0.5 排名，不扩大为形式化隐私保证。
- 第 6 页 Implementation Details：记录 100-shot 时论文默认 `D_few_shot = D_train`。
  README 明示当前 `example_rows: 20`，并说明改为 100；当前多规模前缀评价是工程选择，
  主实验只评价 1,000 行时可将 `generation.n_samples` 设为 `[1000]`。
- 区分论文报告结果、当前 Adult 示例和离线工程验证；整理安装、分阶段运行、恢复、
  回放、汇总与开发入口，补充 CLI 覆盖参数及配置变化对应新运行目录的准确说明。

两名 agent 分别完成论文事实和使用说明复核。可执行检查覆盖：11 段代码块的结构、
11 条 CLI 示例的参数、14 个链接或页内锚点、JSON 与 shell 语法；Pandoc 按 GitHub Markdown
解析得到 3 张表（6/3/7 行）。原配置和文档说明的 100 条 prompt / 1,000 条生成配置均通过
`plan` 检查，未请求模型或创建运行目录。PDF 第 1、3、5、7 页经渲染核对。
本次为文档变更，未重复运行算法测试或实验；临时提取、页面渲染与 HTML 预览在检查后清理。

随后按用户反馈精简 README：移除论文结果表、方法展开、指标解释、元数据示例、
恢复与回放机制及打包细节，保留项目定位、安装、快速运行、代码导航和引用。
仅保留影响运行的配置差异说明（20/100 条 prompt 示例及 1,000 条生成设置）；
方法与实验细节引导读者查看论文，模块细节链接到已有代码导航。
