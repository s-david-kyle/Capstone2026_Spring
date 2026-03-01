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
# See also
- [[Research Paper Summaries]]
# Source
- https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giae082/7943459?login=false