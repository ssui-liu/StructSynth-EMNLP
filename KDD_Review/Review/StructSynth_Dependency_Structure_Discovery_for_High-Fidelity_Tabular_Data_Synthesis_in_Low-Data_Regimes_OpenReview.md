# StructSynth: Dependency Structure Discovery for High-Fidelity Tabular Data Synthesis in Low-Data Regimes

**Keywords:** Tabular Data Synthesis, Dependency Structure Discovery, Structure-Conditioned Generation, Data Augmentation, Low-Data Regimes

**TL;DR:** StructSynth learns a dataset's hidden structure and uses it as a blueprint to guide an LLM, generating more realistic synthetic data from scarce samples.

## Abstract

The application of machine learning on tabular data in specialized domains is severely limited by data scarcity. Tabular data derives its value from the dependency relationships among features, yet reliably discovering these patterns becomes unstable when samples are scarce. Existing generative approaches either learn dependencies implicitly (failing in low-data regimes), assume pre-learned dependency graphs (which collapse under data scarcity), or induce dependencies from unstructured text (ignoring explicit structure). To address these limitations, we introduce StructSynth, a discover-then-synthesize framework that decouples dependency structure mining from data generation. In the first stage, StructSynth performs explicit dependency structure discovery, combining LLM-based reasoning with statistical association cues to construct a Directed Acyclic Graph (DAG) from limited samples. In the second stage, this learned structure serves as a blueprint for structure-conditioned generation, where data synthesis proceeds autoregressively following topological order, ensuring each feature is conditioned on its parent nodes. This design guarantees, by construction, that synthetic data respects the discovered dependencies. Extensive experiments demonstrate that StructSynth achieves state-of-the-art downstream utility while providing the best privacy-fidelity trade-off, proving especially effective in challenging low-data scenarios.

---

## Official Review by Reviewer hziw

### Paper Summary

This paper proposes StructSynth, a high-fidelity tabular data synthesis method designed for low-data regimes. The core idea is to decouple dependency structure discovery from data generation: first, a directed acyclic graph (DAG) is constructed from limited samples using a large language model combined with statistical association measures, along with a reasoning-based mechanism to resolve structural conflicts; then, this learned structure is used as a blueprint to guide generation in a topological order, ensuring that the synthesized data preserves the feature dependencies of the original data. Experiments on multiple real-world datasets and benchmark datasets with known structures demonstrate that the proposed method outperforms existing approaches in downstream task performance, privacy-fidelity trade-off, and robustness under low-data settings.

### Paper Strengths

1. The paper addresses an important and practical problem of tabular data synthesis under low-data regimes.
2. The proposed two-stage "discover-then-synthesize" framework is intuitive and improves interpretability.
3. The method effectively integrates LLM reasoning with statistical signals for structure learning.
4. Extensive experiments demonstrate strong performance across utility, privacy, and robustness metrics.

### Paper Weaknesses

1. Although the paper proposes a two-stage "structure discovery + data generation" framework, similar paradigms already exist, and the overall pipeline shows limited fundamental novelty beyond module integration.
2. While targeting low-data scenarios, the method mainly relies on LLM reasoning without specific mechanisms for small-sample instability, and is equally applicable to large-data settings, weakening its core motivation.
3. The privacy metric based on nearest-neighbor matching is insufficiently justified and not compared with standard approaches (e.g., membership inference), limiting the credibility of the privacy claims.
4. The work is strong in engineering and experimentation but lacks novelty, structural reliability analysis, cost evaluation, and theoretical depth, making it more of a system integration than a fundamentally new contribution.

### Questions And Suggestions For Rebuttal

1. Please clearly distinguish your method from prior "structure learning + generation" frameworks and highlight any fundamentally new contributions beyond LLM-based implementation.
2. What specific mechanisms make the approach particularly suitable for low-data regimes, rather than being generally applicable to any data scale?
3. How robust is the LLM-guided structure discovery under small samples, and how do errors in the learned DAG affect downstream generation quality?
4. Can the authors better justify the chosen privacy metric and compare it with standard evaluations?
5. Can the authors provide a clearer analysis of computational cost (e.g., token usage, runtime) versus performance gains, especially for practical deployment?

