# Level 4 词级精确性独立审计报告

## 1. 标题与范围

本报告审计 `Latex-EMNLP/**` 中论文文本相对于 `Audit/writing_checklist.md` 的 Level 4: Word-Level Precision。审计重点为：4.1 术语一致性、4.2 学术语体、4.3 易混词、4.4 过度用词、4.5 介词准确性；特别关注术语变体、模糊/过度词、非正式表达、缩写、介词搭配与定量措辞精确性。

## 2. 判定摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 4.1 术语一致性 | 需中等幅度修订 | 核心思想清楚，但同一核心对象在 `dependency graph`、`DAG`、`dependency structure`、`learned graph`、`structural/generative/executable blueprint`、`generation plan` 之间频繁切换，且非因语义需要而变化。 |
| 4.2 学术语体 | 基本通过，需局部降调 | 未发现真正的英文缩写否定式或第一人称单数；但有 `data-hungry`、`wins`、`top-tier`、`outsized returns`、`powerful evidence` 等偏口语或宣传化措辞。 |
| 4.3 易混词 | 基本通过，存在概念词风险 | 未见明显 `affect/effect`、`compare to/with`、`based off` 等错误；主要风险是 `causal/causes/effects` 与论文声明的“非因果 dependency graph”边界偶有混淆。 |
| 4.4 过度用词 | 需修订 | `strong`、`substantial(ly)`、`robust`、`significant(ly)`、`effective`、`best`、`competitive`、`leverage/utilize` 等高频出现，部分可以用具体数值或更普通动词替代。 |
| 4.5 介词准确性 | 基本通过 | 未发现系统性错误如 `depend of`、`based off of`、`consist in`；仅有少量题注/短语可微调，如 `Ablation Study on Adult Datasets`。 |

## 3. 优点

- 关键方法名 `Evidence-Grounded Graph Induction` 与 `Graph-Planned Conditional Synthesis` 在摘要、引言和方法中基本稳定，读者能识别两阶段框架。
- `DAG` 在 `Latex-EMNLP/sections/introduction.tex:30` 有脚注限定为生成蓝图而非真实因果声明，属于很有价值的词级防误解设计。
- 未检出真正的英文 contraction；`I` 的命中仅为数学符号 `\mathbb{I}`，不是第一人称单数。
- 常见介词搭配整体可靠；`conditioned on`、`based on`、`depend on` 类表达未见明显误用。
- 实验段通常邻近提供数值、rank 或标准差，为把模糊形容词改成精确量化表达提供了现成材料。

## 4. 主要问题（按严重程度）

### 4.1 核心术语隐喻过多，削弱中心贡献的词级稳定性

同一核心对象和作用在多个术语间切换：摘要在同一行使用 `dependency graphs`、`generation plan`、`Directed Acyclic Graph (DAG)`（`Latex-EMNLP/sections/abstract.tex:3`）；引言又使用 `dependency structure`、`directed dependency graph`、`generative blueprint`、`executable generation plan`（`Latex-EMNLP/sections/introduction.tex:24`, `Latex-EMNLP/sections/introduction.tex:30`, `Latex-EMNLP/sections/introduction.tex:31`）；方法中出现 `learned DAG as an executable blueprint`（`Latex-EMNLP/sections/method.tex:8`），结论中又变为 `dependency blueprint` 与 `outsized returns`（`Latex-EMNLP/sections/conclusion.tex:5`）。

建议将中心表述固定为：图对象用 `dependency graph (DAG)`，功能用 `generation plan`。`blueprint` 如保留，应只作为一次性的解释性隐喻，不再与 `plan` 并列反复替换。

### 4.2 因果词与依赖词边界不够稳，可能与“不作因果声明”冲突

论文已在 `Latex-EMNLP/sections/introduction.tex:30` 明确说明 DAG 不是 ground-truth causal claim，但附录和 prompt 模板中仍有强因果词：`source node is ... not caused by any other variable`（`Latex-EMNLP/sections/appendix.tex:569`）、`direct successors (effects)`（`Latex-EMNLP/sections/appendix.tex:616`）、`valid causal path`（`Latex-EMNLP/sections/appendix.tex:331`）。Asia benchmark 的因果说明可以保留，但应明确“仅在已知因果基准中使用 causal 词汇”；方法/prompt 的一般描述宜改为 dependency/topological language。

