# Level 10 审计报告：EMNLP / ACL Specific Requirements

## 1. 标题与范围

本报告独立审计 `Latex-EMNLP` 论文对 Writing Checklist Level 10 的符合情况，范围限定为 `Audit/writing_checklist.md` 中 10.1--10.3 的 EMNLP / ACL 特定要求：review-mode 匿名化、作者/单位暴露、自识别链接、limitations/ethics/reproducibility、超参数、计算成本，以及 Responsible NLP checklist 准备度。

## 2. 判定摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 10.1 Anonymization | 部分通过，但有高风险 | `main.tex` 已使用 `\usepackage[review]{acl}`，ACL 样式会将作者显示为匿名；但源码中仍保留作者姓名、单位、邮箱和 `\thanks{Corresponding author.}`，若提交源码/补充材料会直接破坏匿名性。 |
| 10.2 Ethics & reproducibility | 部分通过 | 有实质性 Limitations、算法、prompt、随机种子、超参数和 token overhead；但缺少独立 Ethics Statement，缺少数据许可/PII/敏感属性/滥用风险说明，计算成本只报告 token，未报告硬件、GPU/CPU 时间、实际 API 成本或环境成本。 |
| 10.3 Responsible NLP checklist | 未通过 / 未准备好 | 在允许范围内未发现 Responsible NLP checklist、ethics/checklist/impact statement 相关章节或文件；现有正文不足以支撑 checklist 中关于数据、伦理、计算、复现、风险的 “yes” 回答。 |

总体结论：论文接近 ACL review 格式，但尚未达到 Level 10 readiness；最需要优先修复的是匿名源码、伦理声明和 Responsible NLP checklist。

## 3. 优点

- Review 模式已开启：`Latex-EMNLP/main.tex:18` 使用 `\usepackage[review]{acl}`，符合清单 `Audit/writing_checklist.md:358`。
- ACL 样式在 review 模式下会启用匿名与行号：`Latex-EMNLP/acl.sty:18-20` 定义 `review` 为 anonymize/line numbers；`Latex-EMNLP/acl.sty:131-134` 在匿名时输出 `Anonymous ACL submission`。
- Limitations 不是空泛占位，覆盖 LLM semantic prior、DAG assumption、LLM API dependence：`Latex-EMNLP/sections/limitations.tex:3-14`。
- 复现实验要素较丰富：主文说明 `gpt-4o-mini`、temperature、`n=100`、`s=1000`、10 次重复与均值/标准差，见 `Latex-EMNLP/sections/experiments.tex:13-15`；附录报告随机种子 42--51，见 `Latex-EMNLP/sections/appendix.tex:181-183`。
- 附录包含算法、prompt、数据集表、超参数表和 token usage 表：算法见 `Latex-EMNLP/sections/appendix.tex:85-156`，prompt 模板见 `Latex-EMNLP/sections/appendix.tex:485-803`，超参数见 `Latex-EMNLP/sections/appendix.tex:189-230`，token overhead 见 `Latex-EMNLP/sections/appendix.tex:392-442`。

## 4. 问题（按严重程度排序）

### S1. 匿名提交源码暴露作者、单位、邮箱和 corresponding-author 信息

证据：`Latex-EMNLP/main.tex:93-103` 明文列出 Siyi Liu、Yujia Zheng、Yongqi Zhang、两所机构和邮箱；`Latex-EMNLP/main.tex:100` 还包含 `\thanks{Corresponding author.}`。虽然 `Latex-EMNLP/acl.sty:131-134` 会在匿名模式下隐藏 PDF 作者行，但 `Latex-EMNLP/acl.sty:144` 仍会输出 `\@thanks`，因此应核查是否出现匿名版孤立脚注。若 EMNLP/ACL review 系统要求上传源码、appendix source 或 supplementary zip，这些内容会直接违反 `Audit/writing_checklist.md:359-362`。

### S1. 缺少 Ethics Statement 和 Responsible NLP checklist 材料

证据：Level 10 明确要求 ethics/reproducibility 与 Responsible NLP checklist，见 `Audit/writing_checklist.md:364-373`。在允许范围内检索 `ethic|responsible|checklist|impact statement|broader impact` 无命中；`Latex-EMNLP/main.tex:118-123` 只输入 introduction、related work、method、experiments、conclusion、limitations，没有 ethics/checklist 章节。

### S2. 数据隐私、敏感属性、公平性和误用风险只被实验指标间接覆盖

