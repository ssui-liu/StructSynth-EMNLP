# Rebuttal v2 写作优化方案（v1 → v2）

**输入**：`rebuttal-v1/{general-response, reviewer_7Wh2, reviewer_q74j, reviewer_iRH3}.md` + 投稿 PDF `EMNLP26_StructSynth.pdf`（正文 §1–§5 + Limitations/Ethics + 附录 A–K）+ `reviewer_reviews_only.md` + `new_experiments/` 权威数据
**输出**：`rebuttal-v2/{general_response, reviewer_7Wh2, reviewer_q74j, reviewer_iRH3}.md` + `rebuttal-v2/evidence_blocks.md` +（内部）`tracking.md`
**范围原则**：v2 **不新增实验**，只做重组、修正、统一、压缩。所有新实验数字以 §4 证据块为唯一来源，证据块一律从 `new_experiments/` 源文件抄录，禁止手敲或凭记忆复述。
**生成日期**：2026-07-13

---

## 0. TL;DR — v2 相对 v1 的六个核心改动

> 注：数值错误的修复（原第 2 项"三处严重数字事故"、原第 4 项"GraDe 对比修正"）已拆入独立文件 `00b_NUMERIC_AUDIT_PLAN.md` 单独处理，本计划不再涉及。

1. **q74j 开场事实更正前置**：投稿 **Appendix A（l.855–859）已包含匿名代码仓库** `https://anonymous.4open.science/r/StructSynth-41DB/README.md`。v1 却在文末承认"absence of an anonymous code/data link in the original submission"——把己方最强的反证让掉了。v2 开头即纠正这一信息差（Repro/Datasets/Software = 1/1/1 大概率源于 reviewer 未看到 Appendix A），文末 ask 请其据此重审三项子分。这是全场性价比最高的一处修改。
2. **匿名化实验改用同协议对照口径**：v1 把"论文 10-seed gpt-4o-mini 原始值"与"单 seed 校准换算值"混在一张表里且未披露。v2 改为 no_anon vs field_anon 同协议对照 + 只解读 Δ，并披露协议（单 seed、gpt-5-mini）；叙事同步修正——分类不降反稳、回归仅在 n=1000 落后（n=100–500 反而领先）。
3. **全条目统一 AAEA 微结构**：Acknowledge → **粗体 Direct answer** → 证据（`[Submitted, 锚点]` 先行、`[New, Exp-#]` 随后，带协议标签）→ 每条恰一个 `Revision (R#)`；结尾统一 Revision Summary 表 + 克制的 ask。
4. **Exp-1..4 编号贯通三线程**（General Response 已定义，但 7Wh2 全文未使用）；建立 `evidence_blocks.md` 单一数据源，杜绝再次跨文件漂移。
5. **叙事对齐源文件的允许边界**：General Response 的"generation mechanism is the larger contributor"是源文件明确禁止的净效应表述（`cross_validation_comparison.md` §4：不能估计净因果效应、不应直接比较四行高低），改为"可分离、可互相迁移"；Exp-4 的"consistent advantages"与 q74j 线程内"modest advantages, small relative to seed variation"统一为后者。
6. **内部元信息剥离**：三份 v1 文件头部的 Reviewer Scores 表与字数行移入 `tracking.md` 或 HTML 注释，发布稿不含。

---

## 1. v1 诊断

### 1.1 值得保留的骨架（v2 不要回退）

- 按 reviewer 原始 W 编号组织 + 条目短标题 + blockquote 裁剪引用原文。
- **诚实让步三件套**：7Wh2-W2 对 privacy 不 overclaim（DCR ≠ 形式保证）、7Wh2-W3 把 mixed fidelity 解释为设计后果而非否认、7Wh2-W1 对 2×2 的"descriptive rather than controlled factorial"完整 caveat 段——这是 v1 最有信誉价值的部分，一句都不能删。
- 7Wh2-W3 的 Bayesian-Sampler 论证（best fidelity 48.86 却 lowest AUC 81.17，pairwise ≠ conditional）——全场最强段落，原样保留。
- iRH3-W1 的"论文已有该评估"回应路径（§4.4 SHD on ground-truth DAGs）。
- q74j-W1 的三分类 baseline 选择原则（每类=奠基方法+2024/25 新方法）。
- General Response 已具备 Exp-1..4 编号、Artifacts 段、Revision plan——骨架好于 DTI v1，保留框架只修内容。
- 逐条 § / Table / Figure / 行号锚点的习惯（多数锚点核对无误，见 §1.3 末尾）。

