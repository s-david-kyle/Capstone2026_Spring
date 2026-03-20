# Overview

# Paper Summary
Research on a knowledge graph-based approach called **KGT** for enhancing the performance of Large Language Models (LLMs) in question answering, specifically within the biomedical domain. Here's a summary of the research:

**Core Focus:** The research introduces and evaluates KGT, a framework that leverages a knowledge graph (KG) to improve LLM performance on biomedical question answering tasks.

**Key Components of KGT:** The framework consists of four foundational modules:

1. **Question analysis:** To extract important information from the question.
2. **Graph schema-based inference:** To identify the optimal relationships within the knowledge graph relevant to the question.
3. **Query statement generation:** To create queries that facilitate subgraph construction within the KG.
4. **Inference process & natural language output:** To process information from the KG and present the results in a natural language format.

**Evaluation:** The researchers conducted an ablation study using the Code-Llama-13B model to evaluate the efficacy of each component of KGT. They compared KGT's performance against other commonly used methods like GPT-4, CoT & ICL, and KG-GPT.

**Results:** The results indicate that KGT significantly outperforms the baseline methods, achieving the highest ROUGE scores (92.4) and BERTScore (97.7) compared to GPT-4, CoT&ICL, and KG-GPT when using the Code-Llama-13B model.

**Implementation Details:** The project, named bioKGQA-KGT, is available on GitHub. It requires a Linux (Ubuntu) operating system with specific hardware resources (at least 2 CPU cores, 32 GB VRAM for inference; 60 GB VRAM for GPU) and programming languages (Shell Script/Bash with Python 3.10.13). It also utilizes libraries like neo4j. The project is licensed under the MIT license.

**Data:** The knowledge graph used in this research was developed by the authors using non-personalized data from credible biomedical sources, adhering to ethical guidelines and data privacy regulations.
# Paper
![[giae082.pdf]]
# Opportunities Addressed
**1. Addressing Hallucinations (Citation 3):** A significant challenge highlighted is the tendency of LLMs to generate "hallucinations" – incorrect or fabricated information. This is a key area for improvement, and the research explored methods to mitigate this.

**2. Catastrophic Forgetting (Citation 3):** <mark>Fine-tuning LLMs, while helpful for reducing hallucinations, can lead to "catastrophic forgetting," where the model loses its previously learned abilities.</mark> This suggests a need for more robust training techniques that preserve prior knowledge while incorporating new information.

**3. Prompt Engineering Optimization (Citation 3):** <mark>While prompt engineering offers a way to enhance LLM performance without fine-tuning, it's an area that can be further optimized. Research into more effective prompt design strategies (like Chain-of-Thought prompting) is ongoing and presents an opportunity for improvement. The development of automated prompt engineering methods (APE) also offers potential gains.</mark>

**4. Knowledge Graph Integration (Citation 3 & 1):** The research highlights the potential of integrating knowledge graphs with LLMs to improve factual accuracy. <mark>Further exploration of different KG architectures, retrieval methods, and reasoning strategies within the KG framework could lead to more robust and reliable systems.</mark>

**5. Scalability & Resource Efficiency (Implied):** While not explicitly stated as an opportunity, the mention of high training expenses associated with fine-tuning implies a need for more efficient methods. <mark>Research into techniques that reduce the computational cost of training and deploying LLMs would be beneficial.</mark>

**6. Generalizability & Benchmarking (Citation 1):** The research emphasizes the importance of robust benchmarking to evaluate LLM capabilities. Continued development and refinement of benchmarks (like the one created for oncology QA) are crucial to drive progress in this field. The focus on generalizability suggests a need to explore methods that allow models to perform well across diverse domains.

# Potential improvements
- The constructed QA dataset was designed to validate the effectiveness of the framework, but does not cover all potential use cases
- <mark>The system does not perform fuzzy matching - if a drug is misspelled by even one letter it will fail to retrieve information from the knowledge graph</mark>
- Their ultimate goal is to create a robust framework applicable to the rapidly evolving domain of medical knowledge to support health care professionals in delivering personalized, precise medication tailored to individual needs
- This study is a proof of concept, and has not been validated in actual clinical practice

# See also
- [[Research Paper Summaries]]
# Source
- https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giae082/7943459?login=false