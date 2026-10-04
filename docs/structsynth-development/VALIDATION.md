# 本轮开发验证记录

本节对应 0.2.0 的论文对齐重构。0.2.1 模块化后的测试、安装包与跨版本回放验证，
见[模块化记录](MODULARIZATION.md)。

日期：2026-10-04。分支：`codex/structsynth-paper-refactor`。
核心实现提交：`06bba68`；图诱导提交：`2411bc4`；初始合同与配置：`ec97095`。
最后的迁移/打包提交可通过 `git log --oneline -- StructSynth-Code` 查看。

测试对应的包源码指纹（`pipeline.source_fingerprint()`）：

```text
18e47a05eec84d051813c58bd69dd67b89a673fb64e1954b98188f2e568c446d
```

## 实测结果

| 检查 | 结果 | 范围 |
|---|---|---|
| Python 3.11.9 项目虚拟环境完整测试 | **321 passed** | 含真实本地 XGBoost 分类/回归、完整 CLI 回放、真实子进程崩溃 |
| Python 3.9.7 现有环境完整测试 | **319 passed, 2 skipped** | 仅跳过未安装 XGBoost 的两项；旧依赖的 5 条弃用警告未改动全局环境 |
| Ruff | **通过** | `src`、`tests`、三个兼容入口 |
| pip dependency check | **通过** | 项目 `.venv` 中无损坏依赖 |
| 构建 | **wheel 与 sdist 成功** | `python -m build --no-isolation`；sdist 含配置、文档、测试与 Adult 输入 |
| wheel 独立导入 | **通过** | `pip --no-deps --no-index --target` 安装到临时目录，从 `/private/tmp` 启动并断言模块来自安装目标 |
| wheel 完整工作流 | **通过** | XGBoost 离线 demo、双 worker、原样续跑 |
| Adult 完整配置离线验收 | **10/10 seeds 成功** | 42–51；100 shot；每 seed 1000 行；100/200/500/1000 四档真实本地评价 |
| Adult 多 seed 汇总 | **4 组，每组 10 个有效 seed** | AUC、privacy、fidelity 均可汇总，sample std 有效，无缺失 seed |
| Adult 单 seed 续跑 | **通过** | 从十 seed 配置选择 seed 42，复用原目录；禁止创建模型客户端；日志及指标哈希不变 |
| 论文/历史输入保护 | **通过** | 4 份论文来源哈希与开始时一致；原始 Adult 输入和历史 results 对基线无 diff |

所有 LLM 请求在本轮验证中由本地 transport/脚本化响应/离线替身完成。没有发送真实模型 API 请求。
离线 Adult 替身会复制训练行；10,000 行合成输出和 40 组评价只证明软件流程与规模处理正确，
不属于新模型结果，也不代表隐私保护或数据质量达标。

## 历史本地检查产物

以下离线产物原位于被 Git 忽略的 `StructSynth-Code/runs/`，已在后续开源目录整理时清理。
这些路径仅记录当时的验证位置，未提交为论文结果，也不再作为可点击的检查入口：

- Adult 十 seed 汇总：`validation-adult/summaries/a674cf73379f6c2a/summary.{json,csv}`。
- Adult seed 42：`validation-adult/adult/100_shot/seed_42/2563b60955f454e1/manifest.json`。
- 独立 wheel：`validation-wheel/offline_demo/20_shot/seed_42/2788d76badb31914/manifest.json`。

原验证依赖版本见[环境快照](constraints-tested-py311.txt)。原 `dist/` 构建产物也已清理。
上述“实测结果”保留原开发轮次的结论，不代表这些临时文件仍然存在。

## 交叉审查修复的具体问题

三名 agent 分别负责图诱导、生成、数据/评价；随后交叉检查共享协议及恢复路径。
除方法对齐外，第二轮反例驱动审查修复了：

1. 进程退出后请求预算丢失；请求先写入持久化 reservation，用量未知时保留 unknown。
2. JSONL 尾部只写完一部分、甚至 UTF-8 字符写到一半时无法恢复；仅修复不完整末行，完整损坏记录仍报错。
3. HTTP 重试期间耗尽预算后，离线回放抛出不同的错误；保留真正的终止原因。
4. 生成耗尽后没有顶层失败事件；现在保留 `failure_details.json` 与检查点。
5. 从多 seed 配置选单 seed 续跑产生新 run；将运行网格从单次实验身份中移出。
6. 账本被删除或清空后续跑把用量归零；检查 started journals、完成阶段哈希与失败前缀水位。
7. 非法评价参数直到付费生成后才失败；先执行并保存本地 real-only 基线。
8. 回放的源模型与当前声明模型不符仍被接受；核验源配置，并将源日志哈希写入 backend 身份。
9. Provider 返回的实际模型 snapshot 丢失；记录 requested/resolved model 和可选 system fingerprint。
10. 数值类别中的整数 `1` 与浮点枚举 `1.0` 被误判不相等；采用 JSON number 等价，同时继续区分布尔和整数输出类型。

## 尚未建立的研究结论与已知边界

- 尚未进行真实 LLM 的质量/成本实验，未重跑六数据集、基线、消融或 SHD 实验，不宣称复现或提高论文表格指标。
- 论文未明确的选择集中记录在 `StructSynth-Code/docs/decisions_*.md`，特别是生成的全部已有条件、privacy ties、fidelity 真实参照与分箱来源。
- 远端模型 alias 可能变化，seed 也不保证确定性；journal 保存实际响应和 provider 提供的版本字段。
- 请求次数是硬上限；token limit 是按已报告用量阻止后续请求，不是预付费硬封顶。
- 生成有逐层/批次恢复；未完成的 discovery 会重新遍历并沿用预算。回放要求记录的请求与当前执行匹配，缺失或无法匹配时显式失败。
- 多 seed 汇总中的成本属于整次最大规模生成，随每个规模组重复展示，不能跨规模相加。
- GitHub Actions 工作流已配置；本轮只执行本地检查，尚未有远端 CI 运行结果。
