# Level 6 引用与参考文献审计报告

## 1. 标题与范围

本报告独立审计 `Latex-EMNLP` 论文源文件在 Writing Checklist Level 6: Citations & References 上的合规性。审计依据为 `Audit/writing_checklist.md` 中 6.1、6.2、6.3 的检查项，并对 `Latex-EMNLP/**/*.tex` 与 `Latex-EMNLP/references.bib` 做静态源码检查。未编译论文，以避免与并行工作发生构建产物冲突。

## 2. 结论摘要

| 检查项 | 判定 | 摘要 |
|---|---|---|
| 6.1 Citation format | 不通过 | 正文与附录中实际引用命令共 93 个，全部为裸 `\cite{...}`；未发现实际使用的 `\citep{...}` 或 `\citet{...}`。 |
| 6.2 Citation placement | 基本通过，需小修 | 未发现引用置于句号之后、双括号或纯引用句的静态证据；但有一处多文献排序不一致。 |
| 6.3 Reference completeness | 部分通过，需清理 | 所有已引用 key 都能在 `references.bib` 中找到；但 211 个 bib 条目中仅 59 个被引用，约 152 个看似未使用；部分已引用条目缺少 pages 或更完整出版信息。 |

## 3. 优点

- `main.tex` 正确挂接参考文献库：`Latex-EMNLP/main.tex:135` 使用 `\bibliography{references}`。
- 静态 key 对照未发现 unresolved citation：59 个唯一已引用 key 均存在于 `Latex-EMNLP/references.bib`。
- 引用位置总体可读：抽查和静态模式检查未发现“句号后放引用”的情况，也未发现 citation-only sentence。
- 引用大多与具体方法、数据集或评价指标绑定，而不是孤立堆砌，例如数据集引用集中在 `Latex-EMNLP/sections/experiments.tex:4` 与附录数据表 `Latex-EMNLP/sections/appendix.tex:171` 至 `Latex-EMNLP/sections/appendix.tex:176`。
- 多数多文献引用已经按时间顺序组织，例如 `Latex-EMNLP/sections/related_work.tex:23` 的 2024、2025 顺序，以及 `Latex-EMNLP/sections/appendix.tex:26` 的 2006、2008、2009 顺序。

## 4. 问题清单，按严重程度排序

### 严重：全篇使用裸 `\cite{...}`，违反 ACL citation format 要求

清单 6.1 明确要求 textual citation 使用 `\citet`，parenthetical citation 使用 `\citep`，并要求不要使用裸 `\cite`。静态检查结果显示，实际引用命令共 93 个，命令类型分布为 `{'cite': 93}`。`main.tex` 中的 `\citep` 和 `\citet` 只出现在 TeXCount 注释里：`Latex-EMNLP/main.tex:7`、`Latex-EMNLP/main.tex:8`，没有在正文中实际使用。

证据示例：

- `Latex-EMNLP/sections/introduction.tex:13`：`healthcare~\cite{choi2017generating}, finance~\cite{rundo2019machine}, and education~\cite{luan2021review}`
- `Latex-EMNLP/sections/related_work.tex:12`：`VAE-based~\cite{patki2016synthetic}`, `GAN-based~\cite{xu2019modeling}`
- `Latex-EMNLP/sections/method.tex:29`：`attributes~\cite{agresti2011categorical}`
- `Latex-EMNLP/sections/experiments.tex:8`：所有 baseline 引用都使用 `\cite`
- `Latex-EMNLP/sections/appendix.tex:11`、`Latex-EMNLP/sections/appendix.tex:14`、`Latex-EMNLP/sections/appendix.tex:17`：扩展相关工作整段使用裸 `\cite`
- `Latex-EMNLP/sections/appendix.tex:171` 至 `Latex-EMNLP/sections/appendix.tex:176`：表格中的数据集来源也使用裸 `\cite`

影响：这会直接触发 Level 6.1 的格式不合规，并可能导致 ACL natbib 样式下 citation 输出不符合作者-年份的语法预期。