推荐替换：`not caused by any other variable` -> `has no incoming dependency edges in this dataset representation`；`direct effects` -> `direct dependent successors`；`valid causal path` -> `valid topological dependency path`。

### 4.3 定量措辞有时没有承接具体数值，导致强 claim 不够精确

摘要称 `state-of-the-art downstream utility and privacy preservation` 且 `competitive statistical fidelity`（`Latex-EMNLP/sections/abstract.tex:3`），引言贡献重复类似措辞（`Latex-EMNLP/sections/introduction.tex:35`）。实验主结果虽有数值，但文字仍使用 `substantial gains`、`notably weaker`（`Latex-EMNLP/sections/experiments.tex:84`）。更关键的是，隐私段称 `best privacy preservation`（`Latex-EMNLP/sections/experiments.tex:90`），但表中平均 privacy score 上 CLLM 的 50.51 比 StructSynth 的 50.95 更接近 0.5；若依据的是 average rank 1.50，应写成“best average privacy rank”而非笼统“best privacy preservation”。

建议把强 claim 改为数值化：例如 `+1.65 average score over CLLM`、`+3.47 over train-only`、`best average privacy rank (1.50)`、`statistical-fidelity rank 7.92`。`Latex-EMNLP/sections/experiments.tex:172` 的 `substantially boost weaker models` 已给出 Maverick `+0.028 AUC`，可直接用该数值替代形容词。

### 4.4 学术语体中有宣传化或口语化词汇

以下表达建议降调：`data-hungry`（`Latex-EMNLP/sections/related_work.tex:12`）可改为 `sample-intensive`；`wins 14 out of 16 cells`（`Latex-EMNLP/sections/experiments.tex:155`, `Latex-EMNLP/sections/appendix.tex:353`）可改为 `achieves the highest score in 14 of 16 cells`；`top-tier models`（`Latex-EMNLP/sections/experiments.tex:172`）可改为 `high-capability models`；`outsized returns`（`Latex-EMNLP/sections/conclusion.tex:5`）可改为 `larger utility gains under data scarcity`；`remarkable structural similarity` 和 `powerful evidence`（`Latex-EMNLP/sections/appendix.tex:299`）可改为 `close structural similarity` 和 `evidence`。

Prompt 模板中的 `weakest link`（`Latex-EMNLP/sections/appendix.tex:688`, `Latex-EMNLP/sections/appendix.tex:692`）口语感较强；若作为可复现实验材料展示，建议改为 `least supported edge`。

### 4.5 过度词和泛化动词重复，降低句子精度

`utilize`/`leverage` 在正文和附录多处出现，如 `utilize three benchmark datasets`（`Latex-EMNLP/sections/experiments.tex:4`）、`utilize it to guide`（`Latex-EMNLP/sections/method.tex:90`）、`leverages the learned graph`（`Latex-EMNLP/sections/related_work.tex:7`）、`leveraging prior knowledge`（`Latex-EMNLP/sections/appendix.tex:29`）。多数位置用 `use` 更直接。

形容词/副词也偏密集：`substantially more samples`（`Latex-EMNLP/sections/introduction.tex:18`）、`substantially easier`（`Latex-EMNLP/sections/method.tex:18`）、`substantially higher errors` 与 `robust structure recovery`（`Latex-EMNLP/sections/experiments.tex:161`）、`significantly more samples`（`Latex-EMNLP/sections/experiments.tex:166`）。建议能量化则量化，不能量化则改为更中性的 `more`、`higher`、`stable` 或删除。

### 4.6 术语大小写、单复数和标签仍有小不一致

