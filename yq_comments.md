StructSynth

title

StructSynth: Dependency Graphs as Generation Plans for Low-Data Tabular Synthesis with Language Models

第一段。
It must preserve the dependency relationships inherent 以及the very dependencies that synthesis must preserve become difficult to discover reliably.这个表述太强，换成Low-data tabular synthesis is fundamentally a dependency-preservation problem.
进一步也可以考虑加一句补充解释 Effective synthetic instances are useful only when they preserve the task-relevant relationships among attributes, not merely when they increase sample size.

第二段，
Conventional tabular generators offer two important but partial ways of handling dependencies. Deep generative model （learn implict dependency through distribution fitting, but require enough data; structure-aware methods make the dependency explicit through graphical models, but replies on the graph quality.）这两点没有把传统方法打死，而且作为我们方法idea前置的铺垫。

第三段进入LLM methods. LLM-based synthesizers provide a complementary advantage: they can exploit attribute names, descriptions, and in-context examples as semantic priors. 然而，most 通过 flat textualization of attribute-value assignments 建模编码依赖，这里主要论述这种implicit dependency的问题。

第四段（讨论考虑dependency的LLM方法，这一类方法意识到了dependency引导llm的重要性，但有局限）

- A natural response is to make dependencies explicit; however, the key challenge lies in what role the dependency plays in generation.
- 然后讲相关方法，GraDe融入attention， SPADA通过conditional normalizing flow来实现高效采样。（不点名的话直接说recent graph-aware llm methods统称也行；以及没有考虑low-data）
- These designs validate the importance of sparse dependency structure, but they do not treat the graph as a prompt-level plan that organizes the LLM’s own generation process.
- 然后引出一个research question: Can a dependency graph determine the generation order, conditioning context, and scope of each black-box LLM call?

第五段，之前的Dependency Structure Discovery 和 Structure-Guided Synthesis比较宽泛，听起来也没啥新意。
We answer this question by instantiating StructSynth, a (prompt-level) framework that treats a dependency graph as a generation plan for black-box LLM synthesis. StructSynth contains two coupled stages: XXX and XXX。 第一个stage可以叫Evidence-Grounded Graph Induction, 第二个stage叫Graph-Planned Conditional Synthesis