证据：论文使用 Adult、Anxiety、Compas、Obesity 等社会、医疗/健康、犯罪领域数据集，见 `Latex-EMNLP/sections/experiments.tex:4` 与 `Latex-EMNLP/sections/appendix.tex:169-176`。隐私风险指标定义较清楚，见 `Latex-EMNLP/sections/experiments.tex:11` 和 `Latex-EMNLP/sections/appendix.tex:245-261`；结果也讨论 memorization，见 `Latex-EMNLP/sections/experiments.tex:90`。但没有说明数据许可证/使用条款、是否含 PII 或敏感属性、是否需要 IRB/consent、生成这些领域样本的滥用风险，以及用 LLM API 处理 few-shot rows 的数据治理。Prompt 示例还直接使用 `Sex`、`Race`、`Native country` 等敏感或近似敏感字段，见 `Latex-EMNLP/sections/appendix.tex:524-531` 与 `Latex-EMNLP/sections/appendix.tex:540-544`。

### S2. 复现性仍受商业 LLM API、代码缺失和版本缺失影响

证据：Limitations 承认当前实现依赖 commercial LLM APIs，API version updates 会影响精确复现，见 `Latex-EMNLP/sections/limitations.tex:12-14`。正文和附录给出模型名、temperature、top_p、max_tokens 等，见 `Latex-EMNLP/sections/experiments.tex:15` 与 `Latex-EMNLP/sections/appendix.tex:201-205`；但未给出 API 版本/调用日期、完整软件版本、数据预处理脚本、匿名代码仓库或代码发布承诺。在允许范围内检索 code release / repository / anonymous repository 等未发现代码发布承诺。

### S2. 计算成本不满足 ACL/EMNLP 可复现披露预期

证据：论文报告 token usage：CLLM 平均 219.8K tokens，StructSynth 平均 287.9K tokens，overhead +31.0%，见 `Latex-EMNLP/sections/appendix.tex:395-403` 与 `Latex-EMNLP/sections/appendix.tex:431-442`。这有助于估算 LLM API 成本，但清单要求 computational cost，见 `Audit/writing_checklist.md:369`；目前未报告硬件、GPU/CPU 型号、GPU/CPU hours、wall-clock time、API 单价/总花费或深度生成基线训练成本。

### S3. 基线和默认超参数可能随库版本漂移

证据：附录说明除 CuratedLLM 外，基线使用 SynthCity 默认配置，见 `Latex-EMNLP/sections/appendix.tex:187`；实现使用 Langchain 和 Causal-Learn，见 `Latex-EMNLP/sections/appendix.tex:191`。但未固定 SynthCity、Langchain、Causal-Learn、XGBoost、sklearn 等版本，也未列出所有默认基线参数。对于 Responsible NLP checklist 的 reproducibility 条目，这会削弱 “sufficient implementation details” 的支撑。

## 5. 可执行修改建议

1. 匿名化 review 源码：在 review 版中删除或条件编译 `\author{...}` 的真实姓名、单位、邮箱和 `\thanks`；可用 `\ifacl@finalcopy` 或独立 `anonymous` 开关只在 camera-ready 版恢复作者信息。提交前编译匿名 PDF，检查首页和脚注没有 corresponding-author 或邮箱残留。
2. 增加 `\section*{Ethics Statement}`：说明所有数据集来源、许可证/terms、是否公开数据、是否含 PII/敏感属性、是否需要 IRB/consent；讨论社会/医疗/犯罪数据生成的风险、误用场景、偏见放大、公平性限制，以及 few-shot records 发送到商业 LLM API 的数据处理假设。
3. 增加 Responsible NLP checklist 支撑段落或补充文件：逐项准备 data、human subjects、annotation、model/API、compute、environmental impact、limitations、risks、reproducibility 的回答，并确保每个 “yes” 都能映射到论文中的具体段落、表格或附录。
4. 强化复现包说明：提供匿名代码仓库或明确 camera-ready release 计划；列出 API provider/model snapshot/调用日期、随机种子、数据预处理、依赖版本、baseline 版本和完整配置。对 “使用默认配置” 的基线，至少固定库版本并导出默认参数表。
5. 扩展计算成本披露：在 token 表旁增加硬件环境、CPU/GPU 型号、运行时间、API 请求次数、估算美元成本、深度基线训练成本；若无 GPU，明确 CPU-only 或 API-only 设置。
6. 补充数据治理和安全边界：对 Adult/Compas/health datasets 说明敏感属性处理方式；在 limitations 或 ethics 中明确合成数据不应被视为真实人群分布替代品，不应用于高风险决策或未审计的公平性评估。

独立性说明：本次审计未访问 Audit/reports，也未读取 Audit/reports_codex 中的其他 Codex 报告。
