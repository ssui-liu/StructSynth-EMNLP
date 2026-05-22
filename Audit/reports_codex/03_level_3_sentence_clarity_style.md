# Level 3 句子级清晰度与风格独立审计报告

## 1. 标题与范围

本报告审计 `Latex-EMNLP` 论文在 Writing Checklist Level 3: Sentence-Level Clarity & Style 下的表现，覆盖 3.1 句长与复杂度、3.2 主动/被动、3.3 谨慎措辞、3.4 具体性、3.5 简洁性、3.6 平行结构、3.7 歧义。审计依据为 `Audit/writing_checklist.md`、`Latex-EMNLP/**` 源文件，以及仅针对这些允许文件运行的轻量静态检查。

轻量静态检查显示：在 `Latex-EMNLP/sections/*.tex` 的正文、图表说明和可读附录文本中，粗略识别约 351 个句子，平均句长约 21.0 词，整体落在 15-25 词的目标区间；但仍有 16 句超过 40 词，其中 1 句超过 60 词。问题集中在实验设置、消融列表、扩展相关工作、效率分析和讨论性附录。

## 2. 结论摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 3.1 句长与复杂度 | 部分通过，需修改 | 平均句长健康，但若干关键句超过 40 词，尤其是 `experiments.tex:11`、`experiments.tex:105`、`appendix.tex:353`、`appendix.tex:456`。 |
| 3.2 主动/被动 | 基本通过 | 主文多用主动句，但方法描述中有较多 agentless passive，如 `method.tex:12`、`method.tex:38`、`method.tex:90`，会降低操作步骤的直接性。 |
| 3.3 Hedging | 部分通过 | 结果解释大体克制，但 `confirms`、`conclusively demonstrating`、`powerful evidence` 等表达偏强，证据强度与措辞不完全匹配。 |
| 3.4 具体性 | 基本通过，局部需增强 | 数据集数、指标和排名较充分；但摘要和结论里的 `state-of-the-art`、`competitive statistical fidelity`、`substantial gains` 可补充具体指标。 |
| 3.5 简洁性 | 基本通过 | 无明显口语化 filler，但存在 `utilize/utilized`、`It is important to...`、`A key observation is...` 等可压缩表达。 |
| 3.6 平行结构 | 部分通过 | 贡献列表整体可读；但比较句和消融列表有平行结构不一致，特别是 `introduction.tex:24` 与 `experiments.tex:105`。 |
| 3.7 歧义 | 部分通过 | 大部分指代清楚；少数 `This/These` 独立开头依赖前文推断，如 `experiments.tex:4`、`experiments.tex:84`、`experiments.tex:90`，建议加名词锚点。 |

## 3. 优点

- 论文核心句式总体清晰，围绕 `dependency graph as a generation plan` 的主线重复稳定，术语负担没有明显失控。
- 摘要、引言和主要实验段落普遍使用主动结构，如 `We introduce`、`We answer`、`We conduct`、`We compare`，读者能快速识别作者动作。
- 大多数结果句包含具体数值、排名或实验设置，例如 `experiments.tex:84` 给出 75.01、71.54、73.36，`experiments.tex:136` 给出 1.0-1.4、1.6、1.1、4.4 AUC pts。
- 解释性段落常采用“观察 -> 解释”的句式，尤其是隐私与保真度权衡段落，逻辑关系对审稿人较友好。

## 4. 按严重程度排序的问题

### 高优先级问题 1：关键实验与附录段落长句过载

- `experiments.tex:11` 将三个评估维度、训练方式、指标定义和“lower/closer is better”规则压进一个长句。审稿人需要反复回读才能区分 Downstream Performance、Statistical Fidelity 和 Privacy Risk。
- `experiments.tex:105` 的消融设置句包含 7 个 variant，且每个 variant 又带解释；静态检查将其中一段识别为约 61 词，超过 checklist 的 40 词上限。
- `experiments.tex:159` 用一个句子同时介绍三个 bnlearn 数据集、SHD 指标和 SHD 定义，句法负载偏高。
- `appendix.tex:353` 在一个长句中列出四种下游模型、四类数据集属性、表格引用和比较对象，信息密度过高。
- `appendix.tex:456` 以 `First/Second/Third` 组织很好，但整行承载三层论证、多个数值和解释，读者扫读成本高。

