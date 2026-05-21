# Level 10 Audit Report: EMNLP / ACL Specific Requirements

**Paper:** StructSynth: Dependency Structure Discovery for High-Fidelity Tabular Data Synthesis in Low-Data Regimes  
**Date:** 2026-05-22

---

## 10.1 Anonymization (for review submission)

### 10.1.1 Review mode flag
- **PASS.** `\usepackage[review]{acl}` is correctly set at `main.tex:18`.
- The `acl.sty` file confirms that the `review` option enables `\acl@anonymizetrue`, `\acl@linenumberstrue`, and `\acl@pagenumberstrue` (acl.sty:19). The `\outauthor` command (acl.sty:129-136) replaces the author block with "Anonymous ACL submission" when anonymize is true.

### 10.1.2 Author block contains identifying information
- **WARNING (low risk).** The `\author{...}` block at `main.tex:93-103` contains full author names, affiliations, and email addresses:
  - `main.tex:94`: Siyi Liu
  - `main.tex:95`: The Hong Kong University of Science and Technology (Guangzhou)
  - `main.tex:96`: `ssui.liu1022@gmail.com`
  - `main.tex:97`: Yujia Zheng
  - `main.tex:98`: Carnegie Mellon University
  - `main.tex:99`: `yujiazh@cmu.edu`
  - `main.tex:100`: Yongqi Zhang (Corresponding author)
  - `main.tex:101`: The Hong Kong University of Science and Technology (Guangzhou)
  - `main.tex:102`: `yzhangee@connect.ust.hk`
  
  **Mitigated:** Because the `[review]` option is active, `acl.sty` automatically suppresses this block and displays "Anonymous ACL submission" instead. This is standard practice -- authors fill in the block but it is hidden during review. However, if the `.tex` source is shared with reviewers (e.g., via supplementary materials), identities would be exposed. Ensure the source code is NOT included in the review submission package.

### 10.1.3 Self-citations revealing author identity
- **PASS (with minor note).** No self-identifying language was found (no "our prior work", "we previously showed", "in our earlier work", etc.). All citations use third-person neutral language.
- **Minor note:** The reference `zheng2024causal` (Causal-Learn library, cited at `appendix.tex:191`) lists "Yujia Zheng" as a co-author, who is also a paper author. However, this is a widely-used open-source library cited as a tool dependency, not a self-promotional citation. The citation language ("we utilize the ... Causal-Learn library") is neutral and does not reveal authorship. **Risk: Very low.**

### 10.1.4 Personal URLs, GitHub repos, university-specific resources
- **PASS.** No GitHub URLs, personal websites, or repository links were found anywhere in the paper body, appendix, or section files.

### 10.1.5 Acknowledgments section
- **PASS.** The acknowledgments section is properly commented out at `main.tex:128-129`:
  ```
  % \section*{Acknowledgments}
  % TODO: Add acknowledgments in the camera-ready version.
  ```

### 10.1.6 Links to non-anonymous repositories
- **PASS.** No links to any repositories (anonymous or otherwise) were found in the manuscript.

---

## 10.2 Ethics & Reproducibility

### 10.2.1 Limitations section
- **PASS.** A substantive Limitations section is present at `limitations.tex:1-14`. It covers three meaningful limitations:
  1. **LLM semantic prior** -- degradation with opaque/anonymized feature schemas
  2. **DAG assumption** -- inability to represent cyclic or bidirectional dependencies
  3. **LLM API dependence** -- cost, reproducibility, and API version sensitivity

### 10.2.2 Ethics statement
- **FAIL.** No explicit ethics statement or broader impact statement is present anywhere in the paper. For EMNLP, while an ethics statement is not always mandatory, it is strongly recommended, especially for papers involving synthetic data generation which has dual-use potential (e.g., generating fake data for deception, privacy implications of generating realistic personal records).

### 10.2.3 Implementation details for reproducibility
- **PASS.** Implementation details are well-documented:
  - LLM used: `gpt-4o-mini` with temperature 0.9 (`experiments.tex:15`)
  - Software libraries: Langchain and Causal-Learn (`appendix.tex:191`)
  - Baseline implementations: SynthCity library with default hyperparameters (`appendix.tex:187`)
  - Experimental protocol: 10 repetitions with seeds 42-51 (`appendix.tex:183`)
  - Data splits: 80:20 train/test ratio (`appendix.tex:183`)

### 10.2.4 Hyperparameter settings
- **PASS.** Comprehensive hyperparameter table provided at `appendix.tex:193-233` (Table in Appendix), covering LLM settings, XGBoost, Random Forest, Logistic Regression, MLP, and PC algorithm parameters.

### 10.2.5 Computational cost (GPU hours, hardware)
- **FAIL.** No mention of computational cost, GPU/CPU hours, hardware specifications, or wall-clock time anywhere in the paper. The token usage analysis in `appendix.tex:393-444` reports token counts (a proxy for API cost), which is helpful but does not constitute full computational cost reporting. Missing: total API cost in dollars, wall-clock time per experiment, hardware used for baseline DGM training, total number of API calls.

### 10.2.6 Commitment to release code/data
- **FAIL.** No mention of code release, data availability, or any commitment to open-source the implementation. No supplementary material or anonymous repository is referenced. This is a significant gap for reproducibility.

