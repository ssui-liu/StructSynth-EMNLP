# Rebuttal v2 数值一致性审计计划（「数字不一致」专项）

**来源**：从 `00_V2_WRITING_PLAN.md` 拆出。主写作计划专注重组 / 结构 / 叙事，本文件独占「数字不一致」的审计与修正。
**范围边界**：
- **本文件负责**：纯数值错误 N1–N7、N14（行列互换 / 跨文件漂移 / 无出处数值 / 错误数值比较）+ 派生值重算 + 决策点 D3（GraDe 溯源）。
- **仍由主计划负责**：锚点修正（N8/N9/N11/N15）、仓库事实更正（N10 / P1）、叙事口径（N12/N13）、决策点 D1（匿名化呈现口径）与 D2（Qwen3-32B 归档）——但 D1/D2 的具体数值细节以本文件 N6 / N14 为准。
**权威来源**：论文 PDF + `new_experiments/` 源文件。证据块一律从源文件**完整抄录**，禁止手敲或凭记忆复述。
**落点**：所有修正最终落到 `rebuttal-v2/evidence_blocks.md`（E1–E5）；三份 v2 草稿与 GR 只从该文件复制数字。
**生成日期**：2026-07-13

---

## 0. 为什么这是最高优先级

7Wh2 是 Confidence 5 的领域专家（"read the paper very carefully"），且 AC 会通读全部线程。表格与自身行文矛盾（N1）、两条线程对同一实验给出不同数字（N3）一旦被发现，直接反噬三份回应的全部可信度。

---

## 1. 三处严重数字事故（原主计划 TL;DR 第 2 项）

修复三处严重数字事故（详见 §4 审计表）：q74j 的 Salary vary-n 表**两行互换**（表与自己的行文、与 General Response、与校准源三方矛盾）；7Wh2 的 2×2 表 **R² 两格互换 + FD-prior 行整行过期**（与 General Response 的推导值直接冲突）；匿名化表的 Anxiety anonymized AUC **0.850 无任何出处**（按同表其余 cell 的换算规则应为 ≈0.870，且方向相反：匿名化在 Anxiety 上并未降低 utility）。

---

## 2. GraDe 对比修正（原主计划 TL;DR 第 4 项）

Table 1 中 GraDe 平均分是 **62.73**，v1 写成 51.05（恰为 Table 2 中 BN 的 fidelity 平均值，串行复制错误）；"75.01 vs 51.05" 全部改为 "75.01 vs 62.73"。

---

## 3. 问题定性（原主计划 P2）

| 问题 | 证据位置 |
|---|---|
| **跨文件 / 文件内数字漂移**（本文件 N1–N7），其中 N1 是表格与同文件行文自相矛盾 | q74j-W2、7Wh2-W1、7Wh2-W4/iRH3-W3 |

---

## 4. 数值与事实审计表（N1–N7、N14；must-fix；权威来源 = 论文 PDF + `new_experiments/` 源文件）