影响：这些位置直接承担实验可信度和机制解释。一旦句子过长，审稿人可能错过“评估指标如何定义”“消融到底移除了什么”“为什么保真度不是最高但效用最好”等核心信息。

### 高优先级问题 2：部分结论性动词过强，hedging 与证据强度不完全匹配

- `experiments.tex:161` 写道 `This confirms that the LLM's semantic prior...`。SHD 趋势支持该解释，但除非有统计检验或因果隔离，`confirms` 可降为 `supports` 或 `suggests`。
- `experiments.tex:172` 使用 `demonstrating that structural guidance can substantially boost weaker models`。该句有具体 AUC 增益示例，但 `substantially` 和 `demonstrating` 组合偏强，可改成更贴近观察的 `indicating`。
- `appendix.tex:299` 同时使用 `powerful evidence` 与 `confirms`，对定性图分析来说说服力较满，可改为 `additional evidence` 和 `supports`。
- `appendix.tex:464` 的 `conclusively demonstrating` 对一个 ablation 观察而言过强；建议改为 `showing` 或 `providing evidence that`。
- `appendix.tex:483` 的 `will naturally align` 也偏确定；更稳妥是 `can align` 或 `is expected to align`。

影响：过强措辞可能让审稿人把写作问题解读为 claim inflation，尤其在结构发现、因果图近似和泛化解释这些敏感点上。

### 中高优先级问题 3：摘要和主结果中的具体性还可以更贴近数值证据

- `abstract.tex:3` 结尾说 `state-of-the-art downstream utility and privacy preservation while maintaining competitive statistical fidelity`，但没有给出六数据集平均分、平均排名或低数据设置下的关键数值。
- `experiments.tex:84` 说 `yields substantial gains`，前一句已有 75.01、71.54、73.36，但没有直接说提升幅度。读者要自行计算 +3.47 over train-only 和 +1.65 over CLLM。
- `experiments.tex:90` 的 `competitive statistical fidelity` 可补上 `avg. rank 7.92` 或与最优方法的距离，否则“competitive”显得主观。
- `conclusion.tex:4` 重复 `state-of-the-art downstream utility and privacy preservation while maintaining competitive statistical fidelity`，但没有用一句话锚定最主要数字。

影响：这些句子出现在摘要、主结果和结论，是审稿人最容易引用的 claim。将形容词替换为数值能显著降低质疑空间。

### 中优先级问题 4：方法描述里 passive 和名词化让步骤不够直接

- `method.tex:12` 使用 `The dependency structure is represented... The graph is constructed...`。作为方法定义，主动句 `We represent... We construct...` 更直接。
- `method.tex:30` 与 `method.tex:38` 中 `The LLM is then queried...` 反复出现；如果 agent 是框架本身，可改为 `StructSynth queries the LLM...`。
- `method.tex:90` 的 `Upon learning... we utilize it... Constructing each synthetic data point is performed...` 同时有 `utilize` 和被动名词化，建议改为 `After learning G, StructSynth generates each synthetic record in two phases...`。
- `appendix.tex:183`、`appendix.tex:187`、`appendix.tex:191` 多次出现 `utilized/utilize/provided`，可用 `use/report/list` 等更短动词替代。

影响：方法段落本应帮助读者重建算法。过多被动和名词化会让“谁做了什么”变得松散。

### 中优先级问题 5：少数 `This/These` 指代需要名词锚点

