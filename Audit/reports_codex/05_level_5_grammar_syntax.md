# Level 5 语法与句法审计报告

## 1. 标题与范围

本报告审计 Writing Checklist Level 5: Grammar & Syntax，范围限于 `Audit/writing_checklist.md` 中 5.1--5.5 的检查项，以及 `Latex-EMNLP/main.tex` 和 `Latex-EMNLP/sections/*.tex` 的论文正文、图表标题、附录和提示模板文本。审计重点是英语语法与句法，不评价叙事结构、实验设计或技术正确性。

## 2. Verdict summary

| 检查项 | 结论 | 摘要 |
|---|---|---|
| 5.1 Subject-verb agreement | 基本通过 | 未发现会影响理解的主谓一致错误；如 `node set ... contains`、`edges ... encode` 等结构处理稳定。 |
| 5.2 Tense consistency | 小修 | 主文方法与实验多用现在时，整体一致；附录基线设置段落出现现在时与过去时混用。 |
| 5.3 Article usage | 小修 | 冠词总体可读，但 `post LLM knowledge cutoff` 等名词短语需要补冠词或改为规范复合修饰语。 |
| 5.4 Comma usage | 基本通过 | Oxford comma 和 introductory comma 使用较稳定，未发现明显 comma splice；少数超长句建议拆分以降低句法负荷。 |
| 5.5 Common syntax errors | 小修 | 未发现严重句子残片；主要问题是单复数标题、并列结构、词形标签和少量笨重的分词结构。 |

## 3. 优点

- 主体论文的主谓一致较稳，尤其是图结构相关表达中，复数 `edges`、`nodes` 与单数 `graph`、`structure` 的谓语选择基本准确。
- 方法部分大多使用现在时描述算法流程，如 `Latex-EMNLP/sections/method.tex:12` 和 `Latex-EMNLP/sections/method.tex:29`，符合方法写作习惯。
- 逗号使用整体规范，三项并列表达中 Oxford comma 较一致，例如 `generation order, conditioning context, and scope` 在摘要和引言中反复使用且形式统一。
- 论文几乎没有真正的 sentence fragment 或 comma splice；多数长句虽复杂，但语法上仍可解析。

## 4. 问题清单（按严重度）

### 中等：附录基线设置段落时态不一致

- 证据：`Latex-EMNLP/sections/appendix.tex:187` 同一段先写 `we utilize`，随后写 `These models were run`、`we used`、`it was configured`。
- 影响：该段是在说明实验设置，当前时态在 present methodological description 与 past completed action 之间跳动。单句不难懂，但不符合 5.2 的段落内时态一致要求。
- 建议：统一为现在时：`we use ... These models are run ... we use ... it is configured ...`；或统一为过去时，但需与主文 `We use...` 的实验设置风格一致。

### 中等：`post LLM knowledge cutoff` 名词短语不够规范

- 证据：`Latex-EMNLP/sections/method.tex:47` 与 `Latex-EMNLP/sections/experiments.tex:20` 均写作 `datasets created post LLM knowledge cutoff`。
- 影响：这里 `post` 后接名词短语时缺少清晰的冠词/连字符结构，读起来像未完成的复合修饰语。
- 建议：改为 `datasets created after the LLM knowledge cutoff`，或在标题式压缩表达中写作 `post-LLM-knowledge-cutoff datasets`。

### 中等：提示示例中 `Rational:` 词形错误

- 证据：`Latex-EMNLP/sections/appendix.tex:522`、`525`、`528`、`531` 使用 `Rational:` 作为标签。
- 影响：`rational` 是形容词；此处需要名词 `Rationale`。这属于 5.5 常见词形/句法标签错误，并且会出现在论文附录的可见示例中。
- 建议：全部改为 `Rationale:`。

### 低：标题和图表标题存在单复数不自然

- 证据：`Latex-EMNLP/sections/related_work.tex:1` 使用 `Related Works`；`Latex-EMNLP/sections/experiments.tex:113` 使用 `Ablation Study on Adult Datasets.`
- 影响：学术论文中章节标题通常用不可数的 `Related Work`；Adult 是一个数据集名，表题中应为单数 `Adult Dataset`。
- 建议：分别改为 `Related Work` 和 `Ablation Study on the Adult Dataset.`。

### 低：并列结构不平行

- 证据：`Latex-EMNLP/sections/appendix.tex:183` 写作 `They differ in tasks, number of features, and domain.`
- 影响：`tasks`、`number of features`、`domain` 的数和抽象层级不一致，句法并列不够平行。
- 建议：改为 `They differ in task type, feature count, and domain.` 或 `They differ in their tasks, numbers of features, and domains.`。

### 低：分词结构略显悬垂或省略过度

- 证据：`Latex-EMNLP/sections/appendix.tex:11` 中 `SMOTE ... generates ..., addressing class imbalance but limited to local linear combinations.`
- 影响：`limited to` 缺少与 `addressing` 平行的动词形式，容易读成省略过度的分词短语。
- 建议：改为 `addressing class imbalance while remaining limited to local linear combinations`。

### 低：部分长句不是错误，但有 run-on 风险

- 证据：`Latex-EMNLP/sections/experiments.tex:11`、`Latex-EMNLP/sections/appendix.tex:26`、`Latex-EMNLP/sections/appendix.tex:353`、`Latex-EMNLP/sections/appendix.tex:395` 都包含多个从句、括号说明、分号或长并列结构。
- 影响：这些句子大多语法成立，但接近 5.5 中 run-on sentence 的风险区间；审稿人快速阅读时容易丢失主谓骨架。
- 建议：将指标定义、方法枚举和结果解释拆为两到三句；保留一个主谓核心，括号说明尽量后移或单独成句。

## 5. 可执行修订建议

1. 先做机械替换：`Related Works` -> `Related Work`；`Adult Datasets` -> `the Adult Dataset`；`Rational:` -> `Rationale:`。
2. 统一 `post LLM knowledge cutoff` 的表达，优先使用 `after the LLM knowledge cutoff`，避免标题压缩式复合名词造成冠词缺失。
3. 统一附录实验设置段落的时态。若主文维持现在时，附录也建议使用 `we use / are run / is configured / are provided`。
4. 对附录长句做轻量拆分，尤其是 `appendix.tex:26`、`appendix.tex:353` 和 `appendix.tex:395`，每句只承载一个主要判断。
5. 最后单独扫一遍图表标题和 prompt box 文本；这些位置容易残留单复数、冠词和标签词形问题。

## 6. 独立性说明

本次审计独立完成；我没有访问、读取、列出或检查 `Audit/reports`，也没有读取 `Audit/reports_codex` 中的其他 Codex 报告。