### 1.2 组织问题清单（P1–P9）

| # | 问题 | 证据位置 |
|---|---|---|
| P1 | **最强事实反证被埋没且写反**：Appendix A 匿名仓库已随投稿提交，v1 在 q74j 文末却承认"absence of an anonymous code/data link"，把更正写成了道歉 | q74j "Reproducibility, Datasets, and Software" 节 |
| P3 | 直接回答不统一：7Wh2-W1 开头是让步句（"We should have cited…"），三段之后才出现 novelty 定位；iRH3-W2 结论（不做 n>200 但给出预期）埋在第三段 | 7Wh2-W1、iRH3-W2 |
| P4 | 证据 provenance/协议标注不系统：新实验有时带 seeds/模型信息（q74j Qwen3 表）有时全无（匿名化表未披露单 seed、gpt-5-mini、校准换算）；`[Submitted]` 证据从不显式标注 | 各文件 |
| P5 | Exp-# 编号只在 GR、q74j、iRH3 使用，7Wh2（恰是新实验最多的线程）全文未用；AC 无法把四条线程拼成一张图 | 7Wh2 全文 |
| P6 | 结尾无统一 ask：三份都以泛泛感谢收尾，未请求据新证据重审评分（q74j 的 1/1/1 更正后尤其应该 ask） | 三文件结尾 |
| P7 | 内部元信息（Reviewer Scores 表、词数行）混在可发布正文中 | 三文件头部 |
| P8 | 加粗-方括号摘要行（`**[Novelty limited…]**`）与标题、引文三重冗余 | 各条目 |
| P9 | 刻度不统一：同一线程内 utility 一会儿百分数（75.01、85.55）一会儿 0–1（0.830、AUC 0.865）；DCR 在论文 Table 2 是百分数（49.97）、在 rebuttal 表是 0–1（0.032） | 7Wh2-W1/W4、q74j-W2 |

### 1.3 数字与事实审计（must-fix；权威来源 = 论文 PDF + `new_experiments/` 源文件）

> 纯数值错误（原 N1–N7、N14：行列互换 / 跨文件漂移 / 无出处数值 / 错误数值比较）已拆入 `00b_NUMERIC_AUDIT_PLAN.md` 单独处理；下表只保留锚点修正、仓库事实更正与叙事口径三类（N8–N13、N15）。

| # | 位置 | v1 数值 | 权威数值（来源） | 处理 |
|---|---|---|---|---|
| N8 | 7Wh2-W1 | "the case study in **§4.5** shows qualitative similarity…" | 案例研究在 **Appendix H.1 / Figure 6**（§4.5 是 vary-n） | 改锚点 |
| N9 | 7Wh2 承诺 4 | "Correct the **Appendix §A.2** baseline description" | baseline 实现说明在 **Appendix G.2**（内容本身属实：G.2 称除 CLLM 外均用 SynthCity 实现，需为 GraDe 更正） | 改锚点，保留承诺 |
| N10 | q74j Repro 节 | "stems from the **absence** of an anonymous code/data link in the original submission" | **Appendix A（l.855–859）已提供匿名仓库链接** | 事实更正，前置到开场（§5.2）；提交前先点开链接确认仓库可访问、内容完整 |
| N11 | q74j Repro 节 | "datasets … cited in S4.1 and **Appendix A**" | 数据集明细在 **Appendix G.1 / Table 4** | 改锚点 |
| N12 | GR Exp-1 | "the inference-time generation mechanism is **the larger contributor** (AUC +0.076/+0.048, R² +0.166/+0.231)" | 推导值本身正确（0.828−0.752、0.829−0.782、0.570−0.404、0.591−0.360 ✓），但源文件 §4 明确禁止净效应/排序叙事（右列两格 generator 不同、seeds 5 vs 10） | 改为"separable and mutually transferable"叙事；四个差值可保留但须紧跟 caveat，或干脆只给 2×2 表 |
| N13 | GR Exp-4 vs q74j-W2 | GR："**consistent** advantages"；q74j："**modest** advantages … small relative to five-seed variation" | Qwen3 均差 +0.013/+0.014，std ±0.012–0.037，重叠 | 统一为 modest 口径（GR 向线程看齐） |
| N15 | q74j-W1 | baselines 锚点 "S4.1, l.306–312" | baselines 段在 **l.334–348**（l.312–328 是 Datasets 段） | 改锚点（次要） |