---

## 10.3 Responsible NLP Checklist Readiness

### 10.3.1 Discussion of potential negative societal impacts
- **FAIL.** The paper does not discuss any negative societal impacts. Relevant concerns that should be addressed include:
  - Synthetic tabular data generation could be misused to fabricate realistic-looking records (e.g., fake medical records, fraudulent financial data)
  - Privacy risks of generating data that closely resembles real individuals (the paper measures privacy risk but does not discuss adversarial misuse)
  - Potential for reinforcing biases present in the training data through structure-preserving synthesis
  - The use of commercial LLM APIs (data sent to third-party servers) when working with sensitive datasets

### 10.3.2 Dataset documentation (source, size, license)
- **PARTIAL PASS.** Dataset details are provided in `appendix.tex:160-183` (Table with dataset characteristics including domain, number of features, task type). Dataset sources are cited with references. However:
  - **Missing:** No dataset licenses are documented for any of the six datasets
  - **Missing:** No total dataset sizes (only that 100 samples are subsampled for training)
  - The datasets are cited via references but explicit URLs or license terms are absent

### 10.3.3 Confidence intervals or significance tests
- **PASS.** All main results report mean +/- standard deviation across 10 runs (`experiments.tex:15`). All result tables include standard deviation values. This provides a measure of variability, though formal statistical significance tests (e.g., paired t-tests, Wilcoxon) are not performed.

---

## 10.4 Formatting Compliance

### 10.4.1 Official ACL style file
- **PASS.** The paper uses the official ACL style file (`acl.sty`), sourced from `https://github.com/acl-org/acl-style-files/`.

### 10.4.2 Line numbers enabled for review
- **PASS.** The `[review]` option at `main.tex:18` enables line numbers automatically.

### 10.4.3 Page limit compliance
- **LIKELY PASS.** The main body sections (abstract through conclusion) contain a reasonable amount of content consistent with the typical 8-page EMNLP limit (excluding references and appendix). The Limitations section does not count toward the page limit per EMNLP policy. Exact page count cannot be verified without compilation, but the content volume appears compliant.

### 10.4.4 References section format
- **PASS.** References are handled via `\bibliography{references}` at `main.tex:135`, using the natbib format automatically applied by `acl.sty`.

### 10.4.5 Appendix placement (after references)
- **PASS.** The appendix correctly appears after the references section:
  - `main.tex:135`: `\bibliography{references}` (references)
  - `main.tex:140-142`: `\newpage`, `\appendix`, `\input{sections/appendix}` (appendix after references)

---

## Summary of Findings

| Item | Status | Severity |
|------|--------|----------|
| 10.1.1 Review mode flag | PASS | -- |
| 10.1.2 Author block | PASS (auto-suppressed) | -- |
| 10.1.3 Self-citations | PASS (minor note on zheng2024causal) | Low |
| 10.1.4 Personal URLs/repos | PASS | -- |
| 10.1.5 Acknowledgments | PASS | -- |
| 10.1.6 Non-anonymous repos | PASS | -- |
| 10.2.1 Limitations section | PASS | -- |
| 10.2.2 Ethics statement | **FAIL** | Medium |
| 10.2.3 Implementation details | PASS | -- |
| 10.2.4 Hyperparameters | PASS | -- |
| 10.2.5 Computational cost | **FAIL** | Medium |
| 10.2.6 Code/data release | **FAIL** | Medium |
| 10.3.1 Negative societal impacts | **FAIL** | Medium |
| 10.3.2 Dataset documentation | PARTIAL PASS | Low-Medium |
| 10.3.3 Confidence intervals | PASS | -- |
| 10.4.1 ACL style file | PASS | -- |
| 10.4.2 Line numbers | PASS | -- |
| 10.4.3 Page limit | LIKELY PASS | -- |
| 10.4.4 References format | PASS | -- |
| 10.4.5 Appendix after references | PASS | -- |

**Overall: 13 PASS, 4 FAIL, 1 PARTIAL PASS, 2 informational notes.**

## Recommended Actions (Priority Order)

1. **Add an Ethics / Broader Impact statement** -- Discuss dual-use risks of synthetic data generation, potential for bias amplification, and privacy considerations when using commercial LLM APIs with sensitive data. This can be added as a short section after Limitations or integrated into the Limitations section.

2. **Add computational cost information** -- Report wall-clock time, total API cost, and hardware used for baseline experiments. The token usage table in the appendix is a good start but should be supplemented with actual cost and time figures.

3. **Add a code/data release commitment** -- Include a statement such as "Code and data will be made available upon acceptance" or provide an anonymous repository link (e.g., anonymous GitHub).

4. **Discuss negative societal impacts** -- Address misuse potential (fake record generation), bias propagation, and the implications of sending potentially sensitive data to commercial LLM APIs.

5. **Document dataset licenses** -- Add license information for each dataset to the dataset summary table in the appendix, or note the terms of use.

6. **Ensure .tex source is not included in review submission** -- While `acl.sty` suppresses author names in the PDF, the raw `.tex` source at `main.tex:93-103` contains full identifying information.