### Scores

| Criterion | Score |
|---|---|
| Relevance | 3: Moderate |
| Novelty | 2: Low |
| Technical Quality | 2: Low |
| Presentation | 3: Moderate |
| Reproducibility | 2: Low |
| Reviewer Confidence | 3: Moderate |

---

## Official Review by Reviewer f5xi

### Paper Summary

This paper studies tabular data synthesis in low-data regimes. Instead of directly learning the full data distribution, it proposes StructSynth, a two-stage framework that first discovers an explicit dependency structure among features and then generates synthetic data conditioned on that structure. The main idea is that preserving feature dependencies is more important than only matching marginal distributions when data is scarce.

### Paper Strengths

1. The paper targets a well-defined and practical problem, and the motivation for focusing on dependency preservation in low-data regimes is clear and convincing.
2. The two-stage design that separates structure discovery and data synthesis is intuitive, improves interpretability, and aligns well with the nature of tabular data.
3. The experimental evaluation is comprehensive, and the method demonstrates strong performance along with a favorable fidelity-privacy trade-off.

### Paper Weaknesses

1. The formulation of inter-column dependency as a directed acyclic graph is not sufficiently justified. For tabular data, feature dependencies are often better viewed as associative rather than inherently directional, so the paper should better explain why a DAG is the right structural assumption here.
2. The proposed graph construction procedure seems to depend on identifying variables that are not influenced by others as starting points. It is unclear how the method would work when such source nodes do not exist or cannot be reliably identified, which may limit its applicability.
3. The method explicitly introduces dependency discovery and statistical signals to improve structural consistency, so one would expect stronger statistical fidelity than prior LLM-based methods such as GReaT and GraDe. However, the reported results do not clearly support this expectation, and the current explanation is not fully convincing.
4. This also raises a broader concern that errors in the discovered dependency structure may propagate to the generation stage. Since the whole framework relies on the quality of the inferred structure, the paper should provide more discussion on how robust the method is when the discovered graph is imperfect.
5. The approach appears to require repeated LLM calls during structured generation, which could introduce substantial computational overhead. The paper would be stronger if it discussed inference cost, runtime, and scalability more explicitly, especially for tables with many columns.

### Questions And Suggestions For Rebuttal

See weaknesses.

### Scores

| Criterion | Score |
|---|---|
| Relevance | 3: Moderate |
| Novelty | 2: Low |
| Technical Quality | 2: Low |
| Presentation | 3: Moderate |
| Reproducibility | 2: Low |
| Reviewer Confidence | 3: Moderate |

---

## Official Review by Reviewer 6JGG

### Paper Summary

This paper presents StructSynth, a two-stage discover-then-synthesize framework for tabular data synthesis under low-data regimes. It decouples dependency structure mining from data generation: in the first stage, it constructs a feature dependency DAG using LLM-guided breadth-first search (BFS) with limited data, and employs LLM-based cycle resolution to ensure acyclicity; in the second stage, it uses the resulting dependency DAG as a blueprint to perform autoregressive structure-conditioned synthesis following topological order, alongside independent feature generation.

### Paper Strengths

This work introduces a decoupled framework that separates dependency discovery from data generation. This process not only mitigates the limitations of implicit structure learning and unstable pre-defined structures in low-data regimes, but also to some extent enhances model interpretability. Furthermore, it achieves an improved privacy-fidelity trade-off by employing the dependency DAG as a structural regularizer to prevent training data memorization. This trade-off yields a better balance between statistical fidelity and privacy protection compared with baseline methods under low-data regimes.

### Paper Weaknesses

1. The novelty is limited, where the discover-then-synthesize paradigm, LLM-based structure discovery and topological autoregressive synthesis are all existing in the literature. StructSynth only combines these with minor tweaks with no significant innovation.
2. The generated data is unreliable. The dependency DAG of features and the generation are all dependent on the LLM where the prior knowledge the LLM has will greatly affects the quality of the generated data. Since each large model has areas of strength and weakness, should different large models be used for table generation tasks in different domains? It has no fundamental difference with the methods with LLM.
3. There are some flaws with experimental design. This paper uses default hyperparameters for baselines and mismatches LLM settings for LLM-based baselines, which will lead to unfair comparisons.

