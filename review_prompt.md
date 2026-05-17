# StructSynth 论文审阅优化提示词

请基于 `EMNLP26_StructSynth.pdf`（LaTeX 源码位于 `Latex-EMNLP/sections/`），以 EMNLP 审稿人视角对该论文进行系统性审阅与优化建议，重点关注以下两个方面：

## 一、篇幅压缩（EMNLP 正文限 8 页）

1. 逐节分析当前篇幅占比，识别可大幅删减或移至附录的内容；
2. 评估 Introduction 中四段式结构的冗余度（特别是 P1 问题铺垫与 P2 方法全景是否存在重叠），提出精简方案；
3. 检查 Related Work 是否存在与 Introduction 重复的综述内容，给出合并或压缩建议；
4. 审视 Methodology 中形式化定义（Problem Definition、公式推导）的必要性，区分核心贡献与可实现性细节；
5. Experiments 中的表格与图表布局是否可优化以节省空间。

## 二、关键问题识别

1. **技术贡献深度**：作为投稿 EMNLP（NLP 顶会）的论文，LLM 的使用方式（prompt-based BFS + autoregressive generation）是否具备足够的 NLP 技术创新性，还是更偏向 applied/data mining 范畴？
2. **实验设计完备性**：仅使用 `gpt-4o-mini` 单一模型、$n=100$ 单一数据规模、XGBoost 单一下游评估器是否充分？是否需要消融实验补充（如不同 LLM backbone、不同 $n$ 值、不同 downstream model）；
3. **方法论局限**：DAG 假设对无环性的要求是否限制了方法的适用范围？cycle resolution mechanism 的合理性是否有充分论证？
4. **与 baseline 的公平性**：StructSynth 使用 LLM 的 in-context learning，而 DGM baselines 从相同 100 样本训练，对比条件是否对等？
5. **可复现性**：prompt 模板、超参数（temperature=0.9、$s=1000$）的敏感性是否需要讨论？

请按**优先级排序**给出具体、可操作的修改建议，并标注每条建议的预期影响（高/中/低）。