### 严重：`references.bib` 有大量未使用条目

静态对照显示：

- `Latex-EMNLP/references.bib` 总条目数：211。
- 唯一已引用 key：59。
- 未解析 key：0。
- 看似未使用 key：152。

清单 6.3 要求 every entry in `references.bib` is cited at least once。当前 bib 文件看起来混入了大量历史或备用条目，虽然 BibTeX 通常不会输出未引用条目，但这仍不符合清单要求，也会增加引用审稿时的噪音与维护风险。

证据示例：

- `Latex-EMNLP/references.bib:1` 的 `jonker2025structured_unstructured_ibm` 未在 tex 源中引用。
- `Latex-EMNLP/references.bib:101` 的 `durkan2019neural` 未引用，而正文使用的是 `papamakarios2021normalizing` 指代 normalizing flows。
- `Latex-EMNLP/references.bib:125` 的 `shi2025tabdiff` 未引用。
- `Latex-EMNLP/references.bib:295` 至 `Latex-EMNLP/references.bib:331` 的若干 LLM 技术报告条目未引用。
- `Latex-EMNLP/references.bib:1478` 的 `bnlearn` 未引用，正文实际使用 `scutari2010learning` 与 `bnlearn-repo-*`。

完整未使用 key 列表见第 5 节静态检查记录。

### 中高：部分已引用 bib 条目元数据不完整

按清单 6.3，参考文献应具备 authors、title、venue、year、pages 等完整元数据。静态字段检查发现若干已引用条目缺少 `pages` 或更完整的出版信息。对 OpenReview、TMLR、arXiv、软件或网页条目，页码可能并不总是适用，但应补足 DOI、URL、eprint、archivePrefix、出版版本等可追溯信息。

证据示例：

- `Latex-EMNLP/references.bib:68`，`liu2023goggle`：`@inproceedings`，有 author/title/booktitle/year，但缺少 pages。
- `Latex-EMNLP/references.bib:75`，`xu2019modeling`：`@article`，有 journal/volume/year，但缺少 pages。
- `Latex-EMNLP/references.bib:118`，`tabsyn`：`@inproceedings`，缺少 pages 或 OpenReview URL。
- `Latex-EMNLP/references.bib:141`，`cllm2024`：ICML 条目缺少 pages，且最后一个字段后保留尾逗号。
- `Latex-EMNLP/references.bib:364`，`zanna2025fairness`：arXiv preprint 仅有 journal/year，缺少 arXiv id 或 URL。
- `Latex-EMNLP/references.bib:378`，`jiralerspong2024efficient`：arXiv preprint 仅有 journal/year，缺少 arXiv id 或 URL。
- `Latex-EMNLP/references.bib:947`，`shimizu2006linear`：journal/volume/number/year 存在，但缺少 pages。
- `Latex-EMNLP/references.bib:1129`，`xie2020generalized`：conference 条目缺少 pages。
- `Latex-EMNLP/references.bib:1892`，`zheng2018dags`：NeurIPS 条目缺少 pages。

影响：参考文献列表即使能编译，也可能在 ACL/EMNLP 审稿标准下显得不完整，尤其是已发表会议论文缺少页码或 ACL Anthology/PMLR 信息时。

### 中：一处多文献引用排序不一致

清单 6.2 要求 multiple citations 按时间或字母顺序保持一致。大多数多文献引用是时间顺序，但 `Latex-EMNLP/sections/appendix.tex:29` 的医学领域引用为：

`medicine~\cite{naik2024applying, antonucci2023zero, arsenyan2024large}`

对应年份为 2024、2023、2024，既非时间顺序，也非 key 的字母顺序。建议统一为时间顺序，例如：

`medicine~\citep{antonucci2023zero, arsenyan2024large, naik2024applying}`

同一年内可继续按作者或 key 字母序排列。

### 中：FCI 引用在附录中前后不一致，可能引用到不够具体的来源