- `experiments.tex:4` 的 `These allow direct measurement...` 紧接 bnlearn 三个数据集之后，读者能推断 `These` 指代 Asia/Child/Insurance，但建议写成 `These benchmark graphs allow...`。
- `experiments.tex:84` 的 `This improves over using only...` 指代上一句的 StructSynth performance，建议改为 `This average score improves...`。
- `experiments.tex:90` 的 `This is because Statistical Fidelity measures...` 指代“高 pairwise fidelity 不保证 downstream utility”，建议改为 `This mismatch arises because...`。
- `appendix.tex:466` 的 `This discrepancy...` 可以更明确为 `The fidelity-utility discrepancy...`。
- `appendix.tex:483` 的 `This is not a contradiction` 可改为 `This causal-alignment observation is not a contradiction` 或直接合并到后一句。

影响：这些指代不至于造成事实错误，但会增加审稿人短时记忆负担，尤其在结果解释段。

### 中低优先级问题 6：平行结构局部不稳

- `introduction.tex:24` 的 `what to generate, in what order, and conditioned on which context` 前两项是疑问名词短语，第三项是被动分词结构。建议改为 `what to generate, when to generate it, and which context to condition on`。
- `experiments.tex:105` 的消融列表混用 `substituting`、`replacing`、`removing`、`conducting`，且结构学习阶段和生成阶段的描述方式不完全平行。建议统一为 `replace X with Y`、`remove X`、`ignore X`。
- `appendix.tex:489` 的 prompt sequence 句式基本平行，但 `after which` 使最后一项附着在前一句上；可拆成 `Finally, ... Then, ...`。

影响：平行性问题主要影响扫读速度，不是实质性缺陷，但在贡献和消融设置中值得修。

### 低优先级问题 7：可压缩表达仍有少量累积

- `method.tex:90`、`appendix.tex:187`、`appendix.tex:191` 中的 `utilize/utilized` 可统一改为 `use/used`。
- `appendix.tex:395` 的 `A practical concern is...`、`appendix.tex:397` 的 `A key observation is...`、`appendix.tex:479` 的 `It is important to clearly distinguish...` 可以直接进入主语和动词。
- `appendix.tex:299` 的 `More importantly`、`remarkable structural similarity`、`powerful evidence` 连续增强语气，可删减为更审稿友好的技术描述。

影响：单处不严重，但附录长段中累积后会形成略显“用力”的风格。

## 5. 可执行修改建议

1. 优先拆分 `experiments.tex:11`：将三项指标各写成一句，格式保持一致。例如 `Downstream Model Performance measures... We report... Statistical Fidelity measures... Privacy Risk measures...`。
2. 重写 `experiments.tex:105` 的消融列表：改成两个短列表或两句。结构学习阶段统一为 `replace/remove`，生成阶段统一为 `ignore/remove/replace`，避免每个 item 都带长从句。
3. 将强结论词降一级：把 `confirms` 改为 `supports`，`conclusively demonstrating` 改为 `showing`，`powerful evidence` 改为 `additional evidence`，除非同一段补充显著性检验或严格因果隔离。
4. 给摘要和结论补一处核心数字：例如在 `abstract.tex:3` 加入 `average downstream score 75.01`、`avg. privacy rank 1.50` 或 `+1.65 over CLLM` 中最能支撑主张的 1-2 个数值。
5. 把方法步骤改成主动主语：`We represent...`、`StructSynth queries...`、`StructSynth generates...`。这会让算法描述更像可复现流程。
6. 给独立开头的 `This/These` 加名词：`This average score`、`This mismatch`、`These benchmark graphs`、`This causal-alignment observation`。
7. 修正平行表达：`what to generate, when to generate it, and which context to condition on`；消融列表统一动词形式；贡献句中的多项对象保持相同语法层级。
8. 做一次全局轻量替换：`utilize/utilized` -> `use/used`，`It is important to distinguish` -> `We distinguish` 或 `StructSynth's DAGs differ from causal graphs because...`。

独立性说明：本次审计未访问 `Audit/reports` 或其中任何文件，也未读取 `Audit/reports_codex` 中其他 Codex 报告；报告仅基于 `Audit/writing_checklist.md`、`Latex-EMNLP/**` 和针对这些允许来源的本地静态检查。