| # | 位置 | v1 数值 | 权威数值（来源） | 处理 |
|---|---|---|---|---|
| N1 | q74j-W2 Salary vary-n 表 | CLLM 48.16/52.34/54.53/61.39；SS 50.56/54.90/55.98/63.54 | CLLM **50.56/54.90**/54.53/**63.54**；SS **48.16/52.34**/55.98/**61.39**（`vary_n_markdown_tables_calibrated.md`，其 Note 明确 n=20/50/200 三列曾互换并已修正） | v1 表是修正前朝向：n=20/50/200 三列两行互换。**表格与同文件行文（"CLLM is ahead at other sample sizes (n=200: 63.54 vs 61.39)"）及 GR 均矛盾**。照源文件重抄，附 ±std |
| N2 | 7Wh2-W1 2×2 表 PAFT 两行 R² | PAFT full 0.360；PAFT+SS graph 0.404 | PAFT full **0.404**；PAFT+SS graph **0.360**（`cross_validation_comparison.md` §0；`cross_validation_table.tex` 同） | 两格互换，照源改写 |
| N3 | 7Wh2-W1 2×2 表 SS+PAFT-FD 行 | AUC 0.808 / R² 0.550 | **0.828 / 0.570**（`paft_fd_prior_deepseek_v4_flash/results_summary.md`：AUC 均值 0.8280、R² 0.5697） | 过期数值。GR 的 "+0.076/+0.166" 由 0.828/0.570 推出——v1 两文件对同一实验数字互相矛盾 |
| N4 | 7Wh2-W1 GraDe 平均 | "avg. 75.01 vs. **51.05**" | GraDe Table 1 平均 = **62.73** | 51.05 恰为 Table 2 中 BN 的 fidelity 平均，疑为串行复制。"outperforms on all six datasets" 本身成立（逐列核对 ✓），只改均值。溯源见 D3 |
| N5 | q74j-W1 | "TabDDPM and TabSyn … (avg scores **63.69 and 68.04**)" | Table 1：DDPM **63.68**、TabSyn **69.64** | 改写（68.04 无出处） |
| N6 | 7Wh2-W4 & iRH3-W3 匿名化表 | Original=论文值（0.865/0.579/0.447；0.560/0.646/0.501）vs Anonymized=0.850/0.534/0.564；0.462/0.615/0.412 | 同协议源（`task_field_anon_experiment/results_summary.md`，n=1000）：Anxiety no_anon→field_anon AUC **0.871→0.877**、fidelity 0.531→0.490、DCR 0.690→0.870；Salary R² **0.569→0.470**、fidelity 0.709→0.674、DCR 0.931→0.766 | v1 表为"论文原值 × 单 seed 校准换算"混合口径且未披露；除 Anxiety AUC 外各 cell 均可由"no_anon 锚定论文值的逐行 scaling"复推，**唯 Anxiety anonymized AUC 按同规则应 ≈0.870（高于 0.865），v1 写 0.850 且无出处、方向反转**。呈现口径见决策点 D1（主计划 §7） |
| N7 | iRH3-W3 / GR | "worst case R² 0.462 remains (well) above **unstructured baselines** in Table 1" | Table 1 Salary 列：CLLM **54.53**、GReaT **51.43**、TabSyn **47.17** 均高于 46.2（或修正后的 47.0） | 该句不成立，撤回或收窄为"高于多数 DGM 基线、与最强 DGM 相当"（TVAE 46.18、CTGAN 46.17 之上，但 TabSyn/GReaT/CLLM 之下） |
| N14 | q74j-W2 Qwen3-32B 表 | 0.8432±0.0118 / 0.8564±0.0141；0.5179±0.0374 / 0.5318±0.0355 | `EMNLP_Rebuttal/new_experiments/` 内**无归档源**（仅 `00_active/StructSynthFull/.tmp_configs/postcutoff_*_qwen3_32b.yaml` 证明实验存在） | **阻塞项 D2（主计划 §7）**：定位结果文件、归档进 `new_experiments/`、核对四个数字后方可进 v2 |

---

## 5. 落点映射（各 N# 修正落在哪个证据块 / 线程 / 决策点）

| N# | 证据块（主计划 §4） | 主用 / 引用线程 | 关联决策点 |
|---|---|---|---|
| N1 | E4（vary-n Salary） | q74j-W2；GR | — |
| N2 | E1（2×2 PAFT R²） | 7Wh2-W1；GR | — |
| N3 | E1（2×2 SS+PAFT-FD 行） | 7Wh2-W1；GR | — |
| N4 | E2（GraDe 均值） | 7Wh2-W1；GR 一句 | D3（本文件 §6） |
| N5 | —（直接引论文 Table 1） | q74j-W1 | — |
| N6 | E3（匿名化同协议对照） | iRH3-W3；7Wh2-W4；GR | D1（主计划 §7，呈现口径） |
| N7 | E3 | iRH3-W3；GR | — |
| N14 | E5（Qwen3-32B backbone） | q74j-W2；GR | D2（主计划 §7，归档） |

---

## 6. 决策点 D3

- **D3 — GraDe 51.05 溯源**：默认按 Table 1 改 62.73；若 51.05 另有协议出处，需注明协议或仍改用 Table 1 口径。

> 关联决策点（主体在主计划 §7，数值细节以本文件为准）：**D1** 匿名化呈现口径（同协议原始 Δ vs 校准换算，涉及 N6 的 0.850/≈0.870）；**D2** Qwen3-32B 结果归档（涉及 N14 的四个数字）。

---

## 7. 数值核对 checklist

- [ ] 所有共享数字与 `evidence_blocks.md` 一致（三份 v2 + GR 做跨文件 diff）
- [ ] 本文件 N1–N7 全部落实；N14（Qwen3）已归档核对
- [ ] 派生值重算：2×2 的四个差值、+3.31、62.73、Δ 列
- [ ] 同一事实跨线程数值口径一致（seeds 数、模型名、n 范围）
- [ ] N1（Salary 行互换）、N2（2×2 R² 互换）、N6（Anxiety AUC 0.850）三处"表与行文 / 跨文件"矛盾已消除

---

## 8. 工作流（与主计划衔接）

1. 逐条落实 N1–N7、N14 的权威数值，抄录进 `rebuttal-v2/evidence_blocks.md` 对应块（N1→E4、N2/N3→E1、N4→E2、N6/N7→E3、N14→E5）。
2. 处理 D3（GraDe 溯源）；协助主计划确认 D1（匿名化口径）与 D2（Qwen3 归档）中的数值。
3. 派生值重算（2×2 四个差值、+3.31、62.73、Δ 列），复核无误。
4. 跨文件数字 diff（三份 v2 + GR ↔ `evidence_blocks.md`）。
5. **回填主计划**：`evidence_blocks.md` 数值就绪后通知主计划 §5，各线程方可引用；主计划 §6 的"数值错误审计"复选框指向本文件完成状态。