`Latex-EMNLP/sections/appendix.tex:26` 中 FCI 使用 `\cite{spirtes1995causal}`，这与 FCI/latent variables 语境匹配；但 `Latex-EMNLP/sections/appendix.tex:481` 中写作：

`PC algorithm~\cite{spirtes2000causation}, FCI~\cite{spirtes2000causation}, or GES~\cite{chickering2002optimal}`

这里 FCI 改用 `spirtes2000causation`，与前文不一致，也不如 `spirtes1995causal` 精确。建议改为 `FCI~\citep{spirtes1995causal}`，同时将全句 citation 命令切换为 `\citep` 或改写为真正 textual citation。

## 5. 静态检查记录

### 裸 citation 命令

- 检查结果：实际 citation 命令 93 个，全部为 `\cite{...}`。
- `\citep` 出现位置：仅 `Latex-EMNLP/main.tex:7` 的 TeXCount 注释。
- `\citet` 出现位置：仅 `Latex-EMNLP/main.tex:8` 的 TeXCount 注释。
- 未发现 `\citep{...}` 或 `\citet{...}` 在正文、方法、实验、附录中实际使用。

### 未解析 key

- 静态解析 `Latex-EMNLP/**/*.tex` 中 citation key 后，与 `Latex-EMNLP/references.bib` 对照。
- 未解析 key 数量：0。
- 说明：未编译，因此未检查 `.aux/.bbl` 层面的 BibTeX 警告；但源码级 key 对照没有发现缺失。

### 看似未使用的 bib key

以下 152 个 key 存在于 `Latex-EMNLP/references.bib`，但未在 `Latex-EMNLP/**/*.tex` 的 citation 命令中出现：

`Abrahamsen2018sparse`, `Breheny2011coordinate`, `Loh2017support`, `Ravikumar2008model`, `Robert1996lasso`, `Wainwright2009sharp`, `Zhang2010nearly`, `acid2003searching`, `albera2005icar`, `andersson1997characterization`, `annoymous2022iclr`, `ball1997elementary`, `bell1995information`, `bing2020adaptive`, `bnlearn`, `bohm1952suggested`, `bollen1989structural`, `buchholz2022function`, `buntine1991theory`, `burgess2018understanding`, `busiello2017explorability`, `carbonneau2022measuring`, `cardoso1998multidimensional`, `chen2018isolating`, `cohen2017emnist`, `comon1994independent`, `costanzo2010genetic`, `darmois1951analyse`, `de1983orthographic`, `dewitt2015many`, `ding2019likelihood`, `dinh2016density`, `donoho2003optimally`, `duan2020unsupervised`, `dupont2018learning`, `durkan2019neural`, `ehsandoust2015blind`, `einstein1905does`, `falck2021multi`, `fan2001variable`, `faye2002copenhagen`, `feng2013complementarity`, `fisher1921014`, `flanders1966liouville`, `forster2020frugal`, `freia`, `geiger2015causal`, `gisin2013there`, `glymour1986causal`, `glymour2019review`, `gong2015discovering`, `gong2017causal`, `granger1969investigating`, `granger1980testing`, `gresele2021independent`, `guo2020ltf`, `guo2025deepseek`, `halva2020hidden`, `halva2021disentangling`, `hoyer2008estimation`, `huang2018generalized`, `huang2020causal`, `hurst2024gpt`, `hyvarinen1997fast`, `hyvarinen1999nonlinear`, `hyvarinen2001independent`, `hyvarinen2010estimation`, `hyvarinen2013independent`, `hyvarinen2016unsupervised`, `hyvarinen2017nonlinear`, `hyvarinen2019nonlinear`, `janzing2010telling`, `joho2000overdetermined`, `jonker2025structured_unstructured_ibm`, `josselyn2020memory`, `kalainathan2020causal`, `khemakhem2020ice`, `khemakhem2020variational`, `kim2004underdetermined`, `kingma2018glow`, `kivva2022identifiability`, `klys2018learning`, `kong2022partial`, `kumar2017variational`, `lachapelle2021disentanglement`, `lam2022greedy`, `lippe2022citris`, `liu2024deepseek`, `locatello2018competitive`, `locatello2019challenging`, `lu2020invariant`, `maeda2020rcd`, `maeda2021causal`, `meta2025llama4`, `mistry2010inverse`, `mongeapplications`, `moran2021identifiable`, `nash1963nature`, `oja2002unsupervised`, `olshausen1996emergence`, `palsson2014sparse`, `pcalg`, `peters2014identifiability`, `pycausal`, `pytetrad`, `ramsey2016improving`, `ramsey2018tetrad`, `rao1998learning`, `raskutti2018learning`, `ravikumar2011high`, `rezende2018short`, `rhodes2021local`, `rohe2020vintage`, `rubenstein2018learning`, `runge2019detecting`, `saito2020universal`, `scheines1998tetrad`, `schwarz1978estimating`, `semon1921mneme`, `shastry2009snps`, `shi2025tabdiff`, `shimizu2011directlingam`, `shojaie2010discovering`, `silander2006simple`, `soeten2011conformal`, `sorrenson2020disentanglement`, `sprekeler2014extension`, `taleb1999source`, `team2024qwen2`, `theis2006towards`, `tong1991indeterminacy`, `trefethen1997numerical`, `tsamardinos2006max`, `tu2019causal`, `uhler2013geometry`, `von2021self`, `willetts2021don`, `wipf2004l0`, `wu2019domain`, `yao2021learning`, `yao2022temporally`, `yuan2013learning`, `zeilinger1996interpretation`, `zeilinger2003einsteins`, `zhang2008minimal`, `zhang2009ica`, `zhang2011kernel`, `zhang2012identifiability`, `zhang2013comparison`, `zhang2018causal`, `zhang2021ivpf`, `zhengidentifiability`。