**已核对无误、可直接沿用**（v2 不必重查，来源=论文 PDF 与源文件逐项比对）：
- Table 3 消融差值：−1.6（No Structure）/ −1.1（No Topological Order）/ −4.4（Bayesian Sampler）/ −1.0（PC）/ −1.4（NoTears）；Bayesian Sampler 48.86 fidelity + 81.17 AUC。
- 三维画像：utility rank 1.00 / privacy rank 1.50 / fidelity rank 8.50；GReaT privacy risk 90.15%；BN fidelity rank 3.00；75.01 / 71.54 / 73.36（Table 1）。
- 2×2 表的 fidelity 与 |DCR−0.5| 列（0.537/0.154、0.540/0.150、0.580/0.053、0.595/0.032）；GR 的 "+0.076/+0.048/+0.166/+0.231" 推导。
- vary-n Anxiety 表全部 8 格 + "largest margin at n=20: +3.31 AUC"。
- 匿名化表 Original 列 = 论文 Table 1/2 值。
- 行号锚点：l.085–087、l.197、l.040–047、l.249–258、§3.2 l.281–297 + Eq.4、§4.2 l.394–421、l.417–421、l.356–359、§4.4 l.470–490、l.496–500、l.500–505、l.530–531、l.539–550、l.574–578、Figure 3/4、Table 3、n ∈ {20,50,100,200}。
- 12 baselines 的 5/4/3 分类及年份描述。

---

## 2. v2 总体写作策略

### 2.1 读者与目标

| Reviewer | OA | Conf | 关键子分 | 立场解读 | v2 目标与主战场 |
|---|---|---|---|---|---|
| 7Wh2 | **2** | 5 | Sound 3, Excit 1.5, Repro/Data/SW 4/4/4 | 唯一实质威胁=与 PAFT 的相似性；其余三条 W 均可用已有证据+让步化解。Conf 5 专家，容错为零 | **主战场**。W1 用"机制三分 + GraDe 已覆盖 + 2×2 双向迁移"守住 novelty 定位，其余条目短而准；目标 2→3，至少给 AC 提供"novelty 顾虑已被正面回应"的书面弹药 |
| q74j | **4** | 4 | Sound 4.5, Excit 3.5, **Repro/Data/SW 1/1/1** | champion；1/1/1 与另两位的 4/4/4、4/3/4 反差极大，几乎确定是没看到 Appendix A 的信息差 | 保住 4；开场事实更正 + artifact checklist 翻子分，给 AC 辩护弹药 |
| iRH3 | 3 | 3 | Sound 3.5, Excit 3 | W1 是可见性问题（§4.4 已做）；W3 实验已补；W2 是诚实的 scope 问题 | 争取 3→3.5/4：W1 亮已有证据，W3 给干净的同协议结果，W2 用 §4.5 + Appendix K.3 做有据的 scope 回应 |

字数向主战场倾斜：7Wh2 ≈ 1,150–1,250 词（W1 占 ~450），q74j ≈ 750，iRH3 ≈ 750，GR ≈ 350–400（均不含表格与引文）。

### 2.2 AAEA 微结构（每条目固定四段）

1. **Acknowledge**（≤1 句）：承认合理内核，措辞多样化（全文不得连续两条以 "We agree" 开头）。
2. **Answer**（1 句，`**Direct answer.**` 加粗开头）：立场一句说死。
3. **Evidence**：先 `[Submitted, §/Table/Appendix 锚点]` 后 `[New, Exp-#]`；新实验表格必须带协议标签（model / seeds / n / 换算方式）；表后一行 `**Takeaway:**`。
4. **Action**（1 句）：`**Revision (R#).** We will <动作> in §<x>.` 每条恰一个 R#，其余承诺收拢到结尾表。

### 2.3 证据 provenance 与协议标签

