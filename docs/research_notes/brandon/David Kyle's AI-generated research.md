# Capstone Proposal: Doctor-Facing Clinical Decision Support System

**Proposed Problem Statement**
Emergency and outpatient physicians must rapidly synthesize heterogeneous patient information — symptoms, medical history, vitals, laboratory results, and prior documentation — under significant time pressure. Current electronic health record systems present information chronologically rather than diagnostically, increasing cognitive load and potentially delaying accurate differential reasoning. This project aims to design and evaluate an AI-driven clinical reasoning support system that extracts structured symptom representations and ranks likely differential diagnoses while surfacing evidence-linked summaries and calibrated uncertainty estimates. The system is intended to assist, not replace, physician decision-making.

**System Overview**
The proposed system will consume structured outputs from the patient intake module and transform them into machine-readable representations. A hybrid architecture will then retrieve candidate diseases from a medical knowledge base and rank them using a combination of learned models and structured feature compatibility. 

The final output will include: 
• Top-ranked differential diagnoses
• Calibrated confidence estimates 
• Highlighted supporting and contradicting evidence 
• Identification of high-risk or red-flag conditions 

The emphasis of this sub-team will be on system architecture, retrieval and ranking methodology, uncertainty quantification, and rigorous evaluation.

**Research Emphasis**
Rather than building a symptom checker alone, this effort will explore and compare multiple
architectural approaches, including LLM-only reasoning, retrieval-augmented generation, and hybrid retrieval-ranking models that incorporate structured clinical data. Evaluation will focus on:
- Top-k diagnostic accuracy
- Calibration and uncertainty measurement
- Explainability and evidence linkage
- Comparative architectural analysis 

The goal is to produce a research-grade prototype that demonstrates thoughtful system design, responsible AI principles, and measurable performance.

# Potential Data Sources for Clinical Decision Support AI
This document outlines potential data sources for a hybrid clinical decision support system. Each source is evaluated along two dimensions: (1) difficulty of integration and (2) potential research and modeling value. Difficulty considers accessibility, preprocessing complexity, regulatory constraints, and technical harmonization. Value considers signal richness, realism, generalizability, and usefulness for evaluation and modeling.

**1. MIMIC-IV (ICU Clinical Dataset)**
Comprehensive ICU dataset containing structured vitals, laboratory values, diagnoses (ICD codes), and clinical notes. Strong for supervised evaluation and multimodal modeling.

**2. eICU Collaborative Research Database**
Multi-center ICU dataset containing structured patient data across multiple hospitals. Valuable for generalization experiments and cross-site robustness testing.

**3. [[PubMed]] Abstracts and Clinical Case Reports**
Large corpus of peer-reviewed biomedical literature. Useful for retrieval-augmented generation and knowledge base construction. Requires NLP preprocessing and filtering.

**4. [[SNOWMED CT]] / [[UMLS]] Ontologies**
Structured medical ontologies mapping symptoms to diagnoses. Enables standardized symptom normalization and knowledge graph construction.

**5. WebMD and Public Health Information Sites**
Public-facing symptom-disease descriptions. Easy to access but limited in structured depth and may lack clinical granularity required for rigorous evaluation.

# Related Work: AI Systems for Clinical Decision Support

**1. Traditional Clinical Decision Support Systems (CDSS)**
Clinical Decision Support Systems have long been integrated into electronic health record platforms. Commercial systems such as UpToDate, VisualDx, and Isabel Healthcare provide diagnostic guidance through curated medical knowledge bases and symptom-based differential generation. These platforms primarily rely on expert-authored content, rule-based reasoning, and deterministic logic rather than machine-learned ranking architectures. While widely adopted in hospitals, they do not typically expose probabilistic calibration metrics or uncertainty-aware outputs.

**2. Probabilistic and AI-Driven Symptom Checkers**
AI-driven triage platforms such as Ada Health and Infermedica employ probabilistic reasoning engines to rank possible diagnoses based on symptom inputs. These systems leverage structured medical ontologies and Bayesian-style updating to estimate likelihoods of disease states. While these tools have demonstrated scalability and clinical utility in triage settings, they remain proprietary, limiting transparency in model architecture, calibration methods, and evaluation benchmarks.

**3. AI Integration within Electronic Health Records**
Major electronic health record vendors such as Epic Systems and Cerner have begun integrating
AI-driven summarization and risk prediction tools into clinical workflows. These systems often focus on documentation summarization, sepsis alerts, readmission prediction, and clinical note generation. While they improve workflow efficiency, they are not primarily designed as transparent, research-oriented differential diagnosis ranking systems.

**4. Large Language Models in Clinical Contexts**
Recent advances in large language models have demonstrated strong performance in medical
question answering and summarization tasks. LLM-based systems can extract structured symptom information from free-text notes and generate physician-facing summaries. However, <mark>LLM-only approaches may produce unsupported reasoning steps and typically lack calibrated probability estimates.</mark> This has led to growing interest in hybrid architectures that combine retrieval mechanisms, structured modeling, and uncertainty quantification.

**5. Retrieval-Augmented and Hybrid Architectures**
Retrieval-Augmented Generation frameworks combine embedding-based knowledge retrieval with language model reasoning. In clinical applications, this enables disease candidates to be retrieved from structured knowledge bases prior to ranking and summarization. Emerging research explores combining text embeddings with structured features such as laboratory values, vital signs, and demographic variables. However, <mark>rigorous comparative evaluation between LLM-only systems and hybrid retrieval-ranking architectures remains limited in academic literature.</mark>

**6. Identified Gaps and Research Motivation**
Despite significant progress in commercial and academic systems, several limitations persist. First, <mark>uncertainty quantification and calibration are rarely emphasized in deployed tools.</mark> Second, <mark>many systems do not explicitly surface evidence chains linking patient features to ranked diagnoses.</mark> Third, comparative experimental evaluation across architectural paradigms is limited due to <mark>proprietary constraints</mark>. The proposed capstone project seeks to address these gaps by designing and experimentally evaluating a hybrid retrieval-ranking architecture that integrates structured and unstructured inputs while emphasizing calibrated uncertainty and explainability.
# See also
- [[Project Proposal]]