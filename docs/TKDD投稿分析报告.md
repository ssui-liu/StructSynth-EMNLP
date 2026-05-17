# ACM TKDD 投稿注意事项 — 调研分析报告

> **生成时间**：2026-04-17  
> **适用论文**：StructSynth — Dependency Structure Discovery for High-Fidelity Tabular Data Synthesis in Low-Data Regimes  
> **投稿类型**：KDD 草稿直接迁移至 TKDD 期刊投稿（非会议论文扩展）

---

## 一、期刊概况

### 1.1 基本信息

| 项目 | 内容 |
|:---|:---|
| **全称** | ACM Transactions on Knowledge Discovery from Data |
| **缩写** | TKDD |
| **出版商** | Association for Computing Machinery (ACM) |
| **Impact Factor** | 4.8（2025 年发布，基于 2024 年数据） |
| **h-index** | 77（SCImago） |
| **h5-index** | 49（Google Scholar, 2020–2024） |
| **JCR 分区** | Q1（Computer Science） |
| **审稿模式** | 单盲 (Single-blind) |
| **投稿方式** | 全年滚动接收（Rolling Submission） |
| **出版模型** | 2026 年起 ACM 全面 Open Access |
| **官方网站** | https://dl.acm.org/journal/tkdd |

### 1.2 期刊定位与覆盖主题

TKDD 专注于知识发现与数据分析的原创研究、综述和技术笔记。覆盖主题如下：

| 大类 | 具体方向 |
|:---|:---|
| **基础理论** | 数据挖掘基础、KDD 框架、数据挖掘语言 |
| **算法研究** | 可扩展/高效的数据挖掘与大数据分析算法 |
| **数据类型** | 图/网络、流数据、多媒体、高维数据、文本、Web、半结构化、时空数据 |
| **方法与应用** | 社区发现、社交网络分析、图挖掘、可视/交互式数据挖掘、安全与隐私 |
| **基础设施** | 分布式网络、云计算、大规模并行处理 |

> **StructSynth 匹配度评估**：论文研究表格数据合成中的依赖结构发现，属于 "算法研究 + 数据类型（结构化/表格数据）" 的交叉领域，与 TKDD Scope 高度契合。

---

## 二、格式与模板要求

### 2.1 LaTeX 模板规范

TKDD 使用 ACM 统一的 `acmart` 文档类，不同阶段的配置如下：

#### 审稿阶段（提交时）

```latex
\documentclass[manuscript, review]{acmart}
```

- `manuscript`：单栏排版，便于审稿人阅读
- `review`：启用行号，便于审稿人引用具体行
- 可选 `anonymous`（如需匿名审稿）

#### 最终提交阶段（录用后）

```latex
\documentclass[acmsmall]{acmart}
```

- 移除 `manuscript` 和 `review` 选项
- TAPS 系统自动生成 `acmsmall` 双栏排版

> ⚠️ **当前项目状态**：`main.tex` 使用 `\documentclass[acmsmall]{acmart}`，适用于最终版本。**投稿审稿阶段应改为 `manuscript, review` 选项。**

### 2.2 CCS 概念分类（必需）

三页及以上的论文必须包含 ACM Computing Classification System (CCS) 代码：

1. 访问 https://dl.acm.org/ccs/ccs.cfm
2. 选择相关描述符并设定优先级
3. 点击 "View CCS TeX Code" 生成代码
4. 将生成的 `\begin{CCSXML}...\end{CCSXML}` 和 `\ccsdesc{...}` 代码插入到 `\maketitle` 之前

> ⚠️ **当前项目状态**：`main.tex` 中**缺少 CCS 概念代码**，需补充。

### 2.3 参考文献

- **必须使用 BibTeX**（`\bibliography{references}` + `.bst` 文件），不允许 `\bibitem`
- 当前项目使用 `ACM-Reference-Format.bst`，✅ 符合要求

### 2.4 页数与篇幅

- TKDD **无严格页数限制**（不同于会议 8-9 页硬限）
- 篇幅应与贡献量匹配，一般正文 20–35 页（单栏格式）
- 避免过度冗长或内容稀薄

### 2.5 格式注意事项