- `[Submitted, Appendix A]` 类标签用于"论文已有"的证据——回应"缺 X"类意见时**优先亮出**（q74j 的仓库、iRH3 的 §4.4、7Wh2 的 GraDe/K.2/H.1 均属此类；v1 有内容但从不标注）。
- `[New, Exp-#]` 用于 post-submission 证据，首次出现时给协议括号，如 *(gpt-5-mini, single seed 42, n=1000; we report deltas rather than absolute levels)*。
- **v1 遗漏的已有弹药，v2 必须用上**：Appendix A（仓库，q74j）；Appendix K.2（fidelity–privacy trade-off 的现成完整论证，7Wh2-W2/W3）；Appendix K.3（boundary conditions & "best suited for n ≤ 100"，iRH3-W2 与 7Wh2-W4 的 scope 句）；Appendix D（DAG 的 functional-not-ontological 定位，iRH3-W1 方向性问题的理论后盾）；Appendix H.1/Figure 6（案例研究，修正 N8 后用于 7Wh2-W1）；Appendix I/Table 6（14/16 cells，7Wh2-W1 的 supporting evidence 加一句）。
- 可选加分项（数据现成，`paft_three_variants_evaluation/results_summary.md`）：PAFT anon-headers（10 seeds：AUC 0.7672 vs full 0.7521）——定量确认 7Wh2-W4 中"PAFT 对 opaque schema 不敏感"的让步，展示我们连对方方法的稳健性都验证过了。

### 2.4 刻度与表格规范

- 同一响应内同一指标只用一种刻度：utility 建议全部百分数两位小数（与论文 Table 1 口径一致，2×2 表 ×100 换算并复核）；fidelity/DCR 若用 0–1 则表头注明，且与该表内其他指标一致。
- 表 ≤6 列；新实验在协议句中披露 seeds，只有各行 seed 数不同时才单设 Seeds 列；粗体只标"同列最优"，混协议行（如 2×2 的 5-seed 行 vs 10-seed 行）不参与互相加粗。
- blockquote 只用于 reviewer 原话；删除所有加粗-方括号摘要行（P8）。

---

## 3. 统一模板

### 3.1 文件头

```markdown
# Response to Reviewer X

<!-- internal: OA=?/Conf=?/…; word budget ~750; strip scores table to tracking.md -->
```

### 3.2 开场段（英文 stub；q74j 版含事实更正）

```markdown
We thank Reviewer X for the careful and constructive review. Below we respond to
each point in order. New evidence referenced in this response: (i) Exp-1 …;
(ii) Exp-2 …. Evidence already in the submission is marked [Submitted].
```

q74j 专用第 2 段（置于导览之前或紧随其后，参照 DTI-hwG5 Software 更正的处理）：

```markdown
Before the itemized responses, we would like to note one factual point regarding
the Reproducibility / Datasets / Software assessments (1/1/1): an anonymized code
repository with the full implementation and usage instructions was included in the
original submission (Appendix A, l.855–859: https://anonymous.4open.science/r/StructSynth-41DB).
We suspect this link may have been missed, and we additionally commit to releasing
preprocessed datasets, exact splits, configuration files, and seeds (checklist below).
```

### 3.3 条目模板

```markdown
## W2: <短标题>
> "<只引最关键的 1–2 句，省略处用 […]>"

<Acknowledge 一句.> **Direct answer.** <一句话立场>.

[Submitted, Table 2, §4.2] <已有证据>. [New, Exp-1] <新证据引言 (协议标签)>:

| …(≤6 列；仅当各行 seed 数不同时含 Seeds 列)… |

**Takeaway:** <一句>.

**Revision (R3).** We will <具体动作> in §<x>.
```

### 3.4 结尾模板

```markdown
## Summary of Revisions

| # | Change | Where |
|---|---|---|
| R1 | Cite and position PAFT; narrow the contribution statement | §1, §2 |
| R2 | … | … |

These commitments involve no claims beyond the evidence above. If our responses
resolve the reviewer's concerns, we would be grateful if the reviewer would
consider revisiting their assessment.
```

（q74j 版 ask 追加：*"…including the Reproducibility, Datasets, and Software dimensions, in light of the anonymized repository in Appendix A."*）

---

## 4. 共享证据块 E1–E6（单一数据源）

> 生成 v2 前先落地 `rebuttal-v2/evidence_blocks.md`：把下表每块的权威表格从源文件**完整抄录**并落实 §1.3 修正；三份 v2 草稿与 GR 的对应内容一律从该文件复制。Exp-#（reviewer 可见编号）与 E#（内部块编号）映射：Exp-1=E1(+E2)、Exp-2=E3、Exp-3=E4、Exp-4=E5。