### Questions And Suggestions For Rebuttal

I wonder what's the fundamental difference between traditional LLM generation method and StructSynth and how ensure the dependency DAG of features is reasonable?

### Scores

| Criterion | Score |
|---|---|
| Relevance | 3: Moderate |
| Novelty | 1: Poor |
| Technical Quality | 2: Low |
| Presentation | 2: Low |
| Reproducibility | 1: Poor |
| Reviewer Confidence | 3: Moderate |

---

## Official Review by Reviewer ep8Q

### Paper Summary

This paper introduces StructSynth, a two-stage framework for tabular data synthesis in low-data regimes. Stage 1 performs dependency structure discovery via LLM-guided breadth-first search combined with statistical association cues to construct a DAG. Stage 2 uses this DAG as a blueprint for generation, synthesizing data layer-by-layer following topological order. Experiments on six datasets and three structure-learning benchmarks show improvements over eleven baselines.

### Paper Strengths

1. **Novel and well-motivated framework.** The discover-then-synthesize paradigm is a clean and principled decomposition. Decoupling structure learning from generation is conceptually appealing and addresses a real limitation of existing approaches that either learn dependencies implicitly or assume pre-learned graphs.
2. **Practical evaluation with downstream model performance as the primary metric.** This paper centers evaluation on downstream model performance which is the most practically relevant measure of synthetic data quality. This application-driven evaluation well reflects real-world use cases where synthetic data is generated to improve ML model training.
3. **Evaluation covers both classification and regression tasks.** The experimental setup includes 4 classification datasets (binary and multi-class) and 2 regression datasets. This broader task coverage, while still limited in scale, provides more generalizable evidence than papers that evaluate on one task (e.g., classification) alone.

### Paper Weaknesses

1. **Insufficient evaluation scale.** The evaluation is limited to only 6 real-world datasets. With so few datasets, formal statistical tests (Friedman test, Wilcoxon signed-rank test) have very low power. The authors should expand to at least 10-15 diverse datasets with varying sizes, feature counts, and domains to substantiate their claims.
2. **Data contamination risk with only 2 post-cutoff datasets.** Only 2 of the 6 datasets (Anxiety, Salary) were released after the LLM knowledge cutoff. The remaining 4 (Adult, Compas, Obesity, Churn) are well-known benchmarks that GPT-4o-mini has probably seen during pretraining. The LLM may be partially recalling training data rather than genuinely learning from the provided samples. The evaluation should include substantially more post-cutoff datasets.
3. **Single downstream model (XGBoost only).** Downstream utility is evaluated using only XGBoost. This is problematic for two reasons: (1) the quality of synthetic data may vary across model families. Patterns that help tree-based models may not help neural networks; (2) some baselines may perform relatively better under different downstream learners. The authors should validate with multiple downstream models (e.g., TabPFNv2.5) to ensure the findings generalize beyond a single evaluator.
4. **Reproducibility concerns.** The paper does not provide a link to an anonymous code repository. Given the complexity of the multi-stage pipeline and the sensitivity of LLM-based methods to prompt engineering, reproducing the results from the paper alone may be very difficult. The full prompt templates in Appendix I are helpful but insufficient without the surrounding orchestration code.

### Questions And Suggestions For Rebuttal

1. How does performance change when the downstream model is not XGBoost? Specifically, have you tested with other models, e.g., TabPFNv2.5?
2. What happens when the number of features increases significantly (e.g., 50+ columns)? How does the BFS-based discovery scale, and how many LLM queries are required?
3. Do you plan to release the code and full implementation? Given the complexity of the pipeline and the sensitivity to prompt design, code availability is important for reproducibility.

### Scores

| Criterion | Score |
|---|---|
| Relevance | 4: High |
| Novelty | 3: Moderate |
| Technical Quality | 2: Low |
| Presentation | 3: Moderate |
| Reproducibility | 2: Low |
| Reviewer Confidence | 3: Moderate |