### Citation placement 静态结果

- 未发现形如句号后再引用的模式。
- 未发现 citation-only sentence。
- 未发现明显 double parentheses 模式。
- 唯一自动标出的多文献排序疑点为 `Latex-EMNLP/sections/appendix.tex:29`。

## 6. 可执行修改建议

1. 全局替换裸 `\cite`，但不要机械一刀切。原则如下：
   - 方法名、数据集名、指标名后附来源时，用 parenthetical：`SMOTE~\citep{chawla2002smote}`、`Privacy Risk~\citep{van2023membership}`。
   - 作者或论文作为句子主语时，改写为 textual：`\citet{borisov2023language} serialize rows ...`。
   - `Following previous work~\cite{...}` 改为 `Following previous work~\citep{...}`。
2. 修正 `Latex-EMNLP/sections/appendix.tex:29` 的多文献排序，例如改为 `\citep{antonucci2023zero, arsenyan2024large, naik2024applying}`。
3. 修正 `Latex-EMNLP/sections/appendix.tex:481` 的 FCI 引用，优先与 `Latex-EMNLP/sections/appendix.tex:26` 保持一致，使用 `spirtes1995causal`。
4. 清理 `Latex-EMNLP/references.bib`：删除或移出 152 个未使用条目；如果某些条目确实应保留，则在正文中补充有语义支撑的引用，不要用 `\nocite{*}` 掩盖 orphan entries。
5. 补全已引用条目的元数据：
   - 对 ICML/PMLR、ACL Anthology、NeurIPS 等已发表论文补 pages、publisher、URL/DOI。
   - 对 OpenReview 条目补 URL。
   - 对 arXiv preprint 补 `eprint`、`archivePrefix={arXiv}`、URL；若已有正式发表版本，应改引正式版本。
6. 完成以上静态修改后，在隔离目录或单独构建目录中运行一次 LaTeX/BibTeX 编译，检查是否仍有 undefined citations、empty bibliography fields 或 natbib warnings。

独立性说明：本次审计未访问 `Audit/reports`，也未读取 `Audit/reports_codex` 中的其他 Codex 报告。