| 块 | 内容 | 权威来源 | 需落实的修正 | 主用线程 | 引用线程 |
|---|---|---|---|---|---|
| E1 | PAFT×SS 双向 2×2（utility/fidelity/DCR + caveats） | `cross_validation_comparison.md` §0–§4、`cross_validation_table.tex`（数字已正确，可直接改写成 markdown） | N12；caveat 补一条"右列两格 generator 不同（gpt-4o-mini vs DeepSeek-V4-Flash）"（数值互换修正见 `00b_NUMERIC_AUDIT_PLAN.md`） | 7Wh2-W1 | GR |
| E2 | PAFT / GraDe / SS 机制三分 + GraDe Table 1 对比 | 论文 Table 1 + v1 机制段（文字质量好，保留） | —（GraDe 均值修正见 `00b_NUMERIC_AUDIT_PLAN.md`） | 7Wh2-W1 | GR 一句 |
| E3 | 匿名化同协议对照（no_anon vs field_anon）+ 图密度（62→19 / 56→47 edges）+ 跨 n 全表 | `task_field_anon_experiment/results_summary.md`、`rebuttal_table.tex`（两张现成 LaTeX 表） | 协议披露（gpt-5-mini、seed 42、n=100–1000）；叙事改为"分类稳、回归仅 n=1000 落后、fidelity 反升、稀疏图去伪边"（数值修正见 `00b_NUMERIC_AUDIT_PLAN.md`） | iRH3-W3 | 7Wh2-W4、GR |
| E4 | Post-cutoff vary-n（Anxiety + Salary，±std） | `vary_n_markdown_tables_calibrated.md` | 标注 5 seeds；校准法是否披露见 D1（Salary 行互换修正见 `00b_NUMERIC_AUDIT_PLAN.md`） | q74j-W2 | GR |
| E5 | Qwen3-32B backbone 检查 | **待定（D2）**——归档后以归档文件为准 | N13（modest 口径）（四个数字核对见 `00b_NUMERIC_AUDIT_PLAN.md`） | q74j-W2 | GR |
| E6 | Artifacts 清单（已提交：Appendix A 仓库；补充承诺：数据/splits/configs/seeds/预处理脚本） | 论文 Appendix A + v1 承诺列表 | N10、N11 | q74j 开场+Repro 节 | GR |

### 各块 canonical takeaway（英文，三线程与 GR 统一复用）

- **E1**: *Graph source and generation mechanism are separable and mutually transferable: PAFT-discovered FD graphs plug into StructSynth with near-paper utility (avg AUC 0.828 vs 0.830), and StructSynth-derived orders selectively improve PAFT's classification (avg AUC 0.752→0.782); PAFT retains the best pairwise fidelity while StructSynth keeps DCR closest to 0.50. We interpret this as compatibility evidence, not a controlled ablation.*
- **E2**: *StructSynth's contribution is not being the first structure-aware synthesizer, but executing a directed dependency graph as an inference-time generation plan for a black-box LLM — no parameter updates, unlike PAFT's permutation-compiled fine-tuning and GraDe's attention-mask injection; against GraDe under identical splits, StructSynth leads on all six datasets (avg 75.01 vs 62.73).*
- **E3**: *Under full task-and-field anonymization the discovered graph shrinks (62→19 edges on Anxiety) yet classification utility is preserved (AUC 0.871→0.877) and pairwise fidelity improves on both datasets; regression trails only at n=1000 (R² 0.569→0.470) while leading at n=100–500. Structural gains, not memorized column-name semantics, drive the improvements — though semantic priors do help regression at scale.*（协议句必须跟随：single-seed exploratory run with gpt-5-mini; we interpret deltas, not absolute levels.）
- **E4**: *On both post-cutoff datasets StructSynth leads CLLM at every n for classification (largest margin +3.31 AUC at n=20); regression is task-dependent — StructSynth leads only at n=100 on Salary. This confirms, on data the LLM has never seen, that structural guidance matters most under scarcity, with an honest task-dependence caveat.*
- **E5**: *Under Qwen3-32B, StructSynth shows modest advantages on both post-cutoff datasets, with mean differences small relative to five-seed variation — supporting backbone generality without overclaiming significance.*（数字以 D2 归档结果为准）
- **E6**: *The anonymized repository (Appendix A) already contains the full implementation; the revision will additionally ship preprocessed datasets, exact train/test splits, configs, and seeds.*

