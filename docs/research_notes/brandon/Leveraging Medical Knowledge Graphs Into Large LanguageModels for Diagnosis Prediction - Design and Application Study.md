# Overview

# Paper summary
A study on problem list summarization in electronic health records (EHRs).

**Core Focus:** Centers around the ProbSum shared task, which involves summarizing patients' active diagnoses and problems from EHR progress notes.

**Datasets Used:** The study utilizes two main datasets:

- **MIMIC-III:** A dataset containing approximately 1005 progress notes with active diagnoses annotated from the "plan" sections.
- **In-house EHR dataset:** A dataset containing 4815 progress notes, which was created by parsing text using a medical concept extractor based on the [[Unified Medical Language System (UMLS)]] [[SNOWMED CT]] vocabulary.

**Methods and Models:** The research explores various approaches for summarization, including:

- **Hierarchical Ensemble of Summarization Models:** A model combining multiple summarization models (including T5-Large and GPT-3.5-Turbo) to improve performance.
- **Pre-training with Extracted Healthcare Terms:** A method using pre-training with extracted healthcare terms to enhance summarization.
- **Data Augmentation with Large Language Models:** Using large language models (like GPT-3.5-Turbo) to augment the training data for summarization models.
- **Fine-tuning T5 Models:** Specifically, the study investigates fine-tuning different variants of the T5 model (vanilla T5, Flan-T5, and Clinical-T5) for summarization.
- **Diagnostic Reasoning Knowledge Graph System (DR.KNOWS):** A knowledge graph system is developed to enhance automated diagnostic reasoning, potentially used in conjunction with the summarization process.

**Evaluation:** The study evaluates the performance of these models on both the MIMIC-III and in-house datasets. It also considers the impact of incorporating predicted paths (from graph models) as auxiliary knowledge for summarization.

**Key Findings/Goals:** The research aims to:

- Evaluate the performance of different language models (T5, GPT-3.5-Turbo) for summarization tasks.
- Investigate the potential benefits of incorporating external knowledge (like a knowledge graph) into the summarization process.
- Analyze the impact of different training strategies (fine-tuning, zero-shot learning) on model performance.

**Data Availability:** The source code for the knowledge graph is available on GitHub, and the MIMIC-III dataset is accessible from PhysioNet.

In essence, this document details a research effort to advance the field of problem list summarization in healthcare by exploring various model architectures, training strategies, and knowledge integration techniques within the context of the ProbSum shared task.
# Paper
![[2308.14321v2.pdf]]
# Source
https://arxiv.org/abs/2308.14321
# See also
- [[DR.KNOWs]]
- [[Research Paper Summaries]]