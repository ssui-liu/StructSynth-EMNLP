# Manual Check Items — 需人工处理的遗留项

> 以下事项需要图片编辑工具或手动修改 bib 文件，无法通过 LaTeX 文本编辑完成。
> Created: 2026-05-22

---

## 1. Figure 1 内部标签更新

| Item | Detail |
|------|--------|
| 文件 | `figures/intro2.png` |
| 引用位置 | `sections/introduction.tex` L6 |
| Caption | 已修复（"through learned graphical structures"） |

### 需要检查 & 修改

打开编译后的 PDF，查看 Figure 1 图片内部是否仍有以下旧标签：

- [ ] "Dependency Structure Discovery" → 应改为 **"Evidence-Grounded Graph Induction"**
- [ ] "Structure-Guided Synthesis" → 应改为 **"Graph-Planned Conditional Synthesis"**

如有，需用图片编辑工具（如 PowerPoint / Figma / Illustrator）修改 `figures/intro2.png` 后重新导出。

---

## 2. Figure 2 (Pipeline) 内部标签 + Notation 更新

| Item | Detail |
|------|--------|
| 文件 | `figures/pipeline.png` |
| 引用位置 | `sections/related_work.tex` L6 |
| Caption | 已修复（"as a generation plan"） |

### 需要检查 & 修改

打开编译后的 PDF，查看 Figure 2 图片内部：

- [ ] 大标题 "Dependency Structure Discovery" → 应改为 **"1. Evidence-Grounded Graph Induction"**
- [ ] 大标题 "Structure-Guided Synthesis" → 应改为 **"2. Graph-Planned Conditional Synthesis"**
- [ ] Prompt box 中的 $\pi_{\text{generation}}$ → 应改为 **$\pi_{\text{generate}}$**（与 method.tex 和 appendix 统一）

如有，需修改 `figures/pipeline.png` 源文件后重新导出。

---

## 3. Figure 4 (vary_n) — Train Only 曲线确认

| Item | Detail |
|------|--------|
| 文件 | `figures/influence_n/vary_n_all.pdf` |
| 引用位置 | `sections/experiments.tex` L143-145 |
| Caption | *"Effect of training sample size ($n$) on downstream utility (AUC↑), statistical fidelity (↓), and privacy risk deviation Δ (↓) on the Adult dataset."* |

### 需要检查

打开编译后的 PDF，查看 Figure 4 的三个面板：

- [ ] **AUC 面板**：Train Only 基线是否出现？（预期：是）
- [ ] **Fidelity 面板**：Train Only 是否出现？（预期：不应出现——Train Only 无 synthetic data，fidelity 无定义）
- [ ] **Privacy Δ 面板**：Train Only 是否出现？（预期：不应出现——同上理由）

**如果 fidelity/privacy 面板中有 Train Only**：
- 方案 A：在 caption 末尾加一句 `Train Only is shown only for the AUC panel, as fidelity and privacy metrics are undefined without synthetic data.`
- 方案 B：重新生成图表，从 fidelity/privacy 面板中移除 Train Only 曲线

---

## 4. Figure 6 (Asia 结构对比) — "Captial" Typo 确认

| Item | Detail |
|------|--------|
| 文件 | `figures/collage_3x2.png` |
| 引用位置 | `sections/appendix.tex` L345 |

### 需要检查

YQ 指出 Figure 6 中有 "Captial Gain / Captial Loss" typo（应为 "Capital"）。

- [ ] 打开编译后的 PDF，在 Figure 6 (Asia dataset 的结构对比图) 中搜索 "Captial"
- [ ] 如果 typo 存在于图片中，需修改 `figures/collage_3x2.png` 源文件

> Note: `grep "Captial" sections/appendix.tex` 返回 0——typo 不在 LaTeX 文本中，只可能在图片内部标签。但 Asia dataset 只有 8 个节点（asia, smoke, tub, lung, bronc, either, xray, dysp），不含 "Capital Gain/Loss"。此 typo 可能出现在其他 dataset 的图表中（如 Adult dataset 的依赖图），请全面检查所有含 Adult 特征名的图表。

---

## 5. Bergsma (2013) 引用 — 手动添加 BibTeX

| Item | Detail |
|------|--------|
| 当前状态 | `sections/appendix.tex` L69 手写引用 "Bergsma and Wicher (2013)"，无 `\cite{}`，`references.bib` 中无条目 |
| 注意 | 作者全名是 **Wicher Bergsma**（单一作者，Wicher 是 first name），非两人合著 |

### 需要执行

**Step 1**：在 `references.bib` 中添加以下条目：

```bibtex
@article{bergsma2013bias,
  title={A bias-correction for {Cram\'er's V} and {Tschuprow's T}},
  author={Bergsma, Wicher},
  journal={Journal of the Korean Statistical Society},
  volume={42},
  number={3},
  pages={323--328},
  year={2013},
  publisher={Elsevier}
}
```

**Step 2**：修改 `sections/appendix.tex` L69：

```
Before:
the bias correction proposed by Bergsma and Wicher (2013).

After:
the bias correction proposed by \citet{bergsma2013bias}.
```

> `\citet` 在 natbib 下渲染为 "Bergsma (2013)"。如 EMNLP 模板不支持 `\citet`，改用 `\cite{bergsma2013bias}` 即渲染为 "(Bergsma, 2013)"。

**Step 3**：编译后确认引用渲染正确，bibliography 中出现该条目。

---

## 6. References 格式 — "and 1 others" 确认

| Item | Detail |
|------|--------|
| 当前状态 | `references.bib` L456 Naik et al. 条目使用 `and others`，bibtex 渲染可能生成 "and 1 others" |

### 需要检查

- [ ] 编译 PDF，在 References 部分搜索 "Bifulco" 所在的条目
- [ ] 检查是否显示为 "Carlo Bifulco, and 1 others"（不正确）
- [ ] 如果是，修改 `references.bib` L456：删除 `and others`，只保留到 `Bifulco, Carlo`，让 bib style 自动处理截断

---

## 检查优先级

| # | 项目 | 优先级 | 工具 |
|---|------|--------|------|
| 5 | Bergsma bib | **HIGH** — 引用格式问题，reviewer 一眼可见 | 文本编辑 |
| 1 | Figure 1 标签 | **HIGH** — 图文不一致，reviewer 会注意 | 图片编辑 |
| 2 | Figure 2 标签 | **HIGH** — 同上 | 图片编辑 |
| 4 | Captial typo | **MEDIUM** — 如果存在是显眼错误 | 图片编辑 |
| 3 | Figure 4 Train Only | **MEDIUM** — 可能无问题 | 查看 PDF |
| 6 | "and 1 others" | **LOW** — 可能是 bib style 的正常行为 | 查看 PDF |