---

## 5. 各 reviewer 重组方案

### 5.1 reviewer_7Wh2.md（4W → 开场 + 4 条 + 结尾；正文 ~1,150–1,250 词）

| v1 | v2 | 预算 | 指令 |
|---|---|---|---|
| 开场 2 句 | 开场导览 | 90 | 致谢 + 承认 PAFT 缺引（保留 v1 的干脆）+ 新证据清单 (i) Exp-1 双向 2×2 (ii) Exp-2 匿名化 (iii) [Submitted] GraDe 已覆盖 FD-guided 类。删 Scores 表（P7） |
| W1 | W1（主战场） | 450 | 证据链重排为五步：① Acknowledge + **Direct answer**（*"The overlap is real at the level of 'discover structure, then use it' — but PAFT compiles FDs into a fine-tuning permutation, whereas StructSynth executes a directed graph as an inference-time plan for a black-box LLM; we will cite PAFT and narrow our claims accordingly."*）② 机制三分段（v1 文字好，保留；补 Eq.4/l.281–297 锚点）③ [Submitted] GraDe 对比④ [New, Exp-1] E1 的 2×2 表 + 完整 caveats（含新增的 backbone 差异句；N12）⑤ [Submitted] 支持证据一句带过：Table 3 消融 + **Appendix H.1/Figure 6** 案例（N8 修正锚点）+ Appendix I 14/16 cells。六条 revision commitments 压缩为 R1–R3（cite&position / narrow claims / 修 G.2（N9）），其余并入结尾表 |
| W2 | W2 | 140 | v1 结构好，保留；开头改 AAEA（Direct answer：*empirical diagnostic, not a claimed guarantee*）；补 [Submitted, Appendix K.2] 锚点（现成的 trade-off 论证）；R# 一条（privacy 措辞全局替换） |
| W3 | W3 | 150 | 保留 Bayesian-Sampler 论证与三维画像原文；补 Appendix K.2 锚点；与 GR 统一"utility 1.00 / privacy 1.50 / fidelity 8.50"三元组措辞 |
| W4 | W4 | 220 | 改用 E3 同协议表（D1）+ 图密度细节（19 vs 62 edges）；叙事修正：Anxiety 分类不降、Salary 回归在 n=1000 落后（附跨 n 小表或一句）；保留"PAFT 统计 FD 发现确实更稳"的让步，可选引 PAFT anon-headers 数据（§2.3）定量坐实；**新增联动句**：schema 不透明时可将统计发现的 FD 图接入 StructSynth（Exp-1 反向已证可行）——把 W1 与 W4 的证据焊在一起；[Submitted, Appendix K.3] boundary conditions 收尾 |
| Revision Summary | Summary of Revisions + ask | 120 | R# 表（R1 cite&position PAFT §1/§2；R2 narrow contribution claim；R3 修 G.2 GraDe 描述；R4 privacy 措辞；R5 三维 trade-off 措辞 §5；R6 匿名化实验进附录 + opaque-schema 限制；R7 结构度量 future work）+ 克制 ask |

### 5.2 reviewer_q74j.md（2W + minor + Repro → 正文 ~750 词）

| v1 | v2 | 预算 | 指令 |
|---|---|---|---|
| （无） | **开场：事实更正 + 导览** | 130 | §3.2 的 q74j 专用段（N10 更正，Appendix A 链接原文列出）+ 新证据 (i) Exp-3 vary-n (ii) Exp-4 Qwen3-32B。语气：更正信息差，不指责 |
| W1 | W1 | 150 | 保留三分类原则与"n=100 是 deliberate"论证；修 N15（l.334–348）；结尾一句：GraDe(2025)/SPADA-NF(2025)/TabSyn(2024) 保证了每类含当年 SOTA |
| W2 | W2 | 260 | ① Direct answer（选 Adult 的三理由压成两句：可比性 + 与 Table 3 消融同数据集的一致性）② [New, Exp-3] E4 表 + 5-seed ±std + Salary 诚实句照旧（行文本来就是对的）③ [New, Exp-4] E5 Qwen3 表（等 D2 归档）+ modest 口径（N13）④ R#：post-cutoff 结果进 §4.5/Appendix |
| Minor | Minor | 50 | 保留 v1（好回应），一句 R# |
| Repro 1/1/1 节 | **Artifact checklist** | 130 | 开场已做更正，此处改 checklist 逐项对应（RePair TyZt-W5 模式）：Code — [Submitted, Appendix A]；Datasets — 全部公开（G.1/Table 4，修 N11）；Splits/configs/seeds — 承诺随修订提供；预处理脚本 — 承诺。删除"we believe this stems from the absence…"整句 |
| Revision Plan | Summary of Revisions + ask | 110 | R# 表 + ask 点名三项子分（§3.4） |

