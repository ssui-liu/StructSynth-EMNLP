# TKDD 期刊投稿 — 正文内容改进 Checklist

> 基于当前迁移完成的版本，以下为除 Appendix 之外的可优化点。

---

## 🔴 高优先级（投稿前必须完成）

### LaTeX 配置
- [ ] **审稿格式切换**：将 `\documentclass[acmsmall]{acmart}` 改为 `\documentclass[manuscript, review]{acmart}`
- [ ] **添加 CCS 概念代码**：在 `\maketitle` 前插入 ACM CCS 分类代码（从 [ACM CCS](https://dl.acm.org/ccs/ccs.cfm) 生成）
- [ ] **补充 ORCID**：为所有作者添加 `\orcid{...}` 字段

### 正文结构
- [ ] **补充 Discussion 章节**：在 Experiments 和 Conclusion 之间添加独立的 Discussion 节，深入讨论：
  - StructSynth 在哪些场景下表现优异、哪些场景受限
  - 结构发现质量与下游性能之间的因果关系分析
  - 与传统因果推断方法的本质区别
- [ ] **补充 Limitations 章节**：明确列出方法局限性（期刊审稿人高度关注），例如：
  - 依赖 LLM 先验知识的局限
  - 对特定数据类型（如纯数值/高维稀疏表格）的适用性
  - API 调用成本与可扩展性
  - DAG 假设（不支持环形依赖 / 双向关联）
- [ ] **扩展 Conclusion**：当前仅 3 行，期刊版需扩展至 8-15 行，包含：
  - 核心贡献回顾
  - 关键实验发现总结
  - 具体 Future Work 方向

---

## 🟡 中优先级（显著提升论文质量）

### Introduction (`introduction.tex`)
- [ ] **补充贡献量化**：在 contributions 列表中加入更具体的性能数据（如"+3.47 AUC pts vs. best baseline"）
- [ ] **添加论文组织说明**：在 Introduction 末尾增加 "The remainder of this paper is organized as follows..." 段落（期刊标准做法）

### Related Work (`related_work.tex`)
- [ ] **更新 2024-2025 最新文献**：补充近两年的关键工作，特别是：
  - 表格数据合成新方法（TabGen-ICL 已有，检查是否有遗漏）
  - LLM for structured data 领域新进展
  - 因果发现与结构学习新方法
- [ ] **添加对比定位表**：用 Table 或 itemize 系统对比 StructSynth 与关键方法的差异（结构发现方式、生成策略等）

### Methodology (`method.tex`)
- [ ] **补充 Complexity Analysis**：添加时间/空间复杂度分析子节：
  - BFS 结构发现的查询复杂度 vs. pairwise 方法
  - 拓扑分层生成的 LLM 调用次数
- [ ] **补充 Convergence / Termination 讨论**：BFS + 环消除过程的终止性保证
- [ ] **添加 Running Example**：用一个小规模数据集（如 3-4 个特征）贯穿方法各步骤，直观展示 pipeline

### Experiments (`experiments.tex`)
- [ ] **增加参数敏感性分析 (Parameter Sensitivity)**：
  - few-shot 样本数 $k$ 的影响
  - LLM temperature 的影响
  - 关联分数阈值对图结构的影响
- [ ] **增加 Error/Failure Case Analysis**：
  - StructSynth 表现不佳的具体场景分析
  - 结构发现失败时的降级策略讨论
- [ ] **增加更多数据集**（如果可行）：补充 2-3 个新数据集以增强泛化性论证
- [ ] **增加统计显著性检验**：对主要结果表添加 paired t-test 或 Wilcoxon 检验的 p-values

---

## 🟢 低优先级（锦上添花）

### 写作与格式
- [ ] **填写 Acknowledgments**：当前为 `% TODO`，需填写资助信息和致谢
- [ ] **AI 使用披露**：如使用了生成式 AI 辅助，在 Acknowledgments 中声明
- [ ] **全文语言润色**：投稿前进行 proofreading（注意会议风格 vs. 期刊风格的措辞差异）
- [ ] **检查 future tense 使用**：期刊论文更多使用 present tense 描述方法和结果

### 可复现性
- [ ] **准备代码仓库**：GitHub/anonymous repository 链接
- [ ] **数据集可获取性**：确保所有数据集有公开链接或说明获取方式
- [ ] **补充 Reproducibility Statement**（可选但推荐）

### 图表优化
- [ ] **检查所有图表在单栏格式下的可读性**：`manuscript` 单栏排版下 `table*` 和 `figure*` 的宽度适配
- [ ] **统一图表风格**：确保所有图表的字体大小、颜色方案一致
- [ ] **为关键图表添加 caption 中的 takeaway**：每个表/图的 caption 应包含核心结论

### 引用完整性
- [ ] **检查 .bib 文件完整性**：确保所有新增引用（结构学习部分）在 `references.bib` 中有对应条目
- [ ] **检查引用格式一致性**：所有 `\cite` 使用正确（区分 `\cite` / `\citet` / `\citep`）