`Related Works`（`Latex-EMNLP/sections/related_work.tex:1`）按 ACL/NLP 惯例宜为 `Related Work`；`Experimental Setups`（`Latex-EMNLP/sections/experiments.tex:2`）宜为 `Experimental Setup`。`Machine Learning (ML)` 在引言中大写（`Latex-EMNLP/sections/introduction.tex:14`），附录中用小写 `machine learning model`（`Latex-EMNLP/sections/appendix.tex:239`）；如不是专名，统一小写即可。`Peter--Clark` 与 `Peter-Clark` 分别出现在 `Latex-EMNLP/sections/experiments.tex:105` 和 `Latex-EMNLP/sections/appendix.tex:191`，建议统一。

### 4.7 介词层面问题较少，但个别题注可更自然

未发现系统性介词错误。可微调的例子包括 `Ablation Study on Adult Datasets`（`Latex-EMNLP/sections/experiments.tex:113`）应为 `Ablation study on the Adult dataset`；`Comparison of Models on Downstream Model Performance`（`Latex-EMNLP/sections/method.tex:47`）可改为 `Comparison of models for downstream performance`；`post LLM knowledge cutoff`（`Latex-EMNLP/sections/experiments.tex:20`）可改为 `after the LLM knowledge cutoff` 或 `post-cutoff datasets`。

## 5. 建议术语表

| Preferred term | 用途 | 建议避免/限制的变体 |
|---|---|---|
| `dependency graph (DAG)` | 指论文发现并用于生成排序的图对象；首次定义后按语境用 `dependency graph` 或 `DAG`。 | `dependency structure`、`learned graph`、`discovered structure` 混用；除非强调不同层面。 |
| `generation plan` | 指 DAG 在 LLM 合成过程中的功能角色。 | `blueprint`、`generative blueprint`、`executable blueprint`、`dependency blueprint` 反复替换。 |
| `Evidence-Grounded Graph Induction` | 第一阶段正式名称。 | `structure learning stage`、`dependency discovery stage` 未定义地交替使用。 |
| `Graph-Planned Conditional Synthesis` | 第二阶段正式名称。 | `structure-guided synthesis`、`graph-based generation`、`generation strategy` 未定义地交替使用。 |
| `low-data regime` | 实验设置，建议明确 `$n \le 100$`；当指 `$n \le 50$` 时单独说明。 | `few samples`、`scarce samples`、`data-scarce settings`、`limited samples` 频繁互换。 |
| `pairwise Statistical Fidelity error` | 指该指标且 lower is better。 | `fidelity`、`raw fidelity`、`high fidelity` 未说明方向或是否 pairwise。 |
| `Privacy Risk` / `privacy rank` | 区分原始 score 与 average rank。 | `best privacy preservation` 在依据 rank 时不加限定。 |

## 6. 可执行修订建议

1. 在引言或方法开头加入一个 3-5 项的术语约定，并据此全篇替换：图对象统一为 `dependency graph (DAG)`，功能统一为 `generation plan`。
2. 将所有非基准说明中的 `causal`、`cause`、`effect` 改成 `dependency`、`predecessor/successor`、`incoming/outgoing edge`；仅在 Asia/ground-truth causal benchmark 描述中保留 causal 词。
3. 对摘要、贡献和结论中的强 claim 做数值化压缩：优先写平均分、rank、AUC 点数、token overhead，而不是 `substantial`、`competitive`、`outsized`。
4. 批量替换低信息动词：大多数 `utilize` -> `use`；`leverage` 只保留在确实表示“利用某种能力/资源产生增益”的位置。
5. 删除或降调宣传化形容词：`remarkable`、`powerful`、`top-tier`、`data-hungry`、`wins`、`outsized returns`。
6. 统一标题和术语大小写：`Related Work`、`Experimental Setup`、`machine learning`、`Peter--Clark`。
7. 对隐私相关表达特别精确：若使用 average rank，就写 `best average privacy rank`；若使用 score，就说明“closer to 0.5 is better”并避免把 rank 和 score 混成一个 claim。

## 7. 独立性说明

本报告为独立审计结果；我没有访问 `Audit/reports`，也没有读取 `Audit/reports_codex` 中任何其他 Codex 报告。