### 5.3 reviewer_iRH3.md（3W → 正文 ~750 词）

| v1 | v2 | 预算 | 指令 |
|---|---|---|---|
| 开场 | 开场导览 | 70 | 新证据 (i) Exp-2 匿名化；已有证据 (ii) [Submitted] §4.4 SHD（direction-aware）。删 Scores 表 |
| W1 | W1 | 200 | v1 路径正确，保留"论文已含该评估"主线；微调三处：① Direct answer 前置（*"§4.4 already evaluates exactly this — SHD on three bnlearn ground-truth DAGs, and SHD counts edge reversals, so direction errors are directly penalized"*——把 reversal 这层含义说破，v1 没说）② 补 [Submitted, Appendix D]（DAG 的功能性定位：方向是生成调度所需，不是本体论断言——直接回应"direction 是否正确"背后的关切）③ 标题修订建议改稳妥措辞："Structural Recovery on Ground-Truth DAGs (including edge directions)"，避免 v1 的 "Edge Direction Accuracy" 对 SHD 的 overclaim |
| W2 | W2 | 230 | 重排：① Acknowledge + Direct answer（目标场景是 n≤200 的 low-data regime；未跑 n>200 是 scope 而非回避——一句说死）② [Submitted] §4.5/Figure 4：n→200 时 gap 收窄但 StructSynth 不劣化；Figure 3 SHD 中 FCI/NoTears 随 n 逼近——已有数据就是"trade-off 随 n 变化"的直接证据 ③ [Submitted, Appendix K.3] 引 boundary conditions（论文已写"best suited for n ≤ 100"）④ 预期收敛机制一段（v1 文字保留，但把"will **not** degrade"降格为 hypothesis 措辞：*we expect … and will state this as an explicit hypothesis*）⑤ R#：operating range + convergence 讨论进 Limitations |
| W3 | W3 | 250 | E3 权威载体（与 7Wh2-W4 同源，本线程放全表+跨 n 表，7Wh2 放摘要）：① Direct answer 扣 fairness 原话（*anonymization removes exactly the semantic advantage the reviewer identifies; what remains is a like-for-like structural comparison*）② 同协议表 + 协议披露 ③ 机制段（稀疏图去伪边→fidelity 反升；回归 n=1000 落后→语义先验对回归的真实贡献，诚实保留）④ R# |
| Revision plan | Summary of Revisions + ask | 100 | R# 表 + ask |

### 5.4 general_response.md（~350–400 词）

保留 v1 骨架（收敛概括 + Exp-1..4 总账 + Artifacts + Revision plan），修六处：
1. Exp-1 段：删"larger contributor"句（N12），换 E1 takeaway；四个差值若保留必须紧跟 caveat。
2. Exp-2 段：换 E3 口径（分类稳/回归 n=1000 落后/fidelity 反升 + 协议句）。
3. Exp-3 段 ✓ 基本不动（本来就与源一致）。
4. Exp-4 段：consistent → modest（N13）。
5. Artifacts 段：改为"repository **already included** in Appendix A; revision additionally ships data/splits/configs/seeds"（N10）。
6. Revision plan 的 (1)–(7) 与三线程 R# 编号对齐，逐条標注落点章节。

---

## 6. 写作规范 checklist（v2 草稿生成后逐项核对）

**数字**
- [ ] 所有共享数字与 `evidence_blocks.md` 一致（三份 + GR 做跨文件 diff）
- [ ] 数值错误审计（原 §1.3 N1–N7、N14 + 派生值重算：2×2 四个差值 / +3.31 / 62.73 / Δ 列）见 `00b_NUMERIC_AUDIT_PLAN.md`，须在其独立流程完成后回填 `evidence_blocks.md`
- [ ] 同一事实跨线程口径一致（seeds 数、模型名、n 范围、modest/consistent 措辞）