- **禁止手动调整排版**：不得修改页边距、字号、行距，不得使用 `\vspace` 强行调整布局
- **仅使用 ACM 批准的 LaTeX 宏包**：参见 [TAPS Best Practices](https://www.acm.org/publications/taps/taps-best-practices)
- **图片路径**：确保使用相对路径（当前 `\graphicspath{{figures/}}` ✅ 符合）

---

## 三、KDD 草稿迁移至 TKDD 投稿须知

### 3.1 投稿性质说明

本次投稿为**直接投稿**，即将 KDD 版本的草稿迁移至 TKDD 期刊格式后直接提交：

- ✅ KDD 草稿**未正式发表**，不构成重复发表
- ✅ 无需满足 "25% 新增内容" 等扩展投稿要求
- ✅ 无需在稿件中声明与 KDD 的关系
- ⚠️ 但需确保论文**未同时投递其他期刊或会议**（ACM 禁止一稿多投）

### 3.2 会议 vs. 期刊写作风格差异

从 KDD 会议风格适配为 TKDD 期刊风格，需重点关注以下差异：

| 维度 | KDD 会议风格 | TKDD 期刊风格 |
|:---|:---|:---|
| **篇幅** | 8-9 页硬限制，内容高度压缩 | 无硬性限制，鼓励完整详尽的呈现 |
| **方法描述** | 关键步骤概述，细节省略 | 完整描述算法细节、推导过程、设计动机 |
| **实验部分** | 核心结果为主 | 更全面的实验设置描述、消融分析、参数敏感性 |
| **相关工作** | 简要综述 | 系统性文献调研，深入分析与定位 |
| **理论分析** | 可选，常置于附录 | 鼓励在正文中展开形式化分析 |
| **审稿标准** | 侧重新颖性和即时影响力 | 要求严谨性、完整性与长期存档价值 |
| **修改机会** | 有限（仅 rebuttal） | 支持 Major/Minor Revision 多轮迭代 |

### 3.3 迁移时的重点补充方向

1. **展开被压缩的内容**  
   将因会议页数限制而省略的技术细节、证明推导、设计讨论充分展开

2. **强化文献综述**  
   从简要概述升级为系统性调研，覆盖近年（尤其 2024–2025）最新工作

3. **丰富实验**  
   - 增加数据集数量和多样性
   - 增加基线方法（尤其是 2024–2025 年新方法）
   - 补充更深入的消融实验和参数敏感性分析
   - 增加案例分析和可视化

4. **补充期刊标准章节**  
   - Discussion：对结果进行深入讨论
   - Limitations：明确列出方法局限性
   - Future Work：提出具体可行的后续研究方向

5. **提升可复现性**  
   详细描述所有实验设置和超参数，提供代码仓库和数据集链接

---

## 四、审稿流程与时间线

### 4.1 流程概述

```
投稿 → EiC 初筛 → [Desk Reject / 分配 AE + 3 位审稿人]
                        ↓
              独立评审（约 2 个月）
                        ↓
              审稿决定：Accept / Minor Revision / Major Revision / Reject
                        ↓
               Minor Revision → 编辑审核 → Accept
               Major Revision → 重新评审（至少允许 1 轮）
```

### 4.2 关键时间节点

| 节点 | 时长 |
|:---|:---|
| 每轮审稿周期（提交 → 决定） | 目标 ≤ 90 天 |
| 审稿人完成评审 | 约 2 个月 |
| Major Revision 修改期 | 通常 2–3 个月 |
| Minor Revision 修改期 | 通常 1 个月 |
| 录用后 TAPS 排版 | 约 2–4 周 |

### 4.3 审稿决定类型

- **Accept**：直接录用，进入排版流程
- **Minor Revision**：小修，由编辑或指定人员审核，无需重新外审
- **Major Revision**：大修，修改后重新送审（至少允许 1 轮大修机会）
- **Reject**：拒稿

---

## 五、投稿常见风险与规避策略

### 5.1 Desk Reject（编辑直接拒稿）风险

| 风险因素 | 规避策略 |
|:---|:---|
| 主题不符合 Scope | 对照 TKDD 覆盖主题，参考近期发表论文确认匹配 |
| 格式不合规 | 使用最新 ACM 模板，确认 `manuscript` + `review` 选项 |
| 英语质量差 | 投稿前进行专业润色 |
| 明显贡献不足 | 确保有清晰、实质性的技术贡献 |
| 缺少 CCS 概念 | 生成并插入 CCS 代码 |

### 5.2 审稿被拒常见原因

| 原因 | 应对方式 |
|:---|:---|
| 新颖性不足 | 突出与现有方法的差异化贡献，充分对比最新工作 |
| 实验不充分 | 增加数据集、基线方法、消融实验 |
| 理论缺乏严谨性 | 补充形式化分析、收敛性/复杂度证明 |
| 写作不清晰 | 结构化呈现，添加 running example，图表辅助 |
| 可复现性差 | 提供代码/数据链接，详细描述实验设置 |
| 相关工作覆盖不全 | 系统性综述，不遗漏近两年关键工作 |

---

## 六、伦理、合规与版权

### 6.1 作者与署名

- 所有作者须有**实质性智力贡献**（构思、设计、分析或撰写/修订）
- 所有作者须提供有效 **ORCID**
- **禁止匿名署名**

### 6.2 生成式 AI 使用披露

ACM 要求对使用生成式 AI 工具（如 ChatGPT、LLM 等）进行明确披露：

| 使用程度 | 披露方式 |
|:---|:---|
| 小范围编辑（语法/拼写润色） | 在 Acknowledgments 中简要声明 |
| 实质性使用（生成段落/代码/数据） | 需设专门的 "Generative AI Usage" 章节 |

- AI 工具**不得列为作者**
- 作者对全部内容（包括 AI 生成部分）承担完全责任

### 6.3 Open Access 与版权

自 2026 年 1 月起，ACM 全面转向 Open Access 出版模式：

| 路径 | 说明 |
|:---|:---|
| **ACM Open（机构模式）** | 若通讯作者所在机构加入 ACM Open 计划，可免 APC |
| **APC（文章处理费）** | 未加入的机构需支付 APC，有减免政策 |

版权方面：
- 作者**保留版权**，授予 ACM 非独占出版许可
- 可选 CC-BY 或 CC-BY-NC-ND 等 Creative Commons 许可
- 作者保留在个人主页、机构仓库或基金要求的仓库中发布预印本的权利

### 6.4 学术诚信

- **禁止一稿多投**（Simultaneous Submission）
- 遵守 ACM 的 plagiarism / falsification / misrepresentation 政策
- 投稿内容须为原创，未在其他地方发表

---

## 七、录用后出版流程（TAPS）

### 7.1 步骤概览

1. **完成权利管理表** (Rights Form)
   - 选择 Creative Commons 许可类型
   - 替换 LaTeX 中的版权代码为 ACM 提供的具体值

2. **准备 ZIP 打包文件**
   ```
   submission.zip
   └── source/
       ├── main.tex
       ├── references.bib
       ├── ACM-Reference-Format.bst
       ├── figures/
       │   ├── fig1.pdf
       │   └── ...
       └── sections/
           ├── abstract.tex
           ├── introduction.tex
           └── ...
   ```
   - **不要包含 `acmart.cls`** 文件
   - 确保所有图片路径为**相对路径**
   - 仅保留一个含 `\documentclass` 的主文件

3. **上传至 TAPS Author Dashboard**
   - 完成权利表后会收到 TAPS 邮件邀请
   - 将 `tapsadmin@aptaracorp.awsapps.com` 加入可信联系人

4. **自动编译与校验**
   - TAPS 编译生成 PDF + HTML5 版本
   - 检查格式错误，如有问题需修改源码重新上传

5. **审校与发布**
   - 仔细校对生成的 PDF 和 HTML5
   - 确认无误后在 Dashboard 上正式批准发布

### 7.2 TAPS 常见问题

| 问题 | 解决方式 |
|:---|:---|
| 编译失败 | 检查是否使用了未批准的宏包 |
| 图片缺失 | 确认路径为相对路径，且包含在 ZIP 中 |
| 参考文献格式错误 | 确认使用 BibTeX 而非 `\bibitem` |
| 未收到 TAPS 邮件 | 检查垃圾邮件，加入信任列表 |

---

## 八、针对 StructSynth 的合规检查清单

基于对 `main.tex` 和项目结构的审查：

### ✅ 已满足

- [x] 使用 ACM `acmart` 文档类
- [x] 设置 `\acmJournal{TKDD}` 期刊标识
- [x] 使用 BibTeX + `ACM-Reference-Format.bst`
- [x] 图片使用相对路径 `\graphicspath{{figures/}}`
- [x] 包含 Abstract 和 Keywords
- [x] 项目结构清晰（`sections/`, `figures/` 分离）

### ⚠️ 需修改/补充

| # | 待办事项 | 优先级 | 说明 |
|:---|:---|:---|:---|
| 1 | **审稿格式切换** | 🔴 高 | 投稿时将 `\documentclass[acmsmall]{acmart}` 改为 `\documentclass[manuscript, review]{acmart}` |
| 2 | **添加 CCS 概念代码** | 🔴 高 | 在 `\maketitle` 前插入 CCS 分类代码 |
| 3 | **ORCID 信息** | 🔴 高 | 为所有作者添加 `\orcid{...}` 字段 |
| 4 | **内容展开** | 🟡 中 | 充分展开方法细节、理论推导、设计讨论 |
| 5 | **文献综述升级** | 🟡 中 | 系统化 Related Work，补充 2024–2025 年最新文献 |
| 6 | **实验丰富** | 🟡 中 | 增加数据集、基线、消融实验、参数分析 |
| 7 | **补充章节** | 🟡 中 | 添加 Discussion / Limitations / Future Work |
| 8 | **可复现性材料** | 🟡 中 | 准备代码仓库和数据集链接 |
| 9 | **AI 使用披露** | 🟢 低 | 如使用生成式 AI，在 Acknowledgments 或专节中声明 |
| 10 | **Acknowledgments** | 🟢 低 | 填写致谢内容（当前为 TODO） |
| 11 | **语言润色** | 🟢 低 | 投稿前全文 proofreading |

---

## 九、参考资源

| 资源 | 链接 |
|:---|:---|
| TKDD 官方主页 | https://dl.acm.org/journal/tkdd |
| ACM 作者信息页 | https://www.acm.org/publications/authors |
| ACM LaTeX 模板 | https://www.acm.org/publications/proceedings-template |
| CCS 分类系统 | https://dl.acm.org/ccs/ccs.cfm |
| ACM 出版政策 | https://www.acm.org/publications/policies/copyright-policy |
| TAPS 作者指南 | https://www.acm.org/publications/taps/word-template-workflow |
| TAPS Best Practices | https://www.acm.org/publications/taps/taps-best-practices |
| ACM Open Access | https://www.acm.org/publications/openaccess |
| ACM Author Gateway | https://authors.acm.org/ |
