# Overview
# Paper summary
This document describes a system called **SymptoTrackAI**, which is an AI-powered tool for symptom analysis. Here's a summary of the research presented:

**SymptoTrackAI is designed to help users understand their symptoms and potentially inform decision-making by:**

- **Providing a Chatbot Interface:** Users can describe their symptoms in natural language through a web (Streamlit) or desktop (Tkinter) interface.
- **Utilizing AI Models:** The system employs an ensemble of AI models, including:
    - **FAISS:** For fast and scalable semantic search to retrieve similar medical cases based on symptoms.
    - **Hybrid RAG Model:** Integrates HyDE and transformer-based NLP models (BERT/GPT) to improve medical reasoning.
    - **Neural Reranking Model:** Enhances the accuracy of retrieved medical cases by prioritizing high-confidence information.
- **Data Storage:** It uses both SQLite (for lightweight storage) and MongoDB (for scalability) to store both structured and unstructured data, including user queries and medical information.
- **Data Logging:** The system tracks past user queries for future reference and to improve the model over time.
- **Secure Data Handling:** User credentials are stored securely using hashing techniques in the databases.

**Evaluation Results:**

The document presents experimental results showing the training and validation accuracy of the proposed model. The evaluation loss consistently decreased during training, and the accuracy improved from approximately 65% to over 90%. The final evaluation achieved an accuracy of 94.2% to 98.2% depending on the specific model configuration (Proposed System).

**Comparison with Existing Work:**

The document also includes a table comparing the performance of SymptoTrackAI with several other research efforts (Retevoi et al. [10], Rau et al. [11], Pandey and Sharma [12], Steybe et al. [13]). In most cases, SymptoTrackAI demonstrates competitive or superior performance in terms of accuracy.

**In essence, the research details the development and evaluation of SymptoTrackAI, a system leveraging various AI techniques to create an intelligent chatbot for medical symptom analysis, with promising results in accuracy and performance.**
# Paper
![[SymptoTrackAI_Hybrid_RAG_Chatbot_for_Symptom_Monitoring.pdf]]
# Source
- https://ieeexplore.ieee.org/abstract/document/11167709
# See also
- [[Research Paper Summaries]]