**锚点与事实**
- [ ] N8–N11、N15 锚点修正落实；新增引用（Appendix A/D/K.2/K.3/H.1/I）逐一对照 PDF
- [ ] Appendix A 仓库链接在提交前实际点开验证（可访问、含 README 与代码）
- [ ] 对照 `reviewer_reviews_only.md` 全文核对无遗漏意见（7Wh2 的四条 W、q74j 的 2W+1 minor、iRH3 的 3W；q74j 的 "Comments" 行已由 Minor 条目覆盖）
- [ ] 诚实让步三件套未被删除（§1.1）

**结构与语气**
- [ ] 每条 AAEA 完整；粗体 Direct answer 在证据之前；每条恰一个 Revision (R#)；结尾 R# 表与正文一一对应
- [ ] Exp-1..4 编号在**全部四份文件**中使用；`[Submitted]`/`[New]` 标签齐全，新实验首次出现带协议括号
- [ ] 无连续 "We agree" 开头；无 "significant(ly)"（新实验均未做显著性检验）；"will not degrade" 类断言均已降格为 hypothesis
- [ ] blockquote 仅用于 reviewer 原话；加粗-方括号摘要行已全删；Scores 表/词数行已移入 tracking.md

**格式**
- [ ] 表 ≤6 列、seed 信息不重复、同表同刻度、粗体规则统一
- [ ] OpenReview 预览：表格渲染、`$` 转义、粗体、引用
- [ ] 确认本轮 ARR/EMNLP 对 author response 的字符/长度限制（markdown 表格计入字符数）；超限预案：2×2 表砍 Generator/Learner 列入表注，vary-n 表两数据集拆分主/附

---

## 7. 执行步骤与阻塞项

**阻塞项（生成 v2 正文前需确认）**

- **D1（需用户拍板）— 匿名化实验的呈现口径**：
  推荐 **(a) 同协议原始数字**（no_anon vs field_anon 同为 gpt-5-mini/seed 42），只解读 Δ、附协议披露句——最经得起 Conf-5 reviewer 追问；代价是 DCR 绝对水平（0.69–0.93）与论文协议明显不同，必须靠"interpret deltas, not levels"句挡住。
  备选 **(b) 保留校准换算**（逐行 scaling 使 no_anon 锚定论文值）但必须显式披露换算方法，且 Anxiety anonymized AUC 修为 ≈0.870——注意这会把叙事反转为"匿名化在 Anxiety 上不降反升"。
  无论选哪个，v1 的 0.850 与"classification degrades modestly"叙事都不可保留（数值细节与出处见 `00b_NUMERIC_AUDIT_PLAN.md`）。另需确认该 run（NaiveHierCLLM 实现、gpt-5-mini）能否代表 StructSynth 主方法，回应中如何命名。
- **D2 — Qwen3-32B 结果归档**：从 `00_active/StructSynthFull/results/`（配置见 `.tmp_configs/postcutoff_*_qwen3_32b.yaml`）定位结果文件，归档到 `new_experiments/qwen3_32b_backbone/` 并核对 v1 的四个数字（数值审计见 `00b_NUMERIC_AUDIT_PLAN.md`）；未归档前 E5 不进 v2。

**工作流**

1. 处理 D1–D2（GraDe 溯源 D3 见 `00b_NUMERIC_AUDIT_PLAN.md`）。
2. 建 `rebuttal-v2/evidence_blocks.md`：按 §4 从源文件抄录 E1–E6 + 落实全部修正；同时建 `tracking.md` 收纳分数表/字数统计。
3. 按 §5 指令逐文件生成 v2（模板见 §3；证据块只复制不重敲）；顺序建议 q74j（最短、收益最确定）→ iRH3 → 7Wh2（最难）→ GR（最后写，索引其余三份）。
4. 一致性审计 pass：跨文件数字 diff → 锚点对照 PDF（数值错误审计与派生值重算见 `00b_NUMERIC_AUDIT_PLAN.md`）。
5. 压缩 pass：对照 §5 预算裁剪；表格瘦身预案见 §6。
6. 终检：§6 checklist 全过 → 剥离 internal 注释 → 定稿。
