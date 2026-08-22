# Reviewer Reviews Only

## Reviewer 7Wh2

Official Review by Reviewer 7Wh2  
Date: 06 Jul 2026, 09:53 (modified: 08 Jul 2026, 20:34)  
Readers: Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer 7Wh2  
Revisions: /revisions?id=6SiIlYQEKB

### Paper Summary

This paper focuses on tabular data synthesis using large language models (LLMs). The idea is to first induce a dependency DAG from a small real table using both LLM reasoning and statistical association measures, then use that DAG as a generation plan for black-box LLM calls. Basically the graph is used to determine feature order and prompt conditioning context.

### Summary Of Strengths

- The paper does a nice job and is akin to Bayesian network papers that separate structure discovery from conditional generation.
- The empirical results are strong. The authors demonstrate that their approach has the best downstream performacne on the datasets considered.
- The ablations are helpful. Replacing the LLM-guided graph discovery, or removing association scores, or ignoring topological order all hurt performance.

### Summary Of Weaknesses

- My main concern with this paper is that it is quite close to the paper by S. Xu et al. "Why LLMs Are Bad at Synthetic Table Generation and what to do about it" (https://arxiv.org/abs/2406.14541 (https://arxiv.org/abs/2406.14541)). This paper argues that LLM tabular generation fails because autoregressive generation imposes an order over columns, and that random feature-order fine-tuning will violate functional dependencies. It proposes injecting knowledge of functional relationships. Just like the proposed paper, there is a DAG learning step and then using that DAG information to generate data. As a result, the novelty here is limited and further the experimental results need to be contrasted with this above paper and their PAFT algorithm (in fact they seem to use the same dataset(s) as well).
- Besides the key related work contrasting and comparison, the privacy evaluation feels underdeveloped and is not quite a contribution.
- The statistical fidelity results are mixed (the algorithm proposed appears middle of the pack in some of these results).
- The limitations section acknowledges that opaque schemas such as V1/V2 or genomic locus identifiers weaken the LLM semantic prior (whereas this may not be a problem for the PAFT paper which seems to be discovering the dependencies).

### Comments Suggestions And Typos

Please see above.

### Ratings And Other Fields

- Confidence: 5 = Positive that my evaluation is correct. I read the paper very carefully and am familiar with related work.
- Soundness: 3 = Acceptable: This study provides sufficient support for its main claims. Some minor points may need extra support or details.
- Excitement: 1.5
- Overall Assessment: 2 = Resubmit next cycle: I think this paper needs substantial revisions that can be completed by the next ARR cycle.
- Ethical Concerns: There are no concerns with this submission.
- Needs Ethics Review: No
- Reproducibility: 4 = They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.
- Datasets: 4 = Useful: I would recommend the new datasets to other researchers or developers for their ongoing work.
- Software: 4 = Useful: I would recommend the new software to other researchers or developers for their ongoing work.
- Knowledge Of Or Educated Guess At Author Identity: No
- Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
- Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
- Publication Ethics Policy Compliance: I did not use any generative AI tools for this review

## Reviewer q74j

Official Review by Reviewer q74j  
Date: 29 Jun 2026, 17:05 (modified: 08 Jul 2026, 20:34)  
Readers: Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer q74j  
Revisions: /revisions?id=OY4fiQT2uE

### Paper Summary

This paper proposes a method for generating additional tabular data in scarce data scenarios. They decouple the extraction task in which a DAG is extracted from the existing tabular data using an LLM, and the generation task, where additional data is generated using the extracted DAG as guidance. They show

### Summary Of Strengths

The paper is very well-written The experimental design is sound. The method is evaluated on six downstream tasks and the extracted graph is evaluated for its quality as well. They show with extensive experiments that method is suitable for the task at hand The ablations further strengthen the claims and show the contribution of the different elements in the design

### Summary Of Weaknesses

It is not clear whether the baselines used are the best available methods in their respective categories. As the authors explain in l.052-l.055, deep generative models' performance varies across architectures and some may require many more examples to train. I expected a little explanation in the experiments section that motivates the choice for the particular models used as baselines. It is not always clear why you select a particular dataset to show results. In Section 4.5 and 4.6 why did you choose the Adult dataset and not one of the datasets that are created after the knowledge cutoff for LLMs?

### Comments Suggestions And Typos

The goal of the paper only became fully clear to me in l. 197. This description could feature earlier in the introduction.

### Ratings And Other Fields

- Confidence: 4 = Quite sure. I tried to check the important points carefully. It's unlikely, though conceivable, that I missed something that should affect my ratings.
- Soundness: 4.5
- Excitement: 3.5
- Overall Assessment: 4 = Conference: I think this paper could be accepted to an *ACL conference.
- Limitations And Societal Impact: The limitation section is insightful and to the point. The paper also discusses ethical considerations well.
- Ethical Concerns: The authors describe ethical considerations well.
- Needs Ethics Review: No
- Reproducibility: 1 = They would not be able to reproduce the results here no matter how hard they tried.
- Datasets: 1 = No usable datasets submitted.
- Software: 1 = No usable software released.
- Knowledge Of Or Educated Guess At Author Identity: No
- Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
- Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
- Publication Ethics Policy Compliance: I did not use any generative AI tools for this review

## Reviewer iRH3

Official Review by Reviewer iRH3  
Date: 24 Jun 2026, 16:38 (modified: 08 Jul 2026, 20:34)  
Readers: Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer iRH3  
Revisions: /revisions?id=54FM9gJXkT

### Paper Summary

This paper proposes StructSynth, a tabular data generation and augmentation method that first constructs a dependency graph among features using an LLM and then generates synthetic samples based on the learned graph structure. Learning dependencies among features is a central challenge in this setting and has been studied from various perspectives, including Bayesian networks, causal discovery, and statistical approaches. The key contribution of this work is to use the semantic knowledge of LLMs to infer the dependency graph, particularly in small sample size scenarios where purely data-driven approaches may struggle.

### Summary Of Strengths

1. The paper addresses an important problem in tabular data generation and augmentation, particularly under small sample size regimes where existing methods often face difficulties.
2. Experimental results are convincing, especially in terms of downstream model performance. The proposed method consistently performs well when the available sample size is small, suggesting that it may be practically useful across a range of applications.
3. The paper goes beyond reporting aggregate performance metrics and also presents examples of the learned dependency graphs. These qualitative results provide useful insights into the behavior of the method and help readers better understand the learned structures.

### Summary Of Weaknesses

1. Since the proposed method infers not only the existence of dependencies but also the directions of edges, the evaluation should assess more than statistical fidelity. While the paper reports measures such as Statistical Fidelity Error, it would also be valuable to evaluate the correctness of the learned graph structure, particularly edge directions, on datasets where ground-truth dependency structures are available.
2. The method is specifically motivated by small sample size scenarios, and the experiments focus on sample sizes up to n = 200. However, it is important to understand how the method behaves as more data become available. Experiments with larger sample sizes would help clarify the trade-off between the advantages of LLM-based graph construction and purely data-driven alternatives.
3. As acknowledged in the limitations section, the proposed approach exploits semantic information contained in feature names and descriptions, whereas most non-LLM baselines cannot use such information. This raises questions about the fairness of the comparison. An informative additional experiment would be to anonymize feature names (e.g., replacing them with V1, V2, ...) and evaluate how much the performance depends on semantic information provided by the feature names.

### Comments Suggestions And Typos

Please address the weaknesses discussed above.

### Ratings And Other Fields

- Confidence: 3 = Pretty sure, but there's a chance I missed something. Although I have a good feel for this area in general, I did not carefully check the paper's details, e.g., the math or experimental design.
- Soundness: 3.5
- Excitement: 3 = Interesting: I might mention some points of this paper to others and/or attend its presentation in a conference if there's time.
- Overall Assessment: 3 = Findings: I think this paper could be accepted to the Findings of the ACL.
- Ethical Concerns: There are no concerns with this submission
- Needs Ethics Review: No
- Reproducibility: 4 = They could mostly reproduce the results, but there may be some variation because of sample variance or minor variations in their interpretation of the protocol or method.
- Datasets: 3 = Potentially useful: Someone might find the new datasets useful for their work.
- Software: 4 = Useful: I would recommend the new software to other researchers or developers for their ongoing work.
- Knowledge Of Or Educated Guess At Author Identity: No
- Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Knowledge Of Paper Source: N/A, I do not know anything about the paper from outside sources
- Impact Of Knowledge Of Paper: N/A, I do not know anything about the paper from outside sources
- Reviewer Certification: I certify that the review I entered accurately reflects my assessment of the work. If you used any type of automated tool to help you craft your review, I hereby certify that its use was restricted to improving grammar and style, and the substance of the review is either my own work or the work of an acknowledged secondary reviewer.
- Publication Ethics Policy Compliance: I used a privacy-preserving tool exclusively for the use case(s) approved by PEC policy, such as language edits
